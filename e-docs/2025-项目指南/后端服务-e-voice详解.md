# 后端服务 e-voice 详解

本说明聚焦 Python 语音服务的运行环境、模块划分与关键业务逻辑，便于研发、运维快速掌握实现细节。

## 1. 服务概述

- **职责**：提供语音识别（离线/在线/实时）、声纹注册与比对、离线会议拆分、监控告警等能力，是整套系统的 AI 与数据核心。【F:e-voice/server/app.py†L28-L54】【F:e-voice/server/routes/voice.py†L29-L162】【F:e-voice/rest_meeting.py†L55-L126】
- **运行方式**：Flask + Flask-SocketIO + Flask-Sock，默认 8210 端口，支持 HTTP、WebSocket 双协议，同时可选开启系统监控线程。【F:e-voice/rest.py†L1-L25】【F:e-voice/server/monitoring.py†L32-L45】

## 2. 运行环境与安装

1. 选择配置文件：通过环境变量 `EVOICE_ENV` 读取 `config/{env}.ini`，默认 `dev`。【F:e-voice/config/config.py†L6-L10】
2. 安装依赖：`pip install -r requirements.txt`，包含 ModelScope、FunASR、Torch、Elasticsearch 客户端等关键包。【F:e-voice/requirements.txt†L1-L31】
3. 启动服务：执行 `python rest.py`，在控制台可看到端口、健康检查地址与 API 提示。【F:e-voice/rest.py†L13-L24】
4. 可选功能：
   - 若 GPU 可用，Torch/ModelScope 将自动调用；否则 `recognize.py` 会退化为模拟输出以保证流程不中断。【F:e-voice/speech_recognition/recognize.py†L37-L117】
   - 若 `monitoring/system_monitor.py` 依赖满足，`optional_start_monitoring()` 将启动监控线程输出系统指标。【F:e-voice/server/monitoring.py†L32-L45】【F:e-voice/monitoring/system_monitor.py†L15-L200】

## 3. 配置说明

| 配置段 | 作用 | 备注 |
| --- | --- | --- |
| `[db]` | 关系型数据库地址，供会议明细等结构化数据写入。 | 通过 `db/db.py` 建立持久连接，默认使用 PyMySQL。【F:e-voice/config/dev.ini†L1-L7】【F:e-voice/db/db.py†L1-L26】 |
| `[es]` | Elasticsearch 地址与认证，用于声纹向量存储、相似度检索。 | 通过 `es/conn.py` 创建客户端实例。【F:e-voice/config/dev.ini†L9-L12】【F:e-voice/es/conn.py†L1-L38】 |
| `[voice]` | 声纹音频临时/持久化路径等参数。 | 由 `audio_utils.resolve_temp_dir()` 读取并确保目录存在。【F:e-voice/config/dev.ini†L17-L18】【F:e-voice/server/audio_utils.py†L18-L47】 |
| `[meeting]` | 离线会议音频输出目录。 | 供会议拆分逻辑保存子音频文件。【F:e-voice/config/dev.ini†L14-L15】【F:e-voice/biz/meeting/parse_offline_meeting.py†L39-L58】 |

## 4. 目录结构与职责

- `server/`：
  - `app.py`：应用工厂，注册 Flask 蓝图（基础、语音、日志、热词、状态等）及 Socket.IO/WS 事件，初始化日志和音频工具。【F:e-voice/server/app.py†L28-L54】
  - `routes/`：封装 REST/WS 路由，重点关注 `voice.py`、`ws.py`、`hotwords.py`、`status.py` 等。【F:e-voice/server/routes/voice.py†L29-L162】【F:e-voice/server/routes/ws.py†L18-L200】
  - `session.py`：实时识别会话管理，负责音频缓冲、句子确认、原始音频保存、重复去除等复杂逻辑。【F:e-voice/server/session.py†L1-L400】
  - `audio_utils.py`：音频读写、格式转换、JSON 编码工具。【F:e-voice/server/audio_utils.py†L1-L83】
  - `logging.py`：配置 loguru 多路日志（ws、音频、识别、关键事件、错误）。【F:e-voice/server/logging.py†L8-L87】
- `speech_recognition/`：
  - `recognize.py`：主识别函数，调用 ModelScope 自动语音识别模型，并在失败时提供模拟结果保障流程。【F:e-voice/speech_recognition/recognize.py†L12-L117】
  - `speech_recognition.py`：FunASR 流式模型封装，可按需接入实时识别。【F:e-voice/speech_recognition/speech_recognition.py†L1-L25】
  - `spk.py`：FunASR 分角色识别模型，产出说话人分段信息。【F:e-voice/speech_recognition/spk.py†L3-L26】
  - `vocabulary_manager.py`：智能词表加载、内存策略与统计。 | 【F:e-voice/speech_recognition/vocabulary_manager.py†L1-L120】
