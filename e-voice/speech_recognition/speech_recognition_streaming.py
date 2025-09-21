import numpy as np
import pyaudio
from modelscope import pipeline, Tasks, snapshot_download

from config.config import conf

# 实时根据麦克风识别语音转文字

# 初始化模型
chunk_size = [0, 10, 5]  # [0, 10, 5] 600ms, [0, 8, 4] 480ms
encoder_chunk_look_back = 4  # number of chunks to lookback for encoder self-attention
decoder_chunk_look_back = 1  # number of encoder chunks to lookback for decoder cross-attention

cache_dir = conf.get('model', 'cache_dir', fallback='')

model_dir = snapshot_download(
    model_id='iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online',
    local_dir=f'{cache_dir}/speech_stream'
)

model = pipeline(
    task=Tasks.auto_speech_recognition,
    model=model_dir,
    disable_update=True)

# 设置音频参数
CHUNK = 960 * 10  # 与模型的 chunk_size 对应
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000  # FunASR 模型需要 16kHz 采样率

# 初始化 PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("开始录音，按 Ctrl+C 停止...")

arr = []

try:
    cache = {}
    while True:
        # 读取音频数据
        audio_data = stream.read(CHUNK)
        # 将字节数据转换为 numpy 数组
        audio_array = np.frombuffer(audio_data, dtype=np.float32)

        # 进行语音识别
        res = model(
            input=audio_array,
            cache=cache,
            is_final=False,
            chunk_size=chunk_size,
            encoder_chunk_look_back=encoder_chunk_look_back,
            decoder_chunk_look_back=decoder_chunk_look_back
        )

        # 进行语音识别
        # res = recognize(audio_array)

        # 如果有识别结果则打印
        if res and res[0]["text"].strip():
            arr.append(res[0]["text"])
            print(res[0]["text"])


except KeyboardInterrupt:
    print("\n停止录音")
    print("".join(arr))
finally:
    # 清理资源
    stream.stop_stream()
    stream.close()
    p.terminate()
