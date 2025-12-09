"""WebSocket streaming endpoint registration.

基于 FunASR Demo 的高性能实现，支持直接二进制音频传输。
协议:
1. 连接后首先发送配置 JSON
2. 之后直接发送二进制音频帧
3. 停止时发送 is_speaking=false 的 JSON
"""

from __future__ import annotations

import base64
import binascii
import json
import time
import traceback
import uuid
from typing import Any, Dict, Iterable

from flask import request
from flask_sock import Sock
from simple_websocket.errors import ConnectionClosed

from server.logging import ws_logger, key_logger
from server.services.streaming_session import SessionContext, StreamingSessionManager
from speech_recognition.streaming.engine import StreamingEngine
from speech_recognition.streaming.loader import ModelLoader
from speech_recognition.streaming.state import StreamingState
from speech_recognition.streaming.text_accumulator import TextAccumulator

# FunASR 风格的配置字段（与 FunASR Demo 一致）
FUNASR_CONFIG_FIELDS = {
    "chunk_size", "chunk_interval", "wav_name", "is_speaking", 
    "mode", "itn", "hotwords", "encoder_chunk_look_back", "decoder_chunk_look_back",
    "sample_rate", "language"
}


def _apply_config(state: StreamingState, payload: Dict[str, Any]) -> None:
    """应用配置消息（支持 FunASR 风格配置）。"""
    # 关键日志：记录配置应用
    ws_logger.info(f"[ws] _apply_config: session={state.session_id}, payload={payload}")
    
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
    
    # FunASR 扩展配置
    if "chunk_size" in payload:
        chunk_size = payload["chunk_size"]
        if isinstance(chunk_size, str):
            chunk_size = chunk_size.split(",")
        try:
            state.chunk_size = [int(x) for x in chunk_size]
        except (TypeError, ValueError):
            ws_logger.warning("invalid chunk_size in config payload")
    if "encoder_chunk_look_back" in payload:
        try:
            state.encoder_chunk_look_back = int(payload["encoder_chunk_look_back"])
        except (TypeError, ValueError):
            ws_logger.warning("invalid encoder_chunk_look_back in config payload")
    if "decoder_chunk_look_back" in payload:
        try:
            state.decoder_chunk_look_back = int(payload["decoder_chunk_look_back"])
        except (TypeError, ValueError):
            ws_logger.warning("invalid decoder_chunk_look_back in config payload")
    if "itn" in payload:
        state.enable_itn = bool(payload["itn"])
    if "wav_name" in payload:
        state.wav_name = payload["wav_name"]
    
    # 关键日志：记录配置应用后的状态
    ws_logger.info(
        f"[ws] config applied: mode={state.mode}, chunk_interval={state.chunk_interval}, "
        f"chunk_size={state.chunk_size}, itn={state.enable_itn}, wav_name={state.wav_name}"
    )


def _is_funasr_config(payload: Dict[str, Any]) -> bool:
    """检测是否为 FunASR 风格的配置消息。"""
    # 如果包含 FunASR 配置字段，且没有 type 字段，则认为是 FunASR 配置
    if "type" not in payload:
        return bool(FUNASR_CONFIG_FIELDS & set(payload.keys()))
    return False


def _decode_audio_chunk(payload: Dict[str, Any]) -> bytes:
    """兼容 legacy JSON chunk（base64/hex/列表）。"""
    audio_field = payload.get("audio") or payload.get("data")
    if audio_field is None:
        return b""
    # base64 字符串
    if isinstance(audio_field, str):
        try:
            return base64.b64decode(audio_field, validate=False)
        except binascii.Error:
            try:
                return bytes.fromhex(audio_field)
            except ValueError:
                return b""
    # 数字列表
    if isinstance(audio_field, (list, tuple)):
        try:
            return bytes(audio_field)
        except Exception:  # pragma: no cover - 容错
            return b""
    return b""


