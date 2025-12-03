-- MDT会议菜单配置SQL
-- 执行前请确认：
-- 1. 如果"会议管理"父级菜单已存在，请先查询其ID替换下面的 @meeting_parent_id
-- 2. 如果"会议管理"不存在，需要先执行第一段创建父级菜单

-- =====================================================
-- 方式一：如果"会议管理"菜单已存在，先查询其ID
-- =====================================================
-- SELECT id FROM business_auth_rule WHERE routePath = '/meeting' OR title = '会议管理';
-- 将查询结果替换下面的 @meeting_parent_id

-- =====================================================
-- 方式二：如果"会议管理"菜单不存在，先创建父级菜单
-- =====================================================
-- 创建"会议管理"目录菜单
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1,                      -- uid
    '会议管理',              -- title
    'menu.meeting',         -- locale
    30,                     -- orderNo (排序)
    0,                      -- type: 0=目录
    0,                      -- pid: 0=顶级菜单
    'icon-calendar',        -- icon
    '/meeting',             -- routePath
    'meeting',              -- routeName
    'LAYOUT',               -- component
    '',                     -- redirect
    '',                     -- permission
    0,                      -- status: 0=启用
    0,                      -- isExt: 0=非外链
    0,                      -- keepalive
    1,                      -- requiresAuth: 1=需要登录
    0,                      -- hideInMenu: 0=显示
    0,                      -- hideChildrenInMenu
    1,                      -- activeMenu
    0,                      -- noAffix
    NOW(),                  -- createTime
    NOW()                   -- updateTime
);

-- 获取刚插入的会议管理菜单ID（如果已存在请替换为实际ID）
SET @meeting_parent_id = LAST_INSERT_ID();

-- =====================================================
-- 创建MDT会议子菜单
-- =====================================================
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1,                          -- uid
    'MDT会议',                   -- title
    'menu.meeting.mdt',         -- locale
    1,                          -- orderNo
    1,                          -- type: 1=菜单
    @meeting_parent_id,         -- pid: 父级菜单ID
    '',                         -- icon
    '/meeting/mdt',             -- routePath
    'meetingMdt',               -- routeName
    '/meeting/mdt/index',       -- component
    '',                         -- redirect
    'meeting:mdt:list',         -- permission
    0,                          -- status: 0=启用
    0,                          -- isExt
    1,                          -- keepalive: 1=缓存
    1,                          -- requiresAuth
    0,                          -- hideInMenu: 0=显示
    0,                          -- hideChildrenInMenu
    1,                          -- activeMenu
    0,                          -- noAffix
    NOW(),
    NOW()
);

-- 获取MDT会议菜单ID
SET @mdt_menu_id = LAST_INSERT_ID();

-- =====================================================
-- 创建MDT会议详情页（隐藏菜单）
-- =====================================================
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1,                              -- uid
    '会议详情',                      -- title
    'menu.meeting.mdt.detail',      -- locale
    2,                              -- orderNo
    1,                              -- type: 1=菜单
    @meeting_parent_id,             -- pid
    '',                             -- icon
    '/meeting/mdt/detail',          -- routePath
    'meetingMdtDetail',             -- routeName
    '/meeting/mdt/Detail',          -- component
    '',                             -- redirect
    'meeting:mdt:detail',           -- permission
    0,                              -- status
    0,                              -- isExt
    0,                              -- keepalive
    1,                              -- requiresAuth
    1,                              -- hideInMenu: 1=隐藏
    0,                              -- hideChildrenInMenu
    1,                              -- activeMenu
    0,                              -- noAffix
    NOW(),
    NOW()
);

-- =====================================================
-- 创建MDT会议按钮权限（可选）
-- =====================================================
-- 新建会议按钮
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1, '新建会议', '', 1, 2, @mdt_menu_id, '', '', '', '', '', 
    'meeting:mdt:add', 0, 0, 0, 1, 0, 0, 1, 0, NOW(), NOW()
);

-- 编辑会议按钮
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1, '编辑会议', '', 2, 2, @mdt_menu_id, '', '', '', '', '', 
    'meeting:mdt:edit', 0, 0, 0, 1, 0, 0, 1, 0, NOW(), NOW()
);

-- 删除会议按钮
INSERT INTO `business_auth_rule` (
    `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, 
    `routePath`, `routeName`, `component`, `redirect`, `permission`,
    `status`, `isExt`, `keepalive`, `requiresAuth`, 
    `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`,
    `createTime`, `updateTime`
) VALUES (
    1, '删除会议', '', 3, 2, @mdt_menu_id, '', '', '', '', '', 
    'meeting:mdt:delete', 0, 0, 0, 1, 0, 0, 1, 0, NOW(), NOW()
);

-- =====================================================
-- 如果需要查看插入结果，执行以下查询
-- =====================================================
-- SELECT * FROM business_auth_rule WHERE routePath LIKE '%meeting%' ORDER BY pid, orderNo;

