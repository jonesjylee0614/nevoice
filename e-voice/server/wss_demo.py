#!/usr/bin/env python
"""Demo-style asyncio WebSocket server (aligned with FunASR runtime demo).

Usage:
    # 直接运行（推荐）
    python server/wss_demo.py --host 0.0.0.0 --port 10096 --ssl
    
    # 或者
    cd nevoice/e-voice && python server/wss_demo.py --port 10096

This keeps the protocol minimal:
    - First text message is JSON config (mode/chunk_size/chunk_interval/itn/wav_name)
    - Subsequent binary messages are raw PCM int16 audio frames
    - Events follow existing nevoice partial/correction schema

The goal is to mirror FunASR/runtime/python/websocket/funasr_wss_server.py behaviour
while复用现有的 FunASRStreamer/ModelLoader。
"""

from __future__ import annotations

# 首先设置路径，避免 server/logging.py 与标准库冲突
import sys
from pathlib import Path

def _setup_path() -> None:
    """设置 Python 路径，确保能导入本地模块且避免命名冲突。"""
    # 添加 e-voice 目录到路径（而不是 server 目录）
    evoice_dir = Path(__file__).resolve().parent.parent
    # 确保 e-voice 目录在路径最前面
    if str(evoice_dir) in sys.path:
        sys.path.remove(str(evoice_dir))
    sys.path.insert(0, str(evoice_dir))
    
    # 移除可能导致冲突的 server 目录
    server_dir = str(evoice_dir / "server")
    if server_dir in sys.path:
        sys.path.remove(server_dir)

_setup_path()

import argparse
import asyncio
import json
import ssl as ssl_module  # 避免与参数名冲突
import uuid
from typing import Any, Dict, Iterable

import websockets
from loguru import logger
from websockets.server import WebSocketServerProtocol

# 直接导入 streaming 模块，避免通过 server 包
from speech_recognition.streaming.engine import StreamingEngine
from speech_recognition.streaming.loader import ModelLoader
from speech_recognition.streaming.state import StreamingState
from speech_recognition.streaming.text_accumulator import TextAccumulator


def build_default_state(config: Dict[str, Any], session_id: str, request_id: str) -> StreamingState:
    audio_cfg = config.get("audio", {})
    mode_cfg = config.get("mode", {})
    return StreamingState(
        session_id=session_id,
        request_id=request_id,
        chunk_interval=audio_cfg.get("chunk_interval", 10),
        sample_rate=audio_cfg.get("sample_rate", 16000),
        hotwords={},
        mode=mode_cfg.get("default", "2pass"),
        chunk_size=audio_cfg.get("chunk_size", [5, 10, 5]),
    )


def apply_config(state: StreamingState, payload: Dict[str, Any]) -> None:
    """应用配置消息（支持 FunASR 风格配置）。"""
    if "mode" in payload:
        state.mode = payload["mode"]
    if "chunk_interval" in payload:
        try:
            state.chunk_interval = int(payload["chunk_interval"])
        except Exception:
            logger.warning("invalid chunk_interval in config payload")
    if "chunk_size" in payload:
        chunk_size = payload["chunk_size"]
        if isinstance(chunk_size, str):
            chunk_size = chunk_size.split(",")
        try:
            state.chunk_size = [int(x) for x in chunk_size]
        except Exception:
            logger.warning("invalid chunk_size in config payload")
    if "itn" in payload:
        state.enable_itn = bool(payload["itn"])
    if "wav_name" in payload:
        state.wav_name = payload["wav_name"]
    if "hotwords" in payload:
        state.hotwords = payload["hotwords"] or {}
    if "is_speaking" in payload:
        state.metrics["is_speaking"] = payload["is_speaking"]


async def send_events(ws: WebSocketServerProtocol, events: Iterable[Dict[str, Any]], state: StreamingState) -> None:
    """发送识别事件到客户端。
    
    转换为 FunASR Demo 兼容格式：
    {
        "mode": "2pass-online" | "2pass-offline" | "online" | "offline",
        "text": "识别文本",
        "wav_name": "h5",
        "is_final": true/false  # 注意：与 is_speaking 一致，不是相反
    }
    """
    for event in events or []:
        if event.get("is_final"):
            state.mark_segment_final(event.get("segment_id"))
        
        # 转换为 FunASR Demo 兼容格式
        # 关键：FunASR Demo 中 is_final = is_speaking（用户正在说话时 is_final=true）
        funasr_event = {
            "mode": event.get("mode", "2pass-online"),
            "text": event.get("text", ""),
            "wav_name": state.wav_name or "h5",
            "is_final": state.metrics.get("is_speaking", True),
        }
        await ws.send(json.dumps(funasr_event))


