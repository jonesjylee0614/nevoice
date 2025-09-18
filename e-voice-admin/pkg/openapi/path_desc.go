package openapi

import (
	"cmp"

	"github.com/gin-gonic/gin"
)

type State int

const (
	StateComplete State = 1
	StateDevelop  State = 2
)

// 接口描述，用于收集openapi相关参数
type PathDoc struct {
	handler   gin.HandlerFunc // 处理函数
	method    string          // 请求方法
	path      string          // 请求路径
	name      string          // 接口名
	note      string          // 接口描述，接受html格式
	state     State           // 接口状态  1完成 2开发中
	hide      bool            // 接口文档是否隐藏
	reqParam  interface{}     // 请求参数,直接给出结构体即可
	reqParams []PathParameter // 请求参数列表，多个参数集合
	reqType   ReqType         // 请求参数方式：json / form, 默认form
	resParam  interface{}     // 响应参数,直接给出结构体即可
	produces  string          // 响应类型，默认json
	order     int             // 排序号
	author    string          // 作者
}

// 默认数据
func (p *PathDoc) Default() {
	p.produces = cmp.Or(p.produces, ProduceJson)
	p.state = cmp.Or(p.state, StateDevelop)
	p.reqType = cmp.Or(p.reqType, ReqTypeJson)
}

// 设置接口名
func (p *PathDoc) Name(name string) *PathDoc {
	p.name = name
	return p
}

// 设置handler
func (p *PathDoc) Handler(handler func(c *gin.Context)) *PathDoc {
	p.handler = handler
	return p
}

// 设置接口描述，接受html格式
func (p *PathDoc) Note(note string) *PathDoc {
	p.note = note
	return p
}

// 设置接口开发状态 1完成 2开发中
func (p *PathDoc) State(state State) *PathDoc {
	p.state = state
	return p
}

// 设置 hide 并返回 PathDoc 结构体本身
func (p *PathDoc) Hide() *PathDoc {
	p.hide = true
	return p
}

// 设置 reqParam 并返回 PathDoc 结构体本身
func (p *PathDoc) Req(reqParam interface{}) *PathDoc {
	p.reqParam = reqParam
	return p
}

// ReqParams 不建议使用，设置请求参数列表，建议只有一个参数的时候使用
func (p *PathDoc) ReqParams(reqParams ...PathParameter) *PathDoc {
	p.reqParams = reqParams
	return p
}

// 设置请求类型 默认json
func (p *PathDoc) ReqType(reqType ReqType) *PathDoc {
	p.reqType = reqType
	return p
}

// 设置返回体对象
func (p *PathDoc) Res(res interface{}) *PathDoc {
	p.resParam = res
	return p
}

// 设置接口响应类型，默认json
func (p *PathDoc) Produces(produces string) *PathDoc {
	p.produces = produces
	return p
}

// 设置接口排序
func (p *PathDoc) Order(order int) *PathDoc {
	p.order = order
	return p
}

// 设置作者
func (p *PathDoc) Author(author string) *PathDoc {
	p.author = author
	return p
}

func NewPathDoc() *PathDoc {
	return new(PathDoc)
}
