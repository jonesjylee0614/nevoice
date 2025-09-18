from pipeline.spk_v_pipeline import sv_pipeline

speaker1_a_wav = 'wavs/speaker1_a_cn_16k.wav'
speaker1_b_wav = 'wavs/speaker1_b_cn_16k.wav'
speaker2_a_wav = 'wavs/speaker2_a_cn_16k.wav'
# 相同说话人语音
# result = sv_pipeline([speaker1_a_wav, speaker1_b_wav])
# print(result)
# # 不同说话人语音
# result = sv_pipeline([speaker1_a_wav, speaker2_a_wav])
# print(result)
# # 可以自定义得分阈值来进行识别
result = sv_pipeline([speaker1_a_wav], output_emb=True)
print(result['embs'], result['outputs'])
# 可以传入output_emb参数，输出结果中就会包含提取到的说话人embedding
# result = sv_pipeline([speaker1_a_wav, speaker2_a_wav], output_emb=True)
# print(result['embs'], result['outputs'])
