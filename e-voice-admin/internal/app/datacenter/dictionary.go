package datacenter

import (
	"gofly/internal/domain/core_dto"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Dictionary struct {
	svc *core_service.CommonDictionaryData `inject:""`
}

func init() {
	gf.RegisterRoute(&Dictionary{})
}

// Get_list 获取列表 /datacenter/dictionary/get_list
func (s *Dictionary) Get_list(c *gin.Context) {

	req := gf.ReqQuery(c, &core_dto.DictPageReq{})

	cond := base.NewCond()
	cond.Where(req.Title, "keyname like ?", "%"+req.Title+"%")
	cond.Where(true, "dic_id", req.DicId)
	cond.Order = "weigh asc"
	list, err := s.svc.Page(c, &req.IPage, cond)
	results.ResPage(c, req.IPage, list, err)

}

// Save 保存 /datacenter/dictionary/save
func (s *Dictionary) Save(c *gin.Context) {
	entity := gf.ReqBody(c, &core.CommonDictionaryData{})
	res, err := s.svc.InsertOrUpdate(c, entity)
	go s.svc.UpdateWeigh(c, entity.Id)
	results.ResSave(c, res, err)
}

// UpStatus 更新状态 /datacenter/dictionary/upStatus
func (s *Dictionary) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	results.ResSave(c, res, err)
}

// Del 删除 /datacenter/dictionary/del
func (s *Dictionary) Del(c *gin.Context) {
	ids := gf.ReqBody(c, &base.Ids{})
	res, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, res, err)
}
func (s *Dictionary) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"dict:base":     {s.Get_list},
		"dict:edit":     {s.Save},
		"dict:del":      {s.Del},
		"dict:upStatus": {s.UpStatus},
	}
}
