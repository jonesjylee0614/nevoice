package main

import (
	"gofly/internal/config"
	"gofly/internal/model/biz"
	"gofly/internal/model/dialect"
	"gofly/pkg/logx"

	_ "gitee.com/liuzongyang/libpq"
)

func main() {
	// 配置数据库连接
	config.Inst.InitFlag()
	// 启用pgsql
	config.Sp.ConfigPath = "./resource/config-dev-lzy-home.yml"
	// 初始化配置
	config.Inst.InitConfig()

	dial := dialect.GetByDriverName(config.Inst.DBconf.Driver)
	db := dial.OpenGorm(&config.Inst.DBconf)

	db = db.Debug()

	dst := []interface{}{
		// 添加了表，就在这里添加实例化的模型
		&biz.VoicePrint{},
	}

	err := db.AutoMigrate(dst...)
	if err != nil {
		logx.Error("自动迁移失败", err)
		return
	}

}