async def handler(ws: WebSocketServerProtocol) -> None:
    model_loader = ModelLoader.current()
    engine = StreamingEngine()

    cfg = model_loader.config
    session_id = str(uuid.uuid4())[:8]
    request_id = session_id
    state = build_default_state(cfg, session_id, request_id)
    state.metrics["is_speaking"] = True
    state.text_accumulator = TextAccumulator()
    logger.info(f"[wss-demo] session={session_id} connected engine_ready={engine.is_ready}")

    chunk_count = 0
    try:
        async for message in ws:
            # 优先处理二进制音频数据（高频路径）
            if isinstance(message, bytes):
                chunk_count += 1
                if chunk_count <= 3 or chunk_count % 100 == 0:
                    logger.debug(f"[wss-demo] session={session_id} chunk #{chunk_count} len={len(message)}")
                events = engine.push(message, state)
                await send_events(ws, events, state)
                continue
            
            # JSON 消息处理
            try:
                payload = json.loads(message)
            except Exception:
                logger.warning(f"[wss-demo] session={session_id} invalid json payload")
                continue
            
            msg_type = payload.get("type") or payload.get("message_type")
            
            # FunASR 风格配置（无 type 字段，但包含 chunk_size/is_speaking 等）
            if msg_type is None:
                apply_config(state, payload)
                # 处理 is_speaking=false 触发 flush
                if payload.get("is_speaking") is False and state.mode != "online":
                    logger.info(f"[wss-demo] session={session_id} is_speaking=false, flushing")
                    events = engine.flush(state)
                    await send_events(ws, events, state)
                else:
                    logger.info(f"[wss-demo] session={session_id} FunASR config applied: {payload}")
                continue
            
            if msg_type in ("config", "start"):
                apply_config(state, payload)
                logger.info(f"[wss-demo] session={session_id} config applied {payload}")
                continue
            if msg_type == "control":
                apply_config(state, payload)
                if payload.get("is_speaking") is False and state.mode != "online":
                    state.metrics["is_speaking"] = False
                    events = engine.flush(state)
                    await send_events(ws, events, state)
                continue
            if msg_type == "ping":
                await ws.send(json.dumps({"type": "pong", "ts": payload.get("ts")}))
                continue
            if msg_type == "end":
                logger.info(f"[wss-demo] session={session_id} end received")
                state.metrics["is_speaking"] = False
                events = engine.flush(state)
                await send_events(ws, events, state)
                continue
    except websockets.ConnectionClosed:
        logger.info(f"[wss-demo] session={session_id} closed")
    finally:
        events = engine.flush(state)
        try:
            await send_events(ws, events, state)
        except Exception:
            pass
        engine.cleanup_session(session_id)
        logger.info(f"[wss-demo] session={session_id} cleanup done")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10096)
    parser.add_argument("--certfile", type=str, default="", help="cert file for TLS")
    parser.add_argument("--keyfile", type=str, default="", help="key file for TLS")
    args = parser.parse_args()

    # 基础日志（控制台 + 文件）
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
    logger.add(log_dir / "wss_demo.log", level="INFO", format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}", rotation="20 MB", retention="7 days", encoding="utf-8")

    # 预加载模型（与现有配置一致）
    loader = ModelLoader.current()
    bundle = loader.load()
    logger.info(f"[wss-demo] FunASR 模型加载完成，device_config={loader.config.get('resources')}")
    logger.info(f"[wss-demo] models ready: asr={bool(bundle.model_asr)} online={bool(bundle.model_asr_online)} vad={bool(bundle.model_vad)} punc={bool(bundle.model_punc)}")

    ssl_ctx = None
    if args.certfile and args.keyfile:
        ssl_ctx = ssl_module.SSLContext(ssl_module.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(args.certfile, args.keyfile)

    # websockets 12.x+ 只传递一个参数（connection），不再传递 path
    # 从 connection.request.path 获取路径
    async def connection_handler(ws):
        path = getattr(ws, 'path', '/') or '/'
        # 如果是新版本 websockets，从 request 获取路径
        if hasattr(ws, 'request') and ws.request:
            path = ws.request.path or '/'
        logger.info(f"[wss-demo] connection on path: {path}")
        await handler(ws)
    
    # 不要求特定的 subprotocol，让浏览器可以直接连接
    async with websockets.serve(connection_handler, args.host, args.port, ping_interval=None, ssl=ssl_ctx):
        logger.info(f"[wss-demo] server started on {args.host}:{args.port} ssl={'on' if ssl_ctx else 'off'}")
        logger.info(f"[wss-demo] supported paths: /, /ws/recognize")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
