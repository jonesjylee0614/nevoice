package biz

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
	"gofly/pkg/json"
)

// MeetingOfflineDetail 离线会议详情
type MeetingOfflineDetail struct {
	base.Model
	MeetingId   int64          `gorm:"comment:会议ID;index" json:"meetingId"`
	Sort        int64          `gorm:"comment:序号" json:"sort"`
	SpkUserId   int64          `gorm:"comment:发言人ID" json:"spkUserId"`
	SpkTime     *json.JsonTime `gorm:"comment:发言时间，根据发言时长、会议开始时间和发言时间戳自动计算" json:"spkTime"`
	Text        string         `gorm:"comment:发言内容" json:"text"`
	WavPath     string         `gorm:"comment:音频路径" json:"wavPath"`
	TrainStatus *int64         `gorm:"comment:训练状态，0、不参与训练 66、已完成训练 55、待训练" json:"trainStatus" default:"0"`
	TrainId     int64          `gorm:"comment:训练任务ID;index" json:"trainId"`
}

var (
	none = int64(0)
	wait = int64(55)
	done = int64(66)

	TrainStatusNone = &none
	TrainStatusWait = &wait
	TrainStatusDone = &done
)

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&MeetingOfflineDetail{})
}

func (v MeetingOfflineDetail) TableName() string {
	return "meeting_offline_detail"
}
