"""配置加载入口。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

BASE_DIR = Path(__file__).resolve().parent


def load_funasr_config(filename: str = "realtime_funasr.yml") -> Dict[str, Any]:
    """加载 FunASR 实时配置。"""
    config_path = BASE_DIR / filename
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}


# 向后兼容别名
load_realtime_config = load_funasr_config
