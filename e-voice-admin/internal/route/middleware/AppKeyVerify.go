package middleware

import (
	"gofly/internal/config"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/pkg/ioc"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/gf"
	"math"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

var (
	X_AK   = "x-ak"
	X_TIME = "x-t"
	X_SIGN = "x-sign"
)

func AppKeyVerify(c *gin.Context, ak string) {

	// 判断时间戳是否在5分钟内
	t, res := checkTime(c)
	if !res {
		return
	}
	// 通过ak获取用户信息和sk
	svc := ioc.GetType[*core_service.BusinessAccount]()
	account := svc.GetByAk(c, ak)
	if account == nil || account.AppKeySecret == "" {
		abort(c, "账号不存在")
		return
	}

	// 通过ak sk 验证签名
	if !checkSign(c, ak, account.AppKeySecret, t) {
		return
	}

	// 保存用户接口调用次数

	// 设置用户信息
	user := &base.SysUser{
		Id:       account.Id,
		Name:     account.Name,
		Username: account.Username,
	}
	c.Set("user", user)
	c.Next()
}
func checkTime(c *gin.Context) (int64, bool) {
	t := anyx.ToInt64(c.GetHeader(X_TIME))
	if t == 0 || math.Abs(float64(time.Now().UnixMilli()-t)) > 5*6*1000 {
		abort(c, "时间戳不在服务器时间5分钟内,请检查系统时间")
		return t, false
	}
	return t, true
}

func checkSign(c *gin.Context, ak, sk string, t int64) bool {
	sign := c.GetHeader(X_SIGN)
	if sign == "" || sign != gf.Md5(ak+sk+strconv.FormatInt(t, 10)) {
		abort(c, "签名错误")
		return false
	}
	return true
}

func abort(c *gin.Context, msg string) {
	c.AbortWithStatusJSON(http.StatusOK, gin.H{
		config.Inst.App.ResCodeName: http.StatusForbidden,
		config.Inst.App.ResMsgName:  msg,
		config.Inst.App.ResDataName: nil,
	})
}
