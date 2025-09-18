package core

import (
	"gofly/internal/model/base"
)

const TableNameLoginLog = "login_logs"

// LoginLog （平台及客户）后台登录日志
type LoginLog struct {
	base.TimeModel
	Type    int    `gorm:"column:type;not null;default:1;comment:类型1=平台。2=b端，3=C端" json:"type"` // 类型1=平台。2=b端，3=C端
	UID     int64  `gorm:"column:uid;not null;comment:用户id" json:"uid"`                         // 用户id
	OutIn   string `gorm:"column:out_in;not null;comment:登录或退出 out in" json:"out_in"`           // 登录或退出 out in
	LoginIP string `gorm:"column:loginIP;not null;comment:登录IP" json:"loginIP"`                 // 登录IP
}

// TableName LoginLog's table name
func (*LoginLog) TableName() string {
	return TableNameLoginLog
}
