"""FunASRStreamer 组件单元测试。"""

import pytest
from unittest.mock import MagicMock, patch

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from speech_recognition.streaming.funasr_streamer import (
    FunASRStreamer,
    FunASRStreamerConfig,
    FunASRStreamerState,
    StreamingEvent,
)


class TestFunASRStreamerConfig:
    """测试 FunASRStreamerConfig 配置类。"""

    def test_default_config(self):
        """测试默认配置。"""
        config = FunASRStreamerConfig()
        assert config.mode == "2pass"
        assert config.chunk_interval == 10
        assert config.chunk_size == [5, 10, 5]
        assert config.sample_rate == 16000
        assert config.enable_vad is True
        assert config.enable_punc is True
        assert config.enable_itn is True
        assert config.itn_language == "zh"

    def test_custom_config(self):
        """测试自定义配置。"""
        config = FunASRStreamerConfig(
            mode="online",
            chunk_interval=20,
            enable_vad=False,
        )
        assert config.mode == "online"
        assert config.chunk_interval == 20
        assert config.enable_vad is False


class TestFunASRStreamerState:
    """测试 FunASRStreamerState 状态类。"""

    def test_initial_state(self):
        """测试初始状态。"""
        state = FunASRStreamerState()
        assert state.vad_pre_idx == 0
        assert state.speech_start is False
        assert state.is_speaking is True
        assert len(state.frames) == 0

    def test_reset(self):
        """测试状态重置。"""
        state = FunASRStreamerState()
        state.vad_pre_idx = 100
        state.speech_start = True
        state.frames.append(b"test")
        
        state.reset()
        
        assert state.vad_pre_idx == 0
        assert state.speech_start is False
        assert len(state.frames) == 0


class TestStreamingEvent:
    """测试 StreamingEvent 事件类。"""

    def test_to_dict(self):
        """测试转换为字典。"""
        event = StreamingEvent(
            type="partial",
            mode="2pass-online",
            text="你好",
            is_final=False,
            wav_name="test",
        )
        
        d = event.to_dict()
        assert d["type"] == "partial"
        assert d["mode"] == "2pass-online"
        assert d["text"] == "你好"
        assert d["is_final"] is False
        assert d["wav_name"] == "test"


class TestFunASRStreamer:
    """测试 FunASRStreamer 流式组件。"""

    @pytest.fixture
    def mock_models(self):
        """创建模拟模型。"""
        model_asr = MagicMock()
        model_asr.generate.return_value = [{"text": "离线识别结果"}]
        
        model_asr_online = MagicMock()
        model_asr_online.generate.return_value = [{"text": "在线识别结果", "cache": {}}]
        
        model_vad = MagicMock()
        model_vad.generate.return_value = [{"value": [[-1, -1]], "cache": {}}]
        
        model_punc = MagicMock()
        model_punc.generate.return_value = [{"text": "带标点的结果。"}]
        
        return model_asr, model_asr_online, model_vad, model_punc

    def test_create_state(self, mock_models):
        """测试创建状态。"""
        model_asr, model_asr_online, model_vad, model_punc = mock_models
        
        config = FunASRStreamerConfig(enable_itn=False)
        streamer = FunASRStreamer(
            model_asr=model_asr,
            model_asr_online=model_asr_online,
            model_vad=model_vad,
            model_punc=model_punc,
            config=config,
        )
        
        state = streamer.create_state()
        assert isinstance(state, FunASRStreamerState)

    def test_process_chunk_online(self, mock_models):
        """测试处理音频块（在线模式）。"""
        model_asr, model_asr_online, model_vad, model_punc = mock_models
        
        config = FunASRStreamerConfig(
            mode="online",
            chunk_interval=1,  # 每个 chunk 都触发在线识别
            enable_vad=False,
            enable_itn=False,
        )
        streamer = FunASRStreamer(
            model_asr=model_asr,
            model_asr_online=model_asr_online,
            model_vad=model_vad,
            model_punc=model_punc,
            config=config,
        )
        
        state = streamer.create_state()
        # 模拟 32ms 的音频数据（16kHz, 16bit = 1024 bytes）
        audio_chunk = b"\x00" * 1024
        
        events = streamer.process_chunk(audio_chunk, state)
        
        assert len(events) == 1
        assert events[0].type == "partial"
        assert events[0].mode == "online"
        assert events[0].text == "在线识别结果"

    def test_process_chunk_2pass(self, mock_models):
        """测试处理音频块（2pass 模式）。"""
        model_asr, model_asr_online, model_vad, model_punc = mock_models
        
        # VAD 检测到语音开始和结束
        model_vad.generate.side_effect = [
            [{"value": [[100, -1]], "cache": {}}],  # 语音开始
            [{"value": [[-1, 200]], "cache": {}}],  # 语音结束
        ]
        
        config = FunASRStreamerConfig(
            mode="2pass",
            chunk_interval=1,
            enable_itn=False,
        )
        streamer = FunASRStreamer(
            model_asr=model_asr,
            model_asr_online=model_asr_online,
            model_vad=model_vad,
            model_punc=model_punc,
            config=config,
        )
        
        state = streamer.create_state()
        audio_chunk = b"\x00" * 1024
        
        # 第一个 chunk（语音开始）
        events1 = streamer.process_chunk(audio_chunk, state)
        assert len(events1) == 1
        assert events1[0].type == "partial"
        
        # 第二个 chunk（语音结束）
        events2 = streamer.process_chunk(audio_chunk, state)
        # 应该有离线纠错结果
        correction_events = [e for e in events2 if e.type == "correction"]
        assert len(correction_events) >= 1

    def test_flush(self, mock_models):
        """测试 flush 刷新缓冲。"""
        model_asr, model_asr_online, model_vad, model_punc = mock_models
        
        config = FunASRStreamerConfig(
            mode="2pass",
            chunk_interval=100,  # 不会触发在线识别
            enable_vad=False,
            enable_itn=False,
        )
        streamer = FunASRStreamer(
            model_asr=model_asr,
            model_asr_online=model_asr_online,
            model_vad=model_vad,
            model_punc=model_punc,
            config=config,
        )
        
        state = streamer.create_state()
        audio_chunk = b"\x00" * 1024
        
        # 先 push 一些数据
        streamer.process_chunk(audio_chunk, state)
        state.frames_asr.append(audio_chunk)
        
        # flush
        events = streamer.flush(state)
        
        # 应该有离线纠错结果
        assert len(events) >= 1


class TestPostprocessNumbers:
    """测试中文数字后处理。"""

    def test_postprocess_numbers_basic(self):
        """测试基本数字转换。"""
        # 这个测试需要 cn2an 安装
        try:
            import cn2an
        except ImportError:
            pytest.skip("cn2an not installed")
        
        result = FunASRStreamer._postprocess_numbers("一百二十三")
        assert result == "123"

    def test_postprocess_numbers_percent(self):
        """测试百分比转换。"""
        try:
            import cn2an
        except ImportError:
            pytest.skip("cn2an not installed")
        
        result = FunASRStreamer._postprocess_numbers("百分之五十")
        assert result == "50%"

    def test_postprocess_numbers_with_unit(self):
        """测试带单位的数字转换。"""
        try:
            import cn2an
        except ImportError:
            pytest.skip("cn2an not installed")
        
        result = FunASRStreamer._postprocess_numbers("三点五万")
        assert result == "3.5万"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

