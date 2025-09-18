package ioc

import (
	"errors"
	"fmt"
	"gofly/pkg/logx"
	"reflect"
)

// 全局默认实例容器
var defaultContainer = newContainer()

// 注册实例至全局默认ioc容器
func Register(component any, opts ...ComponentOption) {
	defaultContainer.register(component, opts...)
}

func PrepareDao(component any, opts ...ComponentOption) {
	defaultContainer.prepareDao(component, opts...)
}

func PrepareSvc(component any, opts ...ComponentOption) {
	defaultContainer.prepareSvc(component, opts...)
}

func PrepareCtrl(component any, opts ...ComponentOption) {
	defaultContainer.prepareCtrl(component, opts...)
}

// GetType 通过组件类型获取组件实例
func GetType[T any]() T {
	var t T

	tp := reflect.TypeOf(t)
	for tp.Kind() == reflect.Ptr {
		tp = tp.Elem()
	}

	var cpath string
	if tp.Kind() == reflect.Struct {
		n := tp.Name()
		// 通过包路径和名称获取实例
		path := tp.PkgPath()

		cpath = fmt.Sprintf("%s.%s", path, n)
		c, _ := defaultContainer.Get(cpath)
		if m, ok := c.(T); ok {
			return m
		}
	}
	msg := fmt.Sprintf("未找到bean: %s", cpath)
	logx.Error("", errors.New(msg))
	panic(msg)
}

// Get 根据组件名获取组件实例
func Get[T any](name string) T {
	c, _ := defaultContainer.Get(name)
	if t, ok := c.(T); ok {
		return t
	}
	return GetType[T]()
}

// 使用全局默认ioc容器中已注册的组件实例 -> 注入到指定实例所依赖的组件实例
func Inject(component any) error {
	return defaultContainer.Inject(component)
}

var postIocFuncs []func()

// ioc初始化完成后执行函数
func AddPostIocFunc(postIocFunc func()) {
	postIocFuncs = append(postIocFuncs, postIocFunc)
}

// 注入默认ioc容器内组件所依赖的其他组件实例
func InjectComponents() {
	RegisterPrepare()

	if nil != defaultContainer.InjectComponents() {
		panic("注入ioc失败")
	}
	for _, fn := range postIocFuncs {
		fn()
	}
}
