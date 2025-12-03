#!/usr/bin/env python3
"""
自动化 WebSocket 语音流测试脚本 (优化版)

功能：
1. 读取预录制的音频文件（WAV/PCM）
2. 模拟实时语音流发送到 WebSocket 服务
3. 验证识别结果
4. 支持快速发送模式测试识别性能

关键优化（参考 FunASR 官方 funasr_wss_client.py）：
- 并行发送/接收：使用多线程分离发送和接收任务，避免串行阻塞
- 快速发送模式：--fast 选项可不等待间隔直接发送，测试最大识别速度
- RTF 统计：实时显示实时率因子（Real-Time Factor）

使用方法：
    # 基本测试（模拟实时发送）
    python test_audio_stream.py --audio resource/asr_speaker_demo.wav

    # 快速发送模式（测试识别性能）
    python test_audio_stream.py --audio resource/asr_speaker_demo.wav --fast

    # 指定服务器地址
    python test_audio_stream.py --server ws://localhost:8210

    # 使用 pytest
    pytest test_audio_stream.py -v
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import wave
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from queue import Queue, Empty

import pytest

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import websocket  # websocket-client (同步库，Windows 兼容性好)
except ImportError:
    websocket = None

try:
    import soundfile as sf
    import numpy as np
except ImportError:
    sf = None
    np = None


# ============ 配置 ============

@dataclass
class StreamConfig:
    """流式测试配置"""
    server_url: str = "ws://localhost:8210/ws/recognize"
    sample_rate: int = 16000
    # FunASR 官方配置：chunk_size=[5,10,5], chunk_interval=10
    # stride = 60 * chunk_size[1] / chunk_interval / 1000 * sample_rate * 2
    # 默认: 60 * 10 / 10 / 1000 * 16000 * 2 = 1920 bytes = 960 samples
    chunk_size: List[int] = field(default_factory=lambda: [5, 10, 5])
    chunk_interval: int = 10  # ms，用于计算 stride
    mode: str = "2pass"
    enable_itn: bool = True
    timeout_seconds: float = 30.0
    verbose: bool = False
    realtime_display: bool = True  # 实时显示识别结果
    fast_mode: bool = False  # 快速发送模式（不等待间隔）
    clear_console: bool = True  # 是否清屏显示


@dataclass
class TestResult:
    """测试结果"""
    success: bool
    audio_file: str
    duration_seconds: float
    chunks_sent: int
    bytes_sent: int
    partial_results: List[str] = field(default_factory=list)
    correction_results: List[str] = field(default_factory=list)
    final_text: str = ""
    send_time_ms: float = 0.0  # 发送耗时
    total_time_ms: float = 0.0  # 总耗时
    rtf: float = 0.0  # Real-Time Factor (处理时间/音频时长)
    errors: List[str] = field(default_factory=list)
    raw_events: List[Dict[str, Any]] = field(default_factory=list)


# ============ 音频处理 ============

def load_audio_file(file_path: str, target_sample_rate: int = 16000) -> bytes:
    """
    加载音频文件并转换为 PCM 16-bit 格式
    
    Args:
        file_path: 音频文件路径 (支持 WAV, MP3, FLAC 等)
        target_sample_rate: 目标采样率
        
    Returns:
        PCM 16-bit 字节数据
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"音频文件不存在: {file_path}")
    
    # 尝试使用 soundfile
    if sf is not None:
        try:
            audio_data, sample_rate = sf.read(file_path, dtype='float32')
            
            # 转换为单声道
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # 重采样（简单线性插值）
            if sample_rate != target_sample_rate:
                ratio = target_sample_rate / sample_rate
                new_length = int(len(audio_data) * ratio)
                indices = np.linspace(0, len(audio_data) - 1, new_length)
                audio_data = np.interp(indices, np.arange(len(audio_data)), audio_data)
            
            # 转换为 16-bit PCM
            audio_data = np.clip(audio_data, -1.0, 1.0)
            pcm_data = (audio_data * 32767).astype(np.int16)
            return pcm_data.tobytes()
            
        except Exception as e:
            print(f"soundfile 加载失败: {e}, 尝试使用 wave 模块")
    
    # 回退到 wave 模块（仅支持 WAV）
    if path.suffix.lower() == '.wav':
        with wave.open(file_path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            
            audio_bytes = wf.readframes(n_frames)
            
            # 转换为 numpy 数组
            if sample_width == 2:
                dtype = np.int16
            elif sample_width == 1:
                dtype = np.int8
            else:
                raise ValueError(f"不支持的采样位深: {sample_width * 8} bits")
            
            if np is None:
                # 没有 numpy，直接返回原始数据
                return audio_bytes
                
            audio_data = np.frombuffer(audio_bytes, dtype=dtype)
            
            # 转换为单声道
            if n_channels > 1:
                audio_data = audio_data.reshape(-1, n_channels).mean(axis=1).astype(np.int16)
            
            # 简单重采样
            if framerate != target_sample_rate:
                ratio = target_sample_rate / framerate
                new_length = int(len(audio_data) * ratio)
                indices = np.linspace(0, len(audio_data) - 1, new_length)
                audio_data = np.interp(indices, np.arange(len(audio_data)), audio_data.astype(np.float32))
                audio_data = audio_data.astype(np.int16)
            
            return audio_data.tobytes()
    
    raise ValueError(f"不支持的音频格式: {path.suffix}")


def generate_silence(duration_ms: int, sample_rate: int = 16000) -> bytes:
    """生成静音数据"""
    num_samples = int(sample_rate * duration_ms / 1000)
    if np is not None:
        return np.zeros(num_samples, dtype=np.int16).tobytes()
    else:
        return b'\x00' * (num_samples * 2)


def generate_test_tone(duration_ms: int, frequency: int = 440, sample_rate: int = 16000) -> bytes:
    """生成测试音（正弦波）"""
    if np is None:
        return generate_silence(duration_ms, sample_rate)
    
    num_samples = int(sample_rate * duration_ms / 1000)
    t = np.arange(num_samples) / sample_rate
    signal = np.sin(2 * np.pi * frequency * t) * 0.5
    return (signal * 32767).astype(np.int16).tobytes()


# ============ WebSocket 客户端 ============

class AudioStreamTester:
    """音频流测试器（使用 websocket-client 同步库 + 多线程）"""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.ws = None
        self.events: List[Dict[str, Any]] = []
        self.partial_texts: List[str] = []
        self.correction_texts: List[str] = []
        # 累积文本状态（参考 FunASR 官方 funasr_wss_client.py）
        self.text_print_2pass_online: str = ""   # 在线流式累积
        self.text_print_2pass_offline: str = ""  # 离线纠错累积
        # 语义分段显示
        self.semantic_segments: List[str] = []   # 按语义分段的句子列表
        # 状态标记
        self._receiving = True
        self._send_done = False
        # 统计信息
        self._chunks_sent = 0
        self._bytes_sent = 0
        self._send_start_time = 0
        self._send_end_time = 0
        # 线程通信
        self._event_queue = Queue()
        self._error = None
    
    def _clear_console(self):
        """清除控制台"""
        import os
        os.system("cls" if os.name == "nt" else "clear")
    
    def _split_by_punctuation(self, text: str) -> List[str]:
        """按标点符号分割文本为语义段落"""
        import re
        # 按句号、问号、感叹号分割，保留标点
        # 支持中英文标点
        pattern = r'([。！？!?]+)'
        parts = re.split(pattern, text)
        
        # 合并标点和前面的句子
        segments = []
        current = ""
        for part in parts:
            if re.match(pattern, part):
                # 这是标点，合并到当前句子
                current += part
                if current.strip():
                    segments.append(current.strip())
                current = ""
            else:
                current += part
        
        # 处理最后没有标点的部分
        if current.strip():
            segments.append(current.strip())
        
        return segments
    
    def _print_realtime_display(self, audio_duration: float = 0):
        """打印实时累积显示（按语义分段，像会议纪要）"""
        if not self.config.realtime_display:
            return
        
        # 清屏并显示（可选）
        if self.config.clear_console:
            self._clear_console()
        
        # ANSI 颜色代码
        GREEN = "\033[32m"
        CYAN = "\033[36m"
        YELLOW = "\033[33m"
        DIM = "\033[2m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
        
        # 显示标题
        print(f"{CYAN}{'='*70}{RESET}")
        print(f"{CYAN}📝 实时语音识别 - 会议纪要模式{RESET}")
        print(f"{CYAN}{'='*70}{RESET}")
        
        # 显示统计信息
        elapsed = time.time() - self._send_start_time if self._send_start_time > 0 else 0
        mode_str = "🚀 快速模式" if self.config.fast_mode else "⏱️ 实时模式"
        print(f"{DIM}模式: {mode_str} | 已发送: {self._chunks_sent} 帧, {self._bytes_sent/1024:.1f}KB | 耗时: {elapsed:.1f}s{RESET}")
        if audio_duration > 0 and elapsed > 0:
            rtf = elapsed / audio_duration
            print(f"{DIM}音频时长: {audio_duration:.1f}s | RTF: {rtf:.2f}x{RESET}")
        print()
        
        # 显示已确认的语义段落（绿色）
        if self.semantic_segments:
            for i, segment in enumerate(self.semantic_segments):
                # 每个语义段落一行，带序号
                print(f"{GREEN}  {i+1}. {segment}{RESET}")
            print()  # 空行分隔
        
        # 显示当前正在识别的内容（黄色/灰色，表示未确认）
        if self.text_print_2pass_online:
            print(f"{YELLOW}{DIM}  ⏳ {self.text_print_2pass_online}{RESET}")
        
        print()
        sys.stdout.flush()
    
    def _handle_realtime_event(self, event: Dict[str, Any], audio_duration: float = 0):
        """处理实时事件并更新显示（参考 FunASR 官方 message() 函数）"""
        mode = event.get("mode", "")
        text = event.get("text", "")
        
        if not mode or not text:
            return
        
        # 参考 FunASR funasr_wss_client.py 的逻辑
        if mode == "online":
            # 纯在线模式
            self.text_print_2pass_online += text
        elif mode == "offline":
            # 纯离线模式：按标点分段
            self.text_print_2pass_offline += text
            self._update_semantic_segments()
        elif mode == "2pass-online":
            # 2pass 在线流式结果：累积追加
            self.text_print_2pass_online += text
        elif mode == "2pass-offline":
            # 2pass 离线纠错结果：清空在线，累积离线
            self.text_print_2pass_online = ""  # 清空在线结果
            self.text_print_2pass_offline += text  # 累积离线结果
            # 按标点重新分段
            self._update_semantic_segments()
        
        # 更新显示
        self._print_realtime_display(audio_duration)
    
    def _update_semantic_segments(self):
        """根据累积的离线文本更新语义分段"""
        if self.text_print_2pass_offline:
            self.semantic_segments = self._split_by_punctuation(self.text_print_2pass_offline)
        
    def connect(self) -> bool:
        """连接到 WebSocket 服务"""
        if websocket is None:
            raise ImportError("请安装 websocket-client: pip install websocket-client")
        
        try:
            self.ws = websocket.create_connection(
                self.config.server_url,
                timeout=10.0
            )
            if self.config.verbose:
                print(f"✓ 已连接到 {self.config.server_url}")
            return True
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None
    
    def _send_thread(self, pcm_data: bytes, audio_duration: float):
        """
        发送音频线程
        
        参考 FunASR 官方 record_from_scp() 函数
        """
        try:
            # 计算 stride（参考 FunASR 官方）
            # stride = 60 * chunk_size[1] / chunk_interval / 1000 * sample_rate * 2
            stride = int(60 * self.config.chunk_size[1] / self.config.chunk_interval / 1000 * self.config.sample_rate * 2)
            chunk_num = (len(pcm_data) - 1) // stride + 1
            
            # 计算发送间隔（参考 FunASR 官方）
            if self.config.fast_mode:
                sleep_duration = 0.001  # 快速模式：最小延迟
            else:
                # 实时模式：60 * chunk_size[1] / chunk_interval / 1000
                sleep_duration = 60 * self.config.chunk_size[1] / self.config.chunk_interval / 1000
            
            # 发送配置消息
            config_msg = {
                "mode": self.config.mode,
                "chunk_size": self.config.chunk_size,
                "chunk_interval": self.config.chunk_interval,
                "audio_fs": self.config.sample_rate,
                "wav_name": "auto-test",
                "wav_format": "pcm",
                "is_speaking": True,
                "itn": self.config.enable_itn,
            }
            self.ws.send(json.dumps(config_msg))
            if self.config.verbose:
                print(f"→ 发送配置: {config_msg}")
            
            self._send_start_time = time.time()
            
            # 分块发送音频
            for i in range(chunk_num):
                if not self._receiving:
                    break
                    
                beg = i * stride
                chunk = pcm_data[beg:beg + stride]
                
                self.ws.send_binary(chunk)
                self._chunks_sent += 1
                self._bytes_sent += len(chunk)
                
                # 最后一个块发送停止信号
                if i == chunk_num - 1:
                    stop_msg = {"is_speaking": False}
                    self.ws.send(json.dumps(stop_msg))
                    if self.config.verbose:
                        print("→ 发送停止信号")
                
                # 等待间隔
                time.sleep(sleep_duration)
            
            self._send_end_time = time.time()
            self._send_done = True
            
            if self.config.verbose:
                send_time = self._send_end_time - self._send_start_time
                print(f"✓ 发送完成: {self._chunks_sent} 帧, {self._bytes_sent/1024:.1f}KB, 耗时 {send_time:.2f}s")
                
        except Exception as e:
            self._error = str(e)
            self._send_done = True
    
    def _receive_thread(self, audio_duration: float):
        """
        接收消息线程
        
        参考 FunASR 官方 message() 函数
        """
        # 快速模式下需要更长的等待时间（因为发送很快，但处理需要时间）
        # 根据音频时长动态计算：假设处理速度约 RTF 0.1-0.2x，再加缓冲
        if self.config.fast_mode:
            # 快速模式：等待时间 = 音频时长 * 0.2 + 5秒缓冲
            final_wait_time = max(audio_duration * 0.2 + 5.0, 15.0)
        else:
            final_wait_time = 5.0
        
        try:
            self.ws.settimeout(1.0)
            
            while self._receiving:
                try:
                    msg = self.ws.recv()
                    if not msg:
                        continue
                        
                    event = json.loads(msg)
                    self.events.append(event)
                    
                    # 分类收集
                    event_type = event.get("type", "")
                    mode = event.get("mode", "")
                    text = event.get("text", "")
                    is_final = event.get("is_final", False)
                    
                    if event_type == "partial" or "online" in mode:
                        if text:
                            self.partial_texts.append(text)
                    elif event_type == "correction" or "offline" in mode:
                        if text:
                            self.correction_texts.append(text)
                    
                    # 实时显示
                    self._handle_realtime_event(event, audio_duration)
                    
                    if self.config.verbose:
                        print(f"← [{event_type or mode}] {text[:50]}{'...' if len(text) > 50 else ''}")
                    
                    # 如果是最终结果且发送已完成，可以退出
                    if is_final and self._send_done:
                        break
                        
                except websocket.WebSocketTimeoutException:
                    # 超时后检查是否应该继续
                    if self._send_done:
                        # 发送完成后，等待更长时间接收处理结果
                        wait_start = time.time()
                        while time.time() - wait_start < final_wait_time:
                            try:
                                self.ws.settimeout(1.0)
                                msg = self.ws.recv()
                                if not msg:
                                    continue
                                    
                                event = json.loads(msg)
                                self.events.append(event)
                                text = event.get("text", "")
                                mode = event.get("mode", "")
                                is_final = event.get("is_final", False)
                                
                                if "online" in mode and text:
                                    self.partial_texts.append(text)
                                elif "offline" in mode and text:
                                    self.correction_texts.append(text)
                                    
                                self._handle_realtime_event(event, audio_duration)
                                
                                # 收到最终结果就退出
                                if is_final:
                                    break
                            except websocket.WebSocketTimeoutException:
                                continue
                            except Exception:
                                break
                        break
                        
        except Exception as e:
            if self.config.verbose:
                print(f"接收错误: {e}")
        
        self._receiving = False
    
    def stream_audio(self, pcm_data: bytes) -> TestResult:
        """
        流式发送音频数据（多线程并行发送/接收）
        
        Args:
            pcm_data: PCM 16-bit 音频数据
            
        Returns:
            TestResult 测试结果
        """
        audio_duration = len(pcm_data) / 2 / self.config.sample_rate
        
        result = TestResult(
            success=False,
            audio_file="",
            duration_seconds=audio_duration,
            chunks_sent=0,
            bytes_sent=0
        )
        
        # 重置状态
        self._receiving = True
        self._send_done = False
        self._chunks_sent = 0
        self._bytes_sent = 0
        self._error = None
        
        start_time = time.time()
        
        try:
            # 创建发送和接收线程
            send_thread = threading.Thread(
                target=self._send_thread, 
                args=(pcm_data, audio_duration)
            )
            recv_thread = threading.Thread(
                target=self._receive_thread, 
                args=(audio_duration,)
            )
            
            # 启动线程
            recv_thread.start()
            send_thread.start()
            
            # 等待两个线程完成
            send_thread.join()
            recv_thread.join()
            
            end_time = time.time()
            
            # 检查错误
            if self._error:
                result.errors.append(self._error)
            
            # 计算统计信息
            result.chunks_sent = self._chunks_sent
            result.bytes_sent = self._bytes_sent
            result.send_time_ms = (self._send_end_time - self._send_start_time) * 1000 if self._send_end_time > 0 else 0
            result.total_time_ms = (end_time - start_time) * 1000
            result.rtf = (end_time - start_time) / audio_duration if audio_duration > 0 else 0
            
            # 整理结果
            result.partial_results = self.partial_texts.copy()
            result.correction_results = self.correction_texts.copy()
            result.final_text = self.text_print_2pass_offline + self.text_print_2pass_online
            result.raw_events = self.events.copy()
            result.success = len(result.errors) == 0
            
        except Exception as e:
            result.errors.append(str(e))
            if self.config.verbose or self.config.realtime_display:
                print(f"\n✗ 流式发送错误: {e}")
        
        return result


def run_audio_test(
    audio_file: str,
    config: Optional[StreamConfig] = None
) -> TestResult:
    """
    运行单个音频文件的测试
    
    Args:
        audio_file: 音频文件路径
        config: 测试配置
        
    Returns:
        TestResult 测试结果
    """
    config = config or StreamConfig()
    
    # 加载音频
    print(f"\n{'='*70}")
    print(f"📁 测试音频: {audio_file}")
    print(f"🌐 服务器: {config.server_url}")
    print(f"⚙️  模式: {config.mode} | {'🚀 快速发送' if config.fast_mode else '⏱️ 实时模拟'}")
    print(f"{'='*70}")
    
    try:
        pcm_data = load_audio_file(audio_file, config.sample_rate)
        duration = len(pcm_data) / 2 / config.sample_rate
        print(f"📊 音频时长: {duration:.2f}s, 大小: {len(pcm_data)/1024:.1f}KB")
    except Exception as e:
        return TestResult(
            success=False,
            audio_file=audio_file,
            duration_seconds=0,
            chunks_sent=0,
            bytes_sent=0,
            errors=[f"加载音频失败: {e}"]
        )
    
    # 创建测试器
    tester = AudioStreamTester(config)
    
    # 连接
    if not tester.connect():
        return TestResult(
            success=False,
            audio_file=audio_file,
            duration_seconds=duration,
            chunks_sent=0,
            bytes_sent=0,
            errors=["连接失败"]
        )
    
    try:
        # 流式发送
        result = tester.stream_audio(pcm_data)
        result.audio_file = audio_file
        
        # 打印结果摘要
        print(f"\n{'─'*70}")
        print(f"📈 性能统计")
        print(f"{'─'*70}")
        print(f"  发送帧数: {result.chunks_sent}")
        print(f"  发送字节: {result.bytes_sent / 1024:.1f}KB")
        print(f"  发送耗时: {result.send_time_ms:.0f}ms")
        print(f"  总耗时: {result.total_time_ms:.0f}ms")
        print(f"  RTF: {result.rtf:.2f}x (< 1.0 表示比实时快)")
        
        if result.partial_results:
            print(f"\n📝 实时结果 ({len(result.partial_results)} 条):")
            for i, text in enumerate(result.partial_results[-3:], 1):
                print(f"  {i}. {text[:60]}{'...' if len(text) > 60 else ''}")
        
        if result.correction_results:
            print(f"\n✅ 纠错结果 ({len(result.correction_results)} 条):")
            for i, text in enumerate(result.correction_results[-3:], 1):
                print(f"  {i}. {text[:60]}{'...' if len(text) > 60 else ''}")
        
        # 显示完整的最终文本（按语义分段）
        print(f"\n{'─'*70}")
        print(f"📄 完整识别文本 (共 {len(result.final_text)} 字):")
        print(f"{'─'*70}")
        
        final_text = result.final_text
        if final_text:
            # 按标点分段显示
            import re
            pattern = r'([。！？!?]+)'
            parts = re.split(pattern, final_text)
            
            # 合并标点和前面的句子
            segments = []
            current = ""
            for part in parts:
                if re.match(pattern, part):
                    current += part
                    if current.strip():
                        segments.append(current.strip())
                    current = ""
                else:
                    current += part
            if current.strip():
                segments.append(current.strip())
            
            # 显示每个语义段落
            for i, segment in enumerate(segments, 1):
                print(f"  {i}. {segment}")
        else:
            print("  (无识别结果)")
        
        print(f"{'='*70}\n")
        
        return result
        
    finally:
        tester.disconnect()


# ============ 测试用例 ============

# 查找测试音频文件
RESOURCE_DIR = PROJECT_ROOT / "resource"
SAMPLE_AUDIOS = [
    RESOURCE_DIR / "asr_speaker_demo.wav",
    RESOURCE_DIR / "1分20.wav",
    RESOURCE_DIR / "audio_data" / "0" / "014.wav",
]

# 获取第一个存在的音频文件
DEFAULT_AUDIO = None
for audio_path in SAMPLE_AUDIOS:
    if audio_path.exists():
        DEFAULT_AUDIO = str(audio_path)
        break


@pytest.fixture
def config():
    """测试配置 fixture"""
    return StreamConfig(
        server_url="ws://localhost:8210/ws/recognize",
        verbose=False
    )


@pytest.mark.skipif(websocket is None, reason="websocket-client not installed")
@pytest.mark.skipif(DEFAULT_AUDIO is None, reason="No test audio file found")
def test_basic_streaming(config):
    """基本流式识别测试"""
    result = run_audio_test(DEFAULT_AUDIO, config)
    assert result.success, f"测试失败: {result.errors}"
    assert result.chunks_sent > 0, "没有发送任何音频帧"


@pytest.mark.skipif(websocket is None, reason="websocket-client not installed")
def test_silence_handling(config):
    """静音处理测试"""
    silence = generate_silence(2000)  # 2秒静音
    
    tester = AudioStreamTester(config)
    if not tester.connect():
        pytest.skip("无法连接到服务器")
    
    try:
        result = tester.stream_audio(silence)
        assert result.success, f"测试失败: {result.errors}"
    finally:
        tester.disconnect()


@pytest.mark.skipif(websocket is None, reason="websocket-client not installed")
@pytest.mark.skipif(DEFAULT_AUDIO is None, reason="No test audio file found")
def test_multiple_modes(config):
    """多模式测试"""
    modes = ["2pass", "online", "offline"]
    
    for mode in modes:
        config.mode = mode
        result = run_audio_test(DEFAULT_AUDIO, config)
        # 只要不出错就算通过（某些模式可能没有结果）
        assert not result.errors or result.success, f"{mode} 模式测试失败: {result.errors}"


@pytest.mark.skipif(websocket is None, reason="websocket-client not installed")
def test_connection_handling(config):
    """连接处理测试"""
    tester = AudioStreamTester(config)
    
    # 测试连接
    connected = tester.connect()
    if not connected:
        pytest.skip("无法连接到服务器")
    
    # 测试断开
    tester.disconnect()
    assert tester.ws is None


@pytest.mark.skipif(websocket is None, reason="websocket-client not installed")
@pytest.mark.skipif(DEFAULT_AUDIO is None, reason="No test audio file found")
def test_fast_mode(config):
    """快速发送模式测试"""
    config.fast_mode = True
    result = run_audio_test(DEFAULT_AUDIO, config)
    assert result.success, f"测试失败: {result.errors}"


# ============ 批量测试 ============

def run_all_tests(config: StreamConfig):
    """运行所有测试"""
    results = []
    
    # 查找所有音频文件
    audio_files = []
    if RESOURCE_DIR.exists():
        for pattern in ["*.wav", "**/*.wav"]:
            audio_files.extend(RESOURCE_DIR.glob(pattern))
    
    # 限制测试文件数量
    audio_files = audio_files[:5]
    
    if not audio_files:
        print("未找到测试音频文件")
        return results
    
    print(f"\n找到 {len(audio_files)} 个音频文件")
    
    for audio_file in audio_files:
        result = run_audio_test(str(audio_file), config)
        results.append(result)
    
    # 汇总
    print("\n" + "="*70)
    print("📊 测试汇总")
    print("="*70)
    success_count = sum(1 for r in results if r.success)
    print(f"成功: {success_count}/{len(results)}")
    
    for result in results:
        status = "✓" if result.success else "✗"
        rtf_str = f"RTF: {result.rtf:.2f}" if result.rtf > 0 else ""
        print(f"  {status} {Path(result.audio_file).name}: {result.final_text[:40]}... {rtf_str}")
    
    return results


# ============ 命令行入口 ============

def main():
    parser = argparse.ArgumentParser(description="WebSocket 语音流自动化测试 (优化版)")
    parser.add_argument("--audio", "-a", default=DEFAULT_AUDIO, help="音频文件路径")
    parser.add_argument("--server", "-s", default="ws://localhost:8210/ws/recognize", help="服务器地址")
    parser.add_argument("--mode", "-m", default="2pass", choices=["2pass", "online", "offline"], help="识别模式")
    parser.add_argument("--fast", "-f", action="store_true", help="快速发送模式（不模拟实时）")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--no-realtime", action="store_true", help="禁用实时显示")
    parser.add_argument("--no-clear", action="store_true", help="禁用清屏（便于查看日志）")
    parser.add_argument("--run-all", action="store_true", help="运行所有测试")
    
    args = parser.parse_args()
    
    config = StreamConfig(
        server_url=args.server,
        mode=args.mode,
        fast_mode=args.fast,
        verbose=args.verbose,
        realtime_display=not args.no_realtime,
        clear_console=not args.no_clear
    )
    
    if args.run_all:
        run_all_tests(config)
    elif args.audio:
        run_audio_test(args.audio, config)
    else:
        print("请指定音频文件 (--audio) 或使用 --run-all 运行所有测试")
        print(f"\n可用的测试音频:")
        for audio in SAMPLE_AUDIOS:
            exists = "✓" if audio.exists() else "✗"
            print(f"  {exists} {audio}")
        print(f"\n示例:")
        print(f"  python test_audio_stream.py --audio resource/asr_speaker_demo.wav")
        print(f"  python test_audio_stream.py --audio resource/asr_speaker_demo.wav --fast")


if __name__ == "__main__":
    main()
