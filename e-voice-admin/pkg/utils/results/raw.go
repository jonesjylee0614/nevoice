package results

import (
	"github.com/gin-gonic/gin"
)

// ResRaw 返回原始数据
func ResRaw(c *gin.Context, data []byte, err error) {
	if err != nil {
		Failed(c, "请求失败", err)
		return
	}
	c.Data(200, "application/json", data)
}

// ResError 返回错误信息
func ResError(c *gin.Context, err error) {
	Failed(c, "请求错误", err)
}