package user

import (
	"gofly/internal/domain/core_service"
	"gofly/internal/model/core"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Data struct {
	BusinessAccountSvc *core_service.BusinessAccount `inject:""`
}

// 初始化生成路由
func init() {
	gf.RegisterRoute(&Data{})
}

// Get_user 获取账号信息 /user/data/get_user
func (s *Data) Get_user(c *gin.Context) {
	user := s.BusinessAccountSvc.GetSysUser(c)
	res, err := s.BusinessAccountSvc.GetById(c, user.Id)
	res.Salt = ""
	res.Password = "" // 隐藏密码信息
	results.ResObj(c, res, err)
}

// SaveInfo 更新账号信息 /user/data/saveInfo
func (s *Data) SaveInfo(c *gin.Context) {
	//获取post传过来的data
	req := gf.ReqBody(c, &core.BusinessAccount{})
	user := s.BusinessAccountSvc.GetSysUser(c)

	req.Id = user.Id

	res, err := s.BusinessAccountSvc.Update(c, req)
	results.ResSave(c, res, err)
}

// CheckPassword 校验密码 /user/data/checkPassword
func (s *Data) CheckPassword(c *gin.Context) {
	//获取post传过来的data
	var parameter map[string]interface{}
	gf.ReqBody(c, &parameter)

	user := s.BusinessAccountSvc.GetSysUser(c)

	data, err := s.BusinessAccountSvc.GetById(c, user.Id)
	assert.ErrIsNilAppendErr(err, "查询数据失败")
	assert.Nil(data, "账号不存在")

	pass := gf.Md5(parameter["password"].(string) + data.Salt)
	assert.IsTrue(pass == data.Password, "密码错误")

	results.Success(c, "密码验证成功", true, nil)

}

// ChangePassword 更新密码 /user/data/changePassword
func (s *Data) ChangePassword(c *gin.Context) {
	//获取post传过来的data
	var parameter map[string]interface{}
	gf.ReqBody(c, &parameter)

	user := s.BusinessAccountSvc.GetSysUser(c)

	data, err := s.BusinessAccountSvc.GetById(c, user.Id)
	assert.ErrIsNilAppendErr(err, "查询数据失败")
	assert.Nil(data, "账号不存在")

	pass := gf.Md5(parameter["oldpassword"].(string) + data.Salt)
	assert.IsTrue(data.Password == pass, "原密码错误")

	newpass := gf.Md5(parameter["password"].(string) + data.Salt)
	entity := &core.BusinessAccount{}
	entity.Id = user.Id
	entity.Password = newpass
	res, err := s.BusinessAccountSvc.Update(c, entity)
	results.ResSave(c, res, err)

}
func (s *Data) Perms() map[string][]gin.HandlerFunc {
	return nil
}
