package core

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

const TableNameCommonDictionaryData = "common_dictionary_data"

// CommonDictionaryData 字典数据-测试数据
type CommonDictionaryData struct {
	base.Model
	DicId    string `gorm:"column:dic_id;not null;comment:字典项值" json:"dicId"`      // 字典id
	Keyname  string `gorm:"column:keyname;not null;comment:字典名称" json:"keyname"`   // 字典名称
	Keyvalue string `gorm:"column:keyvalue;not null;comment:字典项值" json:"keyvalue"` // 字典项值
	Des      string `gorm:"column:des;not null;comment:字典描述" json:"des"`           // 字典描述
	Status   int64  `gorm:"column:status;not null;comment:状态" json:"status"`       // 状态 0启用 1禁用
	Weigh    int64  `gorm:"column:weigh;not null;comment:排序" json:"weigh"`         // 排序
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&CommonDictionaryData{})
}

// TableName CommonDictionaryData's table name
func (*CommonDictionaryData) TableName() string {
	return TableNameCommonDictionaryData
}
