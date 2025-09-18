package middleware

import (
	"gofly/internal/config"
	"net/http"

	"github.com/didip/tollbooth"
	"github.com/gin-gonic/gin"
)

func LimitHandler() gin.HandlerFunc {
	lmt := tollbooth.NewLimiter(100, nil)
	lmt.SetMessage("您访问过于频繁，系统安全检查认为恶意攻击。")
	return func(c *gin.Context) {
		httpError := tollbooth.LimitByRequest(lmt, c.Writer, c.Request)
		if httpError != nil {
			c.AbortWithStatusJSON(http.StatusOK, gin.H{
				config.Inst.App.ResCodeName: 1,
				config.Inst.App.ResMsgName:  "您的操作太频繁，请稍后再试！",
				config.Inst.App.ResDataName: nil,
			})
			c.Data(httpError.StatusCode, lmt.GetMessageContentType(), []byte(httpError.Message))
		} else {
			c.Next()
		}
	}
}
