"""
片段合并模块 - 用于将连续的短句合并为更完整的发言。

核心原则：
1. 不跨说话人合并 - speaker_id 变化立即断开
2. 句末标点断开 - 以 。！？!? 结尾一律不合并
3. 时间间隔限制 - 超过 max_gap_ms 不合并
4. 短句优先合并 - 先尝试合并，合并不了再过滤

关键概念：
- max_gap_ms 是"允许合并的最大间隔"，不是 UI 延迟时间
- correction 到来时先暂存，超过间隔就立即落地上一条
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from loguru import logger


# 默认配置
DEFAULT_CONFIG = {
    "enabled": True,
    "max_gap_ms": 3000,  # 允许合并的最大间隔
    "min_text_length": 4,  # 无法合并时的过滤阈值（去掉标点后）
    "min_duration_ms": 800,  # 无法合并时的过滤阈值
    "force_break_punctuation": ['。', '！', '？', '!', '?'],  # 强制断句标点
}

# 移除标点的正则
ALL_PUNCTUATION_PATTERN = re.compile(r'[。！？!?，,、；;：:""''""\'\'()（）【】\[\]《》<>—\-…·\s]+')


@dataclass
class MergeConfig:
    """合并配置"""
    enabled: bool = True
    max_gap_ms: int = 3000
    min_text_length: int = 4
    min_duration_ms: int = 800
    force_break_punctuation: List[str] = field(default_factory=lambda: ['。', '！', '？', '!', '?'])
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "MergeConfig":
        """从字典创建配置"""
        return cls(
            enabled=config.get("enabled", DEFAULT_CONFIG["enabled"]),
            max_gap_ms=config.get("max_gap_ms", DEFAULT_CONFIG["max_gap_ms"]),
            min_text_length=config.get("min_text_length", DEFAULT_CONFIG["min_text_length"]),
            min_duration_ms=config.get("min_duration_ms", DEFAULT_CONFIG["min_duration_ms"]),
            force_break_punctuation=config.get(
                "force_break_punctuation", 
                DEFAULT_CONFIG["force_break_punctuation"]
            ),
        )


@dataclass
class PendingSegment:
    """待处理的片段"""
    text: str
    start_offset_ms: int
    end_offset_ms: int
    duration_ms: int
    speaker_id: Optional[int]  # None 表示未识别
    speaker_name: str
    audio_path: Optional[str]
    audio_data: Optional[bytes]  # 音频数据用于合并后重新保存
    original_event: Dict[str, Any]  # 原始事件数据
    timestamp_ms: int  # 事件到达时间戳
    
    @classmethod
    def from_event(cls, event: Dict[str, Any]) -> "PendingSegment":
        """从 correction 事件创建待处理片段"""
        speaker_info = event.get("speaker_info") or {}
        return cls(
            text=event.get("text", ""),
            start_offset_ms=event.get("start_offset_ms", 0),
            end_offset_ms=event.get("end_offset_ms", 0),
            duration_ms=event.get("duration_ms", 0),
            speaker_id=speaker_info.get("speaker_id"),
            speaker_name=speaker_info.get("speaker_name", "未知发言人"),
            audio_path=event.get("audio_path"),
            audio_data=event.get("audio_data"),
            original_event=event,
            timestamp_ms=int(time.time() * 1000),
        )
    
    def to_event(self) -> Dict[str, Any]:
        """转换回事件格式"""
        event = dict(self.original_event)
        event["text"] = self.text
        event["start_offset_ms"] = self.start_offset_ms
        event["end_offset_ms"] = self.end_offset_ms
        event["duration_ms"] = self.duration_ms
        event["audio_path"] = self.audio_path
        # 更新 speaker_info
        if "speaker_info" in event and event["speaker_info"]:
            event["speaker_info"]["speaker_id"] = self.speaker_id
            event["speaker_info"]["speaker_name"] = self.speaker_name
        # 移除 audio_data，因为 bytes 不能 JSON 序列化
        event.pop("audio_data", None)
        return event


class SegmentMergeBuffer:
    """
    单个会话的片段合并缓冲区。
    
    合并逻辑：
    1. correction 事件到来时先暂存
    2. 判断是否可以与前一条合并
    3. 不能合并则立即输出前一条，当前作为新缓冲
    """
    
    def __init__(self, session_id: str, config: MergeConfig):
        self.session_id = session_id
        self.config = config
        self._pending: Optional[PendingSegment] = None
        self._audio_segments: List[bytes] = []  # 合并时收集的音频片段
    
    def _can_merge(self, prev: PendingSegment, curr: PendingSegment) -> Tuple[bool, str]:
        """
        判断当前片段是否可以合并到前一个片段。
        
        Returns:
            (可否合并, 原因说明)
        """
        # 约束1：不跨说话人
        # speaker_id 都为 None 视为同一说话人（都未识别）
        if prev.speaker_id != curr.speaker_id:
            # 如果都是 None，可以合并
            if not (prev.speaker_id is None and curr.speaker_id is None):
                return False, f"说话人变化: {prev.speaker_id} -> {curr.speaker_id}"
        
        # 约束2：前一条以强制断句标点结尾
        if prev.text:
            last_char = prev.text[-1]
            if last_char in self.config.force_break_punctuation:
                return False, f"前一条以句末标点结尾: '{last_char}'"
        
        # 约束3：时间间隔检查
        gap_ms = curr.start_offset_ms - prev.end_offset_ms
        if gap_ms > self.config.max_gap_ms:
            return False, f"时间间隔过大: {gap_ms}ms > {self.config.max_gap_ms}ms"
        
        return True, "可以合并"
    
    def _merge_segments(self, prev: PendingSegment, curr: PendingSegment) -> PendingSegment:
        """
        合并两个片段。
        
        合并规则：
        - 文本：直接拼接（中间不加空格，中文无需）
        - 时间：取第一段 start，最后一段 end
        - 说话人：保持前一条的（如果两者都未识别则保持未识别）
        - 音频：收集到列表中，后续需要时再拼接
        """
        # 合并文本
        merged_text = prev.text + curr.text
        
        # 合并时间
        start_ms = prev.start_offset_ms
        end_ms = curr.end_offset_ms
        duration_ms = end_ms - start_ms
        
        # 收集音频数据
        if curr.audio_data:
            self._audio_segments.append(curr.audio_data)
        
        # 创建合并后的片段
        merged = PendingSegment(
            text=merged_text,
            start_offset_ms=start_ms,
            end_offset_ms=end_ms,
            duration_ms=duration_ms,
            speaker_id=prev.speaker_id if prev.speaker_id is not None else curr.speaker_id,
            speaker_name=prev.speaker_name if prev.speaker_name != "未知发言人" else curr.speaker_name,
            audio_path=prev.audio_path,  # 保持第一个的路径，后续可能需要重新保存
            audio_data=prev.audio_data,  # 保持第一个的数据
            original_event=prev.original_event,  # 保持第一个的事件结构
            timestamp_ms=prev.timestamp_ms,
        )
        
        logger.debug(
            f"[segment_merge] session={self.session_id} 合并: "
            f"'{prev.text}' + '{curr.text}' -> '{merged_text}'"
        )
        
        return merged
    
    def _should_filter(self, segment: PendingSegment) -> Tuple[bool, str]:
        """
        判断无法合并的片段是否应该被过滤。
        
        注意：这是最后一道防线，短句应该优先尝试合并！
        
        Returns:
            (是否过滤, 原因说明)
        """
        # 去掉标点后的纯文本
        pure_text = ALL_PUNCTUATION_PATTERN.sub('', segment.text)
        
        # 空文本
        if not pure_text:
            return True, "空文本"
        
        # 长度检查
        if len(pure_text) < self.config.min_text_length:
            # 时长也很短，过滤
            if segment.duration_ms < self.config.min_duration_ms:
                return True, f"短句过滤: len={len(pure_text)} < {self.config.min_text_length}, duration={segment.duration_ms}ms < {self.config.min_duration_ms}ms"
        
        return False, "保留"
    
    def process(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        处理一个 correction 事件。
        
        返回需要立即输出的事件列表（可能为空、一个或多个）。
        
        核心逻辑：
        1. 如果没有待处理片段，当前片段作为新的待处理
        2. 如果有待处理片段，判断是否可以合并
           - 可以合并：合并后继续等待
           - 不能合并：输出前一条，当前作为新的待处理
        """
        if not self.config.enabled:
            # 合并功能禁用，直接返回
            return [event]
        
        curr = PendingSegment.from_event(event)
        output_events: List[Dict[str, Any]] = []
        
        if self._pending is None:
            # 没有待处理片段，当前作为新的待处理
            self._pending = curr
            # 初始化音频片段列表
            self._audio_segments = [curr.audio_data] if curr.audio_data else []
            logger.debug(
                f"[segment_merge] session={self.session_id} 新缓冲: '{curr.text}'"
            )
        else:
            # 有待处理片段，判断是否可以合并
            can_merge, reason = self._can_merge(self._pending, curr)
            
            if can_merge:
                # 可以合并
                self._pending = self._merge_segments(self._pending, curr)
                logger.info(
                    f"[segment_merge] session={self.session_id} 合并成功: {reason}"
                )
            else:
                # 不能合并，输出前一条
                logger.info(
                    f"[segment_merge] session={self.session_id} 不合并: {reason}"
                )
                
                # 检查前一条是否需要过滤
                should_filter, filter_reason = self._should_filter(self._pending)
                if should_filter:
                    logger.info(
                        f"[segment_merge] session={self.session_id} 过滤: {filter_reason}, text='{self._pending.text}'"
                    )
                else:
                    output_events.append(self._pending.to_event())
                
                # 当前作为新的待处理
                self._pending = curr
                self._audio_segments = [curr.audio_data] if curr.audio_data else []
        
        return output_events
    
    def flush(self) -> List[Dict[str, Any]]:
        """
        刷新缓冲区，输出所有待处理的片段。
        
        在会话结束时调用。
        """
        output_events: List[Dict[str, Any]] = []
        
        if self._pending is not None:
            # 检查是否需要过滤
            should_filter, filter_reason = self._should_filter(self._pending)
            if should_filter:
                logger.info(
                    f"[segment_merge] session={self.session_id} flush 过滤: {filter_reason}, text='{self._pending.text}'"
                )
            else:
                output_events.append(self._pending.to_event())
                logger.info(
                    f"[segment_merge] session={self.session_id} flush 输出: '{self._pending.text}'"
                )
            
            self._pending = None
            self._audio_segments = []
        
        return output_events
    
    def get_merged_audio_data(self) -> Optional[bytes]:
        """
        获取合并后的音频数据。
        
        如果有多个音频片段被合并，返回拼接后的数据。
        """
        if not self._audio_segments:
            return None
        if len(self._audio_segments) == 1:
            return self._audio_segments[0]
        return b"".join(self._audio_segments)


