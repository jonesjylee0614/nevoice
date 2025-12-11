
-- ----------------------------
-- Dump Platform: mayfly-go
-- Dump Time: 2025-07-23 15:45:10 
-- Dump DB: gofly_single 
-- DB Dialect: postgres 
-- ----------------------------


-- ----------------------------
-- Table structure: attachment 
-- ----------------------------
DROP TABLE IF EXISTS "attachment";
CREATE TABLE "attachment" (
 "id" bigserial NOT NULL,
 "uid" int8 NOT NULL DEFAULT 0,
 "cid" int8 NOT NULL DEFAULT 0,
 "url" varchar(255) NOT NULL,
 "imagewidth" varchar(30) NOT NULL,
 "imageheight" varchar(30) NOT NULL,
 "imagetype" varchar(30) NOT NULL,
 "imageframes" int4 NOT NULL DEFAULT 0,
 "filesize" int4 NOT NULL DEFAULT 0,
 "mimetype" varchar(100) NOT NULL,
 "extparam" varchar(255) NOT NULL,
 "storage" varchar(500) NOT NULL DEFAULT 'local',
 "sha1" varchar(40) NOT NULL,
 "title" varchar(500) NOT NULL,
 "name" varchar(500) NOT NULL,
 "cover_url" varchar(255) NOT NULL,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP,
 "upload_time" timestamp, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "attachment" IS '附件管理';
COMMENT ON COLUMN "attachment"."uid" IS '上传用户';
COMMENT ON COLUMN "attachment"."cid" IS '分类';
COMMENT ON COLUMN "attachment"."url" IS '访问路径';
COMMENT ON COLUMN "attachment"."imagewidth" IS '宽度';
COMMENT ON COLUMN "attachment"."imageheight" IS '高度';
COMMENT ON COLUMN "attachment"."imagetype" IS '图片类型';
COMMENT ON COLUMN "attachment"."imageframes" IS '图片帧数';
COMMENT ON COLUMN "attachment"."filesize" IS '文件大小';
COMMENT ON COLUMN "attachment"."mimetype" IS 'mime类型';
COMMENT ON COLUMN "attachment"."extparam" IS '透传数据';
COMMENT ON COLUMN "attachment"."storage" IS '存储位置';
COMMENT ON COLUMN "attachment"."sha1" IS '文件 sha1编码';
COMMENT ON COLUMN "attachment"."title" IS '文件名称';
COMMENT ON COLUMN "attachment"."name" IS '附件名称';
COMMENT ON COLUMN "attachment"."cover_url" IS '视频封面';
COMMENT ON COLUMN "attachment"."update_time" IS '更新时间';
COMMENT ON COLUMN "attachment"."upload_time" IS '上传时间';

-- ----------------------------
-- Data: attachment 
-- ----------------------------
BEGIN;
INSERT INTO "attachment" ("id", "uid", "cid", "url", "imagewidth", "imageheight", "imagetype", "imageframes", "filesize", "mimetype", "extparam", "storage", "sha1", "title", "name", "cover_url", "update_time", "upload_time") VALUES 
(722, 1, 0, 'resource/uploads/20230309/162ba4b5924cc0fe399d7a2ffd1d1110.png', '', '', '', 0, 21902, 'image/png', '', 'E:\\Project\\go\\src\\GoFlyAdmin\\tmpresource\\uploads\\20230309\\162ba4b5924cc0fe399d7a2ffd1d1110.png', '820751820adeadea0c353765e7c7137b', '接种后定时回访缩略图', '接种后定时回访缩略图.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(723, 1, 0, 'resource/uploads/20230310/b4ac2e2246073c50c9dc764d5b426720.png', '', '', '', 0, 21902, 'image/png', '', 'E:\\Project\\go\\src\\GoFlyAdmin\\tmpresource\\uploads\\20230310\\b4ac2e2246073c50c9dc764d5b426720.png', 'd811adccbd7d0b424f6de118c09e7ed3', '接种后定时回访缩略图', '接种后定时回访缩略图.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(725, 1, 0, 'resource/uploads/20230506/d4bb8324ee87699ed727bc1fd0479b34.jpg', '', '', '', 0, 2621283, 'image/jpeg', '', '/dataDB/project/go/gofly_singleresource\\uploads\\20230506\\d4bb8324ee87699ed727bc1fd0479b34.jpg', 'b089570f68f71c6f4175b1e91cac6014', 'Default', 'Default.jpg', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(726, 1, 0, 'resource/uploads/20230507/7992812e7e9f2b140968ba3874de1d1a.jpg', '', '', '', 0, 23454, 'image/jpeg', '', '/dataDB/project/go/gofly_singleresource\\uploads\\20230507\\7992812e7e9f2b140968ba3874de1d1a.jpg', 'c378ea13ca636384da41926588b95fdb', '0', '0.jpg', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(727, 1, 0, 'resource/uploads/20230607/f1fbf7039464d632d9b5fcecb1e41fab.png', '', '', '', 0, 337597, 'image/png', '', '/dataDB/project/go/gofly_singleresource\\uploads\\20230607\\f1fbf7039464d632d9b5fcecb1e41fab.png', 'ca7ce059dbafb26a728f8d3c66ef5cb6', 'loginbanner1', 'loginbanner1.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(728, 1, 0, 'resource/uploads/20230607/4825b3bc4721d2e6266b9696f47b23c5.png', '', '', '', 0, 277224, 'image/png', '', '/dataDB/project/go/gofly_singleresource\\uploads\\20230607\\4825b3bc4721d2e6266b9696f47b23c5.png', '5120d2bcc567803f0435e4782e857457', 'loginbanner2', 'loginbanner2.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(729, 1, 0, 'resource/uploads/20230607/33926ec2fcbc2da95e9cae158e00019e.png', '', '', '', 0, 136610, 'image/png', '', '/dataDB/project/go/gofly_singleresource\\uploads\\20230607\\33926ec2fcbc2da95e9cae158e00019e.png', '8b13300e268f2f4ddf100eaf8c2876b9', 'loginbanner3', 'loginbanner3.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(730, 1, 0, 'resource/uploads/20230608/eaf1511fa669c7dd54af301d50c9478e.png', '', '', '', 0, 277224, 'image/png', '', '/dataDB/project/go/gofly_singleresource\\uploads\\20230608\\eaf1511fa669c7dd54af301d50c9478e.png', '53bc5d1a0ac48e75121295b5c1e004ce', 'loginbanner2', 'loginbanner2.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(733, 1, 0, 'resource/uploads/20230609/82b4e47320cd007879ff180ca63fe2b2.png', '', '', '', 0, 351874, 'image/png', '', '/dataDB/project/go/gofly_singleresource\\uploads\\20230609\\82b4e47320cd007879ff180ca63fe2b2.png', '8536ed44d16b2e7c1f354ced43f50b7b', 'menu', 'menu.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(734, 1, 0, 'resource/uploads/20231202/95ca6221f1ec5ba2f9739c7f4cb736c6.zip', '', '', '', 0, 129849, 'application/x-zip-compressed', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20231202\\95ca6221f1ec5ba2f9739c7f4cb7', '4aa32d3b5af3ea81d9ea362fad210b3b', 'wxsys', 'wxsys.zip', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(735, 1, 0, 'resource/uploads/20231202/363e90e3ae28ab59569347cb610a30f6.zip', '', '', '', 0, 124345, 'application/x-zip-compressed', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20231202\\363e90e3ae28ab59569347cb610a', '98e7ce8be96f1530d1de1786a891c8fc', 'wxplus', 'wxplus.zip', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(736, 1, 0, 'resource/uploads/20231203/b014ea30ed4e749fe61cd87f4d66ca5c.zip', '', '', '', 0, 129849, 'application/x-zip-compressed', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20231203\\b014ea30ed4e749fe61cd87f4d66', 'c3a1da93c79a72dd17a17b8a3faab206', 'wxsys', 'wxsys.zip', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(737, 1, 0, 'resource/uploads/20231203/f803f6e9cbab2eb6bb64ad1a18e37bab.zip', '', '', '', 0, 129849, 'application/x-zip-compressed', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20231203\\f803f6e9cbab2eb6bb64ad1a18e3', 'c3a1da93c79a72dd17a17b8a3faab206', 'wxsys', 'wxsys.zip', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(738, 1, 0, 'resource/uploads/20231203/99fa7bda307258942a6e84c41cf88eff.zip', '', '', '', 0, 129849, 'application/x-zip-compressed', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20231203\\99fa7bda307258942a6e84c41cf8', 'c3a1da93c79a72dd17a17b8a3faab206', 'wxsys', 'wxsys.zip', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(739, 1, 1, 'resource/uploads/20240120/269281af0350cb928a6ce8c9c59b7335.png', '', '', '', 0, 36400, 'image/png', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20240120\\269281af0350cb928a6ce8c9c59b', '8886f29db3f9396e566920d4bfa27adf', 'electron', 'electron.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(740, 1, 1, 'resource/uploads/20240120/c9b0b82ab76bafbf2c237c683a9ca6d3.png', '', '', '', 0, 55614, 'image/png', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20240120\\c9b0b82ab76bafbf2c237c683a9c', '3df0d0f5c7f0753d75cea532be054472', '103011293', '103011293.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(741, 1, 1, 'resource/uploads/20240120/bd1f5a91d41a69efa81c1d9e06447824.png', '', '', '', 0, 337597, 'image/png', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20240120\\bd1f5a91d41a69efa81c1d9e0644', '5da9e68d5ad04f4ea5f38ebccca908d9', 'loginbanner1', 'loginbanner1.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(742, 1, 1, 'resource/uploads/20240120/407161e2dbdc4cc4848bdc1a1478fde7.jpg', '', '', '', 0, 52295, 'image/jpeg', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20240120\\407161e2dbdc4cc4848bdc1a1478', '5d19ce226813f6755921e67ac606d875', '微信图片_20230816001705', '微信图片_20230816001705.jpg', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(743, 1, 1, 'resource/uploads/20240120/3f5ef54b8f57c7de9a702b7302567a87.png', '', '', '', 0, 3953, 'image/png', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20240120\\3f5ef54b8f57c7de9a702b730256', 'd363a8e018ba91331c43e2b2468a6717', 'getimage', 'getimage.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(744, 1, 1, 'resource/uploads/20240120/70180de5ee294a6a78ee88a2be52a796.png', '', '', '', 0, 686638, 'image/png', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmpresource\\uploads\\20240120\\70180de5ee294a6a78ee88a2be52', '31eeb6f38f852d46c94417b55c19c0a4', '微信截图_20230802001834 - 副本', '微信截图_20230802001834 - 副本.png', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21');
SELECT setval('attachment_id_seq', (SELECT max(id) FROM attachment));
COMMIT;

-- ----------------------------
-- Table structure: business_account 
-- ----------------------------
DROP TABLE IF EXISTS "business_account";
CREATE TABLE "business_account" (
 "id" bigserial NOT NULL,
 "uid" int8 NOT NULL,
 "dept_id" int8 NOT NULL,
 "username" text NOT NULL,
 "password" text NOT NULL,
 "salt" text NOT NULL,
 "name" varchar(50) NOT NULL DEFAULT '0',
 "nickname" text NOT NULL,
 "avatar" text NOT NULL,
 "tel" text NOT NULL,
 "mobile" text NOT NULL,
 "email" text NOT NULL,
 "lastLoginIp" text NOT NULL,
 "lastLoginTime" int8 NOT NULL,
 "status" int8 NOT NULL,
 "validtime" int8 NOT NULL,
 "create_time" timestamp,
 "update_time" timestamp,
 "address" text NOT NULL,
 "city" text NOT NULL,
 "remark" text NOT NULL,
 "company" text NOT NULL,
 "province" text NOT NULL,
 "area" text NOT NULL,
 "fileSize" int8 NOT NULL DEFAULT 3787456512,
 "loginstatus" int2,
 "appkey" varchar(50),
 "appKeySecret" varchar(100), 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "business_account" IS '用户端-用户信息';
COMMENT ON COLUMN "business_account"."uid" IS '添加用户';
COMMENT ON COLUMN "business_account"."dept_id" IS '部门id';
COMMENT ON COLUMN "business_account"."username" IS '用户账号';
COMMENT ON COLUMN "business_account"."password" IS '密码';
COMMENT ON COLUMN "business_account"."salt" IS '密码盐';
COMMENT ON COLUMN "business_account"."name" IS '姓名';
COMMENT ON COLUMN "business_account"."nickname" IS '昵称';
COMMENT ON COLUMN "business_account"."avatar" IS '头像';
COMMENT ON COLUMN "business_account"."tel" IS '备用电话用户自己填写';
COMMENT ON COLUMN "business_account"."mobile" IS '手机号码';
COMMENT ON COLUMN "business_account"."email" IS '邮箱';
COMMENT ON COLUMN "business_account"."lastLoginIp" IS '最后登录IP';
COMMENT ON COLUMN "business_account"."lastLoginTime" IS '最后登录时间';
COMMENT ON COLUMN "business_account"."status" IS '状态0=正常，1=禁用';
COMMENT ON COLUMN "business_account"."validtime" IS '账号有效时间0=无限';
COMMENT ON COLUMN "business_account"."create_time" IS '创建时间';
COMMENT ON COLUMN "business_account"."update_time" IS '更新时间';
COMMENT ON COLUMN "business_account"."address" IS '地址';
COMMENT ON COLUMN "business_account"."city" IS '城市';
COMMENT ON COLUMN "business_account"."remark" IS '描述';
COMMENT ON COLUMN "business_account"."company" IS '公司名称';
COMMENT ON COLUMN "business_account"."province" IS '省份';
COMMENT ON COLUMN "business_account"."area" IS '地区';
COMMENT ON COLUMN "business_account"."fileSize" IS '附件存储空间';
COMMENT ON COLUMN "business_account"."loginstatus" IS '登录状态';
COMMENT ON COLUMN "business_account"."appkey" IS 'appkey';
COMMENT ON COLUMN "business_account"."appKeySecret" IS 'appKeySecret';

-- ----------------------------
-- Data: business_account 
-- ----------------------------
BEGIN;
INSERT INTO "business_account" ("id", "uid", "dept_id", "username", "password", "salt", "name", "nickname", "avatar", "tel", "mobile", "email", "lastLoginIp", "lastLoginTime", "status", "validtime", "create_time", "update_time", "address", "city", "remark", "company", "province", "area", "fileSize", "loginstatus", "appkey", "appKeySecret") VALUES 
(1, 1, 3, 'gofly', '8cb8aef923ab5174aa392457960902af', '1697472561111', '开发管理员', 'leozy', 'http://localhost:8108/common/uploadfile/get_image?url=resource/uploads/20250704/71e26ab83700a7c7d7429456a017eda7.png', '88422345', '18988347563', '595324626@qq.com', '', 1753256417717, 0, 0, '2025-07-16 23:06:21', '2025-07-23 15:40:17', '中国重庆渝北区', '昆明', '开发账号', 'GoFLy科技1', '', 'chaoyang', 2147483647, 1, 'xNSo4SRBYnJR2AuX', 'X45JxQkb7IFdrhWtbe9CJI5v2iTW76'),
(14, 1, 3, 'test', 'd891fa386193b8a0d07f7396d01e003d', '1751618562166', 'test', 'test', 'http://localhost:8108/common/uploadfile/get_image?url=resource/uploads/20250711/6199ab6b6fad8f3f449b5ff175b17653.jpg', '', '', '', '', 1752035036751, 0, 0, '2025-07-11 15:06:21', '2025-07-11 18:27:53', '', '', '', '', '', '', 3787456512, 1, NULL, NULL),
(15, 1, 3, 'docliu', '75bf955239bb6901ebbb771299d0852a', '1752214339915', '刘医生', '刘医生', 'http://localhost:8108/common/uploadfile/get_image?url=resource/uploads/20250711/d37669a872c8004355c73ac5e672e262.jpg', '', '', '', '', 0, 0, 0, '2025-07-13 14:12:20', '2025-07-11 17:32:05', '', '', '', '', '', '', 3787456512, 0, NULL, NULL);
SELECT setval('business_account_id_seq', (SELECT max(id) FROM business_account));
COMMIT;

-- ----------------------------
-- Table Index: business_account 
-- ----------------------------
DROP INDEX IF EXISTS unique_idx;
CREATE unique INDEX "unique_idx" ON "business_account"("appkey");

-- ----------------------------
-- Table structure: business_attachment 
-- ----------------------------
DROP TABLE IF EXISTS "business_attachment";
CREATE TABLE "business_attachment" (
 "id" bigserial NOT NULL,
 "weigh" int8 NOT NULL DEFAULT 0,
 "pid" int8 NOT NULL DEFAULT 0,
 "name" varchar(500) NOT NULL,
 "title" varchar(500) NOT NULL,
 "type" int2 NOT NULL DEFAULT 0,
 "url" varchar(255) NOT NULL,
 "imagewidth" varchar(30) NOT NULL,
 "imageheight" varchar(30) NOT NULL,
 "filesize" int4 NOT NULL DEFAULT 0,
 "mimetype" varchar(100) NOT NULL,
 "extparam" varchar(255) NOT NULL,
 "storage" varchar(500) NOT NULL DEFAULT 'local',
 "cover_url" varchar(255) NOT NULL,
 "sha1" varchar(40) NOT NULL,
 "is_common" int2 NOT NULL DEFAULT 0,
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "business_attachment" IS '客户端附件';
COMMENT ON COLUMN "business_attachment"."weigh" IS '排序';
COMMENT ON COLUMN "business_attachment"."pid" IS '附件';
COMMENT ON COLUMN "business_attachment"."name" IS '附件原来名称';
COMMENT ON COLUMN "business_attachment"."title" IS '文件名称';
COMMENT ON COLUMN "business_attachment"."type" IS '文件类型0=图片，1=文件夹,2=视频，3=音频';
COMMENT ON COLUMN "business_attachment"."url" IS '访问路径';
COMMENT ON COLUMN "business_attachment"."imagewidth" IS '宽度';
COMMENT ON COLUMN "business_attachment"."imageheight" IS '高度';
COMMENT ON COLUMN "business_attachment"."filesize" IS '文件大小';
COMMENT ON COLUMN "business_attachment"."mimetype" IS 'mime类型';
COMMENT ON COLUMN "business_attachment"."extparam" IS '透传数据';
COMMENT ON COLUMN "business_attachment"."storage" IS '存储位置';
COMMENT ON COLUMN "business_attachment"."cover_url" IS '视频封面';
COMMENT ON COLUMN "business_attachment"."sha1" IS '文件 sha1编码';
COMMENT ON COLUMN "business_attachment"."is_common" IS '是否公共1=是';
COMMENT ON COLUMN "business_attachment"."create_time" IS '创建时间';
COMMENT ON COLUMN "business_attachment"."update_time" IS '更新时间';

-- ----------------------------
-- Data: business_attachment 
-- ----------------------------
BEGIN;
INSERT INTO "business_attachment" ("id", "weigh", "pid", "name", "title", "type", "url", "imagewidth", "imageheight", "filesize", "mimetype", "extparam", "storage", "cover_url", "sha1", "is_common", "create_time", "update_time") VALUES 
(1, 1, 0, '', '默认文件', 1, '', '', '', 0, '', '', 'local', '', '', 1, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(3, 3, 0, '', '新建文件夹', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(4, 4, 0, '', '新建文件夹', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(7, 7, 5, '', '新建文件夹', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(9, 9, 6, '', '新建文件夹', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(10, 10, 0, '', '新建文件夹', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(11, 11, 0, '', '新建文件夹4', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(24, 24, 0, '', '新建文件夹7', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(25, 25, 0, '', '新建文件夹8', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(26, 26, 0, '', '新建文件夹9', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(27, 27, 0, '', '新建文件夹10', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(28, 28, 0, '', '新建文件夹11', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(29, 29, 0, '', '新建文件夹12', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(30, 30, 0, '', '新建文件夹13', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(31, 31, 0, '', '新建文件夹13', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(32, 32, 0, '', '新建文件夹15', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(33, 33, 0, '', '新建文件夹16', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(34, 34, 0, '', '新建文件夹16', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(35, 35, 0, '', '新建文件夹18', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(36, 36, 0, '', '新建文件夹19', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(37, 37, 0, '', '新建文件夹20', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(38, 38, 0, '', '里面有文件', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(45, 45, 38, '', '新建文件夹1', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(49, 49, 38, '', '新建文件夹2', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(50, 50, 38, '', '新建文件夹3', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(51, 51, 38, '', '新建文件夹3', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(52, 52, 38, '', '新建文件夹5', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(53, 53, 38, '', '新建文件夹5', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(54, 54, 38, '', '新建文件夹7', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(55, 55, 38, '', '新建文件夹8', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(56, 56, 38, '', '新建文件夹9', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(57, 57, 38, '', '新建文件夹10', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(58, 58, 38, '', '新建文件夹11', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(59, 59, 38, '', '新建文件夹11', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(60, 60, 38, '', '新建文件夹13', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(61, 61, 38, '', '新建文件夹14', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(62, 62, 38, '', '新建文件夹15', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(63, 63, 38, '', '新建文件夹16', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(64, 64, 38, '', '新建文件夹17', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(65, 65, 38, '', '新建文件夹18', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(66, 66, 38, '', '新建文件夹19', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(67, 67, 38, '', '新建文件夹20', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(68, 68, 38, '', '新建文件夹21', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(69, 69, 38, '', '新建文件夹22', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(70, 70, 38, '', '新建文件夹23', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(71, 71, 38, '', '新建文件夹24', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(72, 72, 38, '', '新建文件夹25', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(73, 73, 38, '', '新建文件夹26', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(74, 74, 38, '', '新建文件夹27', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(75, 75, 38, '', '新建文件夹28', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(76, 76, 38, '', '新建文件夹29', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(77, 77, 38, '', '新建文件夹30', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(78, 78, 38, '', '新建文件夹31', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(85, 85, 0, '', '新建文件夹21', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(90, 90, 0, '', '新建文件夹20', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(91, 91, 0, '', '新建文件夹21', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(94, 94, 0, '', '111', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(97, 97, 1, '', '新建文件夹1', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(107, 107, 0, 'electron.png', 'electron', 0, 'resource/uploads/20231221/d397e65e2d50e0dcc2ced152fd8c224e.png', '', '', 36400, 'image/png', '', 'D:\\Project\\develop\\go\\src\\gofly_enterprise\\tmp/resource/uploads/20231221/d397e65e2d50e0dcc2ced152fd8', '', '62d3dbda952ff1bb762f92988fcbb293', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(108, 108, 0, '微信图片_20250402173339_137.jpg', '微信图片_20250402173339_137', 0, 'resource/uploads/20250704/7eba4b6d00da2e5fd2c586f4ddd14530.jpg', '', '', 77970, 'image/jpeg', '', '/home/leozy/.cache/JetBrains/GoLand2025.1/tmp/GoLand/resource/uploads/20250704/7eba4b6d00da2e5fd2c586f4ddd14530.jpg', '', '900ea939f029e8e6a3387681451624c4', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(109, 110, 0, '微信图片_2025-03-28_170508_330.png', '微信图片_2025-03-28_170508_330', 0, 'resource/uploads/20250704/71e26ab83700a7c7d7429456a017eda7.png', '', '', 85494, 'image/png', '', '/home/leozy/.cache/JetBrains/GoLand2025.1/tmp/GoLand/resource/uploads/20250704/71e26ab83700a7c7d7429456a017eda7.png', '', '3d8447540c99dcea7dae39f433bcd493', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(111, 111, 0, '', '新建文件夹20', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(112, 122, 0, '', '新建文件夹21', 1, '', '', '', 0, '', '', 'local', '', '', 0, '2025-07-10 15:06:21', '2025-07-17 16:55:47'),
(113, 113, 0, '微信图片_20250711165557_330.jpg', '微信图片_20250711165557_330', 0, 'resource/uploads/20250711/d37669a872c8004355c73ac5e672e262.jpg', '', '', 23574, 'image/jpeg', '', '/home/leozy/.cache/JetBrains/GoLand2025.1/tmp/GoLand/resource/uploads/20250711/d37669a872c8004355c73ac5e672e262.jpg', '', 'c33127b22e1124cd7775bf4dedc7765b', 0, '2025-07-11 16:56:39', '2025-07-11 16:56:39'),
(114, 114, 0, '微信图片_20250711165618_332.jpg', '微信图片_20250711165618_332', 0, 'resource/uploads/20250711/6199ab6b6fad8f3f449b5ff175b17653.jpg', '', '', 74715, 'image/jpeg', '', '/home/leozy/.cache/JetBrains/GoLand2025.1/tmp/GoLand/resource/uploads/20250711/6199ab6b6fad8f3f449b5ff175b17653.jpg', '', 'f5a3bc960892fb43627e4fc559a49743', 0, '2025-07-11 16:56:56', '2025-07-11 16:56:56');
SELECT setval('business_attachment_id_seq', (SELECT max(id) FROM business_attachment));
COMMIT;

-- ----------------------------
-- Table structure: business_auth_dept 
-- ----------------------------
DROP TABLE IF EXISTS "business_auth_dept";
CREATE TABLE "business_auth_dept" (
 "id" bigserial NOT NULL,
 "uid" int8 NOT NULL DEFAULT 0,
 "name" varchar(100) NOT NULL,
 "pid" int8 NOT NULL DEFAULT 0,
 "weigh" int8 NOT NULL,
 "status" int2 NOT NULL DEFAULT 0,
 "remark" varchar(255) NOT NULL,
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "business_auth_dept" IS '管理后台部门';
COMMENT ON COLUMN "business_auth_dept"."uid" IS '添加用户';
COMMENT ON COLUMN "business_auth_dept"."name" IS '部门名称';
COMMENT ON COLUMN "business_auth_dept"."pid" IS '上级部门';
COMMENT ON COLUMN "business_auth_dept"."weigh" IS '排序';
COMMENT ON COLUMN "business_auth_dept"."status" IS '状态';
COMMENT ON COLUMN "business_auth_dept"."remark" IS '备注';
COMMENT ON COLUMN "business_auth_dept"."create_time" IS '创建时间';
COMMENT ON COLUMN "business_auth_dept"."update_time" IS '更新时间';

-- ----------------------------
-- Data: business_auth_dept 
-- ----------------------------
BEGIN;
INSERT INTO "business_auth_dept" ("id", "uid", "name", "pid", "weigh", "status", "remark", "create_time", "update_time") VALUES 
(1, 1, '市场部门', 0, 1, 0, '营销', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(2, 1, '第一组', 1, 2, 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(3, 1, '研发部门', 1, 3, 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(4, 2, '领导部门', 0, 4, 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(6, 2, '人事组', 4, 6, 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21');
SELECT setval('business_auth_dept_id_seq', (SELECT max(id) FROM business_auth_dept));
COMMIT;

-- ----------------------------
-- Table structure: business_auth_role 
-- ----------------------------
DROP TABLE IF EXISTS "business_auth_role";
CREATE TABLE "business_auth_role" (
 "id" bigserial NOT NULL,
 "uid" int8 NOT NULL DEFAULT 0,
 "pid" int8 NOT NULL DEFAULT 0,
 "name" varchar(50) NOT NULL,
 "rules" text NOT NULL,
 "menu" text NOT NULL,
 "status" int2 NOT NULL DEFAULT 0,
 "data_access" int2 NOT NULL DEFAULT 0,
 "remark" varchar(255) NOT NULL,
 "weigh" int8 NOT NULL,
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "business_auth_role" IS '权限分组';
COMMENT ON COLUMN "business_auth_role"."uid" IS '添加用户id';
COMMENT ON COLUMN "business_auth_role"."pid" IS '父级';
COMMENT ON COLUMN "business_auth_role"."name" IS '名称';
COMMENT ON COLUMN "business_auth_role"."rules" IS '规则ID 所拥有的权限包扣父级';
COMMENT ON COLUMN "business_auth_role"."menu" IS '选择的id，用于编辑赋值';
COMMENT ON COLUMN "business_auth_role"."status" IS '状态1=禁用';
COMMENT ON COLUMN "business_auth_role"."data_access" IS '数据权限0=自己1=自己及子权限，2=全部';
COMMENT ON COLUMN "business_auth_role"."remark" IS '描述';
COMMENT ON COLUMN "business_auth_role"."weigh" IS '排序';
COMMENT ON COLUMN "business_auth_role"."create_time" IS '创建时间';
COMMENT ON COLUMN "business_auth_role"."update_time" IS '更新时间';

-- ----------------------------
-- Data: business_auth_role 
-- ----------------------------
BEGIN;
INSERT INTO "business_auth_role" ("id", "uid", "pid", "name", "rules", "menu", "status", "data_access", "remark", "weigh", "create_time", "update_time") VALUES 
(1, 1, 0, '超级管理组', '*', '*', 0, 0, '账号的总管理员', 1, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(5, 1, 1, '销售员2', '8,11,13,49,59,6', '[8,11,13,49,59]', 0, 0, '产品销售组', 2, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(6, 1, 1, '管理员', '7,11,13,32,8,64,61,12,63,6', '[7,11,13,32,8,64,61,12,63]', 0, 0, '', 3, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(7, 1, 6, '编辑组', '7,34,33,11,12,6', '[7,34,33,11,12]', 0, 0, '', 4, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(8, 1, 6, '兼职组', '11,12,34,7,33', '[11,12,34,7,33]', 0, 0, '测试', 8, '2025-07-10 23:06:21', '2025-07-11 14:09:27'),
(11, 1, 0, '管理组', '8,9,10,6', '[8,9,10]', 0, 0, '', 11, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(13, 1, 0, '市场部门', '8,6', '[8]', 0, 0, '', 13, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(16, 1, 0, '财务室', '8,48,49,59,69,6', '[8,48,49,59,69]', 0, 0, '修改', 16, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(19, 1, 1, '新增权限2', '70,8,11,438,439,437,443,455,453,454,13,444,458,456,442,451,452,450,69,68', '[70,8,11,438,439,437,443,455,453,454,13,444,458,456,442,451,452,450,69,68]', 0, 0, '', 19, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(21, 1, 0, '测试', '61,63,437,11,13,12', '[61,63,437,11,13,12]', 0, 0, '测试', 21, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(22, 1, 0, '测试', '61,63,437,11,13,12', '[61,63,437,11,13,12]', 0, 0, '测试', 22, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(23, 1, 0, 'test', '', '', 0, 0, '', 23, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(24, 1, 0, 'test', '61,63,438,439,440,437,11,442,451,452,450,13,443,454,455,453,12,444,457,458,456', '[61,63,438,439,440,437,11,442,451,452,450,13,443,454,455,453,12,444,457,458,456]', 0, 0, 'test', 24, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(25, 1, 20, 'test', '11,442,451,452,450', '[11,442,451,452,450]', 0, 0, 'test', 25, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(26, 1, 1, '声纹注册用户', '68,69,70', '[68,69,70]', 0, 0, '声纹管理需要查询拥有此角色的用户', 26, '2025-07-12 06:05:51', '2025-07-11 14:08:12');
SELECT setval('business_auth_role_id_seq', (SELECT max(id) FROM business_auth_role));
COMMIT;

-- ----------------------------
-- Table structure: business_auth_role_access 
-- ----------------------------
DROP TABLE IF EXISTS "business_auth_role_access";
CREATE TABLE "business_auth_role_access" (
 "id" bigserial NOT NULL,
 "uid" int8 NOT NULL DEFAULT 0,
 "role_id" int8 NOT NULL DEFAULT 0, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "business_auth_role_access" IS '用户角色授权';
COMMENT ON COLUMN "business_auth_role_access"."uid" IS '账号id';
COMMENT ON COLUMN "business_auth_role_access"."role_id" IS '授权id';

-- ----------------------------
-- Data: business_auth_role_access 
-- ----------------------------
BEGIN;
INSERT INTO "business_auth_role_access" ("id", "uid", "role_id") VALUES 
(1, 4, 1),
(2, 5, 6),
(3, 9, 6),
(4, 9, 5),
(5, 3, 5),
(6, 10, 5),
(7, 11, 1),
(8, 12, 1),
(9, 13, 1),
(10, 1, 1),
(25, 15, 26),
(26, 14, 19),
(27, 14, 26);
SELECT setval('business_auth_role_access_id_seq', (SELECT max(id) FROM business_auth_role_access));
COMMIT;

-- ----------------------------
-- Table structure: business_auth_rule 
-- ----------------------------
DROP TABLE IF EXISTS "business_auth_rule";
CREATE TABLE "business_auth_rule" (
 "id" bigserial NOT NULL,
 "uid" int8 NOT NULL DEFAULT 0,
 "title" varchar(200) NOT NULL,
 "locale" varchar(50),
 "orderNo" int8 NOT NULL DEFAULT 0,
 "type" int2 NOT NULL DEFAULT 0,
 "pid" int8 NOT NULL DEFAULT 0,
 "icon" varchar(50) NOT NULL,
 "routePath" varchar(100) NOT NULL,
 "routeName" varchar(100) NOT NULL,
 "component" varchar(100) NOT NULL,
 "redirect" varchar(100),
 "permission" varchar(80),
 "status" int2 NOT NULL DEFAULT 0,
 "isExt" int2 NOT NULL DEFAULT 0,
 "keepalive" int2 NOT NULL DEFAULT 0,
 "requiresAuth" int2 NOT NULL DEFAULT 1,
 "hideInMenu" int2 NOT NULL DEFAULT 0,
 "hideChildrenInMenu" int2 NOT NULL DEFAULT 0,
 "activeMenu" int2 NOT NULL DEFAULT 0,
 "noAffix" int2 NOT NULL DEFAULT 0,
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "business_auth_rule" IS 'C端-菜单';
COMMENT ON COLUMN "business_auth_rule"."uid" IS '添加用户';
COMMENT ON COLUMN "business_auth_rule"."title" IS '菜单名称';
COMMENT ON COLUMN "business_auth_rule"."locale" IS '中英文标题key';
COMMENT ON COLUMN "business_auth_rule"."orderNo" IS '排序';
COMMENT ON COLUMN "business_auth_rule"."type" IS '类型 0=目录，1=菜单，2=按钮';
COMMENT ON COLUMN "business_auth_rule"."pid" IS '上一级';
COMMENT ON COLUMN "business_auth_rule"."icon" IS '图标';
COMMENT ON COLUMN "business_auth_rule"."routePath" IS '路由地址';
COMMENT ON COLUMN "business_auth_rule"."routeName" IS '路由名称';
COMMENT ON COLUMN "business_auth_rule"."component" IS '组件路径';
COMMENT ON COLUMN "business_auth_rule"."redirect" IS '重定向地址';
COMMENT ON COLUMN "business_auth_rule"."permission" IS '权限标识';
COMMENT ON COLUMN "business_auth_rule"."status" IS '状态 0=启用1=禁用';
COMMENT ON COLUMN "business_auth_rule"."isExt" IS '是否外链 0=否1=是';
COMMENT ON COLUMN "business_auth_rule"."keepalive" IS '是否缓存 0=否1=是';
COMMENT ON COLUMN "business_auth_rule"."requiresAuth" IS '是否需要登录鉴权 0=否1=是';
COMMENT ON COLUMN "business_auth_rule"."hideInMenu" IS '是否在左侧菜单中隐藏该项 0=否1=是';
COMMENT ON COLUMN "business_auth_rule"."hideChildrenInMenu" IS '强制在左侧菜单中显示单项 0=否1=是';
COMMENT ON COLUMN "business_auth_rule"."activeMenu" IS '高亮设置的菜单项 0=否1=是';
COMMENT ON COLUMN "business_auth_rule"."noAffix" IS '如果设置为true，标签将不会添加到tab-bar中 0=否1=是';
COMMENT ON COLUMN "business_auth_rule"."create_time" IS '创建时间';
COMMENT ON COLUMN "business_auth_rule"."update_time" IS '更新时间';

-- ----------------------------
-- Data: business_auth_rule 
-- ----------------------------
BEGIN;
INSERT INTO "business_auth_rule" ("id", "uid", "title", "locale", "orderNo", "type", "pid", "icon", "routePath", "routeName", "component", "redirect", "permission", "status", "isExt", "keepalive", "requiresAuth", "hideInMenu", "hideChildrenInMenu", "activeMenu", "noAffix", "create_time", "update_time") VALUES 
(8, 1, '概况', '', 1, 1, 0, 'icon-dashboard', '/home', 'home', '/dashboard/workplace/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(11, 1, '角色管理', '', 2, 1, 61, '', 'role', 'role', '/system/role/index', '', '', 0, 0, 1, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(12, 1, '菜单管理', '', 4, 1, 61, '', 'rule', 'rule', '/system/rule/index', '', '', 0, 0, 1, 1, 2, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(13, 1, '部门管理', '', 3, 1, 61, '', 'dept', 'dept', '/system/dept/index', '', '', 0, 0, 1, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(61, 14, '系统设置', '', 3, 0, 0, 'icon-settings', '/system', 'system', 'LAYOUT', '/system/account', '', 0, 0, 0, 0, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(63, 1, '账户管理', '', 1, 1, 61, '', 'account', 'account', '/system/account/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(64, 1, '添加账号', '', 64, 2, 7, '', '', '', '', '', 'add', 0, 0, 0, 0, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(68, 1, '个人中心', '', 2, 0, 0, 'icon-user', '/user', 'user', 'LAYOUT', '/user/info', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(69, 1, '账号信息', '', 0, 1, 68, '', 'info', 'info', '/user/info/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(70, 1, '用户设置', '', 0, 1, 68, '', 'setting', 'setting', '/user/setting/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(74, 14, '开发者', '', 5, 0, 0, 'icon-code', '/developer', 'developer', 'LAYOUT', '/developer/apidoc', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(75, 1, '接口文档', '', 2, 1, 74, '', 'http://localhost:8108/openapi/', 'devapi', '/developer/generatecode/index', '', '', 0, 1, 0, 1, 0, 0, 0, 0, '2025-07-11 07:06:21', '2025-07-15 15:02:12'),
(97, 1, '生成代码', '', 3, 1, 74, '', 'generatecode', 'generatecode', '/developer/generatecode/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(121, 1, '数据中心', '', 4, 0, 0, 'icon-storage', '/datacenter', 'datacenter', 'LAYOUT', '/datacenter/dictionary', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(123, 1, '字典数据', '', 1, 1, 121, '', 'data', 'data', '/datacenter/dictionary/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(137, 1, '附件管理', '', 2, 1, 121, '', 'attachment', 'attachment', 'datacenter/attachment/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(143, 1, '配置管理', '', 3, 1, 121, '', 'configuration', 'configuration', '/datacenter/configuration/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(374, 1, '代码生成器', '', 1, 1, 74, '', 'codemaker', 'codemaker', '/developer/generatecode/codemaker.vue', '', '', 0, 0, 0, 1, 1, 0, 0, 1, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(435, 1, '测试代码产品', '', 1, 1, 383, 'icon-sun-fill', 'product', 'product', 'makecode/product/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(436, 1, '测试代码产品分类', '', 2, 1, 383, '', 'cate', 'cate', 'makecode/cate/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(437, 1, '修改状态', '', 4, 2, 63, '', '', '', '', '', 'account:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(438, 1, '基本权限', '', 1, 2, 63, '', '', '', '', '', 'account:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(439, 1, '编辑', '', 2, 2, 63, '', '', '', '', '', 'account:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(440, 1, '删除', '', 3, 2, 63, '', '', '', '', '', 'account:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(442, 1, '基本权限', '', 1, 2, 11, '', '', '', '', '', 'role:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(443, 1, '基本权限', '', 1, 2, 13, '', '', '', '', '', 'dept:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(444, 1, '基本权限', '', 1, 2, 12, '', '', '', '', '', 'rule:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(445, 1, '基本权限', '', 1, 2, 123, '', '', '', '', '', 'dict:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(446, 1, '基本权限', '', 1, 2, 137, '', '', '', '', '', 'atta:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(447, 1, '基本权限', '', 1, 2, 143, '', '', '', '', '', 'config:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(450, 1, '修改状态', '', 4, 2, 11, '', '', '', '', '', 'role:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(451, 1, '编辑', '', 2, 2, 11, '', '', '', '', '', 'role:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(452, 1, '删除', '', 3, 2, 11, '', '', '', '', '', 'role:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(453, 1, '修改状态', '', 4, 2, 13, '', '', '', '', '', 'dept:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(454, 1, '编辑', '', 2, 2, 13, '', '', '', '', '', 'dept:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(455, 1, '删除', '', 3, 2, 13, '', '', '', '', '', 'dept:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(456, 1, '修改状态', '', 4, 2, 12, '', '', '', '', '', 'rule:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(457, 1, '编辑', '', 2, 2, 12, '', '', '', '', '', 'rule:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(458, 1, '删除', '', 3, 2, 12, '', '', '', '', '', 'rule:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(459, 1, '删除', '', 3, 2, 123, '', '', '', '', '', 'dict:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(460, 1, '编辑', '', 2, 2, 123, '', '', '', '', '', 'dict:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(461, 1, '修改状态', '', 4, 2, 123, '', '', '', '', '', 'dict:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(462, 1, '添加', '', 2, 2, 137, '', '', '', '', '', 'atta:add', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(463, 1, '删除', '', 3, 2, 137, '', '', '', '', '', 'atta:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(464, 1, '基本权限', '', 1, 2, 97, '', '', '', '', '', 'gen:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(465, 1, '声纹注册', '', 1, 1, 466, '', '/voice/print', 'print', '/voice/print/index.vue', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-13 10:16:36', '2025-07-11 18:19:45'),
(466, 1, '声纹管理', '', 6, 0, 0, 'icon-idcard', '/voice', 'voice', 'LAYOUT', '/voice', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-12 10:17:52', '2025-07-11 18:19:32'),
(800, 1, '语音能力', '', 20, 0, 0, 'icon-sound', '/voice', 'voice2', 'LAYOUT', '/voice/identify', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-31 00:00:00', '2025-07-31 00:00:00'),
(801, 1, '实时语音识别', '', 1, 1, 800, '', '/voice/identify', 'voiceIdentify', '/voice/identify/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-31 00:00:00', '2025-07-31 00:00:00'),
(802, 1, '在线语音识别', '', 2, 1, 800, '', '/voice/identify/online', 'voiceIdentifyOnline', '/voice/identify/online', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-31 00:00:00', '2025-07-31 00:00:00'),
(803, 1, '离线语音识别', '', 3, 1, 800, '', '/voice/identify/offline', 'voiceIdentifyOffline', '/voice/identify/offline', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-31 00:00:00', '2025-07-31 00:00:00'),
(479, 1, '实时语音识别', '', 2, 1, 466, 'icon-mic', '/voice/identify', 'voice_identify', '/voice/identify/index.vue', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-09-06 10:00:00', '2025-09-06 10:00:00'),
(467, 1, '添加', '', 1, 2, 465, '', '', '', '', '', 'print:add', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-14 12:16:20', '2025-07-14 12:16:20'),
(468, 1, '删除', '', 2, 2, 465, '', '', '', '', '', 'print:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-14 20:16:32', '2025-07-14 12:16:36'),
(469, 1, '会议管理','',7,0,0,'icon-user-group','/meeting','meeting','LAYOUT','/meeting','',0,0,0,1,0,0,0,0,'2025-07-25 22:14:50','2025-07-25 22:14:50'),
(470, 1, '离线会议','',1,1,469,'','/meeting/offline','meeting_offline','/meeting/offline/index.vue','','',0,0,0,1,0,0,0,0,'2025-07-25 22:15:55','2025-07-25 22:15:55'),
(471, 1, '基础权限','',1,2,465,'','','','','','print:base',0,0,0,1,0,0,0,0,'2025-07-25 22:16:34','2025-07-25 22:16:34'),
(472, 1, '基础权限','',1,2,470,'','','','','','meeting:offline:base',0,0,0,1,0,0,0,0,'2025-07-25 22:17:02','2025-07-25 22:17:02'),
(473, 1, '编辑','',2,2,470,'','','','','','meeting:offline:edit',0,0,0,1,0,0,0,0,'2025-07-26 06:17:17','2025-07-25 22:17:45'),
(474, 1, '删除','',3,2,470,'','','','','','meeting:offline:del',0,0,0,1,0,0,0,0,'2025-07-25 22:17:31','2025-07-25 22:17:31'),
(475, 1, '会议详情','',4,2,470,'','','','','','meeting:offline:detail',0,0,0,1,0,0,0,0,'2025-07-25 22:18:25','2025-07-25 22:18:25'),
(476, 1, '会议详情-编辑','',5,2,470,'','','','','','meeting:offline:detail:edit',0,0,0,1,0,0,0,0,'2025-07-25 22:19:01','2025-07-25 22:19:01'),
(477, 1, '会议详情-编辑训练状态','',6,2,470,'','','','','','meeting:offline:detail:edit_train',0,0,0,1,0,0,0,0,'2025-07-26 06:20:33','2025-07-25 22:20:56'),
(478, 1, '会议详情-导出','',7,2,470,'','','','','','meeting:offline:detail:export',0,0,0,1,0,0,0,0,'2025-07-26 06:21:49','2025-07-25 22:27:11');

SELECT setval('business_auth_rule_id_seq', (SELECT max(id) FROM business_auth_rule));
COMMIT;

-- ----------------------------
-- Table structure: business_home_quickop 
-- ----------------------------
DROP TABLE IF EXISTS "business_home_quickop";
CREATE TABLE "business_home_quickop" (
 "id" bigserial NOT NULL,
 "uid" int8 NOT NULL DEFAULT 0,
 "is_common" int2 NOT NULL DEFAULT 0,
 "type" int2 NOT NULL DEFAULT 0,
 "name" varchar(50) NOT NULL,
 "path_url" varchar(50) NOT NULL,
 "icon" varchar(50) NOT NULL,
 "weigh" int8 NOT NULL DEFAULT 0, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "business_home_quickop" IS '首页快捷操作';
COMMENT ON COLUMN "business_home_quickop"."uid" IS '添加人';
COMMENT ON COLUMN "business_home_quickop"."is_common" IS '公共1=是';
COMMENT ON COLUMN "business_home_quickop"."type" IS '类型1=外部';
COMMENT ON COLUMN "business_home_quickop"."name" IS '快捷名称';
COMMENT ON COLUMN "business_home_quickop"."path_url" IS '跳转路径';
COMMENT ON COLUMN "business_home_quickop"."icon" IS '图标';
COMMENT ON COLUMN "business_home_quickop"."weigh" IS '权重';

-- ----------------------------
-- Data: business_home_quickop 
-- ----------------------------
BEGIN;
INSERT INTO "business_home_quickop" ("id", "uid", "is_common", "type", "name", "path_url", "icon", "weigh") VALUES 
(1, 1, 0, 0, '文档接口', 'devapi', 'icon-common', 1),
(2, 1, 0, 0, '生成代码', 'generatecode', 'icon-mobile', 2);
SELECT setval('business_home_quickop_id_seq', (SELECT max(id) FROM business_home_quickop));
COMMIT;

-- ----------------------------
-- Table structure: common_apidoc_group 
-- ----------------------------
DROP TABLE IF EXISTS "common_apidoc_group";
CREATE TABLE "common_apidoc_group" (
 "id" bigserial NOT NULL,
 "type" varchar(20) NOT NULL DEFAULT 'admin',
 "pid" int8 NOT NULL DEFAULT 0,
 "name" varchar(50) NOT NULL,
 "status" int2 NOT NULL DEFAULT 0,
 "type_id" int8 NOT NULL DEFAULT 0, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_apidoc_group" IS '后台端接口测试分组';
COMMENT ON COLUMN "common_apidoc_group"."type" IS '分类接口属于那端，admin=管理，biz=B端，client=C端';
COMMENT ON COLUMN "common_apidoc_group"."pid" IS '父级0=一级';
COMMENT ON COLUMN "common_apidoc_group"."name" IS '分类名称';
COMMENT ON COLUMN "common_apidoc_group"."status" IS '状态1=禁用';
COMMENT ON COLUMN "common_apidoc_group"."type_id" IS '接口类型';

-- ----------------------------
-- Data: common_apidoc_group 
-- ----------------------------
BEGIN;
INSERT INTO "common_apidoc_group" ("id", "type", "pid", "name", "status", "type_id") VALUES 
(1, 'biz', 0, 'app端', 0, 3),
(2, 'biz', 0, '小程序', 0, 1),
(3, 'biz', 0, '后台管理', 0, 2),
(4, 'biz', 2, '小程序-疫苗计划', 0, 1);
SELECT setval('common_apidoc_group_id_seq', (SELECT max(id) FROM common_apidoc_group));
COMMIT;

-- ----------------------------
-- Table structure: common_apidoc_type 
-- ----------------------------
DROP TABLE IF EXISTS "common_apidoc_type";
CREATE TABLE "common_apidoc_type" (
 "id" bigserial NOT NULL,
 "name" varchar(50) NOT NULL,
 "rooturl" varchar(255) NOT NULL,
 "verifyEncrypt" varchar(80) NOT NULL,
 "isself" int2 NOT NULL DEFAULT 0,
 "user_tablename" varchar(50) NOT NULL,
 "user_id" int4 NOT NULL DEFAULT 0,
 "login_url" varchar(100) NOT NULL,
 "model_name" varchar(50) NOT NULL, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_apidoc_type" IS '接口类型';
COMMENT ON COLUMN "common_apidoc_type"."name" IS '类型名称';
COMMENT ON COLUMN "common_apidoc_type"."rooturl" IS '请求服务器地址';
COMMENT ON COLUMN "common_apidoc_type"."verifyEncrypt" IS '加密验证字符串';
COMMENT ON COLUMN "common_apidoc_type"."isself" IS '是否是本端1=是';
COMMENT ON COLUMN "common_apidoc_type"."user_tablename" IS '测试授权用户数据表名';
COMMENT ON COLUMN "common_apidoc_type"."user_id" IS '测试用户id';
COMMENT ON COLUMN "common_apidoc_type"."login_url" IS '登录地址';
COMMENT ON COLUMN "common_apidoc_type"."model_name" IS '模块目录';

-- ----------------------------
-- Data: common_apidoc_type 
-- ----------------------------
BEGIN;
INSERT INTO "common_apidoc_type" ("id", "name", "rooturl", "verifyEncrypt", "isself", "user_tablename", "user_id", "login_url", "model_name") VALUES 
(1, '小程序', 'https://yg.goflys.cn', 'gofly@888', 0, 'business_wxsys_user', 6, '/wxapp/user/get_apitoken', 'wxapp'),
(2, '本端', '', '', 1, '', 0, '', ''),
(3, '手机APP', 'https://yg.goflys.cn', 'gofly@888', 0, '', 0, '', '');
SELECT setval('common_apidoc_type_id_seq', (SELECT max(id) FROM common_apidoc_type));
COMMIT;

-- ----------------------------
-- Table structure: common_config 
-- ----------------------------
DROP TABLE IF EXISTS "common_config";
CREATE TABLE "common_config" (
 "id" bigserial NOT NULL,
 "keyname" varchar(255) NOT NULL,
 "keyvalue" varchar(255) NOT NULL,
 "des" varchar(255) NOT NULL,
 "weigh" int8 NOT NULL DEFAULT 0, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_config" IS '系统配置参数';
COMMENT ON COLUMN "common_config"."keyname" IS '配置名称';
COMMENT ON COLUMN "common_config"."keyvalue" IS '配置值';
COMMENT ON COLUMN "common_config"."des" IS '描述';
COMMENT ON COLUMN "common_config"."weigh" IS '排序';

-- ----------------------------
-- Data: common_config 
-- ----------------------------
BEGIN;
INSERT INTO "common_config" ("id", "keyname", "keyvalue", "des", "weigh") VALUES 
(2, 'rooturl', 'http://localhost:8108/common/uploadfile/get_image?url=', '图片路径', 0);
SELECT setval('common_config_id_seq', (SELECT max(id) FROM common_config));
COMMIT;

-- ----------------------------
-- Table structure: common_dictionary_data 
-- ----------------------------
DROP TABLE IF EXISTS "common_dictionary_data";
CREATE TABLE "common_dictionary_data" (
 "id" bigserial NOT NULL,
 "dic_id" int8,
 "keyname" varchar(100) NOT NULL,
 "keyvalue" varchar(255) NOT NULL,
 "des" varchar(80) NOT NULL,
 "status" int2 NOT NULL,
 "weigh" int8 NOT NULL DEFAULT 0,
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_dictionary_data" IS '字典数据-测试数据';
COMMENT ON COLUMN "common_dictionary_data"."dic_id" IS '字典id';
COMMENT ON COLUMN "common_dictionary_data"."keyname" IS '字典名称';
COMMENT ON COLUMN "common_dictionary_data"."keyvalue" IS '字典项值';
COMMENT ON COLUMN "common_dictionary_data"."des" IS '字典描述';
COMMENT ON COLUMN "common_dictionary_data"."status" IS '状态';
COMMENT ON COLUMN "common_dictionary_data"."weigh" IS '排序';
COMMENT ON COLUMN "common_dictionary_data"."create_time" IS '创建时间';
COMMENT ON COLUMN "common_dictionary_data"."update_time" IS '更新时间';

-- ----------------------------
-- Data: common_dictionary_data 
-- ----------------------------
BEGIN;
INSERT INTO "common_dictionary_data" ("id", "dic_id", "keyname", "keyvalue", "des", "status", "weigh", "create_time", "update_time") VALUES 
(1, 2, '管理层', 'mteam', '公司领导', 0, 1, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(2, 2, '业务员', 'salesman', '', 0, 2, '2025-07-10 15:06:21', '2025-07-10 15:06:21');
SELECT setval('common_dictionary_data_id_seq', (SELECT max(id) FROM common_dictionary_data));
COMMIT;

-- ----------------------------
-- Table structure: common_dictionary_table 
-- ----------------------------
DROP TABLE IF EXISTS "common_dictionary_table";
CREATE TABLE "common_dictionary_table" (
 "id" bigserial NOT NULL,
 "title" varchar(50) NOT NULL,
 "remark" varchar(200) NOT NULL,
 "tablename" varchar(50) NOT NULL,
 "status" int2 NOT NULL,
 "weigh" int8 NOT NULL DEFAULT 0,
 "create_time" timestamp, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_dictionary_table" IS '字典表';
COMMENT ON COLUMN "common_dictionary_table"."title" IS '字典名称';
COMMENT ON COLUMN "common_dictionary_table"."remark" IS '备注';
COMMENT ON COLUMN "common_dictionary_table"."tablename" IS '数据表名称';
COMMENT ON COLUMN "common_dictionary_table"."status" IS '状态';
COMMENT ON COLUMN "common_dictionary_table"."weigh" IS '排序';
COMMENT ON COLUMN "common_dictionary_table"."create_time" IS '创建时间';

-- ----------------------------
-- Data: common_dictionary_table 
-- ----------------------------
BEGIN;
INSERT INTO "common_dictionary_table" ("id", "title", "remark", "tablename", "status", "weigh", "create_time") VALUES 
(2, '用户分组', '用户分组', 'common_dictionary_data', 0, 2, '2025-07-10 15:06:21'),
(3, 'test', '', 'common_dictionary_data', 0, 3, '2025-07-10 15:06:21');
SELECT setval('common_dictionary_table_id_seq', (SELECT max(id) FROM common_dictionary_table));
COMMIT;

-- ----------------------------
-- Table structure: common_email 
-- ----------------------------
DROP TABLE IF EXISTS "common_email";
CREATE TABLE "common_email" (
 "id" bigserial NOT NULL,
 "sender_email" varchar(50) NOT NULL,
 "auth_code" varchar(50) NOT NULL,
 "mail_title" varchar(80) NOT NULL,
 "mail_body" text NOT NULL,
 "service_host" varchar(30) NOT NULL,
 "service_port" int8 NOT NULL DEFAULT 0, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_email" IS '业务端邮箱';
COMMENT ON COLUMN "common_email"."sender_email" IS '发送者邮箱';
COMMENT ON COLUMN "common_email"."auth_code" IS '邮箱授权码';
COMMENT ON COLUMN "common_email"."mail_title" IS '邮件标题';
COMMENT ON COLUMN "common_email"."mail_body" IS '邮件内容,可以是html';
COMMENT ON COLUMN "common_email"."service_host" IS '邮件服务器';
COMMENT ON COLUMN "common_email"."service_port" IS '邮件服务器端口';

-- ----------------------------
-- Data: common_email 
-- ----------------------------
BEGIN;
INSERT INTO "common_email" ("id", "sender_email", "auth_code", "mail_title", "mail_body", "service_host", "service_port") VALUES 
(1, '504500934@qq.com', 'amidmyjnnxy(youwkey)', 'GoFly验证码', '你的验证码为：{code}', 'smtp.qq.com', 587),
(2, '504500934@qq.com', 'amidmyjnnxy(youkey)', 'GoFly验证码', '你的验证码为：{code}', 'smtp.qq.com', 587);
SELECT setval('common_email_id_seq', (SELECT max(id) FROM common_email));
COMMIT;

-- ----------------------------
-- Table structure: common_generatecode 
-- ----------------------------
DROP TABLE IF EXISTS "common_generatecode";
CREATE TABLE "common_generatecode" (
 "id" bigserial NOT NULL,
 "tablename" varchar(50) NOT NULL,
 "comment" varchar(100) NOT NULL,
 "engine" varchar(50) NOT NULL,
 "table_rows" int8 NOT NULL DEFAULT 0,
 "collation" varchar(50) NOT NULL,
 "auto_increment" int8 NOT NULL DEFAULT 1,
 "status" int2 NOT NULL DEFAULT 0,
 "pid" int8 NOT NULL DEFAULT 0,
 "icon" varchar(50),
 "routePath" varchar(255),
 "routeName" varchar(100),
 "component" varchar(100),
 "api_path" varchar(60),
 "api_filename" varchar(50),
 "fields" text,
 "rule_id" int8 NOT NULL DEFAULT 0,
 "rule_name" varchar(30) NOT NULL,
 "is_install" int2 NOT NULL DEFAULT 0,
 "tpl_type" varchar(20) NOT NULL DEFAULT 'list',
 "cate_tablename" varchar(50),
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_generatecode" IS '代码生成';
COMMENT ON COLUMN "common_generatecode"."tablename" IS '表名称';
COMMENT ON COLUMN "common_generatecode"."comment" IS '表备注';
COMMENT ON COLUMN "common_generatecode"."engine" IS '引擎';
COMMENT ON COLUMN "common_generatecode"."table_rows" IS '记录数';
COMMENT ON COLUMN "common_generatecode"."collation" IS '编码';
COMMENT ON COLUMN "common_generatecode"."auto_increment" IS '自增索引';
COMMENT ON COLUMN "common_generatecode"."status" IS '状态1=禁用';
COMMENT ON COLUMN "common_generatecode"."pid" IS '菜单上级';
COMMENT ON COLUMN "common_generatecode"."icon" IS '图标';
COMMENT ON COLUMN "common_generatecode"."routePath" IS '路由地址';
COMMENT ON COLUMN "common_generatecode"."routeName" IS '路由名称';
COMMENT ON COLUMN "common_generatecode"."component" IS '组件路径';
COMMENT ON COLUMN "common_generatecode"."api_path" IS '后端业务接口';
COMMENT ON COLUMN "common_generatecode"."api_filename" IS '后端文件名';
COMMENT ON COLUMN "common_generatecode"."fields" IS '查询字段';
COMMENT ON COLUMN "common_generatecode"."rule_id" IS '生成菜单id';
COMMENT ON COLUMN "common_generatecode"."rule_name" IS '菜单名称';
COMMENT ON COLUMN "common_generatecode"."is_install" IS '是否安装0=未安装，1=已安装，2=已卸载';
COMMENT ON COLUMN "common_generatecode"."tpl_type" IS '模板类型list=仅一个数据，cate=数据加分类';
COMMENT ON COLUMN "common_generatecode"."cate_tablename" IS '分类表名称';
COMMENT ON COLUMN "common_generatecode"."create_time" IS '创建时间';
COMMENT ON COLUMN "common_generatecode"."update_time" IS '更新时间';

-- ----------------------------
-- Data: common_generatecode 
-- ----------------------------
BEGIN;
INSERT INTO "common_generatecode" ("id", "tablename", "comment", "engine", "table_rows", "collation", "auto_increment", "status", "pid", "icon", "routePath", "routeName", "component", "api_path", "api_filename", "fields", "rule_id", "rule_name", "is_install", "tpl_type", "cate_tablename", "create_time", "update_time") VALUES 
(1, 'admin_auth_dept', '管理后台部门', 'InnoDB', 5, 'utf8mb4_general_ci', 6, 1, 0, '', '', '', '', '', '', '', 0, '管理后台部门', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(2, 'admin_auth_role', '权限分组', 'InnoDB', 8, 'utf8mb4_general_ci', 16, 1, 0, '', '', '', '', '', '', '', 0, '权限分组', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(3, 'admin_auth_role_access', 'admin端菜单权限', 'InnoDB', 6, 'utf8mb4_general_ci', 0, 1, 0, '', '', '', '', '', '', '', 0, 'admin端菜单权限', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(4, 'admin_auth_rule', 'C端-菜单', 'InnoDB', 22, 'utf8mb4_general_ci', 80, 1, 0, '', '', '', '', '', '', '', 0, 'C端-菜单', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(6, 'attachment', '附件管理', 'InnoDB', 20, 'utf8mb4_general_ci', 744, 1, 0, '', '', '', '', '', '', '', 0, '附件管理', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(7, 'business_attachment', '客户端附件', 'InnoDB', 63, 'utf8mb4_general_ci', 108, 1, 0, '', '', '', '', '', '', '', 0, '客户端附件', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(8, 'business_auth_dept', '管理后台部门', 'InnoDB', 5, 'utf8mb4_general_ci', 7, 1, 0, '', '', '', '', '', '', '', 0, '管理后台部门', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(9, 'business_auth_role', '权限分组', 'InnoDB', 15, 'utf8mb4_general_ci', 21, 1, 0, '', '', '', '', '', '', '', 0, '权限分组', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(10, 'business_auth_role_access', '用户角色授权', 'InnoDB', 11, 'utf8mb4_general_ci', 0, 1, 0, '', '', '', '', '', '', '', 0, '商务端菜单授权', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(11, 'business_auth_rule', 'C端-菜单', 'InnoDB', 47, 'utf8mb4_general_ci', 435, 1, 0, '', '', '', '', '', '', '', 0, 'C端-菜单', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(16, 'business_home_quickop', '首页快捷操作', 'InnoDB', 2, 'utf8mb4_general_ci', 4, 1, 0, '', '', '', '', '', '', '', 0, '首页快捷操作', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(18, 'business_wxsys_officonfig', '微信公众号配置', 'InnoDB', 2, 'utf8mb4_general_ci', 6, 1, 0, '', '', '', '', '', '', '', 0, '微信公众号配置', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(19, 'business_wxsys_user', '微信关注用户', 'InnoDB', 0, 'utf8mb4_general_ci', 0, 1, 0, '', '', '', '', '', '', '', 0, '微信关注用户', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(20, 'business_wxsys_wxappconfig', '微信小程序配置', 'InnoDB', 2, 'utf8mb4_general_ci', 6, 1, 0, '', '', '', '', '', '', '', 0, '微信小程序配置', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(21, 'business_wxsys_wxmenu', '微站微信菜单', 'InnoDB', 2, 'utf8mb4_general_ci', 13, 1, 0, '', '', '', '', '', '', '', 0, '微站微信菜单', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(25, 'common_config', '系统配置参数', 'InnoDB', 1, 'utf8mb4_general_ci', 3, 1, 0, '', '', '', '', '', '', '', 0, '系统配置参数', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(26, 'common_dictionary_data', '字典数据-测试数据', 'InnoDB', 2, 'utf8mb4_general_ci', 2, 1, 0, '', '', '', '', '', '', '', 0, '字典数据-测试数据', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(27, 'common_dictionary_integral', '积分等级-测试数据', 'InnoDB', 3, 'utf8mb4_general_ci', 3, 1, 0, '', '', '', '', '', '', '', 0, '', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(28, 'common_dictionary_table', '字典表', 'InnoDB', 2, 'utf8mb4_general_ci', 2, 1, 0, '', '', '', '', '', '', '', 0, '字典表', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(29, 'common_email', '业务端邮箱', 'InnoDB', 2, 'utf8mb4_general_ci', 2, 1, 0, '', '', '', '', '', '', '', 0, '业务端邮箱', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(30, 'common_generatecode', '代码生成', 'InnoDB', 45, 'utf8mb4_general_ci', 61, 1, 0, '', '', '', '', '', '', '', 0, '代码生成', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(31, 'common_logininfo', '登录页面内容', 'InnoDB', 3, 'utf8mb4_general_ci', 4, 1, 0, '', '', '', '', '', '', '', 0, '登录页面内容', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(32, 'common_message', '系统通用消息', 'InnoDB', 0, 'utf8mb4_general_ci', 0, 1, 0, '', '', '', '', '', '', '', 0, '系统通用消息', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(33, 'common_picture', '图片库', 'InnoDB', 4, 'utf8mb4_general_ci', 8, 1, 0, '', '', '', '', '', '', '', 0, '图片库', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(34, 'common_picture_cate', '分类名称', 'InnoDB', 27, 'utf8mb4_general_ci', 27, 1, 0, '', '', '', '', '', '', '', 0, '分类名称', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(35, 'common_verify_code', '验证码存储', 'InnoDB', 1, 'utf8mb4_general_ci', 1, 1, 0, '', '', '', '', '', '', '', 0, '验证码存储', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(36, 'login_logs', '（平台及客户）后台登录日志', 'InnoDB', 31, 'utf8mb4_general_ci', 976, 1, 0, '', '', '', '', '', '', '', 0, '（平台及客户）后台登录日志', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(41, 'business_email', '业务端邮箱', 'InnoDB', 0, 'utf8mb4_general_ci', 1, 1, 0, '', '', '', '', '', '', '', 0, '', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(42, 'admin_account', '用户端-用户信息', 'InnoDB', 4, 'utf8mb4_general_ci', 9, 1, 0, '', '', '', '', '', '', '', 0, '用户端-用户信息', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(43, 'business_account', '用户端-用户信息', 'InnoDB', 2, 'utf8mb4_general_ci', 14, 1, 0, '', '', '', '', '', '', '', 0, '用户端-用户信息', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(44, 'common_apidoc', '接口测试数据', 'InnoDB', 4, 'utf8mb4_general_ci', 19, 1, 0, '', '', '', '', '', '', '', 0, '接口测试数据', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(45, 'common_apidoc_group', '后台端接口测试分组', 'InnoDB', 4, 'utf8mb4_general_ci', 5, 1, 0, '', '', '', '', '', '', '', 0, '后台端接口测试分组', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(46, 'common_apidoc_type', '接口类型', 'InnoDB', 3, 'utf8mb4_general_ci', 4, 1, 0, '', '', '', '', '', '', '', 0, '接口类型', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(51, 'createcode_product', '测试代码产品', 'InnoDB', 2, 'utf8mb4_general_ci', 4, 0, 383, 'icon-sun-fill', 'product', 'product', 'makecode/product/index', 'business/makecode', 'product.go', 'id,title,price,num,createtime', 435, '测试代码产品', 1, 'contentlist', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(52, 'common_generatecode_field', '生成代码字段管理', 'InnoDB', 30, 'utf8mb4_general_ci', 45, 1, 0, '', '', '', '', '', '', '', 0, '生成代码字段管理', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(53, 'createcode_product_cate', '测试代码产品分类', 'InnoDB', 0, 'utf8mb4_general_ci', 0, 0, 383, '', 'cate', 'cate', 'makecode/cate/index', 'business/makecode', 'cate.go', '', 436, '测试代码产品分类', 1, 'list', 'createcode_product_cate', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(54, 'business_website_article_cate', '网站管理-文章分类', 'InnoDB', 15, 'utf8mb4_general_ci', 21, 1, 0, '', '', '', '', '', '', '', 0, '网站管理-文章分类', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(55, 'business_website_article_content', '网站管理-文章内容', 'InnoDB', 11, 'utf8mb4_general_ci', 24, 1, 0, '', '', '', '', '', '', '', 0, '网站管理-文章内容', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(56, 'business_website_leavemessage', '网站管理-留言', 'InnoDB', 4, 'utf8mb4_general_ci', 23, 1, 0, '', '', '', '', '', '', '', 0, '网站管理-留言', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(57, 'business_website_link', '网站-友情链接', 'InnoDB', 2, 'utf8mb4_general_ci', 3, 1, 0, '', '', '', '', '', '', '', 0, '网站-友情链接', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(58, 'business_website_module', '网站模块', 'InnoDB', 7, 'utf8mb4_general_ci', 9, 1, 0, '', '', '', '', '', '', '', 0, '网站模块', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(59, 'business_website_site', '网站管理-站点', 'InnoDB', 0, 'utf8mb4_general_ci', 1, 1, 0, '', '', '', '', '', '', '', 0, '网站管理-站点', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(60, 'business_website_visit_record', '网站访问记录', 'InnoDB', 302, 'utf8mb4_general_ci', 1780, 1, 0, '', '', '', '', '', '', '', 0, '', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(61, 'voice_document', '', '', 0, '', 1, 0, 0, '', '', '', '', '', '', '', 0, '', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02'),
(62, 'voice_print', '', '', 0, '', 1, 0, 0, '', '', '', '', '', '', '', 0, '', 0, 'list', '', '2025-07-10 15:06:21', '2025-07-18 11:25:02');
SELECT setval('common_generatecode_id_seq', (SELECT max(id) FROM common_generatecode));
COMMIT;

-- ----------------------------
-- Table structure: common_generatecode_field 
-- ----------------------------
DROP TABLE IF EXISTS "common_generatecode_field";
CREATE TABLE "common_generatecode_field" (
 "id" bigserial NOT NULL,
 "generatecode_id" int4 NOT NULL,
 "islist" int2 NOT NULL DEFAULT 0,
 "name" varchar(50) NOT NULL,
 "field" varchar(50) NOT NULL,
 "isorder" int2 NOT NULL DEFAULT 0,
 "align" varchar(10) NOT NULL DEFAULT 'left',
 "width" int4 NOT NULL DEFAULT 0,
 "isform" int2 NOT NULL DEFAULT 0,
 "required" int2 NOT NULL DEFAULT 0,
 "formtype" varchar(15) NOT NULL,
 "datatable" varchar(30) NOT NULL,
 "datatablename" varchar(30) NOT NULL,
 "issearch" int2 NOT NULL DEFAULT 0,
 "searchway" varchar(15) NOT NULL DEFAULT '=',
 "searchtype" varchar(30) NOT NULL,
 "field_weigh" int4 NOT NULL,
 "list_weigh" int4 NOT NULL,
 "search_weigh" int4 NOT NULL DEFAULT 0,
 "def_value" varchar(255) NOT NULL, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_generatecode_field" IS '生成代码字段管理';
COMMENT ON COLUMN "common_generatecode_field"."generatecode_id" IS '关联列表';
COMMENT ON COLUMN "common_generatecode_field"."islist" IS '是否是列表1=是';
COMMENT ON COLUMN "common_generatecode_field"."name" IS '字段名称';
COMMENT ON COLUMN "common_generatecode_field"."field" IS '字段';
COMMENT ON COLUMN "common_generatecode_field"."isorder" IS '是否参与排序';
COMMENT ON COLUMN "common_generatecode_field"."align" IS '对齐方向';
COMMENT ON COLUMN "common_generatecode_field"."width" IS '宽度';
COMMENT ON COLUMN "common_generatecode_field"."isform" IS '是否为表单字段';
COMMENT ON COLUMN "common_generatecode_field"."required" IS '是否为必填项';
COMMENT ON COLUMN "common_generatecode_field"."formtype" IS '表单类型';
COMMENT ON COLUMN "common_generatecode_field"."datatable" IS '关联数据表';
COMMENT ON COLUMN "common_generatecode_field"."datatablename" IS '关联显示字段';
COMMENT ON COLUMN "common_generatecode_field"."issearch" IS '是否查询';
COMMENT ON COLUMN "common_generatecode_field"."searchway" IS '查询方式';
COMMENT ON COLUMN "common_generatecode_field"."searchtype" IS '查询文本类型';
COMMENT ON COLUMN "common_generatecode_field"."field_weigh" IS '表单排序';
COMMENT ON COLUMN "common_generatecode_field"."list_weigh" IS '列表排序';
COMMENT ON COLUMN "common_generatecode_field"."search_weigh" IS '搜索排序';
COMMENT ON COLUMN "common_generatecode_field"."def_value" IS '默认选项json';

-- ----------------------------
-- Data: common_generatecode_field 
-- ----------------------------
BEGIN;
INSERT INTO "common_generatecode_field" ("id", "generatecode_id", "islist", "name", "field", "isorder", "align", "width", "isform", "required", "formtype", "datatable", "datatablename", "issearch", "searchway", "searchtype", "field_weigh", "list_weigh", "search_weigh", "def_value") VALUES 
(37, 51, 1, 'ID', 'id', 1, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 1, 1, 1, '[]'),
(38, 51, 1, '标题1', 'title', 1, 'center', 200, 1, 1, 'text', '', '', 0, '=', 'text', 2, 2, 2, '[]'),
(39, 51, 1, '库存', 'num', 1, 'left', 0, 1, 1, 'number', '', '', 1, '=', 'text', 4, 5, 4, '[]'),
(40, 51, 1, '价格', 'price', 0, 'left', 0, 1, 0, 'number', 'business_auth_dept', 'pid', 0, '=', 'text', 3, 4, 3, '[]'),
(41, 51, 0, '内容', 'content', 1, 'left', 220, 1, 1, 'editor', 'business_auth_role', 'data_access', 0, '=', 'text', 5, 3, 5, '[]'),
(42, 51, 1, '上传时间', 'createtime', 0, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 6, 6, 6, '[]'),
(43, 50, 0, 'ID', 'id', 1, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 0, 0, 0, '[]'),
(44, 50, 0, '名称', 'name', 0, 'left', 0, 0, 0, 'text', '', '', 0, '=', 'text', 0, 0, 0, '[]'),
(45, 50, 0, '上传时间', 'createtime', 0, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 0, 0, 0, '[]'),
(49, 62, 0, '主键ID', 'id', 1, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 1, 1, 1, '[]'),
(50, 62, 0, '创建人ID', 'creator_id', 0, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 2, 2, 2, '[]'),
(51, 62, 0, '创建人名称', 'creator_name', 0, 'left', 0, 0, 0, 'text', '', '', 0, '=', 'text', 3, 3, 3, '[]'),
(52, 62, 0, '创建时间', 'create_time', 0, 'left', 0, 0, 0, 'time', '', '', 0, '=', 'text', 4, 4, 4, '[]'),
(53, 62, 0, '更新人ID', 'updater_id', 0, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 5, 5, 5, '[]'),
(54, 62, 0, '更新人名称', 'updater_name', 0, 'left', 0, 0, 0, 'text', '', '', 0, '=', 'text', 6, 6, 6, '[]'),
(55, 62, 0, '更新时间', 'update_time', 0, 'left', 0, 0, 0, 'time', '', '', 0, '=', 'text', 7, 7, 7, '[]'),
(56, 62, 0, '是否删除', 'deleted', 0, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 8, 8, 8, '[]'),
(57, 62, 0, '删除时间', 'deleted_at', 0, 'left', 0, 0, 0, 'text', '', '', 0, '=', 'text', 9, 9, 9, '[]'),
(58, 62, 0, '用户ID', 'user_id', 0, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 10, 10, 10, '[]'),
(59, 62, 0, '用户名', 'user_name', 0, 'left', 0, 0, 0, 'text', '', '', 0, '=', 'text', 11, 11, 11, '[]'),
(60, 62, 0, '声纹ID', 'print_id', 0, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 12, 12, 12, '[]'),
(61, 61, 0, '主键ID', 'id', 1, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 1, 1, 1, '[]'),
(62, 61, 0, '创建人ID', 'creator_id', 0, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 2, 2, 2, '[]'),
(63, 61, 0, '创建人名称', 'creator_name', 0, 'left', 0, 0, 0, 'text', '', '', 0, '=', 'text', 3, 3, 3, '[]'),
(64, 61, 0, '创建时间', 'create_time', 0, 'left', 0, 0, 0, 'time', '', '', 0, '=', 'text', 4, 4, 4, '[]'),
(65, 61, 0, '更新人ID', 'updater_id', 0, 'left', 0, 0, 0, 'number', '', '', 0, '=', 'text', 5, 5, 5, '[]'),
(66, 61, 0, '更新人名称', 'updater_name', 0, 'left', 0, 0, 0, 'text', '', '', 0, '=', 'text', 6, 6, 6, '[]'),
(67, 61, 0, '更新时间', 'update_time', 0, 'left', 0, 0, 0, 'time', '', '', 0, '=', 'text', 7, 7, 7, '[]'),
(68, 61, 0, '范文名', 'name', 0, 'left', 0, 0, 0, 'text', '', '', 0, '=', 'text', 8, 8, 8, '[]'),
(69, 61, 0, '范文内容', 'content', 0, 'left', 0, 0, 0, 'textarea', '', '', 0, '=', 'text', 9, 9, 9, '[]');
SELECT setval('common_generatecode_field_id_seq', (SELECT max(id) FROM common_generatecode_field));
COMMIT;

-- ----------------------------
-- Table structure: common_logininfo 
-- ----------------------------
DROP TABLE IF EXISTS "common_logininfo";
CREATE TABLE "common_logininfo" (
 "id" bigserial NOT NULL,
 "type" varchar(20) NOT NULL DEFAULT 'common',
 "title" varchar(80) NOT NULL,
 "des" varchar(255) NOT NULL,
 "image" varchar(145) NOT NULL,
 "status" int2 NOT NULL,
 "weigh" int8 NOT NULL DEFAULT 0,
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_logininfo" IS '登录页面内容';
COMMENT ON COLUMN "common_logininfo"."type" IS 'admin=管理端，business=商业端 common=公共';
COMMENT ON COLUMN "common_logininfo"."title" IS '标题';
COMMENT ON COLUMN "common_logininfo"."des" IS '描述';
COMMENT ON COLUMN "common_logininfo"."image" IS '图片';
COMMENT ON COLUMN "common_logininfo"."status" IS '状态';
COMMENT ON COLUMN "common_logininfo"."weigh" IS '排序';
COMMENT ON COLUMN "common_logininfo"."create_time" IS '创建时间';
COMMENT ON COLUMN "common_logininfo"."update_time" IS '更新时间';

-- ----------------------------
-- Data: common_logininfo 
-- ----------------------------
BEGIN;
INSERT INTO "common_logininfo" ("id", "type", "title", "des", "image", "status", "weigh", "create_time", "update_time") VALUES 
(1, 'common', '智能语音识别', '基于深度学习的端到端语音识别引擎，支持实时流式识别与离线转写，识别准确率领先业界水平。', '/common/uploadfile/get_image?url=resource/uploads/20230607/f1fbf7039464d632d9b5fcecb1e41fab.png', 0, 1, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(2, 'common', '声纹识别管理', '精准的声纹特征提取与比对技术，一次注册即可实现说话人身份识别，广泛应用于身份验证场景。', '/common/uploadfile/get_image?url=resource/uploads/20230607/4825b3bc4721d2e6266b9696f47b23c5.png', 0, 2, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(3, 'common', '智能会议转写', '支持多人会议的语音转文字与说话人分离，自动识别发言人并生成结构化会议纪要。', '/common/uploadfile/get_image?url=resource/uploads/20230607/33926ec2fcbc2da95e9cae158e00019e.png', 0, 3, '2025-07-10 15:06:21', '2025-07-10 15:06:21');
SELECT setval('common_logininfo_id_seq', (SELECT max(id) FROM common_logininfo));
COMMIT;

-- ----------------------------
-- Table structure: common_message 
-- ----------------------------
DROP TABLE IF EXISTS "common_message";
CREATE TABLE "common_message" (
 "id" bigserial NOT NULL,
 "adduid" int8 NOT NULL DEFAULT 0,
 "touid" int8 NOT NULL DEFAULT 0,
 "type" int2 NOT NULL DEFAULT 2,
 "title" varchar(255) NOT NULL,
 "path" varchar(255) NOT NULL,
 "content" text NOT NULL,
 "isread" int2 NOT NULL DEFAULT 0,
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_message" IS '系统通用消息';
COMMENT ON COLUMN "common_message"."adduid" IS '添加用户';
COMMENT ON COLUMN "common_message"."touid" IS '接收用户';
COMMENT ON COLUMN "common_message"."type" IS '类型1=通知，2=消息，3=代办';
COMMENT ON COLUMN "common_message"."title" IS '消息标题';
COMMENT ON COLUMN "common_message"."path" IS '跳转路由';
COMMENT ON COLUMN "common_message"."content" IS '消息内容';
COMMENT ON COLUMN "common_message"."isread" IS '是否已读1=已读';
COMMENT ON COLUMN "common_message"."create_time" IS '创建时间';
COMMENT ON COLUMN "common_message"."update_time" IS '更新时间';

-- ----------------------------
-- Data: common_message 
-- ----------------------------
BEGIN;
SELECT setval('common_message_id_seq', (SELECT max(id) FROM common_message));
COMMIT;

-- ----------------------------
-- Table structure: common_picture 
-- ----------------------------
DROP TABLE IF EXISTS "common_picture";
CREATE TABLE "common_picture" (
 "id" bigserial NOT NULL,
 "uid" int8 NOT NULL DEFAULT 0,
 "cid" int8 NOT NULL DEFAULT 0,
 "weigh" int8 NOT NULL DEFAULT 0,
 "name" varchar(50) NOT NULL,
 "title" varchar(50) NOT NULL,
 "type" int2 NOT NULL DEFAULT 0,
 "url" varchar(255) NOT NULL,
 "imagewidth" varchar(30) NOT NULL,
 "imageheight" varchar(30) NOT NULL,
 "filesize" int4 NOT NULL DEFAULT 0,
 "mimetype" varchar(100) NOT NULL,
 "storage" varchar(500) NOT NULL DEFAULT 'local',
 "cover_url" varchar(255) NOT NULL,
 "sha1" varchar(40) NOT NULL,
 "create_time" timestamp,
 "status" int2 NOT NULL DEFAULT 0, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_picture" IS '图片库';
COMMENT ON COLUMN "common_picture"."uid" IS '添加账号';
COMMENT ON COLUMN "common_picture"."cid" IS '分类id';
COMMENT ON COLUMN "common_picture"."weigh" IS '排序';
COMMENT ON COLUMN "common_picture"."name" IS '附件原来名称';
COMMENT ON COLUMN "common_picture"."title" IS '文件名称';
COMMENT ON COLUMN "common_picture"."type" IS '类型0=素材图1=插图,2=视频，3=音频';
COMMENT ON COLUMN "common_picture"."url" IS '访问路径';
COMMENT ON COLUMN "common_picture"."imagewidth" IS '宽度';
COMMENT ON COLUMN "common_picture"."imageheight" IS '高度';
COMMENT ON COLUMN "common_picture"."filesize" IS '文件大小';
COMMENT ON COLUMN "common_picture"."mimetype" IS 'mime类型';
COMMENT ON COLUMN "common_picture"."storage" IS '存储位置';
COMMENT ON COLUMN "common_picture"."cover_url" IS '视频封面';
COMMENT ON COLUMN "common_picture"."sha1" IS '文件 sha1编码';
COMMENT ON COLUMN "common_picture"."create_time" IS '创建时间';
COMMENT ON COLUMN "common_picture"."status" IS '状态1=禁用';

-- ----------------------------
-- Data: common_picture 
-- ----------------------------
BEGIN;
INSERT INTO "common_picture" ("id", "uid", "cid", "weigh", "name", "title", "type", "url", "imagewidth", "imageheight", "filesize", "mimetype", "storage", "cover_url", "sha1", "create_time", "status") VALUES 
(5, 1, 20, 5, 'GoFLy发布文章封面.png', 'GoFLy发布文章封面', 0, 'https://sg.goflys.cn/common/uploadfile/get_image?url=resource/uploads/20230609/00658402ef4e5ba229f3935eca6701d8.png', '', '', 40902, 'image/png', '/dataDB/project/go/gofly_singleresource\\uploads\\20230609\\00658402ef4e5ba229f3935eca6701d8.png', '', 'b98da546d168f3e1d91d32585aaf719e', '2025-07-10 15:06:21', 0),
(6, 1, 24, 6, '信息.png', '信息', 1, 'https://sg.goflys.cn/common/uploadfile/get_image?url=resource/uploads/20230609/46e5cc40453791e1db8c0e25a1c8ff9c.png', '', '', 65892, 'image/png', '/dataDB/project/go/gofly_singleresource\\uploads\\20230609\\46e5cc40453791e1db8c0e25a1c8ff9c.png', '', 'd58b80c230362875af642143b6bd3a70', '2025-07-10 15:06:21', 0),
(7, 1, 25, 7, '宣传.png', '宣传', 1, 'https://sg.goflys.cn/common/uploadfile/get_image?url=resource/uploads/20230609/d43a77c266fd59f23b438a7204e80173.png', '', '', 42539, 'image/png', '/dataDB/project/go/gofly_singleresource\\uploads\\20230609\\d43a77c266fd59f23b438a7204e80173.png', '', 'a226b08471c634ebd11b4d32ac138176', '2025-07-10 15:06:21', 0),
(8, 1, 19, 8, 'sw1.jpg', 'sw1', 0, 'https://sg.goflys.cn/common/uploadfile/get_image?url=resource/uploads/20230609/c895e724853152e06b5915f046348808.jpg', '', '', 25384, 'image/jpeg', '/dataDB/project/go/gofly_singleresource\\uploads\\20230609\\c895e724853152e06b5915f046348808.jpg', '', '8a81b3c0d0f346d7a36a4573e7196408', '2025-07-10 15:06:21', 0);
SELECT setval('common_picture_id_seq', (SELECT max(id) FROM common_picture));
COMMIT;

-- ----------------------------
-- Table structure: common_picture_cate 
-- ----------------------------
DROP TABLE IF EXISTS "common_picture_cate";
CREATE TABLE "common_picture_cate" (
 "id" bigserial NOT NULL,
 "uid" int8 NOT NULL DEFAULT 0,
 "weigh" int8 NOT NULL DEFAULT 0,
 "type" int2 NOT NULL DEFAULT 0,
 "name" varchar(50) NOT NULL,
 "status" int2 NOT NULL DEFAULT 0,
 "remark" varchar(255) NOT NULL,
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_picture_cate" IS '分类名称';
COMMENT ON COLUMN "common_picture_cate"."uid" IS '添加账号';
COMMENT ON COLUMN "common_picture_cate"."weigh" IS '排序';
COMMENT ON COLUMN "common_picture_cate"."type" IS '类型0=素材图1=插图,2=两种共有';
COMMENT ON COLUMN "common_picture_cate"."name" IS '分类名称';
COMMENT ON COLUMN "common_picture_cate"."status" IS '状态1=禁用';
COMMENT ON COLUMN "common_picture_cate"."remark" IS '备注';
COMMENT ON COLUMN "common_picture_cate"."create_time" IS '创建时间';
COMMENT ON COLUMN "common_picture_cate"."update_time" IS '更新时间';

-- ----------------------------
-- Data: common_picture_cate 
-- ----------------------------
BEGIN;
INSERT INTO "common_picture_cate" ("id", "uid", "weigh", "type", "name", "status", "remark", "create_time", "update_time") VALUES 
(1, 1, 1, 0, '商务', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(2, 1, 2, 2, '科技', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(3, 1, 3, 0, '教育', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(4, 1, 4, 0, '风景', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(5, 1, 5, 0, '建筑', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(6, 1, 6, 2, '人物', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(7, 1, 7, 0, '金融', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(8, 1, 8, 0, '城市', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(9, 1, 9, 0, '运动', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(10, 1, 10, 2, '美食', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(11, 1, 11, 0, '交通', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(12, 1, 12, 0, '植物', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(13, 1, 13, 2, '动物', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(14, 1, 14, 0, '生活', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(15, 1, 15, 0, '创意', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(16, 1, 16, 0, '艺术', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(17, 1, 17, 0, '场景', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(18, 1, 18, 0, '生产', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(19, 1, 19, 0, '军事', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(20, 1, 20, 0, '背景', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(21, 1, 21, 1, '产品', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(22, 1, 22, 1, '浮漂', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(23, 1, 23, 1, '水墨', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(24, 1, 24, 1, '特效', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(25, 1, 25, 1, '动物', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(26, 1, 26, 1, '自然', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(27, 1, 27, 1, '文字', 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21');
SELECT setval('common_picture_cate_id_seq', (SELECT max(id) FROM common_picture_cate));
COMMIT;

-- ----------------------------
-- Table structure: common_verify_code 
-- ----------------------------
DROP TABLE IF EXISTS "common_verify_code";
CREATE TABLE "common_verify_code" (
 "id" bigserial NOT NULL,
 "keyname" varchar(50) NOT NULL,
 "code" varchar(20) NOT NULL,
 "create_time" timestamp, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "common_verify_code" IS '验证码存储';
COMMENT ON COLUMN "common_verify_code"."keyname" IS '存储key';
COMMENT ON COLUMN "common_verify_code"."code" IS '验证码';
COMMENT ON COLUMN "common_verify_code"."create_time" IS '创建时间';

-- ----------------------------
-- Data: common_verify_code 
-- ----------------------------
BEGIN;
INSERT INTO "common_verify_code" ("id", "keyname", "code", "create_time") VALUES 
(1, 'huang_li_shi@163.com', '380466', '2025-07-10 15:06:21');
SELECT setval('common_verify_code_id_seq', (SELECT max(id) FROM common_verify_code));
COMMIT;

-- ----------------------------
-- Table structure: login_logs 
-- ----------------------------
DROP TABLE IF EXISTS "login_logs";
CREATE TABLE "login_logs" (
 "id" bigserial NOT NULL,
 "type" int2 NOT NULL DEFAULT 1,
 "uid" int8 NOT NULL,
 "out_in" varchar(10) NOT NULL,
 "loginIP" varchar(30) NOT NULL,
 "create_time" timestamp,
 "update_time" timestamp DEFAULT CURRENT_TIMESTAMP, 
PRIMARY KEY ("id")
);
COMMENT ON TABLE "login_logs" IS '（平台及客户）后台登录日志';
COMMENT ON COLUMN "login_logs"."type" IS '类型1=平台。2=b端，3=C端';
COMMENT ON COLUMN "login_logs"."uid" IS '用户id';
COMMENT ON COLUMN "login_logs"."out_in" IS '登录或退出 out in';
COMMENT ON COLUMN "login_logs"."loginIP" IS '登录IP';
COMMENT ON COLUMN "login_logs"."create_time" IS '创建时间';
COMMENT ON COLUMN "login_logs"."update_time" IS '更新时间';

-- ----------------------------
-- Data: login_logs 
-- ----------------------------
BEGIN;
INSERT INTO "login_logs" ("id", "type", "uid", "out_in", "loginIP", "create_time", "update_time") VALUES 
(976, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(977, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(978, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(979, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(980, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(981, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(982, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(983, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(984, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(985, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(986, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(987, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(988, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(989, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(990, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(991, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(992, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(993, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(994, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(995, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(996, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(997, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(998, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(999, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(1000, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(1001, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(1002, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(1003, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(1004, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(1005, 1, 14, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(1006, 1, 1, 'in', '', '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(1007, 1, 1, 'in', '', '2025-07-17 17:22:33', '2025-07-17 17:22:33'),
(1008, 1, 1, 'in', '', '2025-07-18 09:23:36', '2025-07-18 09:23:36'),
(1009, 1, 1, 'in', '', '2025-07-23 08:59:54', '2025-07-23 08:59:54'),
(1010, 1, 1, 'in', '', '2025-07-23 09:06:47', '2025-07-23 09:06:47'),
(1011, 1, 1, 'in', '', '2025-07-23 10:57:14', '2025-07-23 10:57:14'),
(1012, 1, 1, 'in', '', '2025-07-23 15:40:18', '2025-07-23 15:40:18');
SELECT setval('login_logs_id_seq', (SELECT max(id) FROM login_logs));
COMMIT;

-- ----------------------------
-- Table structure: voice_document 
-- ----------------------------
DROP TABLE IF EXISTS "voice_document";
CREATE TABLE "voice_document" (
 "id" bigserial NOT NULL,
 "creator_id" int8,
 "creator_name" varchar(200),
 "create_time" timestamp,
 "updater_id" int8,
 "updater_name" varchar(200),
 "update_time" timestamp,
 "name" varchar(100),
 "content" varchar(1000), 
PRIMARY KEY ("id")
);
COMMENT ON COLUMN "voice_document"."id" IS '主键ID';
COMMENT ON COLUMN "voice_document"."creator_id" IS '创建人ID';
COMMENT ON COLUMN "voice_document"."creator_name" IS '创建人名称';
COMMENT ON COLUMN "voice_document"."create_time" IS '创建时间';
COMMENT ON COLUMN "voice_document"."updater_id" IS '更新人ID';
COMMENT ON COLUMN "voice_document"."updater_name" IS '更新人名称';
COMMENT ON COLUMN "voice_document"."update_time" IS '更新时间';
COMMENT ON COLUMN "voice_document"."name" IS '范文名';
COMMENT ON COLUMN "voice_document"."content" IS '范文内容';

-- ----------------------------
-- Data: voice_document 
-- ----------------------------
BEGIN;
SELECT setval('voice_document_id_seq', (SELECT max(id) FROM voice_document));
COMMIT;

-- ----------------------------
-- Table structure: voice_print 
-- ----------------------------
DROP TABLE IF EXISTS "voice_print";
CREATE TABLE "voice_print" (
 "id" bigserial NOT NULL,
 "creator_id" int8,
 "creator_name" varchar(200),
 "create_time" timestamp,
 "updater_id" int8,
 "updater_name" varchar(200),
 "update_time" timestamp,
 "deleted" int2 DEFAULT 0,
 "deleted_at" timestamp,
 "user_id" int8,
 "user_name" varchar(100),
 "print_id" int8, 
PRIMARY KEY ("id")
);
COMMENT ON COLUMN "voice_print"."id" IS '主键ID';
COMMENT ON COLUMN "voice_print"."creator_id" IS '创建人ID';
COMMENT ON COLUMN "voice_print"."creator_name" IS '创建人名称';
COMMENT ON COLUMN "voice_print"."create_time" IS '创建时间';
COMMENT ON COLUMN "voice_print"."updater_id" IS '更新人ID';
COMMENT ON COLUMN "voice_print"."updater_name" IS '更新人名称';
COMMENT ON COLUMN "voice_print"."update_time" IS '更新时间';
COMMENT ON COLUMN "voice_print"."deleted" IS '是否删除';
COMMENT ON COLUMN "voice_print"."deleted_at" IS '删除时间';
COMMENT ON COLUMN "voice_print"."user_id" IS '用户ID';
COMMENT ON COLUMN "voice_print"."user_name" IS '用户名';
COMMENT ON COLUMN "voice_print"."print_id" IS '声纹ID';

-- ----------------------------
-- Data: voice_print 
-- ----------------------------
BEGIN;
SELECT setval('voice_print_id_seq', (SELECT max(id) FROM voice_print));
COMMIT;
