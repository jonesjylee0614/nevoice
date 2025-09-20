from funasr import AutoModel
from config.config import conf
import os

# 分角色语音识别

# output_dir = "../results"
# spk_pipeline = pipeline(
#     task=Tasks.auto_speech_recognition,
#     model='/home/leozy/.cache/modelscope/hub/iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch', model_revision='v2.0.4',
#     vad_model='iic/speech_fsmn_vad_zh-cn-16k-common-pytorch', vad_model_revision="v2.0.4",
#     punc_model='iic/punc_ct-transformer_cn-en-common-vocab471067-large', punc_model_revision="v2.0.4",
#     disable_update=True,
#     spk_model="iic/speech_campplus_sv_zh-cn_16k-common", spk_model_version="v2.0.2"
#     # output_dir=output_dir,
# )

model_conf = conf['model']

# 仅使用本地模型路径，避免任何联网下载
asr_model_path = model_conf.get('speech_paraformer')
spk_model_path = model_conf.get('speech_campplus')

if not asr_model_path or not os.path.exists(asr_model_path):
    raise RuntimeError(f"ASR 本地模型未配置或不存在: {asr_model_path}")
if not spk_model_path or not os.path.exists(spk_model_path):
    raise RuntimeError(f"说话人本地模型未配置或不存在: {spk_model_path}")

spk_pipeline = AutoModel(
    model=asr_model_path,
    # 不传独立的 VAD 与 PUNC 模型，使用 paraformer-vad-punc 集成模型能力
    spk_model=spk_model_path,
    disable_update=True,
)


if __name__ == "__main__":
    rec_result = spk_pipeline.generate("../resource/asr_speaker_demo.wav")
    print(rec_result)
