from modelscope import snapshot_download

# 实时根据麦克风识别语音转文字

# 初始化模型
chunk_size = [0, 10, 5]  # [0, 10, 5] 600ms, [0, 8, 4] 480ms
encoder_chunk_look_back = 4  # number of chunks to lookback for encoder self-attention
decoder_chunk_look_back = 1  # number of encoder chunks to lookback for decoder cross-attention

model_dir = snapshot_download(
    model_id='iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online',
    local_dir='/home/zrway/.cache/model/speech_stream'
)

print(model_dir)
