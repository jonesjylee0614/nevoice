"""StreamingEngine push/flush 实现。

使用 FunASRStreamer 进行完整的 VAD + 流式 ASR + 纠错 + 标点 + ITN。

🚀 优化策略：
1. 离线纠正异步化：在线识别结果立即返回，离线纠正在后台线程执行
2. 这样实时识别不会被离线ASR阻塞，大幅降低延迟
"""

from __future__ import annotations

import os
import re
import time
import uuid
import wave
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, List, Optional, Tuple, Callable

from loguru import logger
from server.logging import ws_logger

from .loader import ModelLoader, FunASRModelBundle
from .state import StreamingState
from .text_accumulator import TextAccumulator
from .funasr_streamer import FunASRStreamer, FunASRStreamerConfig, FunASRStreamerState
from .segment_merge import SegmentMergeManager

# 导入同音词修正器
try:
    from zh_correct.homophone_corrector import correct_homophones
    HOMOPHONE_CORRECTION_AVAILABLE = True
except ImportError:
    HOMOPHONE_CORRECTION_AVAILABLE = False
    logger.warning("同音词修正模块不可用")


# 音频片段保存目录
AUDIO_SEGMENT_DIR = "data/meeting/audio_segments"

# 是否启用自动声纹匹配（可以在运行时配置）
ENABLE_AUTO_VOICEPRINT = True


# 中文句末标点正则 - 用于基于语义的二次分段
SENTENCE_END_PATTERN = re.compile(r'([。！？!?])')
# 检查是否只包含标点符号的正则
PUNCTUATION_ONLY_PATTERN = re.compile(r'^[。！？!?，,、；;：:""''""\'\'()（）【】\[\]《》<>—\-…·\s]+$')
# 开头的标点符号正则（需要移除的）
LEADING_PUNCTUATION_PATTERN = re.compile(r'^[。！？!?，,、；;：:""''""\'\'()（）【】\[\]《》<>—\-…·\s]+')
# 移除所有标点符号的正则（用于计算纯文字长度）
ALL_PUNCTUATION_PATTERN = re.compile(r'[。！？!?，,、；;：:""''""\'\'()（）【】\[\]《》<>—\-…·\s]+')

# 无意义填充词集合（会被过滤的短句内容）
# 这些词单独出现时通常是背景噪音、叹息、杂声等，语义价值很低
FILLER_WORDS = {
    '嗯', '啊', '呃', '额', '哦', '哎', '嘿', '噢', '唔',
    '是', '对', '好', '行', '嗯嗯', '哦哦', '啊啊', '嘘',
    '嗯啊', '啊嗯', '是是', '对对', '好好', '行行',
    '然后', '那个', '这个', '就是', '所以',
    # 补充：短促回应和叹息
    '嗨', '喂', '诶', '欸', '呀', '呐', '哇', '哈', '嘻',
    '嗯哼', '啊哈', '哎呀', '哦哦哦', '啊啊啊',
}

# 最小有效句子长度（去掉标点后）
MIN_MEANINGFUL_LENGTH = 2

# 最小有效语音段时长（毫秒）
# 如果时长小于此值且是填充词，则过滤
MIN_MEANINGFUL_DURATION_MS = 500


def is_meaningless_sentence(text: str, duration_ms: int = 0) -> bool:
    """
    判断句子是否无意义（应该被过滤）。
    
    过滤标准：
    1. 去掉标点后长度小于 MIN_MEANINGFUL_LENGTH（默认2）
    2. 只包含填充词（嗯、是、啊等）
    3. 🎯 新增：时长小于 MIN_MEANINGFUL_DURATION_MS 且是填充词
    
    Args:
        text: 待检查的文本
        duration_ms: 语音段时长（毫秒），0 表示不检查时长
        
    Returns:
        True 表示无意义应过滤，False 表示有意义应保留
    """
    if not text:
        return True
    
    # 去掉所有标点符号
    pure_text = ALL_PUNCTUATION_PATTERN.sub('', text)
    
    # 空文本
    if not pure_text:
        return True
    
    # 长度检查：少于最小长度的句子大概率是噪音
    if len(pure_text) < MIN_MEANINGFUL_LENGTH:
        return True
    
    # 填充词检查：如果纯文本完全是填充词，则过滤
    if pure_text in FILLER_WORDS:
        return True
    
    # 🎯 时长+填充词组合检查：短时长的疑似填充词更可能是噪音
    # 即使文本长度>=2，如果时长很短且包含填充词成分，也过滤
    if duration_ms > 0 and duration_ms < MIN_MEANINGFUL_DURATION_MS:
        # 检查是否以填充词开头或结尾
        for filler in FILLER_WORDS:
            if pure_text.startswith(filler) or pure_text.endswith(filler):
                # 如果去掉填充词后剩余内容很少，则过滤
                remaining = pure_text.replace(filler, '', 1)
                if len(remaining) < MIN_MEANINGFUL_LENGTH:
                    return True
    
    return False


