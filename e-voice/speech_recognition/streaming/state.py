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
    mode: str = "2pass"
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

