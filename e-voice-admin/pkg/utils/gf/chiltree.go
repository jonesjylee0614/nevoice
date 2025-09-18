package gf

import (
	"gofly/internal/model/base"
	"gofly/pkg/utils/collx"
)

// GetAllChildren 递归查询所有子集
func GetAllChildren(tablename string, ids []int64) []int64 {
	var res []int64
	getAllChild(&res, tablename, ids)
	return collx.Unique(res)
}

// 获取所有子级ID
func getAllChild(res *[]int64, tablename string, ids []int64) []int64 {

	var subIds []int64
	base.GormDb.Table(tablename).Select("id").Where("pid", ids).Scan(&subIds)

	if len(subIds) > 0 {
		*res = append(*res, subIds...)
		*res = append(*res, getAllChild(res, tablename, subIds)...)
	}
	return *res
}
