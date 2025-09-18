package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonPictureCate = "common_picture_cate"

// CommonPictureCate 分类名称
type CommonPictureCate struct {
	base.TimeModel
	UID    int64  `gorm:"column:uid;not null;comment:添加账号" json:"uid"`                 // 添加账号
	Weigh  int64  `gorm:"column:weigh;not null;comment:排序" json:"weigh"`               // 排序
	Type   int64  `gorm:"column:type;not null;comment:类型0=素材图1=插图,2=两种共有" json:"type"` // 类型0=素材图1=插图,2=两种共有
	Name   string `gorm:"column:name;not null;comment:分类名称" json:"name"`               // 分类名称
	Status int64  `gorm:"column:status;not null;comment:状态1=禁用" json:"status"`         // 状态1=禁用
	Remark string `gorm:"column:remark;not null;comment:备注" json:"remark"`             // 备注
}

// TableName CommonPictureCate's table name
func (*CommonPictureCate) TableName() string {
	return TableNameCommonPictureCate
}
