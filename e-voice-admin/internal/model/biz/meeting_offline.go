package biz

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
	"gofly/pkg/json"
)

// MeetingOffline 离线会议
type MeetingOffline struct {
	base.Model
	Name        string         `gorm:"size:200;comment:会议名" json:"name"`
	MeetingTime *json.JsonTime `gorm:"comment:会议时间" json:"meetingTime"`
	AudioPath   string         `gorm:"size:300;comment:音频路径" json:"audioPath"`
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&MeetingOffline{})
}

func (v MeetingOffline) TableName() string {
	return "meeting_offline"
}
