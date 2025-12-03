import asyncio
import json
import websockets
import time
import logging
import tracemalloc
import numpy as np
import argparse
import ssl
import os
import sys
import re
try:
    import cn2an
except Exception:
    cn2an = None

# ITN (逆文本归一化) 使用 cn2an 实现
# cn2an 已在 requirements.txt 中


parser = argparse.ArgumentParser()
parser.add_argument(
    "--host", type=str, default="0.0.0.0", required=False, help="host ip, localhost, 0.0.0.0"
)
parser.add_argument("--port", type=int, default=10095, required=False, help="grpc server port")
parser.add_argument(
    "--asr_model",
    type=str,
    default="iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    help="model from modelscope",
)
parser.add_argument("--asr_model_revision", type=str, default="v2.0.4", help="")
parser.add_argument(
    "--asr_model_online",
    type=str,
    default="iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online",
    help="model from modelscope",
)
parser.add_argument("--asr_model_online_revision", type=str, default="v2.0.4", help="")
parser.add_argument(
    "--vad_model",
    type=str,
    default="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
    help="model from modelscope",
)
parser.add_argument("--vad_model_revision", type=str, default="v2.0.4", help="")
parser.add_argument(
    "--punc_model",
    type=str,
    default="iic/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727",
    help="model from modelscope",
)
parser.add_argument("--punc_model_revision", type=str, default="v2.0.4", help="")
parser.add_argument("--ngpu", type=int, default=1, help="0 for cpu, 1 for gpu")
parser.add_argument("--device", type=str, default="cuda", help="cuda, cpu")
parser.add_argument("--ncpu", type=int, default=4, help="cpu cores")
parser.add_argument(
    "--certfile",
    type=str,
    default="",  # 不强制证书，方便本地测试
    required=False,
    help="certfile for ssl",
)

parser.add_argument(
    "--keyfile",
    type=str,
    default="",  # 不强制证书，方便本地测试
    required=False,
    help="keyfile for ssl",
)
parser.add_argument(
    "--enable_itn", type=int, default=0, help="1 to enable inverse text normalization, 0 to disable"
)
parser.add_argument(
    "--itn_lang",
    type=str,
    default="zh",
    help="language for ITN (default zh)",
)
parser.add_argument(
    "--itn_cache_dir",
    type=str,
    default=None,
    help="cache directory for ITN grammars; defaults to ./itn_cache under this folder",
)
args = parser.parse_args()


websocket_users = set()

print("model loading")
from funasr import AutoModel

# asr
model_asr = AutoModel(
    model=args.asr_model,
    model_revision=args.asr_model_revision,
    ngpu=args.ngpu,
    ncpu=args.ncpu,
    device=args.device,
    disable_update=True,
    disable_pbar=True,
    disable_log=True,
)
# asr
model_asr_streaming = AutoModel(
    model=args.asr_model_online,
    model_revision=args.asr_model_online_revision,
    ngpu=args.ngpu,
    ncpu=args.ncpu,
    device=args.device,
    disable_update=True,
    disable_pbar=True,
    disable_log=True,
)
# vad
model_vad = AutoModel(
    model=args.vad_model,
    model_revision=args.vad_model_revision,
    ngpu=args.ngpu,
    ncpu=args.ncpu,
    device=args.device,
    disable_update=True,
    disable_pbar=True,
    disable_log=True,
    # chunk_size=60,
)

if args.punc_model != "":
    model_punc = AutoModel(
        model=args.punc_model,
        model_revision=args.punc_model_revision,
        ngpu=args.ngpu,
        ncpu=args.ncpu,
        device=args.device,
        disable_update=True,
        disable_pbar=True,
        disable_log=True,
    )
else:
    model_punc = None

inverse_normalizer = None
if args.enable_itn:
    try:
        from fun_text_processing.inverse_text_normalization.inverse_normalize import (
            InverseNormalizer,
        )

        cache_dir = (
            args.itn_cache_dir
            if args.itn_cache_dir is not None
            else os.path.join(os.path.dirname(__file__), "itn_cache")
        )
        os.makedirs(cache_dir, exist_ok=True)
        inverse_normalizer = InverseNormalizer(
            lang=args.itn_lang, cache_dir=cache_dir, overwrite_cache=False
        )
        print(f"ITN enabled (lang={args.itn_lang}, cache={cache_dir})")
    except Exception as e:
        print(f"ITN disabled, failed to initialize: {e}")


