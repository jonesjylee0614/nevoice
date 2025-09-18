"""
系统监控模块 - 实时语音识别系统健康检查
"""
import os
import time
import json
import psutil
import threading
from datetime import datetime, timedelta
from collections import deque, defaultdict
from loguru import logger
from typing import Dict, List, Optional, Any
import torch

class SystemMonitor:
    """
    实时语音识别系统监控器
    
    监控内容：
    1. 系统资源（CPU, 内存, GPU）
    2. 识别性能指标
    3. WebSocket连接状态
    4. ModelScope模型状态
    5. 音频质量统计
    6. 错误率和延迟
    """
    
    def __init__(self, log_interval=30):
        self.monitor_logger = logger.bind(component="system_monitor")
        self.log_interval = log_interval
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 历史数据存储（最近1小时）
        self.history_size = 120  # 30秒间隔 * 120 = 1小时
        self.metrics_history = defaultdict(lambda: deque(maxlen=self.history_size))
        
        # 性能阈值配置
        self.thresholds = {
            'cpu_percent': 80.0,          # CPU使用率阈值
            'memory_percent': 85.0,       # 内存使用率阈值
            'gpu_memory_percent': 90.0,   # GPU内存使用率阈值
            'recognition_delay_ms': 1000, # 识别延迟阈值(ms)
            'error_rate_percent': 5.0,    # 错误率阈值(%)
            'connection_count': 100       # 最大连接数
        }
        
        # 当前统计
        self.current_stats = {
            'start_time': time.time(),
            'total_connections': 0,
            'active_connections': 0,
            'total_recognitions': 0,
            'successful_recognitions': 0,
            'failed_recognitions': 0,
            'avg_recognition_time': 0.0,
            'avg_audio_rms': 0.0,
            'last_health_check': time.time()
        }
        
        # 错误统计
        self.error_stats = defaultdict(int)
        self.error_history = deque(maxlen=1000)  # 最近1000个错误
        
        self.monitor_logger.info("🔍 系统监控器初始化完成")
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            self.monitor_logger.warning("⚠️ 监控已在运行")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.monitor_logger.success("🚀 系统监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.monitor_logger.info("⏹️ 系统监控已停止")
    
    def _monitoring_loop(self):
        """监控主循环"""
        while self.is_monitoring:
            try:
                # 收集系统指标
                system_metrics = self._collect_system_metrics()
                performance_metrics = self._collect_performance_metrics()
                model_metrics = self._collect_model_metrics()
                
                # 合并所有指标
                all_metrics = {
                    'timestamp': time.time(),
                    'datetime': datetime.now().isoformat(),
                    **system_metrics,
                    **performance_metrics,
                    **model_metrics
                }
                
                # 存储历史数据
                for key, value in all_metrics.items():
                    if isinstance(value, (int, float)):
                        self.metrics_history[key].append(value)
                
                # 健康检查
                health_status = self._health_check(all_metrics)
                
                # 记录监控日志
                self._log_metrics(all_metrics, health_status)
                
                # 检查警告
                try:
                    self._check_alerts(all_metrics)
                except Exception as _:
                    pass
                
                time.sleep(self.log_interval)
                
            except Exception as e:
                self.monitor_logger.error(f"❌ 监控循环异常: {e}")
                time.sleep(10)  # 异常时降低频率
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统资源指标（GPU失败不影响CPU/内存采集）"""
        metrics: Dict[str, Any] = {}

        # CPU 和内存、磁盘
        try:
            metrics['cpu_percent'] = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            metrics['memory_percent'] = memory.percent
            metrics['memory_available_mb'] = memory.available // (1024 * 1024)
            disk = psutil.disk_usage('/')
            metrics['disk_percent'] = disk.percent
            metrics['disk_free_gb'] = disk.free // (1024 * 1024 * 1024)
        except Exception as e:
            self.monitor_logger.error(f"❌ 系统基础指标收集失败: {e}")

        # GPU（可选）
        try:
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                for i in range(gpu_count):
                    # 设备信息
                    try:
                        props = torch.cuda.get_device_properties(i)
                        metrics[f'gpu_{i}_name'] = getattr(props, 'name', f'cuda:{i}')
                        total_mem_mb = getattr(props, 'total_memory', 0) // (1024 * 1024)
                        metrics[f'gpu_{i}_memory_total_mb'] = total_mem_mb
                    except Exception:
                        pass

                    # 显存使用
                    try:
                        allocated = torch.cuda.memory_allocated(i) // (1024 * 1024)
                        reserved = torch.cuda.memory_reserved(i) // (1024 * 1024)
                    except Exception:
                        # 兼容老版本API
                        try:
                            stats = torch.cuda.memory_stats(i)
                            allocated = stats.get('allocated_bytes.all.current', 0) // (1024 * 1024)
                            reserved = stats.get('reserved_bytes.all.current', 0) // (1024 * 1024)
                        except Exception:
                            allocated = 0
                            reserved = 0

                    metrics[f'gpu_{i}_memory_allocated_mb'] = allocated
                    metrics[f'gpu_{i}_memory_reserved_mb'] = reserved

                    # 利用率（如不可用则默认0，不强依赖pynvml）
                    metrics[f'gpu_{i}_utilization'] = 0
        except Exception as e:
            # 仅记录调试信息，不影响整体
            self.monitor_logger.debug(f"GPU指标采集失败（可忽略）: {e}")

        return metrics
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """收集性能指标"""
        uptime = time.time() - self.current_stats['start_time']
        
        # 计算成功率
        total_recognitions = self.current_stats['total_recognitions']
        success_rate = (self.current_stats['successful_recognitions'] / max(total_recognitions, 1)) * 100
        error_rate = (self.current_stats['failed_recognitions'] / max(total_recognitions, 1)) * 100
        
        # 计算每分钟识别次数
        recognitions_per_minute = (total_recognitions / max(uptime/60, 1))
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'total_recognitions': total_recognitions,
            'success_rate_percent': success_rate,
            'error_rate_percent': error_rate,
            'recognitions_per_minute': recognitions_per_minute,
            'avg_recognition_time_ms': self.current_stats['avg_recognition_time'],
            'active_connections': self.current_stats['active_connections'],
            'avg_audio_rms': self.current_stats['avg_audio_rms']
        }
    
    def _collect_model_metrics(self) -> Dict[str, Any]:
        """收集模型相关指标（使用绝对导入，避免相对导入报错）"""
        try:
            from speech_recognition.vocabulary_manager import vocab_manager  # type: ignore
            vocab_stats = vocab_manager.get_stats()
            return {
                'vocab_mode': vocab_stats.get('current_mode', 'unknown'),
                'vocab_load_time': vocab_stats.get('load_time', 0),
                'vocab_memory_mb': vocab_stats.get('memory_usage_mb', 0)
            }
        except ImportError:
            # 词汇模块不可用时，返回默认值，避免错误级别日志
            self.monitor_logger.warning("📚 词汇模块未加载，跳过模型指标收集")
            return {'vocab_mode': 'unknown'}
        except Exception as e:
            self.monitor_logger.warning(f"⚠️ 模型指标收集失败: {e}")
            return {}
    
    def _health_check(self, metrics: Dict[str, Any]) -> str:
        """系统健康检查"""
        issues = []
        
        # CPU检查
        if metrics.get('cpu_percent', 0) > self.thresholds['cpu_percent']:
            issues.append(f"CPU使用率过高: {metrics['cpu_percent']:.1f}%")
        
        # 内存检查
        if metrics.get('memory_percent', 0) > self.thresholds['memory_percent']:
            issues.append(f"内存使用率过高: {metrics['memory_percent']:.1f}%")
        
        # 错误率检查
        if metrics.get('error_rate_percent', 0) > self.thresholds['error_rate_percent']:
            issues.append(f"识别错误率过高: {metrics['error_rate_percent']:.1f}%")
        
        # 响应时间检查
        if metrics.get('avg_recognition_time_ms', 0) > self.thresholds['recognition_delay_ms']:
            issues.append(f"识别延迟过高: {metrics['avg_recognition_time_ms']:.1f}ms")
        
        # GPU内存检查
        for key, value in metrics.items():
            if key.startswith('gpu_') and key.endswith('_memory_allocated_mb'):
                gpu_id = key.split('_')[1]
                reserved_key = f'gpu_{gpu_id}_memory_reserved_mb'
                if reserved_key in metrics:
                    usage_percent = (value / max(metrics[reserved_key], 1)) * 100
                    if usage_percent > self.thresholds['gpu_memory_percent']:
                        issues.append(f"GPU{gpu_id}内存使用率过高: {usage_percent:.1f}%")
        
        if not issues:
            return "HEALTHY"
        elif len(issues) <= 2:
            return "WARNING"
        else:
            return "CRITICAL"
    
    def _log_metrics(self, metrics: Dict[str, Any], health_status: str):
        """记录监控指标"""
        status_emoji = {"HEALTHY": "✅", "WARNING": "⚠️", "CRITICAL": "🚨"}.get(health_status, "❓")
        
        log_msg = (
            f"{status_emoji} 系统监控报告 [{health_status}]\n"
            f"⏱️  运行时间: {metrics.get('uptime_hours', 0):.1f}小时\n"
            f"🖥️  CPU: {metrics.get('cpu_percent', 0):.1f}% | 内存: {metrics.get('memory_percent', 0):.1f}%\n"
            f"🎯  识别成功率: {metrics.get('success_rate_percent', 0):.1f}% ({metrics.get('total_recognitions', 0)}次)\n"
            f"⚡  平均延迟: {metrics.get('avg_recognition_time_ms', 0):.1f}ms\n"
            f"🔊  音频质量: RMS={metrics.get('avg_audio_rms', 0):.4f}\n"
            f"🌐  活跃连接: {metrics.get('active_connections', 0)}个\n"
            f"📚  词汇模式: {metrics.get('vocab_mode', 'unknown')}"
        )
        
        if health_status == "HEALTHY":
            self.monitor_logger.info(log_msg)
        elif health_status == "WARNING":
            self.monitor_logger.warning(log_msg)
        else:
            self.monitor_logger.error(log_msg)
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """检查告警条件"""
        # 这里可以实现具体的告警逻辑
        # 比如发送邮件、Webhook通知等
        pass
    
    def record_recognition(self, success: bool, duration_ms: float, audio_rms: float = 0.0):
        """记录识别结果"""
        self.current_stats['total_recognitions'] += 1
        
        if success:
            self.current_stats['successful_recognitions'] += 1
        else:
            self.current_stats['failed_recognitions'] += 1
        
        # 更新平均值
        total = self.current_stats['total_recognitions']
        self.current_stats['avg_recognition_time'] = (
            (self.current_stats['avg_recognition_time'] * (total-1) + duration_ms) / total
        )
        
        if audio_rms > 0:
            self.current_stats['avg_audio_rms'] = (
                (self.current_stats['avg_audio_rms'] * (total-1) + audio_rms) / total
            )
    
    def record_connection(self, connected: bool):
        """记录连接变化"""
        if connected:
            self.current_stats['total_connections'] += 1
            self.current_stats['active_connections'] += 1
        else:
            self.current_stats['active_connections'] = max(0, self.current_stats['active_connections'] - 1)
    
    def record_error(self, error_type: str, error_msg: str):
        """记录错误"""
        self.error_stats[error_type] += 1
        self.error_history.append({
            'timestamp': time.time(),
            'type': error_type,
            'message': error_msg
        })
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取监控面板数据"""
        recent_metrics = {}
        for key, history in self.metrics_history.items():
            if history:
                recent_metrics[key] = {
                    'current': history[-1],
                    'avg_5min': sum(list(history)[-10:]) / min(len(history), 10),
                    'max_1hour': max(history),
                    'min_1hour': min(history)
                }
        
        return {
            'current_stats': self.current_stats,
            'recent_metrics': recent_metrics,
            'error_stats': dict(self.error_stats),
            'thresholds': self.thresholds,
            'history_length': len(next(iter(self.metrics_history.values()), [])),
            'last_updated': datetime.now().isoformat()
        }
    
    def export_metrics(self, filepath: str = None):
        """导出监控数据"""
        if filepath is None:
            filepath = f"monitoring_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'dashboard_data': self.get_dashboard_data(),
            'metrics_history': {k: list(v) for k, v in self.metrics_history.items()},
            'error_history': list(self.error_history)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.monitor_logger.info(f"📊 监控数据已导出: {filepath}")
        return filepath

# 全局监控器实例
system_monitor = SystemMonitor()

def start_system_monitoring():
    """启动系统监控"""
    system_monitor.start_monitoring()

def stop_system_monitoring():
    """停止系统监控"""
    system_monitor.stop_monitoring()

if __name__ == "__main__":
    # 测试监控系统
    monitor = SystemMonitor(log_interval=5)
    monitor.start_monitoring()
    
    try:
        # 模拟一些操作
        import random
        time.sleep(2)
        
        for i in range(10):
            # 模拟识别记录
            success = random.random() > 0.1  # 90%成功率
            duration = random.uniform(20, 100)  # 20-100ms
            rms = random.uniform(0.01, 0.05)
            monitor.record_recognition(success, duration, rms)
            
            # 模拟连接
            if random.random() > 0.8:
                monitor.record_connection(True)
            
            time.sleep(1)
        
        # 导出数据
        monitor.export_metrics()
        
        # 显示面板数据
        dashboard = monitor.get_dashboard_data()
        print(json.dumps(dashboard, indent=2, ensure_ascii=False))
        
    finally:
        monitor.stop_monitoring()
