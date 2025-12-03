package dto

import (
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/json"
)

// ========== 会议主表 DTO ==========

// MeetingMdtPageReq 会议列表分页查询请求
type MeetingMdtPageReq struct {
	*base.IPage
	Title    string `form:"title" json:"title"`
	Status   *int64 `form:"status" json:"status"`
	HostName string `form:"hostName" json:"hostName"`
	// 日期区间 格式：yyyy-MM-dd,yyyy-MM-dd
	CreatedTime string `form:"createdTime" json:"createdTime"`
	StartTime   string `form:"startTime" json:"startTime"`
}

// MeetingMdtCreateReq 创建会议请求
type MeetingMdtCreateReq struct {
	Title       string         `form:"title" json:"title"`
	Description string         `form:"description" json:"description"`
	HostId      *int64         `form:"hostId" json:"hostId"`
	HostName    string         `form:"hostName" json:"hostName"`
	StartTime   *json.JsonTime `form:"startTime" json:"startTime"`
	EndTime     *json.JsonTime `form:"endTime" json:"endTime"`
	Tags        []string       `form:"tags" json:"tags"`
}

// MeetingMdtUpdateReq 更新会议请求
type MeetingMdtUpdateReq struct {
	Id          int64          `form:"id" json:"id" binding:"required"`
	Title       string         `form:"title" json:"title"`
	Description string         `form:"description" json:"description"`
	HostId      *int64         `form:"hostId" json:"hostId"`
	HostName    string         `form:"hostName" json:"hostName"`
	StartTime   *json.JsonTime `form:"startTime" json:"startTime"`
	EndTime     *json.JsonTime `form:"endTime" json:"endTime"`
	Status      *int64         `form:"status" json:"status"`
	Tags        []string       `form:"tags" json:"tags"`
}

// MeetingMdtDetailRes 会议详情响应
type MeetingMdtDetailRes struct {
	*biz.MeetingMdt
	Dialogs         []MeetingMdtDialogRes `json:"dialogs"`
	ParticipantList []MeetingParticipant  `json:"participantList"`
	TagList         []string              `json:"tagList"`
}

// MeetingParticipant 参会人信息
type MeetingParticipant struct {
	UserId     int64  `json:"userId"`
	UserName   string `json:"userName"`
	Department string `json:"department"`
	Role       string `json:"role"`
}

// ========== 对话详情 DTO ==========

// MeetingMdtDialogPageReq 对话列表查询请求
type MeetingMdtDialogPageReq struct {
	*base.IPage
	MeetingId int64 `form:"meetingId" json:"meetingId" binding:"required"`
}

// MeetingMdtDialogRes 对话详情响应
type MeetingMdtDialogRes struct {
	*biz.MeetingMdtDialog
}

// MeetingMdtDialogUpdateReq 更新对话文本请求
type MeetingMdtDialogUpdateReq struct {
	Id   int64  `form:"id" json:"id" binding:"required"`
	Text string `form:"text" json:"text" binding:"required"`
}

// MeetingMdtAssignSpeakerReq 指定发言人请求
type MeetingMdtAssignSpeakerReq struct {
	DialogId    int64  `form:"dialogId" json:"dialogId" binding:"required"`
	SpeakerId   int64  `form:"speakerId" json:"speakerId" binding:"required"`
	SpeakerName string `form:"speakerName" json:"speakerName" binding:"required"`
	SpeakerRole string `form:"speakerRole" json:"speakerRole"`
}

// MeetingMdtDialogCreateReq 创建对话请求（实时识别时使用）
type MeetingMdtDialogCreateReq struct {
	MeetingId        int64          `form:"meetingId" json:"meetingId" binding:"required"`
	Seq              int64          `form:"seq" json:"seq"`
	SpeakerId        *int64         `form:"speakerId" json:"speakerId"`
	SpeakerName      string         `form:"speakerName" json:"speakerName"`
	SpeakerRole      string         `form:"speakerRole" json:"speakerRole"`
	Recognized       int64          `form:"recognized" json:"recognized"`
	RecognitionNote  string         `form:"recognitionNote" json:"recognitionNote"`
	RecognitionScore *float64       `form:"recognitionScore" json:"recognitionScore"`
	SpeakTime        *json.JsonTime `form:"speakTime" json:"speakTime"`
	StartOffset      int64          `form:"startOffset" json:"startOffset"`
	EndOffset        int64          `form:"endOffset" json:"endOffset"`
	DurationMs       int64          `form:"durationMs" json:"durationMs"`
	Text             string         `form:"text" json:"text"`
	AudioPath        string         `form:"audioPath" json:"audioPath"`
}

// ========== AI总结 DTO ==========

// MeetingMdtSummaryReq 生成总结请求
type MeetingMdtSummaryReq struct {
	MeetingId int64 `form:"meetingId" json:"meetingId" binding:"required"`
}

// MeetingMdtSummaryRes 总结状态响应
type MeetingMdtSummaryRes struct {
	Status  int64  `json:"status"`
	Summary string `json:"summary"`
	Message string `json:"message"`
}

// ========== 人员库 DTO ==========

// StaffSearchReq 人员搜索请求
type StaffSearchReq struct {
	Keyword string `form:"keyword" json:"keyword"`
	Limit   int    `form:"limit" json:"limit"`
}

// StaffInfo 人员信息
type StaffInfo struct {
	UserId     int64  `json:"userId"`
	UserName   string `json:"userName"`
	Department string `json:"department"`
	Role       string `json:"role"`
}
