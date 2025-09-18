package middleware

import (
	"gofly/internal/config"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/gf"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// 验证接口合法性
func ValidityApi() gin.HandlerFunc {
	return func(c *gin.Context) {
		//加载配置
		app := config.Inst.App
		// 验证-根目录
		var NoVerifyApiRootArr []string
		if app.NoVerifyAPIRoot != "" {
			NoVerifyApiRootArr = strings.Split(app.NoVerifyAPIRoot, `,`)
		} else {
			NoVerifyApiRootArr = make([]string, 0)
		}
		// 验证-具体路径
		var NoVerifyAPIArr []string
		if app.NoVerifyAPI != "" {
			NoVerifyAPIArr = strings.Split(app.NoVerifyAPI, `,`)
		} else {
			NoVerifyAPIArr = make([]string, 0)
		}
		rootPath := strings.Split(c.Request.URL.Path, "/")
		if (len(rootPath) > 2 &&
			collx.ArrayAnyContains(NoVerifyApiRootArr, rootPath[1])) ||
			collx.ArrayAnyContains(NoVerifyAPIArr, c.Request.URL.Path) ||
			strings.Contains(c.Request.URL.Path, "/common/uploadfile/get_image") { //过滤附件访问接口
			//不需验证
			c.Next()
		} else {
			//需要验证
			// 1、判断MD5和时间差,开发环境不校验
			if !app.IsDev() {
				var apiSecret = app.Apisecret
				encrypt := c.Request.Header.Get("verify-encrypt")
				verifyTime := c.Request.Header.Get("verify-time")
				md5secret := gf.Md5(apiSecret + verifyTime)
				verifyTimeInt, _ := strconv.ParseInt(verifyTime, 10, 64)
				if md5secret != encrypt || (time.Now().UnixMilli()-verifyTimeInt*1000 > 60*15*1000) { //15分钟
					c.AbortWithStatusJSON(http.StatusOK, gin.H{
						app.ResCodeName: 1,
						app.ResMsgName:  "您的请求不合法，请按规范请求数据!",
						app.ResDataName: nil,
					})
					return
				}
			}
			// 放行
			c.Next()
		}

	}
}
