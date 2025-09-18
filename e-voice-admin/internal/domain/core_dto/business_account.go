package core_dto

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
)

type BusinessAccountPageReq struct {
	base.IPage
	Cid       int64  `form:"cid" json:"cid"`
	Name      string `form:"name" json:"name"`
	Cimobiled string `form:"cimobiled" json:"cimobiled"`
}

type BusinessAccountPageItem struct {
	*core.BusinessAccount
	Rolename []string `json:"rolename"`
	Roleid   []int64  `json:"roleid"`
	Depname  string   `json:"depname"`
}

type BusinessAccountUpStatus struct {
	Id     int64 `json:"id" binding:"required"`
	Status int64 `json:"status" binding:"required"`
}
type BusinessAccountUpPwdReq struct {
	PasswordOld string `json:"passwordOld" binding:"required"`
	PasswordNew string `json:"passwordNew" binding:"required"`
}
