# 语音识别调试指南

## 问题描述
语音输入法风格的语音识别测试界面输出有点乱，需要通过日志分析来定位问题。

## 快速调试步骤

### 1. 启动调试模式
```bash
# 使用专用的调试脚本启动服务器
python test_speech_recognition.py
```

这个脚本会：
- 检查运行环境和依赖
- 清理并备份旧日志
- 启动服务器并实时显示输出
- 生成详细的分层日志文件

### 2. 访问测试页面
打开浏览器访问：
```
http://localhost:8210/../tests/pages/speech-recognition-test.html
```

### 3. 使用调试功能

#### 前端日志
- 勾选"显示详细日志"查看实时调试信息
- 点击"下载日志"保存前端日志到文件
- 点击"获取服务器日志"下载后端日志

#### 后端日志文件
系统会自动生成以下日志文件：

| 日志文件 | 用途 | 详细程度 |
|---------|------|----------|
| `logs/websocket_speech.log` | WebSocket连接和消息处理 | DEBUG级别 |
| `logs/audio_processing.log` | 音频数据处理和格式转换 | TRACE级别 |
| `logs/recognition_results.log` | 语音识别结果和性能统计 | INFO级别 |
| `logs/error.log` | 错误和异常信息 | ERROR级别 |

## 调试流程

### 步骤1：重现问题
1. 启动调试服务器：`python test_speech_recognition.py`
2. 在测试页面中：
   - 点击"连接"建立WebSocket连接
   - 点击"开始实时识别"
   - 正常说话测试
   - 观察"实时内容"和"确认文本"区域的显示

### 步骤2：收集日志
1. 测试完成后，点击"下载日志"保存前端日志
2. 点击"获取服务器日志"获取后端日志
3. 或直接查看 `logs/` 目录下的日志文件

### 步骤3：分析日志
重点关注以下信息：

#### WebSocket连接日志 (`websocket_speech.log`)
```
会话abc12345: WebSocket会话开始
会话abc12345: 收到消息#1, type=start, format=pcm
会话abc12345: 开始实时识别
会话abc12345: 处理音频块#1
会话abc12345: 发送实时结果#1: '你好' (置信度: 0.856)
会话abc12345: 句子完成#1: '你好'
```

#### 音频处理日志 (`audio_processing.log`)
```
收到音频块: format=pcm, raw_size=8192 bytes, sample_rate=16000
PCM解码完成: samples=4096
音频块处理完成: format=pcm, samples=4096, max_amp=0.2341, rms_amp=0.0456
有效音频输入: RMS=0.0456, 时长=0.26s
```

#### 识别结果日志 (`recognition_results.log`)
```
开始实时识别: buffer_size=65536, duration=4.10s
识别结果: '你好世界' (置信度: 0.892)
句子更新: '你好' -> '你好世界'
```

## 常见问题排查

### 问题1：实时区域不显示内容
**症状**：说话后"实时内容"区域没有文字更新

**排查步骤**：
1. 检查 `websocket_speech.log` 中是否有"收到音频块"的记录
2. 检查 `audio_processing.log` 中的 RMS 值是否大于 0.005
3. 确认 `recognition_results.log` 中是否有识别结果

### 问题2：句子不能确认到最终区域
**症状**：实时区域有文字，但不转移到确认区域

**排查步骤**：
1. 检查 `websocket_speech.log` 中"句子完成"的记录
2. 查看音频处理日志中的静音检测
3. 确认句子完成检测逻辑是否正常触发

### 问题3：重复显示buffer内容
**症状**：确认区域显示累积的重复内容

**排查步骤**：
1. 检查 `recognition_results.log` 中的"句子更新"记录
2. 确认缓存清理逻辑是否正常工作
3. 查看WebSocket消息的`type`是否正确区分`partial`和`final`

## 日志级别说明

- **TRACE**: 最详细的调试信息（音频数据处理细节）
- **DEBUG**: 详细的调试信息（消息处理、函数调用）
- **INFO**: 一般信息（识别结果、重要状态变化）
- **WARNING**: 警告信息（音频质量问题、格式问题）
- **ERROR**: 错误信息（异常、失败）

## 提交问题报告

如果问题仍然存在，请提供：

1. 问题的详细描述和重现步骤
2. 前端日志文件（从"下载日志"获取）
3. 相关的后端日志片段：
   - `logs/websocket_speech.log` 的会话记录
   - `logs/recognition_results.log` 的识别过程
   - `logs/error.log` 的错误信息（如果有）

## 性能监控

日志中包含以下性能指标：
- 音频处理时间（`processing_time`）
- 识别处理时间（`processing_time_ms`）
- 音频质量指标（`max_amp`, `rms_amp`）
- 会话统计信息（消息数、音频块数、结果数）

通过这些指标可以分析性能瓶颈和音频质量问题。 