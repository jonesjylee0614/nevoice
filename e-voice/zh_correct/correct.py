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


#
# logger.info('开始纠错')
# res = m.correct_batch(['少先队员因该为老人让坐到玄丹升麻汤上', '你找到你最喜欢的工作，我也很高心。', '怎么肥四  困成狗'])
#
# logger.info(res)
#
# logger.info('纠错完成')


def correct(text):
    return m.correct(text)
