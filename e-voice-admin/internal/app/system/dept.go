package system

import (
	"gofly/internal/domain/core_dto"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/dt"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Dept struct {
	BusinessAccountSvc *core_service.BusinessAccount  `inject:""`
	svc                *core_service.BusinessAuthDept `inject:""`
}

func init() {
	gf.RegisterRoute(&Dept{})
}

// Get_list 获取部门列表 /system/dept/get_list
func (s *Dept) Get_list(c *gin.Context) {
	req := gf.ReqQuery(c, &core_dto.DeptPageReq{})
	cond := base.NewCond()
	cond.Order = "weigh asc"
	cond.Where(req.Name, "name like ?", "%"+req.Name+"%")
	cond.Where(req.Status, "status", req.Status)

	list, err := s.svc.List(c, cond)
	depList := gf.GetTreeArray(collx.ArrayToMap(list), 0, "")
	if depList == nil {
		depList = make([]dt.Map, 0)
	}
	results.ResObj(c, depList, err)
}

// Get_parent 获取部门列表-表单 /system/dept/get_parent
func (s *Dept) Get_parent(c *gin.Context) {
	cond := base.NewCond()
	cond.Fields = "id,pid,name"
	cond.Order = "weigh asc"

	list, err := s.svc.List(c, cond)

	depList := gf.GetMenuChildrenArray(collx.ArrayToMap(list), 0, "pid")
	if depList == nil {
		depList = make([]dt.Map, 0)
	}
	results.ResObj(c, depList, err)
}

// Save 保存 /system/dept/save
func (s *Dept) Save(c *gin.Context) {
	//获取post传过来的data
	req := gf.ReqBody(c, &core.BusinessAuthDept{})
	//当前用户
	user := s.BusinessAccountSvc.GetSysUser(c)
	req.UID = user.Id

	res, err := s.svc.InsertOrUpdate(c, req)
	results.ResSave(c, res, err)
	s.svc.UpdateWeigh(c, req.Id)
}

// UpStatus 更新状态 /system/dept/upStatus
func (s *Dept) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	results.ResSave(c, res, err)
}

// Upgrouppid 更新父级-拖拽更新父id /system/dept/upgrouppid
func (s *Dept) Upgrouppid(c *gin.Context) {
	//获取post传过来的data

	req := gf.ReqBody(c, &core_dto.UpDeptGroupPidReq{})

	tx := base.GormDb.Table(s.svc.GetModel().TableName()).
		Where("id in (?)", req.Ids).
		Update("pid", req.Pid)

	results.ResSave(c, tx.RowsAffected, tx.Error)

}

// Del 删除 /system/role/del
func (s *Dept) Del(c *gin.Context) {
	//获取post传过来的data
	ids := gf.ReqBody(c, &base.Ids{})
	batch, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, batch, err)
}
func (s *Dept) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"dept:base":     {s.Get_list},
		"dept:edit":     {s.Save, s.Upgrouppid, s.Get_parent},
		"dept:del":      {s.Del},
		"dept:upStatus": {s.UpStatus},
	}
}
