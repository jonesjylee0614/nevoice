"""Streaming 会话管理器。"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Optional

from server.logging import ws_logger
from monitoring.streaming_metrics import StreamingMetrics
from speech_recognition.streaming.state import StreamingState
from speech_recognition.streaming.text_accumulator import TextAccumulator


@dataclass(slots=True)
class SessionContext:
    session_id: str
    request_id: str
    state: StreamingState
    text_accumulator: TextAccumulator | None


class StreamingSessionManager:
    """占位实现，后续将提供实际的会话管理逻辑。"""

    _instance: "StreamingSessionManager | None" = None

    def __init__(self) -> None:
        self._sessions: dict[str, SessionContext] = {}
        self._lock = Lock()
        self._metrics = StreamingMetrics()

    @classmethod
    def current(cls) -> "StreamingSessionManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_session(self, context: SessionContext) -> SessionContext:
        ws_logger.debug(
            f"[session] register session={context.session_id} request={context.request_id}"
        )
        with self._lock:
            self._sessions[context.session_id] = context
            self._metrics.active_sessions = len(self._sessions)
        return context

    def close_session(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._sessions:
                ws_logger.debug(f"[session] close session={session_id}")
                self._sessions.pop(session_id, None)
                self._metrics.active_sessions = len(self._sessions)

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        with self._lock:
            return self._sessions.get(session_id)

    def metrics_snapshot(self) -> StreamingMetrics:
        with self._lock:
            return StreamingMetrics(**self._metrics.to_dict())

    def record_metrics(
        self,
        *,
        stream_latency_ms: float | None = None,
        correction_latency_ms: float | None = None,
        chunk_drop_count: int | None = None,
    ) -> None:
        with self._lock:
            if stream_latency_ms is not None:
                self._metrics.stream_latency_ms = stream_latency_ms
            if correction_latency_ms is not None:
                self._metrics.correction_latency_ms = correction_latency_ms
            if chunk_drop_count is not None:
                self._metrics.chunk_drop_count = chunk_drop_count

