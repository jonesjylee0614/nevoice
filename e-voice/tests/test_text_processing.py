import importlib.util
import importlib.machinery
import types
import unittest
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parents[1]
_SERVER_DIR = _BASE_DIR / 'server'

server_pkg = types.ModuleType('server')
server_pkg.__path__ = [str(_SERVER_DIR)]

import sys

sys.modules['server'] = server_pkg

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


dummy_loguru = types.ModuleType('loguru')
_dummy_logger = _DummyLogger()
dummy_loguru.logger = _dummy_logger
sys.modules['loguru'] = dummy_loguru

dummy_logging = types.ModuleType('server.logging')
dummy_logging.__spec__ = importlib.machinery.ModuleSpec('server.logging', loader=None)
dummy_logging.recognition_logger = _dummy_logger
dummy_logging.audio_logger = _dummy_logger
dummy_logging.key_logger = _dummy_logger
sys.modules['server.logging'] = dummy_logging

# Mock zh_correct.homophone_corrector for testing
dummy_homophone = types.ModuleType('zh_correct.homophone_corrector')
dummy_homophone.__spec__ = importlib.machinery.ModuleSpec('zh_correct.homophone_corrector', loader=None)
dummy_homophone.correct_homophones = lambda text: text  # 直接返回原文
sys.modules['zh_correct.homophone_corrector'] = dummy_homophone
sys.modules['zh_correct'] = types.ModuleType('zh_correct')

_SPEC = importlib.util.spec_from_file_location(
    'server.text_processing',
    _SERVER_DIR / 'text_processing.py',
    submodule_search_locations=[str(_SERVER_DIR)],
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault('server.text_processing', _MODULE)
_SPEC.loader.exec_module(_MODULE)

format_numbers = getattr(_MODULE, 'format_numbers')


class FormatNumbersTestCase(unittest.TestCase):
    def test_percentage_without_qualifier(self):
        self.assertEqual(format_numbers('百分之五'), '5%')
        self.assertEqual(format_numbers('百分之3.5'), '3.5%')

    def test_percentage_with_qualifier(self):
        self.assertEqual(format_numbers('百分之五以上'), '5%以上')
        self.assertEqual(format_numbers('百分之十以下'), '10%以下')

    def test_large_numbers_with_units(self):
        self.assertEqual(format_numbers('一百六十七万亩'), '167万亩')
        self.assertEqual(format_numbers('三千万吨'), '3000万吨')
        self.assertEqual(format_numbers('五千六百七十亿元'), '5670亿元')
        self.assertEqual(format_numbers('零点五万亩'), '0.5万亩')

    def test_population_examples(self):
        self.assertEqual(format_numbers('三千五百人'), '3500人')
        self.assertEqual(format_numbers('一亿三千万人'), '1.3亿人')
        self.assertEqual(format_numbers('三百二十人以上'), '320人以上')

    def test_year_and_date(self):
        self.assertEqual(format_numbers('二零二四年'), '2024年')
        self.assertEqual(format_numbers('一月一日'), '1月1日')


if __name__ == '__main__':
    unittest.main()
