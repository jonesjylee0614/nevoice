# E-Voice 废弃代码归档

**创建日期**: 2025-11-09
**目的**: 存放已废弃但保留用于参考的代码

---

## 📁 目录说明

此目录用于存放 E-Voice 项目中已被新架构替代的废弃代码。这些代码不再在生产环境中使用，但保留用于：

1. **历史参考**: 了解旧实现的设计思路
2. **测试兼容**: 部分历史测试仍依赖这些代码
3. **迁移对比**: 对比新旧实现的差异

---

## ⚠️ 重要说明

- **禁止在生产环境使用此目录中的代码**
- **新功能开发请使用新架构**
- **此目录仅供参考，不保证代码可用性**

---

## 📂 归档清单

### 2025-11-09-session-cleanup

**归档原因**: 实时识别架构重构

**废弃文件**:
- `session.py` - 旧的 `RealtimeSpeechSession` 类

**替代方案**:
- 新架构位于 `e-voice/speech_recognition/streaming/`
  - `engine.py` - StreamingEngine
  - `state.py` - StreamingState
  - `text_accumulator.py` - TextAccumulator
  - 详见: `e-docs/2025-11-09-实时识别修复重构/`

**已知问题**:
1. 状态管理复杂，存在多个冗余字段
2. 缓冲区裁剪逻辑导致"吞字回删"问题
3. 双模型调用混乱，难以维护

**仍在使用的地方**:
- `e-voice/tests/test_session_pipeline.py` (历史测试)

---

## 🗂️ 使用指南

### 查看归档代码

```bash
# 查看废弃的 session.py
cat e-voice-deprecated/2025-11-09-session-cleanup/session.py

# 查看归档说明
cat e-voice-deprecated/2025-11-09-session-cleanup/README.md
```

### 迁移到新架构

如果你正在使用废弃代码，请参考以下迁移指南：

**旧代码**:
```python
from server.session import RealtimeSpeechSession

session = RealtimeSpeechSession()
session.process_audio_chunk(audio_chunk)
```

**新代码**:
```python
from speech_recognition.streaming.engine import StreamingEngine
from speech_recognition.streaming.state import StreamingState

state = StreamingState(...)
engine = StreamingEngine()
events = engine.push(audio_chunk, state)
```

详细迁移指南: `e-docs/2025-11-09-实时识别修复重构/01-修复计划.md`

---

## 📝 归档政策

### 何时归档

代码满足以下条件时应归档：
1. 已被新实现完全替代
2. 不再在生产环境使用
3. 仅保留用于参考或历史测试

### 归档流程

1. 创建带日期的归档子目录: `YYYY-MM-DD-描述/`
2. 移动废弃文件到归档目录
3. 创建归档说明 README
4. 更新相关引用（如测试文件）
5. 在主文档中记录归档情况

### 清理政策

- 归档代码保留 **至少 6 个月**
- 6 个月后如无使用需求，可考虑删除
- 删除前需确认：
  - 无测试依赖
  - 无参考价值
  - 已有完整的迁移文档

---

## 📞 联系方式

如有疑问，请联系：
- 项目负责人: [待填写]
- 技术支持: [待填写]

---

**最后更新**: 2025-11-09
**维护者**: Claude Code
