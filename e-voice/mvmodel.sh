rm -rf ~/.cache/model/speech_campplus
rm -rf ~/.cache/model/speech_train
rm -rf ~/.cache/model/speech_test

mkdir -p ~/.cache/model/speech_campplus
mkdir -p ~/.cache/model/speech_train
mkdir -p ~/.cache/model/speech_test

cp -r ~/.cache/modelscope/hub/iic/speech_campplus_sv_zh-cn_16k-common/. ~/.cache/model/speech_campplus
cp -r ~/.cache/modelscope/hub/iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch/. ~/.cache/model/speech_train
cp -r ~/.cache/modelscope/hub/iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch/. ~/.cache/model/speech_test
