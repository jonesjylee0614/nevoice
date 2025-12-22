from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

model_id = 'iic/speech_sambert-hifigan_tts_zh-cn_16k'
tts = pipeline(task=Tasks.text_to_speech, model=model_id)

#  zhitian_emo，zhiyan_emo，zhizhe_emo，zhibei_emo

# 少女
def zhitian_emo(text: str, out_path: str):
    output = tts(input=text, voice='zhitian_emo')
    wav = output[OutputKeys.OUTPUT_WAV]
    with open(out_path, 'wb') as f:
        f.write(wav)
# 小男孩
def zhiyan_emo(text: str, out_path: str):
    output = tts(input=text, voice='zhiyan_emo')
    wav = output[OutputKeys.OUTPUT_WAV]
    with open(out_path, 'wb') as f:
        f.write(wav)

# 大姐姐
def zhizhe_emo(text: str, out_path: str):
    output = tts(input=text, voice='zhizhe_emo')
    wav = output[OutputKeys.OUTPUT_WAV]
    with open(out_path, 'wb') as f:
        f.write(wav)

# 男人
def zhibei_emo(text: str, out_path: str):
    output = tts(input=text, voice='zhibei_emo')
    wav = output[OutputKeys.OUTPUT_WAV]
    with open(out_path, 'wb') as f:
        f.write(wav)

if __name__ == '__main__':
    zhibei_emo(text='今天天气不错', out_path='zhibei_emo.wav')