-- 创建默认管理员账户
-- 用户名: admin
-- 密码: admin123
-- Salt: e-voice-2024

-- 首先检查是否已存在 admin 用户
SELECT id, username, name FROM business_account WHERE username = 'admin';

-- 如果不存在，插入新的管理员账户
-- 注意：需要根据实际情况调整 dept_id 和其他字段
INSERT INTO business_account (
    uid,
    dept_id,
    username,
    password,
    salt,
    name,
    nickname,
    avatar,
    tel,
    mobile,
    email,
    lastLoginIp,
    lastLoginTime,
    status,
    validtime,
    address,
    city,
    remark,
    company,
    province,
    area,
    fileSize,
    loginstatus,
    create_time,
    update_time,
    creator_id,
    creator_name,
    updater_id,
    updater_name
) VALUES (
    1,                                              -- uid: 添加用户ID
    1,                                              -- dept_id: 部门ID
    'admin',                                        -- username: 用户账号
    MD5(CONCAT('admin123', 'e-voice-2024')),       -- password: 密码哈希
    'e-voice-2024',                                 -- salt: 密码盐
    '系统管理员',                                    -- name: 姓名
    '管理员',                                        -- nickname: 昵称
    '',                                             -- avatar: 头像
    '',                                             -- tel: 备用电话
    '',                                             -- mobile: 手机号码
    'admin@example.com',                           -- email: 邮箱
    '127.0.0.1',                                   -- lastLoginIp: 最后登录IP
    0,                                              -- lastLoginTime: 最后登录时间
    0,                                              -- status: 状态 0=正常
    0,                                              -- validtime: 账号有效时间 0=无限
    '',                                             -- address: 地址
    '',                                             -- city: 城市
    'E-Voice系统默认管理员',                         -- remark: 描述
    '',                                             -- company: 公司名称
    '',                                             -- province: 省份
    '',                                             -- area: 地区
    3787456512,                                     -- fileSize: 附件存储空间
    0,                                              -- loginstatus: 登录状态
    NOW(),                                          -- create_time: 创建时间
    NOW(),                                          -- update_time: 更新时间
    1,                                              -- creator_id: 创建人ID
    'system',                                       -- creator_name: 创建人名称
    1,                                              -- updater_id: 更新人ID
    'system'                                        -- updater_name: 更新人名称
)
ON DUPLICATE KEY UPDATE
    password = MD5(CONCAT('admin123', 'e-voice-2024')),
    salt = 'e-voice-2024';

-- 验证插入结果
SELECT id, username, name, email, status FROM business_account WHERE username = 'admin';

-- 如果需要为管理员分配角色权限，执行以下语句：
-- 注意：需要先确保 business_auth_role 表中存在角色记录

-- 查看现有角色
SELECT id, name FROM business_auth_role WHERE status = 0 LIMIT 10;

-- 如果存在超级管理员角色（假设 role_id = 1），为管理员分配角色
-- INSERT INTO business_auth_role_access (uid, role_id, create_time, update_time)
-- SELECT 
--     (SELECT id FROM business_account WHERE username = 'admin'),
--     1,
--     NOW(),
--     NOW()
-- FROM DUAL
-- WHERE NOT EXISTS (
--     SELECT 1 FROM business_auth_role_access 
--     WHERE uid = (SELECT id FROM business_account WHERE username = 'admin')
--     AND role_id = 1
-- );


