package errorx

import (
	"fmt"
)

// 业务错误
type BizError struct {
	code int
	err  string
}

var (
	Success      = NewBizCode(200, "success")
	BizErr       = NewBizCode(400, "业务错误")
	ServerError  = NewBizCode(500, "未知错误，请查看日志")
	PermErr      = NewBizCode(403, "无权访问")
	AuthErr      = NewBizCode(403, "登录信息失效")
	SignErr      = NewBizCode(400, "签名错误")
	ValidErr     = NewBizCode(402, "参数校验错误")
	AuthExpired  = NewBizCode(4031, "登录信息失效") // 提示modal
	AuthNotValid = NewBizCode(4032, "登录信息失效") // 直接跳转登录
)

// 错误消息
func (e BizError) Error() string {
	return e.err
}

// 错误码
func (e BizError) Code() int {
	return e.code
}

func (e BizError) String() string {
	return fmt.Sprintf("errCode: %d, errMsg: %s", e.Code(), e.Error())
}

// 创建业务逻辑错误结构体，默认为业务逻辑错误
func NewBiz(msg string, formats ...any) *BizError {
	return &BizError{code: BizErr.code, err: fmt.Sprintf(msg, formats...)}
}

// 创建业务逻辑错误结构体，可设置指定错误code
func NewBizCode(code int, msg string, formats ...any) *BizError {
	return &BizError{code: code, err: fmt.Sprintf(msg, formats...)}
}
func NewBizCodeWithErr(code int, err error, msg string) *BizError {
	return &BizError{code: code, err: fmt.Sprintf("%s %s", err.Error(), msg)}
}

func WrapBizErr(bizErr *BizError, err error, msg string) *BizError {
	bizErr.err += fmt.Sprintf("%s %s", err.Error(), msg)
	return bizErr
}
