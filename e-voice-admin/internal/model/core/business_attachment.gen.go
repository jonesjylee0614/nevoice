package core

import (
	"gofly/internal/model/base"
)

const TableNameBusinessAttachment = "business_attachment"

// BusinessAttachment 客户端附件
type BusinessAttachment struct {
	base.TimeModel
	Weigh       int64  `gorm:"column:weigh;not null;comment:排序" json:"weigh"`                     // 排序
	Pid         int64  `gorm:"column:pid;not null;comment:附件" json:"pid"`                         // 附件
	Name        string `gorm:"column:name;not null;comment:附件原来名称" json:"name"`                   // 附件原来名称
	Title       string `gorm:"column:title;not null;comment:文件名称" json:"title"`                   // 文件名称
	Type        int64  `gorm:"column:type;not null;comment:文件类型0=图片，1=文件夹,2=视频，3=音频" json:"type"` // 文件类型0=图片，1=文件夹,2=视频，3=音频
	URL         string `gorm:"column:url;not null;comment:访问路径" json:"url"`                       // 访问路径
	Imagewidth  string `gorm:"column:imagewidth;not null;comment:宽度" json:"imagewidth"`           // 宽度
	Imageheight string `gorm:"column:imageheight;not null;comment:高度" json:"imageheight"`         // 高度
	Filesize    int64  `gorm:"column:filesize;not null;comment:文件大小" json:"filesize"`             // 文件大小
	Mimetype    string `gorm:"column:mimetype;not null;comment:mime类型" json:"mimetype"`           // mime类型
	Extparam    string `gorm:"column:extparam;not null;comment:透传数据" json:"extparam"`             // 透传数据
	Storage     string `gorm:"column:storage;not null;default:local;comment:存储位置" json:"storage"` // 存储位置
	CoverURL    string `gorm:"column:cover_url;not null;comment:视频封面" json:"cover_url"`           // 视频封面
	Sha1        string `gorm:"column:sha1;not null;comment:文件 sha1编码" json:"sha1"`                // 文件 sha1编码
	IsCommon    int64  `gorm:"column:is_common;not null;comment:是否公共1=是" json:"is_common"`        // 是否公共1=是
}

// TableName BusinessAttachment's table name
func (*BusinessAttachment) TableName() string {
	return TableNameBusinessAttachment
}
