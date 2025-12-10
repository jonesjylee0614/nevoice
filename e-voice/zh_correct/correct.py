from pathlib import Path

from loguru import logger
from pycorrector import Corrector

BASE_DIR = Path(__file__).resolve().parent
CUSTOM_FREQ = BASE_DIR / "custom_word_freq.txt"

m = Corrector()
# 设置自定义词频，防止被误杀
try:
    if CUSTOM_FREQ.exists():
        m.set_custom_word_freq(path=str(CUSTOM_FREQ))
        logger.info(f"中文纠错模型初始化完成，自定义词频: {CUSTOM_FREQ}")
    else:
        logger.warning(f"未找到自定义词频文件: {CUSTOM_FREQ}")
except Exception as exc:  # pragma: no cover - 纠错初始化失败时降级
    logger.warning(f"加载自定义词频失败: {exc}")
logger.info('中文纠错模型初始化完成')

# 导入同音词修正器（延迟加载）
_homophone_corrector = None


def _get_homophone_corrector():
    """延迟加载同音词修正器"""
    global _homophone_corrector
    if _homophone_corrector is None:
        try:
            from zh_correct.homophone_corrector import get_corrector
            _homophone_corrector = get_corrector()
        except Exception as e:
            logger.warning(f"同音词修正器加载失败: {e}")
            _homophone_corrector = False  # 标记为不可用
    return _homophone_corrector if _homophone_corrector else None


def correct(text):
    """
    文本纠错（语法纠错）
    
    Args:
        text: 待纠错的文本
        
    Returns:
        dict: {'source': 原文, 'target': 纠错后文本, 'errors': 错误列表}
    """
    return m.correct(text)


def correct_with_homophones(text: str) -> str:
    """
    文本纠错 + 同音词修正
    
    先进行同音词修正（热词替换），再进行语法纠错。
    
    Args:
        text: 待纠错的文本
        
    Returns:
        str: 纠错后的文本
    """
    if not text:
        return text
    
    # 1. 同音词修正（热词替换）
    corrector = _get_homophone_corrector()
    if corrector:
        text = corrector.correct(text)
    
    # 2. 语法纠错
    result = m.correct(text)
    return result.get('target', text)


def reload_homophones():
    """重新加载同音词热词库"""
    global _homophone_corrector
    _homophone_corrector = None
    corrector = _get_homophone_corrector()
    if corrector:
        corrector.reload()
        logger.info("同音词热词库已重新加载")
