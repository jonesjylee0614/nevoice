package system

import (
	"fmt"
	"gofly/internal/domain/core_dto"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"time"

	"github.com/gin-gonic/gin"
)

func init() {
	gf.RegisterRoute(&Account{})
}

// 用于自动注册路由
type Account struct {
	svc                       *core_service.BusinessAccount        `inject:""`
	CommonConfigSvc           *core_service.CommonConfig           `inject:""`
	BusinessAuthDeptSvc       *core_service.BusinessAuthDept       `inject:""`
	BusinessAuthRoleSvc       *core_service.BusinessAuthRole       `inject:""`
	BusinessAuthRoleAccessSvc *core_service.BusinessAuthRoleAccess `inject:""`
	LoginLogSvc               *core_service.LoginLog               `inject:""`
}

// Get_list 获取成员列表 /system/account/get_list
func (s *Account) Get_list(c *gin.Context) {

	req := gf.ReqQuery(c, &core_dto.BusinessAccountPageReq{})

	cond := base.NewCond()
	cond.Fields = "id,status,name,username,nickname,avatar,tel,mobile,email,dept_id,remark,city,address,company,create_time,update_time,updater_name,updater_id"
	cond.Where(req.Cid, "dept_id", req.Cid)
	cond.Where(req.Name, "name like ? or username like ?", "%"+req.Name+"%", "%"+req.Name+"%")
	cond.Where(req.Cimobiled, "mobile", req.Cimobiled)
	cond.Order = "id asc"

	list, err := s.svc.Page(c, &req.IPage, cond)
	assert.ErrIsNilAppendErr(err, "获取数据失败")

	uids := collx.ArrayMap(list, func(val *core.BusinessAccount) int64 {
		return val.Id
	})
	roleAccessMap := s.BusinessAuthRoleAccessSvc.GetRoleAccessIdsByUIds(c, uids...)

	var resList []*core_dto.BusinessAccountPageItem

	for _, val := range list {
		item := &core_dto.BusinessAccountPageItem{BusinessAccount: val}
		resList = append(resList, item)

		roleIds := roleAccessMap[val.Id]
		roles := s.BusinessAuthRoleSvc.GetRolesByIds(c, roleIds...)
		rolename := collx.ArrayMap(roles, func(val *core.BusinessAuthRole) string {
			return val.Name
		})
		item.Rolename = rolename
		item.Roleid = roleIds

		dep, _ := s.BusinessAuthDeptSvc.GetById(c, val.DeptID)
		item.Depname = dep.Name
		//头像
		if val.Avatar == "" {
			val.Avatar = "/common/uploadfile/get_image?url=resource/staticfile/avatar.png"
		}
	}

	results.ResPage(c, req.IPage, resList, err)

}

// Save 保存、编辑 /system/account/save
func (s *Account) Save(c *gin.Context) {

	req := gf.ReqBody(c, &core_dto.BusinessAccountPageItem{})

	user := s.svc.GetSysUser(c)

	if req.Password != "" {
		salt := time.Now().UnixMilli()
		req.Password = gf.Md5(fmt.Sprintf("%v%v", req.Password, salt))
		req.Salt = fmt.Sprintf("%v", salt)
	}
	if req.Avatar == "" {
		req.Avatar = "resource/staticfile/avatar.png"
	}
	if req.Id == 0 {
		req.UID = user.Id
		_, err := s.svc.Insert(c, req.BusinessAccount)
		assert.ErrIsNilAppendErr(err, "添加失败")
		//添加角色-多个
		s.BusinessAuthRoleAccessSvc.AppRoleAccess(c, req.Roleid, req.BusinessAccount.Id)
		results.Success(c, "添加成功！", req.BusinessAccount.Id, nil)
	} else {

		res, err := s.svc.Update(c, req.BusinessAccount)

		assert.ErrIsNilAppendErr(err, "更新失败")
		//添加角色-多个
		if req.Roleid != nil {
			s.BusinessAuthRoleAccessSvc.AppRoleAccess(c, req.Roleid, req.Id)
		}
		results.Success(c, "更新成功！", res, nil)
	}
}

// UpStatus 更新状态 /system/account/upStatus
func (s *Account) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	results.ResSave(c, res, err)
}

// Del 删除 /system/account/del
func (s *Account) Del(c *gin.Context) {
	//获取post传过来的data
	ids := gf.ReqBody(c, &base.Ids{})
	batch, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, batch, err)
}

// Get_account 获取账号信息 /system/account/get_account
func (s *Account) Get_account(c *gin.Context) {
	user := s.svc.GetSysUser(c)
	res, err := s.svc.GetById(c, user.Id)
	results.ResObj(c, res, err)
}

// Get_role 表单-选择角色 /system/account/get_role
func (s *Account) Get_role(c *gin.Context) {

	user := s.svc.GetSysUser(c)
	roleIdAccess := s.BusinessAuthRoleAccessSvc.GetRoleAccessIdsByUId(c, user.Id)
	roleIds := gf.GetAllChildren("business_auth_role", roleIdAccess) //批量获取子节点id

	allRoleId := gf.MergeArr(roleIdAccess, roleIds)
	cond := base.NewCond()
	cond.Fields = "id,pid,name"
	cond.Order = "weigh asc"
	cond.Where(true, "status", 0)
	cond.Where(true, "id", allRoleId)

	list, err := s.BusinessAuthRoleSvc.List(c, cond)
	results.ResObj(c, list, err)
}

// Get_loginloglist 获取登录日志 /system/account/get_loginloglist
func (s *Account) Get_loginloglist(c *gin.Context) {

	req := gf.ReqBody(c, &core_dto.LoginLogPageReq{})
	cond := base.NewCond()
	cond.Where(true, "uid", req.Uid)
	cond.Where(true, "type", 2)
	cond.Order = "id desc"
	list, err := s.LoginLogSvc.Page(c, &req.IPage, cond)
	results.ResPage(c, req.IPage, list, err)
}

// Isaccountexist 判断账号是否存在 /system/account/isaccountexist
func (s *Account) Isaccountexist(c *gin.Context) {
	//获取post传过来的data
	var parameter map[string]interface{}
	gf.ReqBody(c, &parameter)

	cond := base.NewCond()
	cond.Fields = "id"
	cond.Where(parameter["id"], "id != ?", parameter["id"])
	cond.Where(true, "username", parameter["username"])
	cond.Limit = 1
	res, err := s.svc.List(c, cond)
	assert.ErrIsNilAppendErr(err, "验证失败")

	assert.IsTrue(len(res) == 0, "账号已存在")

	results.Success(c, "验证通过", 0, nil)
}

func (s *Account) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"account:base":     {s.Get_list, s.Get_loginloglist, s.Get_account, s.Get_role},
		"account:edit":     {s.Save, s.Isaccountexist},
		"account:upStatus": {s.UpStatus},
		"account:del":      {s.Del},
	}
}
