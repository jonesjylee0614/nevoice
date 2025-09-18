package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonGeneratecode = "common_generatecode"

// CommonGeneratecode 代码生成
type CommonGeneratecode struct {
	base.TimeModel
	Tablename     string `gorm:"column:tablename;not null;comment:表名称" json:"tablename"`                                  // 表名称
	Comment       string `gorm:"column:comment;not null;comment:表备注" json:"comment"`                                      // 表备注
	Engine        string `gorm:"column:engine;not null;comment:引擎" json:"engine"`                                         // 引擎
	TableRows     int64  `gorm:"column:table_rows;not null;comment:记录数" json:"table_rows"`                                // 记录数
	Collation     string `gorm:"column:collation;not null;comment:编码" json:"collation"`                                   // 编码
	AutoIncrement int64  `gorm:"column:auto_increment;not null;default:1;comment:自增索引" json:"auto_increment"`             // 自增索引
	Status        int64  `gorm:"column:status;not null;comment:状态1=禁用" json:"status"`                                     // 状态1=禁用
	Pid           int64  `gorm:"column:pid;not null;comment:菜单上级" json:"pid"`                                             // 菜单上级
	Icon          string `gorm:"column:icon;comment:图标" json:"icon"`                                                      // 图标
	RoutePath     string `gorm:"column:routePath;comment:路由地址" json:"routePath"`                                          // 路由地址
	RouteName     string `gorm:"column:routeName;comment:路由名称" json:"routeName"`                                          // 路由名称
	Component     string `gorm:"column:component;comment:组件路径" json:"component"`                                          // 组件路径
	APIPath       string `gorm:"column:api_path;comment:后端业务接口" json:"api_path"`                                          // 后端业务接口
	APIFilename   string `gorm:"column:api_filename;comment:后端文件名" json:"api_filename"`                                   // 后端文件名
	Fields        string `gorm:"column:fields;comment:查询字段" json:"fields"`                                                // 查询字段
	RuleID        int64  `gorm:"column:rule_id;not null;comment:生成菜单id" json:"rule_id"`                                   // 生成菜单id
	RuleName      string `gorm:"column:rule_name;not null;comment:菜单名称" json:"rule_name"`                                 // 菜单名称
	IsInstall     int64  `gorm:"column:is_install;not null;comment:是否安装0=未安装，1=已安装，2=已卸载" json:"is_install"`              // 是否安装0=未安装，1=已安装，2=已卸载
	TplType       string `gorm:"column:tpl_type;not null;default:list;comment:模板类型list=仅一个数据，cate=数据加分类" json:"tpl_type"` // 模板类型list=仅一个数据，cate=数据加分类
	CateTablename string `gorm:"column:cate_tablename;comment:分类表名称" json:"cate_tablename"`                               // 分类表名称
}

// TableName CommonGeneratecode's table name
func (*CommonGeneratecode) TableName() string {
	return TableNameCommonGeneratecode
}
