package core

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

const TableNameBusinessAuthDept = "business_auth_dept"

// BusinessAuthDept 管理后台部门
type BusinessAuthDept struct {
	base.Model
	UID    int64  `gorm:"column:uid;not null;comment:添加用户" json:"uid"`     // 添加用户
	Name   string `gorm:"column:name;not null;comment:部门名称" json:"name"`   // 部门名称
	Pid    int64  `gorm:"column:pid;not null;comment:上级部门" json:"pid"`     // 上级部门
	Weigh  int64  `gorm:"column:weigh;not null;comment:排序" json:"weigh"`   // 排序
	Status int64  `gorm:"column:status;not null;comment:状态" json:"status"` // 状态
	Remark string `gorm:"column:remark;not null;comment:备注" json:"remark"` // 备注
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&BusinessAuthDept{})
}

// TableName BusinessAuthDept's table name
func (*BusinessAuthDept) TableName() string {
	return TableNameBusinessAuthDept
}
