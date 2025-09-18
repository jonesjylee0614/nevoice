package middleware

import (
	"cmp"
	"net/http"

	"github.com/gin-gonic/gin"
)

func Cors(origin string) gin.HandlerFunc {
	return func(c *gin.Context) {
		method := c.Request.Method

		c.Header("Access-Control-Allow-Origin", cmp.Or(origin, c.GetHeader("Origin")))
		c.Header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE, UPDATE")
		c.Header("Access-Control-Allow-Headers", "*")
		c.Header("Access-Control-Expose-Headers", "Content-Length, Access-Control-Allow-Origin, Access-Control-Allow-Headers, Cache-Control, Content-Language, Content-Type, x-requested-with, authorization, Content-Type, Authorization, credential, X-XSRF-TOKEN, token, sign, t, cqliving_server_token, cqliving_cms_token, appId, cqlivingAppClientType, cqlivingAppClientVersion")
		c.Header("Access-Control-Allow-Credentials", "true")

		//放行所有OPTIONS方法
		if method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
		}
		// 处理请求
		c.Next()
	}
}
