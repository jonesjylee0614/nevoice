package ioc

import (
	"errors"
	"fmt"
	"gofly/internal/config"
	"gofly/pkg/logx"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/reflectx"
	"gofly/pkg/utils/structx"
	"reflect"
	"sort"
	"strings"
	"sync"
)

// 容器
type container struct {
	mu         sync.RWMutex
	components map[string]*Component // 组件名 对应的组件
}

func newContainer() *container {
	return &container{
		components: make(map[string]*Component),
	}
}

// 注册实例至实例容器
func (c *container) register(bean any, opts ...ComponentOption) {
	c.mu.Lock()
	defer c.mu.Unlock()

	cType := structx.IndirectType(reflect.TypeOf(bean))

	component := NewComponent(bean, opts...)
	name := component.Name
	if config.Inst.Log.EnableIocLog {
		logx.Debugf(" [ioc] register : %s = %s.%s", name, cType.PkgPath(), cType.Name())
	}

	// 组件名为空，则取组件路劲作为组件名
	if name == "" {
		name = fmt.Sprintf("%s.%s", cType.PkgPath(), cType.Name())
	}

	c.registerComponentsByName(name, component)

}

func (c *container) registerComponentsByName(name string, component *Component) {
	if _, ok := c.components[name]; ok {
		logx.Warnf("组件名[%s]已注册, 请勿重复注册...", name)
	}
	c.components[name] = component
}

// 注册对象实例的字段含有inject:"xxx"标签或者Setter方法，则注入对应组件实例
func (c *container) Inject(obj any) error {
	objValue := reflect.ValueOf(obj)

	if structx.Indirect(objValue).Kind() != reflect.Struct {
		return nil
	}

	cType := structx.IndirectType(reflect.TypeOf(obj))

	// 通过字段注入，解析字段tag、字段名作为bean名
	if err := c.injectWithField(objValue, cType); err != nil {
		return err
	}

	// 通过方法名注入，解析前缀名为Inject的方法，后缀作为bean名
	if err := c.injectWithMethodNameSuffix(objValue, cType); err != nil {
		return err
	}

	// 通过方法参数类型自动注入，解析方法名为DaoInject的方法，解析参数类型对应的名字为bean名
	// 方法名不能以Inject为前缀，会与前面的以方法名注入冲突
	if err := c.InjectWithMethodParam(objValue, cType, "DaoInject"); err != nil {
		return err
	}
	return nil
}

type PostInject interface {
	// PostInject bean注入完成后自动通过反射执行
	// see container.PostInject
	PostInject()
}

func (c *container) PostInject(obj any) error {
	cType := structx.IndirectType(reflect.TypeOf(obj))
	return c.InjectWithMethodParam(reflect.ValueOf(obj), cType, "PostInject")
}

// 对所有组件实例执行Inject。即为实例字段注入依赖的组件实例
func (c *container) InjectComponents() error {
	keys := collx.MapKeys(c.components)
	sort.Strings(keys)

	// 执行注入ioc对象
	logx.Infof("[ioc] 开始注入组件依赖，包括字段注入，方法注入，方法参数注入...")
	for _, key := range keys {
		cp := c.components[key]
		if err := c.Inject(cp.Value); err != nil {
			logx.PanicError(err)
		}
	}

	// bean所有依赖注入完成后执行PostInject函数
	logx.Infof("[ioc] 开始异步执行PostInject函数...")
	for _, key := range keys {
		go func() {
			cp := c.components[key]
			if err := c.PostInject(cp.Value); err != nil {
				logx.PanicError(err)
			}
		}()
	}

	return nil
}

// 根据组件实例名，获取对应实例信息
func (c *container) Get(nameOrPath string) (any, error) {
	component, ok := c.components[nameOrPath]
	if !ok {
		return nil, errors.New("component not found: " + nameOrPath)
	}
	return component.Value, nil
}

// 根据实例字段的inject:"xxx"标签进行依赖注入
func (c *container) injectWithField(objValue reflect.Value, objType reflect.Type) error {
	objValue = structx.Indirect(objValue)
	fields := reflectx.GetAllFields(objType)
	for _, field := range fields {
		componentName, ok := field.Tag.Lookup("inject")
		if !ok {
			continue
		}
		// inject tag字段名为空则默认为字段名
		if componentName == "" {
			componentName = field.Name
		}
		injectInfo := fmt.Sprintf("[ioc] inject  field [ %s -> %s.%s#%s ]", componentName, objType.PkgPath(), objType.Name(), field.Name)
		if config.Inst.Log.EnableIocLog {
			logx.Debugf(injectInfo)
		}

		// 优先从字段名获取组件
		component, _ := c.Get(componentName)

		var err error
		ft := structx.IndirectType(field.Type)
		// 组件未拿到时，尝试从包路径+字段名获取组件
		if component == nil {
			componentPath := fmt.Sprintf("%s.%s", ft.PkgPath(), componentName)
			component, _ = c.Get(componentPath)
		}
		// 组件未拿到时，尝试从包路径+类型名获取组件
		if component == nil {
			componentPath := fmt.Sprintf("%s.%s", ft.PkgPath(), ft.Name())
			component, err = c.Get(componentPath)
		}
		// 仍然没拿到组件，则报错
		if err != nil {
			return fmt.Errorf("%s error: %s", injectInfo, err.Error())
		}

		fieldValue := objValue.FieldByName(componentName)
		if !fieldValue.IsValid() || !fieldValue.CanSet() {
			// 不可导出变量处理
			fieldPtrValue := reflect.NewAt(fieldValue.Type(), fieldValue.Addr().UnsafePointer())
			fieldValue = fieldPtrValue.Elem()
			if !fieldValue.IsValid() || !fieldValue.CanSet() {
				return fmt.Errorf("%s error: 字段无效或为不可导出类型", injectInfo)
			}
		}

		fieldValue.Set(reflect.ValueOf(component))
	}

	return nil
}

