package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonLogininfo = "common_logininfo"

// CommonLogininfo 登录页面内容
type CommonLogininfo struct {
	base.TimeModel
	Type   string `gorm:"column:type;not null;default:common;comment:admin=管理端，business=商业端 common=公共" json:"type"` // admin=管理端，business=商业端 common=公共
	Title  string `gorm:"column:title;not null;comment:标题" json:"title"`                                            // 标题
	Des    string `gorm:"column:des;not null;comment:描述" json:"des"`                                                // 描述
	Image  string `gorm:"column:image;not null;comment:图片" json:"image"`                                            // 图片
	Status int64  `gorm:"column:status;not null;comment:状态" json:"status"`                                          // 状态
	Weigh  int64  `gorm:"column:weigh;not null;comment:排序" json:"weigh"`                                            // 排序
}

// TableName CommonLogininfo's table name
func (*CommonLogininfo) TableName() string {
	return TableNameCommonLogininfo
}
