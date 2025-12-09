# Nevoice 语音识别系统

## 项目概述

E-Voice 是一个多服务语音识别和声纹识别系统，包含以下主要组件：

### 1. e-voice (Python 后端)
Flask-based 语音识别服务，集成 FunASR 和 ModelScope 模型。
- **端口**: 8210
- **入口**: `nevoice/e-voice/rest.py`

### 2. e-voice-admin (Go 网关)
Gin-based API 网关和业务管理后端。
- **端口**: 8108
- **入口**: `nevoice/e-voice-admin/main.go`

### 3. e-voice-admin-front (Vue 前端)
管理界面，用于声纹和会议管理。
- **入口**: `nevoice/e-voice-admin-front/src/main.ts`

### 4. e-mdt-meeting-front (MDT 会议前端)
MDT 会议纪要系统前端。
- **端口**: 9598 (可能动态变化)
- **入口**: `nevoice/e-mdt-meeting-front/src/main.ts`

---

## 本地开发配置

### ⚠️ 重要：本地开发使用的配置文件

| 服务 | 配置文件 |
|------|---------|
| **e-voice-admin (Go 网关)** | `resource/config-dev-wnl-home.yml` |
| **e-voice (Python 后端)** | `config/dev_wnl.ini` |

---

## 启动命令

### Python 后端 (e-voice)
```bash
cd nevoice/e-voice
set EVOICE_ENV=dev
python rest.py
```

### Go 网关 (e-voice-admin)
```bash
cd nevoice/e-voice-admin
go run main.go -c ./resource/config-dev-wnl-home.yml
```

### MDT 会议前端 (e-mdt-meeting-front)
```bash
cd nevoice/e-mdt-meeting-front
pnpm install
pnpm run dev
```

---

## 测试账号

| 系统 | 用户名 | 密码 |
|------|--------|------|
| MDT 会议系统 | gofly | admin123 |

---

## 数据库配置

Go 网关使用 MySQL 数据库：
- **主机**: 192.168.1.4
- **端口**: 3306
- **数据库**: evoice
- **用户名**: root

---

## 注意事项

1. 启动 Go 网关前，请确保 MySQL 和 Redis 服务已运行
2. MDT 会议前端的端口可能会因为端口占用而自动变化（如 9598 → 9600）
3. 前端 Vite proxy 会将 `/api` 请求代理到 Go 网关 8108 端口

