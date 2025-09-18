package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonDictionaryTable = "common_dictionary_table"

// CommonDictionaryTable 字典表
type CommonDictionaryTable struct {
	base.TimeModel
	Title     string `gorm:"column:title;not null;comment:字典名称" json:"title"`          // 字典名称
	Remark    string `gorm:"column:remark;not null;comment:备注" json:"remark"`          // 备注
	Tablename string `gorm:"column:tablename;not null;comment:数据表名称" json:"tablename"` // 数据表名称
	Status    int64  `gorm:"column:status;not null;comment:状态" json:"status"`          // 状态
	Weigh     int64  `gorm:"column:weigh;not null;comment:排序" json:"weigh"`            // 排序
}

// TableName CommonDictionaryTable's table name
func (*CommonDictionaryTable) TableName() string {
	return TableNameCommonDictionaryTable
}