// 通过方法名注入，解析前缀名为Inject的方法，后缀作为bean名
func (c *container) injectWithMethodNameSuffix(objValue reflect.Value, objType reflect.Type) error {

	rt := objValue.Type()

	for i := 0; i < rt.NumMethod(); i++ {
		method := rt.Method(i)
		methodName := method.Name

		// 不是以Inject开头的函数，则默认跳过
		if !strings.HasPrefix(methodName, "Inject") {
			continue
		}

		// 获取组件名，InjectTestApp -> TestApp
		componentName := methodName[6:]

		injectInfo := fmt.Sprintf("[ioc] inject method [ %s.%s#%s(%s) ]", objType.PkgPath(), objType.Name(), methodName, componentName)
		if config.Inst.Log.EnableIocLog {
			logx.Debugf(injectInfo)
		}

		if method.Type.NumIn() != 2 {
			logx.Warnf("%s error: 方法入参不为1个, 无法进行注入", injectInfo)
			continue
		}

		component, err := c.Get(componentName)
		if err != nil {
			return fmt.Errorf("%s error: %s", injectInfo, err.Error())
		}

		componentType := reflect.TypeOf(component)
		// 期望的组件类型，即参数入参类型
		expectedComponentType := method.Type.In(1)
		if !componentType.AssignableTo(expectedComponentType) {
			componentType = structx.IndirectType(componentType)
			return fmt.Errorf("%s error: 注入类型不一致(期望类型->%s.%s, 组件类型->%s.%s)", injectInfo, expectedComponentType.PkgPath(), expectedComponentType.Name(), componentType.PkgPath(), componentType.Name())
		}

		method.Func.Call([]reflect.Value{objValue, reflect.ValueOf(component)})
	}

	return nil
}

// 通过方法参数类型自动注入，解析指定方法名的方法，解析参数类型对应的名字为bean名并调用此方法
func (c *container) InjectWithMethodParam(objValue reflect.Value, objType reflect.Type, methodName string) error {

	method := objValue.MethodByName(methodName)
	if !method.IsValid() {
		return nil
	}
	// 获取参数列表，遍历参数列表，获取每个参数的类型，通过类型名字获取对应的组件实例，注入到方法中
	methodType := method.Type()
	var params []reflect.Value
	pkgPath := objType.PkgPath()
	objName := objType.Name()

	for j := 0; j < methodType.NumIn(); j++ {
		paramType := methodType.In(j)
		if paramType.Kind() != reflect.Ptr {
			logx.Panicf("[ioc] inject method [ %s.%s#%s(%s) ] error: 参数类型需要是指针类型", pkgPath, objName, methodName, paramType.Name())
			continue
		}

		paramTypeElem := paramType.Elem()

		if paramTypeElem.Kind() != reflect.Struct {
			logx.Panicf("[ioc] inject method [ %s.%s#%s(%s) ] error: 参数类型需要是结构体类型", pkgPath, objName, methodName, paramTypeElem.Name())
			continue
		}

		componentName := paramTypeElem.Name()
		injectInfo := fmt.Sprintf("[ioc] inject method [ %s.%s#%s(%s) ]", pkgPath, objName, methodName, componentName)
		if config.Inst.Log.EnableIocLog {
			logx.Debugf(injectInfo)
		}

		component, _ := c.Get(componentName)
		if component == nil {
			var cpath = fmt.Sprintf("%s.%s", paramTypeElem.PkgPath(), paramTypeElem.Name())

			if c, err := c.Get(cpath); err != nil {
				logx.Panicf("未找到bean: %s, %v", componentName, err.Error())
			} else {
				component = c
			}
		}
		componentType := reflect.TypeOf(component)
		if !componentType.AssignableTo(paramType) {
			componentType = structx.IndirectType(componentType)
			return fmt.Errorf("%s error: 注入类型不一致(期望类型->%s.%s, 组件类型->%s.%s)", injectInfo, paramType.PkgPath(), paramType.Name(), componentType.PkgPath(), componentType.Name())
		}

		params = append(params, reflect.ValueOf(component))
	}

	method.Call(params)

	return nil
}
