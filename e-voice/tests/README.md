# 测试工具目录结构

## 概述

这个目录包含了项目的API测试工具，采用模块化设计，便于维护和扩展。

## 目录结构

```
tests/
├── test_page.html          # 主测试页面（入口）
├── components/             # 共用组件
│   ├── config.js          # 配置文件
│   ├── common.js          # 共用JavaScript函数
│   └── common.css         # 共用样式
├── pages/                 # 专项测试页面
│   ├── voice-test.html    # 语音注册接口测试
│   ├── speech-recognition-test.html # 传统实时/离线识别测试
│   ├── realtime-correction-demo.html # 流式识别 + 自动纠错演示
│   └── embedding-test.html # Embedding接口测试
├── test_api.sh           # Shell脚本测试
├── test_page.html        # 原始测试页面（现已重构）
└── README.md             # 本说明文档
```

## 主要改进

### 1. 解决硬编码IP地址问题

**原问题**: 测试页面中硬编码了 `http://172.31.77.180:8210` 地址
**解决方案**:
- 默认使用 `localhost:8210` 作为开发环境
- 提供环境选择下拉菜单：
  - 本地开发 (localhost:8210)
  - 开发环境 (172.31.77.180:8210)  
  - 生产环境 (127.0.0.1:8210)
  - 自定义地址

### 2. 模块化架构

**组件分离**:
- `components/config.js`: 统一的配置管理
- `components/common.js`: 共用的JavaScript函数
- `components/common.css`: 统一的样式设计

**页面分离**:
- `test_page.html`: 主入口页面，提供导航和基础测试
- `pages/voice-test.html`: 专门的语音接口测试
- `pages/embedding-test.html`: 专门的Embedding接口测试

### 3. 功能增强

**主测试页面**:
- 添加快速导航到专项测试页面
- 环境切换功能
- 保留基础的健康检查、Embedding和语音注册测试

**语音注册页面** (`pages/voice-test.html`):
- 专门的语音注册接口测试
- 预留语音验证接口（开发中）
- 批量语音测试功能
- 拖拽上传支持

**语音识别页面** (`pages/speech-recognition-test.html`):
- 离线语音识别接口测试
- 在线语音识别接口测试
- 实时录音识别功能
- 支持多种音频格式和采样率

**实时纠错演示页面** (`pages/realtime-correction-demo.html`):
- 聚焦 FunASR 重构后的实时识别 + 智能纠错链路
- 展示候选增量、最终确认、纠错轨迹三面板
- 内建日志面板、Ping 检测与录音质量（RMS）反馈
- 适合演示新版 WebSocket `/ws/recognize` 流程

**Embedding测试页面**:
- 预设测试数据（简单、复杂、中文、医学）
- 批量测试不同数据格式
- 性能压力测试（并发请求）
- 详细的测试结果分析

## 使用方法

### 1. 快速开始
1. 打开 `test_page.html` 作为主入口
2. 选择适当的服务器环境
3. 点击"检查连接"确认服务器状态
4. 使用导航功能进入专项测试页面

### 2. 环境配置
```javascript
// 在 components/config.js 中修改服务器选项
SERVER_OPTIONS: {
    'localhost': 'http://localhost:8210',
    'development': 'http://172.31.77.180:8210',  // 开发环境
    'production': 'http://127.0.0.1:8210'  // 生产环境
}
```

### 3. 添加新的测试页面
1. 在 `pages/` 目录下创建新的HTML文件
2. 引入共用的CSS和JS文件：
   ```html
   <link rel="stylesheet" href="../components/common.css">
   <script src="../components/config.js"></script>
   <script src="../components/common.js"></script>
   ```
3. 在主页面添加导航链接

## 技术特性

- **响应式设计**: 支持移动端和桌面端
- **错误处理**: 完善的网络错误和超时处理
- **拖拽上传**: 支持文件拖拽上传
- **实时状态**: 服务器连接状态实时显示
- **批量测试**: 支持多种数据格式的批量测试
- **性能测试**: 并发请求和响应时间分析

## 未来扩展

可以继续添加以下功能模块：
- `pages/database-test.html` - 数据库接口测试
- `pages/auth-test.html` - 认证和授权测试
- `pages/websocket-test.html` - WebSocket连接测试
- `pages/performance-test.html` - 综合性能测试

每个新模块都可以复用 `components/` 中的共用组件，保持一致的UI和功能体验。 