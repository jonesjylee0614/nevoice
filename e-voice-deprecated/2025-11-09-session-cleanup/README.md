# Session 架构废弃归档

**归档日期**: 2025-11-09
**原路径**: `nevoice/e-voice/server/session.py`
**原因**: 实时识别架构重构，被新的 streaming 模块替代

---

## 📋 归档文件清单

| 文件名 | 原路径 | 大小 | 说明 |
|-------|--------|------|------|
| `session.py` | `e-voice/server/session.py` | ~77 KB | RealtimeSpeechSession 类 |

---

## ⚠️ 废弃原因

### 核心问题

1. **状态管理复杂**
   - 存在多个冗余字段（confirmed_text、candidate_text、full_sentence 等）
   - 状态转换逻辑不清晰
   - 难以维护和扩展

2. **缓冲区裁剪问题**
   - 音频缓冲区裁剪逻辑导致上下文丢失
   - 引发"吞字回删"问题
   - 影响识别准确度

3. **双模型调用混乱**
   - ModelScope 离线识别 + FunASR 流式混用
   - 代码逻辑分散
   - 维护成本高

---

## 🆕 新架构替代方案

### 新架构位置

```
e-voice/speech_recognition/streaming/
├── engine.py              # StreamingEngine - 流式推理引擎
├── state.py               # StreamingState - 状态管理
├── text_accumulator.py    # TextAccumulator - 文本累积器
├── loader.py              # ModelLoader - 模型加载器
└── bundle.py              # ModelBundle - 模型打包
```

### 核心改进

| 方面 | 旧架构 (session.py) | 新架构 (streaming/) |
|-----|-------------------|-------------------|
| **状态管理** | 复杂，多个冗余字段 | 清晰，单一数据类 |
| **缓冲区处理** | 裁剪导致上下文丢失 | 保持完整缓冲区 |
| **模型调用** | 双模型混用 | 统一 FunASR 流式 |
| **代码组织** | 单文件 2000+ 行 | 模块化，职责清晰 |
| **可维护性** | 低 | 高 |

### 迁移示例

**旧代码** (session.py):
```python
from server.session import RealtimeSpeechSession

session = RealtimeSpeechSession()
session.audio_chunks = []

# 处理音频块
for chunk in audio_chunks:
    session.audio_chunks.append(chunk)
    session.process_realtime_audio()

# 最终识别
final_result = session.finalize_current_sentence()
```

**新代码** (streaming/):
```python
from speech_recognition.streaming.engine import StreamingEngine
from speech_recognition.streaming.state import StreamingState
from speech_recognition.streaming.text_accumulator import TextAccumulator

# 初始化
state = StreamingState(
    session_id="xxx",
    request_id="yyy",
    chunk_interval=40,
    sample_rate=16000,
    hotwords={},
)
state.text_accumulator = TextAccumulator()
engine = StreamingEngine()

# 处理音频块（在线识别）
for chunk in audio_chunks:
    events = engine.push(chunk, state)
    # events 包含 partial 事件

# 最终识别（离线纠错）
final_events = engine.flush(state)
# final_events 包含 correction 事件
```

---

## 🔗 仍在使用的地方

### 测试文件

**文件**: `e-voice/tests/test_session_pipeline.py`

**使用方式**:
```python
# 通过绝对路径导入
_SESSION_SPEC = importlib.util.spec_from_file_location(
    "server.session",
    "../../../e-voice-deprecated/2025-11-09-session-cleanup/session.py",
)
RealtimeSpeechSession = getattr(_SESSION_MODULE, "RealtimeSpeechSession")
```

**迁移建议**:
- 短期：保持现状，测试继续使用废弃代码
- 中期：将测试迁移到新架构
- 长期：删除旧测试，使用新测试框架

---

## 📚 参考文档

### 修复重构文档

详细的修复过程和新架构说明：
- **修复计划**: `e-docs/2025-11-09-实时识别修复重构/01-修复计划.md`
- **代码变更清单**: `e-docs/2025-11-09-实时识别修复重构/02-代码变更清单.md`
- **修复总结报告**: `e-docs/2025-11-09-实时识别修复重构/03-修复总结报告.md`

### 项目文档

- **总体架构**: `e-docs/2025-项目指南/总体架构与说明.md`
- **后端详解**: `e-docs/2025-项目指南/后端服务-e-voice详解.md`

---

## 🗓️ 归档时间线

| 日期 | 事件 |
|-----|------|
| 2025-11-09 | 新架构开发完成，修复核心 Bug |
| 2025-11-09 | 将 session.py 标记为废弃 |
| 2025-11-09 | 移动到废弃代码归档目录 |
| 2025-05-09 | 计划清理（6 个月后） |

---

## ⚙️ 技术细节

### RealtimeSpeechSession 类特点

**主要方法**:
- `__init__()` - 初始化会话
- `process_realtime_audio()` - 处理实时音频
- `finalize_current_sentence()` - 完成当前句子
- `predict_punctuation()` - 预测标点
- `_auto_correct_text()` - 自动纠错

**状态字段**:
```python
self.audio_chunks = []           # 音频块列表
self.full_sentence = ""          # 完整句子
self.confirmed_sentences = []    # 已确认句子
self._live_text = ""             # 当前段落流式文本
self._segment_revision = 0       # 段落版本号
```

**问题字段**（已废弃但未清理）:
```python
# 🗑️ 废弃但仍保留
self.confirmed_text = ""         # 已确认文本
self.candidate_text = ""         # 候选文本
self.text_stability_tracker = {} # 文本稳定性跟踪
```

---

## 📝 归档检查清单

- [x] 代码已复制到归档目录
- [x] 创建归档说明文档
- [x] 识别所有引用位置
- [ ] 更新测试文件路径（待执行）
- [ ] 从原位置删除文件（待执行）
- [ ] 更新主文档记录（待执行）

---

**归档人**: Claude Code
**审核状态**: 待审核