def postprocess_numbers(text: str) -> str:
    """Convert Chinese numerals to digits; keeps original text on failure."""
    if not text or cn2an is None:
        return text

    def _fmt(val):
        try:
            # remove trailing .0 for ints
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
            # only numbers without 万亿兆 inside will reach here
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
    # X(万|亿|兆) where X 不含万亿兆，输出保留单位（如 三点五万 -> 3.5万）
    text = re.sub(r"([〇零一二两三四五六七八九十百千零点两]+)([万亿兆])", _conv_with_unit, text)
    # 其他纯中文数字
    text = re.sub(r"[〇零一二两三四五六七八九十百千万亿兆点]+", _conv_plain, text)
    return text


def apply_itn(text: str) -> str:
    if not text:
        return text
    if inverse_normalizer is None:
        return postprocess_numbers(text)
    try:
        normalized = inverse_normalizer.inverse_normalize_list([text], verbose=False)[0]
        return postprocess_numbers(normalized)
    except Exception as e:
        print(f"ITN error, fallback to raw text: {e}")
        return postprocess_numbers(text)

print("model loaded! only support one client at the same time now!!!!")


async def ws_reset(websocket):
    print("ws reset now, total num is ", len(websocket_users))

    websocket.status_dict_asr_online["cache"] = {}
    websocket.status_dict_asr_online["is_final"] = True
    websocket.status_dict_vad["cache"] = {}
    websocket.status_dict_vad["is_final"] = True
    websocket.status_dict_punc["cache"] = {}

    await websocket.close()


async def clear_websocket():
    for websocket in websocket_users:
        await ws_reset(websocket)
    websocket_users.clear()


async def ws_serve(websocket, path=None):
    frames = []
    frames_asr = []
    frames_asr_online = []
    global websocket_users
    # await clear_websocket()
    websocket_users.add(websocket)
    websocket.status_dict_asr = {"itn": True}
    websocket.status_dict_asr_online = {"cache": {}, "is_final": False, "itn": True}
    websocket.status_dict_vad = {"cache": {}, "is_final": False}
    websocket.status_dict_punc = {"cache": {}}
    websocket.chunk_interval = 10
    websocket.vad_pre_idx = 0
    websocket.is_speaking = True
    speech_start = False
    speech_end_i = -1
    websocket.wav_name = "microphone"
    websocket.mode = "2pass"
    # 默认 chunk_size，避免未配置时访问报错
    websocket.status_dict_asr_online.setdefault("chunk_size", [5, 10, 5])
    websocket.status_dict_asr_online.setdefault("encoder_chunk_look_back", 5)
    websocket.status_dict_asr_online.setdefault("decoder_chunk_look_back", 5)
    print("new user connected", flush=True)

    try:
        async for message in websocket:
            if isinstance(message, str):
                messagejson = json.loads(message)

                if "is_speaking" in messagejson:
                    websocket.is_speaking = messagejson["is_speaking"]
                    websocket.status_dict_asr_online["is_final"] = not websocket.is_speaking
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
                    websocket.status_dict_asr_online["encoder_chunk_look_back"] = messagejson[
                        "encoder_chunk_look_back"
                    ]
                if "decoder_chunk_look_back" in messagejson:
                    websocket.status_dict_asr_online["decoder_chunk_look_back"] = messagejson[
                        "decoder_chunk_look_back"
                    ]
                if "hotwords" in messagejson:
                    websocket.status_dict_asr["hotword"] = messagejson["hotwords"]
                if "itn" in messagejson:
                    websocket.status_dict_asr["itn"] = messagejson["itn"]
                    websocket.status_dict_asr_online["itn"] = messagejson["itn"]
                if "mode" in messagejson:
                    websocket.mode = messagejson["mode"]

            websocket.status_dict_vad["chunk_size"] = int(
                websocket.status_dict_asr_online["chunk_size"][1] * 60 / websocket.chunk_interval
            )
            if len(frames_asr_online) > 0 or len(frames_asr) >= 0 or not isinstance(message, str):
                if not isinstance(message, str):
                    frames.append(message)
                    duration_ms = len(message) // 32
                    websocket.vad_pre_idx += duration_ms

                    # asr online
                    frames_asr_online.append(message)
                    websocket.status_dict_asr_online["is_final"] = speech_end_i != -1
                    if (
                        len(frames_asr_online) % websocket.chunk_interval == 0
                        or websocket.status_dict_asr_online["is_final"]
                    ):
                        if websocket.mode == "2pass" or websocket.mode == "online":
                            audio_in = b"".join(frames_asr_online)
                            try:
                                await async_asr_online(websocket, audio_in)
                            except:
                                print(f"error in asr streaming, {websocket.status_dict_asr_online}")
                        frames_asr_online = []
                    if speech_start:
                        frames_asr.append(message)
                    # vad online
                    try:
                        speech_start_i, speech_end_i = await async_vad(websocket, message)
                    except:
                        print("error in vad")
                    if speech_start_i != -1:
                        speech_start = True
                        beg_bias = (websocket.vad_pre_idx - speech_start_i) // duration_ms
                        frames_pre = frames[-beg_bias:]
                        frames_asr = []
                        frames_asr.extend(frames_pre)
                # asr punc offline
                if speech_end_i != -1 or not websocket.is_speaking:
                    # print("vad end point")
                    if websocket.mode == "2pass" or websocket.mode == "offline":
                        audio_in = b"".join(frames_asr)
                        try:
                            await async_asr(websocket, audio_in)
                        except:
                            print("error in asr offline")
                    frames_asr = []
                    speech_start = False
                    frames_asr_online = []
                    websocket.status_dict_asr_online["cache"] = {}
                    if not websocket.is_speaking:
                        websocket.vad_pre_idx = 0
                        frames = []
                        websocket.status_dict_vad["cache"] = {}
                    else:
                        frames = frames[-20:]

    except websockets.ConnectionClosed:
        print("ConnectionClosed...", websocket_users, flush=True)
        await ws_reset(websocket)
        websocket_users.remove(websocket)
    except websockets.InvalidState:
        print("InvalidState...")
    except Exception as e:
        print("Exception:", e)