class SegmentMergeManager:
    """
    片段合并管理器 - 管理多个会话的合并缓冲区。
    
    单例模式，同步和异步路径共用同一个实例。
    """
    
    _instance: Optional["SegmentMergeManager"] = None
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = MergeConfig.from_dict(config or {})
        self._buffers: Dict[str, SegmentMergeBuffer] = {}
    
    @classmethod
    def current(cls, config: Optional[Dict[str, Any]] = None) -> "SegmentMergeManager":
        """获取或创建单例实例"""
        if cls._instance is None:
            cls._instance = cls(config)
        elif config is not None:
            # 如果提供了新配置，更新配置
            cls._instance._config = MergeConfig.from_dict(config)
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """重置单例（测试用）"""
        cls._instance = None
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """更新配置"""
        self._config = MergeConfig.from_dict(config)
        logger.info(f"[segment_merge] 配置更新: {config}")
    
    def get_buffer(self, session_id: str) -> SegmentMergeBuffer:
        """获取或创建会话的合并缓冲区"""
        if session_id not in self._buffers:
            self._buffers[session_id] = SegmentMergeBuffer(session_id, self._config)
            logger.debug(f"[segment_merge] 创建缓冲区: session={session_id}")
        return self._buffers[session_id]
    
    def process_event(self, session_id: str, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        处理一个 correction 事件。
        
        Args:
            session_id: 会话 ID
            event: correction 事件
            
        Returns:
            需要立即输出的事件列表
        """
        buffer = self.get_buffer(session_id)
        return buffer.process(event)
    
    def flush_session(self, session_id: str) -> List[Dict[str, Any]]:
        """刷新指定会话的缓冲区"""
        if session_id in self._buffers:
            events = self._buffers[session_id].flush()
            return events
        return []
    
    def cleanup_session(self, session_id: str) -> None:
        """清理会话的缓冲区"""
        if session_id in self._buffers:
            del self._buffers[session_id]
            logger.debug(f"[segment_merge] 清理缓冲区: session={session_id}")
    
    @property
    def config(self) -> MergeConfig:
        """获取当前配置"""
        return self._config
    
    @property
    def enabled(self) -> bool:
        """合并功能是否启用"""
        return self._config.enabled

