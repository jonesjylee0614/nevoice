package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonMessage = "common_message"

// CommonMessage 系统通用消息
type CommonMessage struct {
	base.TimeModel
	Adduid  int64  `gorm:"column:adduid;not null;comment:添加用户" json:"adduid"`                   // 添加用户
	Touid   int64  `gorm:"column:touid;not null;comment:接收用户" json:"touid"`                     // 接收用户
	Type    int64  `gorm:"column:type;not null;default:2;comment:类型1=通知，2=消息，3=代办" json:"type"` // 类型1=通知，2=消息，3=代办
	Title   string `gorm:"column:title;not null;comment:消息标题" json:"title"`                     // 消息标题
	Path    string `gorm:"column:path;not null;comment:跳转路由" json:"path"`                       // 跳转路由
	Content string `gorm:"column:content;not null;comment:消息内容" json:"content"`                 // 消息内容
	Isread  bool   `gorm:"column:isread;not null;comment:是否已读1=已读" json:"isread"`               // 是否已读1=已读
}

// TableName CommonMessage's table name
func (*CommonMessage) TableName() string {
	return TableNameCommonMessage
}
