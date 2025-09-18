package user

import (
	"encoding/json"
	"gofly/internal/domain/core_service"
	"gofly/internal/domain/dto"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/internal/route/middleware"
	"gofly/pkg/captcha"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/cryptox"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/redis"
	"gofly/pkg/utils/results"
	"math/rand"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"gopkg.in/gomail.v2"
)

/**
*使用 Index 是省略路径中的index
*本路径为： /admin/user/login -省去了index
 */
func init() {
	gf.RegisterRoute(&Index{})
}

type Index struct {
	redis.BaseRedis
	AccountService            *core_service.BusinessAccount        `inject:""`
	LoginLogService           *core_service.LoginLog               `inject:""`
	CommonConfigService       *core_service.CommonConfig           `inject:""`
	CommonEmailService        *core_service.CommonEmail            `inject:""`
	CommonVerifyCodeService   *core_service.CommonVerifyCode       `inject:""`
	CommonLogininfoService    *core_service.CommonLogininfo        `inject:""`
	BusinessAuthRoleAccessSvc *core_service.BusinessAuthRoleAccess `inject:""`
	BusinessAuthRoleSvc       *core_service.BusinessAuthRole       `inject:""`
	BusinessAuthRuleSvc       *core_service.BusinessAuthRule       `inject:""`

	CaptchaService *captcha.Service `inject:""`
}

// Get_Captcha 获取验证码 /user/get_Captcha
func (s *Index) Get_Captcha(c *gin.Context) {
	f := gf.ReqQuery(c, &dto.CaptchaGet{})
	res := s.CaptchaService.Generate(c.Request.Context(), captcha.Type(f.Type))
	results.Success(c, "获取验证码", res, nil)
}

// Check_Captcha 验证码验证 /user/check_Captcha
func (s *Index) Check_Captcha(c *gin.Context) {
	results.Success(c, "获取验证码", "", nil)
}

// Login  登录 /user/login
func (s *Index) Login(c *gin.Context) {
	login := gf.ReqBody(c, &dto.Login{})

	decryptStr, err := cryptox.AesDecrypt(login.EncryptStr, []byte(login.Check.Secret))
	assert.ErrIsNilAppendErr(err, "加密信息错误: %s")

	err = json.Unmarshal([]byte(decryptStr), login)
	assert.ErrIsNilAppendErr(err, "json转换出错: %s")
	// 检查验证码正确性
	checkRes := s.CaptchaService.Check(c.Request.Context(), login.Check)
	assert.IsTrue(checkRes, "验证码校验失败")

	cond := base.NewCond()
	cond.Where(true, "username", login.UserName)
	cond.Or(true, "email", login.UserName)
	cond.Limit = 1

	account, err := s.AccountService.First(c, cond)
	assert.IsTrue(account != nil, "账号或密码不正确")
	assert.ErrIsNilAppendErr(err, "账号或密码不正确")

	pass := gf.Md5(login.UserPass + account.Salt)
	assert.IsTrue(pass == account.Password, "账号或密码不正确")

	user := &base.SysUser{
		Id:       account.Id,
		Name:     account.Name,
		Username: account.Username,
	}

	// 获取用户权限列表
	//获取用户权限菜单
	roleIds := s.BusinessAuthRoleAccessSvc.GetRoleAccessIdsByUId(c, account.Id)
	assert.IsTrue(len(roleIds) > 0, "您没有使用权限")
	ruleIds := s.BusinessAuthRoleSvc.GetRulesByIds(c, roleIds...)
	if len(ruleIds) > 0 {
		if collx.ArrayContains(ruleIds, "*") {
			user.AllPerm = true
		} else {
			perms, _ := s.BusinessAuthRuleSvc.ListPermsByRuleIds(c, ruleIds)
			user.ResetPerms(c, s.RedisClient, perms)
		}
	}

	//token
	token := middleware.GenerateToken(user)

	account.Loginstatus = true
	account.LastLoginIP = gf.GetIp(c)
	account.LastLoginTime = time.Now().UnixMilli()
	_, _ = s.AccountService.Update(c, account)

	_, _ = s.LoginLogService.Insert(c, &core.LoginLog{
		Type:    1,
		UID:     account.Id,
		OutIn:   "in",
		LoginIP: gf.GetIp(c),
	})
	results.Success(c, "登录成功返回token！", token, nil)
}

