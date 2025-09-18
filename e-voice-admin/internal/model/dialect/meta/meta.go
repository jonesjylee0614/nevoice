package meta

type Column struct {
	TableName     string `gorm:"column:tableName" json:"tableName"`         // 表名
	ColumnName    string `gorm:"column:columnName" json:"columnName"`       // 列名
	DataType      string `gorm:"column:dataType" json:"dataType"`           // 数据类型
	ColumnComment string `gorm:"column:columnComment" json:"columnComment"` // 列备注
	IsPrimaryKey  bool   `gorm:"column:isPrimaryKey" json:"isPrimaryKey"`   // 是否为主键
	IsIdentity    bool   `gorm:"column:isIdentity" json:"isIdentity"`       // 是否自增
	ColumnDefault string `gorm:"column:columnDefault" json:"columnDefault"` // 默认值
	Nullable      bool   `gorm:"column:nullable" json:"nullable"`           // 是否可为null
	CharMaxLength int    `gorm:"column:charMaxLength" json:"charMaxLength"` // 字符最大长度
	NumPrecision  int    `gorm:"column:numPrecision" json:"numPrecision"`   // 精度(总数字位数)
	NumScale      int    `gorm:"column:numScale" json:"numScale"`           // 小数点位数
	Extra         string `gorm:"column:extra" json:"extra"`                 // 其他额外信息
}

type Table struct {
	TableName    string `gorm:"column:tableName" json:"tableName"`       // 表名
	TableComment string `gorm:"column:tableComment" json:"tableComment"` // 表备注
	CreateTime   string `gorm:"column:createTime" json:"createTime"`     // 创建时间
	TableRows    int64  `gorm:"column:tableRows" json:"tableRows"`
	DataLength   int64  `gorm:"column:dataLength" json:"dataLength"`
	IndexLength  int64  `gorm:"column:indexLength" json:"indexLength"`
}
