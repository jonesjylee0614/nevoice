from funasr import AutoModel
from modelscope import snapshot_download

from config.config import conf

cache_dir = conf.get('model', 'cache_dir', fallback='')

model_dir = snapshot_download(
    model_id='iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
    local_dir=f'{cache_dir}/speech_train'
)


def load_spk_model():
    """加载或重新加载spk_pipeline模型"""
    global spk_pipeline
    spk_pipeline = AutoModel(
        model=model_dir,
        model_revision="v2.0.5",
        vad_model="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
        vad_model_revision="v2.0.4",
        punc_model="iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
        punc_model_revision="v2.0.4",
        spk_model="iic/speech_campplus_sv_zh-cn_16k-common",
        spk_model_revision="v2.0.2",
        disable_update=True,
    )
    return spk_pipeline


def reload_spk_pipeline():
    """重新加载spk_pipeline模型实例"""
    global spk_pipeline
    import gc
    import torch

    # 删除旧实例
    if spk_pipeline is not None:
        del spk_pipeline

    # 清理内存
    torch.cuda.empty_cache()
    gc.collect()

    # 重新加载
    return load_spk_model()


# 初始加载
spk_pipeline = load_spk_model()

if __name__ == '__main__':
    print(spk_pipeline.generate("../resource/1分20.wav"))
