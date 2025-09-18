package middleware

import (
	"gofly/pkg/logx"
	"gofly/pkg/utils/errorx"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {

		defer func() {
			if err := recover(); err != nil {
				// FIXME 可以判断错误类型，自定义错误信息

				switch t := err.(type) {
				case *errorx.BizError:
					logx.Warnf("业务错误: %v", err)
					resErr(c, t.Error(), "")
				case error:
					logx.Errorf("接口调用错误: %v", err)
					resErr(c, t.Error(), "")
				default:
					logx.Errorf("服务器内部错误: %v", err)
					resErr(c, "服务器内部错误", err)
				}
			}
		}()

		c.Next() // 调用c.Next()执行后面的中间件

	}
}

func resErr(c *gin.Context, msg string, err any) {
	c.AbortWithStatusJSON(http.StatusOK, gin.H{
		"code":    1,
		"message": msg,
		"data":    err,
		"time":    time.Now().UnixMilli(),
	})
}
