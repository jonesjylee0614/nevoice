"""
E-Voice 智能语音识别系统 REST API服务器
====================================

主要功能：
1. 语音注册 - 上传音频文件，提取声纹特征并存储
2. 离线语音识别 - 上传音频文件进行语音转文字
3. 在线语音识别 - 实时流式语音识别
4. Embedding向量化 - 通用数据向量化接口
5. WebSocket实时语音处理

技术栈：
- Flask + SocketIO + CORS
- es 向量数据库
- ModelScope语音识别模型
- SoundFile/PyDub音频处理

注意事项：
- 使用相对路径存储音频文件 (data/voice/print/)
- 支持环境变量PORT配置端口 (默认8210)
- 需要安装libsox-dev支持音频重采样
"""

import base64
import io
import json
import os
import time
import traceback
import uuid

import numpy as np
import soundfile as sf
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sock import Sock
from flask_socketio import SocketIO, emit
from loguru import logger
from numba import int64
from pydub import AudioSegment

from config.config import conf
from es.voice import insert_voice
from pipeline.spk_v_pipeline import embedding
from rest_meeting import meeting_app
from rest_prints import print_app
from speech_recognition.recognize import recognize

# ================== 日志配置 ==================
# 创建logs目录
os.makedirs("logs", exist_ok=True)

# 配置loguru日志
logger.remove()  # 移除默认处理器

# 控制台日志 - 只显示重要信息
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    colorize=True
)

# WebSocket实时语音识别专用日志（会话/消息）
ws_logger = logger.bind(component="ws")
ws_logger.add(
    "logs/websocket_speech.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[component]} | {function}:{line} | {message}",
    rotation="50 MB",
    retention="7 days",
    encoding="utf-8",
    filter=lambda record: record["extra"].get("component") == "ws"
)

# 错误日志
logger.add(
    "logs/error.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {function}:{line} | {message}\n{exception}",
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8"
)

# 音频处理详细日志
audio_logger = logger.bind(component="audio")
audio_logger.add(
    "logs/audio_processing.log",
    level="TRACE",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[component]} | {function}:{line} | {message}",
    rotation="100 MB",
    retention="3 days",
    encoding="utf-8",
    filter=lambda record: record["extra"].get("component") == "audio"
)

# 语音识别结果日志
recognition_logger = logger.bind(component="recognition")
recognition_logger.add(
    "logs/recognition_results.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[component]} | {message}",
    rotation="50 MB",
    retention="7 days",
    encoding="utf-8",
    filter=lambda record: record["extra"].get("component") == "recognition"
)

logger.info("日志系统初始化完成")
logger.info("WebSocket语音识别日志: logs/websocket_speech.log")
logger.info("音频处理日志: logs/audio_processing.log")
logger.info("识别结果日志: logs/recognition_results.log")
logger.info("错误日志: logs/error.log")

# 关键事件日志（精简关键信息，便于排查）
key_logger = logger.bind(component="key")
key_logger.add(
    "logs/realtime_key.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[component]} | {message}",
    rotation="20 MB",
    retention="14 days",
    encoding="utf-8",
    filter=lambda record: record["extra"].get("component") == "key"
)

# ================== 增强热词管理系统 ==================
_hotword_manager = None

