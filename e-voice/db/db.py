import pymysql
from loguru import logger

from config.config import conf


def connect():
    db_conf = conf['db']
    return pymysql.connect(host=db_conf['host'],  # 连接名称，默认127.0.0.1
                           port=db_conf.getint('port', 3306),  # 端口，默认为3306
                           user=db_conf['user'],  # 用户名
                           passwd=db_conf['password'],  # 密码
                           db=db_conf['database'],  # 数据库名称
                           charset='utf8mb4'  # 字符编码
                           )


c = connect()


def check_db():
    global c
    try:
        c.ping()  # 采用连接对象的ping()函数检测连接状态
    except Exception as e:  # 出现异常重新连接
        logger.error(f"连接数据库异常: {str(e)}")
        c = connect()
    return c


def get_db():
    return connect()


def get_dbcursor():
    return check_db().cursor()

# def target():
#     while True:
#         check_db()
#         time.sleep(10)
#
#
# # 创建线程01，不指定参数
# thread_01 = Thread(target=target)
# # 启动线程01
# thread_01.start()
