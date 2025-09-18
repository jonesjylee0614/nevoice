import io
import json
import os
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import soundfile as sf
import torch
from flask import Blueprint, request
from loguru import logger
from pydub import AudioSegment

from biz.meeting.parse_offline_meeting import process_audio_task
from config.config import conf


class SafeThreadPoolExecutor(ThreadPoolExecutor):
    """安全的线程池执行器"""

    def submit(self, fn, *args, **kwargs):
        """提交任务时包装异常处理"""

        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logger.error(f"线程任务执行异常: {str(e)}")
                logger.error(traceback.format_exc())
                raise

        return super().submit(wrapper, *args, **kwargs)


# 创建全局线程池
executor = SafeThreadPoolExecutor(max_workers=4)

meeting_app = Blueprint('meeting', __name__)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


meeting_conf = conf['meeting']


# 会议纪要 上传音频，返回识别结果、发言人、及文字信息
@meeting_app.route("/meeting/offline", methods=['POST'])
def meeting_offline():
    if 'audio' not in request.files:
        return {'error': '没有接收到音频文件'}, 400

    audio_file = request.files['audio']
    meeting_id = request.form.get('meetingId')

    # 获取form表单其他参数
    meetinginfo = {
        'meetingId': meeting_id,
        'meetingTime': request.form.get('meetingTime'),  # 格式 2023-05-05 09:05:05
    }
    opuser = {
        'username': request.form.get('username'),
        'userid': request.form.get('userid')
    }

    save_path = ''
    filename = ''
    try:
        # 直接读取音频数据到内存
        audio_data = audio_file.read()
        audio_stream = io.BytesIO(audio_data)

        try:
            # 首先尝试使用soundfile直接读取音频数据
            audio_array, samplerate = sf.read(audio_stream)
        except Exception as e:
            logger.warning(f"读取音频数据异常: {str(e)}")
            # 如果失败，使用pydub转换
            audio_stream.seek(0)  # 重置流位置
            audio = AudioSegment.from_file(audio_stream)
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            audio_array, samplerate = sf.read(wav_buffer)

        # 保存处理后的音频到文件
        if audio_file:
            # 保存处理后的音频到文件 - 使用相对路径避免权限问题
            folder = f"{meeting_conf['offline_wav_path']}/{meeting_id}"
            if not os.path.exists(folder):
                os.makedirs(folder)

            filename = f"{str(time.time() * 1000)}.{str(uuid.uuid4())}.{audio_file.filename}"
            save_path = f"{folder}/{filename}"
            sf.write(save_path, audio_array, samplerate)

        # 提交异步任务处理批量说话人确认+语音转文字
        future = executor.submit(process_audio_task, save_path, meetinginfo, opuser)
        # 记录任务ID，可用于后续查询任务状态
        task_id = id(future)

        # 这里可以添加其他音频处理逻辑
        data = {
            'msg': '添加任务成功',
            'audio_name': filename,
            'data': {
                'task_id': task_id,
            },
            'code': 0,
            "success": True
        }
        return json.dumps(data, cls=NumpyEncoder), 200

    except Exception as e:
        torch.cuda.empty_cache()
        logger.error(f"错误详情: {str(e)}")
        return {'error': f'音频处理失败: {str(e)}'}, 500

# 增(python)删改查(go)离线会议接口
