"""Streaming metrics collection helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class StreamingMetrics:
    stream_latency_ms: float = 0.0
    correction_latency_ms: float = 0.0
    active_sessions: int = 0
    chunk_drop_count: int = 0
    extras: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, float]:
        data = {
            "stream_latency_ms": self.stream_latency_ms,
            "correction_latency_ms": self.correction_latency_ms,
            "active_sessions": float(self.active_sessions),
            "chunk_drop_count": float(self.chunk_drop_count),
        }
        data.update(self.extras)
        return data
