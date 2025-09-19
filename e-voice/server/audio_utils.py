"""Audio helpers shared by the REST endpoints and realtime sessions."""

from __future__ import annotations

import io
import json
import os
from typing import Any, Dict, Tuple

import numpy as np
import soundfile as sf
from pydub import AudioSegment

__all__ = [
    "init_audio_utils",
    "resolve_temp_dir",
    "NumpyEncoder",
    "extract_text_from_result",
    "audio_segment_to_array",
    "process_audio_file",
]

_voice_conf: Dict[str, Any] = {}


def init_audio_utils(conf: Dict[str, Any]) -> None:
    """Store the voice configuration so helper functions can reuse it."""
    global _voice_conf
    _voice_conf = conf or {}


def resolve_temp_dir() -> str:
    try:
        configured = _voice_conf.get("temp_path") if _voice_conf else None
    except Exception:  # pragma: no cover - defensive
        configured = None

    candidates = [configured, "data/temp", "data/voice/temp"]
    for path in candidates:
        if not path:
            continue
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except Exception:  # pragma: no cover - defensive
            continue

    fallback = "data/temp"
    try:
        os.makedirs(fallback, exist_ok=True)
    except Exception:  # pragma: no cover - defensive
        pass
    return fallback


class NumpyEncoder(json.JSONEncoder):
    """自定义JSON编码器，用于序列化NumPy数组和浮点数。"""

    def default(self, obj: Any) -> Any:  # type: ignore[override]
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def extract_text_from_result(res: Any) -> str:
    try:
        if res is None:
            return ""
        if isinstance(res, str):
            return res.strip()
        if isinstance(res, dict):
            return (
                res.get("text")
                or res.get("result")
                or res.get("transcription")
                or ""
            ).strip()
        if isinstance(res, (list, tuple)):
            for item in res:
                if isinstance(item, dict) and "text" in item:
                    return (item.get("text") or "").strip()
            return (str(res[0]) if res else "").strip()
    except Exception:  # pragma: no cover - defensive
        return ""


def audio_segment_to_array(audio: AudioSegment) -> Tuple[np.ndarray, int]:
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)
    data, samplerate = sf.read(buffer)
    return data, samplerate


def process_audio_file(audio_file) -> Tuple[np.ndarray, int]:
    try:
        audio_data = audio_file.read()
        audio_stream = io.BytesIO(audio_data)
        try:
            audio_array, samplerate = sf.read(audio_stream)
        except Exception:
            audio_stream.seek(0)
            audio = AudioSegment.from_file(audio_stream)
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            audio_array, samplerate = sf.read(wav_buffer)
        return audio_array, samplerate
    except Exception as exc:
        raise Exception(f"音频文件处理失败: {exc}") from exc
