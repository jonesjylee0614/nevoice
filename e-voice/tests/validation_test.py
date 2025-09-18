"""
验证测试脚本 - 实时语音识别系统功能验证
"""
import os
import sys
import time
import json
import base64
from pathlib import Path

import numpy as np
import pytest

pytest.skip("功能验证脚本仅供手动运行，自动化测试默认跳过", allow_module_level=True)

import websocket
from loguru import logger

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class ValidationTester:
    """
    功能验证测试器
    
    验证项目：
    1. WebSocket连接和通信
    2. 音频数据接收和处理
    3. 语音识别功能
    4. 实时响应能力
    5. 错误处理机制
    """
    
    def __init__(self, server_url="ws://localhost:8210"):
        self.server_url = server_url
        self.test_logger = logger.bind(component="validation_test")
        
        # 测试结果
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        self.test_logger.info("✅ 验证测试器初始化完成")
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """记录测试结果"""
        if passed:
            self.test_results['passed'] += 1
            self.test_logger.success(f"✅ {test_name}: 通过")
        else:
            self.test_results['failed'] += 1
            self.test_logger.error(f"❌ {test_name}: 失败 - {details}")
        
        self.test_results['details'].append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': time.time()
        })
    
    def test_websocket_connection(self) -> bool:
        """测试WebSocket连接"""
        self.test_logger.info("🔗 测试WebSocket连接...")
        
        try:
            ws = websocket.create_connection(self.server_url, timeout=5.0)
            ws.close()
            self.log_test_result("WebSocket连接", True)
            return True
        except Exception as e:
            self.log_test_result("WebSocket连接", False, str(e))
            return False
    
    def test_audio_data_transmission(self) -> bool:
        """测试音频数据传输"""
        self.test_logger.info("🎵 测试音频数据传输...")
        
        try:
            # 生成测试音频数据
            sample_rate = 16000
            duration = 1.0
            samples = int(sample_rate * duration)
            
            # 生成1kHz正弦波
            t = np.linspace(0, duration, samples, False)
            audio_data = np.sin(2 * np.pi * 1000 * t) * 0.1  # 1kHz, RMS=0.07
            audio_16bit = (audio_data * 32767).astype(np.int16)
            
            # 编码为base64
            audio_bytes = audio_16bit.tobytes()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # 发送音频数据
            ws = websocket.create_connection(self.server_url, timeout=5.0)
            
            message = json.dumps({
                'type': 'audio_chunk',
                'data': audio_b64,
                'sample_rate': sample_rate,
                'debug_info': {
                    'test_type': 'validation_test',
                    'audio_type': '1kHz_sine_wave',
                    'rms_expected': 0.07
                }
            })
            
            ws.send(message)
            
            # 等待响应
            response = ws.recv()
            ws.close()
            
            # 验证响应
            if response:
                self.log_test_result("音频数据传输", True, f"收到响应: {len(response)}字符")
                return True
            else:
                self.log_test_result("音频数据传输", False, "未收到响应")
                return False
                
        except Exception as e:
            self.log_test_result("音频数据传输", False, str(e))
            return False
    
    def test_speech_recognition(self) -> bool:
        """测试语音识别功能"""
        self.test_logger.info("🗣️ 测试语音识别功能...")
        
        try:
            # 生成包含语音特征的测试音频
            sample_rate = 16000
            duration = 2.0
            samples = int(sample_rate * duration)
            
            # 创建复合波形模拟语音（多个频率组合）
            t = np.linspace(0, duration, samples, False)
            # 模拟语音的基频和谐波
            audio_data = (
                0.05 * np.sin(2 * np.pi * 200 * t) +    # 基频200Hz
                0.03 * np.sin(2 * np.pi * 400 * t) +    # 2次谐波
                0.02 * np.sin(2 * np.pi * 600 * t) +    # 3次谐波
                0.01 * np.random.normal(0, 1, samples)   # 添加噪声
            )
            
            # 添加包络（模拟语音的音量变化）
            envelope = np.exp(-((t - duration/2) / (duration/4))**2)
            audio_data = audio_data * envelope * 0.5  # RMS约0.1
            
            audio_16bit = (audio_data * 32767).astype(np.int16)
            audio_b64 = base64.b64encode(audio_16bit.tobytes()).decode('utf-8')
            
            # 发送音频进行识别
            ws = websocket.create_connection(self.server_url, timeout=10.0)
            
            message = json.dumps({
                'type': 'audio_chunk',
                'data': audio_b64,
                'sample_rate': sample_rate,
                'debug_info': {
                    'test_type': 'speech_recognition_test',
                    'audio_type': 'synthetic_speech',
                    'expected_rms': 0.1
                }
            })
            
            ws.send(message)
            
            # 等待识别结果
            response = ws.recv()
            ws.close()
            
            # 分析响应
            try:
                response_data = json.loads(response)
                if 'text' in response_data or 'result' in response_data:
                    self.log_test_result("语音识别功能", True, f"识别响应: {response}")
                    return True
                else:
                    self.log_test_result("语音识别功能", False, f"响应格式异常: {response}")
                    return False
            except json.JSONDecodeError:
                # 响应可能不是JSON格式
                if response.strip():
                    self.log_test_result("语音识别功能", True, f"非JSON响应: {response}")
                    return True
                else:
                    self.log_test_result("语音识别功能", False, "空响应")
                    return False
                    
        except Exception as e:
            self.log_test_result("语音识别功能", False, str(e))
            return False
    
    def test_real_time_response(self) -> bool:
        """测试实时响应能力"""
        self.test_logger.info("⚡ 测试实时响应能力...")
        
        try:
            ws = websocket.create_connection(self.server_url, timeout=5.0)
            
            # 发送多个音频片段，测试实时处理
            response_times = []
            
            for i in range(3):
                # 生成短音频片段（0.5秒）
                sample_rate = 16000
                duration = 0.5
                samples = int(sample_rate * duration)
                
                t = np.linspace(0, duration, samples, False)
                audio_data = 0.05 * np.sin(2 * np.pi * 440 * t)  # 440Hz (A音)
                audio_16bit = (audio_data * 32767).astype(np.int16)
                audio_b64 = base64.b64encode(audio_16bit.tobytes()).decode('utf-8')
                
                # 记录发送时间
                send_time = time.time()
                
                message = json.dumps({
                    'type': 'audio_chunk',
                    'data': audio_b64,
                    'sample_rate': sample_rate,
                    'chunk_id': i,
                    'debug_info': {'test_type': 'realtime_test'}
                })
                
                ws.send(message)
                
                # 等待响应
                response = ws.recv()
                response_time = time.time() - send_time
                response_times.append(response_time)
                
                self.test_logger.debug(f"音频片段 {i+1} 响应时间: {response_time*1000:.2f}ms")
            
            ws.close()
            
            # 评估实时性能
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            # 判断是否满足实时要求（平均<1秒，最大<2秒）
            real_time_ok = avg_response_time < 1.0 and max_response_time < 2.0
            
            details = f"平均响应时间: {avg_response_time*1000:.2f}ms, 最大: {max_response_time*1000:.2f}ms"
            self.log_test_result("实时响应能力", real_time_ok, details)
            
            return real_time_ok
            
        except Exception as e:
            self.log_test_result("实时响应能力", False, str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理机制"""
        self.test_logger.info("🛡️ 测试错误处理机制...")
        
        error_tests = [
            ("无效JSON", "invalid json data"),
            ("缺少字段", json.dumps({"type": "audio_chunk"})),  # 缺少data字段
            ("无效音频数据", json.dumps({"type": "audio_chunk", "data": "invalid_base64"})),
            ("空音频数据", json.dumps({"type": "audio_chunk", "data": ""}))
        ]
        
        passed_tests = 0
        
        for test_name, test_data in error_tests:
            try:
                ws = websocket.create_connection(self.server_url, timeout=5.0)
                
                # 发送错误数据
                ws.send(test_data)
                
                try:
                    # 等待响应（应该有错误处理响应或连接保持稳定）
                    response = ws.recv()
                    error_handled = True
                except websocket.WebSocketTimeoutException:
                    # 超时也可能是正常的错误处理方式
                    error_handled = True
                except:
                    error_handled = False
                
                ws.close()
                
                # 测试服务器是否仍然可用
                try:
                    test_ws = websocket.create_connection(self.server_url, timeout=3.0)
                    test_ws.close()
                    server_stable = True
                except:
                    server_stable = False
                
                test_passed = error_handled and server_stable
                if test_passed:
                    passed_tests += 1
                    self.test_logger.debug(f"✅ 错误处理测试 [{test_name}]: 通过")
                else:
                    self.test_logger.warning(f"❌ 错误处理测试 [{test_name}]: 失败")
                
            except Exception as e:
                self.test_logger.error(f"错误处理测试 [{test_name}] 异常: {e}")
        
        # 总体评估
        error_handling_ok = passed_tests >= len(error_tests) * 0.8  # 80%通过率
        details = f"通过 {passed_tests}/{len(error_tests)} 项错误处理测试"
        self.log_test_result("错误处理机制", error_handling_ok, details)
        
        return error_handling_ok
    
    def test_audio_quality_requirements(self) -> bool:
        """测试音频质量要求"""
        self.test_logger.info("🎚️ 测试音频质量要求...")
        
        # 测试不同RMS级别的音频
        rms_tests = [
            ("极低音量", 0.0001),   # 应该被拒绝或产生警告
            ("低音量", 0.005),     # 边缘情况
            ("标准音量", 0.05),    # 应该正常处理
            ("高音量", 0.2),       # 应该正常处理
            ("过载", 0.9)          # 可能产生警告但仍处理
        ]
        
        quality_results = {}
        
        for test_name, rms_level in rms_tests:
            try:
                # 生成指定RMS的音频
                sample_rate = 16000
                duration = 1.0
                samples = int(sample_rate * duration)
                
                # 生成白噪声并缩放到指定RMS
                audio_data = np.random.normal(0, rms_level, samples)
                audio_16bit = (audio_data * 32767).astype(np.int16)
                audio_b64 = base64.b64encode(audio_16bit.tobytes()).decode('utf-8')
                
                ws = websocket.create_connection(self.server_url, timeout=5.0)
                
                message = json.dumps({
                    'type': 'audio_chunk',
                    'data': audio_b64,
                    'sample_rate': sample_rate,
                    'debug_info': {
                        'test_type': 'audio_quality_test',
                        'expected_rms': rms_level
                    }
                })
                
                start_time = time.time()
                ws.send(message)
                response = ws.recv()
                response_time = time.time() - start_time
                
                ws.close()
                
                quality_results[test_name] = {
                    'rms': rms_level,
                    'response_time': response_time,
                    'got_response': bool(response),
                    'response_content': response
                }
                
            except Exception as e:
                quality_results[test_name] = {
                    'rms': rms_level,
                    'error': str(e)
                }
        
        # 评估音频质量处理能力
        successful_tests = sum(1 for result in quality_results.values() 
                             if result.get('got_response', False))
        quality_ok = successful_tests >= len(rms_tests) * 0.6  # 60%处理成功
        
        details = f"成功处理 {successful_tests}/{len(rms_tests)} 种音频质量"
        self.log_test_result("音频质量要求", quality_ok, details)
        
        return quality_ok
    
    def run_all_tests(self) -> dict:
        """运行所有验证测试"""
        self.test_logger.info("🧪 开始功能验证测试...")
        
        # 定义测试方法
        tests = [
            ("WebSocket连接", self.test_websocket_connection),
            ("音频数据传输", self.test_audio_data_transmission),
            ("语音识别功能", self.test_speech_recognition),
            ("实时响应能力", self.test_real_time_response),
            ("错误处理机制", self.test_error_handling),
            ("音频质量要求", self.test_audio_quality_requirements)
        ]
        
        # 执行测试
        for test_name, test_method in tests:
            self.test_logger.info(f"📋 执行测试: {test_name}")
            try:
                test_method()
            except Exception as e:
                self.log_test_result(test_name, False, f"测试异常: {e}")
        
        # 生成测试总结
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests) * 100 if total_tests > 0 else 0
        
        summary = {
            'total_tests': total_tests,
            'passed': self.test_results['passed'],
            'failed': self.test_results['failed'],
            'success_rate': success_rate,
            'details': self.test_results['details']
        }
        
        # 输出测试总结
        self.test_logger.info("📊 验证测试完成")
        self.test_logger.info(f"✅ 通过: {self.test_results['passed']}")
        self.test_logger.info(f"❌ 失败: {self.test_results['failed']}")
        self.test_logger.info(f"🎯 成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            self.test_logger.success("🎉 系统验证通过！")
        else:
            self.test_logger.warning("⚠️ 系统存在问题，需要进一步检查")
        
        return summary

def main():
    """主验证函数"""
    # 配置日志
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
    
    # 创建验证测试器
    tester = ValidationTester("ws://localhost:8210")
    
    try:
        # 运行验证测试
        results = tester.run_all_tests()
        
        # 保存结果
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        result_file = f'validation_results_{timestamp}.json'
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📊 验证结果已保存: {result_file}")
        
        return results['success_rate'] >= 80
        
    except KeyboardInterrupt:
        print("\n⏹️ 验证测试被用户中断")
        return False
    except Exception as e:
        logger.error(f"验证测试异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
