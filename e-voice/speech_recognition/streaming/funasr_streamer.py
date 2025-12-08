"""
FunASR 流式推理组件。

基于 FunASR/runtime/python/websocket/funasr_wss_server.py 抽取为可复用的类，
处理 VAD 分段、在线增量 ASR、离线二次纠错、标点与 ITN，管理 cache/状态。

支持 mode（2pass/online/offline）与 chunk_size/chunk_interval 配置，输出统一的事件字典。
"""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

# 尝试导入 cn2an 用于中文数字转阿拉伯数字（ITN 功能）
try:
    import cn2an
except ImportError:
    cn2an = None
    logger.warning("cn2an 未安装，中文数字转换功能将被禁用 (pip install cn2an)")

# InverseNormalizer 已弃用，统一使用 cn2an 实现 ITN
InverseNormalizer = None


@dataclass(slots=True)
class FunASRStreamerConfig:
    """FunASR 流式组件配置。
    
    与官方 FunASR Demo (funasr_wss_server.py) 配置保持一致。
    """
    
    mode: str = "2pass"  # 2pass, online, offline
    chunk_interval: int = 10  # 每 N 个 chunk 触发一次在线识别
    chunk_size: List[int] = field(default_factory=lambda: [5, 10, 5])
    encoder_chunk_look_back: int = 5  # 编码器回看 chunk 数
    decoder_chunk_look_back: int = 5  # 解码器回看 chunk 数
    sample_rate: int = 16000
    enable_vad: bool = True
    enable_punc: bool = True
    enable_itn: bool = True
    itn_language: str = "zh"
    itn_cache_dir: Optional[str] = None
    debug: bool = False
    
    # VAD 分段参数
    vad_max_single_segment_time: int = 45000  # 单段最大时长 ms
    vad_max_end_silence_time: int = 1200  # 句末静音阈值 ms
    vad_speech_noise_thres: float = 0.7  # 语音/噪声阈值


@dataclass(slots=True)
class FunASRStreamerState:
    """FunASR 流式组件状态。
    
    与 FunASR Demo (funasr_wss_server.py) 保持一致的状态管理：
    - online_is_final: 使用上一帧的 VAD 结果，供当前帧在线 ASR 判断是否 final
    """
    
    # VAD 状态
    vad_cache: Dict[str, Any] = field(default_factory=dict)
    vad_pre_idx: int = 0
    speech_start: bool = False
    
    # 在线 ASR 状态
    online_cache: Dict[str, Any] = field(default_factory=dict)
    online_is_final: bool = False  # 上一帧的 speech_end 状态，用于当前帧在线 ASR 判断
    
    # 离线 ASR 状态
    offline_cache: Dict[str, Any] = field(default_factory=dict)
    
    # 标点状态
    punc_cache: Dict[str, Any] = field(default_factory=dict)
    
    # 音频缓冲
    frames: List[bytes] = field(default_factory=list)  # 所有帧
    frames_asr: List[bytes] = field(default_factory=list)  # 离线 ASR 帧
    frames_asr_online: List[bytes] = field(default_factory=list)  # 在线 ASR 帧
    
    # 其他
    wav_name: str = "microphone"
    is_speaking: bool = True
    hotwords: Dict[str, Any] = field(default_factory=dict)
    session_id: str = ""  # 便于日志聚合
    
    # 时间追踪
    total_audio_ms: int = 0           # 总音频时长(ms) - 基于实际发送的音频计算
    current_segment_start_ms: int = 0  # 当前段起始时间(ms) - 相对于音频文件的绝对位置
    last_segment_end_ms: int = 0       # 上一段结束时间(ms)
    
    # 音频片段缓冲（用于保存音频片段文件）
    current_segment_audio: List[bytes] = field(default_factory=list)
    
    def reset(self) -> None:
        """重置所有状态。"""
        self.vad_cache = {}
        self.vad_pre_idx = 0
        self.speech_start = False
        self.online_cache = {}
        self.online_is_final = False
        self.offline_cache = {}
        self.punc_cache = {}
        self.frames = []
        self.frames_asr = []
        self.frames_asr_online = []
        self.is_speaking = True
        self.current_segment_audio = []
        self.total_audio_ms = 0
        self.current_segment_start_ms = 0
        self.last_segment_end_ms = 0


