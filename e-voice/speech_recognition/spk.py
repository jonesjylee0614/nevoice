from funasr import AutoModel

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

spk_pipeline = AutoModel(
    model="iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    vad_model="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
    punc_model="iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
    spk_model="iic/speech_campplus_sv_zh-cn_16k-common",
    disable_update=True,
)


if __name__ == "__main__":
    rec_result = spk_pipeline.generate("../resource/asr_speaker_demo.wav")
    print(rec_result)
