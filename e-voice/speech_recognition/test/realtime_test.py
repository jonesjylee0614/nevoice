import logging
from pathlib import Path

import librosa
import pytest

pytest.importorskip("funasr")

from funasr import AutoModel
from modelscope.utils.logger import get_logger

logger = get_logger(log_level=logging.CRITICAL)
logger.setLevel(logging.CRITICAL)

model = AutoModel(model="paraformer-zh-streaming", disable_update=True)

audio_path = Path(__file__).resolve().parents[2] / "resource" / "asr_speaker_demo.wav"
if not audio_path.exists():
    pytest.skip("缺少实时识别示例音频，跳过集成测试", allow_module_level=True)

# 以16000Hz的采样率读取文件
speech, sample_rate = librosa.load(audio_path, sr=16000)

# 将字节数据转换为 numpy 数组
# speech = np.frombuffer(speech, dtype=np.float16)

speech_length = speech.shape[0]

sample_offset = 0
chunk_size = [0, 10, 5]  # [5, 10, 5] 600ms, [8, 8, 4] 480ms
encoder_chunk_look_back = 4
decoder_chunk_look_back = 1
stride_size = chunk_size[1] * 960

cache = {}
is_final = False
for sample_offset in range(0, speech_length, min(stride_size, speech_length - sample_offset)):
    if sample_offset + stride_size >= speech_length - 1:
        stride_size = speech_length - sample_offset
        is_final = True

    res = model.generate(input=speech[sample_offset: sample_offset + stride_size],
                         cache=cache,
                         is_final=is_final,
                         chunk_size=chunk_size,
                         encoder_chunk_look_back=encoder_chunk_look_back,
                         decoder_chunk_look_back=decoder_chunk_look_back)
    print(res)
