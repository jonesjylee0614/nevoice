from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


model_id = 'damo/speech_sambert-hifigan_tts_zhitian_emo_zh-cn_16k'
zhitian_emo = pipeline(task=Tasks.text_to_speech, model=model_id)

def out(text: str, out_path: str):
    output = zhitian_emo(input=text)
    wav = output[OutputKeys.OUTPUT_WAV]
    with open(out_path, 'wb') as f:
        f.write(wav)

if __name__ == '__main__':
    out('今天是个好日子', 'output1.wav')
    # zhitian_emo 支持如下情感：neutral，happy，angry，sad，fear，hate，surprise
    hap = '<speak><emotion category="happy" intensity="1.0">今天是个好日子！</emotion></speak>'
    out(hap, 'output2.wav')

    hap = '<speak><emotion category="surprise" intensity="1.0">天呐，好壮观啊！</emotion></speak>'
    out(hap, 'output3.wav')

    hap = '<speak><emotion category="angry" intensity="1.0">我要杀了你，为我孩子报仇！</emotion></speak>'
    out(hap, 'output4.wav')