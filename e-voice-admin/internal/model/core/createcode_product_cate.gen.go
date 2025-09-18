package core

import (
	"gofly/internal/model/base"
)

const TableNameCreatecodeProductCate = "createcode_product_cate"

// CreatecodeProductCate 测试代码产品分类
type CreatecodeProductCate struct {
	base.TimeModel
	Name string `gorm:"column:name;not null;comment:名称" json:"name"` // 名称
}

// TableName CreatecodeProductCate's table name
func (*CreatecodeProductCate) TableName() string {
	return TableNameCreatecodeProductCate
}
