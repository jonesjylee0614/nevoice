-- ============================================================
-- MDT会议功能数据库表结构
-- 创建日期: 2024-12-02
-- 说明: 多学科团队(MDT)会议管理功能，支持实时语音识别、声纹匹配、AI总结
-- ============================================================

-- ------------------------------------------------------------
-- 表1: meeting_mdt (MDT会议主表)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `meeting_mdt`;
CREATE TABLE `meeting_mdt` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `title` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '会议标题',
    `description` TEXT COMMENT '会议说明',
    `host_id` BIGINT DEFAULT NULL COMMENT '主持人ID（关联voice_print.user_id）',
    `host_name` VARCHAR(100) DEFAULT '' COMMENT '主持人姓名',
    `start_time` DATETIME DEFAULT NULL COMMENT '开始时间',
    `end_time` DATETIME DEFAULT NULL COMMENT '结束时间',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态：0-待开始 1-进行中 2-已结束',
    `participants` JSON COMMENT '参会人列表 [{userId, userName, department, role}]',
    `tags` JSON COMMENT '标签 ["多学科", "病例讨论"]',
    `summary` TEXT COMMENT 'AI生成的会议总结',
    `summary_status` TINYINT NOT NULL DEFAULT 0 COMMENT '总结状态：0-未生成 1-生成中 2-已生成',
    `audio_path` VARCHAR(500) DEFAULT '' COMMENT '完整录音文件路径',
    `dialog_count` INT NOT NULL DEFAULT 0 COMMENT '对话条数',
    `duration_seconds` INT NOT NULL DEFAULT 0 COMMENT '会议时长（秒）',
    
    -- 基础字段
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `creator_id` BIGINT DEFAULT NULL COMMENT '创建人ID',
    `creator_name` VARCHAR(200) DEFAULT '' COMMENT '创建人名称',
    `updater_id` BIGINT DEFAULT NULL COMMENT '更新人ID',
    `updater_name` VARCHAR(200) DEFAULT '' COMMENT '更新人名称',
    
    -- 软删除字段
    `deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否删除：0-否 1-是',
    `deleted_at` DATETIME DEFAULT NULL COMMENT '删除时间',
    
    PRIMARY KEY (`id`),
    KEY `idx_status` (`status`),
    KEY `idx_start_time` (`start_time`),
    KEY `idx_host_id` (`host_id`),
    KEY `idx_create_time` (`create_time`),
    KEY `idx_deleted` (`deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MDT会议主表';


-- ------------------------------------------------------------
-- 表2: meeting_mdt_dialog (MDT会议对话详情表)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `meeting_mdt_dialog`;
CREATE TABLE `meeting_mdt_dialog` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `meeting_id` BIGINT NOT NULL COMMENT '会议ID',
    `seq` INT NOT NULL DEFAULT 0 COMMENT '序号（对话顺序）',
    `speaker_id` BIGINT DEFAULT NULL COMMENT '发言人ID（关联voice_print.user_id）',
    `speaker_name` VARCHAR(100) DEFAULT '' COMMENT '发言人姓名',
    `speaker_role` VARCHAR(200) DEFAULT '' COMMENT '发言人角色/科室',
    `recognized` TINYINT NOT NULL DEFAULT 0 COMMENT '识别状态：0-未识别 1-声纹自动识别 2-手动指定',
    `recognition_note` VARCHAR(200) DEFAULT '' COMMENT '识别备注',
    `recognition_score` DECIMAL(5,4) DEFAULT NULL COMMENT '声纹匹配相似度分数',
    `speak_time` DATETIME DEFAULT NULL COMMENT '发言时间',
    `start_offset` INT DEFAULT 0 COMMENT '录音起始偏移（毫秒）',
    `end_offset` INT DEFAULT 0 COMMENT '录音结束偏移（毫秒）',
    `duration_ms` INT DEFAULT 0 COMMENT '发言时长（毫秒）',
    `text` TEXT COMMENT '识别文本内容',
    `audio_path` VARCHAR(500) DEFAULT '' COMMENT '音频片段路径',
    
    -- 基础字段
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (`id`),
    KEY `idx_meeting_id` (`meeting_id`),
    KEY `idx_speaker_id` (`speaker_id`),
    KEY `idx_seq` (`meeting_id`, `seq`),
    KEY `idx_speak_time` (`speak_time`),
    CONSTRAINT `fk_dialog_meeting` FOREIGN KEY (`meeting_id`) REFERENCES `meeting_mdt` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MDT会议对话详情表';


