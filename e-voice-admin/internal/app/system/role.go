package system

import (
	"cmp"
	"fmt"
	"gofly/internal/domain/core_dto"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/dt"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"strings"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Role struct {
	BusinessAccountSvc        *core_service.BusinessAccount        `inject:""`
	BusinessAuthRoleAccessSvc *core_service.BusinessAuthRoleAccess `inject:""`
	svc                       *core_service.BusinessAuthRole       `inject:""`
	BusinessAuthRuleSvc       *core_service.BusinessAuthRule       `inject:""`
}

// 初始化生成路由
func init() {
	gf.RegisterRoute(&Role{})
}

// Get_list 获取数据列表-子树结构 /system/role/get_list
func (s *Role) Get_list(c *gin.Context) {
	name := c.DefaultQuery("name", "")
	status := c.DefaultQuery("status", "")
	user := s.BusinessAccountSvc.GetSysUser(c)

	roleId := s.BusinessAuthRoleAccessSvc.GetRoleAccessIdsByUId(c, user.Id)
	roleIds := gf.GetAllChildren("business_auth_role", roleId) //批量获取子节点id
	allRoleId := gf.MergeArr(roleId, roleIds)

	cond := base.NewCond()
	cond.Order = "weigh asc"
	cond.Where(true, `id`, allRoleId)
	cond.Where(name, "name like ?", "%"+name+"%")
	cond.Where(status, "status", status)

	list, err := s.svc.List(c, cond)
	roleList := gf.GetTreeArray(collx.ArrayToMap(list), 0, "")
	if roleList == nil {
		roleList = make([]dt.Map, 0)
	}
	results.ResObj(c, roleList, err)
}

// Get_parent 表单获取选择父级 /system/role/get_parent
func (s *Role) Get_parent(c *gin.Context) {
	user := s.BusinessAccountSvc.GetSysUser(c)
	roleId := s.BusinessAuthRoleAccessSvc.GetRoleAccessIdsByUId(c, user.Id)
	roleIds := gf.GetAllChildren("business_auth_role", roleId) //批量获取子节点id
	allRoleId := gf.MergeArr(roleId, roleIds)
	cond := base.NewCond()
	cond.Fields = "id,pid,name"
	cond.Order = "weigh asc"
	cond.Where(true, "id", allRoleId)
	list, err := s.svc.List(c, cond)
	menuList := gf.GetMenuChildrenArray(collx.ArrayToMap(list), 0, "pid")

	results.ResObj(c, menuList, err)
}

// Get_menuList 获取菜单 /system/role/get_menuList
func (s *Role) Get_menuList(c *gin.Context) {

	ruleCond := base.NewCond()
	ruleCond.Fields = "id,pid,title,locale"
	ruleCond.Order = "orderNo asc"
	ruleCond.Where(true, "status", 0)

	//账号信息
	user := s.BusinessAccountSvc.GetSysUser(c)
	roleIds := s.BusinessAuthRoleAccessSvc.GetRoleAccessIdsByUId(c, user.Id)
	menuIds := s.svc.GetRulesByIds(c, roleIds...)
	if !collx.ArrayContains(menuIds, "*") { //不是超级权限-过滤菜单权限
		ruleCond.Where(true, "id", gf.RulesMerge(menuIds))
	}
	menuList, err := s.BusinessAuthRuleSvc.List(c, ruleCond)
	assert.ErrIsNilAppendErr(err, "获取菜单错误 %s")

	var menu []*core_dto.BusinessAuthRuleMenu
	for _, val := range menuList {
		m := &core_dto.BusinessAuthRuleMenu{
			Id:    val.Id,
			Pid:   val.Pid,
			Title: cmp.Or(val.Title, val.Locale),
		}
		menu = append(menu, m)
	}
	menu = GetMenuChildrenArray2(menu, 0)
	results.Success(c, "获取菜单数据", menu, nil)
}

// Save 保存编辑 /system/role/save
func (s *Role) Save(c *gin.Context) {

	req := gf.ReqBody(c, &core_dto.BusinessAuthRoleSaveReq{})
	//当前用户
	user := s.BusinessAccountSvc.GetSysUser(c)
	req.UID = user.Id

	if len(req.Menu) > 0 && req.Rules != "*" {
		//获取子菜单包含的父级ID
		ruleIds := s.BusinessAuthRuleSvc.GetRulesID(c, req.Menu)
		var rulesStr []string
		for _, v := range ruleIds {
			str := fmt.Sprintf("%v", v) //转string
			rulesStr = append(rulesStr, str)
		}
		req.Rules = strings.Join(rulesStr, ",")
		req.BusinessAuthRole.Menu = gf.JSONMarshalToString(req.Menu)
	}
	res, err := s.svc.InsertOrUpdate(c, req.BusinessAuthRole)
	results.ResSave(c, res, err)
	s.svc.UpdateWeigh(c, req.Id)
}

// UpStatus 更新状态 /system/role/upStatus
func (s *Role) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	results.ResSave(c, res, err)
}

// Del 删除 /system/role/del
func (s *Role) Del(c *gin.Context) {
	//获取post传过来的data
	ids := gf.ReqBody(c, &base.Ids{})
	batch, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, batch, err)
}
func (s *Role) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"role:base":     {s.Get_list, s.Get_parent, s.Get_menuList},
		"role:edit":     {s.Save},
		"role:del":      {s.Del},
		"role:upStatus": {s.UpStatus},
	}
}
