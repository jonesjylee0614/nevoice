"""Server package initialisation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _ensure_local_speech_recognition() -> None:
    """Force Python to load the in-repo `speech_recognition` package."""
    base_dir = Path(__file__).resolve().parent.parent / "speech_recognition"
    init_file = base_dir / "__init__.py"

    if not init_file.exists():
        raise ImportError(f"Local speech recognition package not found at {init_file}")

    existing = sys.modules.get("speech_recognition")
    if existing and getattr(existing, "__file__", None) == str(init_file):
        return

    spec = importlib.util.spec_from_file_location("speech_recognition", init_file)
    if spec and spec.loader:
        spec.submodule_search_locations = [str(base_dir)]
        module = importlib.util.module_from_spec(spec)
        module.__path__ = [str(base_dir)]
        sys.modules["speech_recognition"] = module
        spec.loader.exec_module(module)
    else:
        module = ModuleType("speech_recognition")
        module.__path__ = [str(base_dir)]
        sys.modules["speech_recognition"] = module


_ensure_local_speech_recognition()

from .app import create_app

__all__ = ["create_app"]
