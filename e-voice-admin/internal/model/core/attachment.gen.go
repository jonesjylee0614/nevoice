package core

import (
	"gofly/internal/model/base"
)

const TableNameAttachment = "attachment"

// Attachment 附件管理
type Attachment struct {
	base.TimeModel
	UID         int64  `gorm:"column:uid;not null;comment:上传用户" json:"uid"`                       // 上传用户
	Cid         int64  `gorm:"column:cid;not null;comment:分类" json:"cid"`                         // 分类
	URL         string `gorm:"column:url;not null;comment:访问路径" json:"url"`                       // 访问路径
	Imagewidth  string `gorm:"column:imagewidth;not null;comment:宽度" json:"imagewidth"`           // 宽度
	Imageheight string `gorm:"column:imageheight;not null;comment:高度" json:"imageheight"`         // 高度
	Imagetype   string `gorm:"column:imagetype;not null;comment:图片类型" json:"imagetype"`           // 图片类型
	Imageframes uint64 `gorm:"column:imageframes;not null;comment:图片帧数" json:"imageframes"`       // 图片帧数
	Filesize    uint64 `gorm:"column:filesize;not null;comment:文件大小" json:"filesize"`             // 文件大小
	Mimetype    string `gorm:"column:mimetype;not null;comment:mime类型" json:"mimetype"`           // mime类型
	Extparam    string `gorm:"column:extparam;not null;comment:透传数据" json:"extparam"`             // 透传数据
	Storage     string `gorm:"column:storage;not null;default:local;comment:存储位置" json:"storage"` // 存储位置
	Sha1        string `gorm:"column:sha1;not null;comment:文件 sha1编码" json:"sha1"`                // 文件 sha1编码
	Title       string `gorm:"column:title;not null;comment:文件名称" json:"title"`                   // 文件名称
	Name        string `gorm:"column:name;not null;comment:附件名称" json:"name"`                     // 附件名称
	CoverURL    string `gorm:"column:cover_url;not null;comment:视频封面" json:"cover_url"`           // 视频封面
}

// TableName Attachment's table name
func (*Attachment) TableName() string {
	return TableNameAttachment
}
