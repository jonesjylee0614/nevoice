package main

import (
	"gofly/internal/config"
	"gofly/internal/model/dialect"

	_ "gitee.com/liuzongyang/libpq"
	"gorm.io/gen"
)

func main() {
	config.Inst.InitFlag()

	// 启用pgsql
	config.Sp.ConfigPath = "./resource/config-dev-lzy-home-mac-pgsql.yml"
	// 初始化配置
	config.Inst.InitConfig()

	dial := dialect.GetByDriverName(config.Inst.DBconf.Driver)
	db := dial.OpenGorm(&config.Inst.DBconf)

	db = db.Debug()
	// 初始化生成器

	cfg := gen.Config{
		OutPath:      "./internal/model/biz", // 指定输出路径
		OutFile:      ".go",
		Mode:         gen.WithDefaultQuery,
		ModelPkgPath: "biz",

		// 字段配置
		FieldWithIndexTag: true,  // 生成数据库索引标签
		FieldWithTypeTag:  false, // 不生成数据库字段类型标签，防止切换数据库类型时，字段类型不匹配
	}
	g := gen.NewGenerator(cfg)

	g.UseDB(db)

	// 从数据库生成所有表的模型
	g.GenerateModel("business_user")

	//models := g.GenerateAllTable()
	//for _, model := range models {
	//	// 创建模型文件
	//	logx.Infof("生成模型文件：%v", model)
	//}

	// 执行生成
	g.Execute()
}
