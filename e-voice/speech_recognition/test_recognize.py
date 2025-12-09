import os
import time

import torch
from loguru import logger
from modelscope import pipeline, Tasks

from config.config import conf

# 创建专用的语音识别日志
rec_logger = logger.bind(component="speech_recognition")

speech_paraformer_test = None

# 直接使用配置文件中的模型路径，不再通过 snapshot_download 下载
test_model_dir = conf.get('model', 'speech_test', fallback='')
rec_logger.info(f"📁 测试模型路径: {test_model_dir}")


# 🔧 临时修复：使用最简单的配置
def reinst_test_model():
    try:
        global speech_paraformer_test
        speech_paraformer_test = pipeline(
            task=Tasks.auto_speech_recognition,
            model=test_model_dir,
            disable_update=True,
            local_files_only=True,
        )
        rec_logger.success("✅ 使用最简单的ModelScope配置")
    except Exception as e:
        rec_logger.error(f"❌ ModelScope初始化失败: {e}")
        speech_paraformer_test = None


def test_recognize(audio):
    """
    临时修复版本的语音识别函数
    """
    if not speech_paraformer_test:
        reinst_test_model()

    start_time = time.time()

    # 检查音频输入
    if isinstance(audio, str):
        if os.path.exists(audio):
            file_size = os.path.getsize(audio)
            rec_logger.warning(f"🔍 [临时识别] 音频文件: {audio}, 大小: {file_size} bytes")
        else:
            rec_logger.error(f"❌ [临时识别] 音频文件不存在: {audio}")
            return ""

    try:

        # 尝试使用ModelScope识别
        rec_logger.warning(f"🔍 [临时识别] 开始ModelScope识别: {audio}")
        res = speech_paraformer_test(audio)
        processing_time = (time.time() - start_time) * 1000

        # 详细分析结果
        rec_logger.warning(f"🔍 [临时识别] 原始结果: {res}")
        rec_logger.warning(f"🔍 [临时识别] 结果类型: {type(res)}")

        # 提取文本
        text_result = ""
        if res is None:
            rec_logger.warning("⚠️ [临时识别] ModelScope返回None")
        elif isinstance(res, str):
            text_result = res
        elif isinstance(res, dict):
            rec_logger.warning(f"🔍 [临时识别] 字典键: {list(res.keys())}")
            # 尝试多种可能的键
            for key in ['text', 'result', 'transcript', 'content', 'output']:
                if key in res and res[key]:
                    text_result = res[key]
                    rec_logger.warning(f"🔍 [临时识别] 从'{key}'提取: '{text_result}'")
                    break

            # 如果还是没找到，检查所有值
            if not text_result:
                for key, value in res.items():
                    rec_logger.warning(f"🔍 [临时识别] 键'{key}': {value} (类型: {type(value)})")
                    if isinstance(value, str) and value.strip():
                        text_result = value
                        break

        elif isinstance(res, (list, tuple)) and res:
            rec_logger.warning(f"🔍 [临时识别] 列表长度: {len(res)}")
            if isinstance(res[0], dict):
                for key in ['text', 'result', 'transcript']:
                    if key in res[0] and res[0][key]:
                        text_result = res[0][key]
                        break
            elif isinstance(res[0], str):
                text_result = res[0]

        # 最终结果处理
        if text_result and text_result.strip():
            rec_logger.success(f"✅ [临时识别] 成功: '{text_result}' (处理时间: {processing_time:.1f}ms)")
            return [{"text": text_result}]
        else:
            # 🔧 修复：ModelScope返回空时，返回空结果而非模板内容
            rec_logger.warning("⚠️ [临时识别] ModelScope返回空，返回空结果")
            rec_logger.success(f"✅ [临时识别] 返回空结果 (处理时间: {processing_time:.1f}ms)")
            return [{"text": ""}]  # 返回空字符串而不是固定模板

    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        rec_logger.error(f"❌ [临时识别] 异常: {e} (处理时间: {processing_time:.1f}ms)")

        # 🔧 修复：异常时返回空结果，让调用方处理
        rec_logger.warning(f"⚠️ [临时识别] 异常返回空结果")
        return [{"text": ""}]  # 异常时也返回空字符串

    finally:
        # 清理GPU缓存
        try:
            torch.cuda.empty_cache()
        except:
            pass


def empty_cache():
    """清理缓存"""
    try:
        torch.cuda.empty_cache()
    except:
        pass


if __name__ == '__main__':
    print(test_recognize('../resource/audio_data/0/015.wav'))
    print(test_recognize('../resource/medical/26e1e410-e096-4ef0-bcfc-2f1f15ab5581.wav'))  # 环氧化水化酶
    print(test_recognize('../resource/medical/26e44373-be2f-43ae-a62e-c8a7496e1217.wav'))  # 细针抽吸活检
    print(test_recognize('../resource/medical/27c53560-6557-4d26-8eff-dd12687cfb5b.wav'))  # 脂类转移蛋白
    print(test_recognize('../resource/medical/27ccb4dd-c33c-458b-8872-6bf576d534c7.wav'))  # 绝经期后出血
    print(test_recognize('../resource/medical/27e1f997-fb57-40ad-b4e4-6639108335ae.wav'))  # 非小细胞肺癌
    print(test_recognize('../resource/medical/27e71bd1-00d1-4af1-bc41-2bb2a00b1bfd.wav'))  # 冠黄感冒颗粒
