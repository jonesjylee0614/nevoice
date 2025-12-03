#!/usr/bin/env python
"""FunASR 兼容的 WebSocket 服务器。

与 FunASR/runtime/python/websocket/funasr_wss_server.py 逻辑完全一致，
只是使用 nevoice 的 ModelLoader 加载模型。

Usage:
    python server/wss_funasr_compatible.py --port 10096
    python server/wss_funasr_compatible.py --port 10096 --certfile ssl_key/server.crt --keyfile ssl_key/server.key
"""

from __future__ import annotations

import sys
from pathlib import Path

# 设置路径
def _setup_path() -> None:
    evoice_dir = Path(__file__).resolve().parent.parent
    if str(evoice_dir) in sys.path:
        sys.path.remove(str(evoice_dir))
    sys.path.insert(0, str(evoice_dir))
    server_dir = str(evoice_dir / "server")
    if server_dir in sys.path:
        sys.path.remove(server_dir)

_setup_path()

import argparse
import asyncio
import json
import ssl as ssl_module
import re
import os

import websockets
from loguru import logger

# 导入模型加载器
from speech_recognition.streaming.loader import ModelLoader

# 尝试导入 cn2an
try:
    import cn2an
except ImportError:
    cn2an = None

# 尝试导入 ITN
try:
    from fun_text_processing.inverse_text_normalization.inverse_normalize import (
        InverseNormalizer,
    )
except ImportError:
    InverseNormalizer = None


# ============================================================================
# 全局变量（与 FunASR Demo 一致）
# ============================================================================
websocket_users = set()
model_asr = None
model_asr_streaming = None
model_vad = None
model_punc = None
inverse_normalizer = None


def postprocess_numbers(text: str) -> str:
    """将中文数字转换为阿拉伯数字。"""
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

    text = re.sub(r"百分之([〇零一二两三四五六七八九十百千万亿兆点]+)", _conv_percent, text)
    text = re.sub(r"([〇零一二两三四五六七八九十百千零点两]+)([万亿兆])", _conv_with_unit, text)
    text = re.sub(r"[〇零一二两三四五六七八九十百千万亿兆点]+", _conv_plain, text)
    return text


def apply_itn(text: str) -> str:
    """应用 ITN 逆文本归一化。"""
    if not text:
        return text
    if inverse_normalizer is None:
        return postprocess_numbers(text)
    try:
        normalized = inverse_normalizer.inverse_normalize_list([text], verbose=False)[0]
        return postprocess_numbers(normalized)
    except Exception as e:
        logger.warning(f"ITN error, fallback to raw text: {e}")
        return postprocess_numbers(text)


async def ws_reset(websocket):
    """重置 WebSocket 连接。"""
    logger.info(f"ws reset, total users: {len(websocket_users)}")
    websocket.status_dict_asr_online["cache"] = {}
    websocket.status_dict_asr_online["is_final"] = True
    websocket.status_dict_vad["cache"] = {}
    websocket.status_dict_vad["is_final"] = True
    websocket.status_dict_punc["cache"] = {}
    await websocket.close()


async def async_vad(websocket, audio_in):
    """执行 VAD 检测。"""
    segments_result = model_vad.generate(input=audio_in, **websocket.status_dict_vad)[0]["value"]
    
    speech_start = -1
    speech_end = -1
    
    if len(segments_result) == 0 or len(segments_result) > 1:
        return speech_start, speech_end
    if segments_result[0][0] != -1:
        speech_start = segments_result[0][0]
        logger.info(f"[vad] speech_start detected at {speech_start}ms")
    if segments_result[0][1] != -1:
        speech_end = segments_result[0][1]
        logger.info(f"[vad] speech_end detected at {speech_end}ms")
    return speech_start, speech_end


async def async_asr(websocket, audio_in):
    """执行离线 ASR。"""
    logger.info(f"[offline_asr] called with audio_len={len(audio_in)}")
    if len(audio_in) > 0:
        rec_result = model_asr.generate(input=audio_in, **websocket.status_dict_asr)[0]
        text = rec_result.get("text", "")
        logger.info(f"[offline_asr] raw result: '{text}'")
        
        if model_punc is not None and len(text) > 0:
            rec_result = model_punc.generate(
                input=text, **websocket.status_dict_punc
            )[0]
            text = rec_result.get("text", text)
            logger.info(f"[offline_asr] after punc: '{text}'")
        
        if len(text) > 0:
            text = apply_itn(text)
            logger.info(f"[offline_asr] after itn: '{text}'")
        
        if len(text) > 0:
            mode = "2pass-offline" if "2pass" in websocket.mode else websocket.mode
            message = json.dumps({
                "mode": mode,
                "text": text,
                "wav_name": websocket.wav_name,
                "is_final": websocket.is_speaking,
            })
            logger.info(f"[offline_asr] sending: {message}")
            await websocket.send(message)
    else:
        mode = "2pass-offline" if "2pass" in websocket.mode else websocket.mode
        message = json.dumps({
            "mode": mode,
            "text": "",
            "wav_name": websocket.wav_name,
            "is_final": websocket.is_speaking,
        })
        logger.info(f"[offline_asr] sending empty: {message}")
        await websocket.send(message)


