# 通过环境变量确定环境名，默认为开发环境，通过读取{环境名}.ini配置文件，获取配置

import os
from configparser import ConfigParser

# 读取环境变量 EVOICE_ENV，如果不存在则默认为 'dev'
env = os.environ.get('EVOICE_ENV', 'dev')

conf = ConfigParser()  # 需要实例化一个ConfigParser对象
conf.read(f'./config/{env}.ini')  # 需要添加上config.ini的路径，不需要open打开，直接给文件路径就读取，也可以指定encoding='utf-8'
