"""
性能测试脚本 - 实时语音识别系统
"""
import os
import sys
import time
import json
import asyncio
import statistics
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import websocket
import base64
import wave
import numpy as np
from loguru import logger

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class PerformanceTester:
    """
    实时语音识别性能测试器
    
    测试项目：
    1. 响应时间测试
    2. 并发连接测试  
    3. 音频质量适应性测试
    4. 内存使用测试
    5. 错误恢复测试
    6. 长时间稳定性测试
    """
    
    def __init__(self, server_url="ws://localhost:8210"):
        self.server_url = server_url
        self.test_logger = logger.bind(component="performance_test")
        
        # 测试配置
        self.test_configs = {
            'response_time': {
                'sample_count': 50,
                'timeout': 5.0
            },
            'concurrency': {
                'max_connections': 20,
                'test_duration': 30
            },
            'audio_quality': {
                'rms_levels': [0.001, 0.01, 0.05, 0.1, 0.2],
                'duration_range': [0.5, 1.0, 2.0, 5.0]
            },
            'stability': {
                'test_duration': 300,  # 5分钟
                'request_interval': 1.0
            }
        }
        
        # 测试结果存储
        self.results = {
            'start_time': None,
            'end_time': None,
            'tests_completed': {},
            'performance_metrics': {},
            'error_logs': []
        }
        
        # 生成测试音频
        self.test_audio_samples = self._generate_test_audio()
        
        self.test_logger.info("🧪 性能测试器初始化完成")
    
    def _generate_test_audio(self) -> Dict[str, bytes]:
        """生成不同质量的测试音频"""
        samples = {}
        sample_rate = 16000
        duration = 2.0  # 2秒
        
        # 生成不同RMS级别的音频
        for rms_level in [0.001, 0.01, 0.05, 0.1]:
            # 生成白噪声
            samples_count = int(sample_rate * duration)
            audio_data = np.random.normal(0, rms_level, samples_count)
            
            # 转换为16位PCM
            audio_16bit = (audio_data * 32767).astype(np.int16)
            
            # 编码为base64
            audio_bytes = audio_16bit.tobytes()
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            samples[f'rms_{rms_level}'] = audio_b64
        
        # 生成静音音频
        silence = np.zeros(int(sample_rate * duration), dtype=np.int16)
        samples['silence'] = base64.b64encode(silence.tobytes()).decode('utf-8')
        
        return samples
    
    async def test_response_time(self) -> Dict[str, Any]:
        """响应时间测试"""
        self.test_logger.info("🚀 开始响应时间测试...")
        
        response_times = []
        success_count = 0
        error_count = 0
        
        for i in range(self.test_configs['response_time']['sample_count']):
            try:
                start_time = time.time()
                
                # 创建WebSocket连接
                ws = websocket.create_connection(
                    self.server_url,
                    timeout=self.test_configs['response_time']['timeout']
                )
                
                # 发送测试音频
                test_audio = self.test_audio_samples['rms_0.05']  # 使用标准质量音频
                ws.send(json.dumps({
                    'type': 'audio_chunk',
                    'data': test_audio,
                    'sample_rate': 16000
                }))
                
                # 等待响应
                response = ws.recv()
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                response_times.append(response_time)
                success_count += 1
                
                ws.close()
                
                self.test_logger.debug(f"响应时间测试 {i+1}/{self.test_configs['response_time']['sample_count']}: {response_time:.2f}ms")
                
            except Exception as e:
                error_count += 1
                self.results['error_logs'].append({
                    'test': 'response_time',
                    'error': str(e),
                    'timestamp': time.time()
                })
                self.test_logger.error(f"响应时间测试失败: {e}")
        
        # 计算统计指标
        if response_times:
            metrics = {
                'mean_ms': statistics.mean(response_times),
                'median_ms': statistics.median(response_times),
                'min_ms': min(response_times),
                'max_ms': max(response_times),
                'std_dev_ms': statistics.stdev(response_times) if len(response_times) > 1 else 0,
                'p95_ms': np.percentile(response_times, 95),
                'p99_ms': np.percentile(response_times, 99),
                'success_rate': (success_count / (success_count + error_count)) * 100
            }
        else:
            metrics = {'error': 'No successful responses'}
        
        self.test_logger.success(f"✅ 响应时间测试完成: 平均{metrics.get('mean_ms', 0):.2f}ms")
        return metrics
    
    async def test_concurrency(self) -> Dict[str, Any]:
        """并发连接测试"""
        self.test_logger.info("🔀 开始并发连接测试...")
        
        max_connections = self.test_configs['concurrency']['max_connections']
        test_duration = self.test_configs['concurrency']['test_duration']
        
        connections = []
        connection_times = []
        active_connections = 0
        max_active = 0
        errors = 0
        
        async def create_connection():
            nonlocal active_connections, max_active, errors
            try:
                start = time.time()
                ws = websocket.create_connection(self.server_url, timeout=5.0)
                connection_time = (time.time() - start) * 1000
                
                active_connections += 1
                max_active = max(max_active, active_connections)
                connection_times.append(connection_time)
                
                # 保持连接一段时间
                await asyncio.sleep(test_duration / max_connections)
                
                ws.close()
                active_connections -= 1
                
            except Exception as e:
                errors += 1
                self.results['error_logs'].append({
                    'test': 'concurrency',
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        # 并发创建连接
        tasks = [create_connection() for _ in range(max_connections)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics = {
            'max_connections_attempted': max_connections,
            'max_active_connections': max_active,
            'successful_connections': len(connection_times),
            'failed_connections': errors,
            'avg_connection_time_ms': statistics.mean(connection_times) if connection_times else 0,
            'connection_success_rate': (len(connection_times) / max_connections) * 100
        }
        
        self.test_logger.success(f"✅ 并发测试完成: 最大{max_active}个连接，成功率{metrics['connection_success_rate']:.1f}%")
        return metrics
    
    async def test_audio_quality_adaptation(self) -> Dict[str, Any]:
        """音频质量适应性测试"""
        self.test_logger.info("🎵 开始音频质量适应性测试...")
        
        quality_results = {}
        
        for audio_name, audio_data in self.test_audio_samples.items():
            try:
                start_time = time.time()
                
                ws = websocket.create_connection(self.server_url, timeout=5.0)
                
                # 发送不同质量的音频
                ws.send(json.dumps({
                    'type': 'audio_chunk',
                    'data': audio_data,
                    'sample_rate': 16000
                }))
                
                # 等待响应
                response = ws.recv()
                response_time = (time.time() - start_time) * 1000
                
                # 解析响应
                try:
                    response_data = json.loads(response)
                    recognition_result = response_data.get('text', '')
                except:
                    recognition_result = ''
                
                quality_results[audio_name] = {
                    'response_time_ms': response_time,
                    'has_result': bool(recognition_result),
                    'result_length': len(recognition_result),
                    'response_data': response
                }
                
                ws.close()
                
                self.test_logger.debug(f"音频质量测试 [{audio_name}]: {response_time:.2f}ms, 结果: {'有' if recognition_result else '无'}")
                
            except Exception as e:
                quality_results[audio_name] = {
                    'error': str(e),
                    'response_time_ms': 0,
                    'has_result': False
                }
                self.results['error_logs'].append({
                    'test': f'audio_quality_{audio_name}',
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        # 计算适应性指标
        successful_tests = sum(1 for result in quality_results.values() 
                             if 'error' not in result)
        adaptation_score = (successful_tests / len(quality_results)) * 100
        
        metrics = {
            'quality_test_results': quality_results,
            'adaptation_score': adaptation_score,
            'tests_passed': successful_tests,
            'total_tests': len(quality_results)
        }
        
        self.test_logger.success(f"✅ 音频质量适应性测试完成: 适应性评分{adaptation_score:.1f}%")
        return metrics
    
    async def test_memory_usage(self) -> Dict[str, Any]:
        """内存使用测试"""
        self.test_logger.info("💾 开始内存使用测试...")
        
        try:
            import psutil
            
            # 获取初始内存状态
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行大量识别请求
            request_count = 100
            memory_samples = []
            
            for i in range(request_count):
                try:
                    ws = websocket.create_connection(self.server_url, timeout=3.0)
                    test_audio = self.test_audio_samples['rms_0.05']
                    
                    ws.send(json.dumps({
                        'type': 'audio_chunk',
                        'data': test_audio,
                        'sample_rate': 16000
                    }))
                    
                    ws.recv()  # 接收响应
                    ws.close()
                    
                    # 每10次请求记录一次内存使用
                    if i % 10 == 0:
                        current_memory = process.memory_info().rss / 1024 / 1024
                        memory_samples.append(current_memory)
                    
                except Exception as e:
                    self.results['error_logs'].append({
                        'test': f'memory_usage_request_{i}',
                        'error': str(e),
                        'timestamp': time.time()
                    })
            
            final_memory = process.memory_info().rss / 1024 / 1024
            
            metrics = {
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_increase_mb': final_memory - initial_memory,
                'peak_memory_mb': max(memory_samples) if memory_samples else final_memory,
                'avg_memory_mb': statistics.mean(memory_samples) if memory_samples else final_memory,
                'memory_samples': memory_samples,
                'requests_completed': request_count
            }
            
            self.test_logger.success(f"✅ 内存测试完成: 增长{metrics['memory_increase_mb']:.2f}MB")
            return metrics
            
        except ImportError:
            self.test_logger.warning("⚠️ psutil未安装，跳过内存测试")
            return {'error': 'psutil not available'}
    
    async def test_error_recovery(self) -> Dict[str, Any]:
        """错误恢复测试"""
        self.test_logger.info("🛡️ 开始错误恢复测试...")
        
        recovery_tests = {
            'invalid_audio_format': {'data': 'invalid_base64_data'},
            'empty_audio': {'data': ''},
            'malformed_json': 'not_json',
            'missing_fields': {'type': 'audio_chunk'}  # 缺少data字段
        }
        
        recovery_results = {}
        
        for test_name, test_data in recovery_tests.items():
            try:
                ws = websocket.create_connection(self.server_url, timeout=3.0)
                
                # 发送错误数据
                if isinstance(test_data, str):
                    ws.send(test_data)
                else:
                    ws.send(json.dumps(test_data))
                
                # 尝试接收响应
                try:
                    response = ws.recv()
                    recovery_results[test_name] = {
                        'recovered': True,
                        'response': response
                    }
                except:
                    recovery_results[test_name] = {
                        'recovered': False,
                        'response': None
                    }
                
                ws.close()
                
                # 测试连接是否仍然可用
                try:
                    ws2 = websocket.create_connection(self.server_url, timeout=3.0)
                    test_audio = self.test_audio_samples['rms_0.05']
                    ws2.send(json.dumps({
                        'type': 'audio_chunk',
                        'data': test_audio,
                        'sample_rate': 16000
                    }))
                    ws2.recv()
                    ws2.close()
                    recovery_results[test_name]['connection_stable'] = True
                except:
                    recovery_results[test_name]['connection_stable'] = False
                
            except Exception as e:
                recovery_results[test_name] = {
                    'error': str(e),
                    'recovered': False,
                    'connection_stable': False
                }
        
        # 计算恢复评分
        stable_connections = sum(1 for result in recovery_results.values() 
                               if result.get('connection_stable', False))
        recovery_score = (stable_connections / len(recovery_tests)) * 100
        
        metrics = {
            'recovery_test_results': recovery_results,
            'recovery_score': recovery_score,
            'stable_connections': stable_connections,
            'total_tests': len(recovery_tests)
        }
        
        self.test_logger.success(f"✅ 错误恢复测试完成: 恢复评分{recovery_score:.1f}%")
        return metrics
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有性能测试"""
        self.test_logger.info("🧪 开始全面性能测试...")
        self.results['start_time'] = datetime.now().isoformat()
        
        # 执行所有测试
        test_methods = [
            ('response_time', self.test_response_time),
            ('audio_quality_adaptation', self.test_audio_quality_adaptation),
            ('error_recovery', self.test_error_recovery),
            ('memory_usage', self.test_memory_usage),
            ('concurrency', self.test_concurrency)
        ]
        
        for test_name, test_method in test_methods:
            try:
                self.test_logger.info(f"📊 执行测试: {test_name}")
                result = await test_method()
                self.results['performance_metrics'][test_name] = result
                self.results['tests_completed'][test_name] = True
            except Exception as e:
                self.test_logger.error(f"❌ 测试失败 [{test_name}]: {e}")
                self.results['performance_metrics'][test_name] = {'error': str(e)}
                self.results['tests_completed'][test_name] = False
                self.results['error_logs'].append({
                    'test': test_name,
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        self.results['end_time'] = datetime.now().isoformat()
        
        # 生成总体评分
        overall_score = self._calculate_overall_score()
        self.results['overall_score'] = overall_score
        
        self.test_logger.success(f"🎯 性能测试完成! 总体评分: {overall_score:.1f}/100")
        return self.results
    
    def _calculate_overall_score(self) -> float:
        """计算总体性能评分"""
        scores = []
        weights = {
            'response_time': 0.3,
            'audio_quality_adaptation': 0.25,
            'error_recovery': 0.2,
            'concurrency': 0.15,
            'memory_usage': 0.1
        }
        
        for test_name, weight in weights.items():
            if test_name in self.results['performance_metrics']:
                metrics = self.results['performance_metrics'][test_name]
                if 'error' in metrics:
                    score = 0
                else:
                    score = self._score_test_result(test_name, metrics)
                scores.append(score * weight)
        
        return sum(scores)
    
    def _score_test_result(self, test_name: str, metrics: Dict[str, Any]) -> float:
        """为单个测试结果评分（0-100）"""
        if test_name == 'response_time':
            # 响应时间评分：<100ms=100分，>1000ms=0分
            avg_time = metrics.get('mean_ms', 1000)
            return max(0, min(100, 100 - (avg_time - 100) / 10))
        
        elif test_name == 'audio_quality_adaptation':
            return metrics.get('adaptation_score', 0)
        
        elif test_name == 'error_recovery':
            return metrics.get('recovery_score', 0)
        
        elif test_name == 'concurrency':
            success_rate = metrics.get('connection_success_rate', 0)
            return success_rate
        
        elif test_name == 'memory_usage':
            # 内存评分：增长<50MB=100分，>200MB=0分
            memory_increase = metrics.get('memory_increase_mb', 200)
            return max(0, min(100, 100 - (memory_increase - 50) / 1.5))
        
        return 0
    
    def save_results(self, filepath: Optional[str] = None) -> str:
        """保存测试结果"""
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'performance_test_results_{timestamp}.json'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        self.test_logger.info(f"📊 测试结果已保存: {filepath}")
        return filepath
    
    def generate_report(self) -> str:
        """生成性能测试报告"""
        if not self.results.get('performance_metrics'):
            return "❌ 没有可用的测试结果"
        
        report = [
            "🧪 实时语音识别系统 - 性能测试报告",
            "=" * 50,
            f"测试时间: {self.results['start_time']} ~ {self.results['end_time']}",
            f"总体评分: {self.results.get('overall_score', 0):.1f}/100",
            "",
            "📊 详细测试结果:",
            "-" * 30
        ]
        
        # 响应时间测试
        if 'response_time' in self.results['performance_metrics']:
            rt_metrics = self.results['performance_metrics']['response_time']
            if 'error' not in rt_metrics:
                report.extend([
                    f"⚡ 响应时间测试:",
                    f"  平均响应时间: {rt_metrics['mean_ms']:.2f}ms",
                    f"  95%分位数: {rt_metrics['p95_ms']:.2f}ms",
                    f"  成功率: {rt_metrics['success_rate']:.1f}%",
                    ""
                ])
        
        # 音频质量适应性
        if 'audio_quality_adaptation' in self.results['performance_metrics']:
            aq_metrics = self.results['performance_metrics']['audio_quality_adaptation']
            if 'error' not in aq_metrics:
                report.extend([
                    f"🎵 音频质量适应性测试:",
                    f"  适应性评分: {aq_metrics['adaptation_score']:.1f}%",
                    f"  通过测试: {aq_metrics['tests_passed']}/{aq_metrics['total_tests']}",
                    ""
                ])
        
        # 并发性能
        if 'concurrency' in self.results['performance_metrics']:
            conc_metrics = self.results['performance_metrics']['concurrency']
            if 'error' not in conc_metrics:
                report.extend([
                    f"🔀 并发性能测试:",
                    f"  最大并发连接: {conc_metrics['max_active_connections']}",
                    f"  连接成功率: {conc_metrics['connection_success_rate']:.1f}%",
                    ""
                ])
        
        # 错误恢复
        if 'error_recovery' in self.results['performance_metrics']:
            er_metrics = self.results['performance_metrics']['error_recovery']
            if 'error' not in er_metrics:
                report.extend([
                    f"🛡️ 错误恢复测试:",
                    f"  恢复能力评分: {er_metrics['recovery_score']:.1f}%",
                    f"  稳定连接: {er_metrics['stable_connections']}/{er_metrics['total_tests']}",
                    ""
                ])
        
        # 内存使用
        if 'memory_usage' in self.results['performance_metrics']:
            mem_metrics = self.results['performance_metrics']['memory_usage']
            if 'error' not in mem_metrics:
                report.extend([
                    f"💾 内存使用测试:",
                    f"  内存增长: {mem_metrics['memory_increase_mb']:.2f}MB",
                    f"  峰值内存: {mem_metrics['peak_memory_mb']:.2f}MB",
                    ""
                ])
        
        # 错误总结
        if self.results['error_logs']:
            report.extend([
                f"❌ 测试过程中的错误 ({len(self.results['error_logs'])}个):",
                "-" * 20
            ])
            for error in self.results['error_logs'][-5:]:  # 只显示最近5个错误
                report.append(f"  [{error['test']}] {error['error']}")
        
        return "\n".join(report)

async def main():
    """主测试函数"""
    # 配置日志
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
    logger.add("performance_test.log", level="DEBUG")
    
    # 创建测试器
    tester = PerformanceTester("ws://localhost:8210")
    
    try:
        # 运行所有测试
        results = await tester.run_all_tests()
        
        # 保存结果
        result_file = tester.save_results()
        
        # 生成报告
        report = tester.generate_report()
        print("\n" + report)
        
        # 保存报告
        report_file = result_file.replace('.json', '_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📊 完整结果: {result_file}")
        print(f"📋 测试报告: {report_file}")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        logger.error(f"测试异常: {e}")

if __name__ == "__main__":
    asyncio.run(main())
