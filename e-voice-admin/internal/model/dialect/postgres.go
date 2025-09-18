package dialect

import (
	"fmt"
	"gofly/internal/config"
	"gofly/internal/model/base"
	"gofly/internal/model/dialect/gorm_postgres"
	"gofly/internal/model/dialect/meta"
	"gofly/pkg/utils/stringx"
	"strings"

	"gorm.io/gorm"
)

type Postgres struct {
	DefaultDb string // 当尝试连接数据库并不指定数据库时，默认连接的数据库
}

var _ Dialect = (*Postgres)(nil)
var PostgresInst = &Postgres{
	DefaultDb: "postgres",
}

func (m *Postgres) GetDriver() string {
	return "postgres"
}
func (m *Postgres) InitParams(db *gorm.DB) {
	db.Exec("SET GLOBAL sql_mode='NO_ENGINE_SUBSTITUTION';")
}
func (m *Postgres) GetDsn(conf *config.DBconf, withDB bool) string {
	dbParam := ""
	if conf.Database == "" {
		conf.Database = m.DefaultDb
	}

	// pg系列可以通过  database/schema 定位到具体的schema
	ss := strings.Split(conf.Database, "/")
	if len(ss) > 1 {
		dbParam = fmt.Sprintf("dbname=%s search_path=%s", ss[0], ss[len(ss)-1])
	} else {
		dbParam = "dbname=" + conf.Database
	}

	return fmt.Sprintf("host=%s port=%s user=%s password=%s %s sslmode=disable connect_timeout=8", conf.Hostname, conf.Hostport, conf.Username, conf.Password, dbParam)

}

func (m *Postgres) GetCreateDatabaseSql(databaseName string) string {
	return fmt.Sprintf("create schema %s", databaseName)
}

func (m *Postgres) OpenGorm(conf *config.DBconf) *gorm.DB {
	db, err := gorm.Open(postgres.Open(m.GetDsn(conf, true)), &gorm.Config{})
	if err != nil {
		panic(err)
	}
	m.InitParams(db)
	return db
}

func (m *Postgres) Tables(tableNames ...string) []meta.Table {

	tableSql := ""
	if len(tableNames) > 0 {

		tableSql = fmt.Sprintf("and c.relname in (%s)", strings.Join(tableNames, ","))
	}

	var tablesInfo []meta.Table

	sqlstr, _ := stringx.TemplateParse(`
select
	c.relname as "tableName",
	obj_description (c.oid) as "tableComment",
	pg_table_size ('"' || n.nspname || '"."' || c.relname || '"') as "dataLength",
	pg_indexes_size ('"' || n.nspname || '"."' || c.relname || '"') as "indexLength",
	psut.n_live_tup as "tableRows"
from
	pg_class c
join pg_namespace n on
	c.relnamespace = n.oid
join pg_stat_user_tables psut on
	psut.relid = c.oid
where
    has_table_privilege(CAST(c.oid AS regclass), 'SELECT')
	and n.nspname = current_schema()
	and c.reltype > 0
   {{ .tableSql }}
order by c.relname
`, map[string]string{"tableSql": tableSql})

	base.GormDb.Raw(sqlstr).Scan(&tablesInfo)
	return tablesInfo
}
func (m *Postgres) Columns(tableNames ...string) []meta.Column {
	if len(tableNames) == 0 {
		panic("需要传入表名")
	}

	var columnInfos []meta.Column
	base.GormDb.Raw(`
SELECT a.table_name                                                                            AS "tableName",
       a.column_name                                                                           AS "columnName",
       case when a.is_nullable = 'YES' then 1 else 0 end                                       AS "nullable",
       a.udt_name                                                                              AS "dataType",
       a.character_maximum_length                                                              AS "charMaxLength",
       a.numeric_precision                                                                     AS "numPrecision",
       case when a.column_default like 'nextval%%' then null else a.column_default end         AS "columnDefault",
       a.numeric_scale                                                                         AS "numScale",
       case when a.column_default like 'nextval%%' then 1 else 0 end                           AS "isIdentity",
       case when b.column_name is not null then 1 else 0 end                                   AS "isPrimaryKey",
       col_description((a.table_schema || '.' || a.table_name) ::regclass, a.ordinal_position) AS "columnComment"
FROM information_schema.columns a
         left join information_schema.key_column_usage b
                   on a.table_schema = b.table_schema and b.table_name = a.table_name and b.column_name = a.column_name
WHERE a.table_schema = (select current_schema())
  and a.table_name in (?)
order by a.table_name, a.ordinal_position
`, tableNames).Scan(&columnInfos)
	return columnInfos
}
