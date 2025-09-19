# 管理前端 e-voice-admin-front 详解

本说明聚焦 Vue3 管理端的技术栈、目录结构与关键页面流程，帮助读者快速理解声纹管理、实时识别与会议纪要等能力的前端实现及与后端的对接方式。

## 1. 工程概览

- **定位**：面向运营与业务人员的管理后台，提供声纹注册、实时语音识别、会议纪要、系统配置等 UI。依赖 Go 网关提供统一 API。 【F:e-voice-admin-front/src/views/voice/print/index.vue†L1-L189】
- **开发工具链**：Vite + Vue3 + TypeScript，配合 Arco Design 组件库与自定义 HTTP/权限工具。开发服务器默认监听 9106，并通过代理转发到 8108 网关。 【F:e-voice-admin-front/vite.config.ts†L12-L90】
- **运行要求**：Node.js ≥ 14（`package.json` 指定），推荐使用 `pnpm` 管理依赖。 【F:e-voice-admin-front/package.json†L1-L38】【F:e-voice-admin-front/README.md†L4-L18】

## 2. 技术栈与核心依赖

| 分类 | 说明 |
| --- | --- |
| 框架 | Vue 3、Vue Router、Pinia 状态管理。 【F:e-voice-admin-front/package.json†L20-L51】 |
| UI/交互 | Arco Design、Iconify、ECharts、CodeMirror 等，用于组件库、图表与编辑能力。 【F:e-voice-admin-front/package.json†L20-L68】 |
| 网络 | Axios 封装（`VAxios`），全局请求/响应拦截、重试、权限校验与错误提示。 【F:e-voice-admin-front/src/utils/http/index.ts†L1-L200】 |
| 国际化与工具 | Vue I18n、Lodash、Day.js、MD5 等。 【F:e-voice-admin-front/package.json†L20-L68】 |
| 构建插件 | `@vitejs/plugin-vue`、`vite-plugin-progress`、Code Inspector、SVG Loader、Arco Resolver 等。 【F:e-voice-admin-front/vite.config.ts†L12-L29】 |

## 3. 环境与配置

| 文件 | 作用 | 关键字段 |
| --- | --- | --- |
| `.env.development` | 开发环境变量，设置 API 代理前缀与 Python WebSocket 目标。| `VITE_API_HOST=/api`、`VITE_API_PY_WS_HOST`（默认 `ws://localhost:5000`，需与 Python 服务一致）。【F:e-voice-admin-front/.env.development†L1-L4】 |
| `vite.config.ts` | Vite 配置：端口、代理、路径别名、生产构建策略。| 开发端口 9106、`/api`/`/resource` 代理至 8108、别名 `@` 指向 `src`。 【F:e-voice-admin-front/vite.config.ts†L12-L131】 |
| `src/utils/http/index.ts` | 全局 HTTP 封装：自动拼接 API Host、附加 token/签名头、统一错误提示与重试策略。| `apiHost`、`requestInterceptors`、`responseInterceptorsCatch`。 【F:e-voice-admin-front/src/utils/http/index.ts†L20-L192】 |
| `README.md` | 快速启动说明，建议使用 `pnpm` 安装并运行 `pnpm run dev`/`pnpm run build`。| 【F:e-voice-admin-front/README.md†L4-L37】 |

> **确认实际调用的语音模型**：前端实时识别直接连到 `.env` 中的 `VITE_API_PY_WS_HOST`；该地址需与 Go 网关配置的 `py_voice.host` 指向同一 Python 实例。通过比对前端/后端配置与 Python 服务日志即可判断当前使用的模型版本。

## 4. 目录结构与职责

| 路径 | 说明 |
| --- | --- |
| `src/views/voice/print/` | 声纹管理模块：用户列表页面（`index.vue`）、声纹注册/管理表单、实时识别弹窗。 【F:e-voice-admin-front/src/views/voice/print/index.vue†L1-L205】【F:e-voice-admin-front/src/views/voice/print/RealtimeForm.vue†L1-L179】 |
| `src/views/meeting/offline/` | 会议纪要模块：列表、详情弹窗、音频上传组件与 API 封装。 【F:e-voice-admin-front/src/views/meeting/offline/AudioUpload.vue†L1-L119】【F:e-voice-admin-front/src/views/meeting/offline/api/index.ts†L1-L37】 |
| `src/utils/http/` | Axios 扩展、错误码处理、重试机制、签名头设置，统一所有请求行为。 【F:e-voice-admin-front/src/utils/http/index.ts†L1-L200】 |
| `src/router/` | 动态菜单、守卫、权限控制，与后端返回的菜单/权限体系联动。 |
| `src/store/modules/` | 用户信息、权限、布局偏好等 Pinia Store。 |
| `src/components/` | 通用组件（Modal、Upload、Captcha、Menu 等），与业务页面组合使用。 |
| `src/config/settings.json` | UI 主题与全局设置，Vite 构建时用于动态主题色。 |

## 5. 核心页面与流程

### 5.1 声纹管理页面

