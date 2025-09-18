package openapi

import (
	"cmp"
	"encoding/json"
	"fmt"
	"gofly/internal/config"
	"gofly/pkg/utils/cryptox"
	"gofly/pkg/utils/idx"
	"time"
)

type ApiDoc struct {
	Openapi    string                      `json:"openapi"` // 版本信息，一般固定 3.0.3
	Info       Info                        `json:"info"`    // 系统信息
	Servers    []Server                    `json:"servers"` // 接口域名
	Tags       []Tag                       `json:"tags"`    // 标签
	Paths      map[string]map[string]*Path `json:"paths"`   // 接口路径描述
	Components Components                  `json:"components"`
}

type Components struct {
	Schemas map[string]Schema `json:"schemas"`
}

type Schema struct {
	Title                string            `json:"title,omitempty"`
	Type                 string            `json:"type,omitempty"`
	Properties           map[string]Schema `json:"properties,omitempty"`
	Ref                  string            `json:"$ref,omitempty"`
	Examples             []any             `json:"examples,omitempty"`
	Example              any               `json:"example,omitempty"`
	Description          string            `json:"description,omitempty"` // 描述
	Items                *Schema           `json:"items,omitempty"`       // 数组类型
	Format               string            `json:"format,omitempty"`
	AdditionalProperties *Schema           `json:"additionalProperties,omitempty"`

	// 字段校验
	Required  bool `json:"required,omitempty"`
	Minimum   int  `json:"minimum,omitempty"`
	Maximum   int  `json:"maximum,omitempty"`
	MaxLength int  `json:"maxLength,omitempty"`
	MinLength int  `json:"minLength,omitempty"`
}

func WrapperBaseSchema(ref string, dataType string) Schema {

	var items *Schema
	if dataType == "array" {
		items = &Schema{
			Ref: ref,
		}
	}
	app := config.Inst.App
	codeName := cmp.Or(app.ResCodeName, "code")
	dataName := cmp.Or(app.ResDataName, "data")
	msgName := cmp.Or(app.ResMsgName, "message")
	defaultSuccessMsg := cmp.Or(app.DefaultSuccessMsg, "success")

	dataSchema := Schema{
		Description: "数据",
		Title:       "数据",
		Type:        dataType,
	}

	if items != nil {
		dataSchema.Items = items
	} else {
		dataSchema.Ref = ref
	}

	return Schema{
		Title: "Base",
		Type:  "object",
		Properties: map[string]Schema{
			codeName: {
				Description: "状态码, 200或0：正常，其他：错误",
				Title:       "状态码",
				Type:        "int",
				Example:     200,
			},
			msgName: {
				Description: "状态描述",
				Type:        "string",
				Title:       "状态描述",
				Example:     defaultSuccessMsg,
			},
			dataName: dataSchema,
			"success": {
				Description: "是否成功",
				Title:       "是否成功",
				Type:        "boolean",
				Example:     true,
			},
			"appName": {
				Description: "应用名，接口报错时会有此字段，可作为报错参考依据",
				Title:       "应用名",
				Type:        "string",
				Example:     app.Name,
			},
			"time": {
				Description: "毫秒时间戳",
				Title:       "时间戳",
				Type:        "string",
				Example:     time.Now().UnixMilli(),
			},
			"traceId": {
				Description: "日志id，接口报错时会有此字段，可作为报错日志快速定位依据",
				Title:       "日志id",
				Type:        "string",
				Example:     cryptox.Md5(idx.UuidStr())[:8],
			},
		},
	}
}

// Info  系统信息
type Info struct {
	Title          string `json:"title"`          // 系统标题, 如：xx系统
	TermsOfService string `json:"termsOfService"` // 接口域名，如： "localhost:8970"
	Version        string `json:"version"`        // 接口版本信息，如："2.0.0"
}

// Server "servers"
type Server struct {
	Url         string `json:"url"`         // 接口域名，如： "localhost:8970"
	Description string `json:"description"` // 接口域名描述，如："Inferred Url"
}

// tags
type Tag struct {
	Order int    `json:"x-order"` // 排序
	Name  string `json:"name"`    // 标签名称
}

type Path struct {
	ContentType string                  `json:"contentType"`
	Tags        []string                `json:"tags"`
	Summary     string                  `json:"summary"`
	Description string                  `json:"description"` // 接口描述，接受html格式
	OperationId string                  `json:"operationId"` // 一般按照规则 {summary} + Using + {method}
	Produces    []string                `json:"produces"`    // 一般按照规则 {summary} + Using + {method}
	Parameters  *[]PathParameter        `json:"parameters,omitempty"`
	RequestBody *map[string]interface{} `json:"requestBody,omitempty"`
	Responses   map[string]interface{}  `json:"responses"`

	Extensions *PathExtensions `json:"extensions,omitempty"`
}
type PathExtensions struct {
	Author string `json:"x-author"`
	Order  int    `json:"x-order"`
}

func NewRequestBodyRef(ref string) *map[string]interface{} {
	return NewRequestBody(ref, "", "", "")
}

func NewRequestBodyItem(resType string, itemType string, itemFormat string) *map[string]interface{} {
	return NewRequestBody("", resType, itemType, itemFormat)
}

func NewRequestBody(ref string, resType string, itemType string, itemFormat string) *map[string]interface{} {

	itemStr := ""
	refStr := ""
	// $ref和item只能二选一
	if resType != "" && itemType != "" && itemFormat != "" {
		itemStr = fmt.Sprintf(`"type": "%s", "items": {"type": "%s", "format": "%s"}`, resType, itemType, itemFormat)
	} else {
		refStr = fmt.Sprintf(`"$ref": "%s"`, ref)
	}

	str := fmt.Sprintf(`{
  "content": {
    "application/json": {
      "schema": {
       %s  %s
      }}}}`, refStr, itemStr)

	body := make(map[string]interface{})
	err := json.Unmarshal([]byte(str), &body)
	if err != nil {
		return nil
	}
	return &body
}

type PathParameter struct {
	Name        string  `json:"name"`        // 参数名
	In          string  `json:"in"`          // 参数的位置，可能的值有 "query", "header", "path" 或 "cookie"
	Description string  `json:"description"` // 参数描述支持富文本
	Required    bool    `json:"required"`    // 是否必须
	Style       string  `json:"style"`       // 默认值为（基于in字段的值）：query、cookie 对应 form； path 、header 对应 simple;
	Schema      *Schema `json:"schema,omitempty"`
	Example     any     `json:"example,omitempty"`
}

// @param style
func NewPathParameter(name, in, description, dataType, style string, required bool) PathParameter {
	return PathParameter{
		Name:        name,
		In:          in,
		Description: description,
		Required:    required,
		Style:       style,
		Schema: &Schema{
			Type: dataType,
		},
	}
}

func NewPathResponse(ref string) map[string]interface{} {
	str := fmt.Sprintf(`{
  "200": {
    "description": "OK",
    "content": {
      "application/json": {
        "schema": {
          "$ref": "%s"
        }}}}}`, ref)

	body := make(map[string]interface{})
	_ = json.Unmarshal([]byte(str), &body)
	return body
}
