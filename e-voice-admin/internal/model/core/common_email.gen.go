package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonEmail = "common_email"

// CommonEmail 业务端邮箱
type CommonEmail struct {
	base.IdModel
	SenderEmail string `gorm:"column:sender_email;not null;comment:发送者邮箱" json:"sender_email"`   // 发送者邮箱
	AuthCode    string `gorm:"column:auth_code;not null;comment:邮箱授权码" json:"auth_code"`         // 邮箱授权码
	MailTitle   string `gorm:"column:mail_title;not null;comment:邮件标题" json:"mail_title"`        // 邮件标题
	MailBody    string `gorm:"column:mail_body;not null;comment:邮件内容,可以是html" json:"mail_body"`  // 邮件内容,可以是html
	ServiceHost string `gorm:"column:service_host;not null;comment:邮件服务器" json:"service_host"`   // 邮件服务器
	ServicePort int64  `gorm:"column:service_port;not null;comment:邮件服务器端口" json:"service_port"` // 邮件服务器端口
}

// TableName CommonEmail's table name
func (*CommonEmail) TableName() string {
	return TableNameCommonEmail
}