@dataclass(slots=True)
class StreamingEvent:
    """流式识别事件。"""
    
    type: str  # partial, correction, final
    mode: str  # 2pass-online, 2pass-offline, online, offline
    text: str
    is_final: bool
    wav_name: str = "microphone"
    start_offset_ms: int = 0  # 起始时间偏移(ms)
    end_offset_ms: int = 0    # 结束时间偏移(ms)
    duration_ms: int = 0      # 时长(ms)
    audio_data: Optional[bytes] = None  # 该段语音的原始音频数据
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "mode": self.mode,
            "text": self.text,
            "is_final": self.is_final,
            "wav_name": self.wav_name,
            "start_offset_ms": self.start_offset_ms,
            "end_offset_ms": self.end_offset_ms,
            "duration_ms": self.duration_ms,
        }


class FunASRStreamer:
    """
    FunASR 流式推理组件。
    
    核心功能：
    1. VAD 分段检测语音端点
    2. 在线流式 ASR 输出 partial 结果
    3. 离线 ASR 进行二次纠错
    4. 标点恢复
    5. ITN 逆文本归一化
    """
    
    def __init__(
        self,
        model_asr: Any,
        model_asr_online: Any,
        model_vad: Any,
        model_punc: Optional[Any] = None,
        config: Optional[FunASRStreamerConfig] = None,
    ) -> None:
        """
        初始化 FunASR 流式组件。
        
        Args:
            model_asr: 离线 ASR 模型
            model_asr_online: 在线流式 ASR 模型
            model_vad: VAD 模型
            model_punc: 标点模型（可选）
            config: 配置
        """
        self.model_asr = model_asr
        self.model_asr_online = model_asr_online
        self.model_vad = model_vad
        self.model_punc = model_punc
        self.config = config or FunASRStreamerConfig()
        
        # 初始化 ITN
        self._inverse_normalizer: Optional[Any] = None
        if self.config.enable_itn:
            self._init_itn()
    
    def _init_itn(self) -> None:
        """初始化 ITN 组件。"""
        if InverseNormalizer is None:
            logger.warning("ITN 初始化失败：fun_text_processing 未安装")
            return
        
        try:
            cache_dir = self.config.itn_cache_dir
            if cache_dir is None:
                # 默认使用 config 目录下的 itn_cache
                cache_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "config",
                    "itn_cache",
                )
            os.makedirs(cache_dir, exist_ok=True)
            
            self._inverse_normalizer = InverseNormalizer(
                lang=self.config.itn_language,
                cache_dir=cache_dir,
                overwrite_cache=False,
            )
            logger.info(f"ITN 初始化成功 (lang={self.config.itn_language}, cache={cache_dir})")
        except Exception as e:
            logger.error(f"ITN 初始化失败: {e}")
            self._inverse_normalizer = None
    
    def create_state(self) -> FunASRStreamerState:
        """创建新的状态对象。"""
        return FunASRStreamerState()
    
    def process_chunk(
        self,
        audio_chunk: bytes,
        state: FunASRStreamerState,
    ) -> List[StreamingEvent]:
        """
        处理单个音频 chunk。
        
        处理顺序与 FunASR Demo (funasr_wss_server.py) 保持一致：
        1. 收集帧
        2. 执行在线 ASR（使用上一帧的 VAD 结果）
        3. 收集离线帧（如果 speech_start）
        4. 执行 VAD 检测（更新端点信息供下一帧使用）
        5. 处理语音开始/结束
        
        Args:
            audio_chunk: 音频数据（16kHz, 16bit, mono PCM）
            state: 流式状态对象
            
        Returns:
            生成的事件列表
        """
        events: List[StreamingEvent] = []
        t_chunk_start = time.time()
        
        # 计算音频时长（毫秒）
        # 16kHz, 16bit = 32 bytes/ms
        duration_ms = len(audio_chunk) // 32
        
        # 更新总音频时长
        state.total_audio_ms += duration_ms
        
        session_tag = f"session={state.session_id or 'unknown'}"

        # 关键日志：记录 chunk 处理开始（增加频率：前10个、每20个、或帧缓冲>30时）
        chunk_count = len(state.frames) + 1
        frames_asr_count = len(state.frames_asr)
        frames_online_count = len(state.frames_asr_online)
        buffer_warning = frames_asr_count > 30 or chunk_count > 100
        
        # 更频繁的日志以便诊断延迟问题
        if chunk_count <= 10 or chunk_count % 20 == 0 or buffer_warning:
            logger.info(
                f"[FunASRStreamer] {session_tag} process_chunk #{chunk_count}: "
                f"audio_len={len(audio_chunk)}, duration_ms={duration_ms}, "
                f"total_ms={state.total_audio_ms}, "
                f"is_speaking={state.is_speaking}, online_is_final={state.online_is_final}, "
                f"speech_start={state.speech_start}, "
                f"frames={len(state.frames)}, frames_asr={frames_asr_count}, frames_online={frames_online_count}"
            )
        
        # 1. 更新帧缓冲
        state.frames.append(audio_chunk)
        state.vad_pre_idx += duration_ms
        
        # 2. 收集在线 ASR 帧并执行（使用上一帧的 VAD 结果 - 通过 state.online_is_final）
        state.frames_asr_online.append(audio_chunk)
        # 注意：state.online_is_final 使用的是上一帧 VAD 检测的结果
        online_trigger_interval = len(state.frames_asr_online) % self.config.chunk_interval == 0
        online_trigger_final = state.online_is_final
        should_run_online = online_trigger_interval or online_trigger_final
        
        # 【诊断日志】每10个chunk记录一次在线ASR触发状态
        if chunk_count % 10 == 0 or should_run_online:
            logger.debug(
                f"[DIAG] {session_tag} chunk#{chunk_count} online_asr_check: "
                f"frames_online={len(state.frames_asr_online)}, interval={self.config.chunk_interval}, "
                f"trigger_interval={online_trigger_interval}, trigger_final={online_trigger_final}, "
                f"will_run={should_run_online}, mode={self.config.mode}"
            )
        
        if should_run_online:
            if self.config.mode in ("2pass", "online") and self.model_asr_online is not None:
                t_online_start = time.time()
                online_event = self._run_online_asr(state)
                t_online_end = time.time()
                online_ms = (t_online_end - t_online_start) * 1000
                
                if online_event:
                    events.append(online_event)
                    logger.info(
                        f"[TIMING] {session_tag} online_asr_triggered: "
                        f"chunk#{chunk_count}, took={online_ms:.1f}ms, "
                        f"text_len={len(online_event.text)}, final={online_event.is_final}"
                    )
                else:
                    # 【诊断日志】在线ASR返回空结果
                    logger.debug(
                        f"[DIAG] {session_tag} chunk#{chunk_count} online_asr returned None, took={online_ms:.1f}ms"
                    )
            else:
                # 【诊断日志】在线ASR被跳过的原因
                logger.debug(
                    f"[DIAG] {session_tag} chunk#{chunk_count} online_asr_skipped: "
                    f"mode={self.config.mode}, model_online_available={self.model_asr_online is not None}"
                )
            state.frames_asr_online = []
        
        # 3. 如果语音已开始，累积离线 ASR 帧
        if state.speech_start:
            state.frames_asr.append(audio_chunk)
            state.current_segment_audio.append(audio_chunk)
        
        # 4. VAD 检测（在在线 ASR 之后执行，与 FunASR Demo 顺序一致）
        speech_start_i, speech_end_i = -1, -1
        if self.config.enable_vad and self.model_vad is not None:
            t_vad_start = time.time()
            try:
                speech_start_i, speech_end_i = self._run_vad(audio_chunk, state)
            except Exception as e:
                logger.error(f"VAD 执行失败: {e}")
                speech_start_i, speech_end_i = -1, -1
            vad_ms = (time.time() - t_vad_start) * 1000
            
            # 【诊断日志】增强VAD状态跟踪（每10个chunk或状态变化时）
            vad_state_changed = speech_start_i != -1 or speech_end_i != -1
            if vad_ms > 30 or vad_state_changed or chunk_count % 10 == 0:
                logger.info(
                    f"[VAD] {session_tag} chunk#{chunk_count}: "
                    f"took={vad_ms:.1f}ms, start_i={speech_start_i}, end_i={speech_end_i}, "
                    f"speech_start_flag={state.speech_start}, vad_pre_idx={state.vad_pre_idx}, "
                    f"frames={len(state.frames)}, frames_asr={len(state.frames_asr)}"
                )
            
            if self.config.debug and vad_state_changed:
                logger.debug(
                    f"[stream] vad start={speech_start_i} end={speech_end_i} "
                    f"frames_asr={len(state.frames_asr)} frames_online={len(state.frames_asr_online)}"
                )
        
        # 5. 处理语音开始
        if speech_start_i != -1:
            state.speech_start = True
            # 记录当前段的起始时间 - 使用实际的音频位置而非 last_segment_end_ms
            # 这样可以准确反映语音在整个音频文件中的位置
            state.current_segment_start_ms = state.total_audio_ms - duration_ms
            
            # 计算需要回溯的帧数
            # beg_bias 表示从当前帧往前数多少帧是语音开始点
            beg_bias = (state.vad_pre_idx - speech_start_i) // duration_ms if duration_ms > 0 else 0
            if beg_bias > 0 and beg_bias <= len(state.frames):
                frames_pre = state.frames[-beg_bias:]
            else:
                frames_pre = state.frames[:]  # 使用所有缓存的帧
            
            state.frames_asr = list(frames_pre)
            # 同时开始收集音频片段
            state.current_segment_audio = list(frames_pre)
            
            # 关键日志
            if len(state.frames) > 0:
                logger.info(
                    f"[FunASRStreamer] {session_tag} speech_start: beg_bias={beg_bias}, "
                    f"frames_pre={len(frames_pre)}, frames={len(state.frames)}"
                )
        
        # 6. 更新 online_is_final 供下一帧使用（与 FunASR Demo 逻辑一致）
        state.online_is_final = speech_end_i != -1
        
        # 7. 处理语音结束（离线 ASR）
        if speech_end_i != -1 or not state.is_speaking:
            # 关键日志：记录语音结束触发条件
            logger.info(
                f"[FunASRStreamer] {session_tag} speech_end triggered: "
                f"speech_end_i={speech_end_i}, is_speaking={state.is_speaking}, "
                f"frames_asr={len(state.frames_asr)}, mode={self.config.mode}"
            )
            
            if self.config.mode in ("2pass", "offline") and self.model_asr is not None:
                offline_event = self._run_offline_asr(state, force_final=True)
                if offline_event:
                    events.append(offline_event)
                    # 关键日志：记录离线 ASR 结果
                    logger.info(
                        f"[FunASRStreamer] {session_tag} offline_asr result: "
                        f"text_len={len(offline_event.text)}, mode={offline_event.mode}"
                    )
            
            # 重置状态
            state.frames_asr = []
            state.speech_start = False
            state.frames_asr_online = []
            state.online_cache = {}
            
            if not state.is_speaking:
                # 关键日志：记录完全复位
                logger.info(
                    f"[FunASRStreamer] {session_tag} full reset: is_speaking=false, clearing all caches"
                )
                state.vad_pre_idx = 0
                state.frames = []
                state.vad_cache = {}
            else:
                # 保留最近帧用于下一段
                # 增大保留帧数以避免丢失语音开始部分
                # 原先是20帧(~1.2s)，现在改为50帧(~3s)以容纳较长的静音间隔
                max_keep_frames = 50
                if len(state.frames) > max_keep_frames:
                    state.frames = state.frames[-max_keep_frames:]
                    logger.debug(
                        f"[FunASRStreamer] {session_tag} speech_end: truncated frames to {max_keep_frames}"
                    )
        
        # 记录 chunk 处理总耗时
        t_chunk_end = time.time()
        chunk_time_ms = (t_chunk_end - t_chunk_start) * 1000
        # 处理耗时显著高于音频时长时给出提示，便于定位堆积
        audio_ms = max(duration_ms, 1)
        rt_factor = chunk_time_ms / audio_ms
        
        # 【关键诊断】计算累积延迟估计
        # 如果处理时间持续超过音频时长，延迟会累积
        buffered_frames = len(state.frames)
        buffered_ms_est = buffered_frames * duration_ms
        
        if rt_factor > 1.0:
            # 处理速度跟不上实时，这是延迟的根本原因
            logger.warning(
                f"[PERF-SLOW] {session_tag} chunk#{chunk_count} RTF={rt_factor:.2f} (>1.0 means falling behind!) "
                f"proc_ms={chunk_time_ms:.1f} audio_ms={duration_ms} "
                f"buffered_frames={buffered_frames} buffered_ms~{buffered_ms_est} "
                f"events={len(events)} speech_start={state.speech_start} is_speaking={state.is_speaking}"
            )
        elif rt_factor > 0.8 or len(events) > 0 or chunk_count % 20 == 0:
            # 正常但接近阈值，或有事件，或定期记录
            logger.info(
                f"[PERF] {session_tag} chunk#{chunk_count} RTF={rt_factor:.2f} "
                f"proc_ms={chunk_time_ms:.1f} audio_ms={duration_ms} "
                f"buffered={buffered_frames} events={len(events)}"
            )
        
        return events
    
    def flush(self, state: FunASRStreamerState) -> List[StreamingEvent]:
        """
        刷新所有缓冲，输出最终结果（与官方 demo 对齐）。
        
        与官方 FunASR Demo (funasr_wss_server.py) 保持一致的缓存复位逻辑：
        - 设置 is_speaking=False, online_is_final=True
        - 如果有在线帧缓冲，先触发在线 ASR
        - 触发离线 ASR 进行最终纠错
        - 复位所有缓存
        
        重要：即使 frames_asr 为空，也检查 frames 中是否有未处理的音频
        
        Args:
            state: 流式状态对象
            
        Returns:
            生成的事件列表
        """
        events: List[StreamingEvent] = []
        session_tag = f"session={state.session_id or 'unknown'}"
        
        # 关键日志：记录 flush 开始
        logger.info(
            f"[FunASRStreamer] {session_tag} flush called: "
            f"frames={len(state.frames)}, frames_asr={len(state.frames_asr)}, "
            f"frames_asr_online={len(state.frames_asr_online)}, "
            f"speech_start={state.speech_start}, mode={self.config.mode}"
        )
        
        # 强制触发最终状态
        state.is_speaking = False
        state.online_is_final = True
        
        # 如果有在线帧缓冲，先触发在线 ASR（与官方 demo 对齐）
        if state.frames_asr_online and self.model_asr_online is not None:
            if self.config.mode in ("2pass", "online"):
                logger.info(
                    f"[FunASRStreamer] {session_tag} flush: running online ASR with {len(state.frames_asr_online)} frames"
                )
                online_event = self._run_online_asr(state)
                if online_event and self.config.mode == "online":
                    # online-only 模式下输出在线结果
                    events.append(online_event)
            state.frames_asr_online = []
        
        # 触发离线 ASR 进行最终纠错
        # 重要：如果 frames_asr 为空但 frames 有数据，说明有未处理的静音后音频
        audio_to_process = state.frames_asr if state.frames_asr else state.frames
        
        if audio_to_process and self.model_asr is not None:
            # 如果 frames_asr 为空，使用 frames 作为离线ASR输入
            if not state.frames_asr and state.frames:
                logger.info(
                    f"[FunASRStreamer] {session_tag} flush: frames_asr is empty but frames has {len(state.frames)} chunks, "
                    f"using frames for offline ASR"
                )
                state.frames_asr = list(state.frames)
                state.current_segment_audio = list(state.frames)
                # 设置时间起点为上一段结束位置
                if state.current_segment_start_ms == 0:
                    state.current_segment_start_ms = state.last_segment_end_ms
            
            logger.info(
                f"[FunASRStreamer] {session_tag} flush: running offline ASR with {len(state.frames_asr)} frames"
            )
            offline_event = self._run_offline_asr(state, force_final=True)
            if offline_event:
                events.append(offline_event)
                logger.info(
                    f"[FunASRStreamer] {session_tag} flush: offline result text_len={len(offline_event.text)}"
                )
        
        # 与官方 demo 对齐：完全复位所有缓存
        logger.info(f"[FunASRStreamer] {session_tag} flush: resetting all state")
        state.reset()
        
        return events
    
    def _run_vad(
        self,
        audio_chunk: bytes,
        state: FunASRStreamerState,
    ) -> Tuple[int, int]:
        """
        执行 VAD 检测。
        
        Returns:
            (speech_start_ms, speech_end_ms) 元组，-1 表示未检测到
        """
        vad_params = {
            "cache": state.vad_cache,
            "is_final": False,
            "chunk_size": int(
                self.config.chunk_size[1] * 60 / self.config.chunk_interval
            ),
            # VAD 分段参数 - 控制语音分段敏感度
            "max_end_silence_time": self.config.vad_max_end_silence_time,
            "max_single_segment_time": self.config.vad_max_single_segment_time,
            "speech_noise_thres": self.config.vad_speech_noise_thres,
        }
        
        result = self.model_vad.generate(input=audio_chunk, **vad_params)[0]
        segments = result.get("value", [])
        
        # 更新缓存
        state.vad_cache = result.get("cache", state.vad_cache)
        
        speech_start = -1
        speech_end = -1
        
        if len(segments) == 1:
            if segments[0][0] != -1:
                speech_start = segments[0][0]
            if segments[0][1] != -1:
                speech_end = segments[0][1]
        
        return speech_start, speech_end
    
    def _run_online_asr(self, state: FunASRStreamerState) -> Optional[StreamingEvent]:
        """执行在线流式 ASR。
        
        与官方 FunASR Demo 对齐：使用配置的 encoder/decoder_chunk_look_back。
        """
        audio_bytes = b"".join(state.frames_asr_online)
        if not audio_bytes:
            return None
        
        t_start = time.time()
        try:
            asr_params = {
                "cache": state.online_cache,
                "is_final": state.online_is_final,
                "chunk_size": self.config.chunk_size,
                "encoder_chunk_look_back": self.config.encoder_chunk_look_back,
                "decoder_chunk_look_back": self.config.decoder_chunk_look_back,
            }
            
            if state.hotwords:
                asr_params["hotword"] = state.hotwords
            
            result = self.model_asr_online.generate(input=audio_bytes, **asr_params)[0]
            t_end = time.time()
            session_tag = f"session={state.session_id or 'unknown'}"
            device_str = str(getattr(self.model_asr_online, "device", "unknown"))
            logger.info(
                f"[TIMING] {session_tag} online_asr took {(t_end-t_start)*1000:.1f}ms, "
                f"audio_len={len(audio_bytes)} text_len={len(result.get('text',''))} "
                f"device={device_str}"
            )
            if self.config.debug:
                logger.debug(
                    f"[stream] online_asr done len={len(audio_bytes)} text_len={len(result.get('text',''))}"
                )
            state.online_cache = result.get("cache", state.online_cache)
            
            text = result.get("text", "")
            if not text:
                return None
            
            # 2pass 模式下，如果是 final 则跳过（等待离线结果）
            if self.config.mode == "2pass" and state.online_is_final:
                return None
            
            # 如果是 final，应用 ITN
            if state.online_is_final:
                text = self._apply_itn(text)
            
            mode = "2pass-online" if self.config.mode == "2pass" else self.config.mode
            return StreamingEvent(
                type="partial",
                mode=mode,
                text=text,
                is_final=not state.is_speaking,
                wav_name=state.wav_name,
            )
        except Exception as e:
            logger.error(f"在线 ASR 执行失败: {e}")
            return None
    
    def _run_offline_asr(self, state: FunASRStreamerState, *, force_final: bool = False) -> Optional[StreamingEvent]:
        """执行离线 ASR 进行二次纠错。"""
        t_start = time.time()
        session_tag = f"session={state.session_id or 'unknown'}"
        logger.info(
            f"[TIMING] {session_tag} offline_asr START, frames_count={len(state.frames_asr)}"
        )
        
        audio_bytes = b"".join(state.frames_asr)
        # 获取当前片段的音频数据用于保存
        segment_audio_bytes = b"".join(state.current_segment_audio) if state.current_segment_audio else audio_bytes
        
        # 计算时间信息
        start_offset_ms = state.current_segment_start_ms
        # 音频时长 = 字节数 / (采样率 * 位深 / 8) * 1000
        # 16kHz, 16bit = 32 bytes/ms
        segment_duration_ms = len(audio_bytes) // 32 if audio_bytes else 0
        end_offset_ms = start_offset_ms + segment_duration_ms
        
        # 更新上一段结束时间
        state.last_segment_end_ms = end_offset_ms
        
        # 清理片段音频缓冲
        state.current_segment_audio = []
        
        if not audio_bytes:
            # 即使没有音频也要发送空结果
            mode = "2pass-offline" if self.config.mode == "2pass" else self.config.mode
            logger.info(
                f"[TIMING] {session_tag} offline_asr END (empty), took {(time.time()-t_start)*1000:.1f}ms"
            )
            return StreamingEvent(
                type="correction",
                mode=mode,
                text="",
                is_final=True if force_final else (not state.is_speaking),
                wav_name=state.wav_name,
                start_offset_ms=start_offset_ms,
                end_offset_ms=end_offset_ms,
                duration_ms=0,
                audio_data=None,
            )
        
        try:
            asr_params = {}
            if state.hotwords:
                asr_params["hotword"] = state.hotwords
            
            t_model_start = time.time()
            result = self.model_asr.generate(input=audio_bytes, **asr_params)[0]
            t_model_end = time.time()
            logger.info(
                f"[TIMING] {session_tag} offline_asr MODEL took {(t_model_end-t_model_start)*1000:.1f}ms, "
                f"audio_len={len(audio_bytes)}, audio_duration={segment_duration_ms}ms"
            )
            if self.config.debug:
                logger.debug(
                    f"[stream] offline_asr done len={len(audio_bytes)} text_len={len(result.get('text',''))}"
                )
            text = result.get("text", "")
            
            # 应用标点
            if text and self.config.enable_punc and self.model_punc is not None:
                try:
                    punc_result = self.model_punc.generate(
                        input=text, **state.punc_cache
                    )[0]
                    text = punc_result.get("text", text)
                except Exception as e:
                    logger.warning(f"标点处理失败: {e}")
            
            # 应用 ITN
            if text:
                text = self._apply_itn(text)
            
            mode = "2pass-offline" if self.config.mode == "2pass" else self.config.mode
            total_ms = (time.time() - t_start) * 1000
            logger.info(
                f"[TIMING] {session_tag} offline_asr TOTAL took {total_ms:.1f}ms "
                f"(model={t_model_end - t_model_start:.3f}s) text_len={len(text)} "
                f"audio_ms={segment_duration_ms}"
            )
            return StreamingEvent(
                type="correction",
                mode=mode,
                text=text,
                is_final=True if force_final else (not state.is_speaking),
                wav_name=state.wav_name,
                start_offset_ms=start_offset_ms,
                end_offset_ms=end_offset_ms,
                duration_ms=segment_duration_ms,
                audio_data=segment_audio_bytes,
            )
        except Exception as e:
            logger.error(f"离线 ASR 执行失败: {e}")
            return None
    
    def _apply_itn(self, text: str) -> str:
        """应用 ITN 逆文本归一化。"""
        if not text or not self.config.enable_itn:
            return text
        
        # 先尝试使用 InverseNormalizer
        if self._inverse_normalizer is not None:
            try:
                text = self._inverse_normalizer.inverse_normalize_list(
                    [text], verbose=False
                )[0]
            except Exception as e:
                logger.warning(f"ITN 处理失败: {e}")
        
        # 再应用中文数字转换
        text = self._postprocess_numbers(text)
        
        return text
    
    @staticmethod
    def _postprocess_numbers(text: str) -> str:
        """
        将中文数字转换为阿拉伯数字。
        
        参考 funasr_wss_server.py 中的 postprocess_numbers 函数。
        """
        if not text or cn2an is None:
            return text
        
        def _fmt(val):
            try:
                if float(val).is_integer():
                    return str(int(val))
                return f"{float(val):g}"
            except Exception:
                return str(val)
        
        def _conv_percent(match):
            raw = match.group(0)
            inner = match.group(1)
            try:
                return f"{_fmt(cn2an.cn2an(inner, 'smart'))}%"
            except Exception:
                return raw
        
        def _conv_with_unit(match):
            raw = match.group(0)
            inner = match.group(1)
            unit = match.group(2)
            try:
                return f"{_fmt(cn2an.cn2an(inner, 'smart'))}{unit}"
            except Exception:
                return raw
        
        def _conv_plain(match):
            raw = match.group(0)
            try:
                return _fmt(cn2an.cn2an(raw, "smart"))
            except Exception:
                return raw
        
        # 百分之X -> X%
        text = re.sub(r"百分之([〇零一二两三四五六七八九十百千万亿兆点]+)", _conv_percent, text)
        # X(万|亿|兆) 输出保留单位
        text = re.sub(r"([〇零一二两三四五六七八九十百千零点两]+)([万亿兆])", _conv_with_unit, text)
        # 其他纯中文数字
        text = re.sub(r"[〇零一二两三四五六七八九十百千万亿兆点]+", _conv_plain, text)
        
        return text

