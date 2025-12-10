import os
import sys
import tempfile
import soundfile as sf
import numpy as np
from scipy import signal
from modelscope import pipeline
from loguru import logger

from config.config import conf

# 直接使用配置文件中的声纹模型路径，不再通过 snapshot_download 下载
model_dir = conf.get('model', 'speech_campplus', fallback='')
logger.info(f"📁 声纹模型路径: {model_dir}")

# 说话人确认模型
sv_pipeline = pipeline(
    task='speaker-verification',
    model=model_dir,
    disable_update=True,
    local_files_only=True
)

# 目标采样率（ModelScope 声纹模型要求 16kHz）
TARGET_SAMPLE_RATE = 16000

# 检测是否在 Windows 上运行（sox 扩展不可用）
IS_WINDOWS = sys.platform == 'win32'
if IS_WINDOWS:
    logger.warning("⚠️ 检测到 Windows 系统，将使用 scipy 重采样（绕过 sox 限制）")


def resample_audio_for_windows(wav_path):
    """
    使用 scipy 重采样音频到 16kHz（Windows 兼容方案）。
    在 Linux/Mac 上不需要调用此函数。
    """
    try:
        audio_data, sample_rate = sf.read(wav_path)
        
        # 如果已经是目标采样率，直接返回原路径
        if sample_rate == TARGET_SAMPLE_RATE:
            return wav_path, None
        
        logger.info(f"📊 [Windows] 音频重采样: {sample_rate}Hz -> {TARGET_SAMPLE_RATE}Hz")
        
        # 计算重采样后的样本数
        num_samples = int(len(audio_data) * TARGET_SAMPLE_RATE / sample_rate)
        
        # 如果是立体声，转为单声道
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # 使用 scipy 进行重采样
        resampled_audio = signal.resample(audio_data, num_samples)
        
        # 保存到临时文件
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"resampled_{os.path.basename(wav_path)}")
        sf.write(temp_path, resampled_audio.astype(np.float32), TARGET_SAMPLE_RATE)
        
        logger.success(f"✅ [Windows] 重采样完成: {temp_path}")
        return temp_path, temp_path  # 返回路径和需要清理的临时文件
        
    except Exception as e:
        logger.warning(f"⚠️ [Windows] 重采样失败，尝试使用原文件: {e}")
        return wav_path, None


def embedding(wav_path):
    """
    提取单个音频的声纹特征向量。
    - Linux/Mac: 直接使用 ModelScope pipeline（效率高）
    - Windows: 先用 scipy 重采样，绕过 sox 限制
    """
    temp_file = None
    
    try:
        if IS_WINDOWS:
            # Windows: 预处理音频后再调用 pipeline
            processed_path, temp_file = resample_audio_for_windows(wav_path)
            result = sv_pipeline([processed_path], output_emb=True)
        else:
            # Linux/Mac: 直接使用 pipeline（内部会自动重采样）
            result = sv_pipeline([wav_path], output_emb=True)
        
        return result['embs'][0]
    
    except RuntimeError as e:
        # 如果在 Linux 上也遇到 sox 问题，fallback 到 scipy 方案
        if 'sox' in str(e).lower():
            logger.warning(f"⚠️ sox 扩展失败，使用 scipy fallback: {e}")
            processed_path, temp_file = resample_audio_for_windows(wav_path)
            result = sv_pipeline([processed_path], output_emb=True)
            return result['embs'][0]
        raise
    
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


def embeddings(wav_paths):
    """
    批量提取多个音频的声纹特征向量。
    - Linux/Mac: 直接使用 ModelScope pipeline（效率高）
    - Windows: 先用 scipy 重采样，绕过 sox 限制
    """
    temp_files = []
    
    try:
        if IS_WINDOWS:
            # Windows: 预处理所有音频
            processed_paths = []
            for wav_path in wav_paths:
                processed_path, temp_file = resample_audio_for_windows(wav_path)
                processed_paths.append(processed_path)
                if temp_file:
                    temp_files.append(temp_file)
            result = sv_pipeline(processed_paths, output_emb=True)
        else:
            # Linux/Mac: 直接使用 pipeline
            try:
                result = sv_pipeline(wav_paths, output_emb=True)
            except RuntimeError as e:
                # Fallback 到 scipy 方案
                if 'sox' in str(e).lower():
                    logger.warning(f"⚠️ sox 扩展失败，使用 scipy fallback")
                    processed_paths = []
                    for wav_path in wav_paths:
                        processed_path, temp_file = resample_audio_for_windows(wav_path)
                        processed_paths.append(processed_path)
                        if temp_file:
                            temp_files.append(temp_file)
                    result = sv_pipeline(processed_paths, output_emb=True)
                else:
                    raise
        
        return result['embs']
    
    finally:
        # 清理所有临时文件
        for temp_file in temp_files:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass


if __name__ == '__main__':
    print(embedding('../resource/audio_data/0/014.wav'))
    print(embeddings(['../resource/audio_data/0/014.wav', '../resource/audio_data/0/015.wav']))
