"""Voice related REST endpoints."""

from __future__ import annotations

import base64
import json
import os
import time
import traceback
import uuid
from typing import Dict

import numpy as np
import soundfile as sf
import torch
from flask import Blueprint, jsonify, request
from numba import int64

from es.voice import insert_voice
from pipeline.spk_v_pipeline import embedding
from speech_recognition.recognize import recognize

from ..audio_utils import NumpyEncoder, extract_text_from_result, process_audio_file, resolve_temp_dir


def create_voice_blueprint(voice_conf: Dict[str, object]) -> Blueprint:
    bp = Blueprint("voice", __name__)

    @bp.route("/voice-register", methods=["POST"])
    def handle_audio_stream():
        if "audio" not in request.files:
            return {"error": "没有接收到音频文件"}, 400

        username = request.form.get("username")
        userid = request.form.get("userid")

        if not username or not userid:
            return {"error": "用户名和用户ID不能为空"}, 400

        userid_int = int(userid)
        audio_file = request.files["audio"]

        try:
            audio_array, samplerate = process_audio_file(audio_file)

            folder = f"{voice_conf['print_wav_path']}/{userid_int}"
            if not os.path.exists(folder):
                os.makedirs(folder)

            filename = f"{int(time.time() * 1000)}.{uuid.uuid4()}.{audio_file.filename}"
            wav_file_path = f"{voice_conf['print_wav_path']}/{userid_int}/{filename}"
            sf.write(wav_file_path, audio_array, samplerate)
            print(f"音频已保存到 {wav_file_path}")

            txt = recognize(wav_file_path)
            txt_res = extract_text_from_result(txt)
            if len(txt_res) > 100:
                txt_res = txt_res[:100]

            insert_voice(
                username,
                userid_int,
                filename,
                txt_res,
                int64(time.time() * 1000),
                embedding(wav_file_path),
            )

            data = {
                "duration": len(audio_array) / samplerate,
                "sample_rate": samplerate,
                "txt": txt_res,
            }
            return json.dumps(data, cls=NumpyEncoder), 200

        except Exception as exc:
            torch.cuda.empty_cache()
            print(f"语音注册错误详情: {traceback.format_exc()}")
            return {"error": f"音频处理失败: {exc}"}, 500

    @bp.route("/voice-recognize-offline", methods=["POST"])
    def voice_recognize_offline():
        if "audio" not in request.files:
            return {"error": "没有接收到音频文件"}, 400

        audio_file = request.files["audio"]
        language = request.form.get("language", "zh-cn")

        try:
            audio_array, samplerate = process_audio_file(audio_file)
            temp_folder = resolve_temp_dir()
            temp_filename = f"temp_{int(time.time() * 1000)}.{uuid.uuid4()}.wav"
            temp_file_path = f"{temp_folder}/{temp_filename}"
            sf.write(temp_file_path, np.clip(audio_array, -1.0, 1.0), samplerate, subtype="PCM_16")

            try:
                recognition_result = recognize(temp_file_path)
                recognized_text = extract_text_from_result(recognition_result)
                confidence = None

                result = {
                    "text": recognized_text,
                    "duration": len(audio_array) / samplerate,
                    "sample_rate": samplerate,
                    "language": language,
                }
                if confidence is not None:
                    result["confidence"] = confidence

                return jsonify(result), 200
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        except Exception as exc:
            torch.cuda.empty_cache()
            print(f"离线语音识别错误详情: {traceback.format_exc()}")
            return {"error": f"语音识别失败: {exc}"}, 500

    @bp.route("/voice-recognize-online", methods=["POST"])
    def voice_recognize_online():
        try:
            data = request.get_json()
            if not data or "audio_data" not in data:
                return {"error": "缺少音频数据"}, 400

            audio_data = data["audio_data"]
            audio_format = data.get("format", "wav")
            sample_rate = data.get("sample_rate", 16000)

            try:
                audio_bytes = base64.b64decode(audio_data)
            except Exception as exc:
                return {"error": f"音频数据解码失败: {exc}"}, 400

            temp_folder = resolve_temp_dir()
            temp_filename = f"online_{int(time.time() * 1000)}.{uuid.uuid4()}.{audio_format}"
            temp_file_path = f"{temp_folder}/{temp_filename}"

            with open(temp_file_path, "wb") as f:
                f.write(audio_bytes)

            try:
                recognition_result = recognize(temp_file_path)
                recognized_text = extract_text_from_result(recognition_result)

                result = {
                    "text": recognized_text,
                    "is_final": True,
                    "timestamp": int(time.time() * 1000),
                    "format": audio_format,
                    "sample_rate": sample_rate,
                }
                return jsonify(result), 200
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        except Exception as exc:
            torch.cuda.empty_cache()
            print(f"在线语音识别错误详情: {traceback.format_exc()}")
            return {"error": f"在线语音识别失败: {exc}"}, 500

    return bp
