"""
同音词热词修正器

基于热词库进行同音字替换，用于修正语音识别中的同音错误。
例如：头胞 → 头孢，阿莫西林 识别为 阿末西林 时可修正。

使用方式：
    from zh_correct.homophone_corrector import HomophoneCorrector
    corrector = HomophoneCorrector()
    result = corrector.correct("阿末西林胶囊")  # → "阿莫西林胶囊"
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from functools import lru_cache

from loguru import logger

# 尝试导入 pypinyin
try:
    from pypinyin import pinyin, Style, lazy_pinyin
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False
    logger.warning("pypinyin 未安装，同音词修正功能不可用。请运行: pip install pypinyin")


class HomophoneCorrector:
    """
    同音词修正器
    
    将识别结果中的同音错误词替换为热词库中的正确词。
    使用内存缓存提高匹配性能。
    """
    
    _instance = None
    _lock = threading.Lock()
    _is_initialized = False  # 类级别标记
    
    # 常用词白名单 - 这些词不会被替换
    # 避免常用词被错误替换为同音的医学词汇
    COMMON_WORDS_WHITELIST = {
        # 常用双字词
        "这是", "那是", "就是", "不是", "还是", "但是", "只是", "而是",
        "可是", "于是", "因此", "所以", "如果", "虽然", "因为", "已经",
        "可以", "应该", "能够", "需要", "希望", "认为", "觉得", "知道",
        "看到", "听到", "想到", "说到", "做到", "得到", "来到", "回到",
        "什么", "怎么", "为什么", "这个", "那个", "哪个", "一个", "几个",
        "我们", "你们", "他们", "她们", "大家", "自己", "别人", "有人",
        "没有", "拥有", "具有", "含有", "存在", "发生", "发现", "发展",
        "问题", "情况", "时候", "地方", "方面", "部分", "过程", "结果",
        "工作", "生活", "学习", "研究", "发展", "建设", "管理", "服务",
        "今天", "明天", "昨天", "现在", "以前", "以后", "之前", "之后",
        "上面", "下面", "前面", "后面", "左边", "右边", "里面", "外面",
        "非常", "特别", "十分", "比较", "更加", "最近", "一直", "已经",
        # 常用三字词
        "怎么样", "为什么", "是不是", "有没有", "能不能", "会不会",
    }
    
    def __new__(cls):
        """单例模式，确保热词库只加载一次"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 使用类级别标记避免重复初始化
        if HomophoneCorrector._is_initialized:
            return
        HomophoneCorrector._is_initialized = True
        
        self._hotwords: Set[str] = set()  # 热词集合
        self._pinyin_to_words: Dict[str, List[str]] = {}  # 拼音 -> 热词列表
        self._word_pinyin_cache: Dict[str, str] = {}  # 词 -> 拼音 缓存
        self._max_word_length: int = 0  # 热词最大长度
        self._min_word_length: int = 2  # 热词最小长度（忽略单字）
        self._load_time: float = 0
        self._file_mtime: float = 0
        
        # 热词文件路径
        self._hotword_file = Path(__file__).resolve().parent / "custom_word_freq.txt"
        
        # 加载热词库
        self._load_hotwords()
    
    def _load_hotwords(self) -> None:
        """加载热词库到内存"""
        if not PYPINYIN_AVAILABLE:
            logger.warning("pypinyin 不可用，跳过热词加载")
            return
        
        if not self._hotword_file.exists():
            logger.warning(f"热词文件不存在: {self._hotword_file}")
            return
        
        start_time = time.time()
        
        try:
            # 检查文件修改时间
            current_mtime = os.path.getmtime(self._hotword_file)
            if current_mtime == self._file_mtime and self._hotwords:
                logger.debug("热词文件未变化，跳过重新加载")
                return
            
            self._file_mtime = current_mtime
            
            # 清空现有数据
            self._hotwords.clear()
            self._pinyin_to_words.clear()
            self._word_pinyin_cache.clear()
            self._max_word_length = 0
            
            # 读取热词文件
            with open(self._hotword_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if not word or len(word) < self._min_word_length:
                        continue
                    
                    self._hotwords.add(word)
                    self._max_word_length = max(self._max_word_length, len(word))
                    
                    # 计算拼音并建立映射
                    word_pinyin = self._get_pinyin(word)
                    if word_pinyin:
                        if word_pinyin not in self._pinyin_to_words:
                            self._pinyin_to_words[word_pinyin] = []
                        self._pinyin_to_words[word_pinyin].append(word)
            
            self._load_time = time.time() - start_time
            logger.info(
                f"✅ 同音词修正器初始化完成: "
                f"{len(self._hotwords)} 个热词, "
                f"{len(self._pinyin_to_words)} 个拼音映射, "
                f"最大词长 {self._max_word_length}, "
                f"耗时 {self._load_time:.2f}s"
            )
            
        except Exception as e:
            logger.error(f"加载热词库失败: {e}")
    
    def _get_pinyin(self, text: str) -> str:
        """获取文本的拼音（去声调）"""
        if not PYPINYIN_AVAILABLE:
            return ""
        
        # 检查缓存
        if text in self._word_pinyin_cache:
            return self._word_pinyin_cache[text]
        
        try:
            # 使用 lazy_pinyin 获取不带声调的拼音
            py_list = lazy_pinyin(text)
            result = ''.join(py_list)
            
            # 缓存结果
            self._word_pinyin_cache[text] = result
            return result
        except Exception:
            return ""
    
    def correct(self, text: str) -> str:
        """
        对文本进行同音词修正
        
        Args:
            text: 待修正的文本
            
        Returns:
            修正后的文本
        """
        if not text or not PYPINYIN_AVAILABLE or not self._hotwords:
            return text
        
        # 使用滑动窗口匹配
        result = []
        i = 0
        text_len = len(text)
        
        while i < text_len:
            matched = False
            
            # 从最长词开始匹配（贪婪匹配）
            for length in range(min(self._max_word_length, text_len - i), self._min_word_length - 1, -1):
                segment = text[i:i + length]
                
                # 如果是白名单中的常用词，直接保留不替换
                if segment in self.COMMON_WORDS_WHITELIST:
                    result.append(segment)
                    i += length
                    matched = True
                    break
                
                # 如果已经是热词，直接保留
                if segment in self._hotwords:
                    result.append(segment)
                    i += length
                    matched = True
                    break
                
                # 检查是否有同音热词
                segment_pinyin = self._get_pinyin(segment)
                if segment_pinyin and segment_pinyin in self._pinyin_to_words:
                    # 找到同音热词，选择第一个（优先级最高的）
                    hotword = self._pinyin_to_words[segment_pinyin][0]
                    if hotword != segment:  # 确实需要替换
                        logger.debug(f"同音替换: '{segment}' → '{hotword}'")
                        result.append(hotword)
                        i += length
                        matched = True
                        break
            
            # 没有匹配到，保留原字符
            if not matched:
                result.append(text[i])
                i += 1
        
        return ''.join(result)
    
    def reload(self) -> None:
        """重新加载热词库（用于热词更新后）"""
        logger.info("正在重新加载热词库...")
        self._file_mtime = 0  # 重置文件修改时间，强制重新加载
        self._load_hotwords()
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'hotword_count': len(self._hotwords),
            'pinyin_mapping_count': len(self._pinyin_to_words),
            'max_word_length': self._max_word_length,
            'load_time': self._load_time,
            'pypinyin_available': PYPINYIN_AVAILABLE,
            'cache_size': len(self._word_pinyin_cache)
        }
    
    def find_homophones(self, word: str) -> List[str]:
        """查找某个词的所有同音词"""
        if not PYPINYIN_AVAILABLE:
            return []
        
        word_pinyin = self._get_pinyin(word)
        if not word_pinyin:
            return []
        
        return self._pinyin_to_words.get(word_pinyin, [])


