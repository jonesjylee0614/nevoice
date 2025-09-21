"""Basic health and placeholder endpoints."""

from __future__ import annotations

import io
import json
import os
import tempfile
import time
import uuid

import soundfile as sf
import torch
from flask import Blueprint, request
from loguru import logger
from pydub import AudioSegment

from es.voice import search_voice_vector
from pipeline.spk_v_pipeline import embedding
from rest_prints import NumpyEncoder
from speech_recognition.spk import reload_spk_pipeline
from speech_recognition.test_recognize import reinst_test_model, test_recognize
from zh_correct.correct import correct


def create_model_blueprint() -> Blueprint:
    bp = Blueprint("model", __name__)

    @bp.route("/model/test_model", methods=["POST"])
    def test_model():
        # go后端调用 把训练好的模型文件放到speech_test下

        # 重新实例化测试模型，并测试音频识别效果
        reinst_test_model()

        if 'audio' not in request.files:
            return {'error': '没有接收到音频文件'}, 400

        audio_file = request.files['audio']
        save_path = ''

        try:
            # 直接读取音频数据到内存
            audio_data = audio_file.read()
            audio_stream = io.BytesIO(audio_data)

            # 使用soundfile直接读取音频数据
            try:
                # 首先尝试直接用soundfile读取
                audio_array, samplerate = sf.read(audio_stream)
            except:
                # 如果失败，使用pydub转换
                audio_stream.seek(0)  # 重置流位置
                audio = AudioSegment.from_file(audio_stream)
                wav_buffer = io.BytesIO()
                audio.export(wav_buffer, format="wav")
                wav_buffer.seek(0)
                audio_array, samplerate = sf.read(wav_buffer)

            # 保存处理后的音频到文件
            if audio_file:
                tmpdir = tempfile.gettempdir()
                folder = os.path.join(tmpdir, 'evoice')
                if not os.path.exists(folder):
                    os.makedirs(folder)
                filename = f"{str(time.time() * 1000)}.{str(uuid.uuid4())}.{audio_file.filename}"
                save_path = os.path.join(folder, filename)
                sf.write(save_path, audio_array, samplerate)

            # 向量搜索
            eb = embedding(save_path)
            search_res = search_voice_vector(eb)

            # 语音识别
            txt = test_recognize(save_path)
            txt_res = txt[0]['text']
            # txt_res 最大允许250个字
            if len(txt_res) > 100:
                txt_res = txt_res[:100]

            # 这里可以添加其他音频处理逻辑
            data = {
                'data': search_res,
                'txt': correct(txt_res)['target']
            }
            return json.dumps(data, cls=NumpyEncoder), 200

        except Exception as e:
            torch.cuda.empty_cache()
            logger.error(f"错误详情: {str(e)}")
            return {'error': f'音频处理失败: {str(e)}'}, 500
        finally:
            os.remove(save_path)

    @bp.route("/model/adopt_model", methods=["POST"])
    def adopt_model():
        # go后端调用 把训练好的模型文件放到speech_train下

        # 重新实例化训练模型，以支持正式使用
        reload_spk_pipeline()

        return {'data': 'success'}

    return bp
