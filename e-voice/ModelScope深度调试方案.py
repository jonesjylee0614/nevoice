#!/usr/bin/env python3
"""
ModelScope深度调试方案 - 解决text字段返回空的问题
"""

import os
import time
import json
import torch
import numpy as np
import soundfile as sf
from modelscope import pipeline, Tasks
from loguru import logger

class ModelScopeDebugger:
    """ModelScope深度调试器"""
    
    def __init__(self):
        self.logger = logger.bind(component="modelscope_debugger")
        self.test_results = {}
        
    def test_different_configurations(self):
        """测试不同的ModelScope配置"""
        
        configs = {
            "config_1_minimal": {
                "description": "最简配置",
                "params": {
                    "task": Tasks.auto_speech_recognition,
                    "model": "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
                }
            },
            "config_2_no_vad": {
                "description": "无VAD配置",
                "params": {
                    "task": Tasks.auto_speech_recognition,
                    "model": "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
                    "disable_update": True
                }
            },
            "config_3_basic_model": {
                "description": "基础模型",
                "params": {
                    "task": Tasks.auto_speech_recognition,
                    "model": "iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
                }
            },
            "config_4_with_batch": {
                "description": "带批处理参数",
                "params": {
                    "task": Tasks.auto_speech_recognition,
                    "model": "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
                    "disable_update": True
                }
            }
        }
        
        results = {}
        
        for config_name, config_data in configs.items():
            self.logger.info(f"🧪 测试配置: {config_name} - {config_data['description']}")
            
            try:
                # 创建pipeline
                start_time = time.time()
                asr_pipeline = pipeline(**config_data['params'])
                init_time = time.time() - start_time
                
                self.logger.info(f"✅ 配置 {config_name} 初始化成功，耗时: {init_time:.2f}s")
                
                # 测试识别
                result = self.test_recognition_with_pipeline(asr_pipeline, config_name)
                results[config_name] = {
                    "init_success": True,
                    "init_time": init_time,
                    "recognition_result": result
                }
                
            except Exception as e:
                self.logger.error(f"❌ 配置 {config_name} 失败: {e}")
                results[config_name] = {
                    "init_success": False,
                    "error": str(e)
                }
                
        return results
    
    def test_recognition_with_pipeline(self, asr_pipeline, config_name):
        """使用指定pipeline测试识别"""
        
        # 生成不同类型的测试音频
        test_audios = {
            "sine_wave": self.generate_sine_wave(),
            "speech_like": self.generate_speech_like_audio(),
            "white_noise": self.generate_white_noise(),
            "real_file": self.find_real_audio_file()
        }
        
        results = {}
        
        for audio_name, audio_file in test_audios.items():
            if audio_file is None:
                continue
                
            self.logger.info(f"🎵 测试音频: {audio_name} - {audio_file}")
            
            try:
                start_time = time.time()
                
                # 测试不同的调用方式
                recognition_methods = [
                    ("direct_call", lambda: asr_pipeline(audio_file)),
                    ("with_batch_size", lambda: asr_pipeline(audio_file, batch_size_s=60)),
                    ("with_params", lambda: asr_pipeline(audio_file, output_dir=None))
                ]
                
                method_results = {}
                
                for method_name, method_func in recognition_methods:
                    try:
                        method_start = time.time()
                        result = method_func()
                        method_time = time.time() - method_start
                        
                        # 详细分析结果
                        analysis = self.analyze_result_structure(result)
                        
                        method_results[method_name] = {
                            "success": True,
                            "time_ms": method_time * 1000,
                            "result": result,
                            "analysis": analysis
                        }
                        
                        self.logger.warning(f"🔍 [{config_name}][{audio_name}][{method_name}] 结果: {result}")
                        self.logger.warning(f"🔍 [{config_name}][{audio_name}][{method_name}] 分析: {analysis}")
                        
                    except Exception as e:
                        method_results[method_name] = {
                            "success": False,
                            "error": str(e)
                        }
                        self.logger.error(f"❌ [{config_name}][{audio_name}][{method_name}] 失败: {e}")
                
                results[audio_name] = method_results
                
            except Exception as e:
                results[audio_name] = {"error": str(e)}
                self.logger.error(f"❌ [{config_name}][{audio_name}] 测试失败: {e}")
        
        return results
    
    def analyze_result_structure(self, result):
        """分析识别结果的结构"""
        analysis = {
            "type": str(type(result)),
            "content": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
        }
        
        if result is None:
            analysis["issue"] = "结果为None"
        elif isinstance(result, str):
            analysis["length"] = len(result)
            analysis["empty"] = len(result.strip()) == 0
        elif isinstance(result, dict):
            analysis["keys"] = list(result.keys())
            if 'text' in result:
                analysis["text_length"] = len(result['text'])
                analysis["text_empty"] = len(result['text'].strip()) == 0
            analysis["all_values"] = {k: str(v)[:100] for k, v in result.items()}
        elif isinstance(result, (list, tuple)):
            analysis["length"] = len(result)
            if result:
                analysis["first_item"] = str(result[0])[:100]
                if isinstance(result[0], dict) and 'text' in result[0]:
                    analysis["first_text"] = result[0]['text']
                    analysis["first_text_empty"] = len(result[0]['text'].strip()) == 0
        
        return analysis
    
    def generate_sine_wave(self, filename="debug_sine.wav"):
        """生成正弦波测试音频"""
        sample_rate = 16000
        duration = 2.0
        frequency = 440  # A音
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        sf.write(filename, audio, sample_rate)
        self.logger.info(f"✅ 生成正弦波音频: {filename}")
        return filename
    
    def generate_speech_like_audio(self, filename="debug_speech.wav"):
        """生成语音类似的音频"""
        sample_rate = 16000
        duration = 3.0
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 创建语音特征的复合波形
        audio = (
            0.15 * np.sin(2 * np.pi * 200 * t) +    # 基频200Hz
            0.1 * np.sin(2 * np.pi * 400 * t) +     # 2次谐波
            0.05 * np.sin(2 * np.pi * 600 * t) +    # 3次谐波
            0.03 * np.sin(2 * np.pi * 800 * t) +    # 4次谐波
            0.02 * np.random.normal(0, 1, len(t))   # 噪声
        )
        
        # 添加包络（语音的音量变化）
        envelope = np.exp(-((t - duration/2) / (duration/2))**2)
        audio = audio * envelope * 0.8
        
        sf.write(filename, audio, sample_rate)
        self.logger.info(f"✅ 生成语音类音频: {filename}")
        return filename
    
    def generate_white_noise(self, filename="debug_noise.wav"):
        """生成白噪声音频"""
        sample_rate = 16000
        duration = 1.0
        
        audio = np.random.normal(0, 0.1, int(sample_rate * duration))
        
        sf.write(filename, audio, sample_rate)
        self.logger.info(f"✅ 生成白噪声音频: {filename}")
        return filename
    
    def find_real_audio_file(self):
        """查找现有的真实音频文件"""
        possible_paths = [
            "resource/asr_speaker_demo.wav",
            "../resource/asr_speaker_demo.wav",
            "data/temp/realtime_96989_54_1757266405794.wav"  # 用户提到的文件
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"✅ 找到真实音频文件: {path}")
                return path
        
        self.logger.warning("⚠️ 未找到真实音频文件")
        return None
    
    def test_audio_file_properties(self, audio_file):
        """测试音频文件的属性"""
        try:
            # 使用soundfile读取
            audio_data, sample_rate = sf.read(audio_file)
            
            properties = {
                "file_size": os.path.getsize(audio_file),
                "sample_rate": sample_rate,
                "duration": len(audio_data) / sample_rate,
                "channels": audio_data.ndim,
                "shape": audio_data.shape,
                "dtype": str(audio_data.dtype),
                "min": float(np.min(audio_data)),
                "max": float(np.max(audio_data)),
                "mean": float(np.mean(audio_data)),
                "rms": float(np.sqrt(np.mean(audio_data ** 2))),
                "zero_crossings": int(np.sum(np.diff(np.sign(audio_data)) != 0))
            }
            
            self.logger.info(f"🔍 音频文件属性: {json.dumps(properties, indent=2)}")
            return properties
            
        except Exception as e:
            self.logger.error(f"❌ 读取音频文件失败: {e}")
            return None
    
    def run_comprehensive_debug(self):
        """运行综合调试"""
        self.logger.info("🚀 开始ModelScope综合调试...")
        
        # 1. 测试不同配置
        self.logger.info("=" * 60)
        self.logger.info("阶段1: 测试不同的ModelScope配置")
        self.logger.info("=" * 60)
        config_results = self.test_different_configurations()
        
        # 2. 分析音频文件
        self.logger.info("=" * 60)
        self.logger.info("阶段2: 分析音频文件属性")
        self.logger.info("=" * 60)
        
        test_files = ["debug_sine.wav", "debug_speech.wav", "debug_noise.wav"]
        for file in test_files:
            if os.path.exists(file):
                self.test_audio_file_properties(file)
        
        # 3. 生成调试报告
        self.logger.info("=" * 60)
        self.logger.info("阶段3: 生成调试报告")
        self.logger.info("=" * 60)
        
        report = self.generate_debug_report(config_results)
        
        # 保存报告
        with open("modelscope_debug_report.json", "w", encoding="utf-8") as f:
            json.dump({
                "config_results": config_results,
                "timestamp": time.time(),
                "summary": report
            }, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.success("✅ 调试报告已保存: modelscope_debug_report.json")
        
        return config_results
    
    def generate_debug_report(self, results):
        """生成调试报告"""
        
        successful_configs = []
        failed_configs = []
        empty_text_configs = []
        
        for config_name, result in results.items():
            if not result.get("init_success", False):
                failed_configs.append(config_name)
                continue
                
            successful_configs.append(config_name)
            
            # 检查是否有空文本问题
            recognition_result = result.get("recognition_result", {})
            has_empty_text = False
            
            for audio_name, audio_results in recognition_result.items():
                if isinstance(audio_results, dict):
                    for method_name, method_result in audio_results.items():
                        if method_result.get("success", False):
                            analysis = method_result.get("analysis", {})
                            if (analysis.get("text_empty", False) or 
                                analysis.get("first_text_empty", False) or
                                analysis.get("empty", False)):
                                has_empty_text = True
                                break
            
            if has_empty_text:
                empty_text_configs.append(config_name)
        
        report = {
            "total_configs": len(results),
            "successful_configs": len(successful_configs),
            "failed_configs": len(failed_configs),
            "empty_text_configs": len(empty_text_configs),
            "successful_list": successful_configs,
            "failed_list": failed_configs,
            "empty_text_list": empty_text_configs
        }
        
        self.logger.info(f"📊 调试总结: {json.dumps(report, indent=2, ensure_ascii=False)}")
        
        if empty_text_configs:
            self.logger.error(f"❌ 发现空文本问题的配置: {empty_text_configs}")
            self.logger.info("💡 建议:")
            self.logger.info("   1. 检查模型版本兼容性")
            self.logger.info("   2. 尝试不同的音频格式")
            self.logger.info("   3. 检查模型参数设置")
            self.logger.info("   4. 验证音频文件内容")
        
        return report

def main():
    """主调试函数"""
    logger.remove()
    logger.add(lambda msg: print(msg.record["message"]), level="INFO")
    logger.add("modelscope_debug.log", level="DEBUG")
    
    debugger = ModelScopeDebugger()
    results = debugger.run_comprehensive_debug()
    
    print("\n" + "="*60)
    print("🎯 调试完成！请查看详细结果:")
    print("   - 控制台输出: 实时调试信息")
    print("   - 日志文件: modelscope_debug.log")
    print("   - 报告文件: modelscope_debug_report.json")
    print("="*60)

if __name__ == "__main__":
    main()