async def async_vad(websocket, audio_in):

    segments_result = model_vad.generate(input=audio_in, **websocket.status_dict_vad)[0]["value"]
    # print(segments_result)

    speech_start = -1
    speech_end = -1

    if len(segments_result) == 0 or len(segments_result) > 1:
        return speech_start, speech_end
    if segments_result[0][0] != -1:
        speech_start = segments_result[0][0]
    if segments_result[0][1] != -1:
        speech_end = segments_result[0][1]
    return speech_start, speech_end


async def async_asr(websocket, audio_in):
    if len(audio_in) > 0:
        # print(len(audio_in))
        rec_result = model_asr.generate(input=audio_in, **websocket.status_dict_asr)[0]
        # print("offline_asr, ", rec_result)
        if model_punc is not None and len(rec_result["text"]) > 0:
            # print("offline, before punc", rec_result, "cache", websocket.status_dict_punc)
            rec_result = model_punc.generate(
                input=rec_result["text"], **websocket.status_dict_punc
            )[0]
        if len(rec_result["text"]) > 0:
            rec_result["text"] = apply_itn(rec_result["text"])
            # print("offline, after punc", rec_result)
        if len(rec_result["text"]) > 0:
            # print("offline", rec_result)
            mode = "2pass-offline" if "2pass" in websocket.mode else websocket.mode
            message = json.dumps(
                {
                    "mode": mode,
                    "text": rec_result["text"],
                    "wav_name": websocket.wav_name,
                    "is_final": websocket.is_speaking,
                }
            )
            await websocket.send(message)

    else:
        mode = "2pass-offline" if "2pass" in websocket.mode else websocket.mode
        message = json.dumps(
            {
                "mode": mode,
                "text": "",
                "wav_name": websocket.wav_name,
                "is_final": websocket.is_speaking,
            }
        )
        await websocket.send(message)    

async def async_asr_online(websocket, audio_in):
    if len(audio_in) > 0:
        # print(websocket.status_dict_asr_online.get("is_final", False))
        rec_result = model_asr_streaming.generate(
            input=audio_in, **websocket.status_dict_asr_online
        )[0]
        # print("online, ", rec_result)
        if websocket.mode == "2pass" and websocket.status_dict_asr_online.get("is_final", False):
            return
            #     websocket.status_dict_asr_online["cache"] = dict()
        if len(rec_result["text"]):
            if websocket.status_dict_asr_online.get("is_final", False):
                rec_result["text"] = apply_itn(rec_result["text"])
            mode = "2pass-online" if "2pass" in websocket.mode else websocket.mode
            message = json.dumps(
                {
                    "mode": mode,
                    "text": rec_result["text"],
                    "wav_name": websocket.wav_name,
                    "is_final": websocket.is_speaking,
                }
            )
            await websocket.send(message)


async def _main():
    if len(args.certfile) > 0:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_cert = args.certfile
        ssl_key = args.keyfile
        ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)
        start_server = websockets.serve(
            ws_serve, args.host, args.port, ping_interval=None, ssl=ssl_context
        )
    else:
        start_server = websockets.serve(
            ws_serve, args.host, args.port, ping_interval=None
        )
    server = await start_server
    print(f"funasr_native ws server started on {args.host}:{args.port} ssl={'on' if len(args.certfile)>0 else 'off'}")
    print(f"supported paths: / (use default) , /ws/recognize")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(_main())
