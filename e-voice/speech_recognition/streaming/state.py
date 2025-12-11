"""实时流式识别状态数据结构定义。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .text_accumulator import TextAccumulator


@dataclass(slots=True)
class StreamingState:
    """维护单个会话的缓存与上下文。"""

    session_id: str
    request_id: str
    chunk_interval: int
    sample_rate: int
    hotwords: Dict[str, Any]
    speaker_id: Optional[str] = None
    language: str = "zh-CN"
    mode: str = "2pass"  # 2pass, online, offline
    vad_state: Dict[str, Any] = field(default_factory=dict)
    online_cache: Dict[str, Any] = field(default_factory=dict)
    offline_cache: Dict[str, Any] = field(default_factory=dict)
    text_state: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    pending_audio: List[bytes] = field(default_factory=list)
    pending_offline_audio: List[bytes] = field(default_factory=list)
    segment_seq: int = 0
    revision: int = 0
    last_activity_ms: int | None = None
    current_segment_id: Optional[str] = None
    last_final_segment_id: Optional[str] = None
    text_accumulator: "TextAccumulator | None" = None
    
    # FunASR 扩展字段
    chunk_size: List[int] = field(default_factory=lambda: [5, 10, 5])
    encoder_chunk_look_back: int = 5
    decoder_chunk_look_back: int = 5
    enable_itn: bool = True
    wav_name: str = "microphone"
    
    # 🎯 实时预览累积文本（当前语音段内的所有 partial 文本）
    # 用于前端覆写显示，而不是增量累加
    current_partial_text: str = ""
    
    # 内部状态标记
    _config_logged: bool = False

    def next_segment_id(self) -> str:
        self.segment_seq += 1
        return f"seg-{self.session_id}-{self.segment_seq:04d}"

    def next_revision(self) -> int:
        self.revision += 1
        return self.revision

    def mark_activity(self, timestamp_ms: int) -> None:
        self.last_activity_ms = timestamp_ms

    def ensure_segment(self) -> str:
        if self.current_segment_id is None:
            self.current_segment_id = self.next_segment_id()
        return self.current_segment_id

    def mark_segment_final(self, segment_id: Optional[str]) -> None:
        if segment_id is None:
            return
        self.last_final_segment_id = segment_id
        self.current_segment_id = None
    
    def append_partial_text(self, text: str) -> str:
        """累加 partial 文本，返回累积的完整文本。"""
        if text:
            self.current_partial_text += text
        return self.current_partial_text
    
    def clear_partial_text(self) -> None:
        """清空累积的 partial 文本（当语音段结束时调用）。"""
        self.current_partial_text = ""

