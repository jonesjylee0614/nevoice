package datacenter

import (
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Configuration struct {
	BusinessAccountSvc *core_service.BusinessAccount `inject:""`
	CommonEmailSvc     *core_service.CommonEmail     `inject:""`
}

func init() {
	gf.RegisterRoute(&Configuration{})
}

// Get_email 获取邮箱 /datacenter/configuration/get_email
func (s *Configuration) Get_email(c *gin.Context) {
	cond := base.NewCond()
	res, err := s.CommonEmailSvc.First(c, cond)
	results.ResObj(c, res, err)
}

// SaveEmail 保存邮箱 /datacenter/configuration/saveEmail
func (s *Configuration) SaveEmail(c *gin.Context) {

	req := gf.ReqBody(c, &core.CommonEmail{})
	res, err := s.CommonEmailSvc.InsertOrUpdate(c, req)
	results.ResSave(c, res, err)
}
func (s *Configuration) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"config:base": {s.SaveEmail},
	}
}
