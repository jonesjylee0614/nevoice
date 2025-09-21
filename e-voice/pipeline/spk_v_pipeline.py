from modelscope import snapshot_download, pipeline

from config.config import conf

cache_dir = conf.get('model', 'cache_dir', fallback='')

model_dir = snapshot_download(
    model_id='iic/speech_campplus_sv_zh-cn_16k-common',
    local_dir=f'{cache_dir}/speech_campplus'
)

# 说话人确认模型
sv_pipeline = pipeline(
    task='speaker-verification',
    model=model_dir,
    disable_update=True,
    local_files_only=True
)


def embedding(wav_path):
    result = sv_pipeline([wav_path], output_emb=True)
    return result['embs'][0]


def embeddings(wav_paths):
    result = sv_pipeline(wav_paths, output_emb=True)
    return result['embs']


if __name__ == '__main__':
    print(embedding('../resource/audio_data/0/014.wav'))
    print(embeddings(['../resource/audio_data/0/014.wav', '../resource/audio_data/0/015.wav']))