- `pipeline/`：ModelScope 说话人验证管线，提供单条或批量嵌入接口，供声纹注册与会议模块使用。【F:e-voice/pipeline/spk_v_pipeline.py†L1-L19】
- `rest_prints.py` / `rest_meeting.py`：声纹管理、会议任务 REST 接口，实现音频读取、临时保存与异步调度。【F:e-voice/rest_prints.py†L33-L129】【F:e-voice/rest_meeting.py†L55-L126】
- `biz/meeting`：离线会议解析逻辑，负责调用说话人识别、切分音频、写入数据库及声纹匹配。【F:e-voice/biz/meeting/parse_offline_meeting.py†L18-L114】
- `es/`：Elasticsearch 封装，定义 Dense Vector 索引与 CRUD 操作。【F:e-voice/es/voice.py†L1-L200】
- `db/`：数据库连接与 DAO（如 `meeting_offline_detail`）。【F:e-voice/db/domain/meeting_offline_detail.py†L1-L29】
- `monitoring/`：系统指标采集与健康检查线程。【F:e-voice/monitoring/system_monitor.py†L15-L200】
- `tests/`：API/WS 验证脚本与前端页面，用于自测部署结果。【F:e-voice/tests/README.md†L1-L64】

## 5. API 与功能说明

### 5.1 声纹相关接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/prints/get_user_prints` | POST | 根据用户 ID 分页获取声纹记录，返回 ES 中的存储信息。 |【F:e-voice/rest_prints.py†L33-L52】|
| `/prints/del` | POST | 删除指定声纹索引文档。 |【F:e-voice/rest_prints.py†L55-L67】|
| `/prints/identify` | POST | 上传音频进行声纹比对，返回最相似用户列表与文本纠错结果。 |【F:e-voice/rest_prints.py†L70-L124】|
| `/voice-register` | POST | 声纹注册：保存音频、调用识别、写入 ES。 |【F:e-voice/server/routes/voice.py†L29-L74】|

### 5.2 语音识别接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/voice-recognize-offline` | POST | 上传音频文件离线识别，返回文本、时长、采样率等信息。 |【F:e-voice/server/routes/voice.py†L81-L118】|
| `/voice-recognize-online` | POST | 传入 Base64 音频数据进行即时识别，支持格式字段。 |【F:e-voice/server/routes/voice.py†L120-L158】|
| `/ws/recognize` | WS | WebSocket 流式识别，支持 start/chunk/end/ping/reset 指令、部分 & 最终结果推送。 |【F:e-voice/server/routes/ws.py†L18-L200】|

### 5.3 会议纪要接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/meeting/offline` | POST | 上传离线会议音频，触发异步拆分任务并返回任务 ID/文件名。 |【F:e-voice/rest_meeting.py†L55-L120】|

### 5.4 调试与监控接口

| 接口 | 说明 |
| --- | --- |
| `/logs/*` | 查看不同类别的日志文件（WebSocket、音频、识别、关键事件）。【F:e-voice/server/routes/logs.py†L13-L57】 |
| `/voice/debug/sessions/*` | 列举或下载调试音频片段、统计文件。 |【F:e-voice/server/routes/debug.py†L13-L77】 |
| `/ws/status` | 返回实时会话统计信息（连接数、累计帧数、上次文本等）。 |【F:e-voice/server/routes/status.py†L13-L31】 |

## 6. 核心业务逻辑

### 6.1 语音识别 pipeline

1. `recognize.py` 初始化 ModelScope Pipeline，捕获异常并切换到模拟结果，确保服务稳定。【F:e-voice/speech_recognition/recognize.py†L12-L117】
2. 识别结果使用 `extract_text_from_result` 统一提取文本、限制长度，并写入日志文件供回溯。【F:e-voice/server/audio_utils.py†L49-L78】【F:e-voice/server/logging.py†L55-L76】
3. WebSocket 场景下，`RealtimeSpeechSession` 会按帧追加音频、检测静音、执行去重与标点预测，并在会话结束时落盘原始 PCM/WAV 以备排查。【F:e-voice/server/session.py†L180-L400】

### 6.2 声纹注册与检索

1. `/voice-register` 处理上传的音频：
   - 调用 `process_audio_file` 做格式兼容与采样率统一；
   - 保存原始 WAV 至 `voice.print_wav_path` 目录；
   - 调用 `recognize` 得到文本摘要，并限制长度；
   - 调用 `pipeline.spk_v_pipeline.embedding` 生成 192 维向量；
   - 调用 `es.voice.insert_voice` 写入 ES Dense Vector 索引。【F:e-voice/server/routes/voice.py†L29-L74】【F:e-voice/es/voice.py†L33-L52】
