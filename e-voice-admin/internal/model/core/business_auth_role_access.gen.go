package core

import (
	"gofly/internal/model/base"
)

const TableNameBusinessAuthRoleAccess = "business_auth_role_access"

// BusinessAuthRoleAccess 商务端菜单授权
type BusinessAuthRoleAccess struct {
	base.IdModel
	Uid    int64 `gorm:"column:uid;comment:用户ID" json:"用户id"`
	RoleID int64 `gorm:"column:role_id;not null;comment:授权id" json:"role_id"` // 授权id
}

// TableName BusinessAuthRoleAccess's table name
func (*BusinessAuthRoleAccess) TableName() string {
	return TableNameBusinessAuthRoleAccess
}
