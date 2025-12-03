# Windows 11 调试指南

本文档说明如何在 Windows 11 上调试 e-voice 实时语音识别服务。

## 环境要求

### 系统要求
- Windows 11
- Python 3.10+ (推荐 3.12)
- CUDA 11.8+ (如果使用 GPU)
- Git

### 硬件要求
- **GPU 模式**：NVIDIA 显卡 (显存 >= 6GB)
- **CPU 模式**：8核+ CPU，16GB+ 内存

## 环境准备

### 1. 安装 Python 环境

推荐使用 Anaconda 或 Miniconda：

```powershell
# 创建虚拟环境
conda create -n evoice python=3.12 -y
conda activate evoice
```

### 2. 安装依赖

```powershell
cd nevoice/e-voice
pip install -r requirements.txt
```

### 3. 安装 PyTorch (GPU 版本)

如果使用 GPU，需要安装 CUDA 版本的 PyTorch：

```powershell
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 或 CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 4. 安装 FunASR

```powershell
pip install funasr==1.2.6
```

### 5. 安装 ITN 依赖 (可选)

如果需要逆文本归一化功能：

```powershell
pip install cn2an==0.5.22

# fun_text_processing 需要从 FunASR 源码安装
cd FunASR/fun_text_processing
pip install -e .
```

## 配置说明

### 配置文件结构

```
nevoice/e-voice/config/
├── dev_wnl.ini           # 服务配置（数据库、ES等）
├── dev.ini               # 默认开发配置
├── prod.ini              # 生产配置
└── realtime_funasr.yml   # FunASR 实时识别配置
```

### realtime_funasr.yml 配置

```yaml
# 核心配置项

mode:
  default: "2pass"  # 2pass: 在线+离线纠错, online: 仅在线, offline: 仅离线

resources:
  ngpu: 1           # GPU 数量，0 表示使用 CPU
  ncpu: 4           # CPU 线程数
  device: "cuda"    # cuda 或 cpu

features:
  use_funasr_streamer: true  # 启用 FunASR 流式引擎
  enable_vad: true           # 启用语音端点检测
  enable_punc: true          # 启用标点恢复
  enable_itn: true           # 启用逆文本归一化
```

### CPU 模式配置

如果没有 GPU，修改 `realtime_funasr.yml`：

```yaml
resources:
  ngpu: 0           # 设为 0
  ncpu: 8           # 增加 CPU 线程
  device: "cpu"     # 设为 cpu
```

## 启动服务

### 1. 设置环境变量

```powershell
# 设置环境名称
$env:EVOICE_ENV = "dev_wnl"

# 或使用命令行参数
python rest.py -e wnl
```

### 2. 启动服务

```powershell
cd nevoice/e-voice
python rest.py -e wnl
```

### 3. 验证启动

服务启动后会显示：
```
开始加载 FunASR 模型...
加载 离线 ASR 模型: damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
加载 在线流式 ASR 模型: damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online
加载 VAD 模型: damo/speech_fsmn_vad_zh-cn-16k-common-pytorch
加载 标点 模型: damo/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727
FunASR 模型加载完成，耗时 xxxms
```

## 测试验证

### 1. 健康检查

```powershell
# 检查服务状态
curl http://localhost:8210/api/health

# 查看模型状态
curl http://localhost:8210/api/streaming/models
```

### 2. WebSocket 测试

使用浏览器打开测试页面：

```
file:///D:/WorkSpace/code/2025/evoice/nevoice/e-voice/tests/pages/realtime-correction-demo.html
```

或启动简易 HTTP 服务器：

```powershell
cd nevoice/e-voice/tests
python -m http.server 8000
# 访问 http://localhost:8000/pages/realtime-correction-demo.html
```

### 3. 直接 WebSocket 连接

```javascript
// 连接地址
ws://localhost:8210/ws/recognize

// 发送配置
{"type": "config", "mode": "2pass", "chunk_interval": 10}

// 发送音频（PCM 16kHz 16bit）
[binary audio data]

// 停止说话
{"type": "control", "is_speaking": false}
```

## 常见问题

### 1. 模型下载失败

模型首次运行会自动从 ModelScope 下载，如果下载失败：

```powershell
# 设置 ModelScope 镜像
$env:MODELSCOPE_CACHE = "D:/models/modelscope"

# 手动下载模型
python -c "from modelscope import snapshot_download; snapshot_download('damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch')"
```

### 2. CUDA 内存不足

如果显存不足，可以：
1. 降低批处理大小
2. 使用 CPU 模式
3. 只加载在线模型（禁用离线纠错）

```yaml
# realtime_funasr.yml
models:
  asr:
    model: ""  # 禁用离线 ASR
```

### 3. 音频格式问题

确保发送的音频是：
- 采样率：16000 Hz
- 位深：16 bit
- 声道：单声道
- 格式：PCM (无头 WAV)

### 4. WebSocket 连接失败

检查：
1. 服务是否正常启动
2. 端口 8210 是否被占用
3. 防火墙是否阻止连接

```powershell
# 检查端口占用
netstat -ano | findstr :8210
```

## 调试技巧

### 1. 启用调试日志

修改 `realtime_funasr.yml`：

```yaml
features:
  debug: true
```

### 2. 查看日志

日志文件位于 `nevoice/e-voice/logs/` 目录：
- `ws.log` - WebSocket 日志
- `recognition_results.log` - 识别结果日志

### 3. VSCode 调试配置

创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "E-Voice Debug",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/nevoice/e-voice/rest.py",
      "args": ["-e", "wnl"],
      "cwd": "${workspaceFolder}/nevoice/e-voice",
      "env": {
        "EVOICE_ENV": "dev_wnl"
      },
      "console": "integratedTerminal"
    }
  ]
}
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/streaming/config` | GET | 获取流式配置 |
| `/api/streaming/models` | GET | 获取模型状态 |
| `/ws/recognize` | WS | 实时语音识别 |
| `/ws/status` | GET | WebSocket 状态 |

## 消息协议

### 输入消息

| 类型 | 说明 |
|------|------|
| `config` | 配置参数 |
| `control` | 控制命令（如 `is_speaking: false`）|
| `ping` | 心跳 |
| binary | PCM 音频数据 |

### 输出消息

| 类型 | 说明 |
|------|------|
| `partial` | 在线流式识别中间结果 |
| `correction` | 离线二次纠错结果（带标点/ITN）|
| `pong` | 心跳响应 |
| `error` | 错误信息 |

