package biz

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

// VoiceDocument 录音范文
type VoiceDocument struct {
	base.Model
	Name    string `gorm:"size:100;comment:范文名" json:"name"`
	Content string `gorm:"size:1000;comment:范文内容" json:"content"`
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&VoiceDocument{})
}

func (v *VoiceDocument) TableName() string {
	return "voice_document"
}