class EnhancedHotwordManager:
    """
    增强热词管理器 - 支持动态更新和个性化学习
    """
    
    def __init__(self):
        self.hotword_dir = os.path.join("data", "hotwords")
        self.static_file = os.path.join(self.hotword_dir, "replace_map.json")
        self.dynamic_file = os.path.join(self.hotword_dir, "dynamic_hotwords.json")
        self.user_learning_file = os.path.join(self.hotword_dir, "user_learning.json")
        
        # 确保目录存在
        os.makedirs(self.hotword_dir, exist_ok=True)
        
        self.static_hotwords = {}  # 静态热词映射
        self.dynamic_hotwords = {}  # 动态热词映射
        self.user_corrections = {}  # 用户纠错记录
        self.hotword_usage_stats = {}  # 热词使用统计
        
        self._load_all_hotwords()
    
    def _load_all_hotwords(self):
        """加载所有热词数据"""
        # 加载静态热词
        try:
            if os.path.exists(self.static_file):
                with open(self.static_file, "r", encoding="utf-8") as f:
                    self.static_hotwords = json.load(f)
            else:
                # 默认静态热词
                self.static_hotwords = {
                    "语数科技": "宇树科技",
                    "宇数科技": "宇树科技",
                    "GPT": "GPT",
                    "AI": "AI",
                    "机器学习": "机器学习",
                    "深度学习": "深度学习"
                }
                self._save_static_hotwords()
        except Exception as e:
            recognition_logger.warning(f"加载静态热词失败: {e}")
            self.static_hotwords = {}
        
        # 加载动态热词
        try:
            if os.path.exists(self.dynamic_file):
                with open(self.dynamic_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.dynamic_hotwords = data.get("hotwords", {})
                    self.hotword_usage_stats = data.get("usage_stats", {})
        except Exception as e:
            recognition_logger.warning(f"加载动态热词失败: {e}")
            self.dynamic_hotwords = {}
            self.hotword_usage_stats = {}
        
        # 加载用户学习记录
        try:
            if os.path.exists(self.user_learning_file):
                with open(self.user_learning_file, "r", encoding="utf-8") as f:
                    self.user_corrections = json.load(f)
        except Exception as e:
            recognition_logger.warning(f"加载用户学习记录失败: {e}")
            self.user_corrections = {}
        
        recognition_logger.info(f"📚 热词管理器加载完成: 静态{len(self.static_hotwords)}个, 动态{len(self.dynamic_hotwords)}个, 用户学习{len(self.user_corrections)}个")
    
    def get_all_hotwords(self):
        """获取所有热词映射（按优先级排序）"""
        all_hotwords = {}
        
        # 1. 静态热词（基础权重）
        all_hotwords.update(self.static_hotwords)
        
        # 2. 动态热词（中等权重）
        all_hotwords.update(self.dynamic_hotwords)
        
        # 3. 用户学习热词（最高权重）
        all_hotwords.update(self.user_corrections)
        
        return all_hotwords
    
    def add_dynamic_hotword(self, wrong_word, correct_word, source="system"):
        """
        添加动态热词
        
        Args:
            wrong_word: 错误识别的词
            correct_word: 正确的词
            source: 来源标识
        """
        self.dynamic_hotwords[wrong_word] = correct_word
        
        # 更新使用统计
        key = f"{wrong_word}->{correct_word}"
        if key not in self.hotword_usage_stats:
            self.hotword_usage_stats[key] = {
                "count": 0,
                "first_added": int(time.time()),
                "last_used": int(time.time()),
                "source": source
            }
        
        self.hotword_usage_stats[key]["count"] += 1
        self.hotword_usage_stats[key]["last_used"] = int(time.time())
        
        # 保存到文件
        self._save_dynamic_hotwords()
        
        recognition_logger.info(f"📚 添加动态热词: '{wrong_word}' -> '{correct_word}' (来源: {source})")
    
    def learn_from_correction(self, original_text, corrected_text):
        """
        从用户纠错中学习
        
        Args:
            original_text: 原始识别文本
            corrected_text: 用户纠正后的文本
        """
        if not original_text or not corrected_text or original_text == corrected_text:
            return
        
        # 简单的词级别差异检测
        original_words = original_text.split()
        corrected_words = corrected_text.split()
        
        # 如果长度相同，检测词级别的替换
        if len(original_words) == len(corrected_words):
            for orig, corr in zip(original_words, corrected_words):
                if orig != corr and len(orig) > 1 and len(corr) > 1:
                    self.user_corrections[orig] = corr
                    recognition_logger.info(f"🎯 用户纠错学习: '{orig}' -> '{corr}'")
        else:
            # 整句级别的替换（简化处理）
            if len(original_text) > 2 and len(corrected_text) > 2:
                self.user_corrections[original_text] = corrected_text
                recognition_logger.info(f"🎯 用户句子纠错: '{original_text}' -> '{corrected_text}'")
        
        # 保存学习记录
        self._save_user_learning()
    
    def apply_hotword_replacement(self, text):
        """
        应用热词替换
        
        Args:
            text: 原始文本
            
        Returns:
            str: 替换后的文本
        """
        if not text:
            return text
        
        result = text
        all_hotwords = self.get_all_hotwords()
        
        # 按长度排序，优先替换长词组
        sorted_hotwords = sorted(all_hotwords.items(), key=lambda x: len(x[0]), reverse=True)
        
        replaced_count = 0
        for wrong_word, correct_word in sorted_hotwords:
            if wrong_word in result:
                result = result.replace(wrong_word, correct_word)
                replaced_count += 1
                
                # 更新使用统计
                key = f"{wrong_word}->{correct_word}"
                if key in self.hotword_usage_stats:
                    self.hotword_usage_stats[key]["count"] += 1
                    self.hotword_usage_stats[key]["last_used"] = int(time.time())
        
        if replaced_count > 0:
            recognition_logger.debug(f"📚 热词替换: '{text}' -> '{result}' (替换{replaced_count}个)")
            # 异步保存统计（避免频繁IO）
            if replaced_count > 0:
                self._save_dynamic_hotwords()
        
        return result
    
    def get_hotword_suggestions(self, partial_text, limit=5):
        """
        获取热词建议（自动补全）
        
        Args:
            partial_text: 部分文本
            limit: 建议数量限制
            
        Returns:
            list: 建议的热词列表
        """
        if not partial_text or len(partial_text) < 2:
            return []
        
        all_hotwords = self.get_all_hotwords()
        suggestions = []
        
        partial_lower = partial_text.lower()
        
        # 查找以partial_text开头的热词
        for correct_word in all_hotwords.values():
            if correct_word.lower().startswith(partial_lower) and correct_word not in suggestions:
                suggestions.append(correct_word)
                if len(suggestions) >= limit:
                    break
        
        # 查找包含partial_text的热词
        if len(suggestions) < limit:
            for correct_word in all_hotwords.values():
                if (partial_lower in correct_word.lower() and 
                    not correct_word.lower().startswith(partial_lower) and 
                    correct_word not in suggestions):
                    suggestions.append(correct_word)
                    if len(suggestions) >= limit:
                        break
        
        return suggestions
    
    def cleanup_old_hotwords(self, days_threshold=90):
        """
        清理长期未使用的动态热词
        
        Args:
            days_threshold: 天数阈值
        """
        current_time = int(time.time())
        threshold_time = current_time - (days_threshold * 24 * 3600)
        
        to_remove = []
        for key, stats in self.hotword_usage_stats.items():
            if stats["last_used"] < threshold_time and stats["count"] < 3:
                # 90天未使用且使用次数少于3次的热词
                wrong_word = key.split("->")[0]
                if wrong_word in self.dynamic_hotwords:
                    to_remove.append(wrong_word)
        
        for word in to_remove:
            del self.dynamic_hotwords[word]
            # 清理相关统计
            keys_to_remove = [k for k in self.hotword_usage_stats.keys() if k.startswith(word + "->")]
            for k in keys_to_remove:
                del self.hotword_usage_stats[k]
        
        if to_remove:
            recognition_logger.info(f"🗑️ 清理{len(to_remove)}个长期未使用的动态热词: {to_remove}")
            self._save_dynamic_hotwords()
        
        return len(to_remove)
    
    def _save_static_hotwords(self):
        """保存静态热词"""
        try:
            with open(self.static_file, "w", encoding="utf-8") as f:
                json.dump(self.static_hotwords, f, ensure_ascii=False, indent=2)
        except Exception as e:
            recognition_logger.error(f"保存静态热词失败: {e}")
    
    def _save_dynamic_hotwords(self):
        """保存动态热词和使用统计"""
        try:
            data = {
                "hotwords": self.dynamic_hotwords,
                "usage_stats": self.hotword_usage_stats,
                "last_updated": int(time.time())
            }
            with open(self.dynamic_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            recognition_logger.error(f"保存动态热词失败: {e}")
    
    def _save_user_learning(self):
        """保存用户学习记录"""
        try:
            data = {
                **self.user_corrections,
                "_meta": {
                    "last_updated": int(time.time()),
                    "total_corrections": len(self.user_corrections)
                }
            }
            with open(self.user_learning_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            recognition_logger.error(f"保存用户学习记录失败: {e}")

def _get_hotword_manager():
    """获取热词管理器实例（单例模式）"""
    global _hotword_manager
    if _hotword_manager is None:
        _hotword_manager = EnhancedHotwordManager()
    return _hotword_manager

def _load_hotword_replace_map():
    """兼容旧接口的热词加载函数"""
    manager = _get_hotword_manager()
    return manager.get_all_hotwords()

def detect_voice_command(text: str):
    """
    语音指令识别系统 - 区分指令和文本内容
    
    Args:
        text: 输入的识别文本
        
    Returns:
        dict: {
            'is_command': bool,  # 是否是指令
            'command_type': str,  # 指令类型
            'command_params': dict,  # 指令参数
            'processed_text': str  # 处理后的文本（如果不是指令）
        }
    """
    if not text or not text.strip():
        return {
            'is_command': False,
            'command_type': None,
            'command_params': {},
            'processed_text': text
        }
    
    text_lower = text.lower().strip()
    
    # 🎯 编辑类指令
    edit_commands = {
        # 删除指令
        '删除': {'type': 'delete', 'target': 'last_word'},
        '删掉': {'type': 'delete', 'target': 'last_word'},
        '删除刚刚说的': {'type': 'delete', 'target': 'last_sentence'},
        '删掉刚刚说的': {'type': 'delete', 'target': 'last_sentence'},
        '删除最后一个字': {'type': 'delete', 'target': 'last_char'},
        '删除全部': {'type': 'delete', 'target': 'all'},
        '清除全部': {'type': 'delete', 'target': 'all'},
        '全部删除': {'type': 'delete', 'target': 'all'},
        
        # 撤销指令
        '撤销': {'type': 'undo'},
        '撤回': {'type': 'undo'},
        
        # 重做指令
        '重做': {'type': 'redo'},
        '恢复': {'type': 'redo'},
    }
    
    # 🎯 标点类指令
    punctuation_commands = {
        '逗号': ',',
        '句号': '。',
        '问号': '？',
        '叹号': '！',
        '感叹号': '！',
        '冒号': '：',
        '分号': '；',
        '顿号': '、',
        '省略号': '……',
        '引号': '""',
        '书名号': '《》',
        '括号': '（）',
        '小括号': '（）',
        '中括号': '【】',
        '双引号': '""',
       '单引号': "'"
    }
    
    # 🎯 格式类指令
    format_commands = {
        '换行': {'type': 'format', 'action': 'newline'},
        '回车': {'type': 'format', 'action': 'newline'},
        '空格': {'type': 'format', 'action': 'space'},
        '空一格': {'type': 'format', 'action': 'space'},
        '制表符': {'type': 'format', 'action': 'tab'},
        '缩进': {'type': 'format', 'action': 'tab'},
    }
    
    # 🎯 功能类指令  
    function_commands = {
        '发送': {'type': 'function', 'action': 'send'},
        '确认': {'type': 'function', 'action': 'confirm'},
        '取消': {'type': 'function', 'action': 'cancel'},
        '完成': {'type': 'function', 'action': 'complete'},
    }
    
    # 检查编辑类指令
    for cmd, params in edit_commands.items():
        if text_lower == cmd or text_lower.endswith(cmd):
            return {
                'is_command': True,
                'command_type': 'edit',
                'command_params': params,
                'processed_text': ''
            }
    
    # 检查标点类指令
    for cmd, punctuation in punctuation_commands.items():
        if text_lower == cmd:
            return {
                'is_command': True,
                'command_type': 'punctuation',
                'command_params': {'punctuation': punctuation},
                'processed_text': punctuation
            }
    
    # 检查格式类指令
    for cmd, params in format_commands.items():
        if text_lower == cmd:
            return {
                'is_command': True,
                'command_type': 'format',
                'command_params': params,
                'processed_text': _format_action_to_text(params['action'])
            }
    
    # 检查功能类指令
    for cmd, params in function_commands.items():
        if text_lower == cmd:
            return {
                'is_command': True,
                'command_type': 'function', 
                'command_params': params,
                'processed_text': ''
            }
    
    # 🎯 复合指令检测（文本中包含指令）
    # 例如："今天天气不错换行心情也很好"
    for cmd in format_commands:
        if cmd in text_lower:
            # 分割文本和指令
            parts = text_lower.split(cmd)
            if len(parts) == 2:
                before_text = parts[0].strip()
                after_text = parts[1].strip()
                format_char = _format_action_to_text(format_commands[cmd]['action'])
                
                combined_text = before_text + format_char + after_text
                return {
                    'is_command': True,
                    'command_type': 'mixed',
                    'command_params': {
                        'original_command': cmd,
                        'before_text': before_text,
                        'after_text': after_text,
                        'format_action': format_commands[cmd]['action']
                    },
                    'processed_text': combined_text
                }
    
    # 不是指令，返回原文本
    return {
        'is_command': False,
        'command_type': None,
        'command_params': {},
        'processed_text': text
    }

def _format_action_to_text(action):
    """将格式动作转换为对应的文本字符"""
    action_map = {
        'newline': '\n',
        'space': ' ',
        'tab': '\t',
    }
    return action_map.get(action, '')

def normalize_text(text: str) -> str:
    """
    统一文本规范化 - 集成产品级优化规则
    
    包含功能：
    - 大小写规范化
    - 热词映射  
    - 文本顺滑处理（过滤口语词、修复重复）
    - 基础数字格式化
    - 智能标点优化
    """
    if not text:
        return text
    try:
        import re
        t = text
        
        # 🎯 文本顺滑处理
        t = _smooth_oral_text(t)
        
        # 🎯 基础数字格式化
        t = _format_numbers(t)
        
        # 原有功能：IPO 大小写规范化
        t = re.sub(r"\bipo\b", "IPO", t, flags=re.IGNORECASE)
        t = re.sub(r"\bipo(?=\.|\s|$)", "IPO", t, flags=re.IGNORECASE)

        # 🎯 应用增强热词管理
        try:
            hotword_manager = _get_hotword_manager()
            t = hotword_manager.apply_hotword_replacement(t)
        except Exception as e:
            recognition_logger.warning(f"热词替换失败: {e}")
            # 兼容性回退
            rep = _load_hotword_replace_map()
            if rep:
                for k, v in rep.items():
                    if not k:
                        continue
                    try:
                        t = t.replace(k, v)
                    except Exception:
                        pass
                    
        return t
    except Exception:
        return text

def _normalize_for_dedup(text: str) -> str:
    """
    规范化文本以用于重复检测：移除空白和常见标点，并统一大小写。
    """
    if not text:
        return ''
    try:
        import re
        t = text.strip()
        # 移除所有空白
        t = re.sub(r"\s+", "", t)
        # 移除常见中英文标点
        t = re.sub(r'[，,。.!？?\-—:：;；、·\"\'()（）\[\]\\/]', "", t)
        # 统一大小写
        return t.lower()
    except Exception:
        return text.strip().lower() if text else ''

def _calc_similarity(a: str, b: str) -> float:
    """
    计算两个字符串的相似度 [0,1]。失败时保守返回0或1。
    """
    try:
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a or '', b or '').ratio()
    except Exception:
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return 1.0 if a == b else 0.0

def _smooth_oral_text(text: str) -> str:
    """
    文本顺滑处理 - 过滤口语化表达
    """
    if not text:
        return text
    
    import re
    
    # 过滤语气词和口头禅
    filler_words = ['嗯', '啊', '呃', '额', '那个', '就是说', '然后呢', '怎么说呢']
    for word in filler_words:
        text = text.replace(word, '')
    
    # 修复重复词语（连续2-4次重复）
    text = re.sub(r'(.{1,3})\1{1,3}', r'\1', text)
    
    # 清理多余的空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def _format_numbers(text: str) -> str:
    """
    基础数字格式化处理
    """
    if not text:
        return text
    
    import re
    
    # 百分比处理：百分之八十 -> 80%
    text = re.sub(r'百分之(\d+)', r'\1%', text)
    text = re.sub(r'百分之([一二三四五六七八九十百]+)', lambda m: f'{_chinese_to_number(m.group(1))}%', text)
    
    # 简单的中文数字转阿拉伯数字（1-100范围）
    chinese_numbers = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
        '零': '0', '〇': '0'
    }
    
    for cn, num in chinese_numbers.items():
        # 避免替换姓名中的数字（简单规则）
        text = re.sub(rf'(?<![a-zA-Z\u4e00-\u9fff]){cn}(?![a-zA-Z\u4e00-\u9fff])', num, text)
    
    return text

def _chinese_to_number(chinese_num: str) -> str:
    """
    中文数字转阿拉伯数字（简化版）
    """
    try:
        # 简单映射，实际可以用更完整的转换库
        mapping = {
            '十': '10', '二十': '20', '三十': '30', '四十': '40', '五十': '50',
            '六十': '60', '七十': '70', '八十': '80', '九十': '90', '一百': '100'
        }
        return mapping.get(chinese_num, chinese_num)
    except:
        return chinese_num

# ================== Flask应用初始化 ==================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# 配置CORS支持跨域请求
CORS(app, resources={r"/*": {"origins": "*"}})

# 注册声纹识别相关路由
app.register_blueprint(print_app)

# 离线会议接口
app.register_blueprint(meeting_app)

app.json.ensure_ascii = False

# 初始化SocketIO和WebSocket支持
socketio = SocketIO(app, cors_allowed_origins="*")
sock = Sock(app)

voice_conf = conf['voice']

# ================== 实时会话全局状态 ==================
active_sessions = {}
global_counters = {
    'total_connections': 0,
    'active_connections': 0,
    'total_messages': 0,
    'total_chunks': 0,
    'total_partials': 0,
    'total_finals': 0
}


# ================== 临时目录解析 ==================
def resolve_temp_dir() -> str:
    """解析并确保可用的临时目录，优先配置项，不可用则回退到 data/temp。
    Returns:
        str: 可写入的临时目录路径
    """
    try:
        configured = voice_conf.get('temp_path', None)
    except Exception:
        configured = None

    candidates = [configured, 'data/temp', 'data/voice/temp']
    for path in candidates:
        if not path:
            continue
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except Exception:
            continue
    # 兜底
    fallback = 'data/temp'
    try:
        os.makedirs(fallback, exist_ok=True)
    except Exception:
        pass
    return fallback


# ================== 工具类和函数 ==================

class NumpyEncoder(json.JSONEncoder):
    """
    自定义JSON编码器，用于序列化NumPy数组和浮点数
    解决NumPy类型无法直接JSON序列化的问题
    """

    def default(self, obj):
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def extract_text_from_result(res) -> str:
    """统一解析识别结果，兼容 str/dict/list 各种返回格式"""
    try:
        if res is None:
            return ''
        if isinstance(res, str):
            return res.strip()
        if isinstance(res, dict):
            return (res.get('text') or res.get('result') or res.get('transcription') or '').strip()
        if isinstance(res, (list, tuple)):
            for item in res:
                if isinstance(item, dict) and 'text' in item:
                    return (item.get('text') or '').strip()
            return (str(res[0]) if res else '').strip()
    except Exception:
        return ''

def audio_segment_to_array(audio: AudioSegment) -> (np.ndarray, int):
    """
    将 AudioSegment 转换为 NumPy 数组和采样率
    
    Args:
        audio: PyDub AudioSegment对象
    
    Returns:
        tuple: (音频数据数组, 采样率)
    """
    # 导出为 wav 格式的内存字节流
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")

    # 用 soundfile 从内存中读取
    buffer.seek(0)
    data, samplerate = sf.read(buffer)

    return data, samplerate


def process_audio_file(audio_file):
    """
    处理上传的音频文件，统一音频格式
    
    Args:
        audio_file: Flask上传的文件对象
    
    Returns:
        tuple: (音频数据数组, 采样率)
    
    Raises:
        Exception: 音频文件处理失败时抛出异常
    """
    try:
        # 直接读取音频数据到内存
        audio_data = audio_file.read()
        audio_stream = io.BytesIO(audio_data)

        # 使用soundfile直接读取音频数据
        try:
            # 首先尝试直接用soundfile读取
            audio_array, samplerate = sf.read(audio_stream)
        except:
            # 如果失败，使用pydub转换
            audio_stream.seek(0)  # 重置流位置
            audio = AudioSegment.from_file(audio_stream)
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            audio_array, samplerate = sf.read(wav_buffer)

        return audio_array, samplerate

    except Exception as e:
        raise Exception(f"音频文件处理失败: {str(e)}")


# ================== 基础API接口 ==================

@app.route('/')
def index():
    """
    健康检查接口
    
    Returns:
        str: 固定返回"success"，用于检查服务器运行状态
    """
    return "success"


@app.route("/embedding", methods=['POST'])
def embedding_and_return():
    """
    通用Embedding向量化接口
    
    接收JSON数据并返回成功状态，可扩展为实际的向量化处理
    
    Returns:
        dict: {"success": True}
    """
    try:
        req = request.get_json()
        # TODO: 在此处添加实际的embedding处理逻辑
        return jsonify({"success": True})
    except Exception as e:
        print(f"Embedding处理错误: {traceback.format_exc()}")
        return {'error': f'Embedding处理失败: {str(e)}'}, 500


# ================== 语音识别API接口 ==================

@app.route('/voice-register', methods=['POST'])
def handle_audio_stream():
    """
    语音注册接口
    
    功能：上传音频文件，进行语音识别并提取声纹特征存储到向量数据库
    
    请求参数:
        audio: 音频文件 (multipart/form-data)
        username: 用户名 (string)
        userid: 用户ID (integer)
    
    返回:
        JSON: {
            "duration": 音频时长(秒),
            "sample_rate": 采样率,
            "txt": 识别的文字内容
        }
    
    错误码:
        400: 缺少必要参数
        500: 服务器内部错误
    """
    if 'audio' not in request.files:
        return {'error': '没有接收到音频文件'}, 400

    username = request.form.get('username')
    userid = request.form.get('userid')

    if not username or not userid:
        return {'error': '用户名和用户ID不能为空'}, 400

    # userid 转为 int64
    userid = int(userid)
    audio_file = request.files['audio']

    try:
        # 处理音频文件
        audio_array, samplerate = process_audio_file(audio_file)

        # 保存处理后的音频到文件 - 使用相对路径避免权限问题
        folder = f"{voice_conf['print_wav_path']}/{userid}"
        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = f"{str(time.time() * 1000)}.{str(uuid.uuid4())}.{audio_file.filename}"
        wav_file_path = f"{voice_conf['print_wav_path']}/{userid}/{filename}"
        sf.write(wav_file_path, audio_array, samplerate)
        print(f"音频已保存到 {wav_file_path}")

        # 语音识别
        txt = recognize(wav_file_path)
        txt_res = extract_text_from_result(txt)
        # txt_res 最大允许100个字
        if len(txt_res) > 100:
            txt_res = txt_res[:100]

        # 提取声纹特征并保存到向量数据库
        insert_res = insert_voice(
            username, userid, filename, txt_res,
            int64(time.time() * 1000),
            embedding(wav_file_path)
        )

        # 返回处理结果
        data = {
            'duration': len(audio_array) / samplerate,
            'sample_rate': samplerate,
            'txt': txt_res
        }
        return json.dumps(data, cls=NumpyEncoder), 200

    except Exception as e:
        torch.cuda.empty_cache()  # 清理GPU内存
        print(f"语音注册错误详情: {traceback.format_exc()}")
        return {'error': f'音频处理失败: {str(e)}'}, 500


@app.route('/voice-recognize-offline', methods=['POST'])
def voice_recognize_offline():
    """
    离线语音识别接口
    
    功能：上传音频文件进行语音转文字，不保存声纹特征
    
    请求参数:
        audio: 音频文件 (multipart/form-data)
        language: 语言类型 (可选，默认zh-cn)
    
    返回:
        JSON: {
            "text": 识别的文字内容,
            "duration": 音频时长(秒),
            "sample_rate": 采样率,
            "confidence": 置信度(如果有)
        }
    
    错误码:
        400: 缺少音频文件
        500: 识别失败
    """
    if 'audio' not in request.files:
        return {'error': '没有接收到音频文件'}, 400

    audio_file = request.files['audio']
    language = request.form.get('language', 'zh-cn')  # 默认中文

    try:
        # 处理音频文件
        audio_array, samplerate = process_audio_file(audio_file)

        # 创建临时文件进行识别
        temp_folder = resolve_temp_dir()

        temp_filename = f"temp_{str(time.time() * 1000)}.{str(uuid.uuid4())}.wav"
        temp_file_path = f"{temp_folder}/{temp_filename}"
        sf.write(temp_file_path, np.clip(audio_array, -1.0, 1.0), samplerate, subtype='PCM_16')

        try:
            # 进行语音识别
            recognition_result = recognize(temp_file_path)
            recognized_text = extract_text_from_result(recognition_result)
            confidence = None

            # 返回识别结果
            result = {
                'text': recognized_text,
                'duration': len(audio_array) / samplerate,
                'sample_rate': samplerate,
                'language': language
            }

            if confidence is not None:
                result['confidence'] = confidence

            return jsonify(result), 200

        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except Exception as e:
        torch.cuda.empty_cache()  # 清理GPU内存
        print(f"离线语音识别错误详情: {traceback.format_exc()}")
        return {'error': f'语音识别失败: {str(e)}'}, 500


@app.route('/voice-recognize-online', methods=['POST'])
def voice_recognize_online():
    """
    在线语音识别接口 (单次请求版本)
    
    功能：接收音频数据进行实时语音识别，支持base64编码的音频数据
    
    请求参数:
        audio_data: base64编码的音频数据 (JSON)
        format: 音频格式 (可选，默认wav)
        sample_rate: 采样率 (可选，默认16000)
    
    返回:
        JSON: {
            "text": 识别的文字内容,
            "is_final": 是否为最终结果,
            "timestamp": 处理时间戳
        }
    
    错误码:
        400: 请求参数错误
        500: 识别失败
    """
    try:
        data = request.get_json()
        if not data or 'audio_data' not in data:
            return {'error': '缺少音频数据'}, 400

        audio_data = data['audio_data']
        audio_format = data.get('format', 'wav')
        sample_rate = data.get('sample_rate', 16000)

        # 解码base64音频数据
        try:
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            return {'error': f'音频数据解码失败: {str(e)}'}, 400

        # 创建临时文件进行识别
        temp_folder = resolve_temp_dir()

        temp_filename = f"online_{str(time.time() * 1000)}.{str(uuid.uuid4())}.{audio_format}"
        temp_file_path = f"{temp_folder}/{temp_filename}"

        # 写入音频数据
        with open(temp_file_path, 'wb') as f:
            f.write(audio_bytes)

        try:
            # 进行语音识别
            recognition_result = recognize(temp_file_path)
            recognized_text = extract_text_from_result(recognition_result)

            # 返回识别结果
            result = {
                'text': recognized_text,
                'is_final': True,  # 单次请求都是最终结果
                'timestamp': int(time.time() * 1000),
                'format': audio_format,
                'sample_rate': sample_rate
            }

            return jsonify(result), 200

        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except Exception as e:
        torch.cuda.empty_cache()  # 清理GPU内存
        print(f"在线语音识别错误详情: {traceback.format_exc()}")
        return {'error': f'在线语音识别失败: {str(e)}'}, 500


# ================== SocketIO事件处理 ==================

@socketio.on('connect')
def handle_connect():
    """
    WebSocket连接事件处理
    """
    print('Client connected')
    try:
        if monitoring_available and system_monitor is not None:
            system_monitor.record_connection(True)
    except Exception:
        pass
    logger.info(f"WebSocket连接: {request.sid}")


@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """
    处理WebSocket音频块数据
    
    Args:
        data: 音频数据块 (WebM格式)
    """
    if not data or len(data) < 100:
        emit('transcription', {'msg': '音频数据不完整或为空', 'code': -1})
        return

    try:
        # 直接从内存中解析 WebM
        audio = AudioSegment.from_file(io.BytesIO(data), format="webm")
        # 统一导出为16k 16-bit PCM 单声道
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export('./test.wav', format="wav", parameters=["-acodec", "pcm_s16le"])
        audio_data, sample_rate = audio_segment_to_array(audio)

        # 调用语音识别模型
        txt = recognize('./test.wav')
        emit('transcription', {'text': extract_text_from_result(txt), 'code': 0})

    except Exception as e:
        print(f"[ERROR] WebM 解析失败: {e}")
        emit('transcription', {'msg': f"[ERROR] WebM 解析失败: {e}", 'code': -400})
        return


# ================== 音频文件下载接口 ==================

@app.route('/voice/debug/sessions', methods=['GET'])
def list_debug_sessions():
    """
    🔧 列出可用的调试会话目录
    """
    try:
        sessions_dir = 'data/temp'
        if not os.path.exists(sessions_dir):
            return {'error': '调试目录不存在'}, 404
            
        sessions = []
        for item in os.listdir(sessions_dir):
            session_path = os.path.join(sessions_dir, item)
            if os.path.isdir(session_path) and item.startswith('session_'):
                # 检查是否有音频文件
                wav_files = []
                pcm_files = []
                stats_file = None
                
                for file in os.listdir(session_path):
                    if file.endswith('.wav'):
                        wav_files.append(file)
                    elif file.endswith('.pcm'):
                        pcm_files.append(file)
                    elif file == 'audio_stats.json':
                        stats_file = file
                        
                if wav_files or pcm_files:
                    session_info = {
                        'session_id': item,
                        'path': session_path,
                        'wav_files': wav_files,
                        'pcm_files': pcm_files,
                        'has_stats': stats_file is not None,
                        'created_time': os.path.getctime(session_path)
                    }
                    sessions.append(session_info)
                    
        # 按创建时间倒序排列
        sessions.sort(key=lambda x: x['created_time'], reverse=True)
        return {'sessions': sessions}
        
    except Exception as e:
        return {'error': f'获取会话列表失败: {str(e)}'}, 500

@app.route('/voice/debug/sessions/<session_id>/download/<filename>', methods=['GET'])
def download_debug_audio(session_id, filename):
    """
    🔧 下载指定会话的音频文件
    """
    try:
        # 安全检查文件名
        if '..' in filename or '/' in filename or '\\' in filename:
            return {'error': '非法文件名'}, 400
            
        session_path = os.path.join('data/temp', session_id)
        if not os.path.exists(session_path):
            return {'error': '会话不存在'}, 404
            
        file_path = os.path.join(session_path, filename)
        if not os.path.exists(file_path):
            return {'error': '文件不存在'}, 404
            
        # 确定MIME类型
        if filename.endswith('.wav'):
            mime_type = 'audio/wav'
        elif filename.endswith('.pcm'):
            mime_type = 'application/octet-stream'
        elif filename.endswith('.json'):
            mime_type = 'application/json'
        else:
            mime_type = 'application/octet-stream'
            
        return send_file(file_path, 
                        mimetype=mime_type,
                        as_attachment=True,
                        download_name=filename)
                        
    except Exception as e:
        return {'error': f'下载文件失败: {str(e)}'}, 500

@app.route('/voice/debug/sessions/<session_id>/stats', methods=['GET'])
def get_session_stats(session_id):
    """
    🔧 获取指定会话的音频统计信息
    """
    try:
        session_path = os.path.join('data/temp', session_id)
        if not os.path.exists(session_path):
            return {'error': '会话不存在'}, 404
            
        stats_path = os.path.join(session_path, 'audio_stats.json')
        if not os.path.exists(stats_path):
            return {'error': '统计信息不存在'}, 404
            
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
            
        return {'stats': stats}
        
    except Exception as e:
        return {'error': f'获取统计信息失败: {str(e)}'}, 500

# ================== 日志查看接口 ==================

@app.route('/logs/websocket', methods=['GET'])
def get_websocket_logs():
    """
    获取WebSocket语音识别日志
    """
    try:
        log_file = "logs/websocket_speech.log"
        if not os.path.exists(log_file):
            return "日志文件不存在", 404

        # 读取最近的1000行日志
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-1000:] if len(lines) > 1000 else lines

        return ''.join(recent_lines), 200

    except Exception as e:
        logger.error(f"获取WebSocket日志失败: {str(e)}")
        return f"获取日志失败: {str(e)}", 500


