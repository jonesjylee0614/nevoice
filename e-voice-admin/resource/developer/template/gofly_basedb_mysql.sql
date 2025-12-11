
-- ----------------------------
-- Dump Platform: mayfly-go
-- Dump Time: 2025-08-01 09:50:17 
-- Dump DB: gofly_single 
-- DB Dialect: mysql 
-- ----------------------------


-- ----------------------------
-- Table structure: attachment 
-- ----------------------------
DROP TABLE IF EXISTS `attachment`;
CREATE TABLE `attachment` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `uid` bigint(19) NOT NULL DEFAULT 0 COMMENT '上传用户',
 `cid` bigint(19) NOT NULL DEFAULT 0 COMMENT '分类',
 `url` varchar(255) NOT NULL COMMENT '访问路径',
 `imagewidth` varchar(30) NOT NULL COMMENT '宽度',
 `imageheight` varchar(30) NOT NULL COMMENT '高度',
 `imagetype` varchar(30) NOT NULL COMMENT '图片类型',
 `imageframes` int(10) NOT NULL DEFAULT 0 COMMENT '图片帧数',
 `filesize` int(10) NOT NULL DEFAULT 0 COMMENT '文件大小',
 `mimetype` varchar(100) NOT NULL COMMENT 'mime类型',
 `extparam` varchar(255) NOT NULL COMMENT '透传数据',
 `storage` varchar(500) NOT NULL DEFAULT 'local' COMMENT '存储位置',
 `sha1` varchar(40) NOT NULL COMMENT '文件 sha1编码',
 `title` varchar(500) NOT NULL COMMENT '文件名称',
 `name` varchar(500) NOT NULL COMMENT '附件名称',
 `cover_url` varchar(255) NOT NULL COMMENT '视频封面',
 `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
 `upload_time` datetime COMMENT '上传时间', 
PRIMARY KEY (id)
) COMMENT '附件管理';

-- ----------------------------
-- Data: attachment 
-- ----------------------------
BEGIN;
INSERT INTO `attachment` (`id`, `uid`, `cid`, `url`, `imagewidth`, `imageheight`, `imagetype`, `imageframes`, `filesize`, `mimetype`, `extparam`, `storage`, `sha1`, `title`, `name`, `cover_url`, `update_time`, `upload_time`) VALUES 
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
COMMIT;

-- ----------------------------
-- Table structure: business_account 
-- ----------------------------
DROP TABLE IF EXISTS `business_account`;
CREATE TABLE `business_account` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `uid` bigint(19) NOT NULL COMMENT '添加用户',
 `dept_id` bigint(19) NOT NULL COMMENT '部门id',
 `username` longtext NOT NULL COMMENT '用户账号',
 `password` longtext NOT NULL COMMENT '密码',
 `salt` longtext NOT NULL COMMENT '密码盐',
 `name` varchar(50) NOT NULL DEFAULT '0' COMMENT '姓名',
 `nickname` longtext NOT NULL COMMENT '昵称',
 `avatar` longtext NOT NULL COMMENT '头像',
 `tel` longtext NOT NULL COMMENT '备用电话用户自己填写',
 `mobile` longtext NOT NULL COMMENT '手机号码',
 `email` longtext NOT NULL COMMENT '邮箱',
 `lastLoginIp` longtext NOT NULL COMMENT '最后登录IP',
 `lastLoginTime` bigint(19) NOT NULL COMMENT '最后登录时间',
 `status` bigint(19) NOT NULL COMMENT '状态0=正常，1=禁用',
 `validtime` bigint(19) NOT NULL COMMENT '账号有效时间0=无限',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime COMMENT '更新时间',
 `address` longtext NOT NULL COMMENT '地址',
 `city` longtext NOT NULL COMMENT '城市',
 `remark` longtext NOT NULL COMMENT '描述',
 `company` longtext NOT NULL COMMENT '公司名称',
 `province` longtext NOT NULL COMMENT '省份',
 `area` longtext NOT NULL COMMENT '地区',
 `fileSize` bigint(19) NOT NULL DEFAULT 3787456512 COMMENT '附件存储空间',
 `loginstatus` tinyint(3) COMMENT '登录状态',
 `appkey` varchar(50) COMMENT 'appkey',
 `appKeySecret` varchar(100) COMMENT 'appKeySecret',
 `creator_id` bigint(19) COMMENT '创建人ID',
 `creator_name` varchar(200) COMMENT '创建人名称',
 `updater_id` bigint(19) COMMENT '更新人ID',
 `updater_name` varchar(200) COMMENT '更新人名称', 
PRIMARY KEY (id)
) COMMENT '用户端-用户信息';

-- ----------------------------
-- Data: business_account 
-- ----------------------------
BEGIN;
INSERT INTO `business_account` (`id`, `uid`, `dept_id`, `username`, `password`, `salt`, `name`, `nickname`, `avatar`, `tel`, `mobile`, `email`, `lastLoginIp`, `lastLoginTime`, `status`, `validtime`, `create_time`, `update_time`, `address`, `city`, `remark`, `company`, `province`, `area`, `fileSize`, `loginstatus`, `appkey`, `appKeySecret`, `creator_id`, `creator_name`, `updater_id`, `updater_name`) VALUES 
(1, 1, 3, 'gofly', '8cb8aef923ab5174aa392457960902af', '1697472561111', '开发管理员', 'leozy', 'http://localhost:8108/common/uploadfile/get_image?url=resource/uploads/20250704/71e26ab83700a7c7d7429456a017eda7.png', '88422345', '18988347563', '595324626@qq.com', '', 1754011475936, 0, 0, '2025-07-17 15:06:21', '2025-08-01 09:24:35', '中国重庆渝北区', '昆明', '开发账号', 'GoFLy科技1', '', 'chaoyang', 2147483647, 1, '7WxQUgJb0LEWwtTQ', 'ci81SMHaMqQ0SHstViDp17wGdKzuNi', NULL, NULL, 1, '开发管理员'),
(14, 1, 3, 'test', 'd891fa386193b8a0d07f7396d01e003d', '1751618562166', 'test', 'test', 'http://localhost:8108/common/uploadfile/get_image?url=resource/uploads/20250711/6199ab6b6fad8f3f449b5ff175b17653.jpg', '', '', '', '', 1752035036751, 0, 0, '2025-07-11 23:06:21', '2025-07-28 15:56:23', '', '', '', '', '', '', 3787456512, 1, 'w1frrmXr0JhR7iEM', 'OiK0EI8STgrRvmHw9LAa1njgzgmBhP', NULL, NULL, 1, '开发管理员'),
(15, 1, 3, 'docliu', '75bf955239bb6901ebbb771299d0852a', '1752214339915', '刘医生', '刘医生', 'http://localhost:8108/common/uploadfile/get_image?url=resource/uploads/20250711/d37669a872c8004355c73ac5e672e262.jpg', '', '', '', '', 0, 0, 0, '2025-07-13 22:12:20', '2025-07-28 15:56:21', '', '', '', '', '', '', 3787456512, 0, 'PeK0q0AFcgd8ZF3B', 'NW1ZhhbP2iLVpQ34pBRCIFVrGciM0J', NULL, NULL, 1, '开发管理员'),
(16, 1, 3, 'zcr1', '3ce5b686896e550cda80c114b9925e5d', '1753689162867', '主持人女', '', 'http://localhost:8108/common/uploadfile/get_image?url=resource/staticfile/avatar.png', '', '', '', '', 0, 0, 0, '2025-07-29 07:52:42', '2025-07-28 15:56:19', '', '', '', '', '', '', 3787456512, 0, 'ZWd558mhN1zYNtj6', 'zsLDXUstXrZoe3BS86Hn4zo4X66dOh', 1, '开发管理员', 1, '开发管理员'),
(21, 1, 3, 'zongj11', '28d7134e8e91b9f4105b006292ce614f', '1753689402375', '技术总监', '', 'http://localhost:8108/common/uploadfile/get_image?url=resource/staticfile/avatar.png', '', '', '', '', 0, 0, 0, '2025-07-28 23:56:42', '2025-07-28 15:56:56', '', '', '', '', '', '', 3787456512, 0, '5pbT952zLMixIxZc', 'qtvxUzzhkqo1tXjWC6kKodfEgNfBEA', 1, '开发管理员', 1, '开发管理员'),
(22, 1, 3, 'zongj12', '2bcda3fda5484640137380ca108c01a3', '1753689408565', '技术总监2', '', 'http://localhost:8108/common/uploadfile/get_image?url=resource/staticfile/avatar.png', '', '', '', '', 0, 0, 0, '2025-07-28 23:56:48', '2025-07-28 15:57:03', '', '', '', '', '', '', 3787456512, 0, 'M8YdaL9yEaM58aNd', 'Af2mmk1dEmFChXOzNSnRr8DIuXMCsG', 1, '开发管理员', 1, '开发管理员'),
(23, 1, 3, 'zhuanjia1', 'ad81bd06b6ad10cf3b54ea9da0039f91', '1753689445510', '砖家1', '', 'resource/staticfile/avatar.png', '', '', '', '', 0, 0, 0, '2025-07-28 15:57:25', '2025-07-28 15:57:25', '', '', '', '', '', '', 3787456512, 0, 'nlWjyLyISgkaHNup', '3NSY7cp0t1TXXu2Qf6F8m1Rv4CfGqW', 1, '开发管理员', 1, '开发管理员');
COMMIT;

-- ----------------------------
-- Table Index: business_account 
-- ----------------------------
ALTER TABLE `business_account` ADD unique INDEX `unique_idx`(`appkey`) USING BTREE;

-- ----------------------------
-- Table structure: business_attachment 
-- ----------------------------
DROP TABLE IF EXISTS `business_attachment`;
CREATE TABLE `business_attachment` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `weigh` bigint(19) NOT NULL DEFAULT 0 COMMENT '排序',
 `pid` bigint(19) NOT NULL DEFAULT 0 COMMENT '附件',
 `name` varchar(500) NOT NULL COMMENT '附件原来名称',
 `title` varchar(500) NOT NULL COMMENT '文件名称',
 `type` tinyint(3) NOT NULL DEFAULT 0 COMMENT '文件类型0=图片，1=文件夹,2=视频，3=音频',
 `url` varchar(255) NOT NULL COMMENT '访问路径',
 `imagewidth` varchar(30) NOT NULL COMMENT '宽度',
 `imageheight` varchar(30) NOT NULL COMMENT '高度',
 `filesize` int(10) NOT NULL DEFAULT 0 COMMENT '文件大小',
 `mimetype` varchar(100) NOT NULL COMMENT 'mime类型',
 `extparam` varchar(255) NOT NULL COMMENT '透传数据',
 `storage` varchar(500) NOT NULL DEFAULT 'local' COMMENT '存储位置',
 `cover_url` varchar(255) NOT NULL COMMENT '视频封面',
 `sha1` varchar(40) NOT NULL COMMENT '文件 sha1编码',
 `is_common` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否公共1=是',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间', 
PRIMARY KEY (id)
) COMMENT '客户端附件';

-- ----------------------------
-- Data: business_attachment 
-- ----------------------------
BEGIN;
INSERT INTO `business_attachment` (`id`, `weigh`, `pid`, `name`, `title`, `type`, `url`, `imagewidth`, `imageheight`, `filesize`, `mimetype`, `extparam`, `storage`, `cover_url`, `sha1`, `is_common`, `create_time`, `update_time`) VALUES 
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
COMMIT;

-- ----------------------------
-- Table structure: business_auth_dept 
-- ----------------------------
DROP TABLE IF EXISTS `business_auth_dept`;
CREATE TABLE `business_auth_dept` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `uid` bigint(19) NOT NULL COMMENT '添加用户',
 `name` longtext NOT NULL COMMENT '部门名称',
 `pid` bigint(19) NOT NULL COMMENT '上级部门',
 `weigh` bigint(19) NOT NULL COMMENT '排序',
 `status` bigint(19) NOT NULL COMMENT '状态',
 `remark` longtext NOT NULL COMMENT '备注',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime COMMENT '更新时间',
 `creator_id` bigint(19) COMMENT '创建人ID',
 `creator_name` varchar(200) COMMENT '创建人名称',
 `updater_id` bigint(19) COMMENT '更新人ID',
 `updater_name` varchar(200) COMMENT '更新人名称', 
PRIMARY KEY (id)
) COMMENT '管理后台部门';

-- ----------------------------
-- Data: business_auth_dept 
-- ----------------------------
BEGIN;
INSERT INTO `business_auth_dept` (`id`, `uid`, `name`, `pid`, `weigh`, `status`, `remark`, `create_time`, `update_time`, `creator_id`, `creator_name`, `updater_id`, `updater_name`) VALUES 
(1, 1, '市场部门', 0, 1, 0, '营销', '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(2, 1, '第一组', 1, 2, 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(3, 1, '研发部门', 1, 3, 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(4, 2, '领导部门', 0, 4, 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(6, 2, '人事组', 4, 6, 0, '', '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL);
COMMIT;

-- ----------------------------
-- Table structure: business_auth_role 
-- ----------------------------
DROP TABLE IF EXISTS `business_auth_role`;
CREATE TABLE `business_auth_role` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `uid` bigint(19) NOT NULL COMMENT '添加用户id',
 `pid` bigint(19) NOT NULL COMMENT '父级',
 `name` longtext NOT NULL COMMENT '名称',
 `rules` longtext NOT NULL COMMENT '规则ID 所拥有的权限包扣父级',
 `menu` longtext NOT NULL COMMENT '选择的id，用于编辑赋值',
 `status` bigint(19) NOT NULL COMMENT '状态1=禁用',
 `data_access` bigint(19) NOT NULL COMMENT '数据权限0=自己1=自己及子权限，2=全部',
 `remark` longtext NOT NULL COMMENT '描述',
 `weigh` bigint(19) NOT NULL COMMENT '排序',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime COMMENT '更新时间',
 `creator_id` bigint(19) COMMENT '创建人ID',
 `creator_name` varchar(200) COMMENT '创建人名称',
 `updater_id` bigint(19) COMMENT '更新人ID',
 `updater_name` varchar(200) COMMENT '更新人名称', 
PRIMARY KEY (id)
) COMMENT '权限分组';

-- ----------------------------
-- Data: business_auth_role 
-- ----------------------------
BEGIN;
INSERT INTO `business_auth_role` (`id`, `uid`, `pid`, `name`, `rules`, `menu`, `status`, `data_access`, `remark`, `weigh`, `create_time`, `update_time`, `creator_id`, `creator_name`, `updater_id`, `updater_name`) VALUES 
(1, 1, 0, '超级管理组', '*', '*', 0, 0, '账号的总管理员', 1, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(5, 1, 1, '销售员2', '8,11,13,49,59,6', '[8,11,13,49,59]', 0, 0, '产品销售组', 2, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(6, 1, 1, '管理员', '7,11,13,32,8,64,61,12,63,6', '[7,11,13,32,8,64,61,12,63]', 0, 0, '', 3, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(7, 1, 6, '编辑组', '7,34,33,11,12,6', '[7,34,33,11,12]', 0, 0, '', 4, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(8, 1, 6, '兼职组', '11,12,34,7,33', '[11,12,34,7,33]', 0, 0, '测试', 8, '2025-07-10 23:06:21', '2025-07-11 14:09:27', NULL, NULL, NULL, NULL),
(11, 1, 0, '管理组', '8,9,10,6', '[8,9,10]', 0, 0, '', 11, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(13, 1, 0, '市场部门', '8,6', '[8]', 0, 0, '', 13, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(16, 1, 0, '财务室', '8,48,49,59,69,6', '[8,48,49,59,69]', 0, 0, '修改', 16, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(19, 1, 1, '新增权限2', '70,8,11,438,439,437,443,455,453,454,13,444,458,456,442,451,452,450,69,68', '[70,8,11,438,439,437,443,455,453,454,13,444,458,456,442,451,452,450,69,68]', 0, 0, '', 19, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(21, 1, 0, '测试', '61,63,437,11,13,12', '[61,63,437,11,13,12]', 0, 0, '测试', 21, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(22, 1, 0, '测试', '61,63,437,11,13,12', '[61,63,437,11,13,12]', 0, 0, '测试', 22, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(23, 1, 0, 'test', '', '', 0, 0, '', 23, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(24, 1, 0, 'test', '61,63,438,439,440,437,11,442,451,452,450,13,443,454,455,453,12,444,457,458,456', '[61,63,438,439,440,437,11,442,451,452,450,13,443,454,455,453,12,444,457,458,456]', 0, 0, 'test', 24, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(25, 1, 20, 'test', '11,442,451,452,450', '[11,442,451,452,450]', 0, 0, 'test', 25, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(26, 1, 1, '声纹注册用户', '68,69,70', '[68,69,70]', 0, 0, '声纹管理需要查询拥有此角色的用户', 26, '2025-07-12 06:05:51', '2025-07-11 14:08:12', NULL, NULL, NULL, NULL);
COMMIT;

-- ----------------------------
-- Table structure: business_auth_role_access 
-- ----------------------------
DROP TABLE IF EXISTS `business_auth_role_access`;
CREATE TABLE `business_auth_role_access` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `uid` bigint(19) NOT NULL DEFAULT 0 COMMENT '账号id',
 `role_id` bigint(19) NOT NULL DEFAULT 0 COMMENT '授权id', 
PRIMARY KEY (id)
) COMMENT '用户角色授权';

-- ----------------------------
-- Data: business_auth_role_access 
-- ----------------------------
BEGIN;
INSERT INTO `business_auth_role_access` (`id`, `uid`, `role_id`) VALUES 
(1, 4, 1),
(2, 5, 6),
(3, 9, 6),
(4, 9, 5),
(5, 3, 5),
(6, 10, 5),
(7, 11, 1),
(8, 12, 1),
(9, 13, 1),
(30, 16, 26),
(31, 15, 26),
(32, 14, 19),
(33, 14, 26),
(34, 1, 1),
(35, 21, 26),
(36, 22, 26),
(37, 23, 26);
COMMIT;

-- ----------------------------
-- Table structure: business_auth_rule 
-- ----------------------------
DROP TABLE IF EXISTS `business_auth_rule`;
CREATE TABLE `business_auth_rule` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `uid` bigint(19) NOT NULL COMMENT '添加用户',
 `title` longtext NOT NULL COMMENT '菜单名称',
 `locale` longtext COMMENT '中英文标题key',
 `orderNo` bigint(19) NOT NULL COMMENT '排序',
 `type` bigint(19) NOT NULL COMMENT '类型 0=目录，1=菜单，2=按钮',
 `pid` bigint(19) NOT NULL COMMENT '上一级',
 `icon` longtext NOT NULL COMMENT '图标',
 `routePath` longtext NOT NULL COMMENT '路由地址',
 `routeName` longtext NOT NULL COMMENT '路由名称',
 `component` longtext NOT NULL COMMENT '组件路径',
 `redirect` longtext COMMENT '重定向地址',
 `permission` longtext COMMENT '权限标识',
 `status` tinyint(3) NOT NULL DEFAULT 0 COMMENT '状态 0=启用1=禁用',
 `isExt` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否外链 0=否1=是',
 `keepalive` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否缓存 0=否1=是',
 `requiresAuth` tinyint(3) NOT NULL DEFAULT 1 COMMENT '是否需要登录鉴权 0=否1=是',
 `hideInMenu` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否在左侧菜单中隐藏该项 0=否1=是',
 `hideChildrenInMenu` tinyint(3) NOT NULL DEFAULT 0 COMMENT '强制在左侧菜单中显示单项 0=否1=是',
 `activeMenu` bigint(19) NOT NULL DEFAULT 1 COMMENT '高亮设置的菜单项 0=否1=是',
 `noAffix` tinyint(3) NOT NULL DEFAULT 0 COMMENT '如果设置为true，标签将不会添加到tab-bar中 0=否1=是',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime COMMENT '更新时间',
 `creator_id` bigint(19) COMMENT '创建人ID',
 `creator_name` varchar(200) COMMENT '创建人名称',
 `updater_id` bigint(19) COMMENT '更新人ID',
 `updater_name` varchar(200) COMMENT '更新人名称', 
PRIMARY KEY (id)
) COMMENT 'C端-菜单';

-- ----------------------------
-- Data: business_auth_rule 
-- ----------------------------
BEGIN;
INSERT INTO `business_auth_rule` (`id`, `uid`, `title`, `locale`, `orderNo`, `type`, `pid`, `icon`, `routePath`, `routeName`, `component`, `redirect`, `permission`, `status`, `isExt`, `keepalive`, `requiresAuth`, `hideInMenu`, `hideChildrenInMenu`, `activeMenu`, `noAffix`, `create_time`, `update_time`, `creator_id`, `creator_name`, `updater_id`, `updater_name`) VALUES 
(8, 1, '概况', '', 1, 1, 0, 'icon-dashboard', '/home', 'home', '/dashboard/workplace/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(11, 1, '角色管理', '', 2, 1, 61, '', 'role', 'role', '/system/role/index', '', '', 0, 0, 1, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(12, 1, '菜单管理', '', 4, 1, 61, '', 'rule', 'rule', '/system/rule/index', '', '', 0, 0, 1, 1, 2, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(13, 1, '部门管理', '', 3, 1, 61, '', 'dept', 'dept', '/system/dept/index', '', '', 0, 0, 1, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(61, 14, '系统设置', '', 3, 0, 0, 'icon-settings', '/system', 'system', 'LAYOUT', '/system/account', '', 0, 0, 0, 0, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(63, 1, '账户管理', '', 1, 1, 61, '', 'account', 'account', '/system/account/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(64, 1, '添加账号', '', 64, 2, 7, '', '', '', '', '', 'add', 0, 0, 0, 0, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(68, 1, '个人中心', '', 2, 0, 0, 'icon-user', '/user', 'user', 'LAYOUT', '/user/info', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(69, 1, '账号信息', '', 0, 1, 68, '', 'info', 'info', '/user/info/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(70, 1, '用户设置', '', 0, 1, 68, '', 'setting', 'setting', '/user/setting/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(74, 14, '开发者', '', 5, 0, 0, 'icon-code', '/developer', 'developer', 'LAYOUT', '/developer/apidoc', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(75, 1, '接口文档', '', 2, 1, 74, '', 'http://localhost:8108/openapi/', 'devapi', '/developer/generatecode/index', '', '', 0, 1, 0, 1, 0, 0, 0, 0, '2025-07-11 07:06:21', '2025-07-15 15:02:12', NULL, NULL, NULL, NULL),
(97, 1, '生成代码', '', 3, 1, 74, '', 'generatecode', 'generatecode', '/developer/generatecode/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(121, 1, '数据中心', '', 4, 0, 0, 'icon-storage', '/datacenter', 'datacenter', 'LAYOUT', '/datacenter/dictionary', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(123, 1, '字典数据', '', 1, 1, 121, '', 'data', 'data', '/datacenter/dictionary/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(137, 1, '附件管理', '', 2, 1, 121, '', 'attachment', 'attachment', 'datacenter/attachment/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(143, 1, '配置管理', '', 3, 1, 121, '', 'configuration', 'configuration', '/datacenter/configuration/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(374, 1, '代码生成器', '', 1, 1, 74, '', 'codemaker', 'codemaker', '/developer/generatecode/codemaker.vue', '', '', 0, 0, 0, 1, 1, 0, 0, 1, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(435, 1, '测试代码产品', '', 1, 1, 383, 'icon-sun-fill', 'product', 'product', 'makecode/product/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(436, 1, '测试代码产品分类', '', 2, 1, 383, '', 'cate', 'cate', 'makecode/cate/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(437, 1, '修改状态', '', 4, 2, 63, '', '', '', '', '', 'account:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(438, 1, '基本权限', '', 1, 2, 63, '', '', '', '', '', 'account:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(439, 1, '编辑', '', 2, 2, 63, '', '', '', '', '', 'account:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(440, 1, '删除', '', 3, 2, 63, '', '', '', '', '', 'account:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(442, 1, '基本权限', '', 1, 2, 11, '', '', '', '', '', 'role:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(443, 1, '基本权限', '', 1, 2, 13, '', '', '', '', '', 'dept:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(444, 1, '基本权限', '', 1, 2, 12, '', '', '', '', '', 'rule:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(445, 1, '基本权限', '', 1, 2, 123, '', '', '', '', '', 'dict:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(446, 1, '基本权限', '', 1, 2, 137, '', '', '', '', '', 'atta:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(447, 1, '基本权限', '', 1, 2, 143, '', '', '', '', '', 'config:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(450, 1, '修改状态', '', 4, 2, 11, '', '', '', '', '', 'role:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(451, 1, '编辑', '', 2, 2, 11, '', '', '', '', '', 'role:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(452, 1, '删除', '', 3, 2, 11, '', '', '', '', '', 'role:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(453, 1, '修改状态', '', 4, 2, 13, '', '', '', '', '', 'dept:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(454, 1, '编辑', '', 2, 2, 13, '', '', '', '', '', 'dept:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(455, 1, '删除', '', 3, 2, 13, '', '', '', '', '', 'dept:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(456, 1, '修改状态', '', 4, 2, 12, '', '', '', '', '', 'rule:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(457, 1, '编辑', '', 2, 2, 12, '', '', '', '', '', 'rule:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(458, 1, '删除', '', 3, 2, 12, '', '', '', '', '', 'rule:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(459, 1, '删除', '', 3, 2, 123, '', '', '', '', '', 'dict:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(460, 1, '编辑', '', 2, 2, 123, '', '', '', '', '', 'dict:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(461, 1, '修改状态', '', 4, 2, 123, '', '', '', '', '', 'dict:upStatus', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(462, 1, '添加', '', 2, 2, 137, '', '', '', '', '', 'atta:add', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(463, 1, '删除', '', 3, 2, 137, '', '', '', '', '', 'atta:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(464, 1, '基本权限', '', 1, 2, 97, '', '', '', '', '', 'gen:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(465, 1, '声纹注册', '', 1, 1, 466, '', '/voice/print', 'print', '/voice/print/index.vue', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-13 10:16:36', '2025-07-11 18:19:45', NULL, NULL, NULL, NULL),
(466, 1, '声纹管理', '', 6, 0, 0, 'icon-idcard', '/voice', 'voice', 'LAYOUT', '/voice', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-12 10:17:52', '2025-07-11 18:19:32', NULL, NULL, NULL, NULL),
-- 语音识别
(800, 1, '语音能力', '', 20, 0, 0, 'icon-sound', '/voice', 'voice2', 'LAYOUT', '/voice/identify', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-31 00:00:00', '2025-07-31 00:00:00', NULL, NULL, NULL, NULL),
(801, 1, '实时语音识别', '', 1, 1, 800, '', '/voice/identify', 'voiceIdentify', '/voice/identify/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-31 00:00:00', '2025-07-31 00:00:00', NULL, NULL, NULL, NULL),
(802, 1, '在线语音识别', '', 2, 1, 800, '', '/voice/identify/online', 'voiceIdentifyOnline', '/voice/identify/online', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-31 00:00:00', '2025-07-31 00:00:00', NULL, NULL, NULL, NULL),
(803, 1, '离线语音识别', '', 3, 1, 800, '', '/voice/identify/offline', 'voiceIdentifyOffline', '/voice/identify/offline', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-31 00:00:00', '2025-07-31 00:00:00', NULL, NULL, NULL, NULL),
(467, 1, '添加', '', 2, 2, 465, '', '', '', '', '', 'print:add', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-14 12:16:20', '2025-07-14 12:16:20', NULL, NULL, NULL, NULL),
(468, 1, '删除', '', 3, 2, 465, '', '', '', '', '', 'print:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-14 20:16:32', '2025-07-14 12:16:36', NULL, NULL, NULL, NULL),
(469, 1, '会议管理', '', 7, 0, 0, 'icon-user-group', '/meeting', 'meeting', 'LAYOUT', '/meeting', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:43:38', '2025-07-28 09:43:52', 1, '开发管理员', 1, '开发管理员'),
(470, 1, '离线会议', '', 1, 1, 469, '', '/meeting/offline', 'meeting_offline', '/meeting/offline/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:44:43', '2025-07-28 09:45:06', 1, '开发管理员', 1, '开发管理员'),
(471, 1, '基础权限', '', 1, 2, 465, '', '', '', '', '', 'print:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-25 22:16:34', '2025-07-25 22:16:34', NULL, NULL, NULL, NULL),
(472, 1, '基础权限', '', 1, 2, 470, '', '', '', '', '', 'meeting:offline:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-25 22:17:02', '2025-07-25 22:17:02', NULL, NULL, NULL, NULL),
(473, 1, '编辑', '', 2, 2, 470, '', '', '', '', '', 'meeting:offline:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-26 06:17:17', '2025-07-25 22:17:45', NULL, NULL, NULL, NULL),
(474, 1, '删除', '', 3, 2, 470, '', '', '', '', '', 'meeting:offline:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-25 22:17:31', '2025-07-25 22:17:31', NULL, NULL, NULL, NULL),
(475, 1, '会议详情', '', 4, 2, 470, '', '', '', '', '', 'meeting:offline:detail', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-25 22:18:25', '2025-07-25 22:18:25', NULL, NULL, NULL, NULL),
(476, 1, '会议详情-编辑', '', 5, 2, 470, '', '', '', '', '', 'meeting:offline:detail:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-25 22:19:01', '2025-07-25 22:19:01', NULL, NULL, NULL, NULL),
(477, 1, '会议详情-编辑训练状态', '', 6, 2, 470, '', '', '', '', '', 'meeting:offline:detail:edit_train', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-26 06:20:33', '2025-07-25 22:20:56', NULL, NULL, NULL, NULL),
(478, 1, '会议详情-导出', '', 7, 2, 470, '', '', '', '', '', 'meeting:offline:detail:export', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-26 06:21:49', '2025-07-25 22:27:11', NULL, NULL, NULL, NULL),
(479, 1, '模型微调', '', 8, 0, 0, 'icon-translate', '/finetune', 'finetune', 'LAYOUT', '/finetune', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-29 09:05:28', '2025-07-31 08:38:51', 1, '开发管理员', 1, '开发管理员'),
(480, 1, '语料管理', '', 1, 1, 479, '', '/finetune/audio', 'finetune_audio', '/finetune/audio/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:06:27', '2025-07-28 17:06:27', 1, '开发管理员', 1, '开发管理员'),
(481, 1, '微调管理', '', 2, 1, 479, '', '/finetune/task', 'finetune_task', '/finetune/task/index', '', '', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:07:05', '2025-07-28 17:07:05', 1, '开发管理员', 1, '开发管理员'),
(482, 1, '基础权限', '', 1, 2, 480, '', '', '', '', '', 'finetune:audio:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:07:33', '2025-07-28 17:07:33', 1, '开发管理员', 1, '开发管理员'),
(483, 1, '编辑', '', 2, 2, 480, '', '', '', '', '', 'finetune:audio:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:07:49', '2025-07-28 17:07:49', 1, '开发管理员', 1, '开发管理员'),
(484, 1, '删除', '', 3, 2, 480, '', '', '', '', '', 'finetune:audio:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:08:01', '2025-07-28 17:08:01', 1, '开发管理员', 1, '开发管理员'),
(485, 1, '基础权限', '', 1, 2, 481, '', '', '', '', '', 'finetune:task:base', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:08:13', '2025-07-28 17:08:13', 1, '开发管理员', 1, '开发管理员'),
(486, 1, '编辑', '', 2, 2, 481, '', '', '', '', '', 'finetune:task:edit', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:08:27', '2025-07-28 17:08:27', 1, '开发管理员', 1, '开发管理员'),
(487, 1, '删除', '', 3, 2, 481, '', '', '', '', '', 'finetune:task:del', 0, 0, 0, 1, 0, 0, 0, 0, '2025-07-28 17:08:37', '2025-07-28 17:08:37', 1, '开发管理员', 1, '开发管理员');
COMMIT;

-- ----------------------------
-- Table structure: business_home_quickop 
-- ----------------------------
DROP TABLE IF EXISTS `business_home_quickop`;
CREATE TABLE `business_home_quickop` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `uid` bigint(19) NOT NULL DEFAULT 0 COMMENT '添加人',
 `is_common` tinyint(3) NOT NULL DEFAULT 0 COMMENT '公共1=是',
 `type` tinyint(3) NOT NULL DEFAULT 0 COMMENT '类型1=外部',
 `name` varchar(50) NOT NULL COMMENT '快捷名称',
 `path_url` varchar(50) NOT NULL COMMENT '跳转路径',
 `icon` varchar(50) NOT NULL COMMENT '图标',
 `weigh` bigint(19) NOT NULL DEFAULT 0 COMMENT '权重', 
PRIMARY KEY (id)
) COMMENT '首页快捷操作';

-- ----------------------------
-- Data: business_home_quickop 
-- ----------------------------
BEGIN;
INSERT INTO `business_home_quickop` (`id`, `uid`, `is_common`, `type`, `name`, `path_url`, `icon`, `weigh`) VALUES 
(1, 1, 0, 0, '文档接口', 'devapi', 'icon-common', 1),
(2, 1, 0, 0, '生成代码', 'generatecode', 'icon-mobile', 2);
COMMIT;

-- ----------------------------
-- Table structure: common_apidoc_group 
-- ----------------------------
DROP TABLE IF EXISTS `common_apidoc_group`;
CREATE TABLE `common_apidoc_group` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `type` varchar(20) NOT NULL DEFAULT 'admin' COMMENT '分类接口属于那端，admin=管理，biz=B端，client=C端',
 `pid` bigint(19) NOT NULL DEFAULT 0 COMMENT '父级0=一级',
 `name` varchar(50) NOT NULL COMMENT '分类名称',
 `status` tinyint(3) NOT NULL DEFAULT 0 COMMENT '状态1=禁用',
 `type_id` bigint(19) NOT NULL DEFAULT 0 COMMENT '接口类型', 
PRIMARY KEY (id)
) COMMENT '后台端接口测试分组';

-- ----------------------------
-- Data: common_apidoc_group 
-- ----------------------------
BEGIN;
INSERT INTO `common_apidoc_group` (`id`, `type`, `pid`, `name`, `status`, `type_id`) VALUES 
(1, 'biz', 0, 'app端', 0, 3),
(2, 'biz', 0, '小程序', 0, 1),
(3, 'biz', 0, '后台管理', 0, 2),
(4, 'biz', 2, '小程序-疫苗计划', 0, 1);
COMMIT;

-- ----------------------------
-- Table structure: common_apidoc_type 
-- ----------------------------
DROP TABLE IF EXISTS `common_apidoc_type`;
CREATE TABLE `common_apidoc_type` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `name` varchar(50) NOT NULL COMMENT '类型名称',
 `rooturl` varchar(255) NOT NULL COMMENT '请求服务器地址',
 `verifyEncrypt` varchar(80) NOT NULL COMMENT '加密验证字符串',
 `isself` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否是本端1=是',
 `user_tablename` varchar(50) NOT NULL COMMENT '测试授权用户数据表名',
 `user_id` int(10) NOT NULL DEFAULT 0 COMMENT '测试用户id',
 `login_url` varchar(100) NOT NULL COMMENT '登录地址',
 `model_name` varchar(50) NOT NULL COMMENT '模块目录', 
PRIMARY KEY (id)
) COMMENT '接口类型';

-- ----------------------------
-- Data: common_apidoc_type 
-- ----------------------------
BEGIN;
INSERT INTO `common_apidoc_type` (`id`, `name`, `rooturl`, `verifyEncrypt`, `isself`, `user_tablename`, `user_id`, `login_url`, `model_name`) VALUES 
(1, '小程序', 'https://yg.goflys.cn', 'gofly@888', 0, 'business_wxsys_user', 6, '/wxapp/user/get_apitoken', 'wxapp'),
(2, '本端', '', '', 1, '', 0, '', ''),
(3, '手机APP', 'https://yg.goflys.cn', 'gofly@888', 0, '', 0, '', '');
COMMIT;

-- ----------------------------
-- Table structure: common_config 
-- ----------------------------
DROP TABLE IF EXISTS `common_config`;
CREATE TABLE `common_config` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `keyname` varchar(255) NOT NULL COMMENT '配置名称',
 `keyvalue` varchar(255) NOT NULL COMMENT '配置值',
 `des` varchar(255) NOT NULL COMMENT '描述',
 `weigh` bigint(19) NOT NULL DEFAULT 0 COMMENT '排序', 
PRIMARY KEY (id)
) COMMENT '系统配置参数';

-- ----------------------------
-- Data: common_config 
-- ----------------------------
BEGIN;
INSERT INTO `common_config` (`id`, `keyname`, `keyvalue`, `des`, `weigh`) VALUES 
(2, 'rooturl', 'http://localhost:8108/common/uploadfile/get_image?url=', '图片路径', 0);
COMMIT;

-- ----------------------------
-- Table structure: common_dictionary_data 
-- ----------------------------
DROP TABLE IF EXISTS `common_dictionary_data`;
CREATE TABLE `common_dictionary_data` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `dic_id` longtext NOT NULL COMMENT '字典项值',
 `keyname` longtext NOT NULL COMMENT '字典名称',
 `keyvalue` longtext NOT NULL COMMENT '字典项值',
 `des` longtext NOT NULL COMMENT '字典描述',
 `status` bigint(19) NOT NULL COMMENT '状态',
 `weigh` bigint(19) NOT NULL COMMENT '排序',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime COMMENT '更新时间',
 `creator_id` bigint(19) COMMENT '创建人ID',
 `creator_name` varchar(200) COMMENT '创建人名称',
 `updater_id` bigint(19) COMMENT '更新人ID',
 `updater_name` varchar(200) COMMENT '更新人名称', 
PRIMARY KEY (id)
) COMMENT '字典数据-测试数据';

-- ----------------------------
-- Data: common_dictionary_data 
-- ----------------------------
BEGIN;
INSERT INTO `common_dictionary_data` (`id`, `dic_id`, `keyname`, `keyvalue`, `des`, `status`, `weigh`, `create_time`, `update_time`, `creator_id`, `creator_name`, `updater_id`, `updater_name`) VALUES 
(1, '2', '管理层', 'mteam', '公司领导', 0, 1, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL),
(2, '2', '业务员', 'salesman', '', 0, 2, '2025-07-10 15:06:21', '2025-07-10 15:06:21', NULL, NULL, NULL, NULL);
COMMIT;

-- ----------------------------
-- Table structure: common_dictionary_table 
-- ----------------------------
DROP TABLE IF EXISTS `common_dictionary_table`;
CREATE TABLE `common_dictionary_table` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `title` varchar(50) NOT NULL COMMENT '字典名称',
 `remark` varchar(200) NOT NULL COMMENT '备注',
 `tablename` varchar(50) NOT NULL COMMENT '数据表名称',
 `status` tinyint(3) NOT NULL COMMENT '状态',
 `weigh` bigint(19) NOT NULL DEFAULT 0 COMMENT '排序',
 `create_time` datetime COMMENT '创建时间', 
PRIMARY KEY (id)
) COMMENT '字典表';

-- ----------------------------
-- Data: common_dictionary_table 
-- ----------------------------
BEGIN;
INSERT INTO `common_dictionary_table` (`id`, `title`, `remark`, `tablename`, `status`, `weigh`, `create_time`) VALUES 
(2, '用户分组', '用户分组', 'common_dictionary_data', 0, 2, '2025-07-10 15:06:21'),
(3, 'test', '', 'common_dictionary_data', 0, 3, '2025-07-10 15:06:21');
COMMIT;

-- ----------------------------
-- Table structure: common_email 
-- ----------------------------
DROP TABLE IF EXISTS `common_email`;
CREATE TABLE `common_email` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `sender_email` varchar(50) NOT NULL COMMENT '发送者邮箱',
 `auth_code` varchar(50) NOT NULL COMMENT '邮箱授权码',
 `mail_title` varchar(80) NOT NULL COMMENT '邮件标题',
 `mail_body` text NOT NULL COMMENT '邮件内容,可以是html',
 `service_host` varchar(30) NOT NULL COMMENT '邮件服务器',
 `service_port` bigint(19) NOT NULL DEFAULT 0 COMMENT '邮件服务器端口', 
PRIMARY KEY (id)
) COMMENT '业务端邮箱';

-- ----------------------------
-- Data: common_email 
-- ----------------------------
BEGIN;
INSERT INTO `common_email` (`id`, `sender_email`, `auth_code`, `mail_title`, `mail_body`, `service_host`, `service_port`) VALUES 
(1, '504500934@qq.com', 'amidmyjnnxy(youwkey)', 'GoFly验证码', '你的验证码为：{code}', 'smtp.qq.com', 587),
(2, '504500934@qq.com', 'amidmyjnnxy(youkey)', 'GoFly验证码', '你的验证码为：{code}', 'smtp.qq.com', 587);
COMMIT;

-- ----------------------------
-- Table structure: common_generatecode 
-- ----------------------------
DROP TABLE IF EXISTS `common_generatecode`;
CREATE TABLE `common_generatecode` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `tablename` varchar(50) NOT NULL COMMENT '表名称',
 `comment` varchar(100) NOT NULL COMMENT '表备注',
 `engine` varchar(50) NOT NULL COMMENT '引擎',
 `table_rows` bigint(19) NOT NULL DEFAULT 0 COMMENT '记录数',
 `collation` varchar(50) NOT NULL COMMENT '编码',
 `auto_increment` bigint(19) NOT NULL DEFAULT 1 COMMENT '自增索引',
 `status` tinyint(3) NOT NULL DEFAULT 0 COMMENT '状态1=禁用',
 `pid` bigint(19) NOT NULL DEFAULT 0 COMMENT '菜单上级',
 `icon` varchar(50) COMMENT '图标',
 `routePath` varchar(255) COMMENT '路由地址',
 `routeName` varchar(100) COMMENT '路由名称',
 `component` varchar(100) COMMENT '组件路径',
 `api_path` varchar(60) COMMENT '后端业务接口',
 `api_filename` varchar(50) COMMENT '后端文件名',
 `fields` text COMMENT '查询字段',
 `rule_id` bigint(19) NOT NULL DEFAULT 0 COMMENT '生成菜单id',
 `rule_name` varchar(30) NOT NULL COMMENT '菜单名称',
 `is_install` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否安装0=未安装，1=已安装，2=已卸载',
 `tpl_type` varchar(20) NOT NULL DEFAULT 'list' COMMENT '模板类型list=仅一个数据，cate=数据加分类',
 `cate_tablename` varchar(50) COMMENT '分类表名称',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间', 
PRIMARY KEY (id)
) COMMENT '代码生成';

-- ----------------------------
-- Data: common_generatecode 
-- ----------------------------
BEGIN;
INSERT INTO `common_generatecode` (`id`, `tablename`, `comment`, `engine`, `table_rows`, `collation`, `auto_increment`, `status`, `pid`, `icon`, `routePath`, `routeName`, `component`, `api_path`, `api_filename`, `fields`, `rule_id`, `rule_name`, `is_install`, `tpl_type`, `cate_tablename`, `create_time`, `update_time`) VALUES 
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
COMMIT;

-- ----------------------------
-- Table structure: common_generatecode_field 
-- ----------------------------
DROP TABLE IF EXISTS `common_generatecode_field`;
CREATE TABLE `common_generatecode_field` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `generatecode_id` int(10) NOT NULL COMMENT '关联列表',
 `islist` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否是列表1=是',
 `name` varchar(50) NOT NULL COMMENT '字段名称',
 `field` varchar(50) NOT NULL COMMENT '字段',
 `isorder` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否参与排序',
 `align` varchar(10) NOT NULL DEFAULT 'left' COMMENT '对齐方向',
 `width` int(10) NOT NULL DEFAULT 0 COMMENT '宽度',
 `isform` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否为表单字段',
 `required` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否为必填项',
 `formtype` varchar(15) NOT NULL COMMENT '表单类型',
 `datatable` varchar(30) NOT NULL COMMENT '关联数据表',
 `datatablename` varchar(30) NOT NULL COMMENT '关联显示字段',
 `issearch` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否查询',
 `searchway` varchar(15) NOT NULL DEFAULT '=' COMMENT '查询方式',
 `searchtype` varchar(30) NOT NULL COMMENT '查询文本类型',
 `field_weigh` int(10) NOT NULL COMMENT '表单排序',
 `list_weigh` int(10) NOT NULL COMMENT '列表排序',
 `search_weigh` int(10) NOT NULL DEFAULT 0 COMMENT '搜索排序',
 `def_value` varchar(255) NOT NULL COMMENT '默认选项json', 
PRIMARY KEY (id)
) COMMENT '生成代码字段管理';

-- ----------------------------
-- Data: common_generatecode_field 
-- ----------------------------
BEGIN;
INSERT INTO `common_generatecode_field` (`id`, `generatecode_id`, `islist`, `name`, `field`, `isorder`, `align`, `width`, `isform`, `required`, `formtype`, `datatable`, `datatablename`, `issearch`, `searchway`, `searchtype`, `field_weigh`, `list_weigh`, `search_weigh`, `def_value`) VALUES 
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
COMMIT;

-- ----------------------------
-- Table structure: common_logininfo 
-- ----------------------------
DROP TABLE IF EXISTS `common_logininfo`;
CREATE TABLE `common_logininfo` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `type` varchar(20) NOT NULL DEFAULT 'common' COMMENT 'admin=管理端，business=商业端 common=公共',
 `title` varchar(80) NOT NULL COMMENT '标题',
 `des` varchar(255) NOT NULL COMMENT '描述',
 `image` varchar(145) NOT NULL COMMENT '图片',
 `status` tinyint(3) NOT NULL COMMENT '状态',
 `weigh` bigint(19) NOT NULL DEFAULT 0 COMMENT '排序',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间', 
PRIMARY KEY (id)
) COMMENT '登录页面内容';

-- ----------------------------
-- Data: common_logininfo 
-- ----------------------------
BEGIN;
INSERT INTO `common_logininfo` (`id`, `type`, `title`, `des`, `image`, `status`, `weigh`, `create_time`, `update_time`) VALUES 
(1, 'common', '智能语音识别', '基于深度学习的端到端语音识别引擎，支持实时流式识别与离线转写，识别准确率领先业界水平。', '/common/uploadfile/get_image?url=resource/uploads/20230607/f1fbf7039464d632d9b5fcecb1e41fab.png', 0, 1, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(2, 'common', '声纹识别管理', '精准的声纹特征提取与比对技术，一次注册即可实现说话人身份识别，广泛应用于身份验证场景。', '/common/uploadfile/get_image?url=resource/uploads/20230607/4825b3bc4721d2e6266b9696f47b23c5.png', 0, 2, '2025-07-10 15:06:21', '2025-07-10 15:06:21'),
(3, 'common', '智能会议转写', '支持多人会议的语音转文字与说话人分离，自动识别发言人并生成结构化会议纪要。', '/common/uploadfile/get_image?url=resource/uploads/20230607/33926ec2fcbc2da95e9cae158e00019e.png', 0, 3, '2025-07-10 15:06:21', '2025-07-10 15:06:21');
COMMIT;

-- ----------------------------
-- Table structure: common_message 
-- ----------------------------
DROP TABLE IF EXISTS `common_message`;
CREATE TABLE `common_message` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `adduid` bigint(19) NOT NULL DEFAULT 0 COMMENT '添加用户',
 `touid` bigint(19) NOT NULL DEFAULT 0 COMMENT '接收用户',
 `type` tinyint(3) NOT NULL DEFAULT 2 COMMENT '类型1=通知，2=消息，3=代办',
 `title` varchar(255) NOT NULL COMMENT '消息标题',
 `path` varchar(255) NOT NULL COMMENT '跳转路由',
 `content` text NOT NULL COMMENT '消息内容',
 `isread` tinyint(3) NOT NULL DEFAULT 0 COMMENT '是否已读1=已读',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间', 
PRIMARY KEY (id)
) COMMENT '系统通用消息';

-- ----------------------------
-- Data: common_message 
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure: common_picture 
-- ----------------------------
DROP TABLE IF EXISTS `common_picture`;
CREATE TABLE `common_picture` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `uid` bigint(19) NOT NULL DEFAULT 0 COMMENT '添加账号',
 `cid` bigint(19) NOT NULL DEFAULT 0 COMMENT '分类id',
 `weigh` bigint(19) NOT NULL DEFAULT 0 COMMENT '排序',
 `name` varchar(50) NOT NULL COMMENT '附件原来名称',
 `title` varchar(50) NOT NULL COMMENT '文件名称',
 `type` tinyint(3) NOT NULL DEFAULT 0 COMMENT '类型0=素材图1=插图,2=视频，3=音频',
 `url` varchar(255) NOT NULL COMMENT '访问路径',
 `imagewidth` varchar(30) NOT NULL COMMENT '宽度',
 `imageheight` varchar(30) NOT NULL COMMENT '高度',
 `filesize` int(10) NOT NULL DEFAULT 0 COMMENT '文件大小',
 `mimetype` varchar(100) NOT NULL COMMENT 'mime类型',
 `storage` varchar(500) NOT NULL DEFAULT 'local' COMMENT '存储位置',
 `cover_url` varchar(255) NOT NULL COMMENT '视频封面',
 `sha1` varchar(40) NOT NULL COMMENT '文件 sha1编码',
 `create_time` datetime COMMENT '创建时间',
 `status` tinyint(3) NOT NULL DEFAULT 0 COMMENT '状态1=禁用', 
PRIMARY KEY (id)
) COMMENT '图片库';

-- ----------------------------
-- Data: common_picture 
-- ----------------------------
BEGIN;
INSERT INTO `common_picture` (`id`, `uid`, `cid`, `weigh`, `name`, `title`, `type`, `url`, `imagewidth`, `imageheight`, `filesize`, `mimetype`, `storage`, `cover_url`, `sha1`, `create_time`, `status`) VALUES 
(5, 1, 20, 5, 'GoFLy发布文章封面.png', 'GoFLy发布文章封面', 0, 'https://sg.goflys.cn/common/uploadfile/get_image?url=resource/uploads/20230609/00658402ef4e5ba229f3935eca6701d8.png', '', '', 40902, 'image/png', '/dataDB/project/go/gofly_singleresource\\uploads\\20230609\\00658402ef4e5ba229f3935eca6701d8.png', '', 'b98da546d168f3e1d91d32585aaf719e', '2025-07-10 15:06:21', 0),
(6, 1, 24, 6, '信息.png', '信息', 1, 'https://sg.goflys.cn/common/uploadfile/get_image?url=resource/uploads/20230609/46e5cc40453791e1db8c0e25a1c8ff9c.png', '', '', 65892, 'image/png', '/dataDB/project/go/gofly_singleresource\\uploads\\20230609\\46e5cc40453791e1db8c0e25a1c8ff9c.png', '', 'd58b80c230362875af642143b6bd3a70', '2025-07-10 15:06:21', 0),
(7, 1, 25, 7, '宣传.png', '宣传', 1, 'https://sg.goflys.cn/common/uploadfile/get_image?url=resource/uploads/20230609/d43a77c266fd59f23b438a7204e80173.png', '', '', 42539, 'image/png', '/dataDB/project/go/gofly_singleresource\\uploads\\20230609\\d43a77c266fd59f23b438a7204e80173.png', '', 'a226b08471c634ebd11b4d32ac138176', '2025-07-10 15:06:21', 0),
(8, 1, 19, 8, 'sw1.jpg', 'sw1', 0, 'https://sg.goflys.cn/common/uploadfile/get_image?url=resource/uploads/20230609/c895e724853152e06b5915f046348808.jpg', '', '', 25384, 'image/jpeg', '/dataDB/project/go/gofly_singleresource\\uploads\\20230609\\c895e724853152e06b5915f046348808.jpg', '', '8a81b3c0d0f346d7a36a4573e7196408', '2025-07-10 15:06:21', 0);
COMMIT;

-- ----------------------------
-- Table structure: common_picture_cate 
-- ----------------------------
DROP TABLE IF EXISTS `common_picture_cate`;
CREATE TABLE `common_picture_cate` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `uid` bigint(19) NOT NULL DEFAULT 0 COMMENT '添加账号',
 `weigh` bigint(19) NOT NULL DEFAULT 0 COMMENT '排序',
 `type` tinyint(3) NOT NULL DEFAULT 0 COMMENT '类型0=素材图1=插图,2=两种共有',
 `name` varchar(50) NOT NULL COMMENT '分类名称',
 `status` tinyint(3) NOT NULL DEFAULT 0 COMMENT '状态1=禁用',
 `remark` varchar(255) NOT NULL COMMENT '备注',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间', 
PRIMARY KEY (id)
) COMMENT '分类名称';

-- ----------------------------
-- Data: common_picture_cate 
-- ----------------------------
BEGIN;
INSERT INTO `common_picture_cate` (`id`, `uid`, `weigh`, `type`, `name`, `status`, `remark`, `create_time`, `update_time`) VALUES 
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
COMMIT;

-- ----------------------------
-- Table structure: common_verify_code 
-- ----------------------------
DROP TABLE IF EXISTS `common_verify_code`;
CREATE TABLE `common_verify_code` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `keyname` varchar(50) NOT NULL COMMENT '存储key',
 `code` varchar(20) NOT NULL COMMENT '验证码',
 `create_time` datetime COMMENT '创建时间', 
PRIMARY KEY (id)
) COMMENT '验证码存储';

-- ----------------------------
-- Data: common_verify_code 
-- ----------------------------
BEGIN;
INSERT INTO `common_verify_code` (`id`, `keyname`, `code`, `create_time`) VALUES 
(1, 'huang_li_shi@163.com', '380466', '2025-07-10 15:06:21');
COMMIT;

-- ----------------------------
-- Table structure: login_logs 
-- ----------------------------
DROP TABLE IF EXISTS `login_logs`;
CREATE TABLE `login_logs` (
 `id` bigint(20) NOT NULL AUTO_INCREMENT,
 `type` tinyint(3) NOT NULL DEFAULT 1 COMMENT '类型1=平台。2=b端，3=C端',
 `uid` bigint(19) NOT NULL COMMENT '用户id',
 `out_in` varchar(10) NOT NULL COMMENT '登录或退出 out in',
 `loginIP` varchar(30) NOT NULL COMMENT '登录IP',
 `create_time` datetime COMMENT '创建时间',
 `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间', 
