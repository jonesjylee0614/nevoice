package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonPicture = "common_picture"

// CommonPicture 图片库
type CommonPicture struct {
	base.IdModel
	UID         int64  `gorm:"column:uid;not null;comment:添加账号" json:"uid"`                       // 添加账号
	Cid         int64  `gorm:"column:cid;not null;comment:分类id" json:"cid"`                       // 分类id
	Weigh       int64  `gorm:"column:weigh;not null;comment:排序" json:"weigh"`                     // 排序
	Name        string `gorm:"column:name;not null;comment:附件原来名称" json:"name"`                   // 附件原来名称
	Title       string `gorm:"column:title;not null;comment:文件名称" json:"title"`                   // 文件名称
	Type        int64  `gorm:"column:type;not null;comment:类型0=素材图1=插图,2=视频，3=音频" json:"type"`    // 类型0=素材图1=插图,2=视频，3=音频
	URL         string `gorm:"column:url;not null;comment:访问路径" json:"url"`                       // 访问路径
	Imagewidth  string `gorm:"column:imagewidth;not null;comment:宽度" json:"imagewidth"`           // 宽度
	Imageheight string `gorm:"column:imageheight;not null;comment:高度" json:"imageheight"`         // 高度
	Filesize    uint64 `gorm:"column:filesize;not null;comment:文件大小" json:"filesize"`             // 文件大小
	Mimetype    string `gorm:"column:mimetype;not null;comment:mime类型" json:"mimetype"`           // mime类型
	Storage     string `gorm:"column:storage;not null;default:local;comment:存储位置" json:"storage"` // 存储位置
	CoverURL    string `gorm:"column:cover_url;not null;comment:视频封面" json:"cover_url"`           // 视频封面
	Sha1        string `gorm:"column:sha1;not null;comment:文件 sha1编码" json:"sha1"`                // 文件 sha1编码
	Createtime  int64  `gorm:"column:create_time;not null;comment:上传时间" json:"create_time"`       // 上传时间
	Status      int64  `gorm:"column:status;not null;comment:状态1=禁用" json:"status"`               // 状态1=禁用
}

// TableName CommonPicture's table name
func (*CommonPicture) TableName() string {
	return TableNameCommonPicture
}
