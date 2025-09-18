package results

import (
	"fmt"
	"gofly/internal/config"
	"gofly/internal/model/base"
	"gofly/pkg/logx"
	"gofly/pkg/utils/cryptox"
	"gofly/pkg/utils/idx"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// 请求成功的时候 使用该方法返回信息
func Success(ctx *gin.Context, msg string, data interface{}, exdata interface{}) {

	res := gin.H{
		config.Inst.App.ResCodeName: 0,
		config.Inst.App.ResMsgName:  msg,
		config.Inst.App.ResDataName: data,
		"success":                   true,
		"appName":                   config.Inst.App.Name,
		"time":                      time.Now().UnixMilli(),
	}

	if exdata != nil {
		res["exdata"] = exdata
	}

	//token := ctx.Request.Header.Get("Authorization")
	//var newtoken interface{}
	//if token != "" {
	//	tockenarr := middleware.Refresh(token)
	//	if tockenarr != nil {
	//		newtoken = tockenarr
	//	}
	//}
	//if newtoken != nil {
	//	res["token"] = newtoken
	//}
	ctx.JSON(http.StatusOK, res)
}

func SuccessPage(ctx *gin.Context, msg string, page base.IPage, data interface{}) {

	Success(ctx, msg, gin.H{
		"page":     page.Page,
		"pageSize": page.PageSize,
		"total":    page.Total,
		"items":    data,
	}, nil)
}

// 请求失败的时候, 使用该方法返回信息
func Failed(ctx *gin.Context, msg string, err error) {
	traceId := cryptox.Md5(idx.UuidStr())[:8]
	if err != nil {
		logx.Error(fmt.Sprintf("请求错误：traceId: %s, msg: %s", traceId, msg), err)
	} else {
		logx.Warnf(msg)
	}
	ctx.JSON(http.StatusOK, gin.H{
		config.Inst.App.ResCodeName: 1,
		config.Inst.App.ResMsgName:  msg,
		config.Inst.App.ResDataName: nil,
		"appName":                   config.Inst.App.Name,
		"success":                   false,
		"time":                      time.Now().UnixMilli(),
		"traceId":                   traceId,
	})
}

func ResSave(c *gin.Context, res int64, err error) {
	if err != nil {
		Failed(c, "编辑失败", err)
		return
	}
	msg := "编辑成功！"
	if res == 0 {
		msg = "暂无数据更新"
	}
	Success(c, msg, res, nil)
}

func ResDel(c *gin.Context, res int64, err error) {
	if err != nil {
		Failed(c, "删除失败", err)
	} else {
		Success(c, "删除成功！", res, nil)
	}
}

func ResPage(c *gin.Context, page base.IPage, list interface{}, err error) {
	if err != nil {
		Failed(c, err.Error(), err)
		return
	}
	SuccessPage(c, "获取全部列表", page, list)
}

func ResObj(c *gin.Context, res interface{}, err error) {
	if err != nil {
		Failed(c, "获取内容失败", err)
		return
	}
	Success(c, "获取内容成功！", res, nil)
}
