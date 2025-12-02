package main

import (
	"context"
	"errors"
	"fmt"
	"gofly/internal/config"
	"gofly/internal/route"
	"gofly/internal/route/middleware"
	"gofly/pkg/ioc"
	"gofly/pkg/logx"
	"gofly/pkg/openapi"
	"gofly/pkg/openapi/statics"
	"gofly/pkg/utils/ipx"
	"net/http"
	"os"
	"os/signal"
	"runtime"
	"strconv"
	"syscall"
	"time"
)

func main() {

	config.Inst.InitFlag()
	// 初始化配置
	config.Inst.InitConfig()

	// 注入ioc组件
	ioc.InjectComponents()

	//如果配置cpu核数大于当前计算机核数，则等当前计算机核数
	cpuNum, _ := strconv.Atoi(config.Inst.App.CPUnum)
	mycpu := runtime.NumCPU()
	if cpuNum > mycpu {
		cpuNum = mycpu
	}
	if cpuNum > 0 {
		runtime.GOMAXPROCS(cpuNum)
	} else {
		runtime.GOMAXPROCS(mycpu)
	}

	RunServer()
}

func RunServer() {
	//加载路由
	r := route.InitRouter()

	// 打印启动成功信息
	url := fmt.Sprintf("http://%s:%s/%s", ipx.GetOutBoundIP(), config.Inst.App.Port, config.Inst.App.ContextPath)

	frontUrl := fmt.Sprintf("\n ⚡ 前端地址：%s%s", url, "webbusiness")
	h5Url := fmt.Sprintf("\n ⚡ h5地址：%s%s", url, "webh5")

	// 添加openapi的静态资源
	apiStr := ""
	if config.Inst.Api.IsEnable() {
		apiStr = "\n ⚡ API地址：" + url + "openapi/"

		r.Use(middleware.Static(middleware.StaticConfig{
			FS:         &statics.ApiFiles,
			URLPrefix:  "openapi",
			EnableGzip: true,
		}))
		openapi.InitOpenapi(r)
	}

	logx.Infof(`
 ⚡ 启动App[ %s ]成功，用时：%dms 
 ⚡ 接口地址：%s%s%s%s
`, config.Inst.App.Name, time.Now().UnixMilli()-config.Inst.App.StartTime,
		url, frontUrl, h5Url, apiStr)

	if config.Inst.App.IsDev() {
		logx.Infof("在浏览器访问：http://localhost:" + config.Inst.App.Port + "/common/install/index 进行安装")
		_ = r.Run(":" + config.Inst.App.Port)
	} else { //优雅-生成环境使用
		//换一种启动方式
		srv := &http.Server{
			Addr:    ":" + config.Inst.App.Port,
			Handler: r,
		}
		logx.Infof("启动端口：" + config.Inst.App.Port)
		go func() {
			if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
				str := fmt.Sprintf("listen: %s\n", err) //拼接字符串
				logx.Errorf(str)
			}
		}()

		// 等待中断信号以优雅地关闭服务器（设置 5 秒的超时时间）
		quit := make(chan os.Signal)
		signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
		<-quit
		logx.Infof("关闭服务器 ...")

		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := srv.Shutdown(ctx); err != nil {
			str := fmt.Sprintf("服务器关闭： %s\n", err) //拼接字符串
			logx.Errorf(str)
		}
		logx.Infof("服务器正在退出 ...")
	}
}