async def async_asr_online(websocket, audio_in):
    """执行在线流式 ASR。"""
    if len(audio_in) > 0:
        logger.debug(f"[online_asr] input_len={len(audio_in)}, is_final={websocket.status_dict_asr_online.get('is_final', False)}")
        rec_result = model_asr_streaming.generate(
            input=audio_in, **websocket.status_dict_asr_online
        )[0]
        
        text = rec_result.get("text", "")
        # 只在有结果时打印日志
        if text:
            logger.info(f"[online_asr] result: '{text}'")
        
        if websocket.mode == "2pass" and websocket.status_dict_asr_online.get("is_final", False):
            logger.debug("[online_asr] skipping final in 2pass mode")
            return
        
        if len(text):
            if websocket.status_dict_asr_online.get("is_final", False):
                text = apply_itn(text)
            
            mode = "2pass-online" if "2pass" in websocket.mode else websocket.mode
            message = json.dumps({
                "mode": mode,
                "text": text,
                "wav_name": websocket.wav_name,
                "is_final": websocket.is_speaking,
            })
            logger.info(f"[online_asr] sending: {message}")
            await websocket.send(message)


async def ws_serve(websocket):
    """WebSocket 连接处理。与 FunASR Demo 逻辑完全一致。"""
    frames = []
    frames_asr = []
    frames_asr_online = []
    
    global websocket_users
    websocket_users.add(websocket)
    
    # 初始化状态（与 FunASR Demo 完全一致）
    websocket.status_dict_asr = {"itn": True}
    websocket.status_dict_asr_online = {"cache": {}, "is_final": False, "itn": True}
    websocket.status_dict_vad = {"cache": {}, "is_final": False}
    websocket.status_dict_punc = {"cache": {}}
    websocket.chunk_interval = 10  # 每 10 帧触发一次识别
    websocket.vad_pre_idx = 0
    speech_start = False
    speech_end_i = -1
    websocket.wav_name = "microphone"
    websocket.mode = "2pass"
    websocket.is_speaking = True
    
    logger.info("new user connected")
    
    try:
        async for message in websocket:
            if isinstance(message, str):
                messagejson = json.loads(message)
                logger.info(f"[config] received JSON config: {messagejson}")
                
                if "is_speaking" in messagejson:
                    websocket.is_speaking = messagejson["is_speaking"]
                    websocket.status_dict_asr_online["is_final"] = not websocket.is_speaking
                    logger.info(f"[config] is_speaking={websocket.is_speaking}")
                if "chunk_interval" in messagejson:
                    websocket.chunk_interval = messagejson["chunk_interval"]
                if "wav_name" in messagejson:
                    websocket.wav_name = messagejson.get("wav_name")
                if "chunk_size" in messagejson:
                    chunk_size = messagejson["chunk_size"]
                    if isinstance(chunk_size, str):
                        chunk_size = chunk_size.split(",")
                    websocket.status_dict_asr_online["chunk_size"] = [int(x) for x in chunk_size]
                if "encoder_chunk_look_back" in messagejson:
                    websocket.status_dict_asr_online["encoder_chunk_look_back"] = messagejson["encoder_chunk_look_back"]
                if "decoder_chunk_look_back" in messagejson:
                    websocket.status_dict_asr_online["decoder_chunk_look_back"] = messagejson["decoder_chunk_look_back"]
                if "hotwords" in messagejson:
                    websocket.status_dict_asr["hotword"] = messagejson["hotwords"]
                if "itn" in messagejson:
                    websocket.status_dict_asr["itn"] = messagejson["itn"]
                    websocket.status_dict_asr_online["itn"] = messagejson["itn"]
                if "mode" in messagejson:
                    websocket.mode = messagejson["mode"]
                
                logger.info(f"[config] after apply: mode={websocket.mode} chunk_size={websocket.status_dict_asr_online.get('chunk_size')} interval={websocket.chunk_interval}")
            
            websocket.status_dict_vad["chunk_size"] = int(
                websocket.status_dict_asr_online.get("chunk_size", [5, 10, 5])[1] * 60 / websocket.chunk_interval
            )
            
            if len(frames_asr_online) > 0 or len(frames_asr) >= 0 or not isinstance(message, str):
                if not isinstance(message, bytes):
                    continue
                
                # 统计帧数
                frame_count = len(frames) + 1
                    
                frames.append(message)
                duration_ms = len(message) // 32
                websocket.vad_pre_idx += duration_ms
                
                # 每 100 帧打印一次状态（减少日志开销）
                if frame_count % 100 == 0:
                    logger.info(f"[loop] frame#{frame_count} len={len(message)} vad_idx={websocket.vad_pre_idx}ms speech_start={speech_start}")
                
                # 在线 ASR
                frames_asr_online.append(message)
                websocket.status_dict_asr_online["is_final"] = speech_end_i != -1
                
                should_run_online = (len(frames_asr_online) % websocket.chunk_interval == 0
                    or websocket.status_dict_asr_online["is_final"])
                
                if should_run_online:
                    # 减少日志输出以提高性能
                    pass
                    if websocket.mode == "2pass" or websocket.mode == "online":
                        audio_in = b"".join(frames_asr_online)
                        try:
                            await async_asr_online(websocket, audio_in)
                        except Exception as e:
                            logger.error(f"error in asr streaming: {e}")
                    frames_asr_online = []
                
                if speech_start:
                    frames_asr.append(message)
                
                # VAD 检测
                try:
                    speech_start_i, speech_end_i = await async_vad(websocket, message)
                except Exception as e:
                    logger.error(f"error in vad: {e}")
                    speech_start_i, speech_end_i = -1, -1
                
                if speech_start_i != -1:
                    speech_start = True
                    beg_bias = (websocket.vad_pre_idx - speech_start_i) // duration_ms
                    frames_pre = frames[-beg_bias:]
                    frames_asr = []
                    frames_asr.extend(frames_pre)
                    logger.info(f"[loop] speech_start=True, beg_bias={beg_bias}, frames_asr={len(frames_asr)}")
                
                # 离线 ASR
                should_run_offline = speech_end_i != -1 or not websocket.is_speaking
                if should_run_offline:
                    logger.info(f"[loop] triggering offline_asr: speech_end={speech_end_i} is_speaking={websocket.is_speaking} frames_asr={len(frames_asr)}")
                    if websocket.mode == "2pass" or websocket.mode == "offline":
                        audio_in = b"".join(frames_asr)
                        try:
                            await async_asr(websocket, audio_in)
                        except Exception as e:
                            logger.error(f"error in asr offline: {e}")
                    
                    frames_asr = []
                    speech_start = False
                    frames_asr_online = []
                    websocket.status_dict_asr_online["cache"] = {}
                    
                    if not websocket.is_speaking:
                        websocket.vad_pre_idx = 0
                        frames = []
                        websocket.status_dict_vad["cache"] = {}
                        logger.info("[loop] reset all state (is_speaking=false)")
                    else:
                        frames = frames[-20:]
    
    except websockets.ConnectionClosed:
        logger.info(f"ConnectionClosed, users: {len(websocket_users)}")
        await ws_reset(websocket)
        websocket_users.discard(websocket)
    except websockets.InvalidState:
        logger.warning("InvalidState")
    except Exception as e:
        logger.error(f"Exception: {e}")


