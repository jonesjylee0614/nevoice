"""Socket.IO event registration."""

from __future__ import annotations

import io

from flask import request
from flask_socketio import SocketIO, emit
from pydub import AudioSegment

from ..audio_utils import audio_segment_to_array, extract_text_from_result
from ..logging import logger
from ..monitoring import record_connection
from speech_recognition.recognize import recognize


def register_socketio_events(socketio: SocketIO) -> None:
    @socketio.on("connect")
    def handle_connect():
        print("Client connected")
        record_connection(True)
        logger.info(f"WebSocket连接: {request.sid}")

    @socketio.on("audio_chunk")
    def handle_audio_chunk(data):
        if not data or len(data) < 100:
            emit("transcription", {"msg": "音频数据不完整或为空", "code": -1})
            return

        try:
            audio = AudioSegment.from_file(io.BytesIO(data), format="webm")
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export("./test.wav", format="wav", parameters=["-acodec", "pcm_s16le"])
            audio_data, _ = audio_segment_to_array(audio)

            txt = recognize("./test.wav")
            emit("transcription", {"text": extract_text_from_result(txt), "code": 0})
        except Exception as exc:
            print(f"[ERROR] WebM 解析失败: {exc}")
            emit("transcription", {"msg": f"[ERROR] WebM 解析失败: {exc}", "code": -400})
