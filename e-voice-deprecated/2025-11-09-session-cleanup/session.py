"""
Realtime speech session management.

⚠️ 【已废弃 / DEPRECATED】2025-11-09
=====================================

此模块中的 RealtimeSpeechSession 类已被新架构替代，不再在生产环境中使用。

新架构位置：
- speech_recognition/streaming/engine.py    (StreamingEngine)
- speech_recognition/streaming/state.py     (StreamingState)
- speech_recognition/streaming/text_accumulator.py (TextAccumulator)
- server/routes/ws.py                       (WebSocket 路由)

旧架构问题：
1. 状态管理复杂，存在多个冗余字段
2. 缓冲区裁剪逻辑导致"吞字回删"问题
3. 双模型调用混乱，难以维护

请使用新的 streaming 模块进行开发。此文件仅保留用于：
- 历史测试（tests/test_session_pipeline.py）
- 参考对照

如需新功能，请勿修改此文件。
=====================================
"""

from __future__ import annotations

import base64
import io
import json
import os
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import soundfile as sf

from speech_recognition.recognize import recognize
from config.config import conf

try:  # FunASR 流式识别
    from funasr import AutoModel  # type: ignore
except Exception:  # pragma: no cover - FunASR 未安装时回退
    AutoModel = None

from .audio_utils import extract_text_from_result, resolve_temp_dir
from .logging import audio_logger, key_logger, recognition_logger
from .text_processing import (
    calc_similarity,
    detect_voice_command,
    normalize_for_dedup,
    normalize_text,
)

try:  # 中文自动纠错
    from zh_correct.correct import correct as zh_correct  # type: ignore
except Exception:  # pragma: no cover - 纠错模型不可用时自动降级
    zh_correct = None

# NOTE: The implementation below is copied from the historic rest.py module
# with only dependency imports updated. Keeping the logic untouched preserves
# the behaviour of the realtime streaming pipeline while allowing us to split
# the server into maintainable modules.

