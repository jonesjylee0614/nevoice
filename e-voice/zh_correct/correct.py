from loguru import logger
from pycorrector import Corrector

m = Corrector()
# 设置自定义词频，防止被误杀
m.set_custom_word_freq(path='./zh_correct/custom_word_freq.txt')
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
