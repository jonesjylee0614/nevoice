"""Text normalisation and voice command utilities."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional

from .hotwords import get_hotword_manager, load_hotword_replace_map
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
        try:
            hotword_manager = get_hotword_manager()
            t = hotword_manager.apply_hotword_replacement(t)
        except Exception as exc:  # pragma: no cover - defensive logging
            recognition_logger.warning(f"热词替换失败: {exc}")
            rep = load_hotword_replace_map()
            if rep:
                for key, value in rep.items():
                    if not key:
                        continue
                    try:
                        t = t.replace(key, value)
                    except Exception:  # pragma: no cover - defensive
                        pass
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


def format_numbers(text: str) -> str:
    if not text:
        return text

    text = re.sub(r"百分之(\d+)", r"\1%", text)
    text = re.sub(r"百分之([一二三四五六七八九十百]+)", lambda m: f"{_chinese_to_number(m.group(1))}%", text)

    chinese_numbers = {
        "一": "1",
        "二": "2",
        "三": "3",
        "四": "4",
        "五": "5",
        "六": "6",
        "七": "7",
        "八": "8",
        "九": "9",
        "十": "10",
        "零": "0",
        "〇": "0",
    }

    for cn, num in chinese_numbers.items():
        text = re.sub(rf"(?<![a-zA-Z\u4e00-\u9fff]){cn}(?![a-zA-Z\u4e00-\u9fff])", num, text)
    return text


def _chinese_to_number(chinese_num: str) -> str:
    mapping = {
        "十": "10",
        "二十": "20",
        "三十": "30",
        "四十": "40",
        "五十": "50",
        "六十": "60",
        "七十": "70",
        "八十": "80",
        "九十": "90",
        "一百": "100",
    }
    return mapping.get(chinese_num, chinese_num)