@app.route('/logs/audio', methods=['GET'])
def get_audio_logs():
    """
    获取音频处理日志
    """
    try:
        log_file = "logs/audio_processing.log"
        if not os.path.exists(log_file):
            return "日志文件不存在", 404

        # 读取最近的1000行日志
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-1000:] if len(lines) > 1000 else lines

        return ''.join(recent_lines), 200

    except Exception as e:
        logger.error(f"获取音频处理日志失败: {str(e)}")
        return f"获取日志失败: {str(e)}", 500


@app.route('/logs/recognition', methods=['GET'])
def get_recognition_logs():
    """
    获取语音识别结果日志
    """
    try:
        log_file = "logs/recognition_results.log"
        if not os.path.exists(log_file):
            return "日志文件不存在", 404

        # 读取最近的500行日志
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-500:] if len(lines) > 500 else lines

        return ''.join(recent_lines), 200

    except Exception as e:
        logger.error(f"获取识别结果日志失败: {str(e)}")
        return f"获取日志失败: {str(e)}", 500


@app.route('/logs/key', methods=['GET'])
def get_key_logs():
    """获取关键事件日志（精简）"""
    try:
        log_file = "logs/realtime_key.log"
        if not os.path.exists(log_file):
            return "日志文件不存在", 404
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-1000:] if len(lines) > 1000 else lines
        return ''.join(recent_lines), 200
    except Exception as e:
        logger.error(f"获取关键日志失败: {str(e)}")
        return f"获取日志失败: {str(e)}", 500


