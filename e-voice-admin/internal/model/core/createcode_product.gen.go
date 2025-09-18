package core

import (
	"gofly/internal/model/base"
)

const TableNameCreatecodeProduct = "createcode_product"

// CreatecodeProduct 测试代码产品
type CreatecodeProduct struct {
	base.IdModel
	Title      string  `gorm:"column:title;not null;comment:标题" json:"title"`               // 标题
	Num        int64   `gorm:"column:num;not null;comment:库存" json:"num"`                   // 库存
	Price      float64 `gorm:"column:price;not null;comment:价格" json:"price"`               // 价格
	Content    string  `gorm:"column:content;not null;comment:内容" json:"content"`           // 内容
	Createtime int64   `gorm:"column:create_time;not null;comment:上传时间" json:"create_time"` // 上传时间
}

// TableName CreatecodeProduct's table name
func (*CreatecodeProduct) TableName() string {
	return TableNameCreatecodeProduct
}
