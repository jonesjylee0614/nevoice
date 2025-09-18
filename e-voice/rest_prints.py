import io
import json
import os
import tempfile
import time
import uuid

import numpy as np
import soundfile as sf
import torch
from flask import request, jsonify, Blueprint
from loguru import logger
from pydub import AudioSegment

from es.conn import delete_by_id
from es.voice import search_voice_vector, list_by_userid, index_name
from pipeline.spk_v_pipeline import embedding
from speech_recognition.recognize import recognize
from zh_correct.correct import correct

print_app = Blueprint('prints', __name__)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# 获取指定用户声纹列表
@print_app.route("/prints/get_user_prints", methods=['POST'])
def get_user_prints():
    req = request.get_json()
    userid = req['userid']
    page = req['page'] or 1
    limit = req['limit'] or 10

    res = list_by_userid(userid, page, limit)
    # 循环修改id为字符串
    for i in res['data']:
        i['id'] = str(i['id'])

    data = {
        'msg': '查询成功',
        'data': res['data'],
        'total': res['total'],
        "success": True
    }
    return json.dumps(data, cls=NumpyEncoder), 200


# 删除指定用户指定id的声纹
@print_app.route("/prints/del", methods=['POST'])
def del_user_prints():
    req = request.get_json()
    userid = int(req['userid'])
    doc_id = req['doc_id']
    res = delete_by_id(index_name, doc_id)
    data = {
        'msg': '删除成功',
        'code': 0,
        "success": True
    }
    return jsonify(data)


# 声纹鉴定 上传或录制音频,返回声纹鉴定结果及文字信息
@print_app.route("/prints/identify", methods=['POST'])
def identify():
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
        txt = recognize(save_path)
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
