package core

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

const TableNameBusinessAuthRole = "business_auth_role"

// BusinessAuthRole 权限分组
type BusinessAuthRole struct {
	base.Model
	UID        int64  `gorm:"column:uid;not null;comment:添加用户id" json:"uid"`                                // 添加用户id
	Pid        int64  `gorm:"column:pid;not null;comment:父级" json:"pid"`                                    // 父级
	Name       string `gorm:"column:name;not null;comment:名称" json:"name"`                                  // 名称
	Rules      string `gorm:"column:rules;not null;comment:规则ID 所拥有的权限包扣父级" json:"rules"`                   // 规则ID 所拥有的权限包扣父级
	Menu       string `gorm:"column:menu;not null;comment:选择的id，用于编辑赋值" json:"menu"`                        // 选择的id，用于编辑赋值
	Status     int64  `gorm:"column:status;not null;comment:状态1=禁用" json:"status"`                          // 状态1=禁用
	DataAccess int64  `gorm:"column:data_access;not null;comment:数据权限0=自己1=自己及子权限，2=全部" json:"data_access"` // 数据权限0=自己1=自己及子权限，2=全部
	Remark     string `gorm:"column:remark;not null;comment:描述" json:"remark"`                              // 描述
	Weigh      int64  `gorm:"column:weigh;not null;comment:排序" json:"weigh"`                                // 排序
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&BusinessAuthRole{})
}

// TableName BusinessAuthRole's table name
func (*BusinessAuthRole) TableName() string {
	return TableNameBusinessAuthRole
}