PRIMARY KEY (id)
) COMMENT '（平台及客户）后台登录日志';

-- ----------------------------
-- Data: login_logs 
-- ----------------------------
BEGIN;
INSERT INTO `login_logs` (`id`, `type`, `uid`, `out_in`, `loginIP`, `create_time`, `update_time`) VALUES 
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
(1012, 1, 1, 'in', '', '2025-07-23 15:40:18', '2025-07-23 15:40:18'),
(1013, 1, 1, 'in', '', '2025-08-01 09:24:36', '2025-08-01 09:24:36');
COMMIT;

-- ----------------------------
-- Table structure: meeting_offline 
-- ----------------------------
DROP TABLE IF EXISTS `meeting_offline`;
CREATE TABLE `meeting_offline` (
 `id` bigint(19) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
 `create_time` datetime COMMENT '创建时间',
 `creator_id` bigint(19) COMMENT '创建人ID',
 `creator_name` varchar(200) COMMENT '创建人名称',
 `update_time` datetime COMMENT '更新时间',
 `updater_id` bigint(19) COMMENT '更新人ID',
 `updater_name` varchar(200) COMMENT '更新人名称',
 `name` varchar(200) COMMENT '会议名',
 `meeting_time` datetime COMMENT '会议时间',
 `audio_path` varchar(300) COMMENT '音频路径', 
PRIMARY KEY (id)
);

