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
type Tabledata struct {
	BusinessAccountSvc *core_service.BusinessAccount       `inject:""`
	svc                *core_service.CommonDictionaryTable `inject:""`
}

func init() {
	gf.RegisterRoute(&Tabledata{})
}

// Get_list 获取列表 /datacenter/tabledata/get_list
func (s *Tabledata) Get_list(c *gin.Context) {
	list, err := s.svc.List(c, &base.Cond{
		Order: "weigh asc",
	})
	results.ResObj(c, list, err)
}

// Save 保存 /datacenter/tabledata/save
func (s *Tabledata) Save(c *gin.Context) {

	req := gf.ReqBody(c, &core.CommonDictionaryTable{})
	res, err := s.svc.InsertOrUpdate(c, req)
	s.svc.UpdateWeigh(c, req.Id)
	results.ResSave(c, res, err)
}

// Del 删除 /datacenter/tabledata/del
func (s *Tabledata) Del(c *gin.Context) {
	ids := gf.ReqBody(c, &base.Ids{})
	batch, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, batch, err)
}
func (s *Tabledata) Perms() map[string][]gin.HandlerFunc {
	return nil
}
