package dashboard

import (
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Workplace struct {
	svc *core_service.BusinessHomeQuickop `inject:""`
}

// 初始化生成路由
func init() {
	gf.RegisterRoute(&Workplace{})
}

// Get_quick 1获取快捷操作 /dashboard/workplace/get_quick
func (s *Workplace) Get_quick(c *gin.Context) {

	cond := base.NewCond()
	cond.Fields = "id,uid,path_url,name,icon,type,is_common,weigh"
	cond.Order = "weigh asc,id asc"
	list, err := s.svc.List(c, cond)
	results.ResObj(c, list, err)
}

// SaveQuick 3保存快捷操作 /dashboard/workplace/save_quick
func (s *Workplace) SaveQuick(c *gin.Context) {
	entity := gf.ReqBody(c, &core.BusinessHomeQuickop{})
	res, err := s.svc.InsertOrUpdate(c, entity)
	results.ResSave(c, res, err)
}

// Del_quick 3删除快捷操作 /dashboard/workplace/del_quick
func (s *Workplace) Del_quick(c *gin.Context) {
	entity := gf.ReqBody(c, &core.BusinessHomeQuickop{})
	res, err := s.svc.Delete(c, entity)
	results.ResDel(c, res, err)
}

func (s *Workplace) Perms() map[string][]gin.HandlerFunc {
	return nil
}
