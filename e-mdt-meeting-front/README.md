# MDT 会议纪要系统

> 多学科团队（MDT）会议智能记录与总结系统前端项目

## 📋 项目简介

MDT会议纪要系统是一个专为医疗机构设计的多学科会议管理平台，支持会议创建、实时语音识别、智能总结生成等功能。

## 🛠 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.5.x | 前端框架 |
| TypeScript | 5.7.x | 类型安全 |
| Vite | 6.0.x | 构建工具 |
| Vant | 4.9.x | UI 组件库 |
| Pinia | 2.3.x | 状态管理 |
| Vue Router | 4.5.x | 路由管理 |
| Axios | 1.7.x | HTTP 请求 |
| Sass | 1.86.x | CSS 预处理器 |

## 📁 项目结构

```
e-mdt-meeting-front/
├── public/                     # 静态资源
├── src/
│   ├── api/                    # API 接口
│   │   ├── auth.ts             # 认证相关接口
│   │   ├── meeting.ts          # 会议相关接口
│   │   └── types.ts            # 类型定义
│   ├── assets/
│   │   └── main.scss           # 全局样式
│   ├── router/
│   │   └── index.ts            # 路由配置
│   ├── service/
│   │   └── request.ts          # Axios 封装
│   ├── stores/
│   │   ├── meeting.ts          # 会议状态
│   │   └── user.ts             # 用户状态
│   ├── views/
│   │   ├── Login.vue           # 登录页
│   │   ├── MeetingList.vue     # 会议列表
│   │   ├── NewMeeting.vue      # 新建会议
│   │   └── MeetingDetail.vue   # 会议详情
│   ├── App.vue                 # 根组件
│   └── main.ts                 # 入口文件
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 🚀 快速开始

### 环境要求

- Node.js >= 18.x
- pnpm >= 8.x（推荐）

### 安装依赖

```bash
cd nevoice/e-mdt-meeting-front
pnpm install
```

### 开发运行

```bash
pnpm dev
```

访问 http://localhost:9598

### 生产构建

```bash
pnpm build
```

### 代码检查

```bash
pnpm lint
```

## 📱 功能模块

### 1. 用户认证

- **登录页面** (`/login`)
  - 用户名密码登录
  - 记住账号功能
  - 登录状态持久化（localStorage）

- **路由守卫**
  - 未登录自动跳转登录页
  - Token 过期自动处理

### 2. 会议列表

- **统计概览**
  - 全部会议数量
  - 进行中会议数
  - 已完成会议数
  - 已生成总结数

- **搜索功能**
  - 支持标题关键词搜索
  - 一键刷新数据

- **会议卡片**
  - 会议标题和状态
  - 时间信息
  - 对话数量
  - 标签显示
  - 快捷操作（查看/删除）

- **分页**
  - 支持上下页切换
  - 显示总记录数

### 3. 新建会议

- **基本信息**
  - 会议标题（选填，自动生成）
  - 开始时间
  - 结束时间（选填）

- **详细信息**
  - 会议说明
  - 会议标签（最多5个）
  - 快速标签选择

### 4. 会议详情

- **会议信息**
  - 会议状态（待开始/进行中/已结束）
  - 主持人
  - 会议时间
  - 对话数量
  - 总结状态

- **录音控制**
  - 开始/暂停/停止录音
  - 实时识别预览

- **对话记录**
  - 时间线展示
  - 发言人识别
  - 文本编辑
  - 音频回放

- **AI总结**
  - 一键生成总结
  - 总结复制功能

## 🎨 设计规范

### 颜色系统

```scss
// 主色调
--primary: #6366f1;           // 主色
--primary-dark: #4f46e5;      // 深色
--primary-light: rgba(99, 102, 241, 0.1);  // 浅色背景

// 语义色
--success: #10b981;           // 成功
--warning: #f59e0b;           // 警告
--danger: #ef4444;            // 危险
--info: #0ea5e9;              // 信息

// 文字颜色
--text-main: #1e293b;         // 主文字
--text-secondary: #64748b;    // 次要文字
--text-tertiary: #94a3b8;     // 辅助文字

// 背景色
--surface: #ffffff;           // 卡片背景
--surface-muted: #f8fafc;     // 浅灰背景
--surface-hover: #f1f5f9;     // 悬浮背景

// 边框
--border: #e2e8f0;
--border-light: #f1f5f9;
```

### 圆角规范

- 小型元素：8px - 10px
- 中型元素：12px - 14px
- 大型卡片：18px - 24px
- 按钮/标签：10px - 14px

### 阴影系统

```scss
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
--shadow-primary: 0 8px 24px -8px rgba(99, 102, 241, 0.5);
```

## 🔌 API 接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/admin/user/login` | 用户登录 |
| GET | `/admin/user/get_userinfo` | 获取用户信息 |
| POST | `/admin/user/logout` | 退出登录 |

### 会议接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/meeting/mdt/get_list` | 获取会议列表 |
| GET | `/meeting/mdt/get_detail` | 获取会议详情 |
| POST | `/meeting/mdt/save` | 创建会议 |
| POST | `/meeting/mdt/update` | 更新会议 |
| DELETE | `/meeting/mdt/del` | 删除会议 |
| POST | `/meeting/mdt/startMeeting` | 开始会议 |
| POST | `/meeting/mdt/endMeeting` | 结束会议 |
| POST | `/meeting/mdt/generateSummary` | 生成AI总结 |
| POST | `/meeting/mdt/assignSpeaker` | 指定发言人 |

## ⚙️ 配置说明

### 环境变量

在项目根目录创建 `.env.local` 文件：

```env
# API 服务地址（生产环境）
VITE_SERVER_URL=https://your-api-server.com

# 基础路径
VITE_BASE_URL=/
```

### 代理配置

开发环境下，API 请求会代理到 `http://localhost:8108`：

```typescript
// vite.config.ts
server: {
  port: 9598,
  proxy: {
    '/api': {
      target: 'http://localhost:8108',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## 📝 更新日志

### v1.0.0 (2024-12-09)

- ✨ 新增登录功能
- 🎨 重新设计页面布局（去除侧边栏）
- 📝 会议列表改为卡片式展示
- 🔧 修复按钮无法点击问题
- 🎨 统一配色和设计规范
- 📱 支持响应式布局

## 📄 许可证

本项目仅供内部使用。
