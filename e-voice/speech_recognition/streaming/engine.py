"""StreamingEngine push/flush 实现。

使用 FunASRStreamer 进行完整的 VAD + 流式 ASR + 纠错 + 标点 + ITN。
"""

from __future__ import annotations

import os
import re
import time
import uuid
import wave
import threading
from typing import Iterable, List, Optional, Tuple

from loguru import logger

from .loader import ModelLoader, FunASRModelBundle
from .state import StreamingState
from .text_accumulator import TextAccumulator
from .funasr_streamer import FunASRStreamer, FunASRStreamerConfig, FunASRStreamerState


# 音频片段保存目录
AUDIO_SEGMENT_DIR = "data/meeting/audio_segments"

# 是否启用自动声纹匹配（可以在运行时配置）
ENABLE_AUTO_VOICEPRINT = True


# 中文句末标点正则 - 用于基于语义的二次分段
SENTENCE_END_PATTERN = re.compile(r'([。！？!?])')


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
            if current.strip():
                sentences.append(current.strip())
            current = ""
    
    # 处理剩余的没有句末标点的文本
    if current.strip():
        # 如果有之前的句子，尝试合并到最后一个（可能是不完整的）
        # 否则作为新句子
        sentences.append(current.strip())
    
    return sentences if sentences else [text]


