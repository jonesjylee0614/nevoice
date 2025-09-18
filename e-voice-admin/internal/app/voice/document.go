package voice

import (
	"gofly/internal/domain/dto"
	"gofly/internal/domain/service"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"strings"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Document struct {
	svc *service.VoiceDocument `inject:""`
}

func init() {
	gf.RegisterRoute(&Document{})
}

// Get_list 获取列表 /voice/document/get_list
func (s *Document) Get_list(c *gin.Context) {
	req := gf.ReqQuery(c, &dto.VoiceDocumentPageReq{})
	cond := base.NewCond()

	// 查询条件示例
	cond.Where(req.Title, "name like ?", "%"+req.Title+"%")

	if req.CreatedTime != "" {
		datetimeArr := strings.Split(req.CreatedTime, ",")
		cond.Where(req.CreatedTime, "create_time between ? and ?", datetimeArr[0]+" 00:00:00", datetimeArr[1]+" 23:59:59")
	}
	cond.Fields = "id,name"
	cond.Order = "id desc"

	list, err := s.svc.Page(c, &req.IPage, cond)
	results.ResPage(c, req.IPage, list, err)
}

// Save 保存 /voice/document/save
func (s *Document) Save(c *gin.Context) {
	entity := gf.ReqBody(c, &biz.VoiceDocument{})
	res, err := s.svc.InsertOrUpdate(c, entity)
	go s.svc.UpdateWeigh(c, entity.Id)
	results.ResSave(c, res, err)
}

// UpStatus 更新状态 /voice/document/upStatus
func (s *Document) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	results.ResSave(c, res, err)
}

// Del 删除 /voice/document/del
func (s *Document) Del(c *gin.Context) {
	ids := gf.ReqBody(c, &base.Ids{})
	res, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, res, err)
}

// Get_content 获取详情 /voice/document/get_content
func (s *Document) Get_content(c *gin.Context) {
	id := c.DefaultQuery("id", "")
	assert.Nil(id, "请传参数id")

	res, err := s.svc.GetById(c, id)
	results.ResObj(c, res, err)
}
func (s *Document) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"vd:base":     {s.Get_list},
		"vd:edit":     {s.Save, s.Get_content},
		"vd:del":      {s.Del},
		"vd:upStatus": {s.UpStatus},
	}
}
