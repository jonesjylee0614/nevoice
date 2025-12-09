package middleware

import (
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"
	"gofly/pkg/utils/redis"

	"github.com/gin-gonic/gin"
)

func LimitTokenVerify(c *gin.Context, xlToken string) {

	// 通过ak获取用户信息和sk
	svc := ioc.GetType[*core_service.BusinessAccount]()

	redisClient := ioc.GetType[*redis.Client]()
	id, err := redisClient.Get(c, biz.X_Ltoken+":"+xlToken).Int64()
	if err != nil || id <= 0 {
		abort(c, "临时token无效或已过期")
		return
	}

	account, _ := svc.GetById(c, id)
	if account == nil {
		abort(c, "账号不存在")
		return
	}
	// 设置用户信息
	user := &base.SysUser{
		Id:       account.Id,
		Name:     account.Name,
		Username: account.Username,
		AllPerm:  true, // 临时token给予所有权限，用于声纹录制
	}
	c.Set("user", user)
	c.Next()
}