class RealtimeSpeechSession:
    """
    ⚠️ 【已废弃 / DEPRECATED】
    实时语音识别会话类 - 输入法风格（已修复回删问题）

    此类已被新的 StreamingEngine 架构替代，请使用：
    - speech_recognition.streaming.engine.StreamingEngine
    - speech_recognition.streaming.state.StreamingState
    - speech_recognition.streaming.text_accumulator.TextAccumulator

    旧特点（仅供参考）：
    1. 流式处理音频块
    2. 区分"已确认文本"和"候选文本"，避免已确认内容被回删
    3. 智能文本确认机制，基于稳定性和置信度
    4. 类似输入法的用户体验，固定已确认部分
    """

    def __init__(self):
        self.audio_chunks = []  # 音频块列表
        
        # 🎯 【修改】简化文本状态管理
        self.full_sentence = ""
        self.confirmed_sentences = [] # 已确认的完整句子列表

        # ✍️ 当前段落的流式文本缓冲（未确认部分）
        self._live_text = ""
        self._segment_revision = 0
        self._last_final_info: Optional[Dict[str, Any]] = None
        
        # 🗑️ 【废弃】以下复杂的文本状态管理将被新的、更简单的逻辑替代
        # self.confirmed_text = ""  # 已确认的文本（固定显示，不再修改）
        # self.candidate_text = ""  # 候选文本（可以变化的部分）
        # self.text_stability_tracker = {}  # 文本稳定性跟踪器
        # self.last_stable_text = ""  # 最后一次稳定的文本
        # self.stability_count = 0  # 文本稳定次数计数
        # self.stability_threshold = 3  # 连续稳定次数阈值（达到后自动确认）
        
        # 音频段落管理（保留部分兼容）
        self.confirmed_audio_length = 0  # 已确认文本对应的音频长度
        self.candidate_audio_start = 0   # 候选文本对应的音频开始位置
        
        # 保留兼容属性
        self.current_sentence = ""  # 兼容现有接口：full_sentence
        self.cache: Dict[str, Any] = {}  # 流式识别缓存
        self.sample_rate = 16000
        self.chunk_size = [0, 10, 5]  # 流式识别参数
        self.encoder_chunk_look_back = 4
        self.decoder_chunk_look_back = 1
        # FunASR streaming 以 chunk_size[1] * 960 作为一步推理的采样点数
        self.streaming_stride_samples = int(self.chunk_size[1] * 960)
        self.last_update_time = time.time()
        # 🌐 基于网络搜索的标准参数配置
        self.chunk_duration = 0.25  # 处理间隔250ms (网络推荐范围100-500ms)
        self.silence_threshold = 2.0  # 静音阈值2秒（句子结束判断）
        self.audio_buffer = np.array([], dtype=np.float32)
        self.last_activity_time = time.time()  # 最后一次有语音活动的时间
        self.last_chunk_time = time.time()  # 最近一次处理音频块的时间
        self.sentence_complete_threshold = 1.2  # 句子完成阈值（自动断句速度）
        self.min_audio_duration = 0.1  # 最小音频长度：100ms (网络标准最小值)
        self.activity_peak_threshold = 0.02  # 峰值触发语音活动阈值
        self.activity_rms_threshold = 0.004  # RMS触发语音活动阈值
        self.interim_punctuation_min_silence = 0.6  # 触发临时标点的最短静音
        self._silence_accumulated = 0.0
        self._pending_synthetic_partial: Optional[Dict[str, Any]] = None
        self._pending_finalize_after_silence = False
        self._last_punctuation_text = ""
        self._last_punctuation_time = 0.0

        # 临时文件配置
        self.temp_file_counter = 0
        self.partial_save_counter = 0
        # 原始音频保存计数器与累积器（用于保留前端原始数据，取证与回放）
        self.raw_file_counter = 0
        self.raw_pcm_accumulator = io.BytesIO()
        self.first_pcm_sample_rate = None
        self.received_non_pcm = False
        self.session_id = None
        # 统一解析临时目录
        self.temp_dir = resolve_temp_dir()
        # 会话目录将在 set_session 中创建
        self.session_dir = None

        # 去重与幂等：最终段落跟踪
        self.final_seq = 0
        self._last_final_norm = ""
        self._recent_final_norms = []  # 最近若干final的规范化文本
        self._recent_final_texts = []  # 最近若干final原文
        self.last_partial_confidence = 0.0

        # 流式识别模型（默认启用 FunASR，失败时回退离线）
        self.streaming_model: Optional[Any] = None
        self._streaming_backend: Optional[str] = None
        self._streaming_available = False
        self._pending_streaming_result: Optional[Dict[str, Any]] = None
        self._last_streaming_result: Optional[Dict[str, Any]] = None
        self._last_streaming_text_sent = ""
        self._streaming_latency_ms = 0
        self._streaming_audio_cache = np.array([], dtype=np.float32)
        model_conf = conf["model"] if conf and conf.has_section("model") else None
        streaming_local_path = None
        if model_conf:
            try:
                streaming_local_path = model_conf.get("streaming_model")
            except Exception:
                streaming_local_path = None

        # 仅在配置了本地流式模型路径时才初始化，避免联网下载
        if AutoModel is not None and streaming_local_path:
            try:
                if streaming_local_path and os.path.exists(streaming_local_path):
                    self.streaming_model = AutoModel(
                        model=streaming_local_path,
                        disable_update=True,
                    )
                    self._streaming_backend = "funasr"
                    self._streaming_available = True
                    recognition_logger.info(
                        f"✅ [streaming] 使用本地模型初始化成功: {streaming_local_path}"
                    )
                else:
                    recognition_logger.warning(
                        f"⚠️ [streaming] 未找到本地流式模型路径: {streaming_local_path}，跳过初始化"
                    )
                    self.streaming_model = None
            except Exception as exc:  # pragma: no cover - 依赖缺失/权重下载失败
                recognition_logger.warning(
                    f"⚠️ [streaming] 流式模型初始化失败（本地路径），使用离线回退: {exc}"
                )
                self.streaming_model = None
        else:  # 未配置或未安装 FunASR
            if AutoModel is None:
                recognition_logger.warning("⚠️ [streaming] 未检测到 FunASR，使用离线回退")
            else:
                recognition_logger.info("ℹ️ [streaming] 未配置本地流式模型路径，跳过流式初始化")

        # 🌐 基于网络标准的质量监控系统
        self.quality_stats = {
            'total_chunks': 0,
            'valid_chunks': 0,
            'high_quality_chunks': 0,
            'recognition_attempts': 0,
            'successful_recognitions': 0,
            'avg_rms': 0.0,
            'last_quality_report': time.time()
        }

    def set_session(self, session_id: str):
        """设置会话ID并创建持久化目录"""
        self.session_id = session_id
        try:
            self.session_dir = os.path.join(self.temp_dir, f"session_{session_id}")
            os.makedirs(self.session_dir, exist_ok=True)
            # 写入会话元信息
            meta = {
                'session_id': session_id,
                'start_time': int(time.time() * 1000),
                'sample_rate': self.sample_rate
            }
            with open(os.path.join(self.session_dir, 'session.json'), 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False)
        except Exception:
            # 目录创建失败不影响主流程
            self.session_dir = None

    def reset(self):
        """重置会话状态"""
        self.audio_chunks.clear()

        self._silence_accumulated = 0.0
        self._pending_synthetic_partial = None
        self._pending_finalize_after_silence = False
        self._last_punctuation_text = ""
        self._last_punctuation_time = 0.0

        if self._streaming_available and self.streaming_model is not None:
            try:
                if self._streaming_audio_cache.size > 0:
                    self._streaming_infer(self._streaming_audio_cache, is_final=True)
                else:
                    self._streaming_infer(np.array([], dtype=np.float32), is_final=True)
            except Exception:  # pragma: no cover - 防御性兜底
                pass

        # 🎯 【修改】重置新的简化状态管理
        self.full_sentence = ""

        # 🗑️ 【废弃】以下状态变量已被移除
        # self.confirmed_text = ""
        # self.candidate_text = ""
        # self.text_stability_tracker.clear()
        # self.last_stable_text = ""
        # self.stability_count = 0
        
        self.confirmed_audio_length = 0
        self.candidate_audio_start = 0

        # 重置原有状态
        self.current_sentence = ""
        self.full_sentence = ""  # 🔧【2025-01-19 修复】同时重置主状态字段
        self.confirmed_sentences = []
        self._live_text = ""
        self._segment_revision = 0
        self._last_final_info = None
        self.final_seq = 0
        self.cache.clear()
        self._pending_streaming_result = None
        self._last_streaming_result = None
        self._last_streaming_text_sent = ""
        self._streaming_latency_ms = 0
        self._streaming_audio_cache = np.array([], dtype=np.float32)
        self.audio_buffer = np.array([], dtype=np.float32)
        self.last_update_time = time.time()
        self.last_activity_time = time.time()
        self.last_chunk_time = time.time()
        
        # 重置质量统计
        self.quality_stats = {
            'total_chunks': 0,
            'valid_chunks': 0,
            'high_quality_chunks': 0,
            'recognition_attempts': 0,
            'successful_recognitions': 0,
            'avg_rms': 0.0,
            'last_quality_report': time.time()
        }

        # 重置去重与幂等状态
        self.final_seq = 0
        self._last_final_norm = ""
        self._recent_final_norms = []
        self._recent_final_texts = []
        self.last_partial_confidence = 0.0

    def _is_duplicate_final(self, text: str, similarity_threshold: float = 0.92) -> bool:
        """
        判断一个最终文本是否与最近一次或最近若干次final重复/极度相似。
        """
        if not text:
            return False
        norm = normalize_for_dedup(text)
        if not norm:
            return False

        if self._last_final_norm:
            sim = calc_similarity(norm, self._last_final_norm)
            if sim >= similarity_threshold:
                return True

        # 与窗口内其他final比较（更稳健）
        for prev_norm in self._recent_final_norms[-4:]:
            if calc_similarity(norm, prev_norm) >= similarity_threshold:
                return True
        return False

    def _register_final(self, text: str):
        """
        在发送final后登记规范化文本用于后续去重。
        """
        norm = normalize_for_dedup(text)
        self._last_final_norm = norm
        self._recent_final_norms.append(norm)
        self._recent_final_texts.append(text)
        # 只保留最近5条
        if len(self._recent_final_norms) > 5:
            self._recent_final_norms = self._recent_final_norms[-5:]
        if len(self._recent_final_texts) > 5:
            self._recent_final_texts = self._recent_final_texts[-5:]

    def _allocate_segment_id(self) -> str:
        """
        生成下一个final段落的segment_id（会话内自增）。
        """
        self.final_seq += 1
        base = str(self.final_seq)
        if self.session_id:
            return f"{self.session_id}-{base}"
        return base

    def _current_segment_seq(self) -> int:
        """返回当前实时段落的序号（final_seq + 1）。"""
        return self.final_seq + 1

    def _format_segment_id(self, seq: Optional[int] = None) -> str:
        """构造指定序号的 segment_id（不自增）。"""
        seg = self.final_seq + 1 if seq is None else seq
        if self.session_id:
            return f"{self.session_id}-{seg}"
        return str(seg)

    def _combine_confirmed_and_live(self, confirmed: str, live: str) -> str:
        confirmed = confirmed or ""
        live = live or ""
        if confirmed and live:
            if confirmed.endswith(tuple("，。！？,.!?：；、 ")):
                return confirmed + live
            return f"{confirmed} {live}"
        return confirmed or live

    def _set_live_text(self, text: str) -> str:
        """统一更新当前未确认文本状态。"""

        normalized = (text or "").strip()
        self._live_text = normalized
        self.full_sentence = normalized
        self.current_sentence = normalized
        return normalized

    def _merge_streaming_text(self, new_text: str) -> str:
        """将新的流式文本合并到当前未确认缓冲。"""

        normalized = (new_text or "").strip()
        if not normalized:
            return self._live_text

        base = (self._live_text or "").strip()
        if not base:
            merged = normalized
        elif normalized == base:
            merged = base
        elif base in normalized and len(normalized) >= len(base):
            merged = normalized
        elif normalized in base and len(normalized) <= len(base):
            merged = base
        else:
            overlap = 0
            max_len = min(len(base), len(normalized))
            for size in range(max_len, 0, -1):
                if base.endswith(normalized[:size]):
                    overlap = size
                    break
            if overlap > 0:
                merged = base + normalized[overlap:]
            else:
                similarity = calc_similarity(base[-max_len:] if max_len else base, normalized)
                if similarity >= 0.6 and len(normalized) >= len(base):
                    merged = normalized
                else:
                    merged = base + normalized

        return self._set_live_text(merged)

    def _maybe_apply_interim_punctuation(self, silence_duration: float) -> None:
        """在长时间静音时，为当前候选文本添加临时标点并触发一次增量更新。"""

        if silence_duration < self.interim_punctuation_min_silence:
            return

        if self._pending_synthetic_partial is not None:
            return

        candidate = (self.full_sentence or "").strip()
        if not candidate:
            return

        if candidate.endswith(tuple("。！？!?……")):
            return

        normalized_current = (self._live_text or "").strip()
        try:
            punctuated = self.predict_punctuation(candidate, silence_duration)
        except Exception:  # pragma: no cover - 预测异常时保持原状
            return

        punctuated_norm = normalize_text(punctuated)
        if not punctuated_norm or punctuated_norm == normalized_current:
            return

        now = time.time()
        if (
            self._last_punctuation_text == punctuated_norm
            and now - self._last_punctuation_time < 0.5
        ):
            return

        self._set_live_text(punctuated_norm)
        self.last_update_time = now
        self._last_punctuation_text = punctuated_norm
        self._last_punctuation_time = now

        confidence = self.last_partial_confidence or 0.9
        self._pending_synthetic_partial = {
            "text": punctuated_norm,
            "raw_text": punctuated,
            "confidence": confidence,
            "processing_time_ms": 0,
            "source": "auto_punctuation",
        }

        if punctuated_norm.endswith(tuple("。！？!?")):
            self._pending_finalize_after_silence = True

        recognition_logger.debug(
            "📝 自动标点预览: silence=%.2fs text='%s'",
            silence_duration,
            punctuated_norm,
        )

    def _select_best_final_text(self, streaming_text: str, offline_text: str) -> Tuple[str, str]:
        """在流式结果与离线结果之间选择更完整的文本。"""

        streaming_clean = (streaming_text or "").strip()
        offline_clean = (offline_text or "").strip()

        if offline_clean and not streaming_clean:
            return offline_clean, "offline"
        if streaming_clean and not offline_clean:
            return streaming_clean, "streaming"
        if not streaming_clean and not offline_clean:
            return "", "none"

        offline_len = len(normalize_for_dedup(offline_clean))
        streaming_len = len(normalize_for_dedup(streaming_clean))

        if offline_clean:
            if offline_len >= streaming_len:
                return offline_clean, "offline"
            similarity = calc_similarity(streaming_clean, offline_clean)
            if similarity < 0.6 and offline_len >= max(3, streaming_len - 2):
                return offline_clean, "offline"

        return streaming_clean, "streaming"

    def _run_offline_final_recognition(self) -> Tuple[str, Optional[Any]]:
        """对当前音频缓冲执行一次离线识别用于矫正。"""

        if self.audio_buffer.size == 0:
            return "", None

        temp_path = os.path.join(
            self.session_dir or self.temp_dir,
            f"offline_final_{int(time.time() * 1000)}.wav",
        )

        try:
            sf.write(
                temp_path,
                np.clip(self.audio_buffer, -1.0, 1.0),
                self.sample_rate,
                subtype="PCM_16",
            )
            result = recognize(temp_path)
            offline_text = extract_text_from_result(result)
            offline_text = normalize_text(offline_text)
            return offline_text, result
        except Exception as exc:  # pragma: no cover - 离线识别失败时记录日志
            recognition_logger.warning(
                f"⚠️ [offline] 最终矫正识别失败: {exc}"
            )
            return "", None
        finally:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:  # pragma: no cover - 防御性
                pass

    def _auto_correct_text(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """对文本执行自动纠错，返回纠错后的文本及元数据。"""

        if not text or not zh_correct:
            return text, {"applied": False, "details": [], "raw_result": None}

        try:
            correction = zh_correct(text)
        except Exception as exc:  # pragma: no cover - 纠错失败降级
            recognition_logger.warning(f"⚠️ 自动纠错失败: {exc}")
            return text, {"applied": False, "details": [], "raw_result": None}

        corrected = text
        details: List[Any] = []

        if isinstance(correction, dict):
            corrected = correction.get("target") or correction.get("corrected_text") or text
            details = correction.get("details") or correction.get("detail") or []
        elif isinstance(correction, (list, tuple)):
            if correction and isinstance(correction[0], str):
                corrected = correction[0]
            if len(correction) > 1:
                details = correction[1]

        corrected = corrected or text
        applied = corrected.strip() != text.strip()

        return corrected, {"applied": applied, "details": details, "raw_result": correction}
        
    def _update_text_stability(self, new_text):
        """🗑️【已废弃】文本稳定性跟踪方法，保留仅为兼容性"""
        return False
        
    def _extract_confirmed_part(self, current_text, previous_text):
        """🗑️【已废弃】文本确认部分提取方法，保留仅为兼容性"""
        return "", current_text
        
    def _should_confirm_by_pause(self):
        """🗑️【已废弃】停顿确认判断方法，保留仅为兼容性"""
        return False
        
    def predict_punctuation(self, text, silence_duration, audio_energy_level=None):
        """
        智能标点预测 - 基于停顿和语调模式
        
        Args:
            text: 输入文本
            silence_duration: 静音时长(秒)
            audio_energy_level: 音频能量级别(可选)
            
        Returns:
            str: 添加标点后的文本
        """
        if not text or not text.strip():
            return text
            
        import re
        
        # 如果文本已有标点，直接返回
        if re.search(r'[。！？,.!?]$', text):
            return text
            
        # 🎯 基于停顿时长的标点预测
        if silence_duration >= 1.5:
            # 长停顿：判断句子类型
            if any(word in text for word in ['什么', '哪里', '怎么', '为什么', '吗']):
                # 疑问句
                text += '？'
                recognition_logger.debug(f"🎯 智能标点: 疑问句 + 长停顿 -> 问号")
            elif any(word in text for word in ['好', '太', '真', '非常']):
                # 可能是感叹句
                text += '！'
                recognition_logger.debug(f"🎯 智能标点: 感叹句 + 长停顿 -> 叹号")
            else:
                # 普通陈述句
                text += '。'
                recognition_logger.debug(f"🎯 智能标点: 陈述句 + 长停顿 -> 句号")
                
        elif 0.3 <= silence_duration < 1.5:
            # 中等停顿：可能需要逗号
            # 简单规则：如果文本较长且没有标点，添加逗号
            if len(text) > 8 and not re.search(r'[，,]', text):
                # 寻找合适的逗号位置（连词后、时间词后等）
                comma_positions = []
                
                # 在连词后添加逗号
                connectors = ['但是', '不过', '然后', '接着', '另外', '而且', '所以', '因此']
                for conn in connectors:
                    pos = text.find(conn)
                    if pos >= 0:
                        comma_positions.append(pos + len(conn))
                
                # 在时间词后添加逗号
                time_words = ['今天', '昨天', '明天', '现在', '刚才', '一会儿']
                for time_word in time_words:
                    pos = text.find(time_word)
                    if pos >= 0:
                        comma_positions.append(pos + len(time_word))
                
                # 选择最合适的位置添加逗号
                if comma_positions:
                    # 选择中间位置的逗号点
                    pos = min(comma_positions, key=lambda x: abs(x - len(text) // 2))
                    text = text[:pos] + '，' + text[pos:]
                    recognition_logger.debug(f"🎯 智能标点: 中等停顿 + 连接词 -> 逗号")
                    
        return text

    def _execute_edit_command(self, command_params):
        """
        【已重构】执行编辑指令，适配新的文本状态管理
        
        Args:
            command_params: 指令参数字典
            
        Returns:
            dict: 更新后的文本状态
        """
        command_type = command_params.get('type')
        
        if command_type == 'delete':
            target = command_params.get('target')
            
            if target == 'all':
                # 删除全部
                old_confirmed = "".join(self.confirmed_sentences)
                old_current = self.full_sentence
                self.confirmed_sentences.clear()
                self.full_sentence = ""
                recognition_logger.info(f"🗑️ 删除全部: 已确认='{old_confirmed}' + 当前='{old_current}' -> ''")
                
            elif target == 'last_sentence':
                # 删除最后一句话
                if self.full_sentence:
                    old_current = self.full_sentence
                    self.full_sentence = ""
                    recognition_logger.info(f"🗑️ 删除当前句子: '{old_current}' -> ''")
                elif self.confirmed_sentences:
                    deleted_sentence = self.confirmed_sentences.pop()
                    recognition_logger.info(f"🗑️ 删除最后确认句子: '{deleted_sentence}'")
                
            elif target == 'last_word':
                # 删除最后一个词
                if self.full_sentence:
                    words = self.full_sentence.split()
                    if words:
                        old_current = self.full_sentence
                        self.full_sentence = ' '.join(words[:-1])
                        recognition_logger.info(f"🗑️ 删除当前句最后词: '{old_current}' -> '{self.full_sentence}'")
                        
            elif target == 'last_char':
                # 删除最后一个字符
                if self.full_sentence:
                    old_current = self.full_sentence
                    self.full_sentence = self.full_sentence[:-1]
                    recognition_logger.info(f"🗑️ 删除当前句最后字符: '{old_current}' -> '{self.full_sentence}'")
                    
        elif command_type == 'undo':
            # 撤销操作（简化实现：清空当前句子）
            if self.full_sentence:
                old_current = self.full_sentence
                self.full_sentence = ""
                recognition_logger.info(f"↩️ 撤销当前句子: '{old_current}' -> ''")
                
        elif command_type == 'redo':
            # 重做操作（简化实现：这里可以扩展为恢复历史状态）
            recognition_logger.info("↪️ 重做指令已接收（当前为简化实现）")
        
        # 返回新架构的状态信息
        return {
            'confirmed_text': "".join(self.confirmed_sentences),
            'candidate_text': self.full_sentence,
            'full_text': "".join(self.confirmed_sentences) + self.full_sentence,
            'changed': True,
            'stability_count': 0,
            'confirmed_length': len("".join(self.confirmed_sentences))
        }

    def update_text_state(self, new_full_text, confidence=0.8):
        """
        🗑️【已废弃】复杂的文本状态管理方法
        此方法在新架构中已不再使用，保留仅为兼容性
        
        Returns:
            dict: 兼容性返回值
        """
        # 简化的兼容性实现
        return {
            'confirmed_text': "".join(self.confirmed_sentences),
            'candidate_text': self.full_sentence,
            'full_text': "".join(self.confirmed_sentences) + self.full_sentence,
            'changed': True,
            'stability_count': 0,
            'confirmed_length': len("".join(self.confirmed_sentences))
        }

    def _streaming_infer(
        self, audio_chunk: Optional[np.ndarray], is_final: bool = False
    ) -> Optional[Dict[str, Any]]:
        """调用流式识别模型并缓存最近一次结果。"""

        if not self._streaming_available or self.streaming_model is None:
            return None

        try:
            if audio_chunk is None:
                audio_chunk = np.array([], dtype=np.float32)
            if not isinstance(audio_chunk, np.ndarray):
                audio_chunk = np.asarray(audio_chunk, dtype=np.float32)
            if audio_chunk.ndim > 1:
                audio_chunk = audio_chunk.flatten()

            start_time = time.time()
            if self._streaming_backend == "funasr":
                result = self.streaming_model.generate(
                    input=audio_chunk.astype(np.float32, copy=False),
                    cache=self.cache,
                    is_final=is_final,
                    chunk_size=self.chunk_size,
                    encoder_chunk_look_back=self.encoder_chunk_look_back,
                    decoder_chunk_look_back=self.decoder_chunk_look_back,
                )
            else:  # pragma: no cover - 仅支持FunASR后端
                return None

            elapsed_ms = int((time.time() - start_time) * 1000)
            text = extract_text_from_result(result)
            confidence = 0.0
            if isinstance(result, dict):
                confidence = float(
                    result.get("confidence")
                    or result.get("score")
                    or 0.0
                )
            elif isinstance(result, (list, tuple)) and result:
                first = result[0]
                if isinstance(first, dict):
                    confidence = float(
                        first.get("confidence")
                        or first.get("score")
                        or 0.0
                    )

            payload = {
                "text": text,
                "confidence": confidence,
                "raw": result,
                "processing_time_ms": elapsed_ms,
                "is_final": is_final,
            }

            self._last_streaming_result = payload
            self._streaming_latency_ms = elapsed_ms

            if not is_final:
                if text and text != self._last_streaming_text_sent:
                    self._pending_streaming_result = payload
                else:
                    self._pending_streaming_result = None
            else:
                # final flush不通过partial发送
                self._pending_streaming_result = None

            return payload
        except Exception as exc:  # pragma: no cover - 推理异常退化
            recognition_logger.warning(
                f"⚠️ [streaming] 流式推理失败，切换离线回退: {exc}"
            )
            self.streaming_model = None
            self._streaming_backend = None
            self._streaming_available = False
            self._pending_streaming_result = None
            self._streaming_audio_cache = np.array([], dtype=np.float32)
            return None

    def add_audio_chunk(self, audio_data, audio_format='pcm', sample_rate=16000, seq=None):
        """
        添加音频块
        
        Args:
            audio_data: base64编码的音频数据
            audio_format: 音频格式 (pcm, wav, webm)
            sample_rate: 采样率
            seq: 前端发送的序号，用于排查丢包/乱序
        """
        chunk_start_time = time.time()
        self.last_chunk_time = chunk_start_time
        buffer_trimmed = False

        try:
            # 解码音频数据
            raw_audio = base64.b64decode(audio_data)
            audio_logger.trace(
                f"收到音频块: format={audio_format}, raw_size={len(raw_audio)} bytes, sample_rate={sample_rate}")

            # 检查数据大小有效性
            if len(raw_audio) < 10:
                audio_logger.warning(f"音频块太小，跳过: {len(raw_audio)} bytes")
                return

            # 先行落盘保存原始数据（仅对PCM做一比一保留）
            try:
                if self.session_dir and audio_format == 'pcm':
                    self.raw_file_counter += 1
                    raw_name = os.path.join(
                        self.session_dir,
                        f"raw_chunk_{self.raw_file_counter}_{len(raw_audio)}.pcm"
                    )
                    with open(raw_name, 'wb') as f:
                        f.write(raw_audio)

                    # 保存原始块的元数据
                    try:
                        raw_meta = {
                            'seq': int(seq) if isinstance(seq, (int, float, str)) and str(seq).isdigit() else seq,
                            'sample_rate': int(sample_rate) if sample_rate else None,
                            'size_bytes': len(raw_audio),
                            'format': audio_format,
                        }
                        with open(os.path.join(self.session_dir, f"raw_chunk_{self.raw_file_counter}.json"), 'w', encoding='utf-8') as mf:
                            json.dump(raw_meta, mf, ensure_ascii=False)
                    except Exception as meta_e:
                        audio_logger.debug(f"原始音频元数据保存失败: {meta_e}")

                    # 聚合原始PCM流与采样率记录
                    try:
                        self.raw_pcm_accumulator.write(raw_audio)
                        if self.first_pcm_sample_rate is None and sample_rate:
                            self.first_pcm_sample_rate = int(sample_rate)
                    except Exception as acc_e:
                        audio_logger.debug(f"原始音频累积失败: {acc_e}")
                else:
                    if audio_format != 'pcm':
                        self.received_non_pcm = True
            except Exception as raw_save_e:
                audio_logger.debug(f"保存原始音频块失败: {raw_save_e}")

            if audio_format == 'pcm':
                # PCM格式：16位小端格式（保证偶数字节对齐）
                if len(raw_audio) % 2 != 0:
                    raw_audio = raw_audio[:-1]
                audio_array = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32)
                # 归一化到 [-1, 1]
                audio_array = audio_array / 32768.0
                audio_logger.trace(f"PCM解码完成: samples={len(audio_array)}")

            elif audio_format == 'webm':
                # WebM格式处理 - 但通常会有问题，所以添加更好的错误处理
                try:
                    from pydub import AudioSegment
                    audio_stream = io.BytesIO(raw_audio)

                    # 检查数据大小，太小的块可能无法解析
                    if len(raw_audio) < 100:
                        audio_logger.warning(f"WebM音频块太小，跳过: {len(raw_audio)} bytes")
                        return

                    audio = AudioSegment.from_file(audio_stream, format="webm")
                    audio = audio.set_frame_rate(sample_rate).set_channels(1)
                    audio_array = np.array(audio.get_array_of_samples(), dtype=np.float32)

                    # 归一化
                    if audio.sample_width == 2:
                        audio_array = audio_array / 32768.0
                    elif audio.sample_width == 4:
                        audio_array = audio_array / 2147483648.0

                    audio_logger.trace(f"WebM解码完成: samples={len(audio_array)}, sample_width={audio.sample_width}")

                except Exception as webm_error:
                    audio_logger.error(f"WebM解码失败，跳过此音频块: {str(webm_error)}")
                    return

            else:
                # WAV等其他格式
                try:
                    audio_stream = io.BytesIO(raw_audio)
                    # 使用全局导入的 soundfile 避免局部覆盖导致的未绑定错误
                    audio_array, _ = sf.read(audio_stream)
                    if audio_array.dtype != np.float32:
                        audio_array = audio_array.astype(np.float32)
                    audio_logger.trace(f"{audio_format}解码完成: samples={len(audio_array)}")
                except Exception as sf_error:
                    audio_logger.error(f"音频格式 {audio_format} 解码失败: {str(sf_error)}")
                    return

            # 确保audio_array是一维的
            if len(audio_array.shape) > 1:
                audio_array = audio_array.flatten()
                audio_logger.trace(f"音频数据已扁平化: final_samples={len(audio_array)}")

            # 若采样率与目标不同，做线性重采样到 16k
            try:
                input_sr = int(sample_rate) if sample_rate else 16000
            except Exception:
                input_sr = 16000
            if input_sr != self.sample_rate and audio_array.size > 0:
                duration_sec = audio_array.size / float(input_sr)
                target_len = int(duration_sec * self.sample_rate)
                if target_len > 0:
                    old_idx = np.linspace(0, audio_array.size - 1, num=audio_array.size)
                    new_idx = np.linspace(0, audio_array.size - 1, num=target_len)
                    audio_array = np.interp(new_idx, old_idx, audio_array).astype(np.float32)
                    audio_logger.info(f"重采样: {input_sr} -> {self.sample_rate}, samples: {len(audio_array)}")

            # 检查音频质量：避免全零或极值数据
            if len(audio_array) == 0:
                audio_logger.debug("检测到空音频块，跳过")
                return
                
            if np.all(audio_array == 0):
                audio_logger.debug("检测到全零音频块，跳过")
                return

            # 自适应增益控制(AGC): 提升过低RMS的音频以触发识别
            pre_agc_rms = float(np.sqrt(np.mean(audio_array ** 2))) if audio_array.size > 0 else 0.0
            if pre_agc_rms > 0 and pre_agc_rms < 0.005:
                target_rms = 0.03  # 目标轻声级RMS
                gain = min(10.0, target_rms / max(pre_agc_rms, 1e-7))
                audio_array = audio_array * gain
                # 限幅避免削波
                max_abs = float(np.max(np.abs(audio_array))) if audio_array.size > 0 else 0.0
                if max_abs > 1.0:
                    audio_array = audio_array / max_abs
                audio_logger.info(f"AGC已应用: 原始RMS={pre_agc_rms:.6f}, 增益={gain:.2f}")

            # 检查音频幅值合理性
            max_amplitude = np.max(np.abs(audio_array))
            rms_amplitude = np.sqrt(np.mean(audio_array ** 2))
            mean_amplitude = np.mean(np.abs(audio_array))

            # 音频质量统计
            non_zero_samples = np.count_nonzero(audio_array)
            zero_ratio = (len(audio_array) - non_zero_samples) / len(audio_array)
            
            audio_logger.debug(
                f"音频质量分析: samples={len(audio_array)}, max_amp={max_amplitude:.4f}, "
                f"rms_amp={rms_amplitude:.4f}, mean_amp={mean_amplitude:.4f}, "
                f"non_zero_ratio={1-zero_ratio:.3f}, zero_ratio={zero_ratio:.3f}")

            if max_amplitude > 10.0:  # 异常大的值
                audio_logger.warning(f"音频幅值异常: max={max_amplitude}，进行裁剪")
                audio_array = np.clip(audio_array, -1.0, 1.0)
                max_amplitude = np.max(np.abs(audio_array))

            chunk_duration_seconds = (
                len(audio_array) / float(self.sample_rate)
                if self.sample_rate and len(audio_array) > 0
                else 0.0
            )

            dynamic_rms_threshold = self.activity_rms_threshold
            if self.quality_stats.get('valid_chunks'):
                dynamic_rms_threshold = max(
                    dynamic_rms_threshold,
                    self.quality_stats.get('avg_rms', 0.0) * 0.5,
                )

            if (
                max_amplitude >= self.activity_peak_threshold
                or rms_amplitude >= dynamic_rms_threshold
            ):
                self.last_activity_time = time.time()
                self._silence_accumulated = 0.0
                self._pending_synthetic_partial = None
                self._pending_finalize_after_silence = False
                self._last_punctuation_text = ""
            else:
                if chunk_duration_seconds > 0:
                    self._silence_accumulated += chunk_duration_seconds
                self._maybe_apply_interim_punctuation(self._silence_accumulated)

            # 添加到缓冲区
            buffer_size_before = self.audio_buffer.size
            if len(self.audio_buffer) > 0:
                self.audio_buffer = np.concatenate([self.audio_buffer, audio_array])
            else:
                self.audio_buffer = audio_array

            self.audio_chunks.append({
                'data': audio_array,
                'timestamp': time.time(),
                'format': audio_format,
                'sample_rate': sample_rate,
                'size': len(audio_array),
                'max_amplitude': max_amplitude,
                'rms_amplitude': rms_amplitude,
                'mean_amplitude': mean_amplitude,
                'zero_ratio': zero_ratio
            })

            if self._streaming_available and self.streaming_model is not None:
                # FunASR 模型要求以固定帧长送入，需将前端 256ms 块聚合成 600ms 步长
                stream_chunk = audio_array.astype(np.float32, copy=False)
                if self._streaming_audio_cache.size == 0:
                    self._streaming_audio_cache = stream_chunk
                else:
                    self._streaming_audio_cache = np.concatenate(
                        (self._streaming_audio_cache, stream_chunk)
                    )

                processed_any = False
                while self._streaming_audio_cache.size >= self.streaming_stride_samples:
                    chunk_to_infer = self._streaming_audio_cache[
                        : self.streaming_stride_samples
                    ]
                    self._streaming_audio_cache = self._streaming_audio_cache[
                        self.streaming_stride_samples :
                    ]

                    streaming_payload = self._streaming_infer(
                        np.ascontiguousarray(chunk_to_infer), is_final=False
                    )
                    processed_any = True
                    if streaming_payload is not None:
                        text = streaming_payload.get("text") or ""
                        if text:
                            merged = self._merge_streaming_text(normalize_text(text))
                            self.last_update_time = time.time()
                            if merged:
                                self.current_sentence = merged
                        elif not self._live_text:
                            self._live_text = ""
                            self.full_sentence = ""
                            self.current_sentence = ""

                        self.last_update_time = time.time()

                        confidence_val = streaming_payload.get("confidence")
                        if confidence_val is not None:
                            try:
                                self.last_partial_confidence = float(confidence_val)
                            except (TypeError, ValueError):  # pragma: no cover - 容错
                                pass

                if not processed_any:
                    audio_logger.trace(
                        "流式缓存未达到模型步长: {}/{} samples",
                        self._streaming_audio_cache.size,
                        self.streaming_stride_samples,
                    )

            # 🔧【2025-01-19 修复】移除缓冲区裁剪逻辑，解决"吞字回删"问题
            # 问题原因：在用户说话过程中截断音频缓冲区，导致get_partial_result()获得不完整的上下文
            # 解决方案：保持句内缓冲区完整，只在finalize_current_sentence()中清空缓冲区
            # 
            # ❌ 原有问题代码（已注释）：
            # max_buffer_size = self.sample_rate * 10
            # buffer_trimmed = False
            # if self.audio_buffer.size > max_buffer_size:
            #     old_buffer_size = self.audio_buffer.size
            #     self.audio_buffer = self.audio_buffer[-max_buffer_size:]  # ⬅️ 这里导致上下文丢失
            #     buffer_trimmed = True
            #     audio_logger.debug(f"缓冲区裁剪: {old_buffer_size} -> {self.audio_buffer.size}")
            
            # ✅ 现在的逻辑：
            # 1. 句内：保持完整音频缓冲区，确保get_partial_result()获得完整上下文
            # 2. 句间：在finalize_current_sentence()中彻底清空缓冲区，避免跨句子干扰

            # 🌐 基于网络标准的活动检测（轻声语音阈值）
            audio_activity_threshold = self.activity_peak_threshold
            if (
                max_amplitude > audio_activity_threshold
                or rms_amplitude > dynamic_rms_threshold
            ):
                activity_level = (
                    "高"
                    if max_amplitude > 0.1
                    else "中"
                    if max_amplitude > 0.03
                    else "低"
                )
                audio_logger.debug(
                    f"🎵 音频活动[{activity_level}]: max_amp={max_amplitude:.6f}, rms={rms_amplitude:.6f}"
                )

            # 详细的音频处理日志
            processing_time = (time.time() - chunk_start_time) * 1000
            audio_logger.debug(
                f"音频块处理完成: format={audio_format}, samples={len(audio_array)}, "
                f"max_amp={max_amplitude:.4f}, rms_amp={rms_amplitude:.4f}, "
                f"buffer_before={buffer_size_before}, buffer_after={self.audio_buffer.size}, "
                f"trimmed={buffer_trimmed}, processing_time={processing_time:.1f}ms"
            )

            # 将本次音频块持久化保存，便于故障排查
            try:
                if self.session_dir:
                    self.temp_file_counter += 1
                    chunk_file = os.path.join(self.session_dir, f"chunk_{self.temp_file_counter}_{len(audio_array)}.wav")
                    sf.write(chunk_file, np.clip(audio_array, -1.0, 1.0), self.sample_rate, subtype='PCM_16')
                    key_logger.info(f"session={self.session_id} save_chunk#{self.temp_file_counter} file={os.path.basename(chunk_file)} samples={len(audio_array)} rms={rms_amplitude:.6f}")
            except Exception as e:
                audio_logger.error(f"保存音频块失败: {str(e)}")

            # 🌐 基于网络标准的有效音频检测和质量统计
            self.quality_stats['total_chunks'] += 1
            effective_audio_threshold = 0.001  # 网络推荐的静音阈值
            
            if rms_amplitude > effective_audio_threshold:
                self.quality_stats['valid_chunks'] += 1
                
                # 更新平均RMS
                self.quality_stats['avg_rms'] = (self.quality_stats['avg_rms'] * (self.quality_stats['valid_chunks'] - 1) + rms_amplitude) / self.quality_stats['valid_chunks']
                
                # 根据RMS值分类音频质量
                if rms_amplitude > 0.05:
                    self.quality_stats['high_quality_chunks'] += 1
                    audio_logger.info(f"🎯 优质音频输入: RMS={rms_amplitude:.6f}, 时长={len(audio_array) / sample_rate:.2f}s")
                elif rms_amplitude > 0.01:
                    audio_logger.info(f"✅ 标准音频输入: RMS={rms_amplitude:.6f}, 时长={len(audio_array) / sample_rate:.2f}s") 
                else:
                    audio_logger.debug(f"🔉 轻声音频输入: RMS={rms_amplitude:.6f}, 时长={len(audio_array) / sample_rate:.2f}s")
            else:
                # 静音/噪音日志已屏蔽，避免日志污染
                pass
            
            # 定期报告质量统计（每30秒）
            if time.time() - self.quality_stats['last_quality_report'] > 30:
                self._report_quality_stats()
                self.quality_stats['last_quality_report'] = time.time()

        except Exception as e:
            audio_logger.error(f"音频块处理失败: {str(e)}")
            audio_logger.error(f"详细错误: {traceback.format_exc()}")

    def get_partial_result(self):
        """获取当前句子的实时识别结果，优先返回流式推理输出。"""

        if self._pending_synthetic_partial:
            payload = self._pending_synthetic_partial
            self._pending_synthetic_partial = None

            text = (payload.get("text") or "").strip()
            if not text:
                return None

            text = self._set_live_text(text)
            raw_text = payload.get("raw_text") or text
            try:
                confidence = float(payload.get("confidence", 0.9))
            except (TypeError, ValueError):  # pragma: no cover - 容错
                confidence = self.last_partial_confidence or 0.9

            if confidence <= 0.0:
                confidence = self.last_partial_confidence or 0.9

            self.last_partial_confidence = confidence
            self._last_streaming_text_sent = text
            self.last_update_time = time.time()
            self._pending_streaming_result = None

            confirmed_text = normalize_text("".join(self.confirmed_sentences))
            combined_text = self._combine_confirmed_and_live(confirmed_text, text)

            self._segment_revision += 1
            segment_id = self._format_segment_id()

            recognition_logger.info(
                f"[streaming] 自动标点 seg={segment_id} rev={self._segment_revision}: '{combined_text}'"
            )

            return {
                'text': text,
                'raw_text': raw_text,
                'is_partial': True,
                'confidence': confidence,
                'processing_time_ms': int(payload.get("processing_time_ms") or 0),
                'segment_id': segment_id,
                'revision': self._segment_revision,
                'combined_text': combined_text,
                'text_state': {
                    'confirmed_text': confirmed_text,
                    'candidate_text': text,
                    'full_text': combined_text,
                    'segment_id': segment_id,
                    'revision': self._segment_revision,
                },
                'source': payload.get("source", "auto_punctuation"),
            }

        if self._streaming_available and self.streaming_model is not None:
            pending = self._pending_streaming_result
            if not pending:
                return None

            text = pending.get("text") or ""
            if not text.strip():
                self._pending_streaming_result = None
                return None

            normalized_raw = normalize_text(text)
            live_text = self._merge_streaming_text(normalized_raw)
            confidence_val = pending.get("confidence")
            try:
                confidence = (
                    float(confidence_val) if confidence_val is not None else 0.85
                )
            except (TypeError, ValueError):  # pragma: no cover - 容错
                confidence = 0.85
            if confidence <= 0.0:
                confidence = self.last_partial_confidence or 0.85

            self.last_partial_confidence = confidence
            self._last_streaming_text_sent = text
            self._pending_streaming_result = None

            processing_ms = int(
                pending.get("processing_time_ms") or self._streaming_latency_ms or 0
            )

            self.quality_stats['recognition_attempts'] += 1
            if text:
                self.quality_stats['successful_recognitions'] += 1

            confirmed_text = normalize_text("".join(self.confirmed_sentences))
            combined_text = self._combine_confirmed_and_live(confirmed_text, live_text)

            self._segment_revision += 1
            segment_id = self._format_segment_id()

            recognition_logger.info(
                f"[streaming] 实时识别 seg={segment_id} rev={self._segment_revision}: '{combined_text}'"
            )

            return {
                'text': live_text,
                'raw_text': normalized_raw,
                'is_partial': True,
                'confidence': confidence,
                'processing_time_ms': processing_ms,
                'segment_id': segment_id,
                'revision': self._segment_revision,
                'combined_text': combined_text,
                'text_state': {
                    'confirmed_text': confirmed_text,
                    'candidate_text': live_text,
                    'full_text': combined_text,
                    'segment_id': segment_id,
                    'revision': self._segment_revision,
                }
            }

        # 离线兜底路径
        current_time = time.time()
        if current_time - self.last_update_time < self.chunk_duration:
            return None

        required_samples = int(self.sample_rate * self.min_audio_duration)
        if self.audio_buffer.size < required_samples:
            recognition_logger.debug(
                f"音频缓冲区不足 ({self.audio_buffer.size} < {required_samples})，跳过"
            )
            return None

        recognition_start_time = time.time()
        recognized_text = ""

        try:
            temp_filename = f"partial_{self.partial_save_counter + 1}.wav"
            temp_file = os.path.join(self.session_dir or self.temp_dir, temp_filename)

            sf.write(temp_file, np.clip(self.audio_buffer, -1.0, 1.0), self.sample_rate, subtype='PCM_16')
            self.partial_save_counter += 1

            result = recognize(temp_file)

            recognized_text = extract_text_from_result(result)

            if recognized_text:
                command_result = detect_voice_command(recognized_text)
                if command_result['is_command']:
                    recognition_logger.info(f"识别到指令: {recognized_text}，暂不处理")
                    return None

            if recognized_text == self.full_sentence:
                return None
            self.full_sentence = recognized_text
            self.last_update_time = current_time

            recognition_logger.info(f"[offline fallback] 实时识别: '{self.full_sentence}'")

            normalized_full_text = normalize_text(self.full_sentence)
            self._live_text = normalized_full_text

            self.quality_stats['recognition_attempts'] += 1
            if recognized_text:
                self.quality_stats['successful_recognitions'] += 1

            confirmed_text = normalize_text("".join(self.confirmed_sentences))
            combined_text = self._combine_confirmed_and_live(confirmed_text, normalized_full_text)

            self._segment_revision += 1
            segment_id = self._format_segment_id()

            return {
                'text': normalized_full_text,
                'is_partial': True,
                'confidence': 0.85,
                'processing_time_ms': int((time.time() - recognition_start_time) * 1000),
                'segment_id': segment_id,
                'revision': self._segment_revision,
                'combined_text': combined_text,
                'text_state': {
                    'confirmed_text': confirmed_text,
                    'candidate_text': normalized_full_text,
                    'full_text': combined_text,
                    'segment_id': segment_id,
                    'revision': self._segment_revision,
                }
            }
        except Exception as e:
            recognition_logger.error(f"实时识别失败: {e}\n{traceback.format_exc()}")
            return None

    def _analyze_semantic_completeness(self, text):
        """
        分析文本的语义完整性
        
        Args:
            text: 待分析的文本
            
        Returns:
            dict: {
                'is_complete': bool,  # 是否语义完整
                'completeness_score': float,  # 完整性得分 0-1
                'missing_elements': list,  # 缺失的语义要素
                'sentence_type': str  # 句子类型
            }
        """
        if not text or not text.strip():
            return {
                'is_complete': False,
                'completeness_score': 0.0,
                'missing_elements': ['content'],
                'sentence_type': 'empty'
            }
        
        text = text.strip()
        completeness_score = 0.0
        missing_elements = []
        
        # 🎯 基础长度检查
        if len(text) >= 2:
            completeness_score += 0.2
        else:
            missing_elements.append('sufficient_length')
        
        # 🎯 句子类型识别
        sentence_type = 'statement'  # 默认陈述句
        
        # 疑问句检测
        question_indicators = ['什么', '哪里', '怎么', '为什么', '谁', '何时', '多少', '吗', '呢']
        if any(indicator in text for indicator in question_indicators) or text.endswith('？'):
            sentence_type = 'question'
            # 疑问句通常语义相对完整
            completeness_score += 0.3
        
        # 感叹句检测
        exclamation_indicators = ['太', '真', '好', '哇', '哎呀', '天哪']
        if any(indicator in text for indicator in exclamation_indicators) or text.endswith('！'):
            sentence_type = 'exclamation'
            completeness_score += 0.3
        
        # 🎯 语法结构分析
        # 主谓宾结构检测（简化版）
        has_subject = self._detect_subject(text)
        has_predicate = self._detect_predicate(text)
        has_object = self._detect_object(text)
        
        if has_subject:
            completeness_score += 0.2
        else:
            missing_elements.append('subject')
            
        if has_predicate:
            completeness_score += 0.3
        else:
            missing_elements.append('predicate')
        
        # 🎯 语义连贯性检查
        # 检查是否有明显的连接词暗示句子未完成
        incomplete_connectors = ['但是', '不过', '然后', '接着', '另外', '而且', '所以', '因此', '如果', '虽然']
        trailing_connectors = ['的', '了', '着', '过']
        
        for connector in incomplete_connectors:
            if text.endswith(connector):
                completeness_score -= 0.3
                missing_elements.append('continuation')
                break
                
        for connector in trailing_connectors:
            if text.endswith(connector):
                completeness_score -= 0.2
                break
        
        # 🎯 标点符号检查
        if text.endswith(('。', '！', '？', '.', '!', '?')):
            completeness_score += 0.3
            sentence_type += '_punctuated'
        else:
            missing_elements.append('punctuation')
        
        # 🎯 特殊情况处理
        # 时间表达通常是完整的
        time_patterns = ['今天', '昨天', '明天', '现在', '刚才', '一会儿', '下午', '晚上', '早上']
        if any(pattern in text for pattern in time_patterns):
            completeness_score += 0.1
        
        # 限制分数范围
        completeness_score = max(0.0, min(1.0, completeness_score))
        
        return {
            'is_complete': completeness_score >= 0.6,  # 阈值：60%
            'completeness_score': completeness_score,
            'missing_elements': missing_elements,
            'sentence_type': sentence_type
        }
    
    def _detect_subject(self, text):
        """检测主语（简化版）"""
        # 人称代词
        pronouns = ['我', '你', '他', '她', '它', '我们', '你们', '他们', '她们']
        if any(pronoun in text for pronoun in pronouns):
            return True
        
        # 名词性主语的简单模式（姓名、专有名词等）
        if len(text) > 3 and any(char.isalpha() for char in text):
            return True
            
        return False
    
    def _detect_predicate(self, text):
        """检测谓语（简化版）"""
        # 动词性词汇
        verbs = ['是', '有', '在', '去', '来', '做', '说', '看', '听', '想', '能', '要', '会', '可以', '应该', '需要']
        if any(verb in text for verb in verbs):
            return True
            
        # 形容词性谓语
        adjectives = ['好', '坏', '大', '小', '多', '少', '高', '低', '快', '慢', '美', '丑']
        if any(adj in text for adj in adjectives):
            return True
            
        return False
    
    def _detect_object(self, text):
        """检测宾语（简化版）"""
        # 如果有谓语且文本较长，可能有宾语
        if self._detect_predicate(text) and len(text) > 4:
            return True
        return False

    def check_sentence_complete(self):
        """
        智能端点检测 - 判断句子完整性
        🎯【修改】判断对象从 confirmed+candidate 改为 self.full_sentence
        """
        if not self.full_sentence or not self.full_sentence.strip():
            return False

        current_time = time.time()
        silence_duration = max(
            current_time - self.last_activity_time,
            self._silence_accumulated,
        )

        # 语义完整性分析
        # 注意: _analyze_semantic_completeness 方法内部应使用 self.full_sentence
        semantic_analysis = self._analyze_semantic_completeness(self.full_sentence)

        # 智能端点判断逻辑
        if (
            self._pending_finalize_after_silence
            and silence_duration >= self.interim_punctuation_min_silence
        ):
            return True

        if (
            semantic_analysis['is_complete']
            and silence_duration >= max(0.8, self.interim_punctuation_min_silence)
        ):
            return True
        if silence_duration >= self.sentence_complete_threshold:
            return True

        return False

    def finalize_current_sentence(self):
        """确认当前句子为最终结果，并完成离线矫正与自动纠错。"""

        segment_seq = self._current_segment_seq()
        segment_id_hint = self._format_segment_id(segment_seq)

        streaming_text = (self._live_text or self.full_sentence or "").strip()

        if self._streaming_available and self.streaming_model is not None:
            flush_audio = (
                np.ascontiguousarray(self._streaming_audio_cache)
                if self._streaming_audio_cache.size > 0
                else np.array([], dtype=np.float32)
            )
            flush_result = self._streaming_infer(flush_audio, is_final=True)
            self._streaming_audio_cache = np.array([], dtype=np.float32)
            if flush_result:
                flush_text = normalize_text(flush_result.get("text") or "")
                if flush_text:
                    streaming_text = self._merge_streaming_text(flush_text)
                confidence_val = flush_result.get("confidence")
                if confidence_val is not None:
                    try:
                        self.last_partial_confidence = float(confidence_val)
                    except (TypeError, ValueError):  # pragma: no cover - 容错
                        pass

        streaming_text = (streaming_text or self._live_text or self.full_sentence or "").strip()

        offline_text, _ = self._run_offline_final_recognition()
        selected_text, source = self._select_best_final_text(streaming_text, offline_text)

        if not selected_text.strip():
            self._pending_finalize_after_silence = False
            return ""

        silence_duration = max(
            time.time() - self.last_activity_time,
            self._silence_accumulated,
        )
        punctuated_text = self.predict_punctuation(selected_text, silence_duration)
        punctuated_text = normalize_text(punctuated_text)

        corrected_text, correction_meta = self._auto_correct_text(punctuated_text)
        corrected_text = normalize_text(corrected_text)
        final_text = (corrected_text or punctuated_text).strip()

        if not final_text:
            self._pending_finalize_after_silence = False
            return ""

        self.confirmed_sentences.append(final_text)
        mode_label = "[streaming]" if self._streaming_available and self.streaming_model is not None else "[offline fallback]"
        recognition_logger.info(
            f"{mode_label} 🏁 最终确认句子 #{len(self.confirmed_sentences)}(seg={segment_id_hint}, source={source}): '{final_text}'"
        )
        if correction_meta.get("applied"):
            recognition_logger.info(
                f"🩹 自动纠错: '{punctuated_text}' -> '{final_text}', details={correction_meta.get('details')}"
            )

        self.full_sentence = ""
        self.current_sentence = ""
        self._live_text = ""
        self._segment_revision = 0
        self._last_streaming_text_sent = ""
        self.last_activity_time = time.time()
        self._silence_accumulated = 0.0
        self._pending_synthetic_partial = None
        self._pending_finalize_after_silence = False
        self._last_punctuation_text = ""
        self._last_punctuation_time = time.time()
        try:
            self.audio_buffer = np.array([], dtype=np.float32)
        except Exception:  # pragma: no cover - 防御
            self.audio_buffer = np.array([], dtype=np.float32)

        if self._streaming_available and self.streaming_model is not None:
            self.cache.clear()
            self._pending_streaming_result = None
            self._last_streaming_result = None
            self._streaming_latency_ms = 0

        final_payload = {
            "text": final_text,
            "raw_text": punctuated_text,
            "selected_source": source,
            "streaming_text": streaming_text,
            "offline_text": offline_text,
            "segment_seq": segment_seq,
            "segment_id_hint": segment_id_hint,
            "auto_correction": correction_meta.get("details") or [],
            "auto_correction_applied": bool(correction_meta.get("applied")),
        }

        self._last_final_info = final_payload
        return final_payload

    def get_final_result(self):
        """
        获取最终识别结果
        
        Returns:
            str: 最终识别文本
        """
        # 🔧【2025-01-19 修复】优先返回当前实时识别的句子
        if self.audio_buffer.size == 0:
            return self.full_sentence  # 统一使用 full_sentence

        try:
            # 使用离线模型进行最终识别
            temp_file = os.path.join(self.temp_dir, f"final_{int(time.time() * 1000)}.wav")
            sf.write(temp_file, self.audio_buffer, self.sample_rate)
            result = recognize(temp_file)
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass

            # 统一解析不同返回类型
            final_text = ''
            try:
                if isinstance(result, str):
                    final_text = result.strip()
                elif isinstance(result, dict):
                    final_text = (result.get('text') or result.get('result') or result.get('transcription') or '').strip()
                elif isinstance(result, (list, tuple)) and len(result) > 0:
                    first = result[0]
                    if isinstance(first, dict):
                        final_text = (first.get('text') or first.get('result') or '').strip()
                    else:
                        final_text = str(first).strip()
            except Exception:
                final_text = ''

            # 🔧【2025-01-19 修复】统一更新 full_sentence
            if final_text:
                # 优先使用最终识别结果，但不覆盖已有的实时识别结果（除非更准确）
                return final_text
            else:
                return self.full_sentence  # 回退到当前实时识别句子

        except Exception as e:
            print(f"最终识别失败: {str(e)}")
            return self.full_sentence  # 回退到当前实时识别句子

    def _extract_words(self, text):
        """
        提取分词结果
        
        Args:
            text: 识别文本
            
        Returns:
            list: 分词结果列表
        """
        # 简单的中文分词（可以后续接入更专业的分词工具）
        words = []
        if text:
            # 按标点符号分割
            import re
            segments = re.split(r'[，。！？；：]', text)
            for segment in segments:
                if segment.strip():
                    words.append({
                        'word': segment.strip(),
                        'confidence': 0.8  # 默认置信度
                    })
        return words

    def detect_pause(self):
        """
        检测是否有停顿
        
        Returns:
            bool: 是否检测到停顿
        """
        return time.time() - self.last_chunk_time > self.silence_threshold

    def _report_quality_stats(self):
        """报告音频质量统计"""
        stats = self.quality_stats
        if stats['total_chunks'] > 0:
            valid_ratio = stats['valid_chunks'] / stats['total_chunks']
            quality_ratio = stats['high_quality_chunks'] / max(1, stats['valid_chunks'])
            recognition_success_rate = stats['successful_recognitions'] / max(1, stats['recognition_attempts'])
            
            audio_logger.info(
                f"📊 音频质量报告: "
                f"有效率={valid_ratio:.1%}, 高质量率={quality_ratio:.1%}, "
                f"平均RMS={stats['avg_rms']:.6f}, 识别成功率={recognition_success_rate:.1%} "
                f"(总块数:{stats['total_chunks']}, 识别尝试:{stats['recognition_attempts']})"
            )

    def save_original_audio_files(self):
        """🔧 增强版本：在会话结束时输出原始PCM合并文件与WAV，支持30秒测试文件生成"""
        try:
            if not self.session_dir:
                audio_logger.warning("会话目录为空，无法保存音频")
                return
            
            raw_bytes = self.raw_pcm_accumulator.getvalue()
            if not raw_bytes:
                audio_logger.warning("无原始音频数据，跳过保存")
                return
                
            # 🔧 计算音频时长统计
            sr = int(self.first_pcm_sample_rate) if self.first_pcm_sample_rate else int(self.sample_rate)
            pcm_int16 = np.frombuffer(raw_bytes, dtype=np.int16)
            duration_seconds = len(pcm_int16) / sr
            
            audio_logger.info(f"🎤 原始音频统计: {len(raw_bytes)} bytes, {len(pcm_int16)} 样本, {duration_seconds:.2f}秒, 采样率{sr}Hz")
            
            # 原始PCM落盘
            raw_pcm_path = os.path.join(self.session_dir, 'original_raw.pcm')
            with open(raw_pcm_path, 'wb') as f:
                f.write(raw_bytes)
            audio_logger.info(f"💾 原始PCM已保存: {raw_pcm_path}")

            # 生成完整WAV（不做任何处理）
            try:
                pcm_float = (pcm_int16.astype(np.float32) / 32768.0).clip(-1.0, 1.0)
                raw_wav_path = os.path.join(self.session_dir, 'original_raw.wav')
                sf.write(raw_wav_path, pcm_float, sr, subtype='PCM_16')
                
                # 生成音频统计信息
                audio_stats = {
                    'duration': duration_seconds,
                    'sample_rate': sr,
                    'samples': len(pcm_int16),
                    'channels': 1,
                    'rms': np.sqrt(np.mean(pcm_float**2)),
                    'peak': np.max(np.abs(pcm_float)),
                    'dynamic_range': np.max(pcm_float) - np.min(pcm_float)
                }
                
                # 保存音频统计信息
                stats_path = os.path.join(self.session_dir, 'audio_stats.json')
                with open(stats_path, 'w', encoding='utf-8') as f:
                    json.dump(audio_stats, f, ensure_ascii=False, indent=2)
                    
                audio_logger.info(f"✅ 原始音频已生成: {raw_wav_path}")
                audio_logger.info(f"📊 音频统计: RMS={audio_stats['rms']:.4f}, Peak={audio_stats['peak']:.4f}, 动态范围={audio_stats['dynamic_range']:.4f}")
                key_logger.info(f"session={self.session_id} original_saved wav={os.path.basename(raw_wav_path)} duration={duration_seconds:.2f}s sr={sr} samples={len(pcm_int16)}")
                
                # 🔧 如果音频超过30秒，生成截取版本用于测试
                if duration_seconds > 30:
                    test_samples = 30 * sr  # 30秒对应的样本数
                    test_audio = pcm_float[:test_samples]
                    test_wav_path = os.path.join(self.session_dir, 'test_30s.wav')
                    sf.write(test_wav_path, test_audio, sr, subtype='PCM_16')
                    audio_logger.info(f"🎧 30秒测试音频已生成: {test_wav_path}")
                    
            except Exception as wav_e:
                audio_logger.error(f"原始WAV生成失败: {wav_e}")
                import traceback
                audio_logger.error(traceback.format_exc())
                
        except Exception as e:
            audio_logger.error(f"保存原始音频失败: {e}")
            import traceback
            audio_logger.error(traceback.format_exc())
