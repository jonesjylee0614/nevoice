package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonVerifyCode = "common_verify_code"

// CommonVerifyCode 验证码存储
type CommonVerifyCode struct {
	base.TimeModel
	Keyname string `gorm:"column:keyname;not null;comment:存储key" json:"keyname"` // 存储key
	Code    string `gorm:"column:code;not null;comment:验证码" json:"code"`         // 验证码
}

// TableName CommonVerifyCode's table name
func (*CommonVerifyCode) TableName() string {
	return TableNameCommonVerifyCode
}
