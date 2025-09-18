package dto

import (
	"gofly/pkg/captcha"
)

type CaptchaGet struct {
	Type string `json:"type" form:"type" binding:"required" comment:"验证码类型 ClickBasic 或 SlideBasic"`
}
type Login struct {
	*captcha.Check
	UserName string `json:"username" form:"username" comment:"用户名"`
	UserPass string `json:"password" form:"password" comment:"密码"`

	EncryptStr string `json:"encryptStr" form:"encryptStr" binding:"required" comment:"加密串"`
}

type ResetPwd struct {
	Email    string `json:"email" form:"email" binding:"required"`
	Password string `json:"password" form:"password" binding:"required"`
	Code     string `json:"code" form:"code" binding:"required"`
}
