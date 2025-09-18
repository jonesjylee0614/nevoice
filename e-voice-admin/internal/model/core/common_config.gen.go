package core

import (
	"gofly/internal/model/base"
)

const TableNameCommonConfig = "common_config"

// CommonConfig 系统配置参数
type CommonConfig struct {
	base.IdModel
	Keyname  string `gorm:"column:keyname;not null;comment:配置名称" json:"keyname"`  // 配置名称
	Keyvalue string `gorm:"column:keyvalue;not null;comment:配置值" json:"keyvalue"` // 配置值
	Des      string `gorm:"column:des;not null;comment:描述" json:"des"`            // 描述
	Weigh    int64  `gorm:"column:weigh;not null;comment:排序" json:"weigh"`        // 排序
}

// TableName CommonConfig's table name
func (*CommonConfig) TableName() string {
	return TableNameCommonConfig
}
