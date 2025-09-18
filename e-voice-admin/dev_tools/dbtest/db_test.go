package dbtest

import (
	"encoding/json"
	"gofly/internal/config"
	"gofly/internal/domain/service"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/internal/model/dialect"
	json2 "gofly/pkg/json"
	"gofly/pkg/logx"
	"net/http"
	"testing"

	"github.com/gin-gonic/gin"

	_ "gitee.com/liuzongyang/libpq"
)

func TestOrmDb(t *testing.T) {
	// 配置数据库连接
	config.Inst.InitFlag()
	//pgsql
	//config.Sp.ConfigPath = "../../resource/config-tany-pgsql.yml"

	// mysql
	config.Sp.ConfigPath = "../../resource/config.yml"

	// 初始化配置
	config.Inst.InitConfig()
	dial := dialect.GetByDriverName(config.Inst.DBconf.Driver)
	db := dial.OpenGorm(&config.Inst.DBconf)

	db = db.Debug()

	base.GormDb = db

	acc := service.VoicePrint{}

	err := db.AutoMigrate(biz.VoicePrint{})
	if err != nil {
		t.Error(err)
		return
	}

	// 新增
	v := &biz.VoicePrint{
		UserId:   1,
		UserName: "admin",
		PrintId:  1,
	}

	ctx := &gin.Context{
		Request: &http.Request{},
	}
	ctx.Set("user", &base.SysUser{
		Id:       1,
		Username: "admin",
		Name:     "admin",
	})
	res, err := acc.Insert(ctx, v)
	logx.Printf("新增成功 id: %v", v.Id)

	// 批量新增
	list := []*biz.VoicePrint{
		{
			UserId:   2,
			UserName: "admin2",
			PrintId:  2,
		},
		{
			UserId:   3,
			UserName: "admin3",
			PrintId:  3,
		},
	}
	res, err = acc.InsertBatch(ctx, list)
	if err != nil {
		t.Error(err)
		return
	}
	t.Logf("批量新增成功 %d 条", res)

	// 批量删除
	ids := &base.Ids{
		Ids: []*json2.JsonInt64{
			json2.NewJsonInt64(list[0].Id),
			json2.NewJsonInt64(list[1].Id),
		},
	}
	res, err = acc.DeleteBatch(ctx, ids)
	t.Logf("批量删除成功 %d 条", res)

	// 查询单条
	v, err = acc.GetById(ctx, v.Id)
	marshal, _ := json.Marshal(v)
	t.Logf("查询单条 %s", string(marshal))

	// 修改
	v.UserName = "admin1"
	res, err = acc.Update(ctx, v)
	t.Logf("修改成功 %d 条 id: %v newName: %s", res, v.Id, v.UserName)

	// 删除
	res, err = acc.Delete(ctx, v)
	t.Logf("删除成功 %d 条 id: %v", res, v.Id)

	// 查询列表
	list, err = acc.List(ctx, base.NewCond())
	if err != nil {
		return
	}
	t.Logf("查询列表成功 %d 条", len(list))
	page := base.NewPage(1, 10)

	// 自定义sql查询
	var list2 []biz.VoicePrint
	err = acc.Select("select * from voice_print where id between ? and ?", &list2, 1, 100)
	t.Logf("自定义sql查询成功 %d 条", len(list2))

	// 分页
	cond := base.NewCond()
	cond.Where(true, "id > ? and id < ?", 1, 100)
	cond.Fields = "id,user_id,user_name"
	cond.Order = "id desc"

	list, err = acc.Page(ctx, page, cond)
	if err != nil {
		return
	}
	t.Logf("分页查询成功 %d 条，总 %d 条", len(list), page.Total)

}
