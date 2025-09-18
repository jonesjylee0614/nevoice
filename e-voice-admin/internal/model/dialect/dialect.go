package dialect

import (
	"database/sql"
	"fmt"
	"gofly/internal/config"
	"gofly/internal/model/dialect/meta"
	"gofly/pkg/utils/collx"

	"gorm.io/gorm"
)

type Dialect interface {
	GetDriver() string
	GetDsn(*config.DBconf, bool) string
	OpenGorm(*config.DBconf) *gorm.DB
	// Tables 获取表信息 (tableNames 为空时获取所有表)
	Tables(tableNames ...string) []meta.Table
	// Columns 获取列信息 (tableNames 为空时获取所有表的列信息)
	Columns(tableNames ...string) []meta.Column
	GetCreateDatabaseSql(dbName string) string
	// InitParams 执行一些初始化参数
	InitParams(db *gorm.DB)
}

var Map = map[string]Dialect{
	"mysql":    MysqlInst,    // github.com/go-sql-driver/mysql
	"postgres": PostgresInst, // github.com/go-sql-driver/mysql
}

func GetByDriverName(driverName string) Dialect {
	drivers := sql.Drivers()
	if !collx.ArrayContains(drivers, driverName) {
		panic(fmt.Sprintf("数据库驱动不存在： %s", driverName))
	}

	if v, ok := Map[driverName]; ok {
		return v
	}

	panic(fmt.Sprintf("未适配数据库： %s", driverName))
}