2. `/prints/identify`：临时保存音频 -> 生成向量 -> `search_voice_vector` 检索最相近文档 -> 语音转文字并通过 `zh_correct.correct` 纠错。【F:e-voice/rest_prints.py†L70-L122】

### 6.3 离线会议拆分

1. `/meeting/offline` 保存上传的音频文件（自动补齐格式）并交由线程池异步处理。【F:e-voice/rest_meeting.py†L55-L120】
2. `process_audio_task` 使用 FunASR `spk_pipeline.generate` 获得带说话人信息的句子列表，切割音频片段，限制每个说话人最多 5 个样本，用于声纹匹配。【F:e-voice/biz/meeting/parse_offline_meeting.py†L34-L68】
3. 对每个说话人使用 `pipeline.embeddings` 批量生成向量，通过 ES `multi_search_voice_vector` 找到最接近的用户 ID，并写入 `meeting_offline_detail` 表。【F:e-voice/biz/meeting/parse_offline_meeting.py†L70-L114】【F:e-voice/es/voice.py†L156-L198】

### 6.4 监控与日志

- `SystemMonitor` 采集 CPU、内存、磁盘、GPU 显存及识别成功率、延迟等指标，可设置阈值触发告警日志。【F:e-voice/monitoring/system_monitor.py†L15-L200】
- 日志路径位于 `logs/`，包括 `websocket_speech.log`、`audio_processing.log`、`recognition_results.log`、`realtime_key.log` 等，便于按组件排查。【F:e-voice/server/logging.py†L33-L87】

## 7. 调试与测试

- **健康检查**：服务启动后访问 `http://<host>:8210/`，若返回 `success` 说明 Flask 路由已就绪。【F:e-voice/server/routes/basic.py†L10-L22】
- **集成测试**：`tests/` 下的 HTML 页面可直接通过浏览器进行 REST/WS 测试，Shell 脚本 `test_api.sh` 则可批量验证 API。【F:e-voice/tests/README.md†L1-L64】
- **日志分析**：可通过 `/logs/*` 接口或直接读取 `logs/` 文件定位问题。必要时开启 `monitoring.system_monitor` 查看性能数据。【F:e-voice/server/routes/logs.py†L13-L57】【F:e-voice/server/monitoring.py†L32-L45】

## 8. 运维建议

- **资源监控**：关注 GPU 显存与 CPU 利用率，`SystemMonitor` 默认 30 秒采样一次，可根据阈值调整告警策略。【F:e-voice/monitoring/system_monitor.py†L38-L126】
- **模型缓存**：ModelScope/FunASR 首次下载模型体积较大，可提前在部署环境预热并配置合适的缓存目录。
- **音频存储**：声纹注册与会议拆分都会在磁盘保存 WAV 文件，需要定期归档/清理，以免磁盘占满。目录由 `[voice]`、`[meeting]` 配置控制。【F:e-voice/server/routes/voice.py†L46-L53】【F:e-voice/biz/meeting/parse_offline_meeting.py†L39-L58】

## 9. 常见问题

| 问题 | 排查要点 |
| --- | --- |
| ModelScope 加载失败 | 查看 `logs/error.log` 与识别日志是否出现 `ModelScope初始化失败`，确认网络与 GPU 资源；必要时使用 FunASR 备选或本地离线模型。【F:e-voice/speech_recognition/recognize.py†L12-L117】 |
| WebSocket 识别卡顿 | 检查前端是否按帧发送、服务器是否及时执行 `session.reset()`、`check_sentence_complete()`；关注 `websocket_speech.log` 中的调试信息。【F:e-voice/server/routes/ws.py†L18-L200】【F:e-voice/server/logging.py†L33-L55】 |
| 会议任务失败 | `parse_offline_meeting` 会捕获并打印堆栈，可通过 `logger.error` 输出定位；同时检查 ES 与数据库连接是否正常。【F:e-voice/biz/meeting/parse_offline_meeting.py†L18-L104】 |
| 声纹检索结果为空 | 确认 ES 索引已创建且包含 Dense Vector 字段；必要时调用 `create_index` 重新生成或核对向量维度（192）。【F:e-voice/es/voice.py†L8-L44】 |

## 10. 相关文档

- 《总体架构与说明》：了解整个项目的组件协同、流程图与部署概览。
- 《网关服务 e-voice-admin 详解》《管理前端 e-voice-admin-front 详解》：掌握网关、前端的对接细节与配置方式。
- 《文档规范》：统一后续文档的结构、命名及存放路径。

