package user

import (
	"gofly/internal/domain/core_dto"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/core"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/redis"
	"gofly/pkg/utils/results"

	"github.com/gin-gonic/gin"
)

func init() {
	gf.RegisterRoute(&Account{})
}

// 用于自动注册路由
type Account struct {
	redis.BaseRedis
	svc                       *core_service.BusinessAccount        `inject:""`
	BusinessAuthRoleAccessSvc *core_service.BusinessAuthRoleAccess `inject:""`
	BusinessAuthRoleSvc       *core_service.BusinessAuthRole       `inject:""`
	BusinessAuthRuleSvc       *core_service.BusinessAuthRule       `inject:""`
}

// Get_userdata 获取用户数据 /user/account/get_userdata
func (s *Account) Get_userdata(c *gin.Context) {
	user := s.svc.GetSysUser(c)
	data, err := s.svc.GetById(c, user.Id)
	results.ResObj(c, data, err)
}

// Get_menu 系统设置-获取菜单  /user/account/get_menu
func (s *Account) Get_menu(c *gin.Context) {
	user := s.svc.GetSysUser(c)
	//获取用户权限菜单
	roleIds := s.BusinessAuthRoleAccessSvc.GetRoleAccessIdsByUId(c, user.Id)
	assert.IsTrue(len(roleIds) > 0, "您没有使用权限")

	menuIds := s.BusinessAuthRoleSvc.GetRulesByIds(c, roleIds...)

	menus, perms, _ := s.BusinessAuthRuleSvc.ListByMenuIds(c, menuIds)

	pm := collx.ArrayMap(perms, func(perm *core.BusinessAuthRule) string {
		return perm.Permission
	})

	user.ResetPerms(c, s.RedisClient, pm)

	ruleMenu := GetMenuArray(c, s.BusinessAuthRuleSvc, menus, 0)
	results.Success(c, " 获取菜单", ruleMenu, nil)
}

// Upuserinfo 保存数据 /user/account/upuserinfo
func (s *Account) Upuserinfo(c *gin.Context) {
	req := gf.ReqBody(c, &core.BusinessAccount{})
	user := s.svc.GetSysUser(c)
	req.Id = user.Id // 需要标记一下当前用户id，否则会越权
	res, err := s.svc.Update(c, req)
	results.ResSave(c, res, err)
}

// Upavatar 更新头像 /user/account/upavatar
func (s *Account) Upavatar(c *gin.Context) {

	var parameter map[string]interface{}
	gf.ReqBody(c, &parameter)

	entity := &core.BusinessAccount{
		Avatar: anyx.ToString(parameter["url"]),
	}
	entity.Id = s.svc.GetSysUser(c).Id
	res, err := s.svc.Update(c, entity)
	results.ResSave(c, res, err)
}

// Changepwd 修改密码 /user/account/changepwd
func (s *Account) Changepwd(c *gin.Context) {

	req := gf.ReqBody(c, &core_dto.BusinessAccountUpPwdReq{})
	user := s.svc.GetSysUser(c)

	userdata, err := s.svc.GetById(c, user.Id)
	assert.ErrIsNilAppendErr(err, "查找账号失败！")

	pass := gf.Md5(req.PasswordOld + userdata.Salt)
	assert.IsTrue(pass == userdata.Password, "原密码错误！")

	newpass := gf.Md5(req.PasswordNew + userdata.Salt)
	entity := &core.BusinessAccount{}
	entity.Id = user.Id
	entity.Password = newpass
	res, err := s.svc.Update(c, entity)

	results.ResSave(c, res, err)
}
func (s *Account) Perms() map[string][]gin.HandlerFunc {
	return nil
}
