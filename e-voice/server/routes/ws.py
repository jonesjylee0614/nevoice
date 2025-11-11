"""WebSocket streaming endpoint registration."""

from __future__ import annotations

import json
import time
import traceback
import uuid
from typing import Any, Dict, Iterable

from flask import request
from flask_sock import Sock

from server.logging import ws_logger, key_logger
from server.services.streaming_session import SessionContext, StreamingSessionManager
from speech_recognition.streaming.engine import StreamingEngine
from speech_recognition.streaming.loader import ModelLoader
from speech_recognition.streaming.state import StreamingState
from speech_recognition.streaming.text_accumulator import TextAccumulator

CONFIG_MESSAGE_TYPES = {"config", "control"}


def _apply_config(state: StreamingState, payload: Dict[str, Any]) -> None:
    if "mode" in payload:
        state.mode = payload["mode"]
    if "language" in payload:
        state.language = payload["language"]
    if "sample_rate" in payload:
        try:
            state.sample_rate = int(payload["sample_rate"])
        except (TypeError, ValueError):
            ws_logger.warning("invalid sample_rate in config payload")
    if "hotwords" in payload:
        state.hotwords = payload["hotwords"] or {}
    if "chunk_interval" in payload:
        try:
            state.chunk_interval = int(payload["chunk_interval"])
        except (TypeError, ValueError):
            ws_logger.warning("invalid chunk_interval in config payload")


def _apply_control(
    state: StreamingState,
    payload: Dict[str, Any],
    engine: StreamingEngine,
    ws,
    request_id: str,
) -> None:
    if "chunk_interval" in payload:
        try:
            state.chunk_interval = int(payload["chunk_interval"])
        except (TypeError, ValueError):
            ws_logger.warning("invalid chunk_interval in control payload")
    if "hotwords" in payload:
        state.hotwords = payload["hotwords"] or {}
    if "is_speaking" in payload:
        state.metrics["is_speaking"] = payload["is_speaking"]
    if payload.get("is_speaking") is False and state.mode != "online":
        events = engine.flush(state)
        state.mark_segment_final(state.current_segment_id)
        _send_events(ws, events, state, request_id)


def _run_vad(state: StreamingState, bundle, audio_chunk: bytes) -> bool:
    if bundle.vad is None:
        return False
    try:
        result = bundle.vad.generate(input=audio_chunk, **state.vad_state)[0]["value"]
        state.vad_state = result.get("cache", state.vad_state)
        if result and isinstance(result, list) and result[0][1] != -1:
            return True
    except Exception as exc:  # pylint: disable=broad-except
        ws_logger.warning(f"[ws] VAD 执行失败: {exc}")
    return False


def _send_events(
    ws,
    events: Iterable[Dict[str, Any]],
    state: StreamingState,
    request_id: str,
) -> None:
    # ✅ P0-1 修复：按 revision_id 严格排序，防止前端收到乱序事件导致文本闪回
    # 将 Iterable 转为 list 以支持排序
    events_list = list(events or [])
    events_list.sort(key=lambda e: e.get('text_state', {}).get('revision_id', 0))

    for event in events_list:
        event.setdefault("session_id", state.session_id)
        event.setdefault("request_id", request_id)

        # ✅ P0-3 修复：简化 segment_id 逻辑，engine 中已设置，这里仅做兜底
        # engine.push() 和 flush() 已经通过 ensure_segment() 设置了 segment_id
        # 这里只在缺失时补充，确保同一句话的 partial 和 correction 使用相同 ID
        event.setdefault("segment_id", state.ensure_segment())
        event.setdefault(
            "mode",
            event.get("mode") or ("offline" if event.get("type") == "correction" else "realtime"),
        )
        timestamps = event.setdefault("timestamps", {})
        timestamps.setdefault("event_ms", int(time.time() * 1000))

        metadata = event.setdefault("metadata", {})
        if state.hotwords:
            metadata.setdefault("hotwords", sorted(state.hotwords.keys()))

        if event.get("is_final"):
            state.mark_segment_final(segment_id)
        ws.send(json.dumps(event))


def _send_error(ws, code: int, message: str) -> None:
    ws.send(
        json.dumps(
            {
                "type": "error",
                "code": code,
                "message": message,
            }
        )
    )


def register_ws_routes(sock: Sock) -> None:
    @sock.route("/ws/recognize", methods=["GET"])
    def recognize(ws):
        manager = StreamingSessionManager.current()
        session_id = str(uuid.uuid4())[:8]
        request_id = request.args.get("request_id", session_id)
        key_logger.info(f"request_id={request_id} session={session_id} websocket started")
        ws_logger.info(f"[ws] 会话开始 session={session_id}")

        model_loader = ModelLoader.current()
        bundle = model_loader.get_bundle()
        engine = StreamingEngine()

        state = StreamingState(
            session_id=session_id,
            request_id=request_id,
            chunk_interval=40,
            sample_rate=16000,
            hotwords={},
        )
        accumulator = TextAccumulator()
        state.text_accumulator = accumulator

        context = SessionContext(
            session_id=session_id,
            request_id=request_id,
            state=state,
            text_accumulator=accumulator,
        )
        manager.create_session(context)
        state.metrics["started_ms"] = int(time.time() * 1000)

        try:
            while True:
                message = ws.receive()
                if message is None:
                    ws_logger.info(f"[ws] session={session_id} connection closed by client")
                    break

                if isinstance(message, (bytes, bytearray)):
                    ws_logger.debug(
                        f"[ws] session={session_id} received binary chunk (len={len(message)})"
                    )
                    speech_end = _run_vad(state, bundle, message)
                    events = engine.push(message, state)
                    _send_events(ws, events, state, request_id)
                    if speech_end and state.mode != "online":
                        _apply_control(state, {"is_speaking": False}, engine, ws, request_id)
                    continue

                try:
                    payload = json.loads(message)
                except json.JSONDecodeError:
                    ws_logger.warning(f"[ws] session={session_id} invalid JSON payload")
                    _send_error(ws, 440001, "invalid json payload")
                    continue

                message_type = payload.get("type")
                if message_type in CONFIG_MESSAGE_TYPES:
                    ws_logger.debug(
                        f"[ws] session={session_id} received config/control: {payload}"
                    )
                    _apply_config(state, payload)
                    if message_type == "control":
                        _apply_control(state, payload, engine, ws, request_id)
                    continue

                if message_type == "ping":
                    ws.send(json.dumps({"type": "pong", "ts": payload.get("ts")}))
                    continue

                ws_logger.warning(
                    f"[ws] session={session_id} unsupported message type: {message_type}"
                )
                _send_error(ws, 440001, "unsupported message type")
        except Exception as exc:  # pylint: disable=broad-except
            ws_logger.error(
                f"[ws] session={session_id} exception: {exc}\n{traceback.format_exc()}"
            )
            _send_error(ws, 50001, "internal server error")
        finally:
            events = engine.flush(state)
            _send_events(ws, events, state, request_id)
            manager.close_session(session_id)
            ws_logger.info(f"[ws] 会话结束 session={session_id}")
            key_logger.info(f"request_id={request_id} session={session_id} websocket closed")
