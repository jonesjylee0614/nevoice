from funasr import AutoModel

model = AutoModel(model="paraformer-zh-streaming",disable_update=True)

cache = {}
chunk_size = [0, 10, 5]  # [0, 10, 5] 600ms
encoder_chunk_look_back = 4
decoder_chunk_look_back = 1


def recognize(audio):
    res = model.generate(
        input=audio,
        cache=cache,
        is_final=False,
        chunk_size=chunk_size,
        encoder_chunk_look_back=encoder_chunk_look_back,
        decoder_chunk_look_back=decoder_chunk_look_back
    )

    # 输出识别结果
    if res and res[0]["text"].strip():
        return res[0]["text"]

    return ""
