package biz

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

// VoiceHotword 医疗热词
type VoiceHotword struct {
	base.Model
	Word   string `gorm:"size:200;not null;uniqueIndex;comment:热词内容" json:"word"`
	Status int    `gorm:"default:1;comment:状态 1启用 0禁用" json:"status"`
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&VoiceHotword{})
}

func (v *VoiceHotword) TableName() string {
	return "voice_hotword"
}

