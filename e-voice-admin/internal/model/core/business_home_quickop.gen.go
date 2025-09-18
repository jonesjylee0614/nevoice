package core

import (
	"gofly/internal/model/base"
)

const TableNameBusinessHomeQuickop = "business_home_quickop"

// BusinessHomeQuickop 首页快捷操作
type BusinessHomeQuickop struct {
	base.IdModel
	UID      int64  `gorm:"column:uid;not null;comment:添加人" json:"uid"`               // 添加人
	IsCommon bool   `gorm:"column:is_common;not null;comment:公共1=是" json:"is_common"` // 公共1=是
	Type     int64  `gorm:"column:type;not null;comment:类型1=外部" json:"type"`          // 类型1=外部
	Name     string `gorm:"column:name;not null;comment:快捷名称" json:"name"`            // 快捷名称
	PathURL  string `gorm:"column:path_url;not null;comment:跳转路径" json:"path_url"`    // 跳转路径
	Icon     string `gorm:"column:icon;not null;comment:图标" json:"icon"`              // 图标
	Weigh    int64  `gorm:"column:weigh;not null;comment:权重" json:"weigh"`            // 权重
}

// TableName BusinessHomeQuickop's table name
func (*BusinessHomeQuickop) TableName() string {
	return TableNameBusinessHomeQuickop
}
