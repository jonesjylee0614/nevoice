package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonGeneratecodeField = "common_generatecode_field"

// CommonGeneratecodeField 生成代码字段管理
type CommonGeneratecodeField struct {
	base.IdModel
	GeneratecodeID int64  `gorm:"column:generatecode_id;not null;comment:关联列表" json:"generatecode_id"` // 关联列表
	Name           string `gorm:"column:name;not null;comment:字段名称" json:"name"`                       // 字段名称
	Field          string `gorm:"column:field;not null;comment:字段" json:"field"`                       // 字段
	Align          string `gorm:"column:align;not null;default:left;comment:对齐方向" json:"align"`        // 对齐方向
	Width          int64  `gorm:"column:width;not null;comment:宽度" json:"width"`                       // 宽度
	Formtype       string `gorm:"column:formtype;not null;comment:表单类型" json:"formtype"`               // 表单类型
	Datatable      string `gorm:"column:datatable;not null;comment:关联数据表" json:"datatable"`            // 关联数据表
	Datatablename  string `gorm:"column:datatablename;not null;comment:关联显示字段" json:"datatablename"`   // 关联显示字段
	Searchway      string `gorm:"column:searchway;not null;default:=;comment:查询方式" json:"searchway"`   // 查询方式
	Searchtype     string `gorm:"column:searchtype;not null;comment:查询文本类型" json:"searchtype"`         // 查询文本类型
	FieldWeigh     int64  `gorm:"column:field_weigh;not null;comment:表单排序" json:"field_weigh"`         // 表单排序
	ListWeigh      int64  `gorm:"column:list_weigh;not null;comment:列表排序" json:"list_weigh"`           // 列表排序
	SearchWeigh    int64  `gorm:"column:search_weigh;not null;comment:搜索排序" json:"search_weigh"`       // 搜索排序
	DefValue       string `gorm:"column:def_value;not null;comment:默认选项json" json:"def_value"`         // 默认选项json
	Islist         int    `gorm:"column:islist;not null;comment:是否是列表1=是" json:"islist"`               // 是否是列表1=是
	Isorder        int    `gorm:"column:isorder;not null;comment:是否参与排序" json:"isorder"`               // 是否参与排序
	Isform         int    `gorm:"column:isform;not null;comment:是否为表单字段" json:"isform"`                // 是否为表单字段
	Required       int    `gorm:"column:required;not null;comment:是否为必填项" json:"required"`             // 是否为必填项
	Issearch       int    `gorm:"column:issearch;not null;comment:是否查询" json:"issearch"`               // 是否查询

}

// TableName CommonGeneratecodeField's table name
func (*CommonGeneratecodeField) TableName() string {
	return TableNameCommonGeneratecodeField
}
