"""
智能词汇管理器 - 动态加载和优化自定义词汇
"""
import time
from pathlib import Path

from loguru import logger


class VocabularyManager:
    """
    智能词汇管理器
    
    功能：
    1. 动态加载词汇文件
    2. 内存使用优化
    3. 性能监控
    4. 热切换支持
    """

    def __init__(self):
        self.vocab_logger = logger.bind(component="vocabulary_manager")
        self.base_path = Path("../zh_correct")

        # 词汇文件配置
        self.vocab_files = {
            'full': self.base_path / 'custom_word_freq.txt',  # 217k词 (~2GB内存)
            'lite': self.base_path / 'custom_word_freq_lite.txt',  # 5k词 (~50MB内存)  
            'mini': self.base_path / 'custom_word_freq_mini.txt',  # 1k词 (~10MB内存)
        }

        # 当前配置
        self.current_mode = 'lite'  # 默认使用精简版
        self.loaded_vocabulary = None
        self.load_time = None
        self.memory_usage = 0

        # 性能统计
        self.stats = {
            'load_count': 0,
            'hit_count': 0,
            'miss_count': 0,
            'avg_load_time': 0
        }

    def create_mini_vocabulary(self):
        """创建超精简版词汇文件（1000个最核心词汇）"""
        try:
            full_file = self.vocab_files['full']
            mini_file = self.vocab_files['mini']

            if not full_file.exists():
                self.vocab_logger.warning(f"原始词汇文件不存在: {full_file}")
                return False

            with open(full_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:1000]  # 只取前1000行

            with open(mini_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            self.vocab_logger.info(f"✅ 创建超精简词汇文件: {len(lines)}词 -> {mini_file}")
            return True

        except Exception as e:
            self.vocab_logger.error(f"❌ 创建超精简词汇文件失败: {e}")
            return False

    def get_optimal_vocabulary_file(self, max_memory_mb=100):
        """
        根据内存限制选择最优词汇文件
        
        Args:
            max_memory_mb: 最大内存使用限制(MB)
            
        Returns:
            最优词汇文件路径或None（不使用词汇）
        """
        memory_requirements = {
            'mini': 10,  # 1k词 ≈ 10MB
            'lite': 50,  # 5k词 ≈ 50MB  
            'full': 2000  # 217k词 ≈ 2GB
        }

        # 按内存使用量排序，选择最大可用的
        for mode in ['full', 'lite', 'mini']:
            if memory_requirements[mode] <= max_memory_mb:
                vocab_file = self.vocab_files[mode]
                if vocab_file.exists():
                    self.vocab_logger.info(f"🎯 选择词汇模式: {mode} (预计{memory_requirements[mode]}MB)")
                    return str(vocab_file)

        self.vocab_logger.warning(f"⚠️ 内存限制过低({max_memory_mb}MB)，禁用自定义词汇")
        return None

    def load_vocabulary(self, mode='auto', max_memory_mb=100):
        """
        加载词汇文件
        
        Args:
            mode: 'auto', 'mini', 'lite', 'full', None
            max_memory_mb: 内存限制
            
        Returns:
            词汇文件路径或None
        """
        start_time = time.time()

        try:
            if mode == 'auto':
                vocab_file = self.get_optimal_vocabulary_file(max_memory_mb)
            elif mode is None:
                vocab_file = None  # 不使用自定义词汇
            else:
                vocab_file = str(self.vocab_files[mode]) if self.vocab_files[mode].exists() else None

            if vocab_file:
                # 验证文件可读性
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)

                load_time = time.time() - start_time
                self.vocab_logger.success(f"✅ 词汇加载成功: {vocab_file} ({line_count:,}词, {load_time:.2f}s)")

                # 更新统计
                self.stats['load_count'] += 1
                self.stats['avg_load_time'] = (self.stats['avg_load_time'] + load_time) / 2
                self.load_time = load_time
                self.current_mode = mode

                return vocab_file
            else:
                self.vocab_logger.info("ℹ️ 不使用自定义词汇（性能优先模式）")
                return None

        except Exception as e:
            self.vocab_logger.error(f"❌ 词汇加载失败: {e}")
            return None

    def get_stats(self):
        """获取性能统计"""
        return {
            'current_mode': self.current_mode,
            'load_time': self.load_time,
            'memory_usage_mb': self.memory_usage,
            **self.stats
        }

    def recommend_mode(self, available_memory_mb=None):
        """
        推荐最优词汇模式
        
        Args:
            available_memory_mb: 可用内存(MB)
            
        Returns:
            推荐的模式和说明
        """
        if available_memory_mb is None:
            # 尝试获取系统内存信息
            try:
                import psutil
                available_memory_mb = psutil.virtual_memory().available // (1024 * 1024)
            except ImportError:
                available_memory_mb = 1000  # 假设1GB可用内存

        recommendations = []

        if available_memory_mb > 3000:  # 3GB+
            recommendations.append(('full', '高内存环境，可使用完整词汇（最高准确率）'))
        elif available_memory_mb > 500:  # 500MB+
            recommendations.append(('lite', '标准环境，推荐精简版词汇（平衡性能）'))
        elif available_memory_mb > 100:  # 100MB+
            recommendations.append(('mini', '低内存环境，使用超精简词汇'))
        else:  # <100MB
            recommendations.append((None, '极低内存环境，建议禁用自定义词汇'))

        return recommendations[0]


# 全局词汇管理器实例
vocab_manager = VocabularyManager()


def initialize_vocabulary_files():
    """初始化所有词汇文件"""
    vocab_manager.create_mini_vocabulary()
    return vocab_manager


if __name__ == "__main__":
    # 测试词汇管理器
    vm = initialize_vocabulary_files()

    # 测试不同模式
    for mode in ['mini', 'lite', None]:
        print(f"\n=== 测试模式: {mode} ===")
        result = vm.load_vocabulary(mode)
        print(f"结果: {result}")
        print(f"统计: {vm.get_stats()}")

    # 推荐模式
    mode, desc = vm.recommend_mode()
    print(f"\n推荐模式: {mode} - {desc}")
