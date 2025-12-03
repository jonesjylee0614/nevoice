# e-voice-admin-front 前端功能梳理

## 项目概述

e-voice-admin-front 是一个基于 Vue 3 + Vite + Arco Design 的语音服务管理前端。

## 技术栈

- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI 组件库**: Arco Design Web Vue
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **WebSocket**: 原生 WebSocket
- **路由**: Vue Router (Hash 模式)

## 功能模块

### 1. 首页 (`/home`)

- **位置**: `views/dashboard/workplace/`
- **功能**: 工作台概览页面
  - 数据统计面板
  - 快捷操作入口
  - 最近访问记录
  - 公告通知

---

### 2. 语音能力 (`/voice`)

#### 2.1 实时语音识别 (`/voice/identify`)

- **位置**: `views/voice/identify/index.vue`
- **功能**: WebSocket 实时语音识别
- **核心特性**:
  - WebSocket 连接管理（自动重连、心跳检测）
  - 麦克风录音（16kHz, PCM 格式）
  - 实时显示识别结果（partial + correction）
  - 音量可视化
  - 识别日志展示
- **使用接口**:
  - `/voice/gateway/wsRecognize` - 获取 WebSocket 地址
  - `ws://xxx:8210/ws/recognize` - WebSocket 连接

#### 2.2 在线语音识别 (`/voice/identify/online`)

- **位置**: `views/voice/identify/online.vue`
- **功能**: 上传音频文件进行识别
- **使用接口**: `/voice/gateway/voice-recognize-online`

#### 2.3 离线语音识别 (`/voice/identify/offline`)

- **位置**: `views/voice/identify/offline.vue`
- **功能**: 离线批量音频识别
- **使用接口**: `/voice/gateway/voice-recognize-offline`

#### 2.4 声纹注册 (`/voice/print`)

- **位置**: `views/voice/print/index.vue`
- **功能**: 声纹数据管理
- **子组件**:
  - `AddForm.vue` - 新增声纹表单
  - `PrintsForm.vue` - 声纹列表
  - `PrintUploadRegister.vue` - 上传音频注册声纹
  - `RealtimeForm.vue` - 实时录音注册声纹 ⭐ (使用 `/ws/recognize`)
  - `IdentifyForm.vue` - 声纹识别表单
  - `IdentifyUpload.vue` - 上传音频进行声纹识别
- **使用接口**:
  - `/voice/print/*` - 声纹 CRUD 接口
  - `ws://xxx:8210/ws/recognize` - 实时录音

#### 2.5 语料管理 (`/voice/document`)

- **位置**: `views/voice/document/index.vue`
- **功能**: 语料文档管理

---

### 3. 模型微调 (`/finetune`)

#### 3.1 微调任务管理 (`/finetune/task`)

- **位置**: `views/finetune/task/index.vue`
- **功能**: ASR 模型微调任务管理
- **子组件**:
  - `AddForm.vue` - 创建微调任务
  - `Log.vue` - 任务日志查看
  - `TestModelForm.vue` - 模型测试
  - `TestModelUpload.vue` - 上传测试音频

#### 3.2 语料管理 (`/finetune/detail`)

- **位置**: `views/finetune/detail/index.vue`
- **功能**: 微调训练语料管理
- **子组件**:
  - `AddForm.vue` - 添加语料
  - `AudioUpload.vue` - 上传音频文件

---

### 4. 会议管理 (`/meeting`) [可能未在路由中配置]

#### 4.1 离线会议处理 (`/meeting/offline`)

- **位置**: `views/meeting/offline/index.vue`
- **功能**: 离线会议音频处理
- **子组件**:
  - `AddForm.vue` - 创建会议任务
  - `AudioUpload.vue` - 上传会议音频
  - `Detail.vue` - 会议详情
  - `DetailForm.vue` - 会议内容编辑

---

### 5. 系统管理 (`/system`) [管理员功能]

#### 5.1 账户管理 (`/system/account`)

- **功能**: 用户账户 CRUD

#### 5.2 部门管理 (`/system/dept`)

- **功能**: 组织部门 CRUD

#### 5.3 角色管理 (`/system/role`)

- **功能**: 角色权限管理

#### 5.4 权限管理 (`/system/rule`)

- **功能**: 菜单权限配置

---

### 6. 数据中心 (`/datacenter`)

#### 6.1 附件管理 (`/datacenter/attachment`)

- **功能**: 文件存储管理

#### 6.2 配置管理 (`/datacenter/configuration`)

- **功能**: 系统配置（附件、邮件等）

#### 6.3 字典管理 (`/datacenter/dictionary`)

- **功能**: 数据字典管理

---

### 7. 用户中心 (`/user`)

#### 7.1 个人信息 (`/user/info`)

- **功能**: 查看个人信息、活动记录

#### 7.2 个人设置 (`/user/setting`)

- **功能**: 修改个人信息、安全设置、API 配置

---

## 实时识别相关页面

以下页面使用了 WebSocket 实时识别接口 (`/ws/recognize`)：

| 页面 | 文件路径 | 功能描述 |
|------|----------|----------|
| 实时语音识别 | `voice/identify/index.vue` | 主要的实时识别页面 |
| 声纹实时注册 | `voice/print/RealtimeForm.vue` | 声纹注册时的实时录音 |

## 消息协议

### 发送消息

```typescript
// 开始识别
{ type: 'start', hotwords?: boolean, speaker?: boolean }

// 发送音频（二进制 PCM 或 Base64）
WebSocket.send(audioData)

// 结束识别
{ type: 'end' }

// 心跳
{ type: 'ping', ts: number }
```

### 接收消息

```typescript
// 开始确认
{ type: 'started', message: string }

// 实时识别结果
{ 
  type: 'partial',
  text: string,
  text_state: {
    confirmed_text: string,
    candidate_text: string,
    revision_id: number
  },
  segment_id: string,
  revision: number
}

// 离线纠错结果
{
  type: 'correction',
  text: string,
  mode: '2pass-offline',
  text_state: { ... },
  is_final: boolean
}

// 最终结果
{
  type: 'final',
  text: string,
  index: number,
  segment_id: string
}

// 会话结束
{ type: 'session_end', message: string }

// 错误
{ type: 'error', message: string, code: number }

// 心跳响应
{ type: 'pong', ts: number }
```

## 环境配置

### 环境变量 (`.env.*`)

```bash
# API 主机地址
VITE_API_HOST=http://localhost:8108

# Python WebSocket 服务地址
VITE_API_PY_WS_HOST=ws://localhost:8210
```

## 目录结构

```
src/
├── api/                    # API 接口定义
├── assets/                 # 静态资源
├── components/             # 通用组件
│   ├── Modal/              # 模态框组件
│   └── gfeditor/           # 富文本编辑器
├── hooks/                  # 组合式函数
├── layout/                 # 布局组件
├── router/                 # 路由配置
│   └── routes/modules/     # 路由模块
├── stores/                 # Pinia 状态管理
├── utils/                  # 工具函数
│   └── http/               # HTTP 请求封装
└── views/                  # 页面组件
    ├── dashboard/          # 仪表板
    ├── voice/              # 语音功能
    ├── finetune/           # 模型微调
    ├── meeting/            # 会议管理
    ├── system/             # 系统管理
    └── user/               # 用户中心
```

