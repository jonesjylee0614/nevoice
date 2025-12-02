package dto

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/json"
)

type VoicePrintPageReq struct {
	base.IPage
	Name string `form:"name" json:"name" comment:"用户名"`
}

type VoiceUserPrintPageReq struct {
	base.IPage
	BaseUserIdReq
}

type VoiceUserPrintPageRes struct {
	Total int64                    `form:"total" json:"total"`
	Data  []VoiceUserPrintPageData `form:"data" json:"data"`
}

type VoiceUserPrintPageData struct {
	CreateTime int64  `json:"create_time,omitempty" comment:"创建时间"`
	Id         string `json:"id,omitempty" comment:"用户ID"`
	Txt        string `json:"txt,omitempty" comment:"文字信息"`
	Userid     int64  `json:"userid,omitempty" comment:"用户ID"`
	Username   string `json:"username,omitempty" comment:"用户姓名"`
	WavPath    string `json:"wav_path,omitempty" comment:"音频文件 通过拼接接口域名+userid可访问"`
}

type VoiceUserPrintDelReq struct {
	BaseUserIdReq
	DocId string `form:"docId" json:"docId" comment:"声纹ID" binding:"required"`
}

type BaseUserIdReq struct {
	// 需要接收前端字符串参数，但是python后端固定需要int64
	UserId *json.JsonInt64 `form:"userId" json:"userId" comment:"用户ID" binding:"required"`
}

type VoiceUserPrintIdentifyRes struct {
	Error string                       `json:"error"`
	Txt   string                       `json:"txt"`
	Data  []VoiceUserPrintIdentifyData `json:"data"`
}

type VoiceUserPrintIdentifyData struct {
	Id       string         `json:"id"`
	Username string         `json:"username"`
	Userid   json.JsonInt64 `json:"userid"`
	Score    float64        `json:"_score"`
}

type UserPrintIdentifyRes struct {
	Txt  string                `json:"txt" comment:"音频中的文本信息"`
	User *core.BusinessAccount `json:"user" comment:"声纹鉴定出的用户信息"`
}
