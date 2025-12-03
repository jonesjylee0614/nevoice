-- MDT会议菜单配置SQL（简化版 - 直接在数据库工具中执行）
-- 数据库：evoice
-- 表名：business_auth_rule

-- =====================================================
-- 步骤1：检查"会议管理"菜单是否存在
-- =====================================================
SELECT id, title, routePath FROM business_auth_rule WHERE routePath = '/meeting' OR title = '会议管理';

-- 如果没有返回结果，继续执行步骤2；如果有结果，记住id值用于步骤3

-- =====================================================
-- 步骤2：创建"会议管理"目录菜单（如果不存在）
-- =====================================================
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1, '会议管理', 'menu.meeting', 30, 0, 0, 'icon-calendar',
    '/meeting', 'meeting', 'LAYOUT', '', '',
    0, 0, 0, 1, 0, 0, 1, 0, NOW(), NOW()
);

-- 执行后记住返回的ID（或执行下面的查询获取）
SELECT id FROM business_auth_rule WHERE routePath = '/meeting';

-- =====================================================
-- 步骤3：创建MDT会议菜单（将 {PARENT_ID} 替换为上面查询的ID）
-- =====================================================
-- 3.1 MDT会议列表页
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1, 'MDT会议', 'menu.meeting.mdt', 1, 1, {PARENT_ID}, '',
    '/meeting/mdt', 'meetingMdt', '/meeting/mdt/index', '', 'meeting:mdt:list',
    0, 0, 1, 1, 0, 0, 1, 0, NOW(), NOW()
);

-- 获取MDT会议菜单ID
SELECT id FROM business_auth_rule WHERE routePath = '/meeting/mdt';

-- 3.2 MDT会议详情页（隐藏菜单）- 将 {PARENT_ID} 替换为会议管理的ID
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1, '会议详情', 'menu.meeting.mdt.detail', 2, 1, {PARENT_ID}, '',
    '/meeting/mdt/detail', 'meetingMdtDetail', '/meeting/mdt/Detail', '', 'meeting:mdt:detail',
    0, 0, 0, 1, 1, 0, 1, 0, NOW(), NOW()
);

-- =====================================================
-- 步骤4：创建按钮权限（将 {MDT_MENU_ID} 替换为MDT会议的ID）
-- =====================================================
-- 新建会议
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1, '新建会议', '', 1, 2, {MDT_MENU_ID}, '', '', '', '', '', 'meeting:mdt:add',
    0, 0, 0, 1, 0, 0, 1, 0, NOW(), NOW()
);

-- 编辑会议
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1, '编辑会议', '', 2, 2, {MDT_MENU_ID}, '', '', '', '', '', 'meeting:mdt:edit',
    0, 0, 0, 1, 0, 0, 1, 0, NOW(), NOW()
);

-- 删除会议
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1, '删除会议', '', 3, 2, {MDT_MENU_ID}, '', '', '', '', '', 'meeting:mdt:delete',
    0, 0, 0, 1, 0, 0, 1, 0, NOW(), NOW()
);

-- =====================================================
-- 步骤5：配置角色权限
-- =====================================================
-- 先查询角色表
SELECT id, name FROM business_auth_role;

-- 查询新添加的所有菜单ID
SELECT id, title, routePath, pid FROM business_auth_rule 
WHERE routePath LIKE '%meeting%' OR title LIKE '%会议%' 
ORDER BY pid, orderNo;

-- 假设超级管理员角色ID为1，将菜单权限添加到角色
-- 查看角色权限关联方式（可能是字段存储或关联表）
-- 如果是字段存储，通常是 business_auth_role 表的 rules 字段
-- 将新菜单ID添加到角色的rules字段中（逗号分隔）

-- 示例：更新角色权限（将 {MENU_IDS} 替换为新菜单ID列表，用逗号分隔）
-- UPDATE business_auth_role SET rules = CONCAT(rules, ',{MENU_IDS}') WHERE id = 1;

-- 或者查看是否有单独的角色菜单关联表
SELECT TABLE_NAME FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'evoice' AND TABLE_NAME LIKE '%role%';

