package dto

import (
	"gofly/internal/model/base"
)

// VoiceHotwordPageReq 热词分页请求
type VoiceHotwordPageReq struct {
	base.IPage
	Word string `form:"word" json:"word"` // 热词关键字搜索
	// 日期区间 格式：yyyy-MM-dd,yyyy-MM-dd
	CreatedTime string `form:"createdTime" json:"createdTime"`
}
