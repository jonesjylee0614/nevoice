-- 重置 gofly 管理员密码
-- 新密码: admin123

UPDATE business_account 
SET 
    password = MD5(CONCAT('admin123', 'e-voice-2024')),
    salt = 'e-voice-2024'
WHERE username = 'gofly';

-- 验证更新结果
SELECT 
    id, 
    username, 
    name, 
    email, 
    status,
    '新密码为: admin123' as note 
FROM business_account 
WHERE username = 'gofly';