-- ----------------------------
-- Data: meeting_offline 
-- ----------------------------
BEGIN;
INSERT INTO `meeting_offline` (`id`, `create_time`, `creator_id`, `creator_name`, `update_time`, `updater_id`, `updater_name`, `name`, `meeting_time`, `audio_path`) VALUES 
(6, '2025-07-28 11:38:57', 1, '开发管理员', '2025-07-28 12:13:48', 1, '开发管理员', 'test12', '2025-07-28 08:04:00', '1753673937775.414.19ebc78e-9b50-469c-abb7-97728c5aeba5.asr_speaker_demo.wav'),
(11, '2025-07-28 16:45:25', 1, '开发管理员', '2025-07-28 16:45:25', 1, '开发管理员', 'test213', '2025-07-24 04:45:17', '1753692325372.2095.02071007-c72b-4920-9db3-b162df827181.asr_speaker_demo.wav'),
(12, '2025-07-28 16:57:30', 1, '开发管理员', '2025-07-28 16:57:30', 1, '开发管理员', 'test6', '2025-07-11 03:59:17', '1753693050210.4143.a9cb7063-0925-4092-86f3-84c99e555827.asr_speaker_demo.wav'),
(13, '2025-07-30 12:10:40', 1, '开发管理员', '2025-07-30 12:10:40', 1, '开发管理员', 'test7', '2025-07-26 01:10:33', '1753848640489.6929.6f777452-89f0-411e-8d42-8bb52190c2dc.asr_speaker_demo.wav');
COMMIT;