// Get_userinfo 获取用户 /user/get_userinfo
func (s *Index) Get_userinfo(c *gin.Context) {
	sysUser := s.AccountService.GetSysUser(c)
	user, err := s.AccountService.GetById(c, sysUser.Id)
	assert.ErrIsNilAppendErr(err, "获取用户失败！")

	//获取用户权限菜单
	roleIds := s.BusinessAuthRoleAccessSvc.GetRoleAccessIdsByUId(c, sysUser.Id)
	assert.IsTrue(len(roleIds) > 0, "您没有使用权限")

	menuIds := s.BusinessAuthRoleSvc.GetRulesByIds(c, roleIds...)
	roles := make([]int64, 0)
	perms := make([]string, 0)
	if !collx.ArrayContains(menuIds, "*") {
		// 通过角色信息查询权限列表
		rCond := base.NewCond()
		rCond.Where(true, "status", 0)
		rCond.Where(true, "type", 2)
		rCond.Order = "orderNo asc"
		roles = gf.RulesMerge(menuIds)
		rCond.Where(true, "id", roles)
		rules, err := s.BusinessAuthRuleSvc.List(c, rCond)
		assert.ErrIsNilAppendErr(err, "获取权限列表错误")

		for _, rule := range rules {
			perms = append(perms, rule.Permission)
		}
	} else {
		perms = []string{"*"}
	}

	results.Success(c, "获取用户信息", map[string]interface{}{
		"userId":       user.Id,
		"username":     user.Username,
		"name":         user.Name,
		"avatar":       user.Avatar,
		"introduction": user.Remark,
		"nickname":     user.Nickname,
		"city":         user.City,
		"company":      user.Company,
		"role":         "admin", //角色权限
		"perms":        perms,   //角色权限
	}, nil)

}

// Refreshtoken 刷新token /user/refreshtoken
func (s *Index) Refreshtoken(c *gin.Context) {
	token := c.Request.Header.Get("Authorization")
	newtoken := middleware.Refresh(token)
	results.Success(c, "刷新token", newtoken, nil)
}

// Logout 5退出登录 /user/logout
func (s *Index) Logout(c *gin.Context) {
	token := c.Request.Header.Get("Authorization")
	if token != "" {
		sysUser := s.AccountService.GetSysUser(c)
		middleware.Refresh(token)
		if sysUser != nil {
			user := &core.BusinessAccount{
				Loginstatus: false,
			}
			user.Id = sysUser.Id
			_, _ = s.AccountService.Update(c, user)
		}
	}
	results.Success(c, "退出登录", true, nil)
}

// Get_code 6获取验证码 /user/get_code
func (s *Index) Get_code(c *gin.Context) {

	email := c.DefaultQuery("email", "")
	assert.IsTrue(email != "", "请填写邮箱")

	cond := base.NewCond()
	cond.Where(true, "data_from", "common")
	list, err := s.CommonEmailService.List(c, cond)
	assert.IsTrue(err == nil && len(list) > 0, "请到admin后台“配置管理”配置邮箱")

	ec := list[0]

	code := gf.GenValidateCode(6)

	m := gomail.NewMessage()
	m.SetHeader("From", ec.SenderEmail)  //发送者腾讯邮箱账号
	m.SetHeader("To", email)             //接收者邮箱列表
	m.SetHeader("Subject", ec.MailTitle) //邮件标题
	m.SetBody("text/html", ec.MailBody)  //邮件内容,可以是html

	// //添加附件
	// zipPath := "./user/temp.zip"
	// m.Attach(zipPath)

	//发送邮件服务器、端口、发送者qq邮箱、qq邮箱授权码
	//服务器地址和端口是腾讯的
	serviceHost := "smtp.qq.com"
	if ec.ServiceHost != "" {
		serviceHost = ec.ServiceHost
	}
	servicePort := 587
	if ec.ServicePort != 0 {
		servicePort = int(ec.ServicePort)
	}
	d := gomail.NewDialer(serviceHost, servicePort, ec.SenderEmail, ec.AuthCode)
	err = d.DialAndSend(m)
	assert.ErrIsNilAppendErr(err, "发送邮件失败 %s")

	_, _ = s.CommonVerifyCodeService.Insert(c, &core.CommonVerifyCode{
		Code:    code,
		Keyname: email,
	})

	results.Success(c, "获取验证码", nil, nil)
}

// ResetPassword 7.重置密码 /user/resetPassword
func (s *Index) ResetPassword(c *gin.Context) {
	req := gf.ReqBody(c, &dto.ResetPwd{})
	assert.IsTrue(req.Code != "" && req.Password != "", "请提交验证码或密码！", nil)

	cond := base.NewCond()
	cond.Fields = "id"
	cond.Where(true, "email", req.Email)

	account, _ := s.AccountService.First(c, cond)
	assert.IsTrue(account != nil, "邮箱不存在！")

	cond = base.NewCond()
	cond.Where(true, "keyname", req.Email)
	cond.Order = "id desc"

	res2, _ := s.CommonVerifyCodeService.First(c, cond)
	assert.IsTrue(res2 != nil && res2.Code == req.Code, "验证码无效")

	rnd := rand.New(rand.NewSource(6))
	salt := strconv.Itoa(rnd.Int())

	account.Salt = salt
	account.Password = gf.Md5(req.Password + salt)
	res, err := s.AccountService.Update(c, account)
	assert.ErrIsNilAppendErr(err, "重置密码失败")

	results.Success(c, "重置密码成功", res, nil)
}

// Get_logininfo 获取登录页面信息 /user/get_logininfo
func (s *Index) Get_logininfo(c *gin.Context) {

	cond := base.NewCond()
	cond.Fields = "title,des,image"
	cond.Order = "weigh asc,id desc"
	cond.Where(true, "type", "business", "common")

	res, err := s.CommonLogininfoService.List(c, cond)

	results.ResObj(c, res, err)
}
func (s *Index) Perms() map[string][]gin.HandlerFunc {
	return nil
}
