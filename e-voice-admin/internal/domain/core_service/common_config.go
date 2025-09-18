package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"

	"github.com/gin-gonic/gin"
)

type CommonConfig struct {
	base.DaoImpl[*core.CommonConfig]
}

func init() {
	ioc.PrepareDao(new(CommonConfig))
}

func (s *CommonConfig) GetRootUrl(c *gin.Context) string {

	cond := base.NewCond()
	cond.Fields = "keyvalue"
	cond.Where(true, "keyname", "rooturl")
	res, err := s.First(c, cond)
	if res == nil || err != nil {
		return ""
	}
	return res.Keyvalue
}
