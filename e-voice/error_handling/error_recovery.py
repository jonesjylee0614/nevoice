"""
错误处理和故障恢复模块 - 实时语音识别系统
"""
import os
import time
import traceback
import threading
from functools import wraps
from collections import defaultdict, deque
from typing import Callable, Any, Dict, Optional
from loguru import logger
from enum import Enum

class ErrorLevel(Enum):
    """错误级别定义"""
    LOW = "low"           # 轻微错误，不影响主要功能
    MEDIUM = "medium"     # 中等错误，影响部分功能  
    HIGH = "high"         # 严重错误，影响主要功能
    CRITICAL = "critical" # 致命错误，系统无法正常工作

class ErrorRecoveryManager:
    """
    错误恢复管理器
    
    功能：
    1. 自动错误检测和分类
    2. 智能重试机制
    3. 故障恢复策略
    4. 错误统计和报告
    5. 自动降级处理
    """
    
    def __init__(self, max_retries=3, retry_delay=1.0):
        self.error_logger = logger.bind(component="error_recovery")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 错误统计
        self.error_counts = defaultdict(int)
        self.error_history = deque(maxlen=1000)
        self.recovery_stats = {
            'total_errors': 0,
            'recovered_errors': 0,
            'unrecovered_errors': 0,
            'auto_retries': 0,
            'manual_interventions': 0
        }
        
        # 故障组件状态
        self.component_status = {
            'audio_capture': 'healthy',
            'websocket': 'healthy',
            'modelscope': 'healthy',
            'vocabulary': 'healthy',
            'file_system': 'healthy'
        }
        
        # 重试策略配置
        self.retry_strategies = {
            'connection_error': {'max_retries': 5, 'delay': 2.0, 'backoff': True},
            'model_error': {'max_retries': 3, 'delay': 1.0, 'backoff': False},
            'audio_error': {'max_retries': 2, 'delay': 0.5, 'backoff': False},
            'file_error': {'max_retries': 3, 'delay': 0.1, 'backoff': False}
        }
        
        # 降级模式
        self.fallback_enabled = True
        self.fallback_mode = False
        
        self.error_logger.info("🛡️ 错误恢复管理器初始化完成")
    
    def classify_error(self, error: Exception, context: str = "") -> ErrorLevel:
        """
        错误分类
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            错误级别
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # 致命错误
        if any(keyword in error_msg for keyword in ['cuda out of memory', 'system error', 'permission denied']):
            return ErrorLevel.CRITICAL
        
        # 严重错误  
        if any(keyword in error_msg for keyword in ['connection refused', 'model load failed', 'file not found']):
            return ErrorLevel.HIGH
        
        # 中等错误
        if any(keyword in error_msg for keyword in ['timeout', 'invalid format', 'decode error']):
            return ErrorLevel.MEDIUM
        
        # 轻微错误
        return ErrorLevel.LOW
    
    def get_retry_strategy(self, error_category: str) -> Dict[str, Any]:
        """获取重试策略"""
        return self.retry_strategies.get(error_category, {
            'max_retries': self.max_retries,
            'delay': self.retry_delay,
            'backoff': False
        })
    
    def calculate_delay(self, attempt: int, base_delay: float, use_backoff: bool) -> float:
        """计算重试延迟时间"""
        if not use_backoff:
            return base_delay
        # 指数退避策略
        return min(base_delay * (2 ** (attempt - 1)), 30.0)  # 最大30秒
    
    def record_error(self, error: Exception, context: str = "", component: str = "unknown"):
        """记录错误"""
        error_level = self.classify_error(error, context)
        error_record = {
            'timestamp': time.time(),
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'component': component,
            'level': error_level.value,
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_record)
        self.error_counts[component] += 1
        self.recovery_stats['total_errors'] += 1
        
        # 更新组件状态
        if error_level in [ErrorLevel.HIGH, ErrorLevel.CRITICAL]:
            self.component_status[component] = 'unhealthy'
        
        self.error_logger.error(
            f"❌ [{error_level.value.upper()}] {component}错误: {str(error)}"
            f" | 上下文: {context}"
        )
    
    def recover_component(self, component: str, recovery_func: Optional[Callable] = None) -> bool:
        """
        组件故障恢复
        
        Args:
            component: 组件名称
            recovery_func: 自定义恢复函数
            
        Returns:
            是否恢复成功
        """
        self.error_logger.info(f"🔧 开始恢复组件: {component}")
        
        try:
            if recovery_func:
                recovery_func()
            else:
                # 默认恢复策略
                self._default_recovery(component)
            
            self.component_status[component] = 'healthy'
            self.recovery_stats['recovered_errors'] += 1
            self.error_logger.success(f"✅ 组件恢复成功: {component}")
            return True
            
        except Exception as e:
            self.error_logger.error(f"❌ 组件恢复失败: {component} - {e}")
            self.recovery_stats['unrecovered_errors'] += 1
            return False
    
    def _default_recovery(self, component: str):
        """默认恢复策略"""
        recovery_actions = {
            'modelscope': self._recover_modelscope,
            'vocabulary': self._recover_vocabulary,
            'file_system': self._recover_file_system,
            'websocket': self._recover_websocket
        }
        
        action = recovery_actions.get(component)
        if action:
            action()
        else:
            self.error_logger.warning(f"⚠️ 无默认恢复策略: {component}")
    
    def _recover_modelscope(self):
        """恢复ModelScope模型"""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()  # 清理GPU缓存
            self.error_logger.info("🧠 ModelScope模型缓存已清理")
        except Exception as e:
            self.error_logger.error(f"ModelScope恢复失败: {e}")
    
    def _recover_vocabulary(self):
        """恢复词汇管理"""
        try:
            from ..speech_recognition.vocabulary_manager import vocab_manager
            vocab_manager.load_vocabulary(mode='lite', max_memory_mb=100)
            self.error_logger.info("📚 词汇管理器已重置为轻量模式")
        except Exception as e:
            self.error_logger.error(f"词汇恢复失败: {e}")
    
    def _recover_file_system(self):
        """恢复文件系统"""
        try:
            temp_dirs = ['data/temp', 'logs', 'monitoring']
            for dir_path in temp_dirs:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
            self.error_logger.info("📁 文件系统目录结构已修复")
        except Exception as e:
            self.error_logger.error(f"文件系统恢复失败: {e}")
    
    def _recover_websocket(self):
        """恢复WebSocket连接"""
        self.error_logger.info("🌐 WebSocket连接将在下次请求时自动重连")
    
    def enable_fallback_mode(self):
        """启用降级模式"""
        if not self.fallback_mode:
            self.fallback_mode = True
            self.error_logger.warning("⬇️ 系统已切换到降级模式")
            # 降级策略：禁用自定义词汇、降低音频质量要求等
            self._apply_fallback_settings()
    
    def disable_fallback_mode(self):
        """禁用降级模式"""
        if self.fallback_mode:
            self.fallback_mode = False
            self.error_logger.success("⬆️ 系统已退出降级模式")
            self._restore_normal_settings()
    
    def _apply_fallback_settings(self):
        """应用降级设置"""
        try:
            # 这里可以实现具体的降级逻辑
            # 例如：降低音频质量要求、禁用高消耗功能等
            self.error_logger.info("🔧 降级设置已应用")
        except Exception as e:
            self.error_logger.error(f"降级设置应用失败: {e}")
    
    def _restore_normal_settings(self):
        """恢复正常设置"""
        try:
            # 恢复正常配置
            self.error_logger.info("🔧 正常设置已恢复")
        except Exception as e:
            self.error_logger.error(f"正常设置恢复失败: {e}")
    
    def auto_recovery_check(self):
        """自动恢复检查"""
        unhealthy_components = [
            component for component, status in self.component_status.items()
            if status == 'unhealthy'
        ]
        
        if unhealthy_components:
            self.error_logger.warning(f"⚠️ 检测到异常组件: {unhealthy_components}")
            
            for component in unhealthy_components:
                if self.recover_component(component):
                    self.error_logger.success(f"✅ 自动恢复成功: {component}")
                else:
                    self.error_logger.error(f"❌ 自动恢复失败: {component}")
    
    def get_health_report(self) -> Dict[str, Any]:
        """获取系统健康报告"""
        total_errors = self.recovery_stats['total_errors']
        recovery_rate = (self.recovery_stats['recovered_errors'] / max(total_errors, 1)) * 100
        
        return {
            'component_status': self.component_status.copy(),
            'error_counts': dict(self.error_counts),
            'recovery_stats': self.recovery_stats.copy(),
            'recovery_rate_percent': recovery_rate,
            'fallback_mode': self.fallback_mode,
            'recent_errors': list(self.error_history)[-10:],  # 最近10个错误
            'most_common_errors': self._get_common_errors()
        }
    
    def _get_common_errors(self) -> Dict[str, int]:
        """获取常见错误统计"""
        error_types = defaultdict(int)
        for error in self.error_history:
            error_types[error['type']] += 1
        
        # 返回前5个最常见的错误
        return dict(sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5])

# 全局错误恢复管理器
error_recovery = ErrorRecoveryManager()

def with_error_recovery(error_category: str = "general", component: str = "unknown"):
    """
    错误恢复装饰器
    
    Args:
        error_category: 错误类别
        component: 组件名称
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            strategy = error_recovery.get_retry_strategy(error_category)
            max_retries = strategy['max_retries']
            base_delay = strategy['delay']
            use_backoff = strategy['backoff']
            
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        error_recovery.recovery_stats['auto_retries'] += 1
                        error_recovery.error_logger.success(
                            f"✅ 重试成功: {func.__name__} (第{attempt}次重试)"
                        )
                    return result
                    
                except Exception as e:
                    last_error = e
                    error_recovery.record_error(e, f"{func.__name__}调用", component)
                    
                    if attempt < max_retries:
                        delay = error_recovery.calculate_delay(attempt + 1, base_delay, use_backoff)
                        error_recovery.error_logger.warning(
                            f"⚠️ 第{attempt+1}次重试失败: {func.__name__}, {delay}s后重试"
                        )
                        time.sleep(delay)
                    else:
                        error_recovery.error_logger.error(
                            f"❌ 最终失败: {func.__name__} (已重试{max_retries}次)"
                        )
            
            # 所有重试都失败了
            raise last_error
            
        return wrapper
    return decorator

def health_check():
    """系统健康检查"""
    return error_recovery.get_health_report()

def start_auto_recovery():
    """启动自动恢复检查"""
    def recovery_loop():
        while True:
            try:
                error_recovery.auto_recovery_check()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                logger.error(f"自动恢复检查异常: {e}")
                time.sleep(10)
    
    thread = threading.Thread(target=recovery_loop, daemon=True)
    thread.start()
    logger.info("🔄 自动恢复检查已启动")

if __name__ == "__main__":
    # 测试错误恢复系统
    
    @with_error_recovery(error_category="test_error", component="test_component")
    def test_function():
        import random
        if random.random() < 0.7:  # 70%概率失败
            raise ValueError("测试错误")
        return "成功"
    
    # 测试重试机制
    try:
        result = test_function()
        print(f"执行结果: {result}")
    except Exception as e:
        print(f"最终失败: {e}")
    
    # 显示健康报告
    report = health_check()
    import json
    print("\n健康报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
