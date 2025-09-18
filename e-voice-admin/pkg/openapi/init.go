package openapi

import (
	"cmp"
	"gofly/internal/config"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/gf"
	"net/http"

	"github.com/gin-gonic/gin"
)

func InitOpenapi(router *gin.Engine) {

	app := config.Inst.App
	api := config.Inst.Api

	// fullPath对应的route
	methodMap := make(map[string]gf.Route)
	for _, route := range gf.Routes {
		methodMap[route.FullPath] = route
	}

	for k, path := range groupPathMap {
		if method, has := methodMap[k]; has {
			path.path = app.ContextPath + method.Path
			path.method = method.HttpMethod
			path.name = cmp.Or(path.name, method.Path)
		}
	}

	if !api.IsEnable() {
		return
	}

	handlers := make([]gin.HandlerFunc, 0)

	if "" != api.Username && "" != api.Password {
		handlers = append(handlers, gin.BasicAuth(gin.Accounts{
			api.Username: api.Password,
		}))
	}

	authorized := router.Group(app.ContextPath+"/openapi/", handlers...)
	for _, rt := range GetApiRoutes() {
		authorized.GET(rt.Path, func(g *gin.Context) {
			if rt.Header != nil {
				for k, v := range rt.Header {
					g.Header(k, v)
				}
			}

			var data any
			if rt.Data != nil {
				data = rt.Data
			} else if rt.DataFn != nil {
				data = rt.DataFn()
			}

			if rt.DataType == "string" {
				g.String(http.StatusOK, anyx.ToString(data))
			} else if rt.DataType == "json" {
				g.JSON(http.StatusOK, data)
			}
		})
	}

}
