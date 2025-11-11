"""在线/离线文本融合工具。"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple


@dataclass(slots=True)
class TextAccumulator:
    """维护确认文本与候选文本，并记录修订历史。"""

    confirmed_text: str = ""
    candidate_text: str = ""
    revision_id: int = 0
    history: List[Dict[str, str]] | None = None

    def diff(self, new_text: str) -> Tuple[str, str]:
        """
        简单差异计算（向后兼容）。

        返回 (removed, appended) 元组。
        如需详细差异，使用 diff_detailed()。
        """
        prefix_len = 0
        for old_ch, new_ch in zip(self.confirmed_text, new_text):
            if old_ch != new_ch:
                break
            prefix_len += 1
        removed = self.confirmed_text[prefix_len:]
        appended = new_text[prefix_len:]
        return removed, appended

    def diff_detailed(self, new_text: str) -> List[Dict[str, Any]]:
        """
        ✅ P1-1 新增：使用编辑距离算法精确计算差异。

        返回详细的编辑操作列表：
        [
            {'type': 'delete', 'text': '好', 'position': 5, 'length': 1},
            {'type': 'insert', 'text': '不错', 'position': 5, 'length': 2},
            {'type': 'replace', 'old_text': 'A', 'new_text': 'B', 'position': 3, ...}
        ]

        示例：
            原文: "今天天气真好"
            新文: "今天的天气真不错"
            结果: [
                {'type': 'insert', 'text': '的', 'position': 2, 'length': 1},
                {'type': 'replace', 'old_text': '好', 'new_text': '不错', 'position': 6, ...}
            ]
        """
        if not self.confirmed_text and not new_text:
            return []

        matcher = SequenceMatcher(None, self.confirmed_text, new_text)
        changes = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                changes.append({
                    'type': 'delete',
                    'text': self.confirmed_text[i1:i2],
                    'position': i1,
                    'length': i2 - i1,
                })
            elif tag == 'insert':
                changes.append({
                    'type': 'insert',
                    'text': new_text[j1:j2],
                    'position': i1,
                    'length': j2 - j1,
                })
            elif tag == 'replace':
                changes.append({
                    'type': 'replace',
                    'old_text': self.confirmed_text[i1:i2],
                    'new_text': new_text[j1:j2],
                    'position': i1,
                    'old_length': i2 - i1,
                    'new_length': j2 - j1,
                })
            # 'equal' 标签表示相同部分，不需要记录

        return changes

    def update_partial(self, text: str, revision: int) -> Dict[str, str | int]:
        self.candidate_text = text
        self.revision_id = revision
        return self.snapshot()

    def apply_final(self, text: str) -> Dict[str, str | int]:
        self.confirmed_text += text
        self.candidate_text = ""
        self.revision_id += 1
        if self.history is None:
            self.history = []
        self.history.append({"confirmed": self.confirmed_text})
        return self.snapshot()

    def apply_correction(self, text: str) -> Dict[str, str | int | List]:
        """
        应用纠错并返回详细差异。

        ✅ P1-1 增强：返回 snapshot 中包含 'changes' 字段，提供详细的编辑操作列表。
        """
        # 使用新的详细差异算法
        changes = self.diff_detailed(text)

        if self.history is None:
            self.history = []

        # 记录历史（向后兼容旧格式）
        removed, appended = self.diff(text)
        if removed:
            self.history.append({"removed": removed})
        if appended:
            self.history.append({"appended": appended})

        # 更新状态
        self.confirmed_text = text
        self.candidate_text = ""
        self.revision_id += 1

        # 返回包含详细差异的 snapshot
        snapshot = self.snapshot()
        snapshot['changes'] = changes  # ✅ 新增详细差异信息
        return snapshot

    def snapshot(self) -> Dict[str, str | int]:
        return {
            "confirmed_text": self.confirmed_text,
            "candidate_text": self.candidate_text,
            "revision_id": self.revision_id,
        }

