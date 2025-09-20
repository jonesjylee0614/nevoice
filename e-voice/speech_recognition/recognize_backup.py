import os
import time
import torch
from modelscope import pipeline, Tasks
from loguru import logger

# 创建专用的语音识别日志
recognition_logger = logger.bind(component="speech_recognition")

# 导入错误恢复装饰器
try:
    from ..error_handling.error_recovery import with_error_recovery
except ImportError:
    # 如果错误恢复模块不可用，创建一个空装饰器
    def with_error_recovery(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# 🎯 智能词汇管理：根据系统配置选择最优词汇文件
from .vocabulary_manager import vocab_manager

# 初始化词汇管理器并选择最优配置
vocab_file = vocab_manager.load_vocabulary(mode='auto', max_memory_mb=200)

# 🔧 紧急修复：强制使用最简配置，确保ModelScope正常工作
try:
    # 尝试完全禁用自定义词汇的配置
    speech_paraformer_large_pipeline = pipeline(
        task=Tasks.auto_speech_recognition,
        model='iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch', 
        model_revision="v2.0.5",
        vad_model='iic/speech_fsmn_vad_zh-cn-16k-common-pytorch', 
        vad_model_revision="v2.0.4",
        punc_model='iic/punc_ct-transformer_cn-en-common-vocab471067-large', 
        punc_model_revision="v2.0.4",
        # 🚨 完全禁用自定义词汇，确保不影响识别
        disable_update=True
    )
    recognition_logger.success("✅ ModelScope pipeline初始化成功（无自定义词汇）")
except Exception as e:
    recognition_logger.error(f"❌ ModelScope pipeline初始化失败: {e}")
    # 降级到最基本的配置
    speech_paraformer_large_pipeline = pipeline(
        task=Tasks.auto_speech_recognition,
        model='iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
        disable_update=True,
    )
    recognition_logger.warning("⚠️ 使用基础ModelScope配置")

@with_error_recovery(error_category="model_error", component="modelscope")
def recognize(audio):
    """
    语音识别函数 - 增强版本，包含详细的调试日志和错误恢复
    
    Args:
        audio: 音频文件路径或音频数据
        
    Returns:
        识别结果或None
    
    注意：
    - 已集成Loguru详细日志记录
    - 包含ModelScope调用时间统计
    - 自动GPU内存管理
    - 智能错误恢复机制
    """
    start_time = time.time()
    
    # 检查音频输入
    audio_info = "未知"
    if isinstance(audio, str):
        # 音频文件路径
        if os.path.exists(audio):
            file_size = os.path.getsize(audio)
            audio_info = f"文件路径: {audio}, 大小: {file_size} bytes"
            recognition_logger.debug(f"语音识别输入: {audio_info}")
        else:
            recognition_logger.error(f"音频文件不存在: {audio}")
            return None
    elif hasattr(audio, '__len__'):
        # 音频数组数据
        audio_info = f"音频数组, 长度: {len(audio)}"
        recognition_logger.debug(f"语音识别输入: {audio_info}")
    else:
        recognition_logger.debug(f"语音识别输入类型: {type(audio)}")
    
    try:
        recognition_logger.debug("开始调用ModelScope语音识别模型")
        
        # 调用识别模型
        res = speech_paraformer_large_pipeline(audio)
        
        # 计算处理时间
        processing_time = (time.time() - start_time) * 1000
        
        # 记录原始结果
        recognition_logger.debug(f"识别模型调用完成，耗时: {processing_time:.1f}ms")
        recognition_logger.debug(f"原始识别结果类型: {type(res)}")
        recognition_logger.debug(f"原始识别结果内容: {res}")
        
        # 🔍 详细分析和调试识别结果结构
        recognition_logger.warning(f"🔍 [调试] ModelScope原始返回值: {res}")
        recognition_logger.warning(f"🔍 [调试] 返回值类型: {type(res)}")
        
        # 提取文本结果的逻辑
        extracted_text = None
        
        if res is None:
            recognition_logger.error("❌ 识别结果为None")
        elif isinstance(res, dict):
            recognition_logger.warning(f"🔍 [调试] 字典结果，所有键: {list(res.keys())}")
            # 尝试多种可能的文本字段名
            for text_key in ['text', 'result', 'transcript', 'output', 'content']:
                if text_key in res:
                    extracted_text = res[text_key]
                    recognition_logger.warning(f"🔍 [调试] 从'{text_key}'字段提取文本: '{extracted_text}'")
                    break
            if not extracted_text:
                # 尝试从嵌套结构中提取
                for key, value in res.items():
                    recognition_logger.warning(f"🔍 [调试] 键'{key}': 值={value}, 类型={type(value)}")
                    if isinstance(value, str) and value.strip():
                        extracted_text = value
                        recognition_logger.warning(f"🔍 [调试] 从'{key}'提取非空字符串: '{extracted_text}'")
                        break
                    elif isinstance(value, (list, dict)) and value:
                        recognition_logger.warning(f"🔍 [调试] 键'{key}'包含嵌套数据: {value}")
        elif isinstance(res, (list, tuple)):
            recognition_logger.warning(f"🔍 [调试] 列表/元组结果，长度: {len(res)}")
            if res:
                recognition_logger.warning(f"🔍 [调试] 首个元素: {res[0]}, 类型: {type(res[0])}")
                if isinstance(res[0], dict):
                    # 递归处理字典
                    for text_key in ['text', 'result', 'transcript']:
                        if text_key in res[0]:
                            extracted_text = res[0][text_key]
                            recognition_logger.warning(f"🔍 [调试] 从列表首项的'{text_key}'提取: '{extracted_text}'")
                            break
                elif isinstance(res[0], str):
                    extracted_text = res[0]
                    recognition_logger.warning(f"🔍 [调试] 列表首项为字符串: '{extracted_text}'")
        elif isinstance(res, str):
            extracted_text = res
            recognition_logger.warning(f"🔍 [调试] 直接字符串结果: '{extracted_text}'")
        else:
            recognition_logger.error(f"❌ 未知结果类型: {type(res)}, 内容: {res}")
        
        # 最终结果处理
        if extracted_text and extracted_text.strip():
            recognition_logger.success(f"✅ 成功识别文本: '{extracted_text}' (处理时间: {processing_time:.1f}ms)")
            return extracted_text
        else:
            recognition_logger.error(f"❌ 未能提取有效文本，原始结果: {res}")
            return ""
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        recognition_logger.error(f"语音识别失败: {str(e)} (耗时: {processing_time:.1f}ms)")
        recognition_logger.error(f"详细错误信息: {e.__class__.__name__}: {str(e)}")
        import traceback
        recognition_logger.error(f"完整异常栈: {traceback.format_exc()}")
        return None
        
    finally:
        empty_cache()


def empty_cache():
    # 处理完成后清理gpu缓存
    try:
        torch.cuda.empty_cache()
        recognition_logger.trace("GPU缓存清理完成")
    except Exception as e:
        recognition_logger.warning(f"GPU缓存清理失败: {str(e)}")

if __name__ == '__main__':
    txt = recognize('../resource/asr_speaker_demo.wav')
    print(txt)
