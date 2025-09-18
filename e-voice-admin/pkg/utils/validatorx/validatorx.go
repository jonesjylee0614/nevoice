package validatorx

import (
	"cmp"
	"errors"
	"gofly/internal/config"
	"gofly/pkg/utils/stringx"
	"gofly/pkg/utils/structx"
	"reflect"
	"strings"

	"github.com/gin-gonic/gin/binding"
	"github.com/go-playground/locales/zh"
	ut "github.com/go-playground/universal-translator"
	"github.com/go-playground/validator/v10"
	zhtrans "github.com/go-playground/validator/v10/translations/zh"
)

var (
	trans ut.Translator
)

func init() {
	config.AddAfterConfigFn(Init)
}

func Init(c *config.Config) {
	// 获取gin的校验器
	validate, ok := binding.Validator.Engine().(*validator.Validate)
	if !ok {
		return
	}

	// 修改返回字段key的格式
	validate.RegisterTagNameFunc(func(fld reflect.StructField) string {
		// 如果存在校验错误提示消息，则使用字段名，后续需要通过该字段名获取相应错误消息
		msgName := cmp.Or(c.App.ResMsgName, "message")
		if _, ok := fld.Tag.Lookup(msgName); ok {
			return fld.Name
		}
		name := strings.SplitN(fld.Tag.Get("json"), ",", 2)[0]
		if name == "-" {
			return ""
		}
		return name
	})

	// 注册翻译器
	zhlc := zh.New()
	uni := ut.New(zhlc, zhlc)

	trans, _ = uni.GetTranslator("zh")

	// 注册翻译器
	_ = zhtrans.RegisterDefaultTranslations(validate, trans)

	// 注册自定义校验器
	_ = validate.RegisterValidation(CustomPatternTagName, patternValidFunc)

	// 注册自定义正则校验规则
}

// Translate 翻译错误信息
func Translate(data any, err error) map[string][]string {
	var result = make(map[string][]string)

	var es validator.ValidationErrors
	errors.As(err, &es)

	for _, err := range es {
		fieldName := err.Field()

		// 判断该字段是否设置了自定义的错误描述信息，存在则使用自定义错误信息进行提示
		if field, ok := structx.IndirectType(reflect.TypeOf(data)).FieldByName(fieldName); ok {
			if errMsg, ok := field.Tag.Lookup("msg"); ok {
				customMsg := getCustomErrMsg(err.Tag(), errMsg)
				if customMsg != "" {
					result[fieldName] = append(result[fieldName], customMsg)
					continue
				}
			}
		}

		// 如果是自定义正则校验规则，则使用自定义的错误描述信息
		if err.Tag() == CustomPatternTagName {
			msg := GetRegErrorMsg(err.Param())
			result[fieldName] = append(result[fieldName], fieldName+msg)
			continue
		}

		result[fieldName] = append(result[fieldName], err.Translate(trans))
	}

	return result
}

// Translate 翻译错误信息为字符串
func Translate2Str(data any, err error) string {
	res := Translate(data, err)
	errMsgs := make([]string, 0)
	for _, v := range res {
		errMsgs = append(errMsgs, v...)
	}
	return strings.Join(errMsgs, ", ")
}

// 获取自定义的错误提示消息
//
// @param validTag 校验标签，如required等
// @param customMsg 自定义错误消息
func getCustomErrMsg(validTag, customMsg string) string {
	// 解析 msg:"required=用户名不能为空,min=用户名长度不能小于8位"
	msgs := strings.Split(customMsg, ",")
	for _, msg := range msgs {
		tagAndMsg := strings.Split(stringx.Trim(msg), "=")
		if len(tagAndMsg) > 1 && validTag == stringx.Trim(tagAndMsg[0]) {
			// 获取valid tag对应的错误消息
			return stringx.Trim(tagAndMsg[1])
		}
	}

	return customMsg
}
