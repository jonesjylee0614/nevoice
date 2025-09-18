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
type Common_config struct {
	BusinessAccountSvc *core_service.BusinessAccount `inject:""`
	CommonConfigSvc    *core_service.CommonConfig    `inject:""`
}

func init() {
	gf.RegisterRoute(&Common_config{})
}

// Get_config 获取配置 /datacenter/common_config/get_config
func (s *Common_config) Get_config(c *gin.Context) {
	keyname := c.DefaultQuery("keyname", "")
	cond := base.NewCond()
	cond.Where(true, "keyname", keyname)
	data, err := s.CommonConfigSvc.First(c, cond)
	results.ResObj(c, data, err)
}

// SaveConfig 保存邮箱 /datacenter/common_config/saveConfig
func (s *Common_config) SaveConfig(c *gin.Context) {

	req := gf.ReqBody(c, &core.CommonConfig{})

	cond := base.NewCond()
	cond.Where(true, "keyname", req.Keyname)
	cond.Fields = "id"
	res, err := s.CommonConfigSvc.InsertOrUpdate(c, req)
	results.ResSave(c, res, err)
}
func (s *Common_config) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"config:base": {s.Get_config, s.SaveConfig},
	}
}