def _apply_control(
    state: StreamingState,
    payload: Dict[str, Any],
    engine: StreamingEngine,
    ws,
    request_id: str,
) -> None:
    """应用控制消息（与官方 demo 对齐）。"""
    if "chunk_interval" in payload:
        try:
            state.chunk_interval = int(payload["chunk_interval"])
        except (TypeError, ValueError):
            ws_logger.warning("invalid chunk_interval in control payload")
    if "hotwords" in payload:
        state.hotwords = payload["hotwords"] or {}
    if "is_speaking" in payload:
        state.metrics["is_speaking"] = payload["is_speaking"]
        # 与官方 demo 对齐：设置 funasr_state.online_is_final
        funasr_state = engine.get_funasr_state(state)
        if funasr_state is not None:
            funasr_state.online_is_final = not payload["is_speaking"]
            funasr_state.is_speaking = payload["is_speaking"]
            ws_logger.info(
                f"[ws] control: is_speaking={payload['is_speaking']} "
                f"online_is_final={funasr_state.online_is_final}"
            )
    if payload.get("is_speaking") is False:
        t_flush_start = time.time()
        events = engine.flush(state)
        flush_ms = (time.time() - t_flush_start) * 1000
        state.mark_segment_final(state.current_segment_id)
        _send_events(ws, events, state, request_id)
        ws_logger.info(
            f"[ws] control flush: session={state.session_id} events={len(events)} "
            f"chunk_count={state.metrics.get('chunk_count', 0)} took={flush_ms:.1f}ms"
        )


def _send_events(
    ws,
    events: Iterable[Dict[str, Any]],
    state: StreamingState,
    request_id: str,
) -> None:
    """发送事件到客户端。
    
    响应格式兼容两种模式：
    1. 官方 FunASR Demo 格式（简单）: {mode, text, wav_name, is_final}
    2. nevoice 扩展格式（详细）: 包含 type, text_state, session_id, segment_id 等
    
    当前实现同时输出两种格式的字段，前端可根据需要选择使用。
    """
    events_list = list(events or [])
    events_list.sort(key=lambda e: e.get('text_state', {}).get('revision_id', 0))

    for event in events_list:
        # === nevoice 扩展字段 ===
        event.setdefault("session_id", state.session_id)
        event.setdefault("request_id", request_id)

        segment_id = event.get("segment_id") or state.ensure_segment()
        event["segment_id"] = segment_id
        
        timestamps = event.setdefault("timestamps", {})
        timestamps.setdefault("event_ms", int(time.time() * 1000))

        metadata = event.setdefault("metadata", {})
        if state.hotwords:
            metadata.setdefault("hotwords", sorted(state.hotwords.keys()))

        # === 官方 FunASR Demo 兼容字段（与 funasr_wss_server.py 对齐）===
        # mode: 2pass-online, 2pass-offline, online, offline
        event_type = event.get("type", "")
        current_mode = state.mode or "2pass"
        if event_type == "partial":
            funasr_mode = "2pass-online" if current_mode == "2pass" else current_mode
        elif event_type == "correction":
            funasr_mode = "2pass-offline" if current_mode == "2pass" else current_mode
        else:
            funasr_mode = event.get("mode") or current_mode
        event["mode"] = funasr_mode
        
        # wav_name: 与官方 demo 一致
        event.setdefault("wav_name", state.wav_name)
        
        # is_final: 官方 demo 语义是"客户端是否仍在说话"，True 表示仍在说话
        # 但 nevoice 的 is_final 语义是"本段是否结束"
        # 为了兼容性，我们同时输出两个字段
        is_speaking = state.metrics.get("is_speaking", True)
        event.setdefault("is_final", not is_speaking)  # nevoice 语义：段结束
        event["is_speaking"] = is_speaking  # 官方 demo 语义：仍在说话

        if event.get("is_final"):
            state.mark_segment_final(segment_id)
        
        # 发送事件到客户端
        event_json = json.dumps(event)
        ws.send(event_json)
        
        # 关键日志：观察实时/纠错事件输出节奏
        text_preview = (event.get('text') or '')[:50]
        if len(event.get('text') or '') > 50:
            text_preview += '...'
        ws_logger.info(
            f"[ws] SEND session={state.session_id} | "
            f"type={event.get('type')} mode={event.get('mode')} | "
            f"is_final={event.get('is_final')} is_speaking={is_speaking} | "
            f"text_len={len(event.get('text') or '')} rev={event.get('revision')} | "
            f"text=\"{text_preview}\""
        )


