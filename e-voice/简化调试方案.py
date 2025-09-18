#!/usr/bin/env python3
"""
简化调试方案 - 不依赖torch等重包，专注于分析ModelScope结果
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_modelscope_basic():
    """基础ModelScope测试"""
    print("🚀 开始基础ModelScope测试...")
    
    try:
        from modelscope import pipeline, Tasks
        print("✅ ModelScope导入成功")
        
        # 测试最基本的配置
        print("🧪 测试基本配置...")
        
        basic_config = {
            "task": Tasks.auto_speech_recognition,
            "model": "iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
        }
        
        print(f"⏳ 正在初始化pipeline...")
        start_time = time.time()
        asr_pipeline = pipeline(**basic_config)
        init_time = time.time() - start_time
        print(f"✅ Pipeline初始化成功，耗时: {init_time:.2f}s")
        
        # 查找测试音频文件
        test_files = []
        possible_paths = [
            "resource/asr_speaker_demo.wav",
            "../resource/asr_speaker_demo.wav",
            "data/temp"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                if os.path.isdir(path):
                    # 查找temp目录中的最新文件
                    temp_files = [f for f in os.listdir(path) if f.endswith('.wav')]
                    if temp_files:
                        latest_file = max(temp_files, key=lambda f: os.path.getmtime(os.path.join(path, f)))
                        test_files.append(os.path.join(path, latest_file))
                else:
                    test_files.append(path)
        
        if not test_files:
            print("❌ 未找到测试音频文件")
            print("💡 建议：先录制一段音频以生成临时文件")
            return False
        
        print(f"📁 找到测试文件: {test_files}")
        
        # 测试识别
        for test_file in test_files[:2]:  # 最多测试2个文件
            print(f"\n🎵 测试文件: {test_file}")
            
            if not os.path.exists(test_file):
                print(f"❌ 文件不存在: {test_file}")
                continue
            
            file_size = os.path.getsize(test_file)
            print(f"📊 文件大小: {file_size} bytes")
            
            try:
                # 测试识别
                print("⏳ 开始识别...")
                start_time = time.time()
                result = asr_pipeline(test_file)
                recognize_time = time.time() - start_time
                
                print(f"✅ 识别完成，耗时: {recognize_time:.2f}s")
                print(f"🔍 原始结果类型: {type(result)}")
                print(f"🔍 原始结果内容: {result}")
                
                # 详细分析结果结构
                analyze_result_detailed(result)
                
            except Exception as e:
                print(f"❌ 识别失败: {e}")
                traceback.print_exc()
        
        return True
        
    except ImportError as e:
        print(f"❌ ModelScope导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False

def analyze_result_detailed(result):
    """详细分析识别结果"""
    print("\n" + "="*50)
    print("🔍 详细结果分析:")
    print("="*50)
    
    def safe_str(obj, max_len=200):
        try:
            s = str(obj)
            return s[:max_len] + "..." if len(s) > max_len else s
        except:
            return "<无法转换为字符串>"
    
    # 基础信息
    print(f"类型: {type(result)}")
    print(f"是否为None: {result is None}")
    
    if result is None:
        print("❌ 结果为None - 这是问题的核心!")
        return
    
    # 字符串类型
    if isinstance(result, str):
        print(f"字符串长度: {len(result)}")
        print(f"是否为空: {len(result.strip()) == 0}")
        print(f"内容: '{result}'")
        if len(result.strip()) == 0:
            print("❌ 字符串为空 - 这是问题!")
    
    # 字典类型
    elif isinstance(result, dict):
        print(f"字典键数量: {len(result)}")
        print(f"所有键: {list(result.keys())}")
        
        # 查找所有可能的文本字段
        text_fields = ['text', 'result', 'transcript', 'output', 'content', 'sentence']
        found_text = False
        
        for field in text_fields:
            if field in result:
                value = result[field]
                print(f"发现文本字段 '{field}': {safe_str(value)}")
                if isinstance(value, str) and len(value.strip()) > 0:
                    found_text = True
                    print(f"✅ 找到有效文本: '{value}'")
        
        if not found_text:
            print("❌ 未找到有效文本字段")
        
        # 打印所有字段的值
        print("\n所有字段详情:")
        for k, v in result.items():
            print(f"  {k}: {safe_str(v, 100)}")
    
    # 列表/元组类型
    elif isinstance(result, (list, tuple)):
        print(f"列表长度: {len(result)}")
        if result:
            print(f"第一个元素类型: {type(result[0])}")
            print(f"第一个元素内容: {safe_str(result[0])}")
            
            # 如果第一个元素是字典，分析其文本字段
            if isinstance(result[0], dict):
                analyze_result_detailed(result[0])
            elif isinstance(result[0], str):
                print(f"第一个元素是否为空: {len(result[0].strip()) == 0}")
        else:
            print("❌ 列表为空")
    
    # 其他类型
    else:
        print(f"其他类型内容: {safe_str(result)}")
        
        # 尝试获取属性
        if hasattr(result, '__dict__'):
            print(f"对象属性: {list(result.__dict__.keys())}")
        
        # 尝试dir()
        attrs = [attr for attr in dir(result) if not attr.startswith('_')]
        if attrs:
            print(f"可用方法/属性: {attrs[:10]}")  # 显示前10个

def test_current_recognize_function():
    """测试当前的recognize函数"""
    print("\n🧪 测试当前的recognize函数...")
    
    try:
        from speech_recognition.recognize import recognize
        print("✅ recognize函数导入成功")
        
        # 查找测试音频
        test_file = None
        possible_paths = [
            "resource/asr_speaker_demo.wav",
            "../resource/asr_speaker_demo.wav"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                test_file = path
                break
        
        # 如果没有找到，尝试temp目录
        if not test_file:
            temp_dir = "data/temp"
            if os.path.exists(temp_dir):
                temp_files = [f for f in os.listdir(temp_dir) if f.endswith('.wav')]
                if temp_files:
                    latest_file = max(temp_files, key=lambda f: os.path.getmtime(os.path.join(temp_dir, f)))
                    test_file = os.path.join(temp_dir, latest_file)
        
        if not test_file:
            print("❌ 未找到测试音频文件")
            return False
        
        print(f"📁 使用测试文件: {test_file}")
        
        # 测试recognize函数
        try:
            print("⏳ 调用recognize函数...")
            result = recognize(test_file)
            print(f"✅ recognize返回结果: '{result}'")
            print(f"🔍 结果类型: {type(result)}")
            print(f"🔍 是否为空: {len(result.strip()) == 0 if isinstance(result, str) else True}")
            
            return True
            
        except Exception as e:
            print(f"❌ recognize函数调用失败: {e}")
            traceback.print_exc()
            return False
    
    except ImportError as e:
        print(f"❌ recognize函数导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始简化ModelScope调试...")
    print("="*60)
    
    # 1. 测试基本ModelScope功能
    success1 = test_modelscope_basic()
    
    # 2. 测试当前recognize函数
    success2 = test_current_recognize_function()
    
    print("\n" + "="*60)
    print("📊 调试总结:")
    print(f"   ModelScope基础测试: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   recognize函数测试: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if not (success1 or success2):
        print("\n💡 建议:")
        print("   1. 检查ModelScope是否正确安装")
        print("   2. 确认是否有可用的测试音频文件")
        print("   3. 检查Python环境和依赖")
    
    print("="*60)

if __name__ == "__main__":
    main()
