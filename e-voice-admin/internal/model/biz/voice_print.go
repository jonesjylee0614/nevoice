package biz

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

// VoicePrint 声纹信息
type VoicePrint struct {
	base.DeleteModel        // 逻辑删除
	UserId           int64  `gorm:"comment:用户ID" json:"userId"`
	UserName         string `gorm:"size:100;comment:用户名" json:"userName"`
	PrintId          int64  `gorm:"comment:声纹ID" json:"printId"`
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&VoicePrint{})
}

func (v VoicePrint) TableName() string {
	return "voice_print"
}
