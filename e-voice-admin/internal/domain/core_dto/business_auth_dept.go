package core_dto

import (
	"gofly/internal/model/base"
)

type DeptPageReq struct {
	Name   string `form:"name" json:"name"`
	Status int64  `form:"status" json:"status"`
}

type UpDeptGroupPidReq struct {
	base.Ids
	Pid int64 `form:"pid" json:"pid" binding:"required"`
}
