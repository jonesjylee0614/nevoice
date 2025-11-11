-- 重置管理员密码脚本
-- 默认用户名: admin
-- 默认密码: admin123
-- Salt: e-voice-2024
-- MD5(admin123 + e-voice-2024) = 4c8f8b8c5e5c0b3d8f9a3b7c2d1e0f6a

-- 注意：请根据实际情况修改用户名
-- 如果使用其他密码，请使用以下公式计算：
-- Password = MD5(明文密码 + salt)

-- 更新管理员密码（通过用户名）
UPDATE business_account 
SET 
    password = MD5(CONCAT('admin123', 'e-voice-2024')),
    salt = 'e-voice-2024'
WHERE username = 'admin';

-- 如果需要更新所有管理员账户，可以使用以下语句：
-- UPDATE business_account 
-- SET 
--     password = MD5(CONCAT('admin123', 'e-voice-2024')),
--     salt = 'e-voice-2024'
-- WHERE id IN (SELECT uid FROM business_auth_role_access WHERE role_id = 1);

-- 验证更新结果
SELECT id, username, name, email, status 
FROM business_account 
WHERE username = 'gofly';

-- 同时也可以为 admin 用户重置密码（如果存在）
UPDATE business_account 
SET 
    password = MD5(CONCAT('admin123', 'e-voice-2024')),
    salt = 'e-voice-2024'
WHERE username = 'admin';

-- 显示所有管理员账户
SELECT id, username, name, email, status 
FROM business_account 
WHERE status = 0 
ORDER BY id 
LIMIT 10;

