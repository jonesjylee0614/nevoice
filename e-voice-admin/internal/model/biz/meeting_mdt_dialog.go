package biz

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
	"gofly/pkg/json"
)

// MeetingMdtDialog MDT会议对话详情
type MeetingMdtDialog struct {
	base.TimeModel
	MeetingId        int64          `gorm:"comment:会议ID;index" json:"meetingId"`
	Seq              int64          `gorm:"comment:序号" json:"seq"`
	SpeakerId        *int64         `gorm:"comment:发言人ID" json:"speakerId"`
	SpeakerName      string         `gorm:"size:100;comment:发言人姓名" json:"speakerName"`
	SpeakerRole      string         `gorm:"size:200;comment:发言人角色" json:"speakerRole"`
	Recognized       int64          `gorm:"default:0;comment:识别状态 0-未识别 1-声纹自动识别 2-手动指定" json:"recognized"`
	RecognitionNote  string         `gorm:"size:200;comment:识别备注" json:"recognitionNote"`
	RecognitionScore *float64       `gorm:"type:decimal(5,4);comment:声纹匹配相似度" json:"recognitionScore"`
	SpeakTime        *json.JsonTime `gorm:"comment:发言时间" json:"speakTime"`
	StartOffset      int64          `gorm:"default:0;comment:录音起始偏移ms" json:"startOffset"`
	EndOffset        int64          `gorm:"default:0;comment:录音结束偏移ms" json:"endOffset"`
	DurationMs       int64          `gorm:"default:0;comment:发言时长ms" json:"durationMs"`
	Text             string         `gorm:"type:text;comment:识别文本" json:"text"`
	AudioPath        string         `gorm:"size:500;comment:音频片段路径" json:"audioPath"`
}

// 识别状态常量
const (
	RecognizedNone   = 0 // 未识别
	RecognizedAuto   = 1 // 声纹自动识别
	RecognizedManual = 2 // 手动指定
)

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&MeetingMdtDialog{})
}

func (m MeetingMdtDialog) TableName() string {
	return "meeting_mdt_dialog"
}

