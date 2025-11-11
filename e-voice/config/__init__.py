"""配置加载入口。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

BASE_DIR = Path(__file__).resolve().parent


def load_realtime_config(filename: str = "realtime.yml") -> Dict[str, Any]:
    config_path = BASE_DIR / filename
    if not config_path.exists():
        config_path = BASE_DIR / "realtime.example.yml"
    with config_path.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)

