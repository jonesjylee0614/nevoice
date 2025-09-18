"""Hotword management utilities used by the speech service."""

from __future__ import annotations

import json
import os
import time
from typing import Dict, List

from .logging import recognition_logger

__all__ = [
    "EnhancedHotwordManager",
    "get_hotword_manager",
    "load_hotword_replace_map",
]


class EnhancedHotwordManager:
    """增强热词管理器 - 支持动态更新和个性化学习。"""

    def __init__(self) -> None:
        self.hotword_dir = os.path.join("data", "hotwords")
        self.static_file = os.path.join(self.hotword_dir, "replace_map.json")
        self.dynamic_file = os.path.join(self.hotword_dir, "dynamic_hotwords.json")
        self.user_learning_file = os.path.join(self.hotword_dir, "user_learning.json")

        os.makedirs(self.hotword_dir, exist_ok=True)

        self.static_hotwords: Dict[str, str] = {}
        self.dynamic_hotwords: Dict[str, str] = {}
        self.user_corrections: Dict[str, str] = {}
        self.hotword_usage_stats: Dict[str, Dict[str, int]] = {}

        self._load_all_hotwords()

    def _load_all_hotwords(self) -> None:
        """加载静态、动态和学习热词。"""
        try:
            if os.path.exists(self.static_file):
                with open(self.static_file, "r", encoding="utf-8") as f:
                    self.static_hotwords = json.load(f)
            else:
                self.static_hotwords = {
                    "语数科技": "宇树科技",
                    "宇数科技": "宇树科技",
                    "GPT": "GPT",
                    "AI": "AI",
                    "机器学习": "机器学习",
                    "深度学习": "深度学习",
                }
                self._save_static_hotwords()
        except Exception as exc:  # pragma: no cover - defensive logging
            recognition_logger.warning(f"加载静态热词失败: {exc}")
            self.static_hotwords = {}

        try:
            if os.path.exists(self.dynamic_file):
                with open(self.dynamic_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.dynamic_hotwords = data.get("hotwords", {})
                    self.hotword_usage_stats = data.get("usage_stats", {})
        except Exception as exc:  # pragma: no cover - defensive logging
            recognition_logger.warning(f"加载动态热词失败: {exc}")
            self.dynamic_hotwords = {}
            self.hotword_usage_stats = {}

        try:
            if os.path.exists(self.user_learning_file):
                with open(self.user_learning_file, "r", encoding="utf-8") as f:
                    self.user_corrections = json.load(f)
        except Exception as exc:  # pragma: no cover - defensive logging
            recognition_logger.warning(f"加载用户学习记录失败: {exc}")
            self.user_corrections = {}

        recognition_logger.info(
            "📚 热词管理器加载完成: 静态{}个, 动态{}个, 用户学习{}个",
            len(self.static_hotwords),
            len(self.dynamic_hotwords),
            len(self.user_corrections),
        )

    def get_all_hotwords(self) -> Dict[str, str]:
        all_hotwords: Dict[str, str] = {}
        all_hotwords.update(self.static_hotwords)
        all_hotwords.update(self.dynamic_hotwords)
        all_hotwords.update(self.user_corrections)
        return all_hotwords

    def add_dynamic_hotword(self, wrong_word: str, correct_word: str, source: str = "system") -> None:
        self.dynamic_hotwords[wrong_word] = correct_word
        key = f"{wrong_word}->{correct_word}"
        if key not in self.hotword_usage_stats:
            self.hotword_usage_stats[key] = {
                "count": 0,
                "first_added": int(time.time()),
                "last_used": int(time.time()),
                "source": source,
            }
        self.hotword_usage_stats[key]["count"] += 1
        self.hotword_usage_stats[key]["last_used"] = int(time.time())
        self._save_dynamic_hotwords()
        recognition_logger.info(
            "📚 添加动态热词: '{}' -> '{}' (来源: {})", wrong_word, correct_word, source
        )

    def learn_from_correction(self, original_text: str, corrected_text: str) -> None:
        if not original_text or not corrected_text or original_text == corrected_text:
            return

        original_words: List[str] = original_text.split()
        corrected_words: List[str] = corrected_text.split()

        if len(original_words) == len(corrected_words):
            for orig, corr in zip(original_words, corrected_words):
                if orig != corr and len(orig) > 1 and len(corr) > 1:
                    self.user_corrections[orig] = corr
                    recognition_logger.info("🎯 用户纠错学习: '{}' -> '{}'", orig, corr)
        else:
            if len(original_text) > 2 and len(corrected_text) > 2:
                self.user_corrections[original_text] = corrected_text
                recognition_logger.info(
                    "🎯 用户句子纠错: '{}' -> '{}'", original_text, corrected_text
                )

        self._save_user_learning()

    def apply_hotword_replacement(self, text: str) -> str:
        if not text:
            return text

        result = text
        all_hotwords = self.get_all_hotwords()
        sorted_hotwords = sorted(all_hotwords.items(), key=lambda item: len(item[0]), reverse=True)

        replaced_count = 0
        for wrong_word, correct_word in sorted_hotwords:
            if wrong_word and wrong_word in result:
                result = result.replace(wrong_word, correct_word)
                replaced_count += 1
                key = f"{wrong_word}->{correct_word}"
                if key in self.hotword_usage_stats:
                    self.hotword_usage_stats[key]["count"] += 1
                    self.hotword_usage_stats[key]["last_used"] = int(time.time())

        if replaced_count > 0:
            recognition_logger.debug(
                "📚 热词替换: '{}' -> '{}' (替换{}个)", text, result, replaced_count
            )
            self._save_dynamic_hotwords()
        return result

    def get_hotword_suggestions(self, partial_text: str, limit: int = 5) -> List[str]:
        if not partial_text or len(partial_text) < 2:
            return []

        all_hotwords = self.get_all_hotwords()
        suggestions: List[str] = []
        partial_lower = partial_text.lower()

        for correct_word in all_hotwords.values():
            if correct_word.lower().startswith(partial_lower) and correct_word not in suggestions:
                suggestions.append(correct_word)
                if len(suggestions) >= limit:
                    break

        if len(suggestions) < limit:
            for correct_word in all_hotwords.values():
                if (
                    partial_lower in correct_word.lower()
                    and not correct_word.lower().startswith(partial_lower)
                    and correct_word not in suggestions
                ):
                    suggestions.append(correct_word)
                    if len(suggestions) >= limit:
                        break
        return suggestions

    def cleanup_old_hotwords(self, days_threshold: int = 90) -> int:
        current_time = int(time.time())
        threshold_time = current_time - (days_threshold * 24 * 3600)
        to_remove: List[str] = []

        for key, stats in list(self.hotword_usage_stats.items()):
            if stats.get("last_used", 0) < threshold_time and stats.get("count", 0) < 3:
                wrong_word = key.split("->")[0]
                if wrong_word in self.dynamic_hotwords:
                    to_remove.append(wrong_word)

        for word in to_remove:
            self.dynamic_hotwords.pop(word, None)
            for key in [k for k in list(self.hotword_usage_stats.keys()) if k.startswith(word + "->")]:
                self.hotword_usage_stats.pop(key, None)

        if to_remove:
            recognition_logger.info(
                "🗑️ 清理{}个长期未使用的动态热词: {}", len(to_remove), to_remove
            )
            self._save_dynamic_hotwords()
        return len(to_remove)

    def _save_static_hotwords(self) -> None:
        try:
            with open(self.static_file, "w", encoding="utf-8") as f:
                json.dump(self.static_hotwords, f, ensure_ascii=False, indent=2)
        except Exception as exc:  # pragma: no cover - defensive
            recognition_logger.error(f"保存静态热词失败: {exc}")

    def _save_dynamic_hotwords(self) -> None:
        try:
            data = {
                "hotwords": self.dynamic_hotwords,
                "usage_stats": self.hotword_usage_stats,
                "last_updated": int(time.time()),
            }
            with open(self.dynamic_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:  # pragma: no cover - defensive
            recognition_logger.error(f"保存动态热词失败: {exc}")

    def _save_user_learning(self) -> None:
        try:
            data = {
                **self.user_corrections,
                "_meta": {
                    "last_updated": int(time.time()),
                    "total_corrections": len(self.user_corrections),
                },
            }
            with open(self.user_learning_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:  # pragma: no cover - defensive
            recognition_logger.error(f"保存用户学习记录失败: {exc}")


_hotword_manager: EnhancedHotwordManager | None = None


def get_hotword_manager() -> EnhancedHotwordManager:
    global _hotword_manager
    if _hotword_manager is None:
        _hotword_manager = EnhancedHotwordManager()
    return _hotword_manager


def load_hotword_replace_map() -> Dict[str, str]:
    return get_hotword_manager().get_all_hotwords()
