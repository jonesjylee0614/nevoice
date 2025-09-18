package core_dto

import (
	"gofly/internal/model/base"
)

type DictPageReq struct {
	base.IPage
	Title  string `form:"title" json:"title"`
	DicId  int64  `form:"dicId" json:"dicId"`
	Status string `form:"status" json:"status"`
}
