from modelscope.pipelines import pipeline

# 说话人确认模型
sv_pipeline = pipeline(
    task='speaker-verification',
    model='iic/speech_campplus_sv_zh-cn_16k-common',
    model_revision='v2.0.2',
    disable_update=True
)


def embedding(wav_path):
    result = sv_pipeline([wav_path], output_emb=True)
    return result['embs'][0]


def embeddings(wav_paths):
    result = sv_pipeline(wav_paths, output_emb=True)
    return result['embs']


if __name__ == '__main__':
    eb = embedding("../resource/audio_data/0/014.wav", )
    print(eb)
