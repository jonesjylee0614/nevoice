# 管理员密码重置指南

## 数据库中没有管理员账户？

如果 `business_account` 表为空，请先创建管理员账户：

```bash
# 创建默认管理员账户
mysql -h 192.168.1.4 -u root -p evoice < dev_tools/create_admin_user.sql
```

这将创建一个默认管理员：
- 用户名: `admin`
- 密码: `admin123`

## 快速重置（已有管理员账户时）

### 方法 1: 使用 SQL 脚本（推荐）

1. 连接到数据库：
```bash
mysql -h 192.168.1.4 -u root -p evoice
```

2. 执行重置脚本：
```bash
mysql -h 192.168.1.4 -u root -p evoice < dev_tools/reset_admin_password.sql
```

3. 使用新密码登录：
   - 用户名: `gofly` 或 `admin`
   - 密码: `admin123`

### 方法 2: 手动执行 SQL

连接数据库后执行：

```sql
UPDATE business_account 
SET 
    password = MD5(CONCAT('admin123', 'e-voice-2024')),
    salt = 'e-voice-2024'
WHERE username = 'admin';
```

## 自定义密码

如果需要设置其他密码，请按以下步骤：

1. 选择一个密码（例如：`MyPassword123`）
2. 选择一个 salt（例如：`my-custom-salt`）
3. 使用 MySQL 函数计算密码哈希：

```sql
UPDATE business_account 
SET 
    password = MD5(CONCAT('你的密码', '你的salt')),
    salt = '你的salt'
WHERE username = 'admin';
```

## 密码加密说明

系统使用以下方式加密密码：
- 加密算法：MD5
- 加密公式：`MD5(明文密码 + salt)`
- Salt 存储在 `business_account.salt` 字段

## 安全建议

1. 重置密码后立即登录并修改为强密码
2. 定期更换管理员密码
3. 不要在生产环境使用默认密码
4. 及时删除本文件和 SQL 脚本以防止信息泄露

## 常见问题

### Q: 不知道管理员用户名？
A: 执行以下 SQL 查询所有管理员账户：
```sql
SELECT id, username, name, email FROM business_account WHERE status = 0 LIMIT 10;
```

### Q: 密码重置后仍无法登录？
A: 检查以下几点：
1. 确认用户状态 `status = 0`（正常）
2. 确认用户有角色权限
3. 检查前端是否已禁用验证码（参考前端修改）
4. 清除浏览器缓存后重试

### Q: 如何恢复原密码？
A: 无法恢复原密码（单向加密），只能重置为新密码。

## 相关修改

本次还进行了以下修改：
1. **前端**：移除了登录页面的拖动验证码组件（`login-form.vue`）
2. **后端**：跳过了验证码和加密检查（`internal/app/user/index.go`）

这些修改简化了登录流程，建议在生产环境中恢复验证码功能以提高安全性。

