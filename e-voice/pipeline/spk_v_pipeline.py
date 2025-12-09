from modelscope import pipeline
from loguru import logger

from config.config import conf

# 直接使用配置文件中的声纹模型路径，不再通过 snapshot_download 下载
model_dir = conf.get('model', 'speech_campplus', fallback='')
logger.info(f"📁 声纹模型路径: {model_dir}")

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
