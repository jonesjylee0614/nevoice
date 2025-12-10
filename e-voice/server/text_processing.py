"""Text normalisation and voice command utilities."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from typing import Dict, List, Optional

from .logging import recognition_logger

__all__ = [
    "detect_voice_command",
    "normalize_text",
    "format_action_to_text",
    "smooth_oral_text",
    "format_numbers",
    "normalize_for_dedup",
    "calc_similarity",
]


def detect_voice_command(text: str) -> Dict[str, object]:
    """识别文本中是否包含语音指令。"""
    if not text or not text.strip():
        return {
            "is_command": False,
            "command_type": None,
            "command_params": {},
            "processed_text": text,
        }

    text_lower = text.lower().strip()

    edit_commands = {
        "删除": {"type": "delete", "target": "last_word"},
        "删掉": {"type": "delete", "target": "last_word"},
        "删除刚刚说的": {"type": "delete", "target": "last_sentence"},
        "删掉刚刚说的": {"type": "delete", "target": "last_sentence"},
        "删除最后一个字": {"type": "delete", "target": "last_char"},
        "删除全部": {"type": "delete", "target": "all"},
        "清除全部": {"type": "delete", "target": "all"},
        "全部删除": {"type": "delete", "target": "all"},
        "撤销": {"type": "undo"},
        "撤回": {"type": "undo"},
        "重做": {"type": "redo"},
        "恢复": {"type": "redo"},
    }

    punctuation_commands = {
        "逗号": ",",
        "句号": "。",
        "问号": "？",
        "叹号": "！",
        "感叹号": "！",
        "冒号": "：",
        "分号": "；",
        "顿号": "、",
        "省略号": "……",
        "引号": '""',
        "书名号": "《》",
        "括号": "（）",
        "小括号": "（）",
        "中括号": "【】",
        "双引号": '""',
        "单引号": "'",
    }

    format_commands = {
        "换行": {"type": "format", "action": "newline"},
        "回车": {"type": "format", "action": "newline"},
        "空格": {"type": "format", "action": "space"},
        "空一格": {"type": "format", "action": "space"},
        "制表符": {"type": "format", "action": "tab"},
        "缩进": {"type": "format", "action": "tab"},
    }

    function_commands = {
        "发送": {"type": "function", "action": "send"},
        "确认": {"type": "function", "action": "confirm"},
        "取消": {"type": "function", "action": "cancel"},
        "完成": {"type": "function", "action": "complete"},
    }

    for cmd, params in edit_commands.items():
        if text_lower == cmd or text_lower.endswith(cmd):
            return {
                "is_command": True,
                "command_type": "edit",
                "command_params": params,
                "processed_text": "",
            }

    for cmd, punctuation in punctuation_commands.items():
        if text_lower == cmd:
            return {
                "is_command": True,
                "command_type": "punctuation",
                "command_params": {"punctuation": punctuation},
                "processed_text": punctuation,
            }

    for cmd, params in format_commands.items():
        if text_lower == cmd:
            return {
                "is_command": True,
                "command_type": "format",
                "command_params": params,
                "processed_text": format_action_to_text(params["action"]),
            }

    for cmd, params in function_commands.items():
        if text_lower == cmd:
            return {
                "is_command": True,
                "command_type": "function",
                "command_params": params,
                "processed_text": "",
            }

    for cmd in format_commands:
        if cmd in text_lower:
            parts = text_lower.split(cmd)
            if len(parts) == 2:
                before_text = parts[0].strip()
                after_text = parts[1].strip()
                format_char = format_action_to_text(format_commands[cmd]["action"])
                combined_text = before_text + format_char + after_text
                return {
                    "is_command": True,
                    "command_type": "mixed",
                    "command_params": {
                        "original_command": cmd,
                        "before_text": before_text,
                        "after_text": after_text,
                        "format_action": format_commands[cmd]["action"],
                    },
                    "processed_text": combined_text,
                }

    return {
        "is_command": False,
        "command_type": None,
        "command_params": {},
        "processed_text": text,
    }


def format_action_to_text(action: str) -> str:
    action_map = {"newline": "\n", "space": " ", "tab": "\t"}
    return action_map.get(action, "")


def normalize_text(text: str) -> str:
    if not text:
        return text
    try:
        t = smooth_oral_text(text)
        t = format_numbers(t)
        t = re.sub(r"\bipo\b", "IPO", t, flags=re.IGNORECASE)
        t = re.sub(r"\bipo(?=\.|\s|$)", "IPO", t, flags=re.IGNORECASE)
        # 同音词修正（热词来自数据库）
        try:
            from zh_correct.homophone_corrector import correct_homophones
            t = correct_homophones(t)
        except Exception as exc:  # pragma: no cover - defensive logging
            recognition_logger.warning(f"同音词修正失败: {exc}")
        return t
    except Exception:  # pragma: no cover - defensive logging
        return text


def normalize_for_dedup(text: str) -> str:
    if not text:
        return ""
    try:
        cleaned = text.strip()
        cleaned = re.sub(r"\s+", "", cleaned)
        cleaned = re.sub(r"[，,。.!？?\-—:：;；、·\"\'()（）\[\]\\/]", "", cleaned)
        return cleaned.lower()
    except Exception:  # pragma: no cover - defensive
        return text.strip().lower() if text else ""


def calc_similarity(a: str, b: str) -> float:
    try:
        return SequenceMatcher(None, a or "", b or "").ratio()
    except Exception:  # pragma: no cover - defensive
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return 1.0 if a == b else 0.0


def smooth_oral_text(text: str) -> str:
    if not text:
        return text

    filler_words = ["嗯", "啊", "呃", "额", "那个", "就是说", "然后呢", "怎么说呢"]
    for word in filler_words:
        text = text.replace(word, "")

    text = re.sub(r"(.{1,3})\1{1,3}", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


_CHINESE_DIGITS = {
    "零": 0,
    "〇": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}

_CHINESE_UNIT_SMALL = {"十": 10, "百": 100, "千": 1000}
_CHINESE_UNIT_SECTION = {"万": 10_000, "亿": 100_000_000, "万亿": 1_000_000_000_000, "亿万": 1_000_000_000_000}
_QUANTITY_SUFFIXES = [
    "个百分点",
    "百分点",
    "平方公里",
    "平方米",
    "立方公里",
    "立方米",
    "公顷",
    "公里/小时",
    "公里每小时",
    "万吨",
    "千吨",
    "万吨",
    "吨",
    "公斤",
    "千克",
    "克",
    "公里",
    "千米",
    "米",
    "厘米",
    "毫米",
    "亩",
    "人次",
    "人年",
    "人日",
    "人",
    "位",
    "户",
    "家",
    "家公司",
    "个",
    "台",
    "辆",
    "架",
    "艘",
    "座",
    "件",
    "条",
    "笔",
    "项",
    "例",
    "份",
    "场",
    "所",
    "小时",
    "分钟",
    "秒",
    "天",
    "日",
    "周",
    "季度",
    "月",
    "个月",
    "年",
    "亿元",
    "万元",
    "元",
    "美元",
    "人民币",
    "倍",
    "成",
    "级",
    "套",
    "张",
    "间",
    "%",
    "‰",
]

_QUANTITY_SUFFIX_PATTERN = "|".join(sorted(set(_QUANTITY_SUFFIXES), key=len, reverse=True))
_QUALIFIER_PATTERN = "以上|以下|以内|以外|左右|多|余"
_NUMBER_TOKEN = r"[零一二三四五六七八九十百千万亿两〇点]+"


def format_numbers(text: str) -> str:
    if not text:
        return text

    percent_pattern = re.compile(
        r"百分之(" + _NUMBER_TOKEN + r"|\d+(?:\.\d+)?)(?P<qualifier>" + _QUALIFIER_PATTERN + r")?"
    )

    def replace_percent(match: re.Match[str]) -> str:
        qualifier = match.group("qualifier") or ""
        number_part = match.group(1)
        parsed = _parse_mixed_number(number_part)
        if parsed is None:
            return match.group(0)
        return f"{_decimal_to_string(parsed)}%{qualifier}"

    text = percent_pattern.sub(replace_percent, text)

    quantity_pattern = re.compile(
        rf"(?P<num>{_NUMBER_TOKEN})(?P<unit>万亿|亿万|万|亿|千|百)?"
        rf"(?P<suffix>(?:{_QUANTITY_SUFFIX_PATTERN}))?"
        rf"(?P<qualifier>(?:{_QUALIFIER_PATTERN}))?"
    )

    def replace_quantity(match: re.Match[str]) -> str:
        original = match.group(0)
        num_token = match.group("num") or ""
        unit_token = match.group("unit") or ""
        suffix = match.group("suffix") or ""
        qualifier = match.group("qualifier") or ""

        if not (unit_token or suffix or qualifier):
            return original

        token_for_parse = num_token
        if not unit_token and "点" in num_token:
            for candidate in ("万亿", "亿", "万"):
                if num_token.endswith(candidate):
                    remainder = num_token[: -len(candidate)]
                    if remainder:
                        unit_token = candidate
                        token_for_parse = remainder
                    break

        parsed = _parse_mixed_number(token_for_parse)
        if parsed is None:
            return original

        number_value = parsed
        display_unit = ""

        if unit_token:
            if unit_token in ("万", "亿", "万亿", "亿万"):
                display_unit = unit_token
            else:
                scale = _CHINESE_UNIT_SMALL.get(unit_token)
                if scale:
                    number_value *= Decimal(scale)
        else:
            for candidate in ("万亿", "亿", "万"):
                if candidate in num_token:
                    try:
                        number_value = number_value / Decimal(_CHINESE_UNIT_SECTION[candidate])
                    except (InvalidOperation, KeyError, ZeroDivisionError):
                        return original
                    display_unit = candidate
                    break

        number_str = _decimal_to_string(number_value)
        return f"{number_str}{display_unit}{suffix}{qualifier}"

    return quantity_pattern.sub(replace_quantity, text)


def _parse_mixed_number(token: str) -> Optional[Decimal]:
    token = (token or "").strip()
    if not token:
        return None

    cleaned = token.replace(",", "")
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", cleaned):
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None

    if re.fullmatch(r"[零〇一二三四五六七八九两]+", cleaned):
        digits = "".join(str(_CHINESE_DIGITS.get(ch, "")) for ch in cleaned)
        if digits:
            try:
                return Decimal(digits)
            except InvalidOperation:
                return None
        return None

    if re.fullmatch(_NUMBER_TOKEN, cleaned):
        return _chinese_to_decimal(cleaned)

    return None


def _chinese_to_decimal(token: str) -> Optional[Decimal]:
    token = token.strip()
    if not token:
        return None

    negative = False
    if token.startswith("负"):
        negative = True
        token = token[1:]

    if not token:
        return None

    if "点" in token:
        integer_part, decimal_part = token.split("点", 1)
    else:
        integer_part, decimal_part = token, ""

    integer_value = _chinese_to_int(integer_part) if integer_part else 0
    if integer_value is None:
        return None

    result = Decimal(integer_value)

    if decimal_part:
        fraction = Decimal("0")
        place = Decimal("0.1")
        for ch in decimal_part:
            digit = _CHINESE_DIGITS.get(ch)
            if digit is None:
                return None
            fraction += place * Decimal(digit)
            place /= 10
        result += fraction

    if negative:
        result = -result

    return result


def _chinese_to_int(token: str) -> Optional[int]:
    token = token.strip()
    if not token:
        return 0

    total = 0
    section = 0
    number = 0
    i = 0
    length = len(token)

    while i < length:
        if token[i : i + 2] == "万亿":
            unit_char = "万亿"
            i += 2
        elif token[i : i + 2] == "亿万":
            unit_char = "亿万"
            i += 2
        else:
            unit_char = token[i]
            i += 1

        if unit_char in _CHINESE_DIGITS:
            number = _CHINESE_DIGITS[unit_char]
        elif unit_char in _CHINESE_UNIT_SMALL:
            unit = _CHINESE_UNIT_SMALL[unit_char]
            if number == 0:
                number = 1
            section += number * unit
            number = 0
        elif unit_char in _CHINESE_UNIT_SECTION:
            section += number
            if section == 0:
                section = 1
            total += section * _CHINESE_UNIT_SECTION[unit_char]
            section = 0
            number = 0
        else:
            return None

    return total + section + number


def _decimal_to_string(value: Decimal, max_fraction: int = 4) -> str:
    if value == 0:
        return "0"

    try:
        quant = Decimal(1).scaleb(-max_fraction)
        quantized = value.quantize(quant)
    except (InvalidOperation, ValueError):
        quantized = value

    normalized = quantized.normalize()
    s = format(normalized, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"
