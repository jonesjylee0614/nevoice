package route

import (
	//一定要导入这个Controller包，用来注册需要访问的方法
	//这里路由-由构架是添加-开发者仅在指定工程目录下controller.go文件添加即可

	_ "gofly/internal/api"
	_ "gofly/internal/app"
	"gofly/internal/config"
	"gofly/internal/route/middleware"
	"gofly/pkg/logx"
	"gofly/pkg/utils/collx"
	"net/http"

	"strings"
	"time"

	//工具
	"gofly/pkg/utils/gf"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

// 路由初始化
func InitRouter() *gin.Engine {
	//控制台日志级别
	gin.SetMode(config.Inst.GetGinMode())
	//ReleaseMode 为方便调试，Gin 框架在运行的时候默认是debug模式，在控制台默认会打印出很多调试日志，上线的时候我们需要关闭debug模式，改为release模式。

	contextPath := config.Inst.App.ContextPath

	//初始化路由
	R := gin.Default()
	_ = R.SetTrustedProxies([]string{"127.0.0.1"})
	/**静态资源处理*/
	// a.1.前端项目静态资源
	// R.StaticFile("/favicon.ico", "./resource/webadmin/favicon.ico")
	//a.2.附件访问
	R.Static(contextPath+"/resource", "./resource")
	//a.3.业务后台
	R.Static(contextPath+"/webadmin", "./resource/webadmin")
	R.Static(contextPath+"/webbusiness", "./resource/webbusiness")
	R.Static(contextPath+"/webh5", "./resource/webh5")
	// 静态文件
	R.Static(contextPath+"/print_voice", config.Inst.Voice.PrintPath)
	R.Static(contextPath+"/meeting_voice", config.Inst.Voice.MeetingPath)
	R.LoadHTMLFiles(contextPath+"./resource/developer/template/install.html", "./resource/developer/template/isinstall.html")
	//访问域名根目录重定向
	R.GET("/", func(c *gin.Context) {
		if config.Inst.App.Rootview != "" {
			c.Redirect(http.StatusMovedPermanently, config.Inst.App.Rootview)
		}
		c.JSON(200, gin.H{config.Inst.App.ResCodeName: 200, config.Inst.App.ResMsgName: "true"})
	})
	// 为 multipart forms 设置较低的内存限制 (默认是 32 MiB)
	R.MaxMultipartMemory = 8 << 20 // 8 MiB
	//0.跨域访问-注意跨域要放在gin.Default下
	var strArr []string
	if config.Inst.App.Allowurl != "" {
		strArr = strings.Split(config.Inst.App.Allowurl, `,`)
	} else {
		strArr = []string{"http://localhost:8080"}
	}

	R.Use(cors.New(cors.Config{
		AllowOrigins: strArr,
		// AllowOriginFunc:  func(origin string) bool { return true },
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"},
		AllowHeaders:     []string{"X-Requested-With", "Content-Type", "Authorization", "Businessid", "verify-encrypt", "ignoreCancelToken", "verify-time", "x-limited-token"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
		AllowOriginFunc: func(origin string) bool {
			if collx.ArrayContains(strArr, origin) {
				return true
			}
			logx.Warnf("not allow origin: %s", origin)
			return false
		},
	}))
	//1.全局异常捕捉
	R.Use(middleware.ErrorHandler())
	//2.限流rate-limit 中间件
	R.Use(middleware.LimitHandler())
	//3.判断接口是否合法
	//R.Use(middleware.ValidityApi())
	//4.验证token
	R.Use(middleware.JwtVerify)
	//5.跨域
	if config.Inst.App.AllowCros {
		R.Use(middleware.Cors(config.Inst.App.AllowOrigin))
	}

	//找不到路由
	R.NoRoute(func(c *gin.Context) {
		path := c.Request.URL.Path
		method := c.Request.Method
		c.AbortWithStatusJSON(404, gin.H{
			config.Inst.App.ResCodeName: 404,
			config.Inst.App.ResMsgName:  "您" + method + "请求地址：" + path + "不存在！",
		})
	})
	//绑定接口路由
	gf.Bind(R)

	logx.Warnf("注册路由完成，所有路由都在/app文件夹下，路由路径即子为文件夹路径")
	return R
}
