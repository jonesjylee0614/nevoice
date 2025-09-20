from modelscope import pipeline

from config.config import conf

# 设置环境变

model_conf = conf['model']
# 说话人确认模型
sv_pipeline = pipeline(
    task='speaker-verification',
    model=model_conf['speech_campplus'],
    disable_update=True,
    local_files_only=True
)


def embedding(wav_path):
    result = sv_pipeline([wav_path], output_emb=True)
    return result['embs'][0]


def embeddings(wav_paths):
    result = sv_pipeline(wav_paths, output_emb=True)
    return result['embs']
