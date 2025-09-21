import os
import sys
from configparser import ConfigParser
from pathlib import Path


# 解析环境名优先级：
# 1) 命令行 -e/--env 传参（例如: python rest.py -e wnl）
# 2) 环境变量 EVOICE_ENV
# 3) 默认值 'dev'
def _resolve_env_name() -> str:
    # 从环境变量读取
    env_name = os.environ.get('EVOICE_ENV')

    # 命令行覆盖（尽量容错兼容 -e wnl / --env=wnl / --env wnl）
    argv = sys.argv[1:]
    if '-e' in argv:
        idx = argv.index('-e')
        if idx + 1 < len(argv):
            env_name = argv[idx + 1]
    else:
        for i, arg in enumerate(argv):
            if arg.startswith('--env='):
                env_name = arg.split('=', 1)[1]
                break
            if arg == '--env' and i + 1 < len(argv):
                env_name = argv[i + 1]
                break

    # 默认值
    env_name = (env_name or 'dev').strip()

    # 常见别名归一化（例如: wnl -> dev_wnl）
    alias_map = {
        'wnl': 'dev_wnl',
        'dev-wnl': 'dev_wnl',
        'dev_wnl': 'dev_wnl',
    }
    return alias_map.get(env_name, env_name)


env = _resolve_env_name()

conf = ConfigParser()
BASE_DIR = Path(__file__).resolve().parent
conf.read(f'{BASE_DIR}/{env}.ini')
