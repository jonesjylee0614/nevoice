package validatorx

import (
	"fmt"
	"gofly/pkg/logx"
	"gofly/pkg/utils/errorx"
	"regexp"

	"github.com/go-playground/validator/v10"
)

const CustomPatternTagName = "pattern"

var (
	RegexpMap = make(map[string]*Validation)

	pwdReg1 = regexp.MustCompile(`^[a-zA-Z]`)
	pwdReg2 = regexp.MustCompile(`^[0-9]+$`)
	pwdReg3 = regexp.MustCompile(`^[^0-9]+$`)
	pwdReg4 = regexp.MustCompile(`^[a-zA-Z0-9]+$`)
)

type ValidateFn func(f validator.FieldLevel) bool

type Validation struct {
	Name string         // 正则名
	Reg  *regexp.Regexp // 正则实例
	Msg  string         // 当校验不通过时的报错信息
	Fn   ValidateFn     // 校验函数，优先级比正则字符串高
}

// 注册自定义正则表达式校验规则
func init() {
	// 账号用户名校验
	RegisterPattern("username", "^[a-zA-Z0-9_]{5,20}$", "只允许输入5-20位大小写字母、数字、下划线", nil)
	// 密码为6-18位，需要包含：数字+大小写字母+特殊符号
	RegisterPattern("password", "", "密码为8-30位，需要以字母开头，包含：数字、大小写字母、特殊符号", func(f validator.FieldLevel) bool {
		s := f.Field().String()
		if s == "" {
			return true
		}

		// 1. 字符串必须以字母开头
		if !pwdReg1.MatchString(s) {
			return false
		}

		// 2. 字符串长度在 8 到 30 个字符之间
		if len(s) < 8 || len(s) > 30 {
			return false
		}

		// 3. 字符串不能全是数字
		if pwdReg2.MatchString(s) {
			return false
		}

		// 4. 字符串不能全是非数字
		if pwdReg3.MatchString(s) {
			return false
		}

		// 5. 字符串不能全是字母和数字
		if pwdReg4.MatchString(s) {
			return false
		}

		// 所有条件都满足
		return true
	})
}

// RegisterPattern 注册自定义正则表达式
// name: 正则名
// regexpStr: 正则表达式
// errMsg: 校验不通过时的报错信息
// fn: 自定义校验函数
func RegisterPattern(name, regexpStr, errMsg string, fn ValidateFn) {
	if regexpStr == "" && fn == nil {
		err := errorx.NewBiz("正则表达式或校验函数不能同时为空")
		logx.PanicError(err)
	}
	if name == "" {
		err := errorx.NewBiz("请设置正则名")
		logx.PanicError(err)
	}

	if _, ok := RegexpMap[name]; ok {
		err := errorx.NewBiz("正则名[%s]已存在", name)
		logx.PanicError(err)
	}

	var reg *regexp.Regexp
	if regexpStr != "" {
		reg = regexp.MustCompile(regexpStr)
	}
	RegexpMap[name] = &Validation{name, reg, errMsg, fn}
}

func patternValidFunc(f validator.FieldLevel) bool {
	reg := RegexpMap[f.Param()]
	if reg == nil {
		logx.Warnf("[%s]的正则校验规则不存在!", f.Param())
		return false
	}

	// 以自定义校验函数优先
	if reg.Fn != nil {
		return reg.Fn(f)
	}

	// 正则校验
	if reg.Reg != nil {
		return reg.Reg.MatchString(f.Field().String())
	}

	return false
}

func GetRegErrorMsg(name string) string {
	if reg, ok := RegexpMap[name]; ok {
		return reg.Msg
	}
	return fmt.Sprintf("正则名[%s]不存在", name)
}
