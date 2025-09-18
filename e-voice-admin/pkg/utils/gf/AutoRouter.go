package gf

/**
* 自动路由工具
 */
import (
	"fmt"
	"gofly/internal/config"
	"gofly/pkg/ioc"
	"gofly/pkg/utils/reflectx"
	"reflect"
	"strings"

	"github.com/gin-gonic/gin"
)

// Route 路由结构体
type Route struct {
	Path       string         //url路径
	HttpMethod string         //http方法 get post
	Method     reflect.Value  //方法路由
	FullPath   string         // 全路径 如: gofly/internal/app/voice.(*Document).Save
	Args       []reflect.Type //参数类型
}

type PermRoute interface {
	// PermRoutes 标记哪些接口需要权限，格式：[权限码]handler
	Perms() map[string][]gin.HandlerFunc
}

// Routes 路由集合
var (
	Routes []Route
	// PermMap 权限map，path -> perm
	PermMap = map[string]string{}
)

// RegisterRoute 注册控制器
func RegisterRoute(ctl PermRoute) {

	ioc.PrepareCtrl(ctl)

	pkgPath := reflect.TypeOf(ctl).Elem().PkgPath()
	v := reflect.ValueOf(ctl)
	//非控制器或无方法则直接返回
	if v.NumMethod() == 0 {
		return
	}
	rootPkg := ""
	if strings.Contains(pkgPath, "/app") {
		arr := strings.Split(pkgPath, "/app")
		rootPkg = arr[len(arr)-1]
	}
	ctrlName := reflect.TypeOf(ctl).String()
	module := ctrlName
	if strings.Contains(ctrlName, ".") {
		module = ctrlName[strings.Index(ctrlName, ".")+1:]
	}
	structName := module
	if module == "Index" { //去index
		module = "/"
	} else {
		module = "/" + strings.ToLower(module) + "/"
	}

	// 遍历需要授权的handler
	authMap := make(map[string]string)
	if ctl.Perms() != nil {
		for k, fns := range ctl.Perms() {
			for _, fn := range fns {
				authMap[reflectx.GetGinFnPath(fn)] = k
			}
		}
	}

	//遍历方法
	for i := 0; i < v.NumMethod(); i++ {
		method := v.Method(i)
		// 忽略参数不为gin.Context的
		if method.Type().NumIn() != 1 || method.Type().In(0).String() != "*gin.Context" {
			continue
		}
		action := v.Type().Method(i).Name
		//拼接路由地址
		path := rootPkg + module + FirstLower(action)
		//遍历参数
		params := make([]reflect.Type, 0, v.NumMethod())
		httpMethod := "POST" //默认POST
		if strings.HasPrefix(action, "Get") || action == "Index" {
			httpMethod = "GET"
		} else if strings.HasPrefix(action, "Del") || action == "Del" {
			httpMethod = "DELETE"
		} else if strings.HasPrefix(action, "Put") || action == "Put" {
			httpMethod = "PUT"
		}
		for j := 0; j < method.Type().NumIn(); j++ {
			params = append(params, method.Type().In(j))
		}
		fullPath := fmt.Sprintf("%s.(*%s).%s-fm", pkgPath, structName, action)
		route := Route{
			Path:       path,
			Method:     method,
			FullPath:   fullPath,
			Args:       params,
			HttpMethod: httpMethod,
		}
		// 权限
		if v, has := authMap[fullPath]; has {
			PermMap[path] = v
		}

		Routes = append(Routes, route)
	}
	return
}

// 绑定路由 m是方法GET POST等
// 绑定基本路由
func Bind(e *gin.Engine) {
	contextPath := config.Inst.App.ContextPath
	for _, route := range Routes {
		if config.Inst.Log.EnableRouterLog {
			fmt.Printf("注册路由: %s %s \n", route.HttpMethod, route.Path)
		}

		if route.HttpMethod == "GET" {
			e.GET(contextPath+route.Path, match(route))
		}
		if route.HttpMethod == "POST" {
			e.POST(contextPath+route.Path, match(route))
		}
		if route.HttpMethod == "DELETE" {
			e.DELETE(contextPath+route.Path, match(route))
		}
		if route.HttpMethod == "PUT" {
			e.PUT(contextPath+route.Path, match(route))
		}
	}
}

// 根据path匹配对应的方法
func match(route Route) gin.HandlerFunc {
	return func(c *gin.Context) {
		route.Method.Call([]reflect.Value{reflect.ValueOf(c)})
	}
}