# 全局单例
_corrector: Optional[HomophoneCorrector] = None


def get_corrector() -> HomophoneCorrector:
    """获取同音词修正器单例"""
    global _corrector
    if _corrector is None:
        _corrector = HomophoneCorrector()
    return _corrector


def correct_homophones(text: str) -> str:
    """
    便捷函数：对文本进行同音词修正
    
    Args:
        text: 待修正的文本
        
    Returns:
        修正后的文本
    """
    return get_corrector().correct(text)


def reload_hotwords() -> None:
    """重新加载热词库"""
    get_corrector().reload()


# 模块加载时预热（在后台线程中进行）
def _preload():
    """后台预加载热词库"""
    try:
        get_corrector()
    except Exception as e:
        logger.warning(f"预加载热词库失败: {e}")


# 使用守护线程预加载，不阻塞主程序
_preload_thread = threading.Thread(target=_preload, daemon=True)
_preload_thread.start()


if __name__ == "__main__":
    # 测试
    print(f"热词文件路径: {Path(__file__).resolve().parent / 'custom_word_freq.txt'}")
    print(f"文件存在: {(Path(__file__).resolve().parent / 'custom_word_freq.txt').exists()}")
    
    # 重置单例以便重新初始化
    HomophoneCorrector._instance = None
    HomophoneCorrector._is_initialized = False
    
    corrector = HomophoneCorrector()
    print(f"统计: {corrector.get_stats()}")
    print(f"热词文件属性: {corrector._hotword_file}")
    print(f"热词文件存在: {corrector._hotword_file.exists()}")
    
    test_cases = [
        "头胞克洛",
        "阿末西林",
        "患者服用头胞克洛后",
        "这是一个普通句子",
    ]
    
    for text in test_cases:
        result = corrector.correct(text)
        if text != result:
            print(f"'{text}' → '{result}'")
        else:
            print(f"'{text}' (无变化)")

