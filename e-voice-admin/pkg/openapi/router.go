package openapi

import (
	_ "embed"
)

type ApiRoute struct {
	Method   string
	Path     string
	Data     any
	DataFn   func() *ApiDoc
	Header   map[string]string
	DataType string // string | json
}

func GetApiRoutes() []*ApiRoute {
	routes := [...]*ApiRoute{
		//{
		//	Method: "GET",
		//	Path:   "index.html",
		//	Data:   apiHtml,
		//	Header: map[string]string{
		//		"Content-Type": "text/html; charset=utf-8",
		//	},
		//	DataType: "string",
		//},
		{
			Method: "GET",
			Path:   "/swagger-resources",
			Data: []map[string]string{
				{
					"name":           "default",
					"url":            "/v3/api-docs",
					"swaggerVersion": "3.0.3",
					"location":       "/v3/api-docs",
				},
			},
			DataType: "json",
		},
		{
			Method:   "GET",
			Path:     "/v3/api-docs",
			DataFn:   generateApiDoc,
			DataType: "json",
		},
	}

	return routes[:]
}
