package dto

import (
	"gofly/internal/model/base"
)

type VoiceDocumentPageReq struct {
	base.IPage
	Title string `form:"title" json:"title"`
	// 日期区间 格式：yyyy-MM-dd,yyyy-MM-dd
	CreatedTime string `form:"createdTime" json:"createdTime"`
}