class StreamingEngine:
    """处理音频 chunk 并输出识别事件。"""

    def __init__(self) -> None:
        self._loader = ModelLoader.current()
        self._funasr_streamer: Optional[FunASRStreamer] = None
        self._funasr_state_map: dict[str, FunASRStreamerState] = {}
        
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
            funasr_state.wav_name = state.session_id
            funasr_state.hotwords = state.hotwords
            self._funasr_state_map[state.session_id] = funasr_state
        return self._funasr_state_map[state.session_id]
    
    # 向后兼容别名
    _get_funasr_state = get_funasr_state
    
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
            
            logger.info(f"音频片段已保存: {filepath} ({len(audio_data)} bytes)")
            
            # 返回相对路径（用于前端访问）
            return f"/{filepath}"
            
        except Exception as e:
            logger.error(f"保存音频片段失败: {e}")
            return None
    
    def _match_speaker(self, audio_data: bytes) -> Optional[dict]:
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
            from server.routes.meeting_mdt import match_speaker_from_pcm
            result = match_speaker_from_pcm(audio_data, sample_rate=16000)
            
            if result.get('recognized'):
                logger.info(
                    f"声纹匹配成功: speaker={result.get('speaker_name')}, "
                    f"score={result.get('recognition_score')}"
                )
            else:
                logger.debug(f"声纹未匹配: {result.get('recognition_note')}")
            
            return result
        except Exception as e:
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
        state.mark_activity(int(time.time() * 1000))
        
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
            events = self._funasr_streamer.process_chunk(audio_chunk, funasr_state)
        except Exception as e:
            logger.error(f"[engine] FunASR 处理失败: {e}")
            return []
        
        # 转换事件格式
        result_events = []
        accumulator: TextAccumulator = state.text_accumulator or TextAccumulator()
        state.text_accumulator = accumulator
        
        for event in events:
            text = event.text
            if not text:
                continue
            
            if event.type == "partial":
                # 实时 partial 结果不分段
                revision = state.next_revision()
                segment_id = state.ensure_segment()
                snapshot = accumulator.update_partial(text, revision)
                result_event = {
                    "type": "partial",
                    "mode": event.mode,
                    "revision": revision,
                    "text": text,
                    "is_final": False,
                    "session_id": state.session_id,
                    "segment_id": segment_id,
                    "text_state": snapshot,
                }
                result_events.append(result_event)
            else:  # correction / final - 基于标点进行二次分段
                # 将长文本按句末标点分成多个语义完整的句子
                sentences = split_by_punctuation(text)
                
                # 获取原始时间信息
                total_start_ms = event.start_offset_ms
                total_duration_ms = event.duration_ms
                total_text_len = len(text.replace(" ", ""))  # 去空格的字符长度
                
                # 保存音频片段文件（如果有音频数据）
                audio_path = None
                speaker_info = None
                
                if event.audio_data and len(sentences) == 1:
                    # 单句情况下保存音频
                    audio_path = self._save_audio_segment(
                        event.audio_data,
                        state.session_id,
                        state.ensure_segment()
                    )
                    # 执行声纹匹配
                    speaker_info = self._match_speaker(event.audio_data)
                
                # 按字符比例分配时间
                current_offset_ms = total_start_ms
                
                for i, sentence in enumerate(sentences):
                    if not sentence:
                        continue
                    
                    revision = state.next_revision()
                    segment_id = state.ensure_segment()
                    
                    is_last_sentence = (i == len(sentences) - 1)
                    snapshot = accumulator.apply_correction(sentence)
                    
                    # 按字符比例计算该句子的时长
                    sentence_len = len(sentence.replace(" ", ""))
                    if total_text_len > 0:
                        sentence_duration_ms = int(total_duration_ms * sentence_len / total_text_len)
                    else:
                        sentence_duration_ms = 0
                    
                    sentence_start_ms = current_offset_ms
                    sentence_end_ms = current_offset_ms + sentence_duration_ms
                    current_offset_ms = sentence_end_ms
                    
                    # 多句情况下，最后一句保存完整音频
                    sentence_audio_path = None
                    sentence_speaker_info = None
                    
                    if len(sentences) == 1:
                        sentence_audio_path = audio_path
                        sentence_speaker_info = speaker_info
                    elif is_last_sentence and event.audio_data:
                        # 多句时将音频保存给最后一句
                        sentence_audio_path = self._save_audio_segment(
                            event.audio_data,
                            state.session_id,
                            segment_id
                        )
                        # 执行声纹匹配
                        sentence_speaker_info = self._match_speaker(event.audio_data)
                    
                    result_event = {
                        "type": "correction",
                        "mode": event.mode,
                        "revision": revision,
                        "text": sentence,
                        "is_final": event.is_final and is_last_sentence,
                        "session_id": state.session_id,
                        "segment_id": segment_id,
                        "text_state": snapshot,
                        # 时间信息
                        "start_offset_ms": sentence_start_ms,
                        "end_offset_ms": sentence_end_ms,
                        "duration_ms": sentence_duration_ms,
                        # 音频路径
                        "audio_path": sentence_audio_path,
                    }
                    
                    # 添加声纹匹配结果
                    if sentence_speaker_info:
                        result_event["speaker_info"] = sentence_speaker_info
                    
                    if event.is_final and is_last_sentence:
                        state.mark_segment_final(segment_id)
                    
                    result_events.append(result_event)
                    
                    # 为下一个句子创建新的 segment
                    if not is_last_sentence:
                        state.current_segment_id = None
        
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
            return []
        
        funasr_state = self._funasr_state_map[state.session_id]
        
        try:
            events = self._funasr_streamer.flush(funasr_state)
        except Exception as e:
            logger.error(f"[engine] FunASR flush 失败: {e}")
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
                
            # 应用标点二次分段（与 push 方法一致）
            sentences = self._split_by_punctuation(text)
            
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                revision = state.next_revision()
                segment_id = state.ensure_segment()
                
                snapshot = accumulator.apply_correction(sentence)
                result_event = {
                    "type": "correction",
                    "mode": event.mode,
                    "revision": revision,
                    "text": sentence,
                    "is_final": True,
                    "session_id": state.session_id,
                    "segment_id": segment_id,
                    "text_state": snapshot,
                    "start_offset": getattr(event, 'start_offset_ms', 0),
                    "end_offset": getattr(event, 'end_offset_ms', 0),
                    "duration_ms": getattr(event, 'duration_ms', 0),
                }
                result_events.append(result_event)
                state.mark_segment_final(segment_id)
                
                # 为下一个句子创建新的 segment
                if i < len(sentences) - 1:
                    state.current_segment_id = None
        
        return result_events

    def cleanup_session(self, session_id: str) -> None:
        """清理会话状态。"""
        if session_id in self._funasr_state_map:
            del self._funasr_state_map[session_id]

    @property
    def is_ready(self) -> bool:
        """检查引擎是否就绪。"""
        return self._funasr_streamer is not None
    
    # 向后兼容
    @property
    def is_funasr_mode(self) -> bool:
        """检查是否使用 FunASR 模式（始终为 True）。"""
        return True
