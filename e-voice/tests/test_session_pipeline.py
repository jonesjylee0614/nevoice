import importlib.machinery
import importlib
import importlib.util
import sys
import time
import types
import unittest
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parents[1]
_SERVER_DIR = _BASE_DIR / "server"
# ✅ 2025-11-09: session.py 已移至废弃代码目录
_DEPRECATED_DIR = Path(__file__).resolve().parents[2] / "e-voice-deprecated" / "2025-11-09-session-cleanup"

if str(_BASE_DIR) not in sys.path:
    sys.path.insert(0, str(_BASE_DIR))

# Ensure the "server" package and its lightweight dependencies are importable in tests.
server_pkg = sys.modules.get("server")
if not server_pkg:
    server_pkg = types.ModuleType("server")
    server_pkg.__path__ = [str(_SERVER_DIR)]
    sys.modules["server"] = server_pkg

if "speech_recognition" not in sys.modules:
    sr_pkg = types.ModuleType("speech_recognition")
    sr_pkg.__path__ = [str(_BASE_DIR / "speech_recognition")]
    sys.modules["speech_recognition"] = sr_pkg

if "speech_recognition.recognize" not in sys.modules:
    dummy_recognize = types.ModuleType("speech_recognition.recognize")
    dummy_recognize.recognize = lambda *args, **kwargs: {}
    sys.modules["speech_recognition.recognize"] = dummy_recognize

if "loguru" not in sys.modules:
    class _DummyLogger:
        def remove(self, *args, **kwargs):
            return None

        def add(self, *args, **kwargs):
            return 0

        def bind(self, **kwargs):
            return self

        def info(self, *args, **kwargs):
            return None

        def debug(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def error(self, *args, **kwargs):
            return None

        def success(self, *args, **kwargs):
            return None

        def trace(self, *args, **kwargs):
            return None

    dummy_logger = _DummyLogger()
    dummy_loguru = types.ModuleType("loguru")
    dummy_loguru.logger = dummy_logger
    sys.modules["loguru"] = dummy_loguru
else:
    dummy_logger = sys.modules["loguru"].logger

if "server.logging" not in sys.modules:
    dummy_logging = types.ModuleType("server.logging")
    dummy_logging.__spec__ = importlib.machinery.ModuleSpec("server.logging", loader=None)
    dummy_logging.recognition_logger = dummy_logger
    dummy_logging.audio_logger = dummy_logger
    dummy_logging.key_logger = dummy_logger
    sys.modules["server.logging"] = dummy_logging

# Mock zh_correct.homophone_corrector for testing
if "zh_correct.homophone_corrector" not in sys.modules:
    dummy_homophone = types.ModuleType("zh_correct.homophone_corrector")
    dummy_homophone.__spec__ = importlib.machinery.ModuleSpec("zh_correct.homophone_corrector", loader=None)
    dummy_homophone.correct_homophones = lambda text: text  # 直接返回原文
    sys.modules["zh_correct.homophone_corrector"] = dummy_homophone
if "zh_correct" not in sys.modules:
    sys.modules["zh_correct"] = types.ModuleType("zh_correct")

# ✅ 2025-11-09: 从废弃代码目录加载 session.py
# 旧架构已被 speech_recognition/streaming/ 替代，此处仅用于历史测试
_SESSION_SPEC = importlib.util.spec_from_file_location(
    "server.session",
    _DEPRECATED_DIR / "session.py",
    submodule_search_locations=[str(_DEPRECATED_DIR)],
)
assert _SESSION_SPEC and _SESSION_SPEC.loader
_SESSION_MODULE = importlib.util.module_from_spec(_SESSION_SPEC)
sys.modules.setdefault("server.session", _SESSION_MODULE)
_SESSION_SPEC.loader.exec_module(_SESSION_MODULE)

RealtimeSpeechSession = getattr(_SESSION_MODULE, "RealtimeSpeechSession")
normalize_text = getattr(importlib.import_module("server.text_processing"), "normalize_text")


class SessionFinalizeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.session = RealtimeSpeechSession()
        # Disable streaming model interactions for deterministic tests.
        self.session._streaming_available = False
        self.session.streaming_model = None
        # Avoid writing audio files during tests.
        self.session._run_offline_final_recognition = lambda: ("", None)
        self.session._auto_correct_text = lambda text: (
            text,
            {"applied": False, "details": [], "raw_result": None},
        )
        # Force silence so finalize_current_sentence will consider punctuation paths.
        self.session._silence_accumulated = 1.5
        self.session.last_activity_time = time.time() - 1.5

    def test_finalize_sentence_applies_normalization_and_locks(self) -> None:
        # Simulate a live sentence that should produce punctuation and numeric normalization.
        self.session._set_live_text("我们预计百分之五以上")
        self.session.predict_punctuation = lambda text, silence: f"{text}。"

        payload = self.session.finalize_current_sentence()
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["text"], "我们预计5%以上。")
        self.assertEqual(self.session.confirmed_sentences, ["我们预计5%以上。"])
        self.assertEqual(self.session._live_text, "")
        self.assertEqual(self.session.full_sentence, "")
        # Confirm that normalized confirmed text matches expectation for downstream consumers.
        confirmed_text = normalize_text("".join(self.session.confirmed_sentences))
        self.assertEqual(confirmed_text, "我们预计5%以上。")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
