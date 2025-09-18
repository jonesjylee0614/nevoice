from io import BytesIO

import numpy as np
from modelscope import pipeline, Tasks
from pydub import AudioSegment

# 实时根据麦克风识别语音转文字

# 初始化模型
sample_offset = 0
chunk_size = [0, 10, 5]  # [5, 10, 5] 600ms, [8, 8, 4] 480ms
encoder_chunk_look_back = 4
decoder_chunk_look_back = 1
stride_size = chunk_size[1] * 960

inference_pipeline = pipeline(
    task=Tasks.auto_speech_recognition,
    model='iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online',
    model_revision='v2.0.5',
    disable_update=True
)


def streaming_recognize(audio, cache, is_final):
    res = inference_pipeline(audio,
                             cache=cache,
                             is_final=is_final,
                             encoder_chunk_look_back=encoder_chunk_look_back,
                             decoder_chunk_look_back=decoder_chunk_look_back,
                             disable_update=True
                             )
    return res


def binary_audio_to_16k_array(audio_bytes):
    """
    将二进制音频数据（bytes）转为 16kHz 单声道浮点数组
    支持格式：MP3, WAV, OGG, FLAC, WebM 等
    """
    # 从内存中读取音频
    audio = AudioSegment.from_file(BytesIO(audio_bytes))

    # 设置采样率为 16000
    audio = audio.set_frame_rate(16000)

    # 转为 numpy 数组
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)

    # 如果是立体声，转为单声道
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)

    # 归一化到 [-1.0, 1.0]
    if audio.sample_width == 2:
        samples = samples / 32768.0
    elif audio.sample_width == 4:
        samples = samples / 2147483648.0

    return samples
