-- 添加热词管理菜单到数据库
-- 请根据实际情况修改 pid 值（语音能力菜单的ID）

-- 1. 先查询语音能力菜单的ID
SELECT id, title, routePath FROM business_auth_rule WHERE routePath = '/voice' OR title = '语音能力';

-- 2. 检查热词管理菜单是否已存在（假设语音能力的pid是结果中的id）
-- SELECT id FROM business_auth_rule WHERE routePath = 'hotword' AND pid = {语音能力ID};

-- 3. 插入热词管理菜单（请将 {语音能力ID} 替换为实际值）
-- INSERT INTO business_auth_rule (pid, title, routePath, component, icon, weigh, type, status, create_time, update_time)
-- VALUES ({语音能力ID}, '热词管理', 'hotword', '/voice/hotword/index', 'icon-file', 100, 1, 1, NOW(), NOW());

-- 4. 插入操作权限（请将 {热词菜单ID} 替换为上面插入后的ID）
-- INSERT INTO business_auth_rule (pid, title, perms, type, status, create_time, update_time) VALUES
-- ({热词菜单ID}, '热词列表', 'vh:base', 2, 1, NOW(), NOW()),
-- ({热词菜单ID}, '热词编辑', 'vh:edit', 2, 1, NOW(), NOW()),
-- ({热词菜单ID}, '热词删除', 'vh:del', 2, 1, NOW(), NOW()),
-- ({热词菜单ID}, '状态更新', 'vh:upStatus', 2, 1, NOW(), NOW()),
-- ({热词菜单ID}, '批量导入', 'vh:import', 2, 1, NOW(), NOW()),
-- ({热词菜单ID}, '导出', 'vh:export', 2, 1, NOW(), NOW()),
-- ({热词菜单ID}, '同步文件', 'vh:sync', 2, 1, NOW(), NOW());