def clean_sentence_text(text: str) -> str:
    """
    清理句子文本：
    1. 移除开头的标点符号
    2. 如果结尾没有句末标点，添加句号
    
    Args:
        text: 待清理的文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return text
    
    # 1. 移除开头的标点符号
    text = LEADING_PUNCTUATION_PATTERN.sub('', text)
    
    if not text:
        return text
    
    # 2. 检查结尾是否有句末标点，如果没有则添加句号
    if text and not SENTENCE_END_PATTERN.search(text[-1]):
        text = text + '。'
    
    return text


# 重复字符过滤正则：去除连续重复 1-3 个字符重复 2 次以上的情况
# 例如："这这这这" -> "这"，"一个一个一个" -> "一个"
REPEATED_PATTERN = re.compile(r'(.{1,3})\1{2,}')


def remove_repeated_chars(text: str) -> str:
    """
    去除文本中的重复字符/短语。
    
    当键盘敲击、背景噪音等被误识别时，常会产生重复字符，
    如 "这这这这这" 或 "一个一个一个"。
    
    Args:
        text: 待处理的文本
        
    Returns:
        去重后的文本
    """
    if not text:
        return text
    
    # 去除连续重复的字符或短语
    # (.{1,3})\1{2,} 匹配 1-3 个字符重复 3 次以上
    cleaned = REPEATED_PATTERN.sub(r'\1', text)
    
    # 记录去重情况
    if cleaned != text:
        ws_logger.debug(f"[去重] '{text}' -> '{cleaned}'")
    
    return cleaned


def split_by_punctuation(text: str) -> List[str]:
    """
    基于句末标点将文本分割成语义完整的句子。
    
    Args:
        text: 待分割的文本
        
    Returns:
        分割后的句子列表
    """
    if not text:
        return []
    
    # 按句末标点分割，保留标点
    parts = SENTENCE_END_PATTERN.split(text)
    
    sentences = []
    current = ""
    
    for part in parts:
        if not part:
            continue
        current += part
        # 如果当前部分是标点，则完成一个句子
        if SENTENCE_END_PATTERN.match(part):
            stripped = current.strip()
            # 只保存有实际内容的句子（不能只是标点符号）
            if stripped and not PUNCTUATION_ONLY_PATTERN.match(stripped):
                sentences.append(stripped)
            # 如果只是标点，直接丢弃，避免产生单独的标点句子
            current = ""
    
    # 处理剩余的没有句末标点的文本
    if current.strip():
        # 如果有之前的句子，尝试合并到最后一个（可能是不完整的）
        # 否则作为新句子
        sentences.append(current.strip())
    
    return sentences if sentences else [text]


class StreamingEngine:
    """处理音频 chunk 并输出识别事件。
    
    🚀 支持离线纠正异步化：
    - 在线识别结果立即返回给前端
    - 离线纠正在后台线程池执行
    - 纠正完成后通过回调函数发送结果
    """

    def __init__(self) -> None:
        self._loader = ModelLoader.current()
        self._funasr_streamer: Optional[FunASRStreamer] = None
        self._funasr_state_map: dict[str, FunASRStreamerState] = {}
        
        # 🚀 异步 ASR 的线程池和回调
        self._async_executor: Optional[ThreadPoolExecutor] = None
        self._async_callbacks: dict[str, Callable] = {}  # session_id -> callback
        self._async_enabled: bool = False
        self._async_online_enabled: bool = False
        
        # 🚀 在线 ASR 异步缓存管理（用于增量识别）
        self._online_cache_map: dict[str, dict] = {}
        
        # 🎯 片段合并管理器（同步/异步路径共用）
        self._segment_merge_manager: Optional[SegmentMergeManager] = None
        
        self._init_funasr_streamer()

    def _init_funasr_streamer(self) -> None:
        """初始化 FunASR 流式组件。"""
        try:
            funasr_bundle = self._loader.get_bundle()
            if not funasr_bundle.is_valid:
                logger.error("FunASR 模型加载不完整，流式识别将不可用")
                return
            
            # 从配置创建 FunASRStreamerConfig
            config = funasr_bundle.config
            audio_config = config.get("audio", {})
            mode_config = config.get("mode", {})
            features = config.get("features", {})
            itn_config = config.get("itn", {})
            vad_config = config.get("vad", {})  # VAD 分段参数
            segment_merge_config = config.get("segment_merge", {})  # 🎯 片段合并配置
            
            # 🚀 读取异步配置
            self._async_enabled = features.get("async_offline_correction", False)
            self._async_online_enabled = features.get("async_online_asr", False)
            
            if self._async_enabled or self._async_online_enabled:
                # 为离线和在线 ASR 创建共享的线程池
                self._async_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="asr_async_")
                logger.info(
                    f"🚀 异步化已启用: offline={self._async_enabled}, online={self._async_online_enabled}"
                )
            
            # 🎯 初始化片段合并管理器
            self._segment_merge_manager = SegmentMergeManager.current(segment_merge_config)
            logger.info(
                f"🎯 片段合并已初始化: enabled={self._segment_merge_manager.enabled}, "
                f"max_gap_ms={self._segment_merge_manager.config.max_gap_ms}"
            )
            
            streamer_config = FunASRStreamerConfig(
                mode=mode_config.get("default", "2pass"),
                chunk_interval=audio_config.get("chunk_interval", 10),
                chunk_size=audio_config.get("chunk_size", [5, 10, 5]),
                sample_rate=audio_config.get("sample_rate", 16000),
                enable_vad=features.get("enable_vad", True),
                enable_punc=features.get("enable_punc", True),
                enable_itn=features.get("enable_itn", True),
                itn_language=itn_config.get("language", "zh"),
                itn_cache_dir=itn_config.get("cache_dir"),
                debug=features.get("debug", False),
                # VAD 分段参数 - 控制语音分段敏感度
                vad_max_single_segment_time=vad_config.get("max_single_segment_time", 45000),
                vad_max_end_silence_time=vad_config.get("max_end_silence_time", 1200),
                vad_speech_noise_thres=vad_config.get("speech_noise_thres", 0.7),
                # 异步配置
                async_offline_correction=self._async_enabled,
                async_online_asr=self._async_online_enabled,
            )
            
            self._funasr_streamer = FunASRStreamer(
                model_asr=funasr_bundle.model_asr,
                model_asr_online=funasr_bundle.model_asr_online,
                model_vad=funasr_bundle.model_vad,
                model_punc=funasr_bundle.model_punc,
                config=streamer_config,
            )
            
            logger.info(f"FunASR 流式引擎初始化成功 (mode={streamer_config.mode})")
        except Exception as e:
            logger.error(f"FunASR 流式引擎初始化失败: {e}")

    def get_funasr_state(self, state: StreamingState) -> Optional[FunASRStreamerState]:
        """获取或创建 FunASR 状态（公共方法，用于外部同步配置）。
        
        与官方 demo 对齐：允许外部直接设置 is_speaking/online_is_final 状态。
        """
        if self._funasr_streamer is None:
            return None
        if state.session_id not in self._funasr_state_map:
            funasr_state = self._funasr_streamer.create_state()
            funasr_state.session_id = state.session_id
            funasr_state.wav_name = state.wav_name
            funasr_state.hotwords = state.hotwords
            self._funasr_state_map[state.session_id] = funasr_state
        elif not getattr(self._funasr_state_map[state.session_id], "session_id", ""):
            # 旧状态补上 session 便于日志聚合
            self._funasr_state_map[state.session_id].session_id = state.session_id
        return self._funasr_state_map[state.session_id]
    
    # 向后兼容别名
    _get_funasr_state = get_funasr_state
    
    def register_async_callback(self, session_id: str, callback: Callable[[dict], None]) -> None:
        """注册异步离线纠正的回调函数。
        
        当离线纠正完成时，会通过此回调发送结果。
        
        Args:
            session_id: 会话 ID
            callback: 回调函数，接收 event dict 作为参数
        """
        if self._async_enabled:
            self._async_callbacks[session_id] = callback
            ws_logger.info(f"[async] session={session_id} registered callback")
    
    def unregister_async_callback(self, session_id: str) -> None:
        """注销异步回调。"""
        self._async_callbacks.pop(session_id, None)
    
    def _save_audio_segment(
        self,
        audio_data: bytes,
        session_id: str,
        segment_id: str,
    ) -> Optional[str]:
        """
        保存音频片段到文件。
        
        Args:
            audio_data: PCM音频数据（16kHz, 16bit, mono）
            session_id: 会话ID
            segment_id: 片段ID
            
        Returns:
            音频文件的相对路径，如果保存失败则返回None
        """
        try:
            t0 = time.time()
            # 确保目录存在
            os.makedirs(AUDIO_SEGMENT_DIR, exist_ok=True)
            
            # 生成文件名
            timestamp = int(time.time() * 1000)
            filename = f"{session_id}_{segment_id}_{timestamp}.wav"
            filepath = os.path.join(AUDIO_SEGMENT_DIR, filename)
            
            # 写入WAV文件
            with wave.open(filepath, 'wb') as wav_file:
                wav_file.setnchannels(1)  # mono
                wav_file.setsampwidth(2)  # 16bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(audio_data)
            
            elapsed_ms = (time.time() - t0) * 1000
            ws_logger.info(
                f"[audio] session={session_id} segment={segment_id} "
                f"saved bytes={len(audio_data)} path={filepath} took={elapsed_ms:.1f}ms"
            )
            
            # 返回 URL 友好的路径（使用正斜杠）
            url_path = filepath.replace("\\", "/")
            return f"/{url_path}"
            
        except Exception as e:
            ws_logger.error(f"[audio] session={session_id} save failed: {e}")
            logger.error(f"保存音频片段失败: {e}")
            return None
    
    def _match_speaker(self, audio_data: bytes, session_id: str) -> Optional[dict]:
        """
        执行声纹匹配。
        
        Args:
            audio_data: PCM音频数据（16kHz, 16bit, mono）
            
        Returns:
            声纹匹配结果，如果失败返回None
        """
        if not ENABLE_AUTO_VOICEPRINT:
            return None
        
        try:
            t0 = time.time()
            from server.routes.meeting_mdt import match_speaker_from_pcm
            result = match_speaker_from_pcm(audio_data, sample_rate=16000)
            elapsed_ms = (time.time() - t0) * 1000
            
            if result.get('recognized'):
                ws_logger.info(
                    f"[voiceprint] session={session_id} recognized={result.get('speaker_name')} "
                    f"score={result.get('recognition_score')} took={elapsed_ms:.1f}ms"
                )
            else:
                ws_logger.info(
                    f"[voiceprint] session={session_id} no_match note={result.get('recognition_note')} "
                    f"took={elapsed_ms:.1f}ms"
                )
            
            return result
        except Exception as e:
            ws_logger.warning(f"[voiceprint] session={session_id} match failed: {e}")
            logger.warning(f"声纹匹配失败: {e}")
            return None

    def push(self, audio_chunk: bytes, state: StreamingState) -> List[dict]:
        """
        处理音频 chunk。
        
        Args:
            audio_chunk: 音频数据
            state: 会话状态
            
        Returns:
            生成的事件列表
        """
        t_push_start = time.time()
        state.mark_activity(int(time.time() * 1000))
        
        # 计算音频时长用于延迟分析
        audio_duration_ms = len(audio_chunk) // 32  # 16kHz 16bit = 32 bytes/ms
        
        if self._funasr_streamer is None:
            logger.warning("FunASR 流式引擎未初始化")
            return []
        
        funasr_state = self._get_funasr_state(state)
        
        # 同步状态（与官方 demo 对齐）
        funasr_state.is_speaking = state.metrics.get("is_speaking", True)
        funasr_state.hotwords = state.hotwords
        funasr_state.wav_name = state.wav_name
        
        # 同步配置到 streamer（与官方 demo 对齐：配置透传）
        if hasattr(self._funasr_streamer, 'config'):
            old_mode = self._funasr_streamer.config.mode
            self._funasr_streamer.config.mode = state.mode
            self._funasr_streamer.config.chunk_interval = state.chunk_interval
            self._funasr_streamer.config.chunk_size = state.chunk_size
            self._funasr_streamer.config.encoder_chunk_look_back = state.encoder_chunk_look_back
            self._funasr_streamer.config.decoder_chunk_look_back = state.decoder_chunk_look_back
            self._funasr_streamer.config.enable_itn = state.enable_itn
            
            # 关键日志：记录配置同步（仅在首次或配置变化时）
            if not hasattr(state, '_config_logged') or old_mode != state.mode:
                logger.info(
                    f"[StreamingEngine] config sync: session={state.session_id}, "
                    f"mode={state.mode}, chunk_interval={state.chunk_interval}, "
                    f"chunk_size={state.chunk_size}, itn={state.enable_itn}, "
                    f"is_speaking={funasr_state.is_speaking}"
                )
                state._config_logged = True
        
        try:
            t_process_start = time.time()
            events = self._funasr_streamer.process_chunk(audio_chunk, funasr_state)
            t_process_end = time.time()
            process_ms = (t_process_end - t_process_start) * 1000
            
            # 计算实时因子 RTF
            rtf = process_ms / max(audio_duration_ms, 1)
            chunk_count = state.metrics.get('chunk_count', 0)
            
            # 【关键诊断】详细的处理时间日志
            # 短期优化：采样输出减少日志I/O
            if rtf > 1.0:
                # RTF > 1 意味着处理速度跟不上实时，会产生延迟累积
                # 每50个chunk输出一次，或RTF>2.0时始终输出
                if chunk_count % 50 == 0 or rtf > 2.0:
                    ws_logger.warning(
                        f"[ENGINE-SLOW] session={state.session_id} chunk#{chunk_count} "
                        f"RTF={rtf:.2f} (FALLING BEHIND!) "
                        f"process_ms={process_ms:.1f} audio_ms={audio_duration_ms} "
                        f"events={len(events)} funasr_frames={len(funasr_state.frames)} "
                        f"speech_start={funasr_state.speech_start}"
                    )
            elif process_ms > 100 or len(events) > 0 or chunk_count % 50 == 0:
                ws_logger.info(
                    f"[ENGINE] session={state.session_id} chunk#{chunk_count} "
                    f"RTF={rtf:.2f} process_ms={process_ms:.1f} audio_ms={audio_duration_ms} "
                    f"events={len(events)} is_speaking={state.metrics.get('is_speaking')}"
                )
        except Exception as e:
            logger.error(f"[engine] FunASR 处理失败: {e}")
            ws_logger.error(f"[engine] session={state.session_id} FunASR 处理失败: {e}")
            return []
        
        # 转换事件格式
        result_events = []
        accumulator: TextAccumulator = state.text_accumulator or TextAccumulator()
        state.text_accumulator = accumulator
        
        for event in events:
            # 🚀 处理异步离线纠正事件
            if event.type == "pending_correction":
                # 异步模式：提交到线程池执行离线 ASR
                if self._async_enabled and self._async_executor and event.audio_data:
                    # 捕获必要的上下文
                    session_id = state.session_id
                    hotwords = dict(state.hotwords) if state.hotwords else None
                    start_offset_ms = event.start_offset_ms
                    duration_ms = event.duration_ms
                    audio_data = event.audio_data
                    segment_id = state.ensure_segment()
                    
                    def async_offline_task():
                        """异步执行离线 ASR 并通过回调发送结果"""
                        try:
                            t_start = time.time()
                            offline_result = self._funasr_streamer.run_offline_asr_standalone(
                                audio_bytes=audio_data,
                                hotwords=hotwords,
                                start_offset_ms=start_offset_ms,
                                duration_ms=duration_ms,
                            )
                            
                            if offline_result and offline_result.text:
                                # 清理文本
                                cleaned_text = clean_sentence_text(offline_result.text)
                                
                                # 空文本直接跳过
                                if not cleaned_text or not cleaned_text.strip():
                                    return
                                
                                # 同音词修正
                                if HOMOPHONE_CORRECTION_AVAILABLE:
                                    try:
                                        corrected_text = correct_homophones(cleaned_text)
                                        if corrected_text != cleaned_text:
                                            cleaned_text = corrected_text
                                    except Exception:
                                        pass
                                
                                # 声纹匹配
                                speaker_info = self._match_speaker(audio_data, session_id)
                                
                                # 保存音频
                                audio_path = self._save_audio_segment(audio_data, session_id, segment_id)
                                
                                # 构建结果事件
                                result_event = {
                                    "type": "correction",
                                    "mode": "2pass-offline-async",
                                    "text": cleaned_text,
                                    "is_final": True,
                                    "session_id": session_id,
                                    "segment_id": segment_id,
                                    "start_offset_ms": start_offset_ms,
                                    "end_offset_ms": start_offset_ms + duration_ms,
                                    "duration_ms": duration_ms,
                                    "audio_path": audio_path,
                                    "audio_data": audio_data,  # 用于合并后重新保存
                                    "async_latency_ms": int((time.time() - t_start) * 1000),
                                }
                                
                                if speaker_info:
                                    result_event["speaker_info"] = speaker_info
                                
                                # 通过回调发送结果
                                callback = self._async_callbacks.get(session_id)
                                if callback:
                                    # 🎯 通过片段合并模块处理（异步路径也使用同一套逻辑）
                                    if self._segment_merge_manager and self._segment_merge_manager.enabled:
                                        merged_events = self._segment_merge_manager.process_event(
                                            session_id, result_event
                                        )
                                        for evt in merged_events:
                                            evt["async_latency_ms"] = int((time.time() - t_start) * 1000)
                                            callback(evt)
                                            ws_logger.info(
                                                f"[ASYNC] session={session_id} merged correction sent, "
                                                f"text_len={len(evt.get('text', ''))}"
                                            )
                                    else:
                                        callback(result_event)
                                        ws_logger.info(
                                            f"[ASYNC] session={session_id} correction sent via callback, "
                                            f"text_len={len(cleaned_text)}, latency_ms={result_event['async_latency_ms']}"
                                        )
                                else:
                                    ws_logger.warning(
                                        f"[ASYNC] session={session_id} no callback registered, result dropped"
                                    )
                        except Exception as e:
                            ws_logger.error(f"[ASYNC] session={session_id} offline_asr failed: {e}")
                    
                    # 提交异步任务
                    self._async_executor.submit(async_offline_task)
                    ws_logger.info(f"[ASYNC] session={state.session_id} offline_asr task submitted")
                continue
            
            # 🚀 处理异步在线 ASR 事件
            if event.type == "pending_online":
                if self._async_online_enabled and self._async_executor and event.audio_data:
                    session_id = state.session_id
                    hotwords = dict(state.hotwords) if state.hotwords else None
                    is_final = event.is_final
                    audio_data = event.audio_data
                    
                    # 获取或创建在线 ASR 缓存
                    online_cache = self._online_cache_map.get(session_id, {})
                    
                    def async_online_task():
                        """异步执行在线 ASR 并通过回调发送结果"""
                        try:
                            t_start = time.time()
                            online_result, new_cache = self._funasr_streamer.run_online_asr_standalone(
                                audio_bytes=audio_data,
                                is_final=is_final,
                                hotwords=hotwords,
                                online_cache=online_cache,
                            )
                            
                            # 更新缓存
                            self._online_cache_map[session_id] = new_cache
                            
                            if online_result and online_result.text:
                                # 🎯 过滤无意义短句
                                if is_meaningless_sentence(online_result.text):
                                    return
                                
                                # 构建结果事件
                                # 🔧 mode 使用 "2pass-online" 而不是 "2pass-online-async"
                                # 这样前端可以统一处理，不需要额外判断
                                result_event = {
                                    "type": "partial",
                                    "mode": "2pass-online",  # 与同步模式保持一致
                                    "text": online_result.text,
                                    "is_final": False,
                                    "session_id": session_id,
                                    "async_latency_ms": int((time.time() - t_start) * 1000),
                                }
                                
                                # 通过回调发送结果
                                callback = self._async_callbacks.get(session_id)
                                if callback:
                                    callback(result_event)
                                    ws_logger.debug(
                                        f"[ASYNC] session={session_id} online sent via callback, "
                                        f"text_len={len(online_result.text)}"
                                    )
                        except Exception as e:
                            ws_logger.error(f"[ASYNC] session={session_id} online_asr failed: {e}")
                    
                    # 提交异步任务
                    self._async_executor.submit(async_online_task)
                continue
            
            text = event.text
            if not text:
                continue
            
            if event.type == "partial":
                # 🎯 去除重复字符（键盘敲击等噪音可能产生重复）
                text = remove_repeated_chars(text)
                
                # 🎯 过滤无意义短句（partial 也过滤，避免干扰实时预览）
                if is_meaningless_sentence(text):
                    ws_logger.debug(f"[filter] session={state.session_id} partial 过滤无意义: '{text}'")
                    continue
                
                # 实时 partial 结果不分段
                revision = state.next_revision()
                segment_id = state.ensure_segment()
                
                # 🎯 累积 partial 文本，供前端覆写显示
                full_text = state.append_partial_text(text)
                
                snapshot = accumulator.update_partial(text, revision)
                result_event = {
                    "type": "partial",
                    "mode": event.mode,
                    "revision": revision,
                    "text": text,  # 增量文本（兼容旧逻辑）
                    "full_text": full_text,  # 🎯 累积的完整文本（前端覆写用）
                    "is_final": False,
                    "session_id": state.session_id,
                    "segment_id": segment_id,
                    "text_state": snapshot,
                }
                result_events.append(result_event)
            elif event.type == "correction":  # correction / final - 通过片段合并模块处理
                # 🎯 片段合并模块处理：短句优先合并，不是直接过滤
                
                # 获取原始时间信息
                total_start_ms = event.start_offset_ms
                total_duration_ms = event.duration_ms
                total_end_ms = total_start_ms + total_duration_ms
                
                # 🎯 去除重复字符（键盘敲击等噪音可能产生重复）
                text = remove_repeated_chars(text)
                
                # 清理文本：移除开头标点，确保结尾有标点
                cleaned_text = clean_sentence_text(text)
                
                # 空文本直接跳过
                if not cleaned_text or not cleaned_text.strip():
                    continue
                
                # 声纹匹配（使用整个 VAD 段的音频）
                speaker_info = None
                if event.audio_data:
                    speaker_info = self._match_speaker(event.audio_data, state.session_id)
                
                revision = state.next_revision()
                segment_id = state.ensure_segment()
                snapshot = accumulator.apply_correction(cleaned_text)
                
                # 保存整个 VAD 段的音频
                audio_path = None
                if event.audio_data:
                    audio_path = self._save_audio_segment(
                        event.audio_data,
                        state.session_id,
                        segment_id
                    )
                
                # 同音词修正（热词替换）
                if HOMOPHONE_CORRECTION_AVAILABLE:
                    try:
                        corrected_text = correct_homophones(cleaned_text)
                        if corrected_text != cleaned_text:
                            ws_logger.debug(f"[同音修正] '{cleaned_text}' → '{corrected_text}'")
                            cleaned_text = corrected_text
                    except Exception as e:
                        ws_logger.warning(f"同音词修正失败: {e}")
                
                result_event = {
                    "type": "correction",
                    "mode": event.mode,
                    "revision": revision,
                    "text": cleaned_text,  # 完整文本，带标点，已清理
                    "is_final": event.is_final,
                    "session_id": state.session_id,
                    "segment_id": segment_id,
                    "text_state": snapshot,
                    # 时间信息
                    "start_offset_ms": total_start_ms,
                    "end_offset_ms": total_end_ms,
                    "duration_ms": total_duration_ms,
                    # 音频路径 - 整个 VAD 段的音频
                    "audio_path": audio_path,
                    # 音频数据 - 用于合并后重新保存
                    "audio_data": event.audio_data,
                }
                
                # 添加声纹匹配结果
                if speaker_info:
                    result_event["speaker_info"] = speaker_info
                
                if event.is_final:
                    state.mark_segment_final(segment_id)
                
                # 🎯 清空累积的 partial 文本（这段语音已经结束）
                state.clear_partial_text()
                
                # 🎯 通过片段合并模块处理
                # 短句优先尝试合并，只有无法合并时才按阈值过滤
                if self._segment_merge_manager and self._segment_merge_manager.enabled:
                    merged_events = self._segment_merge_manager.process_event(
                        state.session_id, result_event
                    )
                    result_events.extend(merged_events)
                else:
                    # 合并功能禁用，直接输出
                    result_events.append(result_event)
        
        # 【诊断日志】push方法总耗时
        t_push_end = time.time()
        push_total_ms = (t_push_end - t_push_start) * 1000
        push_rtf = push_total_ms / max(audio_duration_ms, 1)
        
        if push_rtf > 1.0 or len(result_events) > 0:
            ws_logger.info(
                f"[ENGINE-PUSH] session={state.session_id} "
                f"total_ms={push_total_ms:.1f} audio_ms={audio_duration_ms} RTF={push_rtf:.2f} "
                f"result_events={len(result_events)}"
            )
        
        return result_events

    def flush(self, state: StreamingState) -> List[dict]:
        """
        刷新所有缓冲，输出最终结果。
        
        Args:
            state: 会话状态
            
        Returns:
            生成的事件列表
        """
        if self._funasr_streamer is None:
            return []
        
        if state.session_id not in self._funasr_state_map:
            # 即使没有 funasr_state，也要刷新 segment_merge 缓冲区
            if self._segment_merge_manager and self._segment_merge_manager.enabled:
                return self._segment_merge_manager.flush_session(state.session_id)
            return []
        
        funasr_state = self._funasr_state_map[state.session_id]
        
        try:
            t_flush_start = time.time()
            events = self._funasr_streamer.flush(funasr_state)
            flush_ms = (time.time() - t_flush_start) * 1000
            ws_logger.info(
                f"[perf] session={state.session_id} engine.flush took={flush_ms:.1f}ms events={len(events)}"
            )
        except Exception as e:
            logger.error(f"[engine] FunASR flush 失败: {e}")
            ws_logger.error(f"[engine] session={state.session_id} FunASR flush 失败: {e}")
            events = []
        
        # 清理状态
        del self._funasr_state_map[state.session_id]
        
        # 转换事件格式，与 push 方法保持一致
        result_events = []
        accumulator: TextAccumulator = state.text_accumulator or TextAccumulator()
        state.text_accumulator = accumulator
        
        for event in events:
            text = event.text
            if not text:
                continue
            
            # 获取时间信息
            start_offset_ms = getattr(event, 'start_offset_ms', 0)
            duration_ms = getattr(event, 'duration_ms', 0)
            end_offset_ms = start_offset_ms + duration_ms
            
            # 清理文本：移除开头标点，确保结尾有标点
            cleaned_text = clean_sentence_text(text)
            if not cleaned_text:
                continue
            
            # 声纹匹配（使用整个 VAD 段的音频）
            speaker_info = None
            audio_data = getattr(event, 'audio_data', None)
            if audio_data:
                speaker_info = self._match_speaker(audio_data, state.session_id)
            
            revision = state.next_revision()
            segment_id = state.ensure_segment()
            
            # 保存整个 VAD 段的音频
            audio_path = None
            if audio_data:
                audio_path = self._save_audio_segment(
                    audio_data,
                    state.session_id,
                    segment_id
                )
            
            snapshot = accumulator.apply_correction(cleaned_text)
            result_event = {
                "type": "correction",
                "mode": event.mode,
                "revision": revision,
                "text": cleaned_text,
                "is_final": True,
                "session_id": state.session_id,
                "segment_id": segment_id,
                "text_state": snapshot,
                "start_offset_ms": start_offset_ms,
                "end_offset_ms": end_offset_ms,
                "duration_ms": duration_ms,
                # 音频路径 - 整个 VAD 段的音频
                "audio_path": audio_path,
                # 音频数据 - 用于合并后重新保存
                "audio_data": audio_data,
            }
            
            # 添加声纹匹配结果
            if speaker_info:
                result_event["speaker_info"] = speaker_info
            
            state.mark_segment_final(segment_id)
            
            # 🎯 通过片段合并模块处理
            if self._segment_merge_manager and self._segment_merge_manager.enabled:
                merged_events = self._segment_merge_manager.process_event(
                    state.session_id, result_event
                )
                result_events.extend(merged_events)
            else:
                result_events.append(result_event)
        
        # 🎯 刷新片段合并缓冲区，输出所有待处理的片段
        if self._segment_merge_manager and self._segment_merge_manager.enabled:
            flush_events = self._segment_merge_manager.flush_session(state.session_id)
            result_events.extend(flush_events)
            ws_logger.info(
                f"[segment_merge] session={state.session_id} flush 输出 {len(flush_events)} 个缓冲事件"
            )
        
        return result_events

    def cleanup_session(self, session_id: str) -> None:
        """清理会话状态。"""
        if session_id in self._funasr_state_map:
            del self._funasr_state_map[session_id]
        # 清理在线 ASR 缓存
        if session_id in self._online_cache_map:
            del self._online_cache_map[session_id]
        # 清理异步回调
        self.unregister_async_callback(session_id)
        # 🎯 清理片段合并缓冲区
        if self._segment_merge_manager:
            self._segment_merge_manager.cleanup_session(session_id)

    @property
    def is_ready(self) -> bool:
        """检查引擎是否就绪。"""
        return self._funasr_streamer is not None
    
    # 向后兼容
    @property
    def is_funasr_mode(self) -> bool:
        """检查是否使用 FunASR 模式（始终为 True）。"""
        return True
