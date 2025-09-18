package core_dto

import (
	"gofly/internal/model/base"
)

type LoginLogPageReq struct {
	base.IPage
	Uid int64 `form:"uid" json:"uid" default:"0"`
}
