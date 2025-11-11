# Win11 + WSL 环境下运行 E-Voice 与 E-Voice-Admin 指南

本文档针对 Windows 11 用户，指导如何在 WSL2 环境中同时运行 `nevoice/e-voice`（Python 实时语音识别服务）和 `nevoice/e-voice-admin`（Go 管理网关）。假设你使用的是 Ubuntu 22.04 或相近的发行版，且仓库已经在 Windows 文件系统 `D:\WorkSpace\code\2025\evoice` 下完成克隆。

---

## 1. Windows 侧准备

- **启用 WSL2 与虚拟化**：在“启用或关闭 Windows 功能”中勾选“适用于 Linux 的 Windows 子系统”“虚拟机平台”，重启后执行：
  ```powershell
  wsl --set-default-version 2
  wsl --install -d Ubuntu-22.04
  ```
- **更新 WSL 内核与系统**：
  ```powershell
  wsl --update
  wsl.exe -d Ubuntu-22.04
  sudo apt update && sudo apt upgrade -y
  ```
- **文件存放建议**：保持仓库位于 Windows 磁盘（如 `D:`）可避免跨系统同步问题，WSL 中路径通常为 `/mnt/d/WorkSpace/code/2025/evoice`。

---

## 2. WSL 共享网络要点

默认情况下，WSL2 可以使用 `localhost` 与 Windows 主机互通。本项目已有多套预设地址（见测试页面的环境下拉），常见情况：

| 名称 | 用途 | 备注 |
| --- | --- | --- |
| `http://localhost:8210` | Windows 浏览器访问 WSL 内的 e-voice | 适用于新版 WSL（2023+），推荐优先尝试 |
| `http://172.31.xx.xx:8210` | Windows 访问 WSL | 若 `localhost` 无法直连，可运行 `ip addr show eth0` 获取当前 IP |
| `http://127.0.0.1:8210` | WSL 内自测 | 供同一实例使用 |

> 建议：先在 WSL 中运行服务，随后在 Windows PowerShell 中 `curl http://localhost:8210/` 验证连通性。

---

## 3. 配置 Python 服务 `nevoice/e-voice`

### 3.1 安装必要依赖

```bash
# 进入项目目录
cd /mnt/d/WorkSpace/code/2025/evoice/nevoice/e-voice

# 推荐使用 Conda（或 Mamba）创建隔离环境
conda create -n evoice python=3.12 -y
conda activate evoice

# 系统层依赖：音频处理需 PortAudio 与 Sox
sudo apt install -y build-essential libsndfile1 libsox-dev sox portaudio19-dev

# Python 依赖
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# （可选）如需 GPU，请提前准备 CUDA/驱动并校验 torch 是否启用 GPU
python -c "import torch; print(torch.cuda.is_available())"
```

### 3.2 配置文件

- 复制示例实时配置：
  ```bash
  cp config/realtime.example.yml config/realtime.yml
  ```
- 按需调整 `config/dev.ini` 或新建 `.env`（若后端读取环境变量）。默认端口为 `8210`，若需修改，记得同步更新测试页面与前端配置。

### 3.3 启动服务

```bash
conda activate evoice
python rest.py --env dev  # 默认读取 config/dev.ini
```

- 服务启动后会监听 `0.0.0.0:8210`，日志中应看到 WebSocket `/ws/recognize` 已注册。
- Windows 浏览器访问 `http://localhost:8210/` 应返回 `success`。

### 3.4 常见问题

- 若提示 `ModuleNotFoundError: No module named 'funasr'`，请确保 requirements 安装成功，必要时执行 `pip install funasr==1.2.6 -U`。
- 若麦克风采集报错，确认浏览器权限、HTTPS 要求以及测试页面实时日志中显示的错误信息。

---

## 4. 配置 Go 服务 `nevoice/e-voice-admin`

### 4.1 安装依赖

```bash
cd /mnt/d/WorkSpace/code/2025/evoice/nevoice/e-voice-admin

# 安装 Go（若未预装，建议通过官方脚本）
sudo apt install -y golang-1.21-go
echo 'export PATH="/usr/lib/go-1.21/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 初始化依赖
go mod download

# （可选）若使用数据库，请在 WSL 中部署 MySQL 或连接外部实例
```

### 4.2 配置文件

- 默认配置位于 `resource/config.yml`，你可以复制为 `resource/config-dev.yml` 并按需修改：
  - `server.address`: 端口建议保持 `8211` 或其他不与 e-voice 冲突的值。
  - `backend.url`: 指向 Python 服务地址，例如 `http://127.0.0.1:8210`（在同一 WSL）。
  - 如需访问 Windows 路径，建议使用 `/mnt/d/...` 形式。
- 若要生成代码/静态资源，确保 `resource/config.yml` 中的 `vueobjroot` 指向前端仓库，如 `/mnt/d/WorkSpace/code/2025/evoice/nevoice/e-voice-admin-front`。

### 4.3 启动服务

```bash
go run main.go -e dev   # 使用 resource/config-dev.yml
```

- 默认监听 `0.0.0.0:8211`。Windows 浏览器访问 `http://localhost:8211/swagger/index.html` 可查看接口文档（如已开启）。

---

## 5. Windows 浏览器验证测试

1. **访问测试页面**：
   - 在 Windows 浏览器中打开 `file:///D:/WorkSpace/code/2025/evoice/nevoice/e-voice/tests/test_page.html`（或通过本地服务器托管静态文件）。
   - 在左侧导航选择 `实时纠错演示`，即可进入新增的 `realtime-correction-demo.html`。
