# Cursor 规则说明

## 规则文件列表

### 1. project-overview.mdc
- **应用范围**: 始终应用 (alwaysApply: true)
- **作用**: 提供项目整体结构和组件概述
- **内容**: 核心文件说明、功能模块介绍、端口配置等

### 2. development-guidelines.mdc  
- **应用范围**: 始终应用 (alwaysApply: true)
- **作用**: 开发指南和最佳实践
- **内容**: 环境要求、开发原则、常见修改场景

### 3. python-backend.mdc
- **应用范围**: Python文件 (globs: *.py)
- **作用**: Python后端开发规范
- **内容**: Flask架构、错误处理、音频处理、性能优化

### 4. frontend-testing.mdc
- **应用范围**: 测试页面文件 (globs: tests/**/*.html,tests/**/*.js,tests/**/*.css)
- **作用**: 前端测试页面开发规范
- **内容**: 模块化架构、组件使用、配置管理、响应式设计

### 5. troubleshooting.mdc
- **应用范围**: 手动应用
- **作用**: 常见问题和故障排除
- **内容**: 高频问题速查、调试技巧、环境配置检查

## 规则使用方式

### 自动应用的规则
- `project-overview.mdc` - 在任何文件中都会显示项目概述
- `development-guidelines.mdc` - 在任何时候都会显示开发指南

### 文件类型特定规则
- `python-backend.mdc` - 在编辑.py文件时自动应用
- `frontend-testing.mdc` - 在编辑tests目录下的HTML/JS/CSS文件时自动应用

### 按需使用规则  
- `troubleshooting.mdc` - 遇到问题时可通过描述"troubleshooting"或"故障排除"来调用

## 规则更新
当项目结构或开发流程发生变化时，及时更新相应的规则文件，确保开发团队获得最新的指导信息。 