- 顶部操作区支持查询、重置、新建、声纹鉴定、实时识别入口。分页表格展示用户信息及快捷操作。 【F:e-voice-admin-front/src/views/voice/print/index.vue†L5-L75】
- 点击“声纹管理”打开 `PrintsForm`，上传音频后通过 `defHttp` 调用 Go 网关 API 与 Python 服务。数据更新后自动刷新列表。 【F:e-voice-admin-front/src/views/voice/print/index.vue†L70-L190】
- 权限码集中在 `perms` 变量，便于与后端的权限系统对应。 【F:e-voice-admin-front/src/views/voice/print/index.vue†L95-L100】

### 5.2 实时语音识别弹窗

- `RealtimeForm` 使用 `RecorderManager` 采集麦克风并按 1280 帧推送，连接地址来自 `VITE_API_PY_WS_HOST`。 【F:e-voice-admin-front/src/views/voice/print/RealtimeForm.vue†L53-L118】
- 支持 `start`/`end` 指令、partial/final 文本渲染与错误提示，适配 Python WebSocket 协议。 【F:e-voice-admin-front/src/views/voice/print/RealtimeForm.vue†L120-L168】
- 会话结束后保留最终文本，便于用户复制或校对。 【F:e-voice-admin-front/src/views/voice/print/RealtimeForm.vue†L160-L168】

### 5.3 会议纪要管理

- `AudioUpload` 组件限制常见音频格式，并在参数变化时回显已有录音。上传时手动调用 `useUploadApi`，将会议 ID、时间等一并提交。 【F:e-voice-admin-front/src/views/meeting/offline/AudioUpload.vue†L1-L119】
- `api/index.ts` 定义 CRUD、详情、训练开关等接口，与 Go 网关后端保持一致的路径规范。 【F:e-voice-admin-front/src/views/meeting/offline/api/index.ts†L1-L37】
- 列表页通过 `getList` 将时间范围拼接为 `createdTime` 参数，后端按时间段查询。 【F:e-voice-admin-front/src/views/meeting/offline/api/index.ts†L13-L18】

### 5.4 HTTP 拦截与错误处理

- 所有请求使用 `defHttp` 包装：自动附加 token、时间戳签名、成功/失败提示，GET 请求默认增加时间戳避免缓存。 【F:e-voice-admin-front/src/utils/http/index.ts†L20-L139】
- `responseInterceptorsCatch` 对超时、网络错误等提供统一提示，并支持 GET 请求自动重试。 【F:e-voice-admin-front/src/utils/http/index.ts†L159-L192】

## 6. 构建与部署

1. **安装依赖**：`pnpm install`（推荐）或 `npm install`。 【F:e-voice-admin-front/README.md†L4-L13】
2. **开发模式**：`pnpm run dev`，默认通过代理访问 `http://localhost:8108`。可在 `.env.development` 中调整 API 与 WS 地址。 【F:e-voice-admin-front/README.md†L11-L18】【F:e-voice-admin-front/.env.development†L1-L4】
3. **打包发布**：`pnpm run build` 输出生产包，若部署在二级目录需要同步修改 Vite `base` 与路由 `createWebHashHistory` 的前缀（README 已给出说明）。 【F:e-voice-admin-front/README.md†L16-L35】【F:e-voice-admin-front/vite.config.ts†L12-L131】
4. **代码检查**：`pnpm run lint`、`pnpm run type:check` 分别执行 ESLint 与 TS 类型检查，确保提交前质量。 【F:e-voice-admin-front/package.json†L10-L18】

## 7. 观测与安全

- **请求签名**：所有请求头附带 `verify-time` 与 `verify-encrypt`（MD5）字段，与 Go 网关联合防止重放攻击。 【F:e-voice-admin-front/src/utils/http/index.ts†L137-L150】
- **权限控制**：通过 Pinia 存储 token，`transformResponseHook` 在成功时刷新 token 并触发自动登出逻辑。 【F:e-voice-admin-front/src/utils/http/index.ts†L47-L84】
- **错误提示**：统一在 Modal/Message 中反馈错误文案，便于排查。 【F:e-voice-admin-front/src/utils/http/index.ts†L52-L84】

## 8. 常见问题与排查

1. **实时识别无响应**：确认 `.env` 中 `VITE_API_PY_WS_HOST` 与 Go 配置一致，并检查浏览器是否允许麦克风权限。 【F:e-voice-admin-front/.env.development†L1-L4】【F:e-voice-admin-front/src/views/voice/print/RealtimeForm.vue†L53-L168】
2. **请求报错 401 或签名失败**：确保浏览器时间与服务器一致，并确认 token 未过期（拦截器会自动登出）。 【F:e-voice-admin-front/src/utils/http/index.ts†L52-L150】
3. **会议上传失败或文件无法预览**：检查上传格式是否在 `acceptAudios` 列表中，或确认返回的 `audioPath` 是否正确映射到静态目录。 【F:e-voice-admin-front/src/views/meeting/offline/AudioUpload.vue†L28-L66】【F:e-voice-admin-front/src/views/meeting/offline/AudioUpload.vue†L69-L118】
4. **构建后资源路径异常**：生产部署在二级目录时需同步调整 `vite.config` 的 `base` 与路由历史模式，详见 README 提示。 【F:e-voice-admin-front/README.md†L29-L35】【F:e-voice-admin-front/vite.config.ts†L12-L131】

---

通过以上内容可快速掌握管理前端的模块划分、配置与运行方式，并与 Go 网关及 Python 语音服务协同定位问题。
