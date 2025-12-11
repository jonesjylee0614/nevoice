"""
片段合并模块单元测试。

测试场景：
1. 短句合并 - 同一说话人、间隔短的短句应该合并
2. 说话人切换断开 - 不同说话人的句子不合并
3. 标点断开 - 以句末标点结尾的句子不与后面合并
4. 时间间隔断开 - 超过 max_gap_ms 的句子不合并
5. 短句过滤 - 无法合并的超短句应被过滤
"""

import pytest
import sys
import os

# 添加项目路径（直接到 streaming 目录，避免加载整个 server 模块）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
streaming_path = os.path.join(project_root, "speech_recognition", "streaming")
sys.path.insert(0, streaming_path)

# 直接导入 segment_merge 模块
from segment_merge import (
    SegmentMergeManager,
    SegmentMergeBuffer,
    MergeConfig,
    PendingSegment,
)


class TestSegmentMerge:
    """片段合并测试类"""
    
    def setup_method(self):
        """每个测试前重置单例"""
        SegmentMergeManager.reset()
    
    def _make_event(
        self,
        text: str,
        start_ms: int,
        end_ms: int,
        speaker_id: int = None,
        speaker_name: str = "未知发言人",
    ) -> dict:
        """创建测试用的 correction 事件"""
        event = {
            "type": "correction",
            "mode": "2pass-offline",
            "text": text,
            "is_final": True,
            "session_id": "test-session",
            "segment_id": f"seg-{start_ms}",
            "start_offset_ms": start_ms,
            "end_offset_ms": end_ms,
            "duration_ms": end_ms - start_ms,
            "audio_path": None,
            "audio_data": None,
        }
        if speaker_id is not None:
            event["speaker_info"] = {
                "speaker_id": speaker_id,
                "speaker_name": speaker_name,
                "recognized": True,
            }
        return event
    
    def test_short_sentence_merge(self):
        """测试短句合并 - 同一说话人、间隔短的短句应该合并"""
        manager = SegmentMergeManager.current({
            "enabled": True,
            "max_gap_ms": 3000,
            "min_text_length": 4,
            "min_duration_ms": 800,
            "force_break_punctuation": ['。', '！', '？', '!', '?'],
        })
        
        session_id = "test-session-1"
        
        # 第一个事件：短句，缓冲
        event1 = self._make_event("好", 0, 500, speaker_id=1, speaker_name="张三")
        result1 = manager.process_event(session_id, event1)
        assert len(result1) == 0, "短句应该被缓冲，不立即输出"
        
        # 第二个事件：短句，间隔 1 秒，应该合并
        event2 = self._make_event("我知道了", 1500, 3000, speaker_id=1, speaker_name="张三")
        result2 = manager.process_event(session_id, event2)
        assert len(result2) == 0, "应该合并到缓冲区"
        
        # 刷新输出
        flush_result = manager.flush_session(session_id)
        assert len(flush_result) == 1, "刷新应该输出一个合并后的事件"
        assert flush_result[0]["text"] == "好我知道了", "文本应该合并"
        assert flush_result[0]["start_offset_ms"] == 0, "起始时间应该是第一个事件的"
        assert flush_result[0]["end_offset_ms"] == 3000, "结束时间应该是最后一个事件的"
    
    def test_speaker_change_break(self):
        """测试说话人切换断开 - 不同说话人的句子不合并"""
        manager = SegmentMergeManager.current({
            "enabled": True,
            "max_gap_ms": 3000,
        })
        
        session_id = "test-session-2"
        
        # 张三说的话
        event1 = self._make_event("差不多一个多亿吧", 0, 2000, speaker_id=1, speaker_name="张三")
        result1 = manager.process_event(session_id, event1)
        assert len(result1) == 0, "第一个事件应该被缓冲"
        
        # 李四说的话（说话人变了）
        event2 = self._make_event("嗯", 2500, 3000, speaker_id=2, speaker_name="李四")
        result2 = manager.process_event(session_id, event2)
        
        # 因为说话人变了，应该输出张三的话
        assert len(result2) == 1, "说话人变化应该立即输出前一条"
        assert result2[0]["text"] == "差不多一个多亿吧", "应该是张三说的话"
        
        # 刷新输出李四的话
        flush_result = manager.flush_session(session_id)
        # 李四的"嗯"太短，可能被过滤
        # 这取决于配置的 min_text_length
    
    def test_punctuation_break(self):
        """测试标点断开 - 以句末标点结尾的句子不与后面合并"""
        manager = SegmentMergeManager.current({
            "enabled": True,
            "max_gap_ms": 3000,
            "force_break_punctuation": ['。', '！', '？', '!', '?'],
        })
        
        session_id = "test-session-3"
        
        # 以句号结尾的句子
        event1 = self._make_event("今天天气真好。", 0, 2000, speaker_id=1)
        result1 = manager.process_event(session_id, event1)
        assert len(result1) == 0, "第一个事件应该被缓冲"
        
        # 下一个句子（同一说话人，间隔短）
        event2 = self._make_event("我们去公园吧", 2500, 4000, speaker_id=1)
        result2 = manager.process_event(session_id, event2)
        
        # 因为前一句以句号结尾，不应该合并
        assert len(result2) == 1, "句号结尾应该立即输出前一条"
        assert result2[0]["text"] == "今天天气真好。", "应该保持原样"
    
    def test_time_gap_break(self):
        """测试时间间隔断开 - 超过 max_gap_ms 的句子不合并"""
        manager = SegmentMergeManager.current({
            "enabled": True,
            "max_gap_ms": 3000,  # 3 秒
        })
        
        session_id = "test-session-4"
        
        # 第一个事件
        event1 = self._make_event("你好", 0, 1000, speaker_id=1)
        result1 = manager.process_event(session_id, event1)
        assert len(result1) == 0
        
        # 第二个事件，间隔 5 秒（超过 max_gap_ms）
        event2 = self._make_event("再见", 6000, 7000, speaker_id=1)
        result2 = manager.process_event(session_id, event2)
        
        # 间隔太长，应该输出前一条
        assert len(result2) == 1, "间隔超过阈值应该立即输出前一条"
        assert result2[0]["text"] == "你好"
    
    def test_short_sentence_filter(self):
        """测试短句过滤 - 无法合并的超短句应被过滤"""
        manager = SegmentMergeManager.current({
            "enabled": True,
            "max_gap_ms": 3000,
            "min_text_length": 4,  # 至少 4 个字符
            "min_duration_ms": 800,  # 至少 800ms
        })
        
        session_id = "test-session-5"
        
        # 超短句
        event1 = self._make_event("嗯", 0, 300, speaker_id=1)  # 只有 300ms
        result1 = manager.process_event(session_id, event1)
        
        # 另一个说话人，触发输出
        event2 = self._make_event("今天开会讨论什么", 5000, 7000, speaker_id=2)
        result2 = manager.process_event(session_id, event2)
        
        # 第一个事件应该被过滤（太短且无法合并）
        # 过滤发生在无法合并时
        assert len(result2) == 0 or result2[0].get("text") != "嗯", "超短句应该被过滤"
    
    def test_disabled_mode(self):
        """测试禁用模式 - 直接输出不合并"""
        manager = SegmentMergeManager.current({
            "enabled": False,
        })
        
        session_id = "test-session-6"
        
        event1 = self._make_event("好", 0, 500, speaker_id=1)
        result1 = manager.process_event(session_id, event1)
        
        # 禁用模式下直接输出
        assert len(result1) == 1, "禁用模式应该直接输出"
        assert result1[0]["text"] == "好"
    
    def test_flush_outputs_buffer(self):
        """测试刷新输出缓冲区"""
        manager = SegmentMergeManager.current({
            "enabled": True,
            "max_gap_ms": 3000,
        })
        
        session_id = "test-session-7"
        
        # 添加一个事件
        event1 = self._make_event("这是一个测试句子", 0, 3000, speaker_id=1)
        result1 = manager.process_event(session_id, event1)
        assert len(result1) == 0, "应该被缓冲"
        
        # 刷新
        flush_result = manager.flush_session(session_id)
        assert len(flush_result) == 1, "刷新应该输出缓冲的事件"
        assert flush_result[0]["text"] == "这是一个测试句子"
        
        # 再次刷新应该为空
        flush_result2 = manager.flush_session(session_id)
        assert len(flush_result2) == 0, "缓冲区已清空"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

