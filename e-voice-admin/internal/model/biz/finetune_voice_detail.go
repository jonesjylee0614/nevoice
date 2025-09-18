package biz

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

// FinetuneVoiceDetail 模型微调语料记录
type FinetuneVoiceDetail struct {
	base.Model
	// 当发起微调任务时，查询所有未关联任务的语料，关联到微调任务中
	FinetuneId int64  `gorm:"comment:微调任务id;index;" json:"finetuneId"`
	VoicePath  string `gorm:"size:1000;comment:音频绝对路径" json:"voicePath"`
	Text       string `gorm:"comment:语料对应的文字;" json:"text"`
	// 通过会议详情修改过来的语料，多次修改保留一次
	MeetingDetailId int64 `gorm:"comment:会议详情id;index;" json:"meetingDetailId"`
	MeetingId       int64 `gorm:"comment:会议id;index;" json:"meetingId"`
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&FinetuneVoiceDetail{})
}

func (v FinetuneVoiceDetail) TableName() string {
	return "finetune_voice_detail"
}
