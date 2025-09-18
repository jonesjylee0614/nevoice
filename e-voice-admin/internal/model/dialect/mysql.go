package dialect

import (
	"fmt"
	"gofly/internal/config"
	"gofly/internal/model/base"
	"gofly/internal/model/dialect/meta"
	"gofly/pkg/utils/stringx"
	"strings"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

type Mysql struct {
	Driver string
}

var _ Dialect = (*Mysql)(nil)
var MysqlInst = &Mysql{
	Driver: "mysql",
}

func (m *Mysql) GetDriver() string {
	return m.Driver
}
func (m *Mysql) InitParams(db *gorm.DB) {
	db.Exec("SET @@sql_mode='NO_ENGINE_SUBSTITUTION';")
}

func (m *Mysql) GetDsn(conf *config.DBconf, withDB bool) string {
	database := ""
	if withDB {
		database = conf.Database
	}
	return fmt.Sprintf("%v:%v@tcp(%v:%v)/%v?charset=utf8&parseTime=True&loc=Local&timeout=1000ms", conf.Username, conf.Password, conf.Hostname, conf.Hostport, database)
}

func (m *Mysql) GetCreateDatabaseSql(databaseName string) string {
	return fmt.Sprintf("CREATE DATABASE IF NOT EXISTS %v DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci", databaseName)
}

func (m *Mysql) OpenGorm(conf *config.DBconf) *gorm.DB {
	db, err := gorm.Open(mysql.Open(m.GetDsn(conf, true)), &gorm.Config{})
	if err != nil {
		panic(err)
	}
	m.InitParams(db)
	return db
}

func (m *Mysql) Tables(tableNames ...string) []meta.Table {

	tableSql := ""
	if len(tableNames) > 0 {
		var arr []string
		for _, name := range tableNames {
			arr = append(arr, fmt.Sprintf("'%s'", name))
		}
		tableSql = fmt.Sprintf("AND table_name IN (%s)", strings.Join(arr, ","))
	}

	var tablesInfo []meta.Table

	sqlStr, _ := stringx.TemplateParse(`
SELECT
  table_name tableName,
  table_comment tableComment,
  table_rows tableRows,
  data_length dataLength,
  index_length indexLength,
  create_time createTime
FROM
  information_schema.tables
WHERE
  table_type = 'BASE TABLE'
    {{.tableSql}}
  AND table_schema = (
    SELECT database()
  )
ORDER BY table_name
`, map[string]string{"tableSql": tableSql})

	base.GormDb.Raw(sqlStr).Scan(&tablesInfo)
	return tablesInfo
}
func (m *Mysql) Columns(tableNames ...string) []meta.Column {
	if len(tableNames) == 0 {
		panic("需要传入表名")
	}
	var columnInfos []meta.Column
	base.GormDb.Raw(`
SELECT table_name     tableName,
       column_name    columnName,
       column_type    columnType,
       data_type      dataType,
       column_default columnDefault,
       column_comment columnComment,
       CASE
           WHEN column_key = 'PRI' THEN
               1
           ELSE 0
           END AS     isPrimaryKey,
       CASE
           WHEN extra LIKE '%%auto_increment%%' THEN
               1
           ELSE 0
           END AS     isIdentity,
	   CASE
	   WHEN is_nullable = 'YES' THEN 1
	   ELSE 0
	   END AS     nullable,
       CHARACTER_MAXIMUM_LENGTH charMaxLength,
       NUMERIC_SCALE  numScale,
       NUMERIC_PRECISION numPrecision
FROM information_schema.COLUMNS
WHERE table_schema = (SELECT DATABASE())
  AND table_name IN (?)
ORDER BY table_name,
         ordinal_position
`, tableNames).Scan(&columnInfos)
	return columnInfos
}
