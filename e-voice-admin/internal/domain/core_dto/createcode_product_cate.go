package core_dto

import (
	"gofly/internal/model/base"
)

type CreatecodeProductCate struct {
	base.IPage
	Title string `form:"title" json:"title"`
	// 时间区间
	CreatedTime string `form:"createdTime" json:"createdTime"`
}