-- ------------------------------------------------------------
-- 表3: meeting_mdt_participant (MDT会议参会人表 - 可选)
-- 说明: 如果参会人关系需要单独管理，可以使用此表
--       否则可以使用meeting_mdt表的participants JSON字段
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `meeting_mdt_participant`;
CREATE TABLE `meeting_mdt_participant` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `meeting_id` BIGINT NOT NULL COMMENT '会议ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID（关联voice_print.user_id）',
    `user_name` VARCHAR(100) DEFAULT '' COMMENT '用户姓名',
    `department` VARCHAR(100) DEFAULT '' COMMENT '科室',
    `role` VARCHAR(100) DEFAULT '' COMMENT '职位/角色',
    `is_host` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否主持人：0-否 1-是',
    `join_time` DATETIME DEFAULT NULL COMMENT '加入时间',
    `leave_time` DATETIME DEFAULT NULL COMMENT '离开时间',
    `speak_count` INT NOT NULL DEFAULT 0 COMMENT '发言次数',
    `speak_duration_ms` INT NOT NULL DEFAULT 0 COMMENT '发言总时长（毫秒）',
    
    -- 基础字段
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_meeting_user` (`meeting_id`, `user_id`),
    KEY `idx_user_id` (`user_id`),
    CONSTRAINT `fk_participant_meeting` FOREIGN KEY (`meeting_id`) REFERENCES `meeting_mdt` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MDT会议参会人表';


-- ------------------------------------------------------------
-- 表4: staff_directory (人员库表 - 扩展voice_print表)
-- 说明: 如果需要独立的人员库管理，可以新建此表
--       也可以直接扩展现有的voice_print表增加department、role字段
-- ------------------------------------------------------------
-- 建议: 先检查voice_print表是否已有相关字段，若无则执行以下ALTER语句

-- ALTER TABLE `voice_print` 
--     ADD COLUMN `department` VARCHAR(100) DEFAULT '' COMMENT '科室' AFTER `user_name`,
--     ADD COLUMN `role` VARCHAR(100) DEFAULT '' COMMENT '职位/角色' AFTER `department`,
--     ADD COLUMN `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用' AFTER `role`;


-- ============================================================
-- 示例数据（用于测试）
-- ============================================================

-- 插入测试会议
INSERT INTO `meeting_mdt` (
    `title`, `description`, `host_id`, `host_name`, 
    `start_time`, `end_time`, `status`, 
    `participants`, `tags`,
    `creator_id`, `creator_name`
) VALUES (
    '呼吸科多学科病例讨论',
    '讨论一例复杂肺部阴影患者的诊疗方案，梳理影像和实验室数据。',
    1, '张主任',
    '2024-05-08 09:30:00', '2024-05-08 10:45:00', 2,
    '[{"userId":1,"userName":"张主任","department":"呼吸与危重症医学科","role":"科室主任"},{"userId":2,"userName":"王专家","department":"影像科","role":"主任医师"},{"userId":3,"userName":"刘医生","department":"重症医学科","role":"主治医师"}]',
    '["多学科","病例讨论"]',
    1, '系统'
);

-- 获取刚插入的会议ID（MySQL变量）
SET @meeting_id = LAST_INSERT_ID();

-- 插入测试对话记录
INSERT INTO `meeting_mdt_dialog` (
    `meeting_id`, `seq`, `speaker_id`, `speaker_name`, `speaker_role`,
    `recognized`, `recognition_note`, `recognition_score`,
    `speak_time`, `start_offset`, `end_offset`, `duration_ms`, `text`
) VALUES 
(
    @meeting_id, 1, 1, '张主任', '呼吸与危重症医学科主任',
    1, '声纹识别匹配成功', 0.8500,
    '2024-05-08 09:32:00', 120000, 145000, 25000,
    '各位专家早上好，患者王某，男性58岁，入院3天，目前影像显示双肺散在磨玻璃样改变，我们需要明确病因并制定治疗方案。'
),
(
    @meeting_id, 2, 2, '王专家', '影像科主任医师',
    1, '声纹识别匹配成功', 0.9200,
    '2024-05-08 09:36:00', 360000, 420000, 60000,
    '从目前CT来看，病灶主要位于右肺上叶背段，考虑免疫相关性肺炎可能性较大，建议结合近期免疫治疗史进一步判断。'
),
(
    @meeting_id, 3, NULL, '未知发言人', '未识别',
    0, '声纹未匹配，可人工指定', NULL,
    '2024-05-08 09:42:00', 720000, 780000, 60000,
    '患者昨天夜间血气分析PaO₂较前下降，呼吸机氧浓度提升至40%才能维持饱和度。'
);

-- 更新会议对话数
UPDATE `meeting_mdt` SET `dialog_count` = 3 WHERE `id` = @meeting_id;


-- ============================================================
-- 查询验证
-- ============================================================

-- 查看会议列表
SELECT id, title, host_name, status, dialog_count, create_time 
FROM meeting_mdt 
WHERE deleted = 0 
ORDER BY create_time DESC;

-- 查看会议对话
SELECT d.seq, d.speaker_name, d.speaker_role, d.recognized, d.text
FROM meeting_mdt_dialog d
WHERE d.meeting_id = @meeting_id
ORDER BY d.seq;


-- ============================================================
-- 常用查询SQL示例
-- ============================================================

-- 1. 获取会议详情及对话列表
/*
SELECT m.*, 
       (SELECT COUNT(*) FROM meeting_mdt_dialog WHERE meeting_id = m.id) as dialog_total
FROM meeting_mdt m 
WHERE m.id = ? AND m.deleted = 0;

SELECT * FROM meeting_mdt_dialog WHERE meeting_id = ? ORDER BY seq;
*/

-- 2. 搜索会议（按标题/主持人/参会人）
/*
SELECT * FROM meeting_mdt 
WHERE deleted = 0 
  AND (title LIKE CONCAT('%', ?, '%') 
       OR host_name LIKE CONCAT('%', ?, '%')
       OR JSON_SEARCH(participants, 'one', CONCAT('%', ?, '%')) IS NOT NULL)
ORDER BY start_time DESC;
*/

-- 3. 更新AI总结
/*
UPDATE meeting_mdt 
SET summary = ?, summary_status = 2, update_time = NOW() 
WHERE id = ?;
*/

-- 4. 手动指定发言人
/*
UPDATE meeting_mdt_dialog 
SET speaker_id = ?, speaker_name = ?, speaker_role = ?, 
    recognized = 2, recognition_note = '已人工确认身份',
    update_time = NOW()
WHERE id = ?;
*/