2. **切换服务器地址**：
   - 先尝试 `本地开发 (localhost:8210)`；若失败，改用 `WSL宿主机 (172.31.xx.xx:8210)`。
3. **验证功能**：
   - 点击“检查连接”应返回在线。
   - “建立 WebSocket”后，点击“开始录音”验证实时识别 + 自动纠错效果。
   - 日志面板可下载调试记录。

---

## 6. 常见排查

| 问题 | 排查步骤 |
| --- | --- |
| 浏览器无法访问 `localhost:8210` | 在 WSL 中 `curl localhost:8210` 检查，必要时查看 `ip addr` 并在浏览器使用该 IP |
| WebSocket 立即断开 | 检查后端日志是否抛异常，确认 `funasr` 模型是否加载成功 |
| 页面麦克风无输入 | 确认浏览器麦克风权限；查看页面 RMS 标签是否大于 0.01；必要时重启浏览器 |
| Go 服务无法访问 Python 服务 | 检查 `resource/config-*.yml` 中的后端地址是否填写 WSL 内可访问的 URL，如 `http://127.0.0.1:8210` |
| 端口冲突 | 使用 `sudo lsof -i:8210` 或 `sudo lsof -i:8211` 查看占用情况，更换端口后同步修改测试页面配置 |

---

## 7. 手动体验实时识别 + 纠错（推荐流程）

为了最大化体验新增页面，建议按以下步骤手动执行一次完整测试：

1. **启动 Python 实时识别服务**
   ```bash
   # 终端 1（WSL）
   conda activate evoice
   cd /mnt/d/WorkSpace/code/2025/evoice/nevoice/e-voice
   python rest.py --env dev
   ```
   - 终端日志出现 `Starting Flask app`、`/ws/recognize` 等信息即表示启动成功。

2. **（可选）启动 Go 网关服务**
   ```bash
   # 终端 2（WSL）
   cd /mnt/d/WorkSpace/code/2025/evoice/nevoice/e-voice-admin
   go run main.go -e dev
   ```
   - 如仅测试 WebSocket 流程，可暂时跳过此步骤。

3. **在 Windows 浏览器打开测试页面**
   - 地址示例：`file:///D:/WorkSpace/code/2025/evoice/nevoice/e-voice/tests/pages/realtime-correction-demo.html`
   - 或从 `tests/test_page.html` 左侧导航进入“实时纠错演示”。

4. **设置服务器地址并检查连通性**
   - 环境下拉选择 `本地开发 (localhost:8210)`。
   - 点击“检查连接”，`服务器状态`显示“在线”表示 REST 接口可达。

5. **建立 WebSocket 会话**
   - 点击“建立 WebSocket”，观察“连接状态”变为“已连接”，并生成会话 ID。
   - 若连接失败，可查看浏览器控制台或后端日志获取错误原因。

6. **开始录音并观察界面反馈**
   - 点击“开始录音”，浏览器会请求麦克风权限（第一次需要允许）。
   - 说话时“实时候选”面板会显示蓝色文本，停顿约 1.5 秒后“最终确认”会记录整句。
   - 若触发自动纠错，“自动纠错结果”表格会添加一行原文与纠正结果。

7. **查看并保存日志**
   - 底部“事件与调试日志”区域会持续输出识别与纠错事件。
   - 可点击“下载日志”导出本次会话记录。

8. **结束会话**
   - 点击“停止录音”结束当前识别。
   - 如不再需要 WebSocket 连接，点击“断开”释放资源。

> 小贴士：若 `RMS` 指标长期 < 0.005，说明麦克风几乎没有拾音，可检查设备或增益设置；若 `WebSocket` 被立即关闭，请确认后端日志中 FunASR 模型是否加载成功。

---

## 7. 建议的启动脚本示例

可以在 WSL 中创建 `scripts/start-services.sh`（自行创建）简化启动流程：

```bash
#!/usr/bin/env bash
set -e

PROJECT_ROOT=/mnt/d/WorkSpace/code/2025/evoice

# 启动 Python 服务
conda activate evoice
cd "$PROJECT_ROOT/nevoice/e-voice"
nohup python rest.py --env dev > logs/rest.log 2>&1 &

# 启动 Go 服务
cd "$PROJECT_ROOT/nevoice/e-voice-admin"
nohup go run main.go -e dev > logs/admin.log 2>&1 &

echo "E-Voice Python 与 E-Voice-Admin Go 已后台启动"
```

> 提示：确保 `logs/` 目录存在，脚本具备执行权限 (`chmod +x scripts/start-services.sh`)。停止服务可在 WSL 中使用 `ps -ef | grep rest.py` / `kill <pid>`。

---

## 8. 复用与扩展

- 若还需启动 `nevoice/e-voice-admin-front`，可在 WSL 或 Windows Node 环境中运行 `pnpm dev`，并在前端 `.env.local` 中配置 API 地址指向 `http://localhost:8211`。
- 使用新增的 `realtime-correction-demo.html` 可以直观演示 FunASR 重构后的实时识别与自动纠错。如果后端部署在远端服务器，只需在页面环境下拉中选择或输入对应地址即可。

---

完成以上步骤后，你即可在 Windows 浏览器中体验实时语音识别 + 智能纠错功能，并通过 e-voice-admin 管理相关接口。遇到问题请结合 `tests/TROUBLESHOOTING.md` 与后端日志进行排查。