@app.route('/ws/status', methods=['GET'])
def get_ws_status():
    """获取实时WebSocket会话状态与全局统计"""
    try:
        sessions = []
        for sid, info in active_sessions.items():
            sessions.append({
                'session_id': sid,
                **info
            })
        return jsonify({
            'counters': global_counters,
            'active_sessions': sessions,
            'time': int(time.time() * 1000)
        })
    except Exception as e:
        logger.error(f"获取WS状态失败: {str(e)}")
        return {'error': str(e)}, 500

# ================== 热词管理API接口 ==================

@app.route('/api/hotwords', methods=['GET'])
def get_hotwords():
    """获取所有热词"""
    try:
        manager = _get_hotword_manager()
        hotwords = manager.get_all_hotwords()
        return jsonify({
            'hotwords': hotwords,
            'count': len(hotwords),
            'timestamp': int(time.time() * 1000)
        })
    except Exception as e:
        logger.error(f"获取热词失败: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/api/hotwords/add', methods=['POST'])
def add_hotword():
    """添加动态热词"""
    try:
        data = request.get_json()
        if not data or 'wrong_word' not in data or 'correct_word' not in data:
            return {'error': '缺少必要参数: wrong_word, correct_word'}, 400
        
        wrong_word = data['wrong_word'].strip()
        correct_word = data['correct_word'].strip()
        source = data.get('source', 'api')
        
        if not wrong_word or not correct_word:
            return {'error': '错误词和正确词不能为空'}, 400
        
        manager = _get_hotword_manager()
        manager.add_dynamic_hotword(wrong_word, correct_word, source)
        
        return jsonify({
            'success': True,
            'message': f"成功添加热词映射: '{wrong_word}' -> '{correct_word}'",
            'hotword': {
                'wrong_word': wrong_word,
                'correct_word': correct_word,
                'source': source
            }
        })
    except Exception as e:
        logger.error(f"添加热词失败: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/api/hotwords/learn', methods=['POST'])
def learn_from_correction():
    """从纠错中学习热词"""
    try:
        data = request.get_json()
        if not data or 'original_text' not in data or 'corrected_text' not in data:
            return {'error': '缺少必要参数: original_text, corrected_text'}, 400
        
        original_text = data['original_text'].strip()
        corrected_text = data['corrected_text'].strip()
        
        if not original_text or not corrected_text:
            return {'error': '原始文本和纠正文本不能为空'}, 400
        
        if original_text == corrected_text:
            return {'error': '原始文本和纠正文本相同，无需学习'}, 400
        
        manager = _get_hotword_manager()
        manager.learn_from_correction(original_text, corrected_text)
        
        return jsonify({
            'success': True,
            'message': '用户纠错学习完成',
            'learning': {
                'original_text': original_text,
                'corrected_text': corrected_text
            }
        })
    except Exception as e:
        logger.error(f"纠错学习失败: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/api/hotwords/suggestions', methods=['GET'])
def get_hotword_suggestions():
    """获取热词建议"""
    try:
        partial_text = request.args.get('text', '').strip()
        limit = int(request.args.get('limit', 5))
        
        if not partial_text:
            return {'error': '缺少查询文本参数'}, 400
        
        manager = _get_hotword_manager()
        suggestions = manager.get_hotword_suggestions(partial_text, limit)
        
        return jsonify({
            'suggestions': suggestions,
            'query': partial_text,
            'count': len(suggestions)
        })
    except Exception as e:
        logger.error(f"获取热词建议失败: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/api/hotwords/cleanup', methods=['POST'])
def cleanup_hotwords():
    """清理长期未使用的热词"""
    try:
        data = request.get_json() or {}
        days_threshold = int(data.get('days_threshold', 90))
        
        manager = _get_hotword_manager()
        removed_count = manager.cleanup_old_hotwords(days_threshold)
        
        return jsonify({
            'success': True,
            'message': f'清理完成，删除了{removed_count}个长期未使用的热词',
            'removed_count': removed_count,
            'days_threshold': days_threshold
        })
    except Exception as e:
        logger.error(f"清理热词失败: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/api/hotwords/stats', methods=['GET'])
def get_hotword_stats():
    """获取热词使用统计"""
    try:
        manager = _get_hotword_manager()
        
        stats = {
            'static_count': len(manager.static_hotwords),
            'dynamic_count': len(manager.dynamic_hotwords),
            'user_learning_count': len(manager.user_corrections),
            'total_count': len(manager.get_all_hotwords()),
            'usage_stats': dict(list(manager.hotword_usage_stats.items())[:10])  # 前10个统计
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取热词统计失败: {str(e)}")
        return {'error': str(e)}, 500

# ================== WebSocket实时语音识别 ==================

class SpeechSession:
    """
    语音会话处理类（旧版本，保持兼容性）
    """

    def __init__(self):
        self.audio_buffer = b''
        self.cache = {}
        self.is_final = False
        self.is_realtime = True
        self.last_chunk_time = time.time()
        self.pause_threshold = 1.0
        self.sample_rate = 16000
        self.frame_duration = 0.6
        self.last_audio_send_time = time.time()
        self.result_id = 0

    def append_audio(self, pcm_base64):
        raw_pcm = base64.b64decode(pcm_base64)
        self.audio_buffer += raw_pcm

    def should_process_frame(self):
        return time.time() - self.last_audio_send_time > self.frame_duration

    def process_buffer(self):
        self.last_chunk_time = time.time()
        try:
            res = recognize(self.audio_buffer)
            logger.info(f"识别结果: {res}")
            if res and res[0]["text"].strip():
                text = res[0]['text']
                return text
        except Exception as e:
            logger.error(f"语音识别处理失败: {str(e)}")
        return None


# 导入系统监控器（可选，避免导入错误）
try:
    from monitoring.system_monitor import system_monitor
    monitoring_available = True
except Exception as e:
    monitoring_available = False
    system_monitor = None
    logger.warning(f"⚠️ 系统监控模块不可用，将跳过监控功能: {e}")

class RealtimeSpeechSession:
    """
    实时语音识别会话类 - 输入法风格（已修复回删问题）
    
    特点：
    1. 流式处理音频块
    2. 区分"已确认文本"和"候选文本"，避免已确认内容被回删
    3. 智能文本确认机制，基于稳定性和置信度
    4. 类似输入法的用户体验，固定已确认部分
    """

    def __init__(self):
        self.audio_chunks = []  # 音频块列表
        
        # 🎯 【修改】简化文本状态管理
        self.full_sentence = ""
        self.confirmed_sentences = [] # 已确认的完整句子列表
        
        # 🗑️ 【废弃】以下复杂的文本状态管理将被新的、更简单的逻辑替代
        # self.confirmed_text = ""  # 已确认的文本（固定显示，不再修改）
        # self.candidate_text = ""  # 候选文本（可以变化的部分）
        # self.text_stability_tracker = {}  # 文本稳定性跟踪器
        # self.last_stable_text = ""  # 最后一次稳定的文本
        # self.stability_count = 0  # 文本稳定次数计数
        # self.stability_threshold = 3  # 连续稳定次数阈值（达到后自动确认）
        
        # 音频段落管理（保留部分兼容）
        self.confirmed_audio_length = 0  # 已确认文本对应的音频长度
        self.candidate_audio_start = 0   # 候选文本对应的音频开始位置
        
        # 保留兼容属性
        self.current_sentence = ""  # 兼容现有接口：full_sentence
        self.cache = {}  # ModelScope流式识别缓存
        self.sample_rate = 16000
        self.chunk_size = [0, 10, 5]  # 流式识别参数
        self.encoder_chunk_look_back = 4
        self.decoder_chunk_look_back = 1
        self.last_update_time = time.time()
        # 🌐 基于网络搜索的标准参数配置
        self.chunk_duration = 0.25  # 处理间隔250ms (网络推荐范围100-500ms)
        self.silence_threshold = 2.0  # 静音阈值2秒（句子结束判断）
        self.audio_buffer = np.array([], dtype=np.float32)
        self.last_activity_time = time.time()  # 最后一次有语音活动的时间
        self.sentence_complete_threshold = 1.5  # 句子完成阈值1.5秒
        self.min_audio_duration = 0.1  # 最小音频长度：100ms (网络标准最小值)

        # 临时文件配置
        self.temp_file_counter = 0
        self.partial_save_counter = 0
        # 原始音频保存计数器与累积器（用于保留前端原始数据，取证与回放）
        self.raw_file_counter = 0
        self.raw_pcm_accumulator = io.BytesIO()
        self.first_pcm_sample_rate = None
        self.received_non_pcm = False
        self.session_id = None
        # 统一解析临时目录
        self.temp_dir = resolve_temp_dir()
        # 会话目录将在 set_session 中创建
        self.session_dir = None

        # 去重与幂等：最终段落跟踪
        self.final_seq = 0
        self._last_final_norm = ""
        self._recent_final_norms = []  # 最近若干final的规范化文本
        self._recent_final_texts = []  # 最近若干final原文
        self.last_partial_confidence = 0.0

        # 关闭流式模型以提高兼容性与稳定性（回退离线识别）
        self.streaming_model = None
        
        # 🌐 基于网络标准的质量监控系统
        self.quality_stats = {
            'total_chunks': 0,
            'valid_chunks': 0,
            'high_quality_chunks': 0,
            'recognition_attempts': 0,
            'successful_recognitions': 0,
            'avg_rms': 0.0,
            'last_quality_report': time.time()
        }

    def set_session(self, session_id: str):
        """设置会话ID并创建持久化目录"""
        self.session_id = session_id
        try:
            self.session_dir = os.path.join(self.temp_dir, f"session_{session_id}")
            os.makedirs(self.session_dir, exist_ok=True)
            # 写入会话元信息
            meta = {
                'session_id': session_id,
                'start_time': int(time.time() * 1000),
                'sample_rate': self.sample_rate
            }
            with open(os.path.join(self.session_dir, 'session.json'), 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False)
        except Exception:
            # 目录创建失败不影响主流程
            self.session_dir = None

    def reset(self):
        """重置会话状态"""
        self.audio_chunks.clear()
        
        # 🎯 【修改】重置新的简化状态管理
        self.full_sentence = ""
        
        # 🗑️ 【废弃】以下状态变量已被移除
        # self.confirmed_text = ""
        # self.candidate_text = ""
        # self.text_stability_tracker.clear()
        # self.last_stable_text = ""
        # self.stability_count = 0
        
        self.confirmed_audio_length = 0
        self.candidate_audio_start = 0
        
        # 重置原有状态
        self.current_sentence = ""
        self.full_sentence = ""  # 🔧【2025-01-19 修复】同时重置主状态字段
        self.confirmed_sentences = []
        self.cache.clear()
        self.audio_buffer = np.array([], dtype=np.float32)
        self.last_update_time = time.time()
        self.last_activity_time = time.time()
        
        # 重置质量统计
        self.quality_stats = {
            'total_chunks': 0,
            'valid_chunks': 0,
            'high_quality_chunks': 0,
            'recognition_attempts': 0,
            'successful_recognitions': 0,
            'avg_rms': 0.0,
            'last_quality_report': time.time()
        }

        # 重置去重与幂等状态
        self.final_seq = 0
        self._last_final_norm = ""
        self._recent_final_norms = []
        self._recent_final_texts = []
        self.last_partial_confidence = 0.0

    def _is_duplicate_final(self, text: str, similarity_threshold: float = 0.92) -> bool:
        """
        判断一个最终文本是否与最近一次或最近若干次final重复/极度相似。
        """
        if not text:
            return False
        norm = _normalize_for_dedup(text)
        if not norm:
            return False

        if self._last_final_norm:
            sim = _calc_similarity(norm, self._last_final_norm)
            if sim >= similarity_threshold:
                return True

        # 与窗口内其他final比较（更稳健）
        for prev_norm in self._recent_final_norms[-4:]:
            if _calc_similarity(norm, prev_norm) >= similarity_threshold:
                return True
        return False

    def _register_final(self, text: str):
        """
        在发送final后登记规范化文本用于后续去重。
        """
        norm = _normalize_for_dedup(text)
        self._last_final_norm = norm
        self._recent_final_norms.append(norm)
        self._recent_final_texts.append(text)
        # 只保留最近5条
        if len(self._recent_final_norms) > 5:
            self._recent_final_norms = self._recent_final_norms[-5:]
        if len(self._recent_final_texts) > 5:
            self._recent_final_texts = self._recent_final_texts[-5:]

    def _allocate_segment_id(self) -> str:
        """
        生成下一个final段落的segment_id（会话内自增）。
        """
        self.final_seq += 1
        base = str(self.final_seq)
        if self.session_id:
            return f"{self.session_id}-{base}"
        return base
        
    def _update_text_stability(self, new_text):
        """🗑️【已废弃】文本稳定性跟踪方法，保留仅为兼容性"""
        return False
        
    def _extract_confirmed_part(self, current_text, previous_text):
        """🗑️【已废弃】文本确认部分提取方法，保留仅为兼容性"""
        return "", current_text
        
    def _should_confirm_by_pause(self):
        """🗑️【已废弃】停顿确认判断方法，保留仅为兼容性"""
        return False
        
    def predict_punctuation(self, text, silence_duration, audio_energy_level=None):
        """
        智能标点预测 - 基于停顿和语调模式
        
        Args:
            text: 输入文本
            silence_duration: 静音时长(秒)
            audio_energy_level: 音频能量级别(可选)
            
        Returns:
            str: 添加标点后的文本
        """
        if not text or not text.strip():
            return text
            
        import re
        
        # 如果文本已有标点，直接返回
        if re.search(r'[。！？,.!?]$', text):
            return text
            
        # 🎯 基于停顿时长的标点预测
        if silence_duration >= 1.5:
            # 长停顿：判断句子类型
            if any(word in text for word in ['什么', '哪里', '怎么', '为什么', '吗']):
                # 疑问句
                text += '？'
                recognition_logger.debug(f"🎯 智能标点: 疑问句 + 长停顿 -> 问号")
            elif any(word in text for word in ['好', '太', '真', '非常']):
                # 可能是感叹句
                text += '！'
                recognition_logger.debug(f"🎯 智能标点: 感叹句 + 长停顿 -> 叹号")
            else:
                # 普通陈述句
                text += '。'
                recognition_logger.debug(f"🎯 智能标点: 陈述句 + 长停顿 -> 句号")
                
        elif 0.3 <= silence_duration < 1.5:
            # 中等停顿：可能需要逗号
            # 简单规则：如果文本较长且没有标点，添加逗号
            if len(text) > 8 and not re.search(r'[，,]', text):
                # 寻找合适的逗号位置（连词后、时间词后等）
                comma_positions = []
                
                # 在连词后添加逗号
                connectors = ['但是', '不过', '然后', '接着', '另外', '而且', '所以', '因此']
                for conn in connectors:
                    pos = text.find(conn)
                    if pos >= 0:
                        comma_positions.append(pos + len(conn))
                
                # 在时间词后添加逗号
                time_words = ['今天', '昨天', '明天', '现在', '刚才', '一会儿']
                for time_word in time_words:
                    pos = text.find(time_word)
                    if pos >= 0:
                        comma_positions.append(pos + len(time_word))
                
                # 选择最合适的位置添加逗号
                if comma_positions:
                    # 选择中间位置的逗号点
                    pos = min(comma_positions, key=lambda x: abs(x - len(text) // 2))
                    text = text[:pos] + '，' + text[pos:]
                    recognition_logger.debug(f"🎯 智能标点: 中等停顿 + 连接词 -> 逗号")
                    
        return text

    def _execute_edit_command(self, command_params):
        """
        【已重构】执行编辑指令，适配新的文本状态管理
        
        Args:
            command_params: 指令参数字典
            
        Returns:
            dict: 更新后的文本状态
        """
        command_type = command_params.get('type')
        
        if command_type == 'delete':
            target = command_params.get('target')
            
            if target == 'all':
                # 删除全部
                old_confirmed = "".join(self.confirmed_sentences)
                old_current = self.full_sentence
                self.confirmed_sentences.clear()
                self.full_sentence = ""
                recognition_logger.info(f"🗑️ 删除全部: 已确认='{old_confirmed}' + 当前='{old_current}' -> ''")
                
            elif target == 'last_sentence':
                # 删除最后一句话
                if self.full_sentence:
                    old_current = self.full_sentence
                    self.full_sentence = ""
                    recognition_logger.info(f"🗑️ 删除当前句子: '{old_current}' -> ''")
                elif self.confirmed_sentences:
                    deleted_sentence = self.confirmed_sentences.pop()
                    recognition_logger.info(f"🗑️ 删除最后确认句子: '{deleted_sentence}'")
                
            elif target == 'last_word':
                # 删除最后一个词
                if self.full_sentence:
                    words = self.full_sentence.split()
                    if words:
                        old_current = self.full_sentence
                        self.full_sentence = ' '.join(words[:-1])
                        recognition_logger.info(f"🗑️ 删除当前句最后词: '{old_current}' -> '{self.full_sentence}'")
                        
            elif target == 'last_char':
                # 删除最后一个字符
                if self.full_sentence:
                    old_current = self.full_sentence
                    self.full_sentence = self.full_sentence[:-1]
                    recognition_logger.info(f"🗑️ 删除当前句最后字符: '{old_current}' -> '{self.full_sentence}'")
                    
        elif command_type == 'undo':
            # 撤销操作（简化实现：清空当前句子）
            if self.full_sentence:
                old_current = self.full_sentence
                self.full_sentence = ""
                recognition_logger.info(f"↩️ 撤销当前句子: '{old_current}' -> ''")
                
        elif command_type == 'redo':
            # 重做操作（简化实现：这里可以扩展为恢复历史状态）
            recognition_logger.info("↪️ 重做指令已接收（当前为简化实现）")
        
        # 返回新架构的状态信息
        return {
            'confirmed_text': "".join(self.confirmed_sentences),
            'candidate_text': self.full_sentence,
            'full_text': "".join(self.confirmed_sentences) + self.full_sentence,
            'changed': True,
            'stability_count': 0,
            'confirmed_length': len("".join(self.confirmed_sentences))
        }

    def update_text_state(self, new_full_text, confidence=0.8):
        """
        🗑️【已废弃】复杂的文本状态管理方法
        此方法在新架构中已不再使用，保留仅为兼容性
        
        Returns:
            dict: 兼容性返回值
        """
        # 简化的兼容性实现
        return {
            'confirmed_text': "".join(self.confirmed_sentences),
            'candidate_text': self.full_sentence,
            'full_text': "".join(self.confirmed_sentences) + self.full_sentence,
            'changed': True,
            'stability_count': 0,
            'confirmed_length': len("".join(self.confirmed_sentences))
        }

    def add_audio_chunk(self, audio_data, audio_format='pcm', sample_rate=16000, seq=None):
        """
        添加音频块
        
        Args:
            audio_data: base64编码的音频数据
            audio_format: 音频格式 (pcm, wav, webm)
            sample_rate: 采样率
            seq: 前端发送的序号，用于排查丢包/乱序
        """
        chunk_start_time = time.time()

        try:
            # 解码音频数据
            raw_audio = base64.b64decode(audio_data)
            audio_logger.trace(
                f"收到音频块: format={audio_format}, raw_size={len(raw_audio)} bytes, sample_rate={sample_rate}")

            # 检查数据大小有效性
            if len(raw_audio) < 10:
                audio_logger.warning(f"音频块太小，跳过: {len(raw_audio)} bytes")
                return

            # 先行落盘保存原始数据（仅对PCM做一比一保留）
            try:
                if self.session_dir and audio_format == 'pcm':
                    self.raw_file_counter += 1
                    raw_name = os.path.join(
                        self.session_dir,
                        f"raw_chunk_{self.raw_file_counter}_{len(raw_audio)}.pcm"
                    )
                    with open(raw_name, 'wb') as f:
                        f.write(raw_audio)

                    # 保存原始块的元数据
                    try:
                        raw_meta = {
                            'seq': int(seq) if isinstance(seq, (int, float, str)) and str(seq).isdigit() else seq,
                            'sample_rate': int(sample_rate) if sample_rate else None,
                            'size_bytes': len(raw_audio),
                            'format': audio_format,
                        }
                        with open(os.path.join(self.session_dir, f"raw_chunk_{self.raw_file_counter}.json"), 'w', encoding='utf-8') as mf:
                            json.dump(raw_meta, mf, ensure_ascii=False)
                    except Exception as meta_e:
                        audio_logger.debug(f"原始音频元数据保存失败: {meta_e}")

                    # 聚合原始PCM流与采样率记录
                    try:
                        self.raw_pcm_accumulator.write(raw_audio)
                        if self.first_pcm_sample_rate is None and sample_rate:
                            self.first_pcm_sample_rate = int(sample_rate)
                    except Exception as acc_e:
                        audio_logger.debug(f"原始音频累积失败: {acc_e}")
                else:
                    if audio_format != 'pcm':
                        self.received_non_pcm = True
            except Exception as raw_save_e:
                audio_logger.debug(f"保存原始音频块失败: {raw_save_e}")

            if audio_format == 'pcm':
                # PCM格式：16位小端格式（保证偶数字节对齐）
                if len(raw_audio) % 2 != 0:
                    raw_audio = raw_audio[:-1]
                audio_array = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32)
                # 归一化到 [-1, 1]
                audio_array = audio_array / 32768.0
                audio_logger.trace(f"PCM解码完成: samples={len(audio_array)}")

            elif audio_format == 'webm':
                # WebM格式处理 - 但通常会有问题，所以添加更好的错误处理
                try:
                    from pydub import AudioSegment
                    audio_stream = io.BytesIO(raw_audio)

                    # 检查数据大小，太小的块可能无法解析
                    if len(raw_audio) < 100:
                        audio_logger.warning(f"WebM音频块太小，跳过: {len(raw_audio)} bytes")
                        return

                    audio = AudioSegment.from_file(audio_stream, format="webm")
                    audio = audio.set_frame_rate(sample_rate).set_channels(1)
                    audio_array = np.array(audio.get_array_of_samples(), dtype=np.float32)

                    # 归一化
                    if audio.sample_width == 2:
                        audio_array = audio_array / 32768.0
                    elif audio.sample_width == 4:
                        audio_array = audio_array / 2147483648.0

                    audio_logger.trace(f"WebM解码完成: samples={len(audio_array)}, sample_width={audio.sample_width}")

                except Exception as webm_error:
                    audio_logger.error(f"WebM解码失败，跳过此音频块: {str(webm_error)}")
                    return

            else:
                # WAV等其他格式
                try:
                    audio_stream = io.BytesIO(raw_audio)
                    # 使用全局导入的 soundfile 避免局部覆盖导致的未绑定错误
                    audio_array, _ = sf.read(audio_stream)
                    if audio_array.dtype != np.float32:
                        audio_array = audio_array.astype(np.float32)
                    audio_logger.trace(f"{audio_format}解码完成: samples={len(audio_array)}")
                except Exception as sf_error:
                    audio_logger.error(f"音频格式 {audio_format} 解码失败: {str(sf_error)}")
                    return

            # 确保audio_array是一维的
            if len(audio_array.shape) > 1:
                audio_array = audio_array.flatten()
                audio_logger.trace(f"音频数据已扁平化: final_samples={len(audio_array)}")

            # 若采样率与目标不同，做线性重采样到 16k
            try:
                input_sr = int(sample_rate) if sample_rate else 16000
            except Exception:
                input_sr = 16000
            if input_sr != self.sample_rate and audio_array.size > 0:
                duration_sec = audio_array.size / float(input_sr)
                target_len = int(duration_sec * self.sample_rate)
                if target_len > 0:
                    old_idx = np.linspace(0, audio_array.size - 1, num=audio_array.size)
                    new_idx = np.linspace(0, audio_array.size - 1, num=target_len)
                    audio_array = np.interp(new_idx, old_idx, audio_array).astype(np.float32)
                    audio_logger.info(f"重采样: {input_sr} -> {self.sample_rate}, samples: {len(audio_array)}")

            # 检查音频质量：避免全零或极值数据
            if len(audio_array) == 0:
                audio_logger.debug("检测到空音频块，跳过")
                return
                
            if np.all(audio_array == 0):
                audio_logger.debug("检测到全零音频块，跳过")
                return

            # 自适应增益控制(AGC): 提升过低RMS的音频以触发识别
            pre_agc_rms = float(np.sqrt(np.mean(audio_array ** 2))) if audio_array.size > 0 else 0.0
            if pre_agc_rms > 0 and pre_agc_rms < 0.005:
                target_rms = 0.03  # 目标轻声级RMS
                gain = min(10.0, target_rms / max(pre_agc_rms, 1e-7))
                audio_array = audio_array * gain
                # 限幅避免削波
                max_abs = float(np.max(np.abs(audio_array))) if audio_array.size > 0 else 0.0
                if max_abs > 1.0:
                    audio_array = audio_array / max_abs
                audio_logger.info(f"AGC已应用: 原始RMS={pre_agc_rms:.6f}, 增益={gain:.2f}")

            # 检查音频幅值合理性
            max_amplitude = np.max(np.abs(audio_array))
            rms_amplitude = np.sqrt(np.mean(audio_array ** 2))
            mean_amplitude = np.mean(np.abs(audio_array))

            # 音频质量统计
            non_zero_samples = np.count_nonzero(audio_array)
            zero_ratio = (len(audio_array) - non_zero_samples) / len(audio_array)
            
            audio_logger.debug(
                f"音频质量分析: samples={len(audio_array)}, max_amp={max_amplitude:.4f}, "
                f"rms_amp={rms_amplitude:.4f}, mean_amp={mean_amplitude:.4f}, "
                f"non_zero_ratio={1-zero_ratio:.3f}, zero_ratio={zero_ratio:.3f}")

            if max_amplitude > 10.0:  # 异常大的值
                audio_logger.warning(f"音频幅值异常: max={max_amplitude}，进行裁剪")
                audio_array = np.clip(audio_array, -1.0, 1.0)
                max_amplitude = np.max(np.abs(audio_array))

            # 添加到缓冲区
            buffer_size_before = self.audio_buffer.size
            if len(self.audio_buffer) > 0:
                self.audio_buffer = np.concatenate([self.audio_buffer, audio_array])
            else:
                self.audio_buffer = audio_array

            self.audio_chunks.append({
                'data': audio_array,
                'timestamp': time.time(),
                'format': audio_format,
                'sample_rate': sample_rate,
                'size': len(audio_array),
                'max_amplitude': max_amplitude,
                'rms_amplitude': rms_amplitude,
                'mean_amplitude': mean_amplitude,
                'zero_ratio': zero_ratio
            })

            # 🔧【2025-01-19 修复】移除缓冲区裁剪逻辑，解决"吞字回删"问题
            # 问题原因：在用户说话过程中截断音频缓冲区，导致get_partial_result()获得不完整的上下文
            # 解决方案：保持句内缓冲区完整，只在finalize_current_sentence()中清空缓冲区
            # 
            # ❌ 原有问题代码（已注释）：
            # max_buffer_size = self.sample_rate * 10
            # buffer_trimmed = False
            # if self.audio_buffer.size > max_buffer_size:
            #     old_buffer_size = self.audio_buffer.size
            #     self.audio_buffer = self.audio_buffer[-max_buffer_size:]  # ⬅️ 这里导致上下文丢失
            #     buffer_trimmed = True
            #     audio_logger.debug(f"缓冲区裁剪: {old_buffer_size} -> {self.audio_buffer.size}")
            
            # ✅ 现在的逻辑：
            # 1. 句内：保持完整音频缓冲区，确保get_partial_result()获得完整上下文
            # 2. 句间：在finalize_current_sentence()中彻底清空缓冲区，避免跨句子干扰

            # 🌐 基于网络标准的活动检测（轻声语音阈值）
            audio_activity_threshold = 0.003  # 网络标准：轻声语音检测阈值
            if max_amplitude > audio_activity_threshold:  # 音频阈值
                self.last_activity_time = time.time()
                activity_level = "高" if max_amplitude > 0.1 else "中" if max_amplitude > 0.03 else "低"
                audio_logger.debug(f"🎵 音频活动[{activity_level}]: max_amp={max_amplitude:.6f} > {audio_activity_threshold}")

            # 详细的音频处理日志
            processing_time = (time.time() - chunk_start_time) * 1000
            audio_logger.debug(
                f"音频块处理完成: format={audio_format}, samples={len(audio_array)}, "
                f"max_amp={max_amplitude:.4f}, rms_amp={rms_amplitude:.4f}, "
                f"buffer_before={buffer_size_before}, buffer_after={self.audio_buffer.size}, "
                f"trimmed={buffer_trimmed}, processing_time={processing_time:.1f}ms"
            )

            # 将本次音频块持久化保存，便于故障排查
            try:
                if self.session_dir:
                    self.temp_file_counter += 1
                    chunk_file = os.path.join(self.session_dir, f"chunk_{self.temp_file_counter}_{len(audio_array)}.wav")
                    sf.write(chunk_file, np.clip(audio_array, -1.0, 1.0), self.sample_rate, subtype='PCM_16')
                    key_logger.info(f"session={self.session_id} save_chunk#{self.temp_file_counter} file={os.path.basename(chunk_file)} samples={len(audio_array)} rms={rms_amplitude:.6f}")
            except Exception as e:
                audio_logger.error(f"保存音频块失败: {str(e)}")

            # 🌐 基于网络标准的有效音频检测和质量统计
            self.quality_stats['total_chunks'] += 1
            effective_audio_threshold = 0.001  # 网络推荐的静音阈值
            
            if rms_amplitude > effective_audio_threshold:
                self.quality_stats['valid_chunks'] += 1
                
                # 更新平均RMS
                self.quality_stats['avg_rms'] = (self.quality_stats['avg_rms'] * (self.quality_stats['valid_chunks'] - 1) + rms_amplitude) / self.quality_stats['valid_chunks']
                
                # 根据RMS值分类音频质量
                if rms_amplitude > 0.05:
                    self.quality_stats['high_quality_chunks'] += 1
                    audio_logger.info(f"🎯 优质音频输入: RMS={rms_amplitude:.6f}, 时长={len(audio_array) / sample_rate:.2f}s")
                elif rms_amplitude > 0.01:
                    audio_logger.info(f"✅ 标准音频输入: RMS={rms_amplitude:.6f}, 时长={len(audio_array) / sample_rate:.2f}s") 
                else:
                    audio_logger.debug(f"🔉 轻声音频输入: RMS={rms_amplitude:.6f}, 时长={len(audio_array) / sample_rate:.2f}s")
            else:
                # 静音/噪音日志已屏蔽，避免日志污染
                pass
            
            # 定期报告质量统计（每30秒）
            if time.time() - self.quality_stats['last_quality_report'] > 30:
                self._report_quality_stats()
                self.quality_stats['last_quality_report'] = time.time()

        except Exception as e:
            audio_logger.error(f"音频块处理失败: {str(e)}")
            audio_logger.error(f"详细错误: {traceback.format_exc()}")

    def get_partial_result(self):
        """
        【再次重构】获取当前句子的识别结果。
        通过识别当前句子的完整音频缓冲区来解决“吞字”问题。
        """
        current_time = time.time()
        if current_time - self.last_update_time < self.chunk_duration:
            return None

        required_samples = int(self.sample_rate * self.min_audio_duration)
        if self.audio_buffer.size < required_samples:
            recognition_logger.debug(f"音频缓冲区不足 ({self.audio_buffer.size} < {required_samples})，跳过")
            return None

        recognition_start_time = time.time()
        recognized_text = ""

        try:
            # 🎯【关键修改】识别整个当前音频缓冲区，而不是切片
            temp_filename = f"partial_{self.partial_save_counter + 1}.wav"
            temp_file = os.path.join(self.session_dir or self.temp_dir, temp_filename)
            
            # 使用16-bit PCM保存，兼容性更好
            sf.write(temp_file, np.clip(self.audio_buffer, -1.0, 1.0), self.sample_rate, subtype='PCM_16')
            self.partial_save_counter += 1

            # 识别当前句子的完整音频缓冲区
            result = recognize(temp_file)
            
            # 提取识别文本的通用函数
            def extract_text_from_result(res):
                if res is None:
                    return ''
                if isinstance(res, str):
                    return res.strip()
                if isinstance(res, dict):
                    return (res.get('text') or res.get('result') or res.get('transcription') or '').strip()
                if isinstance(res, (list, tuple)) and res:
                    for item in res:
                        if isinstance(item, dict) and 'text' in item:
                            return (item.get('text') or '').strip()
                    return (str(res[0]) if res else '').strip()
                return ''

            recognized_text = extract_text_from_result(result)

            # 文本后处理
            if recognized_text:
                # 语音指令检测
                command_result = detect_voice_command(recognized_text)
                if command_result['is_command']:
                    # 如果检测到指令（如"删除"），这里需要实现对应的指令逻辑
                    # 为简化起见，此处暂时忽略指令，实际应用中需要处理
                    recognition_logger.info(f"识别到指令: {recognized_text}，暂不处理")
                    return None # 避免指令词本身上屏
                
            # 🎯【关键修改】直接用新的识别结果更新当前句子
            if recognized_text == self.full_sentence:
                return None
            self.full_sentence = recognized_text
            self.last_update_time = current_time

            recognition_logger.info(f"实时识别: '{self.full_sentence}'")

            # 规范化处理
            normalized_full_text = normalize_text(self.full_sentence)
            
            # 更新统计
            self.quality_stats['recognition_attempts'] += 1
            if recognized_text:
                self.quality_stats['successful_recognitions'] += 1

            return {
                'text': normalized_full_text,
                'is_partial': True,
                'confidence': 0.85,  # 简化的置信度
                'processing_time_ms': int((time.time() - recognition_start_time) * 1000),
                # 🎯 返回简化的、正确的文本状态
                'text_state': {
                    'confirmed_text': normalize_text("".join(self.confirmed_sentences)),
                    'candidate_text': normalized_full_text, # 整个当前句都是候选
                }
            }
        except Exception as e:
            recognition_logger.error(f"实时识别失败: {e}\n{traceback.format_exc()}")
            return None

    def _analyze_semantic_completeness(self, text):
        """
        分析文本的语义完整性
        
        Args:
            text: 待分析的文本
            
        Returns:
            dict: {
                'is_complete': bool,  # 是否语义完整
                'completeness_score': float,  # 完整性得分 0-1
                'missing_elements': list,  # 缺失的语义要素
                'sentence_type': str  # 句子类型
            }
        """
        if not text or not text.strip():
            return {
                'is_complete': False,
                'completeness_score': 0.0,
                'missing_elements': ['content'],
                'sentence_type': 'empty'
            }
        
        text = text.strip()
        completeness_score = 0.0
        missing_elements = []
        
        # 🎯 基础长度检查
        if len(text) >= 2:
            completeness_score += 0.2
        else:
            missing_elements.append('sufficient_length')
        
        # 🎯 句子类型识别
        sentence_type = 'statement'  # 默认陈述句
        
        # 疑问句检测
        question_indicators = ['什么', '哪里', '怎么', '为什么', '谁', '何时', '多少', '吗', '呢']
        if any(indicator in text for indicator in question_indicators) or text.endswith('？'):
            sentence_type = 'question'
            # 疑问句通常语义相对完整
            completeness_score += 0.3
        
        # 感叹句检测
        exclamation_indicators = ['太', '真', '好', '哇', '哎呀', '天哪']
        if any(indicator in text for indicator in exclamation_indicators) or text.endswith('！'):
            sentence_type = 'exclamation'
            completeness_score += 0.3
        
        # 🎯 语法结构分析
        # 主谓宾结构检测（简化版）
        has_subject = self._detect_subject(text)
        has_predicate = self._detect_predicate(text)
        has_object = self._detect_object(text)
        
        if has_subject:
            completeness_score += 0.2
        else:
            missing_elements.append('subject')
            
        if has_predicate:
            completeness_score += 0.3
        else:
            missing_elements.append('predicate')
        
        # 🎯 语义连贯性检查
        # 检查是否有明显的连接词暗示句子未完成
        incomplete_connectors = ['但是', '不过', '然后', '接着', '另外', '而且', '所以', '因此', '如果', '虽然']
        trailing_connectors = ['的', '了', '着', '过']
        
        for connector in incomplete_connectors:
            if text.endswith(connector):
                completeness_score -= 0.3
                missing_elements.append('continuation')
                break
                
        for connector in trailing_connectors:
            if text.endswith(connector):
                completeness_score -= 0.2
                break
        
        # 🎯 标点符号检查
        if text.endswith(('。', '！', '？', '.', '!', '?')):
            completeness_score += 0.3
            sentence_type += '_punctuated'
        else:
            missing_elements.append('punctuation')
        
        # 🎯 特殊情况处理
        # 时间表达通常是完整的
        time_patterns = ['今天', '昨天', '明天', '现在', '刚才', '一会儿', '下午', '晚上', '早上']
        if any(pattern in text for pattern in time_patterns):
            completeness_score += 0.1
        
        # 限制分数范围
        completeness_score = max(0.0, min(1.0, completeness_score))
        
        return {
            'is_complete': completeness_score >= 0.6,  # 阈值：60%
            'completeness_score': completeness_score,
            'missing_elements': missing_elements,
            'sentence_type': sentence_type
        }
    
    def _detect_subject(self, text):
        """检测主语（简化版）"""
        # 人称代词
        pronouns = ['我', '你', '他', '她', '它', '我们', '你们', '他们', '她们']
        if any(pronoun in text for pronoun in pronouns):
            return True
        
        # 名词性主语的简单模式（姓名、专有名词等）
        if len(text) > 3 and any(char.isalpha() for char in text):
            return True
            
        return False
    
    def _detect_predicate(self, text):
        """检测谓语（简化版）"""
        # 动词性词汇
        verbs = ['是', '有', '在', '去', '来', '做', '说', '看', '听', '想', '能', '要', '会', '可以', '应该', '需要']
        if any(verb in text for verb in verbs):
            return True
            
        # 形容词性谓语
        adjectives = ['好', '坏', '大', '小', '多', '少', '高', '低', '快', '慢', '美', '丑']
        if any(adj in text for adj in adjectives):
            return True
            
        return False
    
    def _detect_object(self, text):
        """检测宾语（简化版）"""
        # 如果有谓语且文本较长，可能有宾语
        if self._detect_predicate(text) and len(text) > 4:
            return True
        return False

    def check_sentence_complete(self):
        """
        智能端点检测 - 判断句子完整性
        🎯【修改】判断对象从 confirmed+candidate 改为 self.full_sentence
        """
        if not self.full_sentence:
            return False

        current_time = time.time()
        silence_duration = current_time - self.last_activity_time
        
        # 语义完整性分析
        # 注意: _analyze_semantic_completeness 方法内部应使用 self.full_sentence
        semantic_analysis = self._analyze_semantic_completeness(self.full_sentence)

        # 智能端点判断逻辑
        if semantic_analysis['is_complete'] and silence_duration > 1.0:
            return True
        if silence_duration > self.sentence_complete_threshold:
            return True
            
        return False

    def finalize_current_sentence(self):
        """
        【已重构】确认当前句子为最终结果，并更新处理状态。
        """
        if not self.full_sentence.strip():
            return ""

        # 智能标点预测
        silence_duration = time.time() - self.last_activity_time
        final_text = self.predict_punctuation(self.full_sentence, silence_duration)
        
        # 文本规范化
        final_text = normalize_text(final_text)

        if not final_text:
            return ""

        self.confirmed_sentences.append(final_text)
        recognition_logger.info(f"🏁 最终确认句子 #{len(self.confirmed_sentences)}: '{final_text}'")

        # 🎯【至关重要】硬重置当前句子的状态并清空音频缓冲区，避免跨句子干扰
        self.full_sentence = ""
        self.current_sentence = ""  # 🔧【2025-01-19 修复】同时重置兼容字段，确保状态一致
        try:
            self.audio_buffer = np.array([], dtype=np.float32)
        except Exception:
            # 兜底防御，确保不因异常阻断流程
            self.audio_buffer = np.array([], dtype=np.float32)
        
        return final_text

    def get_final_result(self):
        """
        获取最终识别结果
        
        Returns:
            str: 最终识别文本
        """
        # 🔧【2025-01-19 修复】优先返回当前实时识别的句子
        if self.audio_buffer.size == 0:
            return self.full_sentence  # 统一使用 full_sentence

        try:
            # 使用离线模型进行最终识别
            temp_file = os.path.join(self.temp_dir, f"final_{int(time.time() * 1000)}.wav")
            sf.write(temp_file, self.audio_buffer, self.sample_rate)
            result = recognize(temp_file)
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass

            # 统一解析不同返回类型
            final_text = ''
            try:
                if isinstance(result, str):
                    final_text = result.strip()
                elif isinstance(result, dict):
                    final_text = (result.get('text') or result.get('result') or result.get('transcription') or '').strip()
                elif isinstance(result, (list, tuple)) and len(result) > 0:
                    first = result[0]
                    if isinstance(first, dict):
                        final_text = (first.get('text') or first.get('result') or '').strip()
                    else:
                        final_text = str(first).strip()
            except Exception:
                final_text = ''

            # 🔧【2025-01-19 修复】统一更新 full_sentence
            if final_text:
                # 优先使用最终识别结果，但不覆盖已有的实时识别结果（除非更准确）
                return final_text
            else:
                return self.full_sentence  # 回退到当前实时识别句子

        except Exception as e:
            print(f"最终识别失败: {str(e)}")
            return self.full_sentence  # 回退到当前实时识别句子

    def _extract_words(self, text):
        """
        提取分词结果
        
        Args:
            text: 识别文本
            
        Returns:
            list: 分词结果列表
        """
        # 简单的中文分词（可以后续接入更专业的分词工具）
        words = []
        if text:
            # 按标点符号分割
            import re
            segments = re.split(r'[，。！？；：]', text)
            for segment in segments:
                if segment.strip():
                    words.append({
                        'word': segment.strip(),
                        'confidence': 0.8  # 默认置信度
                    })
        return words

    def detect_pause(self):
        """
        检测是否有停顿
        
        Returns:
            bool: 是否检测到停顿
        """
        return time.time() - self.last_chunk_time > self.silence_threshold

    def _report_quality_stats(self):
        """报告音频质量统计"""
        stats = self.quality_stats
        if stats['total_chunks'] > 0:
            valid_ratio = stats['valid_chunks'] / stats['total_chunks']
            quality_ratio = stats['high_quality_chunks'] / max(1, stats['valid_chunks'])
            recognition_success_rate = stats['successful_recognitions'] / max(1, stats['recognition_attempts'])
            
            audio_logger.info(
                f"📊 音频质量报告: "
                f"有效率={valid_ratio:.1%}, 高质量率={quality_ratio:.1%}, "
                f"平均RMS={stats['avg_rms']:.6f}, 识别成功率={recognition_success_rate:.1%} "
                f"(总块数:{stats['total_chunks']}, 识别尝试:{stats['recognition_attempts']})"
            )

    def save_original_audio_files(self):
        """🔧 增强版本：在会话结束时输出原始PCM合并文件与WAV，支持30秒测试文件生成"""
        try:
            if not self.session_dir:
                audio_logger.warning("会话目录为空，无法保存音频")
                return
            
            raw_bytes = self.raw_pcm_accumulator.getvalue()
            if not raw_bytes:
                audio_logger.warning("无原始音频数据，跳过保存")
                return
                
            # 🔧 计算音频时长统计
            sr = int(self.first_pcm_sample_rate) if self.first_pcm_sample_rate else int(self.sample_rate)
            pcm_int16 = np.frombuffer(raw_bytes, dtype=np.int16)
            duration_seconds = len(pcm_int16) / sr
            
            audio_logger.info(f"🎤 原始音频统计: {len(raw_bytes)} bytes, {len(pcm_int16)} 样本, {duration_seconds:.2f}秒, 采样率{sr}Hz")
            
            # 原始PCM落盘
            raw_pcm_path = os.path.join(self.session_dir, 'original_raw.pcm')
            with open(raw_pcm_path, 'wb') as f:
                f.write(raw_bytes)
            audio_logger.info(f"💾 原始PCM已保存: {raw_pcm_path}")

            # 生成完整WAV（不做任何处理）
            try:
                pcm_float = (pcm_int16.astype(np.float32) / 32768.0).clip(-1.0, 1.0)
                raw_wav_path = os.path.join(self.session_dir, 'original_raw.wav')
                sf.write(raw_wav_path, pcm_float, sr, subtype='PCM_16')
                
                # 生成音频统计信息
                audio_stats = {
                    'duration': duration_seconds,
                    'sample_rate': sr,
                    'samples': len(pcm_int16),
                    'channels': 1,
                    'rms': np.sqrt(np.mean(pcm_float**2)),
                    'peak': np.max(np.abs(pcm_float)),
                    'dynamic_range': np.max(pcm_float) - np.min(pcm_float)
                }
                
                # 保存音频统计信息
                stats_path = os.path.join(self.session_dir, 'audio_stats.json')
                with open(stats_path, 'w', encoding='utf-8') as f:
                    json.dump(audio_stats, f, ensure_ascii=False, indent=2)
                    
                audio_logger.info(f"✅ 原始音频已生成: {raw_wav_path}")
                audio_logger.info(f"📊 音频统计: RMS={audio_stats['rms']:.4f}, Peak={audio_stats['peak']:.4f}, 动态范围={audio_stats['dynamic_range']:.4f}")
                key_logger.info(f"session={self.session_id} original_saved wav={os.path.basename(raw_wav_path)} duration={duration_seconds:.2f}s sr={sr} samples={len(pcm_int16)}")
                
                # 🔧 如果音频超过30秒，生成截取版本用于测试
                if duration_seconds > 30:
                    test_samples = 30 * sr  # 30秒对应的样本数
                    test_audio = pcm_float[:test_samples]
                    test_wav_path = os.path.join(self.session_dir, 'test_30s.wav')
                    sf.write(test_wav_path, test_audio, sr, subtype='PCM_16')
                    audio_logger.info(f"🎧 30秒测试音频已生成: {test_wav_path}")
                    
            except Exception as wav_e:
                audio_logger.error(f"原始WAV生成失败: {wav_e}")
                import traceback
                audio_logger.error(traceback.format_exc())
                
        except Exception as e:
            audio_logger.error(f"保存原始音频失败: {e}")
            import traceback
            audio_logger.error(traceback.format_exc())


@sock.route('/ws/recognize')
def ws_recognize(ws):
    """
    WebSocket实时语音识别端点 - 输入法风格实时反馈
    
    协议格式:
    {
        "type": "start|chunk|end",
        "audio": base64编码的PCM音频数据,
        "format": "pcm|wav|webm",
        "sample_rate": 16000
    }
    
    返回格式:
    {
        "type": "partial|final|error",
        "text": "识别结果",
        "confidence": 置信度,
        "words": 分词结果,
        "timestamp": 时间戳
    }
    """
    session_id = str(uuid.uuid4())[:8]
    ws_logger.info(f"会话开始: {session_id}")
    key_logger.info(f"session={session_id} started")
    session = RealtimeSpeechSession()
    # 设置会话目录用于持久化保存
    try:
        session.set_session(session_id)
    except Exception:
        pass
    try:
        global_counters['total_connections'] += 1
        global_counters['active_connections'] += 1
        active_sessions[session_id] = {
            'start': int(time.time() * 1000),
            'chunks': 0,
            'partials': 0,
            'finals': 0,
            'last_active': int(time.time() * 1000),
            'last_partial': '',
            'last_final': ''
        }
    except Exception:
        pass

    message_count = 0
    audio_chunks_received = 0
    partial_results_sent = 0
    final_results_sent = 0

    while True:
        try:
            message = ws.receive()
            message_count += 1
            try:
                global_counters['total_messages'] += 1
            except Exception:
                pass

            if not message:
                ws_logger.debug(f"会话{session_id}: 收到空消息，连接关闭")
                break

            msg = json.loads(message)

            # 兼容 RecorderManager 等外部格式 { data: { status, format, encoding, audio } }
            # status: 0=start, 1=chunk, 2=end
            seq_local = None
            if 'data' in msg and isinstance(msg.get('data'), dict):
                data_obj = msg['data']
                status = data_obj.get('status')
                mapped_type = 'chunk'
                if status == 0:
                    mapped_type = 'start'
                elif status == 2:
                    mapped_type = 'end'

                # 解析格式 "audio/L16;rate=16000"
                fmt = data_obj.get('format', 'audio/L16;rate=16000')
                fmt_lower = str(fmt).lower()
                if 'l16' in fmt_lower or 'pcm' in fmt_lower:
                    audio_format = 'pcm'
                elif 'webm' in fmt_lower:
                    audio_format = 'webm'
                else:
                    audio_format = 'wav'

                # 提取采样率
                try:
                    if 'rate=' in fmt_lower:
                        sr_txt = fmt_lower.split('rate=')[-1].split(';')[0]
                        sample_rate = int(sr_txt)
                    else:
                        sample_rate = int(msg.get('sample_rate', 16000))
                except Exception:
                    sample_rate = 16000

                msg_type = mapped_type
                audio_data = data_obj.get('audio', '')
                try:
                    seq_local = data_obj.get('seq', msg.get('seq'))
                except Exception:
                    seq_local = None
            else:
                msg_type = msg.get('type', 'chunk')
                audio_data = msg.get('audio', '')
                audio_format = msg.get('format', 'pcm')
                sample_rate = msg.get('sample_rate', 16000)
                try:
                    seq_local = msg.get('seq')
                except Exception:
                    seq_local = None

            ws_logger.debug(f"会话{session_id}: 收到消息#{message_count}, type={msg_type}, format={audio_format}")

            if msg_type == 'start':
                ws_logger.info(f"会话{session_id}: 开始实时识别")
                session.reset()
                try:
                    active_sessions[session_id]['last_active'] = int(time.time() * 1000)
                except Exception:
                    pass

                response = {
                    "type": "started",
                    "message": "实时识别已开始",
                    "timestamp": int(time.time() * 1000),
                    "session_id": session_id
                }
                ws.send(json.dumps(response))
                ws_logger.debug(f"会话{session_id}: 发送started消息")
                continue

            elif msg_type == 'end':
                ws_logger.info(f"会话{session_id}: 结束实时识别，处理最终结果")
                key_logger.info(f"session={session_id} end requested")

                # 处理最终结果 - 确保最后一句话也输出
                final_sentence = None
                # 🔧【2025-01-19 修复】统一使用 full_sentence 状态，避免状态不一致
                if session.full_sentence:
                    final_sentence = session.finalize_current_sentence()
                    if final_sentence:
                        final_sentence = normalize_text(final_sentence)
                elif session.audio_buffer.size > 0:
                    # 如果还有缓冲音频但 full_sentence 为空，尝试进行最终识别
                    try:
                        last_text = session.get_final_result()
                        if last_text and last_text.strip():
                            session.full_sentence = last_text.strip()  # 🔧 统一使用 full_sentence
                            final_sentence = session.finalize_current_sentence()
                            if final_sentence:
                                final_sentence = normalize_text(final_sentence)
                    except Exception:
                        pass

                # 如果仍然没有，则回退输出最近的非空实时句子或提示
                if not final_sentence:
                    fallback = session.full_sentence.strip() if session.full_sentence else ''  # 🔧 统一使用 full_sentence
                    if not fallback and len(session.confirmed_sentences) > 0:
                        fallback = session.confirmed_sentences[-1].strip()
                    if fallback:
                        final_sentence = fallback

                if final_sentence:
                    # 去重/幂等控制
                    if session._is_duplicate_final(final_sentence):
                        ws_logger.info(f"会话{session_id}: 跳过重复final(结束): '{final_sentence}'")
                    else:
                        segment_id = session._allocate_segment_id()
                        session._register_final(final_sentence)
                        final_results_sent += 1
                        response = {
                            "type": "final",
                            "text": final_sentence,
                            "index": len(session.confirmed_sentences) - 1,
                            "timestamp": int(time.time() * 1000),
                            "is_final": True,
                            "segment_id": segment_id,
                            "session_id": session_id,
                            "offsets": {
                                "start_ms": None,
                                "end_ms": None
                            }
                        }
                        ws.send(json.dumps(response))
                        ws_logger.info(f"会话{session_id}: 发送最终句子#{final_results_sent}: '{final_sentence}', segment_id={segment_id}")

                # 在结束时尝试保存原始音频文件
                try:
                    session.save_original_audio_files()
                except Exception:
                    pass

                # 发送会话结束消息
                response = {
                    "type": "session_end",
                    "message": "识别会话结束",
                    "total_sentences": len(session.confirmed_sentences),
                    "timestamp": int(time.time() * 1000),
                    "session_id": session_id,
                    "stats": {
                        "messages_received": message_count,
                        "audio_chunks_processed": audio_chunks_received,
                        "partial_results_sent": partial_results_sent,
                        "final_results_sent": final_results_sent
                    }
                }
                ws.send(json.dumps(response))
                ws_logger.info(
                    f"会话{session_id}: 结束统计 - 消息:{message_count}, 音频块:{audio_chunks_received}, 实时:{partial_results_sent}, 最终:{final_results_sent}")
                break

            elif msg_type == 'reset':
                ws_logger.info(f"会话{session_id}: 重置会话状态")
                session.reset()

                response = {
                    "type": "reset_confirm",
                    "message": "会话状态已重置",
                    "timestamp": int(time.time() * 1000)
                }
                ws.send(json.dumps(response))
                ws_logger.debug(f"会话{session_id}: 发送reset_confirm消息")
                continue

            elif msg_type == 'ping':
                # 心跳响应
                try:
                    pong = {
                        "type": "pong",
                        "ts": msg.get("ts", int(time.time() * 1000)),
                        "timestamp": int(time.time() * 1000)
                    }
                    ws.send(json.dumps(pong))
                except Exception:
                    pass
                continue

            elif msg_type == 'chunk':
                # 处理音频块
                if audio_data:
                    audio_chunks_received += 1
                    ws_logger.trace(f"会话{session_id}: 处理音频块#{audio_chunks_received}")

                    session.add_audio_chunk(audio_data, audio_format, sample_rate, seq_local)
                    try:
                        global_counters['total_chunks'] += 1
                        active_sessions[session_id]['chunks'] += 1
                        active_sessions[session_id]['last_active'] = int(time.time() * 1000)
                    except Exception:
                        pass

                    # 检查是否有句子完成
                    sentence_completed = session.check_sentence_complete()
                    if sentence_completed:
                        completed_sentence = session.finalize_current_sentence()
                        if completed_sentence and len(completed_sentence.strip()) >= 2:
                            completed_sentence = normalize_text(completed_sentence)

                            # 去重/幂等：跳过与最近final重复的内容
                            if session._is_duplicate_final(completed_sentence):
                                ws_logger.info(f"会话{session_id}: 跳过重复final: '{completed_sentence}'")
                            else:
                                segment_id = session._allocate_segment_id()
                                session._register_final(completed_sentence)

                                final_results_sent += 1
                                response = {
                                    "type": "final",
                                    "text": completed_sentence,
                                    "index": len(session.confirmed_sentences) - 1,
                                    "timestamp": int(time.time() * 1000),
                                    "is_final": True,
                                    "segment_id": segment_id,
                                    "session_id": session_id,
                                    "offsets": {
                                        "start_ms": None,
                                        "end_ms": None
                                    }
                                }
                                ws.send(json.dumps(response))
                                ws_logger.info(f"会话{session_id}: 句子完成#{final_results_sent}: '{completed_sentence}', segment_id={segment_id}")
                                try:
                                    global_counters['total_finals'] += 1
                                    active_sessions[session_id]['finals'] += 1
                                    active_sessions[session_id]['last_final'] = completed_sentence
                                    key_logger.info(f"session={session_id} final id={segment_id}: '{completed_sentence}'")
                                except Exception:
                                    pass

                    # 获取当前句子的实时识别结果
                    partial_result = session.get_partial_result()
                    if partial_result:
                        partial_results_sent += 1
                        response = {
                            "type": "partial",
                            "text": partial_result["text"],
                            "confidence": partial_result.get("confidence", 0.0),
                            "words": partial_result.get("words", []),
                            "timestamp": int(time.time() * 1000),
                            "processing_time_ms": partial_result.get("processing_time_ms", 0),
                            "is_final": False,
                            "session_id": session_id,
                            "text_state": partial_result.get("text_state")
                        }
                        ws.send(json.dumps(response))
                        ws_logger.debug(
                            f"会话{session_id}: 发送实时结果#{partial_results_sent}: '{partial_result['text']}' (置信度: {partial_result.get('confidence', 0):.3f})")
                        try:
                            global_counters['total_partials'] += 1
                            active_sessions[session_id]['partials'] += 1
                            active_sessions[session_id]['last_partial'] = partial_result['text']
                        except Exception:
                            pass
                else:
                    ws_logger.warning(f"会话{session_id}: 收到chunk消息但无音频数据")

        except json.JSONDecodeError as e:
            ws_logger.error(f"会话{session_id}: JSON解析失败: {str(e)}")
            error_response = {
                "type": "error",
                "message": f"消息格式错误: {str(e)}",
                "timestamp": int(time.time() * 1000)
            }
            ws.send(json.dumps(error_response))

        except Exception as e:
            error_info = traceback.format_exc()
            ws_logger.error(f"会话{session_id}: WebSocket错误详情:\n{error_info}")

            error_response = {
                "type": "error",
                "message": f"识别错误: {str(e)}",
                "timestamp": int(time.time() * 1000)
            }
            try:
                ws.send(json.dumps(error_response))
            except:
                ws_logger.error(f"会话{session_id}: 无法发送错误消息，连接可能已断开")
            break

    # 连接关闭时也做一次原始音频保存尝试
    try:
        session.save_original_audio_files()
    except Exception:
        pass

    ws_logger.info(f"会话{session_id}: WebSocket连接关闭")
    key_logger.info(f"session={session_id} closed")
    try:
        global_counters['active_connections'] = max(0, global_counters['active_connections'] - 1)
        if session_id in active_sessions:
            del active_sessions[session_id]
    except Exception:
        pass


# ================== 应用启动 ==================

if __name__ == '__main__':
    # 从环境变量获取端口，默认8210与start_rest.sh保持一致
    port = int(os.environ.get('PORT', 8210))

    print(f"E-Voice REST API服务器启动中...")
    print(f"监听端口: {port}")
    print(f"健康检查: http://localhost:{port}/")
    print(f"API文档参考: tests/README.md")

    # 启动系统监控
    try:
        from monitoring.system_monitor import start_system_monitoring
        start_system_monitoring()
        logger.success("🔍 系统监控已启动")
    except ImportError:
        logger.warning("⚠️ 无法启动系统监控（monitoring模块未找到）")

    try:
        # 启动SocketIO服务器
        socketio.run(app, host='0.0.0.0', port=port)
    finally:
        # 停止系统监控
        try:
            from monitoring.system_monitor import stop_system_monitoring
            stop_system_monitoring()
            logger.info("🔍 系统监控已停止")
        except ImportError:
            pass