def _send_error(ws, code: int, message: str) -> None:
    """发送错误消息。"""
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
    """注册 WebSocket 路由。"""
    
    @sock.route("/ws/recognize", methods=["GET"])
    def recognize(ws):
        """
        实时语音识别 WebSocket 端点。
        
        支持 FunASR Demo 风格的协议：
        1. 连接后首先发送配置 JSON（包含 chunk_size, mode, is_speaking 等）
        2. 之后直接发送二进制音频帧（PCM 16kHz 16bit）
        3. 停止时发送 is_speaking=false 的 JSON
        
        也兼容 legacy 协议（start/chunk/end 消息）。
        """
        manager = StreamingSessionManager.current()
        session_id = str(uuid.uuid4())[:8]
        request_id = request.args.get("request_id", session_id)
        key_logger.info(f"request_id={request_id} session={session_id} websocket started")
        ws_logger.info(f"[ws] 会话开始 session={session_id}")

        model_loader = ModelLoader.current()
        engine = StreamingEngine()

        # 从配置获取默认值
        config = model_loader.config
        audio_config = config.get("audio", {})
        mode_config = config.get("mode", {})
        
        state = StreamingState(
            session_id=session_id,
            request_id=request_id,
            chunk_interval=audio_config.get("chunk_interval", 10),
            sample_rate=audio_config.get("sample_rate", 16000),
            hotwords={},
            mode=mode_config.get("default", "2pass"),
            chunk_size=audio_config.get("chunk_size", [5, 10, 5]),
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
        state.metrics["is_speaking"] = True
        state.metrics["chunk_count"] = 0  # 统计接收的音频块数量
        state.metrics["total_process_ms"] = 0  # 累计处理时间
        state.metrics["total_audio_ms"] = 0  # 累计音频时长
        state.metrics["max_rtf"] = 0  # 最大实时因子
        
        ws_logger.info(f"[ws] session={session_id} engine_ready={engine.is_ready}")

        try:
            while True:
                message = ws.receive()
                if message is None:
                    ws_logger.info(f"[ws] session={session_id} connection closed by client")
                    break

                # 优先处理二进制数据（FunASR Demo 风格）
                if isinstance(message, (bytes, bytearray)):
                    import time as _time
                    t_recv = _time.time()
                    state.metrics["chunk_count"] += 1
                    chunk_num = state.metrics["chunk_count"]
                    now_ms = int(t_recv * 1000)
                    
                    # 计算音频时长 (16kHz, 16bit = 32 bytes/ms)
                    audio_chunk_ms = len(message) // 32
                    state.metrics["total_audio_ms"] = state.metrics.get("total_audio_ms", 0) + audio_chunk_ms
                    
                    prev_ms = state.metrics.get("last_chunk_ms")
                    if prev_ms and now_ms - prev_ms > 1500:
                        ws_logger.warning(
                            f"[WS-GAP] session={session_id} chunk#{chunk_num} gap={now_ms - prev_ms}ms "
                            f"(expected ~{audio_chunk_ms}ms)"
                        )
                    state.metrics["last_chunk_ms"] = now_ms
                    
                    # 更频繁的日志（前10个、每30个）
                    if chunk_num <= 10 or chunk_num % 30 == 0:
                        ws_logger.info(
                            f"[WS-RECV] session={session_id} chunk#{chunk_num} len={len(message)} "
                            f"audio_ms={audio_chunk_ms} total_audio_ms={state.metrics['total_audio_ms']}"
                        )
                    
                    events = engine.push(message, state)
                    t_process = _time.time()
                    _send_events(ws, events, state, request_id)
                    t_send = _time.time()
                    
                    # 记录每个 chunk 的处理时间
                    process_ms = (t_process - t_recv) * 1000
                    send_ms = (t_send - t_process) * 1000
                    total_ms = (t_send - t_recv) * 1000
                    
                    # 更新累计统计
                    state.metrics["total_process_ms"] = state.metrics.get("total_process_ms", 0) + total_ms
                    rtf = total_ms / max(audio_chunk_ms, 1)
                    state.metrics["max_rtf"] = max(state.metrics.get("max_rtf", 0), rtf)
                    
                    # 计算累积延迟估计
                    cumulative_process_ms = state.metrics["total_process_ms"]
                    cumulative_audio_ms = state.metrics["total_audio_ms"]
                    estimated_lag_ms = cumulative_process_ms - cumulative_audio_ms
                    avg_rtf = cumulative_process_ms / max(cumulative_audio_ms, 1)
                    
                    # 【关键诊断】检测延迟累积
                    if rtf > 1.0:
                        ws_logger.warning(
                            f"[WS-SLOW] session={session_id} chunk#{chunk_num} "
                            f"RTF={rtf:.2f} (>1.0 FALLING BEHIND!) "
                            f"process={process_ms:.1f}ms audio={audio_chunk_ms}ms "
                            f"estimated_lag={estimated_lag_ms:.0f}ms avg_RTF={avg_rtf:.2f} "
                            f"events={len(events)}"
                        )
                    elif len(events) > 0 or total_ms > 80 or chunk_num % 30 == 0:
                        ws_logger.info(
                            f"[WS-TIMING] session={session_id} chunk#{chunk_num} "
                            f"RTF={rtf:.2f} process={process_ms:.1f}ms send={send_ms:.1f}ms "
                            f"total={total_ms:.1f}ms events={len(events)} "
                            f"lag_est={estimated_lag_ms:.0f}ms"
                        )
                    continue

                # JSON 消息处理
                try:
                    payload = json.loads(message)
                except json.JSONDecodeError:
                    ws_logger.warning(f"[ws] session={session_id} invalid JSON payload")
                    _send_error(ws, 440001, "invalid json payload")
                    continue

                message_type = payload.get("type")
                
                # FunASR 风格配置（无 type 字段）
                if _is_funasr_config(payload):
                    ws_logger.info(f"[ws] session={session_id} FunASR config: {payload}")
                    _apply_config(state, payload)
                    
                    # 处理 is_speaking 状态变化（与官方 demo 对齐）
                    # 官方行为：收到 is_speaking 时立即设置 online_is_final = not is_speaking
                    if "is_speaking" in payload:
                        state.metrics["is_speaking"] = payload["is_speaking"]
                        # 与官方 demo 对齐：设置 funasr_state.online_is_final
                        funasr_state = engine.get_funasr_state(state)
                        if funasr_state is not None:
                            funasr_state.online_is_final = not payload["is_speaking"]
                            funasr_state.is_speaking = payload["is_speaking"]
                            ws_logger.info(
                                f"[ws] session={session_id} is_speaking={payload['is_speaking']} "
                                f"online_is_final={funasr_state.online_is_final}"
                            )
                        
                        if payload["is_speaking"] is False:
                            ws_logger.info(f"[ws] session={session_id} is_speaking=false, flushing")
                            t_flush = time.time()
                            events = engine.flush(state)
                            flush_ms = (time.time() - t_flush) * 1000
                            state.mark_segment_final(state.current_segment_id)
                            _send_events(ws, events, state, request_id)
                            ws_logger.info(
                                f"[ws] session={session_id} flush_on_is_speaking_false "
                                f"events={len(events)} took={flush_ms:.1f}ms"
                            )
                            
                            # 发送处理完成信号，告诉前端可以关闭连接
                            complete_msg = {
                                "type": "session_complete",
                                "session_id": session_id,
                                "is_final": True,
                                "is_speaking": False,
                                "message": "all audio processed",
                            }
                            ws.send(json.dumps(complete_msg))
                            ws_logger.info(
                                f"[ws] session={session_id} sent session_complete signal"
                            )
                    continue
                
                # config/control 消息
                if message_type in {"config", "control"}:
                    ws_logger.debug(
                        f"[ws] session={session_id} received config/control: {payload}"
                    )
                    _apply_config(state, payload)
                    if message_type == "control":
                        _apply_control(state, payload, engine, ws, request_id)
                    continue

                # Legacy 协议：start/chunk/end
                if message_type == "start":
                    ws_logger.info(f"[ws] session={session_id} legacy start received")
                    state.metrics["is_speaking"] = True
                    continue
                    
                if message_type == "chunk":
                    audio_bytes = _decode_audio_chunk(payload)
                    if not audio_bytes:
                        ws_logger.warning(
                            f"[ws] session={session_id} legacy chunk decode failed"
                        )
                        _send_error(ws, 440002, "invalid audio chunk")
                        continue
                    state.metrics["chunk_count"] += 1
                    events = engine.push(audio_bytes, state)
                    _send_events(ws, events, state, request_id)
                    continue
                    
                if message_type == "end":
                    ws_logger.info(f"[ws] session={session_id} legacy end received")
                    state.metrics["is_speaking"] = False
                    events = engine.flush(state)
                    _send_events(ws, events, state, request_id)
                    continue

                if message_type == "ping":
                    ws.send(json.dumps({"type": "pong", "ts": payload.get("ts")}))
                    continue

                # 如果包含 data 字段，尝试作为 legacy chunk 处理
                if "data" in payload:
                    audio_bytes = _decode_audio_chunk(payload)
                    if audio_bytes:
                        state.metrics["chunk_count"] += 1
                        events = engine.push(audio_bytes, state)
                        _send_events(ws, events, state, request_id)
                        continue

                ws_logger.warning(
                    f"[ws] session={session_id} unsupported message: {payload}"
                )
                
        except ConnectionClosed as exc:
            # 正常关闭（code=1000）不记录为错误
            if exc.reason == 1000:
                ws_logger.info(
                    f"[ws] session={session_id} connection closed normally: {exc.message}"
                )
            else:
                ws_logger.warning(
                    f"[ws] session={session_id} connection closed abnormally: code={exc.reason} message={exc.message}"
                )
        except Exception as exc:  # pylint: disable=broad-except
            ws_logger.error(
                f"[ws] session={session_id} exception: {exc}\n{traceback.format_exc()}"
            )
            _send_error(ws, 50001, "internal server error")
        finally:
            total_chunks = state.metrics.get("chunk_count", 0)
            duration_ms = int(time.time() * 1000) - state.metrics.get("started_ms", 0)
            total_audio_ms = state.metrics.get("total_audio_ms", 0)
            total_process_ms = state.metrics.get("total_process_ms", 0)
            max_rtf = state.metrics.get("max_rtf", 0)
            avg_rtf = total_process_ms / max(total_audio_ms, 1) if total_audio_ms > 0 else 0
            
            last_chunk_ms = state.metrics.get("last_chunk_ms")
            if last_chunk_ms:
                gap_ms = int(time.time() * 1000) - last_chunk_ms
                ws_logger.info(
                    f"[WS-END] session={session_id} gap_since_last_chunk={gap_ms}ms"
                )
            
            # 【关键诊断】会话结束统计
            ws_logger.info(
                f"[WS-SUMMARY] session={session_id} "
                f"chunks={total_chunks}, session_duration={duration_ms}ms, "
                f"total_audio={total_audio_ms}ms, total_process={total_process_ms:.0f}ms, "
                f"avg_RTF={avg_rtf:.2f}, max_RTF={max_rtf:.2f}, "
                f"estimated_lag={(total_process_ms - total_audio_ms):.0f}ms"
            )
            
            if avg_rtf > 1.0:
                ws_logger.warning(
                    f"[WS-PERF-ISSUE] session={session_id} "
                    f"avg_RTF={avg_rtf:.2f} > 1.0 indicates system cannot keep up with real-time! "
                    f"Consider: 1) Check GPU utilization 2) Reduce chunk_interval 3) Check for blocking operations"
                )
            
            t_final_flush = time.time()
            events = engine.flush(state)
            flush_ms = (time.time() - t_final_flush) * 1000
            _send_events(ws, events, state, request_id)
            ws_logger.info(
                f"[WS-FLUSH] session={session_id} final_flush events={len(events)} took={flush_ms:.1f}ms"
            )
            engine.cleanup_session(session_id)
            manager.close_session(session_id)
            ws_logger.info(f"[ws] 会话结束 session={session_id}")
            key_logger.info(f"request_id={request_id} session={session_id} websocket closed")