async def main():
    global model_asr, model_asr_streaming, model_vad, model_punc, inverse_normalizer
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10096)
    parser.add_argument("--certfile", type=str, default="")
    parser.add_argument("--keyfile", type=str, default="")
    parser.add_argument("--enable_itn", type=int, default=1)
    parser.add_argument("--itn_lang", type=str, default="zh")
    args = parser.parse_args()
    
    # 配置日志
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
    logger.add(log_dir / "wss_funasr_compatible.log", level="INFO", rotation="20 MB", retention="7 days", encoding="utf-8")
    
    # 使用 nevoice 的 ModelLoader 加载模型
    logger.info("Loading models using nevoice ModelLoader...")
    loader = ModelLoader.current()
    bundle = loader.load()
    
    model_asr = bundle.model_asr
    model_asr_streaming = bundle.model_asr_online
    model_vad = bundle.model_vad
    model_punc = bundle.model_punc
    
    logger.info(f"Models loaded: asr={model_asr is not None}, online={model_asr_streaming is not None}, vad={model_vad is not None}, punc={model_punc is not None}")
    
    # 初始化 ITN
    if args.enable_itn and InverseNormalizer is not None:
        try:
            cache_dir = os.path.join(os.path.dirname(__file__), "..", "itn_cache")
            os.makedirs(cache_dir, exist_ok=True)
            inverse_normalizer = InverseNormalizer(
                lang=args.itn_lang, cache_dir=cache_dir, overwrite_cache=False
            )
            logger.info(f"ITN enabled (lang={args.itn_lang})")
        except Exception as e:
            logger.warning(f"ITN disabled: {e}")
    
    logger.info("Model loaded! Ready to accept connections.")
    
    # SSL 配置
    ssl_ctx = None
    if args.certfile and args.keyfile:
        ssl_ctx = ssl_module.SSLContext(ssl_module.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(args.certfile, args.keyfile)
    
    # 注意：不要求 subprotocol，让浏览器可以直接连接
    # FunASR Demo 要求 subprotocols=["binary"]，但浏览器默认不发送
    async with websockets.serve(
        ws_serve, 
        args.host, 
        args.port, 
        ping_interval=None, 
        ssl=ssl_ctx
    ):
        logger.info(f"Server started on {args.host}:{args.port} (ssl={'on' if ssl_ctx else 'off'})")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