-- ----------------------------
-- Table structure: meeting_offline_detail 
-- ----------------------------
DROP TABLE IF EXISTS `meeting_offline_detail`;
CREATE TABLE `meeting_offline_detail` (
 `id` bigint(19) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
 `create_time` datetime COMMENT '创建时间',
 `creator_id` bigint(19) COMMENT '创建人ID',
 `creator_name` varchar(200) COMMENT '创建人名称',
 `update_time` datetime COMMENT '更新时间',
 `updater_id` bigint(19) COMMENT '更新人ID',
 `updater_name` varchar(200) COMMENT '更新人名称',
 `meeting_id` bigint(19) COMMENT '会议ID',
 `sort` bigint(19) COMMENT '序号',
 `spk_user_id` bigint(19) COMMENT '发言人ID',
 `spk_time` datetime COMMENT '发言时间，根据发言时长、会议开始时间和发言时间戳自动计算',
 `text` longtext COMMENT '发言内容',
 `wav_path` longtext COMMENT '音频路径',
 `train_status` bigint(19) COMMENT '训练状态，0、不参与训练 66、已完成训练 55、待训练',
 `train_id` bigint(19) COMMENT '训练任务ID', 
PRIMARY KEY (id)
);

-- ----------------------------
-- Data: meeting_offline_detail 
-- ----------------------------
BEGIN;
INSERT INTO `meeting_offline_detail` (`id`, `create_time`, `creator_id`, `creator_name`, `update_time`, `updater_id`, `updater_name`, `meeting_id`, `sort`, `spk_user_id`, `spk_time`, `text`, `wav_path`, `train_status`, `train_id`) VALUES 
(1, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 1, 0, '2025-07-28 00:03:00', '非常高兴哈能够和几位的话呢一起来讨论互联网企业如何决胜全球化新高地这个话题。', 'data/meeting/offline/detail/3/1753671672392/3_50_9810.wav', 0, 0),
(2, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 2, 0, '2025-07-28 00:03:10', '然后第二块其实是游戏平台。', 'data/meeting/offline/detail/3/1753671672392/3_10290_12150.wav', 0, 0),
(3, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 3, 0, '2025-07-28 00:03:12', '所谓游戏平台，', 'data/meeting/offline/detail/3/1753671672392/3_12770_13890.wav', 0, 0),
(4, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 4, 0, '2025-07-28 00:03:14', '它主要是呃简单来说就是一个商店加社区的这样一个模式。', 'data/meeting/offline/detail/3/1753671672392/3_14010_18910.wav', 0, 0),
(5, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 5, 0, '2025-07-28 00:03:19', '而这么多年，', 'data/meeting/offline/detail/3/1753671672392/3_19370_20230.wav', 0, 0),
(6, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 6, 0, '2025-07-28 00:03:20', '我们随着整个业务的拓张呢，', 'data/meeting/offline/detail/3/1753671672392/3_20250_21990.wav', 0, 0),
(7, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 7, 0, '2025-07-28 00:03:21', '会发现跟阿里云有非常紧密的联系。', 'data/meeting/offline/detail/3/1753671672392/3_21990_25330.wav', 0, 0),
(8, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 8, 0, '2025-07-28 00:03:25', '因为刚开始伟光在介绍的时候也讲阿里云也是阿里巴巴的云。', 'data/meeting/offline/detail/3/1753671672392/3_25330_29770.wav', 0, 0),
(9, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 9, 0, '2025-07-28 00:03:29', '所以这个过程中一会儿也可以稍微展开。', 'data/meeting/offline/detail/3/1753671672392/3_29770_32030.wav', 0, 0),
(10, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 10, 0, '2025-07-28 00:03:32', '跟大家讲一下，', 'data/meeting/offline/detail/3/1753671672392/3_32030_32710.wav', 0, 0),
(11, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 11, 0, '2025-07-28 00:03:32', '我们跟云是怎么一路走来的。', 'data/meeting/offline/detail/3/1753671672392/3_32710_35750.wav', 0, 0),
(12, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 12, 0, '2025-07-28 00:03:36', '其实的确的话呢，', 'data/meeting/offline/detail/3/1753671672392/3_36070_37290.wav', 0, 0),
(13, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 13, 0, '2025-07-28 00:03:37', '就对我们互联网公司来说，', 'data/meeting/offline/detail/3/1753671672392/3_37290_38730.wav', 0, 0),
(14, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 14, 0, '2025-07-28 00:03:38', '如果不能够问当地的人口的话，', 'data/meeting/offline/detail/3/1753671672392/3_38750_41050.wav', 0, 0),
(15, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 15, 0, '2025-07-28 00:03:41', '我想我们可能这个整个的就失去了后边所有的这个动力。', 'data/meeting/offline/detail/3/1753671672392/3_41250_46130.wav', 0, 0),
(16, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 16, 0, '2025-07-28 00:03:46', '不知道你们各位怎么看，', 'data/meeting/offline/detail/3/1753671672392/3_46130_47730.wav', 0, 0),
(17, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 17, 0, '2025-07-28 00:03:48', '就是我们最大的这个问题是不是效率优先？', 'data/meeting/offline/detail/3/1753671672392/3_48190_51590.wav', 0, 0),
(18, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 18, 0, '2025-07-28 00:03:51', ' yes，', 'data/meeting/offline/detail/3/1753671672392/3_51590_51830.wav', 0, 0),
(19, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 19, 0, '2025-07-28 00:03:52', ' oh no。', 'data/meeting/offline/detail/3/1753671672392/3_52290_53175.wav', 0, 0),
(20, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 20, 0, '2025-07-28 00:03:54', '然后如果是讲一个最关键的，', 'data/meeting/offline/detail/3/1753671672392/3_54000_58450.wav', 0, 0),
(21, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 21, 0, '2025-07-28 00:03:58', '你们是怎么来克服这些挑战的啊，', 'data/meeting/offline/detail/3/1753671672392/3_58550_62635.wav', 0, 0),
(22, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 22, 0, '2025-07-28 00:04:04', '因因因为其我们最近一直在做海外业务，', 'data/meeting/offline/detail/3/1753671672392/3_64610_66990.wav', 0, 0),
(23, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 23, 0, '2025-07-28 00:04:07', '嗯，', 'data/meeting/offline/detail/3/1753671672392/3_67110_67330.wav', 0, 0),
(24, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 24, 0, '2025-07-28 00:04:07', '就是所以说这呃我们碰到一些问题可以一起分享出来给大家，', 'data/meeting/offline/detail/3/1753671672392/3_67330_71250.wav', 0, 0),
(25, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 25, 0, '2025-07-28 00:04:11', '其实一起探讨一下。', 'data/meeting/offline/detail/3/1753671672392/3_71270_72450.wav', 0, 0),
(26, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 26, 0, '2025-07-28 00:04:12', '嗯嗯，', 'data/meeting/offline/detail/3/1753671672392/3_72450_73350.wav', 0, 0),
(27, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 27, 0, '2025-07-28 00:04:13', '其实海外外就是我我们是这个个观的过是呃无论你准备工作做的有多充分，', 'data/meeting/offline/detail/3/1753671672392/3_73590_81170.wav', 0, 0),
(28, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 28, 0, '2025-07-28 00:04:21', '嗯，', 'data/meeting/offline/detail/3/1753671672392/3_81370_81510.wav', 0, 0),
(29, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 29, 0, '2025-07-28 00:04:21', '无论你有就是呃学习能力有多强，', 'data/meeting/offline/detail/3/1753671672392/3_81510_84970.wav', 0, 0),
(30, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 30, 0, '2025-07-28 00:04:24', '嗯，', 'data/meeting/offline/detail/3/1753671672392/3_84970_85110.wav', 0, 0),
(31, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 31, 0, '2025-07-28 00:04:25', '你一个中企业的负责人，', 'data/meeting/offline/detail/3/1753671672392/3_85110_86330.wav', 0, 0),
(32, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 32, 0, '2025-07-28 00:04:26', '其实在出海的时候，', 'data/meeting/offline/detail/3/1753671672392/3_86330_87510.wav', 0, 0),
(33, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 33, 0, '2025-07-28 00:04:28', '呃，', 'data/meeting/offline/detail/3/1753671672392/3_88050_88290.wav', 0, 0),
(34, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 34, 0, '2025-07-28 00:04:28', '他整体还是一个强试错的过程。', 'data/meeting/offline/detail/3/1753671672392/3_88350_90150.wav', 0, 0),
(35, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 35, 0, '2025-07-28 00:04:30', '嗯，', 'data/meeting/offline/detail/3/1753671672392/3_90410_90650.wav', 0, 0),
(36, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 36, 0, '2025-07-28 00:04:30', '后来退退德国或者拓大新加坡、', 'data/meeting/offline/detail/3/1753671672392/3_90750_93030.wav', 0, 0),
(37, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 37, 0, '2025-07-28 00:04:33', '印尼、', 'data/meeting/offline/detail/3/1753671672392/3_93110_93530.wav', 0, 0),
(38, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 38, 0, '2025-07-28 00:04:33', '越南等等等些地方方，', 'data/meeting/offline/detail/3/1753671672392/3_93530_95290.wav', 0, 0),
(39, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 39, 0, '2025-07-28 00:04:35', '每一个地方走过去都面临的一个问题是建站的效率怎么样能够快速的把这这站站能建起来。', 'data/meeting/offline/detail/3/1753671672392/3_95610_101570.wav', 0, 0),
(40, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 40, 0, '2025-07-28 00:04:41', '一方面我们当初刚好从一四年刚好开始要出去的时候呢，', 'data/meeting/offline/detail/3/1753671672392/3_101570_105270.wav', 0, 0),
(41, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 41, 0, '2025-07-28 00:04:45', '去国内就是三个北上广深。', 'data/meeting/offline/detail/3/1753671672392/3_105530_108085.wav', 0, 0),
(42, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 42, 0, '2025-07-28 00:04:48', '那当在海外呢？', 'data/meeting/offline/detail/3/1753671672392/3_108750_109730.wav', 0, 0),
(43, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 43, 0, '2025-07-28 00:04:49', '要同时开服北美美东美西对吧？', 'data/meeting/offline/detail/3/1753671672392/3_109730_112850.wav', 0, 0),
(44, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 44, 0, '2025-07-28 00:04:52', '欧洲、', 'data/meeting/offline/detail/3/1753671672392/3_112850_113270.wav', 0, 0),
(45, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 45, 0, '2025-07-28 00:04:53', '日本，', 'data/meeting/offline/detail/3/1753671672392/3_113410_113850.wav', 0, 0),
(46, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 46, 0, '2025-07-28 00:04:54', '那我还记得那个时候，', 'data/meeting/offline/detail/3/1753671672392/3_114190_115230.wav', 0, 0),
(47, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 47, 0, '2025-07-28 00:04:55', '那我们在海外如何去建立这种 IDC 的勘探建设、', 'data/meeting/offline/detail/3/1753671672392/3_115230_118510.wav', 0, 0),
(48, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 48, 0, '2025-07-28 00:04:58', '基础设施，', 'data/meeting/offline/detail/3/1753671672392/3_118730_119290.wav', 0, 0),
(49, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 49, 0, '2025-07-28 00:04:59', '建设云服务的部署，', 'data/meeting/offline/detail/3/1753671672392/3_119290_120890.wav', 0, 0),
(50, '2025-07-28 03:01:43', 1, 'gofly', '2025-07-28 03:01:43', 1, 'gofly', 3, 50, 0, '2025-07-28 00:05:01', '那都是一个全新的挑战。', 'data/meeting/offline/detail/3/1753671672392/3_121370_122805.wav', 0, 0),
(51, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 1, 0, '2025-07-28 00:05:00', '非常高兴哈能够和几位的话呢一起来讨论互联网企业如何决胜全球化新高地这个话题。', 'data/meeting/offline/detail/4/1753671968129/4_50_9810.wav', 0, 0),
(52, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 2, 0, '2025-07-28 00:05:10', '然后第二块其实是游戏平台。', 'data/meeting/offline/detail/4/1753671968129/4_10290_12150.wav', 0, 0),
(53, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 3, 0, '2025-07-28 00:05:12', '所谓游戏平台，', 'data/meeting/offline/detail/4/1753671968129/4_12790_13890.wav', 0, 0),
(54, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 4, 0, '2025-07-28 00:05:14', '它主要是呃简单来说就是一个商店加社区的这样一个模式。', 'data/meeting/offline/detail/4/1753671968129/4_14010_18910.wav', 0, 0),
(55, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 5, 0, '2025-07-28 00:05:19', '而这么多年，', 'data/meeting/offline/detail/4/1753671968129/4_19350_20230.wav', 0, 0),
(56, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 6, 0, '2025-07-28 00:05:20', '我们随着整个业务的拓张呢，', 'data/meeting/offline/detail/4/1753671968129/4_20250_21990.wav', 0, 0),
(57, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 7, 0, '2025-07-28 00:05:21', '会发现跟阿里云有非常紧密的联系。', 'data/meeting/offline/detail/4/1753671968129/4_21990_25330.wav', 0, 0),
(58, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 8, 0, '2025-07-28 00:05:25', '因为刚开始伟光在介绍的时候也讲阿里云也是阿里巴巴的云。', 'data/meeting/offline/detail/4/1753671968129/4_25330_29770.wav', 0, 0),
(59, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 9, 0, '2025-07-28 00:05:29', '所以这个过程中一会儿也可以稍微展开。', 'data/meeting/offline/detail/4/1753671968129/4_29770_32030.wav', 0, 0),
(60, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 10, 0, '2025-07-28 00:05:32', '跟大家讲一下，', 'data/meeting/offline/detail/4/1753671968129/4_32030_32710.wav', 0, 0),
(61, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 11, 0, '2025-07-28 00:05:32', '我们跟云是怎么一路走来的。', 'data/meeting/offline/detail/4/1753671968129/4_32710_35750.wav', 0, 0),
(62, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 12, 0, '2025-07-28 00:05:36', '其实的确的话呢，', 'data/meeting/offline/detail/4/1753671968129/4_36070_37290.wav', 0, 0),
(63, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 13, 0, '2025-07-28 00:05:37', '就对我们互联网公司来说，', 'data/meeting/offline/detail/4/1753671968129/4_37290_38730.wav', 0, 0),
(64, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 14, 0, '2025-07-28 00:05:38', '如果不能够问当地的人口的话，', 'data/meeting/offline/detail/4/1753671968129/4_38750_41050.wav', 0, 0),
(65, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 15, 0, '2025-07-28 00:05:41', '我想我们可能这个整个的就失去了后边所有的这个动力。', 'data/meeting/offline/detail/4/1753671968129/4_41250_46130.wav', 0, 0),
(66, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 16, 0, '2025-07-28 00:05:46', '不知道你们各位怎么看，', 'data/meeting/offline/detail/4/1753671968129/4_46130_47730.wav', 0, 0),
(67, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 17, 0, '2025-07-28 00:05:48', '就是我们最大的这个问题是不是效率优先？', 'data/meeting/offline/detail/4/1753671968129/4_48190_51590.wav', 0, 0),
(68, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 18, 0, '2025-07-28 00:05:51', ' yes，', 'data/meeting/offline/detail/4/1753671968129/4_51590_51830.wav', 0, 0),
(69, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 19, 0, '2025-07-28 00:05:52', ' oh no。', 'data/meeting/offline/detail/4/1753671968129/4_52290_53175.wav', 0, 0),
(70, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 20, 0, '2025-07-28 00:05:54', '然后如果是讲一个最关键的，', 'data/meeting/offline/detail/4/1753671968129/4_54000_58450.wav', 0, 0),
(71, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 21, 0, '2025-07-28 00:05:58', '你们是怎么来克服这些挑战的啊，', 'data/meeting/offline/detail/4/1753671968129/4_58550_62635.wav', 0, 0),
(72, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 22, 0, '2025-07-28 00:06:04', '因因因为其我们最近一直在做海外业务，', 'data/meeting/offline/detail/4/1753671968129/4_64610_66990.wav', 0, 0),
(73, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 23, 0, '2025-07-28 00:06:07', '嗯，', 'data/meeting/offline/detail/4/1753671968129/4_67110_67330.wav', 0, 0),
(74, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 24, 0, '2025-07-28 00:06:07', '就是所以说这呃我们碰到了些问题，', 'data/meeting/offline/detail/4/1753671968129/4_67330_69410.wav', 0, 0),
(75, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 25, 0, '2025-07-28 00:06:09', '可以一起分享出来给大家，', 'data/meeting/offline/detail/4/1753671968129/4_69410_71250.wav', 0, 0),
(76, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 26, 0, '2025-07-28 00:06:11', '其实一起探讨一下。', 'data/meeting/offline/detail/4/1753671968129/4_71270_72450.wav', 0, 0),
(77, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 27, 0, '2025-07-28 00:06:12', '嗯，', 'data/meeting/offline/detail/4/1753671968129/4_72450_72690.wav', 0, 0),
(78, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 28, 0, '2025-07-28 00:06:13', '呃其实海外外就是我我们是这个强观的说是呃无论你准备工作做的有多充分，', 'data/meeting/offline/detail/4/1753671968129/4_73110_80870.wav', 0, 0),
(79, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 29, 0, '2025-07-28 00:06:21', '嗯，', 'data/meeting/offline/detail/4/1753671968129/4_81370_81510.wav', 0, 0),
(80, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 30, 0, '2025-07-28 00:06:21', '无论你有就是呃学习能力有多强。', 'data/meeting/offline/detail/4/1753671968129/4_81510_84650.wav', 0, 0),
(81, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 31, 0, '2025-07-28 00:06:24', '嗯，', 'data/meeting/offline/detail/4/1753671968129/4_84970_85110.wav', 0, 0),
(82, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 32, 0, '2025-07-28 00:06:25', '一个中国企业的负责人，', 'data/meeting/offline/detail/4/1753671968129/4_85110_86330.wav', 0, 0),
(83, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 33, 0, '2025-07-28 00:06:26', '其实在出海的时候，', 'data/meeting/offline/detail/4/1753671968129/4_86330_87510.wav', 0, 0),
(84, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 34, 0, '2025-07-28 00:06:28', '呃，', 'data/meeting/offline/detail/4/1753671968129/4_88050_88290.wav', 0, 0),
(85, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 35, 0, '2025-07-28 00:06:28', '他整体还是一个强试错的过程。', 'data/meeting/offline/detail/4/1753671968129/4_88350_90150.wav', 0, 0),
(86, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 36, 0, '2025-07-28 00:06:30', '嗯，', 'data/meeting/offline/detail/4/1753671968129/4_90390_90630.wav', 0, 0),
(87, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 37, 0, '2025-07-28 00:06:30', '后来退到德国或者拓大新加坡、', 'data/meeting/offline/detail/4/1753671968129/4_90750_93030.wav', 0, 0),
(88, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 38, 0, '2025-07-28 00:06:33', '印尼、', 'data/meeting/offline/detail/4/1753671968129/4_93110_93530.wav', 0, 0),
(89, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 39, 0, '2025-07-28 00:06:33', '越南等等这些地方。', 'data/meeting/offline/detail/4/1753671968129/4_93530_94770.wav', 0, 0),
(90, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 40, 0, '2025-07-28 00:06:35', '那每一个地方走过去都面临的一个问题是建站的效率一么样能够快速的把这个站点能建起来。', 'data/meeting/offline/detail/4/1753671968129/4_95070_101570.wav', 0, 0),
(91, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 41, 0, '2025-07-28 00:06:41', '一方面我们当初刚好从一四年刚好开始要出去的时候呢，', 'data/meeting/offline/detail/4/1753671968129/4_101570_105270.wav', 0, 0),
(92, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 42, 0, '2025-07-28 00:06:45', '去国内就是三个北上广深。', 'data/meeting/offline/detail/4/1753671968129/4_105550_108085.wav', 0, 0),
(93, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 43, 0, '2025-07-28 00:06:48', '那当在海外呢？', 'data/meeting/offline/detail/4/1753671968129/4_108750_109730.wav', 0, 0),
(94, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 44, 0, '2025-07-28 00:06:49', '要同时开服北美美东美西对吧？', 'data/meeting/offline/detail/4/1753671968129/4_109730_112850.wav', 0, 0),
(95, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 45, 0, '2025-07-28 00:06:52', '欧洲、', 'data/meeting/offline/detail/4/1753671968129/4_112850_113270.wav', 0, 0),
(96, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 46, 0, '2025-07-28 00:06:53', '日本，', 'data/meeting/offline/detail/4/1753671968129/4_113410_113850.wav', 0, 0),
(97, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 47, 0, '2025-07-28 00:06:54', '那我还记得那个时候，', 'data/meeting/offline/detail/4/1753671968129/4_114190_115230.wav', 0, 0),
(98, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 48, 0, '2025-07-28 00:06:55', '那我们在海外如何去建立这种 IDC 的勘探建设、', 'data/meeting/offline/detail/4/1753671968129/4_115230_118510.wav', 0, 0),
(99, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 11:06:24', 1, '开发管理员', 4, 49, 0, '2025-07-28 00:06:58', '基础设施，', 'data/meeting/offline/detail/4/1753671968129/4_118730_119290.wav', 0, 0),
(100, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 50, 0, '2025-07-28 00:06:59', '建设云服务的部署，', 'data/meeting/offline/detail/4/1753671968129/4_119290_120890.wav', 0, 0),
(101, '2025-07-28 03:06:13', 1, 'gofly', '2025-07-28 03:06:13', 1, 'gofly', 4, 51, 0, '2025-07-28 00:07:01', '那都是一个全新的挑战。', 'data/meeting/offline/detail/4/1753671968129/4_121370_122805.wav', 0, 0),
(102, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 1, 0, '2025-07-28 00:05:00', '非常高兴哈能够和几位的话呢一起来讨论互联网企业如何决胜全球化新高地这个话题。', 'data/meeting/offline/detail/5/1753672704946/5_50_9810.wav', 0, 0),
(103, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 2, 0, '2025-07-28 00:05:10', '然后第二块其实是游戏平台。', 'data/meeting/offline/detail/5/1753672704946/5_10290_12150.wav', 0, 0),
(104, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 3, 0, '2025-07-28 00:05:12', '所谓游戏平台，', 'data/meeting/offline/detail/5/1753672704946/5_12770_13890.wav', 0, 0),
(105, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 4, 0, '2025-07-28 00:05:14', '它主要是呃简单来说就是一个商店加社区的这样一个模式。', 'data/meeting/offline/detail/5/1753672704946/5_14010_18910.wav', 0, 0),
(106, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 5, 0, '2025-07-28 00:05:19', '而这么多年，', 'data/meeting/offline/detail/5/1753672704946/5_19370_20230.wav', 0, 0),
(107, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 6, 0, '2025-07-28 00:05:20', '我们随着整个业务的拓张呢，', 'data/meeting/offline/detail/5/1753672704946/5_20250_21990.wav', 0, 0),
(108, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 7, 0, '2025-07-28 00:05:21', '会发现跟阿里云有非常紧密的联系。', 'data/meeting/offline/detail/5/1753672704946/5_21990_25330.wav', 0, 0),
(109, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 8, 0, '2025-07-28 00:05:25', '因为刚开始伟光在介绍的时候也讲阿里云也是阿里巴巴的云。', 'data/meeting/offline/detail/5/1753672704946/5_25330_29770.wav', 0, 0),
(110, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 9, 0, '2025-07-28 00:05:29', '所以这个过程中一会儿也可以稍微展开。', 'data/meeting/offline/detail/5/1753672704946/5_29770_32030.wav', 0, 0),
(111, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 10, 0, '2025-07-28 00:05:32', '跟大家讲一下，', 'data/meeting/offline/detail/5/1753672704946/5_32030_32710.wav', 0, 0),
(112, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 11, 0, '2025-07-28 00:05:32', '我们跟云是怎么一路走来的。', 'data/meeting/offline/detail/5/1753672704946/5_32710_35750.wav', 0, 0),
(113, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 12, 0, '2025-07-28 00:05:36', '其实的确的话呢，', 'data/meeting/offline/detail/5/1753672704946/5_36070_37290.wav', 0, 0),
(114, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 13, 0, '2025-07-28 00:05:37', '就对我们互联网公司来说，', 'data/meeting/offline/detail/5/1753672704946/5_37290_38730.wav', 0, 0),
(115, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 14, 0, '2025-07-28 00:05:38', '如果不能够问当地的人口的话，', 'data/meeting/offline/detail/5/1753672704946/5_38750_41050.wav', 0, 0),
(116, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 15, 0, '2025-07-28 00:05:41', '我想我们可能这个整个的就失去了后边所有的这个动力。', 'data/meeting/offline/detail/5/1753672704946/5_41250_46130.wav', 0, 0),
(117, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 16, 0, '2025-07-28 00:05:46', '不知道你们各位怎么看，', 'data/meeting/offline/detail/5/1753672704946/5_46130_47730.wav', 0, 0),
(118, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 17, 0, '2025-07-28 00:05:48', '就是我们最大的这个问题是不是效率优先？', 'data/meeting/offline/detail/5/1753672704946/5_48190_51590.wav', 0, 0),
(119, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 18, 0, '2025-07-28 00:05:51', ' yes，', 'data/meeting/offline/detail/5/1753672704946/5_51590_51830.wav', 0, 0),
(120, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 19, 0, '2025-07-28 00:05:52', ' oh no。', 'data/meeting/offline/detail/5/1753672704946/5_52290_53175.wav', 0, 0),
(121, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 20, 0, '2025-07-28 00:05:54', '然后如果是讲一个最关键的，', 'data/meeting/offline/detail/5/1753672704946/5_54000_58450.wav', 0, 0),
(122, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 21, 0, '2025-07-28 00:05:58', '你们是怎么来克服这些挑战的啊，', 'data/meeting/offline/detail/5/1753672704946/5_58550_62635.wav', 0, 0),
(123, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 22, 0, '2025-07-28 00:06:04', '因因因为其我们最近一直在做海外业务，', 'data/meeting/offline/detail/5/1753672704946/5_64610_66990.wav', 0, 0),
(124, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 23, 0, '2025-07-28 00:06:07', '嗯，', 'data/meeting/offline/detail/5/1753672704946/5_67110_67330.wav', 0, 0),
(125, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 24, 0, '2025-07-28 00:06:07', '就是所以说这呃我们碰到一些问题可以一起分享出来给大家，', 'data/meeting/offline/detail/5/1753672704946/5_67330_71250.wav', 0, 0),
(126, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 25, 0, '2025-07-28 00:06:11', '其实一起探讨一下。', 'data/meeting/offline/detail/5/1753672704946/5_71270_72450.wav', 0, 0),
(127, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 26, 0, '2025-07-28 00:06:12', '嗯嗯，', 'data/meeting/offline/detail/5/1753672704946/5_72450_73350.wav', 0, 0),
(128, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 27, 0, '2025-07-28 00:06:13', '其实海外外就是我我们是这个个观的过是呃无论你准备工作做的有多充分，', 'data/meeting/offline/detail/5/1753672704946/5_73590_81170.wav', 0, 0),
(129, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 28, 0, '2025-07-28 00:06:21', '嗯，', 'data/meeting/offline/detail/5/1753672704946/5_81370_81510.wav', 0, 0),
(130, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 29, 0, '2025-07-28 00:06:21', '无论你有就是呃学习能力有多强，', 'data/meeting/offline/detail/5/1753672704946/5_81510_84970.wav', 0, 0),
(131, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 30, 0, '2025-07-28 00:06:24', '嗯，', 'data/meeting/offline/detail/5/1753672704946/5_84970_85110.wav', 0, 0),
(132, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 31, 0, '2025-07-28 00:06:25', '你一个中企业的负责人，', 'data/meeting/offline/detail/5/1753672704946/5_85110_86330.wav', 0, 0),
(133, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 32, 0, '2025-07-28 00:06:26', '其实在出海的时候，', 'data/meeting/offline/detail/5/1753672704946/5_86330_87510.wav', 0, 0),
(134, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 33, 0, '2025-07-28 00:06:28', '呃，', 'data/meeting/offline/detail/5/1753672704946/5_88050_88290.wav', 0, 0),
(135, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 34, 0, '2025-07-28 00:06:28', '他整体还是一个强试错的过程。', 'data/meeting/offline/detail/5/1753672704946/5_88350_90150.wav', 0, 0),
(136, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 35, 0, '2025-07-28 00:06:30', '嗯，', 'data/meeting/offline/detail/5/1753672704946/5_90410_90650.wav', 0, 0),
(137, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 36, 0, '2025-07-28 00:06:30', '后来退退德国或者拓大新加坡、', 'data/meeting/offline/detail/5/1753672704946/5_90750_93030.wav', 0, 0),
(138, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 37, 0, '2025-07-28 00:06:33', '印尼、', 'data/meeting/offline/detail/5/1753672704946/5_93110_93530.wav', 0, 0),
(139, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 38, 0, '2025-07-28 00:06:33', '越南等等等些地方方，', 'data/meeting/offline/detail/5/1753672704946/5_93530_95290.wav', 0, 0),
(140, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 39, 0, '2025-07-28 00:06:35', '每一个地方走过去都面临的一个问题是建站的效率怎么样能够快速的把这这站站能建起来。', 'data/meeting/offline/detail/5/1753672704946/5_95610_101570.wav', 0, 0),
(141, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 40, 0, '2025-07-28 00:06:41', '一方面我们当初刚好从一四年刚好开始要出去的时候呢，', 'data/meeting/offline/detail/5/1753672704946/5_101570_105270.wav', 0, 0),
(142, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 41, 0, '2025-07-28 00:06:45', '去国内就是三个北上广深。', 'data/meeting/offline/detail/5/1753672704946/5_105530_108085.wav', 0, 0),
(143, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 42, 0, '2025-07-28 00:06:48', '那当在海外呢？', 'data/meeting/offline/detail/5/1753672704946/5_108750_109730.wav', 0, 0),
(144, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 43, 0, '2025-07-28 00:06:49', '要同时开服北美美东美西对吧？', 'data/meeting/offline/detail/5/1753672704946/5_109730_112850.wav', 0, 0),
(145, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 44, 0, '2025-07-28 00:06:52', '欧洲、', 'data/meeting/offline/detail/5/1753672704946/5_112850_113270.wav', 0, 0),
(146, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 45, 0, '2025-07-28 00:06:53', '日本，', 'data/meeting/offline/detail/5/1753672704946/5_113410_113850.wav', 0, 0),
(147, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 46, 0, '2025-07-28 00:06:54', '那我还记得那个时候，', 'data/meeting/offline/detail/5/1753672704946/5_114190_115230.wav', 0, 0),
(148, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 47, 0, '2025-07-28 00:06:55', '那我们在海外如何去建立这种 IDC 的勘探建设、', 'data/meeting/offline/detail/5/1753672704946/5_115230_118510.wav', 0, 0),
(149, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 48, 0, '2025-07-28 00:06:58', '基础设施，', 'data/meeting/offline/detail/5/1753672704946/5_118730_119290.wav', 0, 0),
(150, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 49, 0, '2025-07-28 00:06:59', '建设云服务的部署，', 'data/meeting/offline/detail/5/1753672704946/5_119290_120890.wav', 0, 0),
(151, '2025-07-28 03:18:28', 1, 'gofly', '2025-07-28 03:18:28', 1, 'gofly', 5, 50, 0, '2025-07-28 00:07:01', '那都是一个全新的挑战。', 'data/meeting/offline/detail/5/1753672704946/5_121370_122805.wav', 0, 0),
(152, '2025-07-28 03:39:00', 1, 'gofly', '2025-07-28 16:39:56', 1, '开发管理员', 6, 1, 0, '2025-07-28 00:04:00', '非常高兴哈能够和几位的话呢一起来讨论互联网企业如何决胜全球化新高地这个话题。', '1753673937821/6_50_9810.wav', 55, 0),
(153, '2025-07-28 03:39:00', 1, 'gofly', '2025-07-28 03:39:00', 1, 'gofly', 6, 2, 0, '2025-07-28 00:04:10', '然后第二块其实是游戏平台。', '1753673937821/6_10290_12150.wav', 0, 0),
(154, '2025-07-28 03:39:00', 1, 'gofly', '2025-07-28 03:39:00', 1, 'gofly', 6, 3, 0, '2025-07-28 00:04:12', '所谓游戏平台，', '1753673937821/6_12770_13890.wav', 0, 0),
(155, '2025-07-28 03:39:00', 1, 'gofly', '2025-07-28 03:39:00', 1, 'gofly', 6, 4, 0, '2025-07-28 00:04:14', '它主要是呃简单来说就是一个商店加社区的这样一个模式。', '1753673937821/6_14010_18910.wav', 0, 0),
(156, '2025-07-28 03:39:00', 1, 'gofly', '2025-07-28 03:39:00', 1, 'gofly', 6, 5, 0, '2025-07-28 00:04:19', '而这么多年，', '1753673937821/6_19370_20230.wav', 0, 0),
(157, '2025-07-28 03:39:00', 1, 'gofly', '2025-07-28 03:39:00', 1, 'gofly', 6, 6, 0, '2025-07-28 00:04:20', '我们随着整个业务的拓张呢，', '1753673937821/6_20250_21990.wav', 0, 0),
(158, '2025-07-28 03:39:00', 1, 'gofly', '2025-07-28 03:39:00', 1, 'gofly', 6, 7, 0, '2025-07-28 00:04:21', '会发现跟阿里云有非常紧密的联系。', '1753673937821/6_21990_25330.wav', 0, 0),
(159, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 8, 0, '2025-07-28 00:04:25', '因为刚开始伟光在介绍的时候也讲阿里云也是阿里巴巴的云。', '1753673937821/6_25330_29770.wav', 0, 0),
(160, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 9, 0, '2025-07-28 00:04:29', '所以这个过程中一会儿也可以稍微展开。', '1753673937821/6_29770_32030.wav', 0, 0),
(161, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 10, 0, '2025-07-28 00:04:32', '跟大家讲一下，', '1753673937821/6_32030_32710.wav', 0, 0),
(162, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 11, 0, '2025-07-28 00:04:32', '我们跟云是怎么一路走来的。', '1753673937821/6_32710_35750.wav', 0, 0),
(163, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 12, 0, '2025-07-28 00:04:36', '其实的确的话呢，', '1753673937821/6_36070_37290.wav', 0, 0),
(164, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 13, 0, '2025-07-28 00:04:37', '就对我们互联网公司来说，', '1753673937821/6_37290_38730.wav', 0, 0),
(165, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 14, 0, '2025-07-28 00:04:38', '如果不能够问当地的人口的话，', '1753673937821/6_38750_41050.wav', 0, 0),
(166, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 15, 0, '2025-07-28 00:04:41', '我想我们可能这个整个的就失去了后边所有的这个动力。', '1753673937821/6_41250_46130.wav', 0, 0),
(167, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 16, 0, '2025-07-28 00:04:46', '不知道你们各位怎么看，', '1753673937821/6_46130_47730.wav', 0, 0),
(168, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 17, 0, '2025-07-28 00:04:48', '就是我们最大的这个问题是不是效率优先？', '1753673937821/6_48190_51590.wav', 0, 0),
(169, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 18, 0, '2025-07-28 00:04:51', ' yes，', '1753673937821/6_51590_51830.wav', 0, 0),
(170, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 19, 0, '2025-07-28 00:04:52', ' oh no。', '1753673937821/6_52290_53175.wav', 0, 0),
(171, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 20, 0, '2025-07-28 00:04:54', '然后如果是讲一个最关键的，', '1753673937821/6_54000_58450.wav', 0, 0),
(172, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 21, 0, '2025-07-28 00:04:58', '你们是怎么来克服这些挑战的啊，', '1753673937821/6_58550_62635.wav', 0, 0),
(173, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 22, 0, '2025-07-28 00:05:04', '因因因为其我们最近一直在做海外业务，', '1753673937821/6_64610_66990.wav', 0, 0),
(174, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 23, 0, '2025-07-28 00:05:07', '嗯，', '1753673937821/6_67110_67330.wav', 0, 0),
(175, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 24, 0, '2025-07-28 00:05:07', '就是所以说这呃我们碰到一些问题可以一起分享出来给大家，', '1753673937821/6_67330_71250.wav', 0, 0),
(176, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 25, 0, '2025-07-28 00:05:11', '其实一起探讨一下。', '1753673937821/6_71270_72450.wav', 0, 0),
(177, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 26, 0, '2025-07-28 00:05:12', '嗯嗯，', '1753673937821/6_72450_73350.wav', 0, 0),
(178, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 27, 0, '2025-07-28 00:05:13', '其实海外外就是我我们是这个个观的过是呃无论你准备工作做的有多充分，', '1753673937821/6_73590_81170.wav', 0, 0),
(179, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 28, 0, '2025-07-28 00:05:21', '嗯，', '1753673937821/6_81370_81510.wav', 0, 0),
(180, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 29, 0, '2025-07-28 00:05:21', '无论你有就是呃学习能力有多强，', '1753673937821/6_81510_84970.wav', 0, 0),
(181, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 30, 0, '2025-07-28 00:05:24', '嗯，', '1753673937821/6_84970_85110.wav', 0, 0),
(182, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 31, 0, '2025-07-28 00:05:25', '你一个中企业的负责人，', '1753673937821/6_85110_86330.wav', 0, 0),
(183, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 32, 0, '2025-07-28 00:05:26', '其实在出海的时候，', '1753673937821/6_86330_87510.wav', 0, 0),
(184, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 33, 0, '2025-07-28 00:05:28', '呃，', '1753673937821/6_88050_88290.wav', 0, 0),
(185, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 34, 0, '2025-07-28 00:05:28', '他整体还是一个强试错的过程。', '1753673937821/6_88350_90150.wav', 0, 0),
(186, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 35, 0, '2025-07-28 00:05:30', '嗯，', '1753673937821/6_90410_90650.wav', 0, 0),
(187, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 36, 0, '2025-07-28 00:05:30', '后来退退德国或者拓大新加坡、', '1753673937821/6_90750_93030.wav', 0, 0),
(188, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 37, 0, '2025-07-28 00:05:33', '印尼、', '1753673937821/6_93110_93530.wav', 0, 0),
(189, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 38, 0, '2025-07-28 00:05:33', '越南等等等些地方方，', '1753673937821/6_93530_95290.wav', 0, 0),
(190, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 39, 0, '2025-07-28 00:05:35', '每一个地方走过去都面临的一个问题是建站的效率怎么样能够快速的把这这站站能建起来。', '1753673937821/6_95610_101570.wav', 0, 0),
(191, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 40, 0, '2025-07-28 00:05:41', '一方面我们当初刚好从一四年刚好开始要出去的时候呢，', '1753673937821/6_101570_105270.wav', 0, 0),
(192, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 41, 0, '2025-07-28 00:05:45', '去国内就是三个北上广深。', '1753673937821/6_105530_108085.wav', 0, 0),
(193, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 42, 0, '2025-07-28 00:05:48', '那当在海外呢？', '1753673937821/6_108750_109730.wav', 0, 0),
(194, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 43, 0, '2025-07-28 00:05:49', '要同时开服北美美东美西对吧？', '1753673937821/6_109730_112850.wav', 0, 0),
(195, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 44, 0, '2025-07-28 00:05:52', '欧洲、', '1753673937821/6_112850_113270.wav', 0, 0),
(196, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 45, 0, '2025-07-28 00:05:53', '日本，', '1753673937821/6_113410_113850.wav', 0, 0),
(197, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 46, 0, '2025-07-28 00:05:54', '那我还记得那个时候，', '1753673937821/6_114190_115230.wav', 0, 0),
(198, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 47, 0, '2025-07-28 00:05:55', '那我们在海外如何去建立这种 IDC 的勘探建设、', '1753673937821/6_115230_118510.wav', 0, 0),
(199, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 48, 0, '2025-07-28 00:05:58', '基础设施，', '1753673937821/6_118730_119290.wav', 0, 0),
(200, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 49, 0, '2025-07-28 00:05:59', '建设云服务的部署，', '1753673937821/6_119290_120890.wav', 0, 0),
(201, '2025-07-28 03:39:01', 1, 'gofly', '2025-07-28 03:39:01', 1, 'gofly', 6, 50, 0, '2025-07-28 00:06:01', '那都是一个全新的挑战。', '1753673937821/6_121370_122805.wav', 0, 0),
(202, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 1, 16, '2025-07-28 06:00:00', '非常高兴哈能够和几位的话呢一起来讨论互联网企业如何决胜全球化新高地这个话题。', '1753690770126/9_50_9810.wav', 0, 0),
(203, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 2, 21, '2025-07-28 06:00:10', '然后第二块其实是游戏平台。', '1753690770126/9_10290_12150.wav', 0, 0),
(204, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 3, 21, '2025-07-28 06:00:12', '所谓游戏平台，', '1753690770126/9_12770_13890.wav', 0, 0),
(205, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 4, 21, '2025-07-28 06:00:14', '它主要是呃简单来说就是一个商店加社区的这样一个模式。', '1753690770126/9_14010_18910.wav', 0, 0),
(206, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 5, 22, '2025-07-28 06:00:19', '而这么多年，', '1753690770126/9_19370_20230.wav', 0, 0),
(207, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 6, 22, '2025-07-28 06:00:20', '我们随着整个业务的拓张呢，', '1753690770126/9_20250_21990.wav', 0, 0),
(208, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 7, 22, '2025-07-28 06:00:21', '会发现跟阿里云有非常紧密的联系。', '1753690770126/9_21990_25330.wav', 0, 0),
(209, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 8, 22, '2025-07-28 06:00:25', '因为刚开始伟光在介绍的时候也讲阿里云也是阿里巴巴的云。', '1753690770126/9_25330_29770.wav', 0, 0),
(210, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 9, 22, '2025-07-28 06:00:29', '所以这个过程中一会儿也可以稍微展开。', '1753690770126/9_29770_32030.wav', 0, 0),
(211, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 10, 22, '2025-07-28 06:00:32', '跟大家讲一下，', '1753690770126/9_32030_32710.wav', 0, 0),
(212, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 11, 22, '2025-07-28 06:00:32', '我们跟云是怎么一路走来的。', '1753690770126/9_32710_35750.wav', 0, 0),
(213, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 12, 16, '2025-07-28 06:00:36', '其实的确的话呢，', '1753690770126/9_36070_37290.wav', 0, 0),
(214, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 13, 16, '2025-07-28 06:00:37', '就对我们互联网公司来说，', '1753690770126/9_37290_38730.wav', 0, 0),
(215, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 14, 16, '2025-07-28 06:00:38', '如果不能够问当地的人口的话，', '1753690770126/9_38750_41050.wav', 0, 0),
(216, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 15, 16, '2025-07-28 06:00:41', '我想我们可能这个整个的就失去了后边所有的这个动力。', '1753690770126/9_41250_46130.wav', 0, 0),
(217, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 16, 16, '2025-07-28 06:00:46', '不知道你们各位怎么看，', '1753690770126/9_46130_47730.wav', 0, 0),
(218, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 17, 16, '2025-07-28 06:00:48', '就是我们最大的这个问题是不是效率优先？', '1753690770126/9_48190_51590.wav', 0, 0),
(219, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 18, 16, '2025-07-28 06:00:51', ' yes，', '1753690770126/9_51590_51830.wav', 0, 0),
(220, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 19, 16, '2025-07-28 06:00:52', ' oh no。', '1753690770126/9_52290_53175.wav', 0, 0),
(221, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 20, 16, '2025-07-28 06:00:54', '然后如果是讲一个最关键的，', '1753690770126/9_54000_58450.wav', 0, 0),
(222, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 21, 16, '2025-07-28 06:00:58', '你们是怎么来克服这些挑战的啊，', '1753690770126/9_58550_62635.wav', 0, 0),
(223, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 22, 21, '2025-07-28 06:01:04', '因因因为其我们最近一直在做海外业务，', '1753690770126/9_64610_66990.wav', 0, 0),
(224, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 23, 21, '2025-07-28 06:01:07', '嗯，', '1753690770126/9_67110_67330.wav', 0, 0),
(225, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 24, 21, '2025-07-28 06:01:07', '就是所以说这呃我们碰到一些问题可以一起分享出来给大家，', '1753690770126/9_67330_71250.wav', 0, 0),
(226, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 25, 21, '2025-07-28 06:01:11', '其实一起探讨一下。', '1753690770126/9_71270_72450.wav', 0, 0),
(227, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 26, 21, '2025-07-28 06:01:12', '嗯嗯，', '1753690770126/9_72450_73350.wav', 0, 0),
(228, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 27, 21, '2025-07-28 06:01:13', '其实海外外就是我我们是这个个观的过是呃无论你准备工作做的有多充分，', '1753690770126/9_73590_81170.wav', 0, 0),
(229, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 28, 21, '2025-07-28 06:01:21', '嗯，', '1753690770126/9_81370_81510.wav', 0, 0),
(230, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 29, 21, '2025-07-28 06:01:21', '无论你有就是呃学习能力有多强，', '1753690770126/9_81510_84970.wav', 0, 0),
(231, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 30, 21, '2025-07-28 06:01:24', '嗯，', '1753690770126/9_84970_85110.wav', 0, 0),
(232, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 31, 21, '2025-07-28 06:01:25', '你一个中企业的负责人，', '1753690770126/9_85110_86330.wav', 0, 0),
(233, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 32, 21, '2025-07-28 06:01:26', '其实在出海的时候，', '1753690770126/9_86330_87510.wav', 0, 0),
(234, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 33, 21, '2025-07-28 06:01:28', '呃，', '1753690770126/9_88050_88290.wav', 0, 0),
(235, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 34, 21, '2025-07-28 06:01:28', '他整体还是一个强试错的过程。', '1753690770126/9_88350_90150.wav', 0, 0),
(236, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 35, 21, '2025-07-28 06:01:30', '嗯，', '1753690770126/9_90410_90650.wav', 0, 0),
(237, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 36, 22, '2025-07-28 06:01:30', '后来退退德国或者拓大新加坡、', '1753690770126/9_90750_93030.wav', 0, 0),
(238, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 37, 22, '2025-07-28 06:01:33', '印尼、', '1753690770126/9_93110_93530.wav', 0, 0),
(239, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 38, 22, '2025-07-28 06:01:33', '越南等等等些地方方，', '1753690770126/9_93530_95290.wav', 0, 0),
(240, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 39, 22, '2025-07-28 06:01:35', '每一个地方走过去都面临的一个问题是建站的效率怎么样能够快速的把这这站站能建起来。', '1753690770126/9_95610_101570.wav', 0, 0),
(241, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 40, 23, '2025-07-28 06:01:41', '一方面我们当初刚好从一四年刚好开始要出去的时候呢，', '1753690770126/9_101570_105270.wav', 0, 0),
(242, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 41, 23, '2025-07-28 06:01:45', '去国内就是三个北上广深。', '1753690770126/9_105530_108085.wav', 0, 0),
(243, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 42, 23, '2025-07-28 06:01:48', '那当在海外呢？', '1753690770126/9_108750_109730.wav', 0, 0),
(244, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 43, 23, '2025-07-28 06:01:49', '要同时开服北美美东美西对吧？', '1753690770126/9_109730_112850.wav', 0, 0),
(245, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 44, 23, '2025-07-28 06:01:52', '欧洲、', '1753690770126/9_112850_113270.wav', 0, 0),
(246, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 45, 23, '2025-07-28 06:01:53', '日本，', '1753690770126/9_113410_113850.wav', 0, 0),
(247, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 46, 23, '2025-07-28 06:01:54', '那我还记得那个时候，', '1753690770126/9_114190_115230.wav', 0, 0),
(248, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 47, 23, '2025-07-28 06:01:55', '那我们在海外如何去建立这种 IDC 的勘探建设、', '1753690770126/9_115230_118510.wav', 0, 0),
(249, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 48, 23, '2025-07-28 06:01:58', '基础设施，', '1753690770126/9_118730_119290.wav', 0, 0),
(250, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 49, 23, '2025-07-28 06:01:59', '建设云服务的部署，', '1753690770126/9_119290_120890.wav', 0, 0),
(251, '2025-07-28 08:21:21', 1, 'gofly', '2025-07-28 08:21:21', 1, 'gofly', 9, 50, 23, '2025-07-28 06:02:01', '那都是一个全新的挑战。', '1753690770126/9_121370_122805.wav', 0, 0),
(252, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 1, 16, '2025-07-30 20:39:59', '非常高兴哈能够和几位的话呢一起来讨论互联网企业如何决胜全球化新高地这个话题。', '1753691771686/10_50_9810.wav', 0, 0),
(253, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 2, 21, '2025-07-30 20:40:09', '然后第二块其实是游戏平台。', '1753691771686/10_10290_12150.wav', 0, 0),
(254, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 3, 21, '2025-07-30 20:40:11', '所谓游戏平台，', '1753691771686/10_12790_13890.wav', 0, 0),
(255, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 16:45:04', 1, '开发管理员', 10, 4, 21, '2025-07-30 20:40:13', '它主要是呃简单来说就是一个商店加社区的这样一个模式。', '1753691771686/10_14010_18910.wav', 0, 0),
(256, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 5, 22, '2025-07-30 20:40:18', '而这么多年，', '1753691771686/10_19350_20230.wav', 0, 0),
(257, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 6, 22, '2025-07-30 20:40:19', '我们随着整个业务的拓张呢，', '1753691771686/10_20250_21990.wav', 0, 0),
(258, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 7, 22, '2025-07-30 20:40:20', '会发现跟阿里云有非常紧密的联系。', '1753691771686/10_21990_25330.wav', 0, 0),
(259, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 8, 22, '2025-07-30 20:40:24', '因为刚开始伟光在介绍的时候也讲阿里云也是阿里巴巴的云。', '1753691771686/10_25330_29770.wav', 0, 0),
(260, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 9, 22, '2025-07-30 20:40:28', '所以这个过程中一会儿也可以稍微展开。', '1753691771686/10_29770_32030.wav', 0, 0),
(261, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 10, 22, '2025-07-30 20:40:31', '跟大家讲一下，', '1753691771686/10_32030_32710.wav', 0, 0),
(262, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 11, 22, '2025-07-30 20:40:31', '我们跟云是怎么一路走来的。', '1753691771686/10_32710_35750.wav', 0, 0),
(263, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 12, 16, '2025-07-30 20:40:35', '其实的确的话呢，', '1753691771686/10_36070_37290.wav', 0, 0),
(264, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 13, 16, '2025-07-30 20:40:36', '就对我们互联网公司来说，', '1753691771686/10_37290_38730.wav', 0, 0),
(265, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 14, 16, '2025-07-30 20:40:37', '如果不能够问当地的人口的话，', '1753691771686/10_38750_41050.wav', 0, 0),
(266, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 15, 16, '2025-07-30 20:40:40', '我想我们可能这个整个的就失去了后边所有的这个动力。', '1753691771686/10_41250_46130.wav', 0, 0),
(267, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 16, 16, '2025-07-30 20:40:45', '不知道你们各位怎么看，', '1753691771686/10_46130_47730.wav', 0, 0),
(268, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 17, 16, '2025-07-30 20:40:47', '就是我们最大的这个问题是不是效率优先？', '1753691771686/10_48190_51590.wav', 0, 0),
(269, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 18, 16, '2025-07-30 20:40:50', ' yes，', '1753691771686/10_51590_51830.wav', 0, 0),
(270, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 19, 16, '2025-07-30 20:40:51', ' oh no。', '1753691771686/10_52290_53175.wav', 0, 0),
(271, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 20, 16, '2025-07-30 20:40:53', '然后如果是讲一个最关键的，', '1753691771686/10_54000_58450.wav', 0, 0),
(272, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 21, 16, '2025-07-30 20:40:57', '你们是怎么来克服这些挑战的啊，', '1753691771686/10_58550_62635.wav', 0, 0),
(273, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 22, 21, '2025-07-30 20:41:03', '因因因为其我们最近一直在做海外业务，', '1753691771686/10_64610_66990.wav', 0, 0),
(274, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 23, 21, '2025-07-30 20:41:06', '嗯，', '1753691771686/10_67110_67330.wav', 0, 0),
(275, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 24, 21, '2025-07-30 20:41:06', '就是所以说这呃我们碰到了些问题，', '1753691771686/10_67330_69410.wav', 0, 0),
(276, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 25, 21, '2025-07-30 20:41:08', '可以一起分享出来给大家，', '1753691771686/10_69410_71250.wav', 0, 0),
(277, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 26, 21, '2025-07-30 20:41:10', '其实一起探讨一下。', '1753691771686/10_71270_72450.wav', 0, 0),
(278, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 27, 21, '2025-07-30 20:41:11', '嗯，', '1753691771686/10_72450_72690.wav', 0, 0),
(279, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 28, 21, '2025-07-30 20:41:12', '呃其实海外外就是我我们是这个强观的说是呃无论你准备工作做的有多充分，', '1753691771686/10_73110_80870.wav', 0, 0),
(280, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 29, 21, '2025-07-30 20:41:20', '嗯，', '1753691771686/10_81370_81510.wav', 0, 0),
(281, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 30, 21, '2025-07-30 20:41:20', '无论你有就是呃学习能力有多强。', '1753691771686/10_81510_84650.wav', 0, 0),
(282, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 31, 21, '2025-07-30 20:41:23', '嗯，', '1753691771686/10_84970_85110.wav', 0, 0),
(283, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 32, 21, '2025-07-30 20:41:24', '一个中国企业的负责人，', '1753691771686/10_85110_86330.wav', 0, 0),
(284, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 33, 21, '2025-07-30 20:41:25', '其实在出海的时候，', '1753691771686/10_86330_87510.wav', 0, 0),
(285, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 34, 21, '2025-07-30 20:41:27', '呃，', '1753691771686/10_88050_88290.wav', 0, 0),
(286, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 35, 21, '2025-07-30 20:41:27', '他整体还是一个强试错的过程。', '1753691771686/10_88350_90150.wav', 0, 0),
(287, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 36, 21, '2025-07-30 20:41:29', '嗯，', '1753691771686/10_90390_90630.wav', 0, 0),
(288, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 37, 22, '2025-07-30 20:41:29', '后来退到德国或者拓大新加坡、', '1753691771686/10_90750_93030.wav', 0, 0),
(289, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 38, 22, '2025-07-30 20:41:32', '印尼、', '1753691771686/10_93110_93530.wav', 0, 0),
(290, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 39, 22, '2025-07-30 20:41:32', '越南等等这些地方。', '1753691771686/10_93530_94770.wav', 0, 0),
(291, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 40, 22, '2025-07-30 20:41:34', '那每一个地方走过去都面临的一个问题是建站的效率一么样能够快速的把这个站点能建起来。', '1753691771686/10_95070_101570.wav', 0, 0),
(292, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 41, 23, '2025-07-30 20:41:40', '一方面我们当初刚好从一四年刚好开始要出去的时候呢，', '1753691771686/10_101570_105270.wav', 0, 0),
(293, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 42, 23, '2025-07-30 20:41:44', '去国内就是三个北上广深。', '1753691771686/10_105550_108085.wav', 0, 0),
(294, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 43, 23, '2025-07-30 20:41:47', '那当在海外呢？', '1753691771686/10_108750_109730.wav', 0, 0),
(295, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 44, 23, '2025-07-30 20:41:48', '要同时开服北美美东美西对吧？', '1753691771686/10_109730_112850.wav', 0, 0),
(296, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 45, 23, '2025-07-30 20:41:51', '欧洲、', '1753691771686/10_112850_113270.wav', 0, 0),
(297, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 46, 23, '2025-07-30 20:41:52', '日本，', '1753691771686/10_113410_113850.wav', 0, 0),
(298, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 47, 23, '2025-07-30 20:41:53', '那我还记得那个时候，', '1753691771686/10_114190_115230.wav', 0, 0),
(299, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 48, 23, '2025-07-30 20:41:54', '那我们在海外如何去建立这种 IDC 的勘探建设、', '1753691771686/10_115230_118510.wav', 0, 0),
(300, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 49, 23, '2025-07-30 20:41:57', '基础设施，', '1753691771686/10_118730_119290.wav', 0, 0),
(301, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 50, 23, '2025-07-30 20:41:58', '建设云服务的部署，', '1753691771686/10_119290_120890.wav', 0, 0),
(302, '2025-07-28 08:36:13', 1, 'gofly', '2025-07-28 08:36:13', 1, 'gofly', 10, 51, 23, '2025-07-30 20:42:00', '那都是一个全新的挑战。', '1753691771686/10_121370_122805.wav', 0, 0),
(303, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 1, 16, '2025-07-23 20:45:17', '非常高兴哈能够和几位的话呢一起来讨论互联网企业如何决胜全球化新高地这个话题。', '1753692325424/11_50_9810.wav', 0, 0),
(304, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 2, 21, '2025-07-23 20:45:27', '然后第二块其实是游戏平台。', '1753692325424/11_10290_12150.wav', 0, 0),
(305, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 3, 21, '2025-07-23 20:45:29', '所谓游戏平台，', '1753692325424/11_12770_13890.wav', 0, 0),
(306, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 4, 21, '2025-07-23 20:45:31', '它主要是呃简单来说就是一个商店加社区的这样一个模式。', '1753692325424/11_14010_18910.wav', 0, 0),
(307, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 5, 22, '2025-07-23 20:45:36', '而这么多年，', '1753692325424/11_19370_20230.wav', 0, 0),
(308, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 6, 22, '2025-07-23 20:45:37', '我们随着整个业务的拓张呢，', '1753692325424/11_20270_21990.wav', 0, 0),
(309, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 7, 22, '2025-07-23 20:45:38', '会发现跟阿里云有非常紧密的联系。', '1753692325424/11_21990_25330.wav', 0, 0),
(310, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 8, 22, '2025-07-23 20:45:42', '因为刚开始伟光在介绍的时候也讲阿里云也是阿里巴巴的云。', '1753692325424/11_25330_29770.wav', 0, 0),
(311, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 9, 22, '2025-07-23 20:45:46', '所以这个过程中一会儿也可以稍微展开。', '1753692325424/11_29770_32030.wav', 0, 0),
(312, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 10, 22, '2025-07-23 20:45:49', '跟大家讲一下，', '1753692325424/11_32030_32710.wav', 0, 0),
(313, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 11, 22, '2025-07-23 20:45:49', '我们跟云是怎么一路走来的。', '1753692325424/11_32710_35750.wav', 0, 0),
(314, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 12, 16, '2025-07-23 20:45:53', '其实的确的话呢，', '1753692325424/11_36070_37290.wav', 0, 0),
(315, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 13, 16, '2025-07-23 20:45:54', '就对我们互联网公司来说，', '1753692325424/11_37290_38730.wav', 0, 0),
(316, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 14, 16, '2025-07-23 20:45:55', '如果不能够问当地的人口的话，', '1753692325424/11_38750_41050.wav', 0, 0),
(317, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 15, 16, '2025-07-23 20:45:58', '我想我们可能这个整个的就失去了后边所有的这个动力。', '1753692325424/11_41250_46130.wav', 0, 0),
(318, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 16, 16, '2025-07-23 20:46:03', '不知道你们各位怎么看，', '1753692325424/11_46130_47730.wav', 0, 0),
(319, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 17, 16, '2025-07-23 20:46:05', '就是我们最大的这个问题是不是效率优先？', '1753692325424/11_48190_51590.wav', 0, 0),
(320, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 18, 16, '2025-07-23 20:46:08', ' yes，', '1753692325424/11_51590_51830.wav', 0, 0),
(321, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 19, 16, '2025-07-23 20:46:09', ' oh no。', '1753692325424/11_52290_53175.wav', 0, 0),
(322, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 20, 16, '2025-07-23 20:46:11', '然后如果是讲一个最关键的，', '1753692325424/11_54000_58450.wav', 0, 0),
(323, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 21, 16, '2025-07-23 20:46:15', '你们是怎么来克服这些挑战的啊，', '1753692325424/11_58550_62635.wav', 0, 0),
(324, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 22, 21, '2025-07-23 20:46:21', '因因因为其我们最近一直在做海外业务，', '1753692325424/11_64610_66990.wav', 0, 0),
(325, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 23, 21, '2025-07-23 20:46:24', '嗯，', '1753692325424/11_67110_67330.wav', 0, 0),
(326, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 24, 21, '2025-07-23 20:46:24', '就是所以说这呃我们碰到一些问题可以一起分享出来给大家，', '1753692325424/11_67330_71250.wav', 0, 0),
(327, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 25, 21, '2025-07-23 20:46:28', '其实一起探讨一下。', '1753692325424/11_71270_72450.wav', 0, 0),
(328, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 26, 21, '2025-07-23 20:46:29', '嗯，', '1753692325424/11_72450_72690.wav', 0, 0),
(329, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 27, 21, '2025-07-23 20:46:30', '呃其实海外外就是我我们是这个强观的说是呃无论你准备工作做的有多充分，', '1753692325424/11_73110_81150.wav', 0, 0),
(330, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 28, 21, '2025-07-23 20:46:38', '嗯，', '1753692325424/11_81370_81510.wav', 0, 0),
(331, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 29, 21, '2025-07-23 20:46:38', '无论你有就是呃学习能力有强强。', '1753692325424/11_81510_84650.wav', 0, 0),
(332, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 30, 21, '2025-07-23 20:46:41', '嗯，', '1753692325424/11_84950_85110.wav', 0, 0),
(333, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 31, 21, '2025-07-23 20:46:42', '一个中国企业的负责人，', '1753692325424/11_85110_86330.wav', 0, 0),
(334, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 32, 21, '2025-07-23 20:46:43', '其实在出海的时候，', '1753692325424/11_86330_87510.wav', 0, 0),
(335, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 33, 21, '2025-07-23 20:46:45', '呃，', '1753692325424/11_88050_88290.wav', 0, 0),
(336, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 34, 21, '2025-07-23 20:46:45', '他整体还是一个强试错的过程。', '1753692325424/11_88350_90150.wav', 0, 0),
(337, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 35, 21, '2025-07-23 20:46:47', '嗯，', '1753692325424/11_90390_90630.wav', 0, 0),
(338, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 36, 22, '2025-07-23 20:46:47', '后来退到德国或者拓大新加坡、', '1753692325424/11_90750_93030.wav', 0, 0),
(339, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 37, 22, '2025-07-23 20:46:50', '印尼、', '1753692325424/11_93110_93530.wav', 0, 0),
(340, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 38, 22, '2025-07-23 20:46:50', '越南等等这些地方。', '1753692325424/11_93530_94770.wav', 0, 0),
(341, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 39, 22, '2025-07-23 20:46:52', '那每一个地方走过去都面临的一个问题是建站的效率一么样能够快速的把这个站点能建起来。', '1753692325424/11_95070_101570.wav', 0, 0),
(342, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 40, 23, '2025-07-23 20:46:58', '一方面我们当初刚好从一四年刚好开始要出去的时候呢，', '1753692325424/11_101570_105270.wav', 0, 0),
(343, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 41, 23, '2025-07-23 20:47:02', '去国内就是三个北上广深。', '1753692325424/11_105550_108085.wav', 0, 0),
(344, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 42, 23, '2025-07-23 20:47:05', '那当在海外呢？', '1753692325424/11_108750_109730.wav', 0, 0),
(345, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 43, 23, '2025-07-23 20:47:06', '要同时开服北美美东美西对吧？', '1753692325424/11_109730_112850.wav', 0, 0),
(346, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 44, 23, '2025-07-23 20:47:09', '欧洲、', '1753692325424/11_112850_113270.wav', 0, 0),
(347, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 45, 23, '2025-07-23 20:47:10', '日本，', '1753692325424/11_113410_113850.wav', 0, 0),
(348, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 46, 23, '2025-07-23 20:47:11', '那我还记得那个时候，', '1753692325424/11_114190_115230.wav', 0, 0),
(349, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 47, 23, '2025-07-23 20:47:12', '那我们在海外如何去建立这种 IDC 的勘探建设、', '1753692325424/11_115230_118510.wav', 0, 0),
(350, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 48, 23, '2025-07-23 20:47:15', '基础设施，', '1753692325424/11_118730_119290.wav', 0, 0),
(351, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 49, 23, '2025-07-23 20:47:16', '建设云服务的部署，', '1753692325424/11_119290_120890.wav', 0, 0),
(352, '2025-07-28 08:45:27', 1, 'gofly', '2025-07-28 08:45:27', 1, 'gofly', 11, 50, 23, '2025-07-23 20:47:18', '那都是一个全新的挑战。', '1753692325424/11_121370_122805.wav', 0, 0),
(353, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 1, 16, '2025-07-10 19:59:17', '非常高兴哈能够和几位的话呢一起来讨论互联网企业如何决胜全球化新高地这个话题。', '1753693050254/12_50_9810.wav', 0, 0),
(354, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 2, 21, '2025-07-10 19:59:27', '然后第二块其实是游戏平台。', '1753693050254/12_10290_12150.wav', 0, 0),
(355, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 3, 21, '2025-07-10 19:59:29', '所谓游戏平台，', '1753693050254/12_12770_13890.wav', 0, 0),
(356, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 4, 21, '2025-07-10 19:59:31', '它主要是呃简单来说就是一个商店加社区的这样一个模式。', '1753693050254/12_14010_18910.wav', 0, 0),
(357, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 5, 22, '2025-07-10 19:59:36', '而这么多年，', '1753693050254/12_19370_20230.wav', 0, 0),
(358, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 6, 22, '2025-07-10 19:59:37', '我们随着整个业务的拓张呢，', '1753693050254/12_20250_21990.wav', 0, 0),
(359, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 7, 22, '2025-07-10 19:59:38', '会发现跟阿里云有非常紧密的联系。', '1753693050254/12_21990_25330.wav', 0, 0),
(360, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 8, 22, '2025-07-10 19:59:42', '因为刚开始伟光在介绍的时候也讲阿里云也是阿里巴巴的云。', '1753693050254/12_25330_29770.wav', 0, 0),
(361, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 9, 22, '2025-07-10 19:59:46', '所以这个过程中一会儿也可以稍微展开。', '1753693050254/12_29770_32030.wav', 0, 0),
(362, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 10, 22, '2025-07-10 19:59:49', '跟大家讲一下，', '1753693050254/12_32030_32710.wav', 0, 0),
(363, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 11, 22, '2025-07-10 19:59:49', '我们跟云是怎么一路走来的。', '1753693050254/12_32710_35750.wav', 0, 0),
(364, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 12, 16, '2025-07-10 19:59:53', '其实的确的话呢，', '1753693050254/12_36070_37290.wav', 0, 0),
(365, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 13, 16, '2025-07-10 19:59:54', '就对我们互联网公司来说，', '1753693050254/12_37290_38730.wav', 0, 0),
(366, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 14, 16, '2025-07-10 19:59:55', '如果不能够问当地的人口的话，', '1753693050254/12_38750_41050.wav', 0, 0),
(367, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 15, 16, '2025-07-10 19:59:58', '我想我们可能这个整个的就失去了后边所有的这个动力。', '1753693050254/12_41250_46130.wav', 0, 0),
(368, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 16, 16, '2025-07-10 20:00:03', '不知道你们各位怎么看，', '1753693050254/12_46130_47730.wav', 0, 0),
(369, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 17, 16, '2025-07-10 20:00:05', '就是我们最大的这个问题是不是效率优先？', '1753693050254/12_48190_51590.wav', 0, 0),
(370, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 18, 16, '2025-07-10 20:00:08', ' yes，', '1753693050254/12_51590_51830.wav', 0, 0),
(371, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 19, 16, '2025-07-10 20:00:09', ' oh no。', '1753693050254/12_52290_53175.wav', 0, 0),
(372, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 20, 16, '2025-07-10 20:00:11', '然后如果是讲一个最关键的，', '1753693050254/12_54000_58450.wav', 0, 0),
(373, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 21, 16, '2025-07-10 20:00:15', '你们是怎么来克服这些挑战的啊，', '1753693050254/12_58550_62635.wav', 0, 0),
(374, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 22, 21, '2025-07-10 20:00:21', '因因因为其我们最近一直在做海外业务，', '1753693050254/12_64610_66990.wav', 0, 0),
(375, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 23, 21, '2025-07-10 20:00:24', '嗯，', '1753693050254/12_67110_67330.wav', 0, 0),
(376, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 24, 21, '2025-07-10 20:00:24', '就是所以说这呃我们碰到一些问题可以一起分享出来给大家，', '1753693050254/12_67330_71250.wav', 0, 0),
(377, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 25, 21, '2025-07-10 20:00:28', '其实一起探讨一下。', '1753693050254/12_71270_72450.wav', 0, 0),
(378, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 26, 21, '2025-07-10 20:00:29', '嗯，', '1753693050254/12_72450_72690.wav', 0, 0),
(379, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 27, 21, '2025-07-10 20:00:30', '呃其实海外外就是我们还是这个观观的说是呃无论你准备工作做的有多充分，', '1753693050254/12_73110_81150.wav', 0, 0),
(380, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 28, 21, '2025-07-10 20:00:38', '嗯，', '1753693050254/12_81370_81510.wav', 0, 0),
(381, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 29, 21, '2025-07-10 20:00:38', '无论你有就是呃学习能力有多强。', '1753693050254/12_81510_84650.wav', 0, 0),
(382, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 30, 21, '2025-07-10 20:00:41', '嗯，', '1753693050254/12_84950_85110.wav', 0, 0),
(383, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 31, 21, '2025-07-10 20:00:42', '你个中国企业的负责人，', '1753693050254/12_85110_86330.wav', 0, 0),
(384, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 32, 21, '2025-07-10 20:00:43', '其实在出海的时候，', '1753693050254/12_86330_87510.wav', 0, 0),
(385, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 33, 21, '2025-07-10 20:00:45', '呃，', '1753693050254/12_88050_88290.wav', 0, 0),
(386, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 34, 21, '2025-07-10 20:00:45', '他整体还是一个强试错的过程。', '1753693050254/12_88350_90150.wav', 0, 0),
(387, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 35, 21, '2025-07-10 20:00:47', '嗯，', '1753693050254/12_90410_90650.wav', 0, 0),
(388, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 36, 22, '2025-07-10 20:00:47', '后来退到德国或者拓大新加坡、', '1753693050254/12_90750_93030.wav', 0, 0),
(389, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 37, 22, '2025-07-10 20:00:50', '印尼、', '1753693050254/12_93110_93530.wav', 0, 0),
(390, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 38, 22, '2025-07-10 20:00:50', '越南等等这些地方。', '1753693050254/12_93530_94770.wav', 0, 0),
(391, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 39, 22, '2025-07-10 20:00:52', '那每一个地方走过去都面临的一个问题是建站的效率一么样能够快速的把这个站点能建起来。', '1753693050254/12_95050_101570.wav', 0, 0),
(392, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 40, 23, '2025-07-10 20:00:58', '一方面我们当初刚好从一四年刚好开始要出去的时候呢，', '1753693050254/12_101570_105270.wav', 0, 0),
(393, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 41, 23, '2025-07-10 20:01:02', '去国内就是三个北上广深。', '1753693050254/12_105550_108085.wav', 0, 0),
(394, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 42, 23, '2025-07-10 20:01:05', '那当在海外呢要同时开服北美、', '1753693050254/12_108750_111230.wav', 0, 0),
(395, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 43, 23, '2025-07-10 20:01:08', '美东美西。', '1753693050254/12_111510_112310.wav', 0, 0),
(396, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 44, 23, '2025-07-10 20:01:09', '对吧？', '1753693050254/12_112450_112850.wav', 0, 0),
(397, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 45, 23, '2025-07-10 20:01:09', '欧洲日本，', '1753693050254/12_112850_113850.wav', 0, 0),
(398, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 46, 23, '2025-07-10 20:01:11', '那我还记得那个时候，', '1753693050254/12_114190_115230.wav', 0, 0),
(399, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 47, 23, '2025-07-10 20:01:12', '那我们在海外如何去建立这种 IDC 的勘探建设、', '1753693050254/12_115230_118510.wav', 0, 0),
(400, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 48, 23, '2025-07-10 20:01:15', '基础设施，', '1753693050254/12_118730_119290.wav', 0, 0),
(401, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 49, 23, '2025-07-10 20:01:16', '建设云服务的部署，', '1753693050254/12_119290_120890.wav', 0, 0),
(402, '2025-07-28 08:57:32', 1, 'gofly', '2025-07-28 08:57:32', 1, 'gofly', 12, 50, 23, '2025-07-10 20:01:18', '那都是一个全新的挑战。', '1753693050254/12_121370_122805.wav', 0, 0),
(403, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 1, 16, '2025-07-25 17:10:33', '非常高兴哈能够和几位的话呢一起来讨论互联网企业如何决胜全球化新高地这个话题。', '1753848640538/13_50_9810.wav', 0, 0),
(404, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 2, 21, '2025-07-25 17:10:43', '然后第二块其实是游戏平台。', '1753848640538/13_10290_12150.wav', 0, 0),
(405, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 3, 21, '2025-07-25 17:10:45', '所谓游戏平台，', '1753848640538/13_12770_13890.wav', 0, 0),
(406, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 4, 21, '2025-07-25 17:10:47', '它主要是呃简单来说就是一个商店加社区的这样一个模式。', '1753848640538/13_14010_18910.wav', 0, 0),
(407, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 5, 22, '2025-07-25 17:10:52', '而这么多年，', '1753848640538/13_19370_20230.wav', 0, 0),
(408, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 6, 22, '2025-07-25 17:10:53', '我们随着整个业务的拓张呢，', '1753848640538/13_20270_21990.wav', 0, 0),
(409, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 7, 22, '2025-07-25 17:10:54', '会发现跟阿里云有非常紧密的联系。', '1753848640538/13_21990_25330.wav', 0, 0),
(410, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 8, 22, '2025-07-25 17:10:58', '因为刚开始伟光在介绍的时候也讲阿里云也是阿里巴巴的云。', '1753848640538/13_25330_29770.wav', 0, 0),
(411, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 9, 22, '2025-07-25 17:11:02', '所以这个过程中一会儿也可以稍微展开。', '1753848640538/13_29770_32030.wav', 0, 0),
(412, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 10, 22, '2025-07-25 17:11:05', '跟大家讲一下，', '1753848640538/13_32030_32710.wav', 0, 0),
(413, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 11, 22, '2025-07-25 17:11:05', '我们跟云是怎么一路走来的。', '1753848640538/13_32710_35750.wav', 0, 0),
(414, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 12, 16, '2025-07-25 17:11:09', '其实的确的话呢，', '1753848640538/13_36070_37290.wav', 0, 0),
(415, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 13, 16, '2025-07-25 17:11:10', '就对我们互联网公司来说，', '1753848640538/13_37290_38730.wav', 0, 0),
(416, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 14, 16, '2025-07-25 17:11:11', '如果不能够问当地的人口的话，', '1753848640538/13_38750_41050.wav', 0, 0),
(417, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 15, 16, '2025-07-25 17:11:14', '我想我们可能这个整个的就失去了后边所有的这个动力。', '1753848640538/13_41250_46130.wav', 0, 0),
(418, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 16, 16, '2025-07-25 17:11:19', '不知道你们各位怎么看，', '1753848640538/13_46130_47730.wav', 0, 0),
(419, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 17, 16, '2025-07-25 17:11:21', '就是我们最大的这个问题是不是效率优先？', '1753848640538/13_48190_51590.wav', 0, 0),
(420, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 18, 16, '2025-07-25 17:11:24', ' yes，', '1753848640538/13_51590_51830.wav', 0, 0),
(421, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 19, 16, '2025-07-25 17:11:25', ' oh no。', '1753848640538/13_52290_53175.wav', 0, 0),
(422, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 20, 16, '2025-07-25 17:11:27', '然后如果是讲一个最关键的，', '1753848640538/13_54000_58450.wav', 0, 0),
(423, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 21, 16, '2025-07-25 17:11:31', '你们是怎么来克服这些挑战的啊，', '1753848640538/13_58550_62635.wav', 0, 0),
(424, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 22, 21, '2025-07-25 17:11:37', '因因因为其我们最近一直在做海外业务，', '1753848640538/13_64610_66990.wav', 0, 0),
(425, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 23, 21, '2025-07-25 17:11:40', '嗯，', '1753848640538/13_67110_67330.wav', 0, 0),
(426, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 24, 21, '2025-07-25 17:11:40', '就是所以说这呃我们碰到一些问题可以一起分享出来给大家，', '1753848640538/13_67330_71250.wav', 0, 0),
(427, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 25, 21, '2025-07-25 17:11:44', '其实一起探讨一下。', '1753848640538/13_71270_72450.wav', 0, 0),
(428, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 26, 21, '2025-07-25 17:11:45', '嗯，', '1753848640538/13_72450_72690.wav', 0, 0),
(429, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 27, 21, '2025-07-25 17:11:46', '呃其实海外外就是我我还是这个强观的说是呃无论你准备工作做的有多充分，', '1753848640538/13_73110_81150.wav', 0, 0),
(430, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 28, 21, '2025-07-25 17:11:54', '嗯，', '1753848640538/13_81370_81510.wav', 0, 0),
(431, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 29, 21, '2025-07-25 17:11:54', '无论你有就是呃学习能力有多强。', '1753848640538/13_81510_84950.wav', 0, 0),
(432, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 30, 21, '2025-07-25 17:11:57', '嗯，', '1753848640538/13_84970_85110.wav', 0, 0),
(433, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 31, 21, '2025-07-25 17:11:58', '一个中国企业的负责人，', '1753848640538/13_85110_86330.wav', 0, 0),
(434, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 32, 21, '2025-07-25 17:11:59', '其实在出海的时候，', '1753848640538/13_86330_87510.wav', 0, 0),
(435, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 33, 21, '2025-07-25 17:12:01', '呃，', '1753848640538/13_88050_88290.wav', 0, 0),
(436, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 34, 21, '2025-07-25 17:12:01', '他整体还是一个强试错的过程。', '1753848640538/13_88350_90150.wav', 0, 0),
(437, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 35, 21, '2025-07-25 17:12:03', '嗯，', '1753848640538/13_90410_90650.wav', 0, 0),
(438, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 36, 22, '2025-07-25 17:12:03', '后来退到德国或者拓大新加坡、', '1753848640538/13_90750_93030.wav', 0, 0),
(439, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 37, 22, '2025-07-25 17:12:06', '印尼、', '1753848640538/13_93110_93530.wav', 0, 0),
(440, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 38, 22, '2025-07-25 17:12:06', '越南等等这些地方。', '1753848640538/13_93530_94770.wav', 0, 0),
(441, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 39, 22, '2025-07-25 17:12:08', '那每一个地方走过去都面临的一个问题是建站的效率一么样能够快速的把这个站点能建起来。', '1753848640538/13_95070_101570.wav', 0, 0),
(442, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 40, 23, '2025-07-25 17:12:14', '一方面我们当初刚好从一四年刚好开始要出去的时候呢，', '1753848640538/13_101570_105270.wav', 0, 0),
(443, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 41, 23, '2025-07-25 17:12:18', '去国内就是三个北上广深。', '1753848640538/13_105550_108085.wav', 0, 0),
(444, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 42, 23, '2025-07-25 17:12:21', '那当在海外呢要同时开服北美、', '1753848640538/13_108750_111230.wav', 0, 0),
(445, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 43, 23, '2025-07-25 17:12:24', '美东美西。', '1753848640538/13_111510_112310.wav', 0, 0),
(446, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 44, 23, '2025-07-25 17:12:25', '对吧？', '1753848640538/13_112450_112850.wav', 0, 0),
(447, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 45, 23, '2025-07-25 17:12:25', '欧洲日本，', '1753848640538/13_112850_113850.wav', 0, 0),
(448, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 46, 23, '2025-07-25 17:12:27', '那我还记得那个时候，', '1753848640538/13_114190_115230.wav', 0, 0),
(449, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 47, 23, '2025-07-25 17:12:28', '那我们在海外如何去建立这种 IDC 的勘探建设、', '1753848640538/13_115230_118510.wav', 0, 0),
(450, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 48, 23, '2025-07-25 17:12:31', '基础设施，', '1753848640538/13_118730_119290.wav', 0, 0),
(451, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 49, 23, '2025-07-25 17:12:32', '建设云服务的部署，', '1753848640538/13_119290_120890.wav', 0, 0),
(452, '2025-07-30 04:10:42', 1, 'gofly', '2025-07-30 04:10:42', 1, 'gofly', 13, 50, 23, '2025-07-25 17:12:34', '那都是一个全新的挑战。', '1753848640538/13_121370_122805.wav', 0, 0);
COMMIT;

-- ----------------------------
-- Table Index: meeting_offline_detail 
-- ----------------------------
ALTER TABLE `meeting_offline_detail` ADD  INDEX `idx_meeting_offline_detail_meeting_id`(`meeting_id`) USING BTREE;
ALTER TABLE `meeting_offline_detail` ADD  INDEX `idx_meeting_offline_detail_train_id`(`train_id`) USING BTREE;

-- ----------------------------
-- Table structure: voice_document 
-- ----------------------------
DROP TABLE IF EXISTS `voice_document`;
CREATE TABLE `voice_document` (
 `id` bigint(19) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
 `creator_id` bigint(19) COMMENT '创建人ID',
 `creator_name` varchar(200) COMMENT '创建人名称',
 `create_time` datetime COMMENT '创建时间',
 `updater_id` bigint(19) COMMENT '更新人ID',
 `updater_name` varchar(200) COMMENT '更新人名称',
 `update_time` datetime COMMENT '更新时间',
 `name` varchar(100) COMMENT '范文名',
 `content` varchar(1000) COMMENT '范文内容', 
PRIMARY KEY (id)
);

-- ----------------------------
-- Data: voice_document 
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure: voice_print 
-- ----------------------------
DROP TABLE IF EXISTS `voice_print`;
CREATE TABLE `voice_print` (
 `id` bigint(19) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
 `creator_id` bigint(19) COMMENT '创建人ID',
 `creator_name` varchar(200) COMMENT '创建人名称',
 `create_time` datetime COMMENT '创建时间',
 `updater_id` bigint(19) COMMENT '更新人ID',
 `updater_name` varchar(200) COMMENT '更新人名称',
 `update_time` datetime COMMENT '更新时间',
 `deleted` tinyint(3) DEFAULT 0 COMMENT '是否删除',
 `deleted_at` datetime COMMENT '删除时间',
 `user_id` bigint(19) COMMENT '用户ID',
 `user_name` varchar(100) COMMENT '用户名',
 `print_id` bigint(19) COMMENT '声纹ID', 
PRIMARY KEY (id)
);

-- ----------------------------
-- Data: voice_print 
-- ----------------------------
BEGIN;
COMMIT;
