package model

import (
	"fmt"
	"gofly/internal/config"
	"gofly/internal/model/base"
	"gofly/internal/model/dialect"
	"gofly/pkg/logx"
	"gofly/pkg/utils/anyx"

	_ "gitee.com/liuzongyang/libpq" // pg系列，支持高斯
	_ "github.com/go-sql-driver/mysql"
	"gorm.io/gorm/logger"
)

var initModels []interface{}

func AddInitModel(md interface{}) {
	initModels = append(initModels, md)
}

func init() {
	config.AddAfterConfigFn(InitDb)
}

// 取得数据库连接实例
func InitDb(cfg *config.Config) {
	dial := dialect.GetByDriverName(cfg.DBconf.Driver)
	// 初始化gorm
	InitGorm(dial)
}

func InitGorm(dial dialect.Dialect) {
	db := dial.OpenGorm(&config.Inst.DBconf)

	err := db.AutoMigrate(initModels...)
	if err != nil {
		logx.Error("同步数据库模型异常：", err)
		return
	}

	lv := logger.Error
	if config.Inst.Log.EnableSqlLog {
		lv = logger.Info
	}
	db.Logger = &Logger{
		LogLevel: lv,
	}

	base.GormDb = db
}

// 新建数据库
func CreateDataBase(driver, Username, Password, Hostname, Hostport, Database interface{}) {
	config.Inst.InitConfig()
	driver1 := anyx.ToString(driver)
	dial := dialect.GetByDriverName(driver1)
	gormDb := dial.OpenGorm(&config.DBconf{
		Driver:   driver1,
		Username: anyx.ToString(Username),
		Password: anyx.ToString(Password),
		Hostname: anyx.ToString(Hostname),
		Hostport: anyx.ToString(Hostport),
		Database: anyx.ToString(Database),
	})

	gormDb.Exec(dial.GetCreateDatabaseSql(fmt.Sprintf("%s", Database)))
}

// 导入数据库文件
func ExecSql(rows string) (int64, error) {
	tx := base.GormDb.Exec(rows)
	if tx.Error != nil {
		logx.Infof(fmt.Sprintf("导入数据失败:%v.", tx.Error))
	}
	return tx.RowsAffected, tx.Error
}
