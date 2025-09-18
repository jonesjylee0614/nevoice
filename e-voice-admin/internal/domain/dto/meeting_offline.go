package dto

import (
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/json"
)

type MeetingOfflinePageReq struct {
	*base.IPage
	Title string `form:"title" json:"title"`
	// 日期区间 格式：yyyy-MM-dd,yyyy-MM-dd
	CreatedTime string `form:"createdTime" json:"createdTime"`
}

type MeetingOfflineUpdateReq struct {
	Id          int64          `form:"id" json:"id" binding:"required"`
	Name        string         `form:"name" json:"name" binding:"required"`
	MeetingTime *json.JsonTime `gorm:"comment:会议时间" json:"meetingTime"`
}

type MeetingOfflineDetailUpdateReq struct {
	Id   int64  `form:"id" json:"id"`
	Text string `form:"text" json:"text"`
}

type MeetingOfflineDetailRes struct {
	*biz.MeetingOfflineDetail
	SpkUserName   string `form:"spkUserName" json:"spkUserName"`
	SpkUserAvatar string `form:"spkUserAvatar" json:"spkUserAvatar"`
}

type MeetingOfflineDetailTrainReq struct {
	Id  int64 `form:"id" json:"id"`
	Add bool  `form:"add" json:"add"`
}
