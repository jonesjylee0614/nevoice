package biz

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
	"gofly/pkg/json"
)

// MeetingMdt MDT会议
type MeetingMdt struct {
	base.DeleteModel
	Title           string         `gorm:"size:200;comment:会议标题" json:"title"`
	Description     string         `gorm:"type:text;comment:会议说明" json:"description"`
	HostId          *int64         `gorm:"comment:主持人ID" json:"hostId"`
	HostName        string         `gorm:"size:100;comment:主持人姓名" json:"hostName"`
	StartTime       *json.JsonTime `gorm:"comment:开始时间" json:"startTime"`
	EndTime         *json.JsonTime `gorm:"comment:结束时间" json:"endTime"`
	Status          int64          `gorm:"default:0;comment:状态 0-待开始 1-进行中 2-已结束" json:"status"`
	Participants    string         `gorm:"type:json;comment:参会人列表" json:"participants"`
	Tags            string         `gorm:"type:json;comment:标签" json:"tags"`
	Summary         string         `gorm:"type:text;comment:AI会议总结" json:"summary"`
	SummaryStatus   int64          `gorm:"default:0;comment:总结状态 0-未生成 1-生成中 2-已生成" json:"summaryStatus"`
	AudioPath       string         `gorm:"size:500;comment:完整录音路径" json:"audioPath"`
	DialogCount     int64          `gorm:"default:0;comment:对话条数" json:"dialogCount"`
	DurationSeconds int64          `gorm:"default:0;comment:会议时长秒" json:"durationSeconds"`
}

// 会议状态常量
const (
	MeetingStatusPending    = 0 // 待开始
	MeetingStatusInProgress = 1 // 进行中
	MeetingStatusEnded      = 2 // 已结束
)

// 总结状态常量
const (
	SummaryStatusNone       = 0 // 未生成
	SummaryStatusGenerating = 1 // 生成中
	SummaryStatusDone       = 2 // 已生成
)

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&MeetingMdt{})
}

func (m MeetingMdt) TableName() string {
	return "meeting_mdt"
}

