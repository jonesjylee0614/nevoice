package base

import "gofly/pkg/json"

type IPage struct {
	Page     json.JsonInt64 `form:"page" json:"page" default:"1"`
	PageSize json.JsonInt64 `form:"pageSize" json:"pageSize" default:"10"`
	Total    int64          `form:"-" json:"-"`
}

func NewPage(pageNum, pageSize int64) *IPage {
	return &IPage{
		Page:     *json.NewJsonInt64(pageNum),
		PageSize: *json.NewJsonInt64(pageSize),
	}
}

type Ids struct {
	Ids []*json.JsonInt64 `form:"ids" json:"ids" binding:"required"`
}

func (i Ids) String() []string {
	var str []string
	for _, id := range i.Ids {
		str = append(str, id.String())
	}
	return str
}

type ReqId struct {
	Id int64 `form:"id" json:"id" binding:"required"`
}

type StatusUpd struct {
	Id     int64  `form:"id" json:"id" binding:"required"`
	Status *int64 `form:"status" json:"status" binding:"required"`
}
type OrderUpd struct {
	Id      int64  `form:"id" json:"id" binding:"required"`
	OrderNo uint64 `form:"orderNo" json:"orderNo" binding:"required"`
}
