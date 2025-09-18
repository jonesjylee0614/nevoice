package openapi

import (
	"cmp"
	"fmt"
	"gofly/internal/config"
	"gofly/pkg/json"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/reflectx"
	"gofly/pkg/utils/stringx"
	"gofly/pkg/utils/structx"
	"reflect"
	"strings"
)

type GroupDoc struct {
	GroupName string // 分组名，相同的分组名接口会放到一起展示
	Order     int    // 指定排序号 默认0 越小越靠前
	Hide      bool   // 是否隐藏
	Paths     []*PathDoc
	basePath  string
}

var (
	apiDoc       *ApiDoc
	groupDocs    = make([]*GroupDoc, 0, 10)
	groupPathMap = make(map[string]*PathDoc)
	timeTypes    = []string{"base.JsonTime", "time.Time"}
	customTypes  = []string{"core.ID"}
)

func RegisterGroupDoc(doc *GroupDoc) {
	// 注册openapi
	groupDocs = append(groupDocs, doc)
	for _, path := range doc.Paths {
		// 获取方法名
		fullName := reflectx.GetGinFnPath(path.handler)
		// 设置path默认值
		path.Default()

		groupPathMap[fullName] = path
	}
}

func isValidStruct(tp reflect.Type) bool {
	tp = structx.IndirectType(tp)
	return tp.Kind() == reflect.Struct && !collx.ArrayContains(timeTypes, tp.String()) && !collx.ArrayContains(customTypes, tp.String())
}

func dealStructSchemaField(field reflect.StructField, pts map[string]Schema, schemas map[string]Schema) {
	field.Type = structx.IndirectType(field.Type)

	// 跳过忽略字段
	if isSkipField(field) {
		return
	}

	// 递归查找父级字段信息
	if field.Anonymous {
		dealAnonymousSchemaFields(field, pts, schemas)
		return
	}

	// 获取字段名
	fieldName := getFieldName(field)

	comment := cmp.Or(field.Tag.Get("comment"), fieldName)

	sp := Schema{
		Description: comment,
		Title:       comment,
		Required:    false,
	}

	binding := field.Tag.Get("binding")
	if binding != "" {
		// 是否必填
		if stringx.Contains(binding, "required") {
			sp.Required = true
		}
		// min max
		// gt lt
	}

	// 处理结构体字段
	if isValidStruct(field.Type) {
		name := getStructName(field.Type)
		dealStruct(name, field.Type, schemas)
		sp.Ref = "#/components/schemas/" + name
		pts[fieldName] = sp
		return
	}

	// 处理数组字段
	if field.Type.Kind() == reflect.Slice || field.Type.Kind() == reflect.Array {
		// 获取数组类型
		// 获取切片的元素类型（指针指向的类型）
		sliceElemType := structx.IndirectType(field.Type.Elem())
		name := getStructName(sliceElemType)
		if isValidStruct(sliceElemType) {
			dealStruct(name, sliceElemType, schemas)
			// 返回结构体名
			sp.Items = &Schema{
				Ref: "#/components/schemas/" + name,
			}
		} else {
			sp.Items = &Schema{
				Type: sliceElemType.Name(),
			}
		}
		sp.Type = "array"
		pts[fieldName] = sp
		return
	}

	sp.Type = field.Type.String()
	sp.Example = getFieldExampleValue(field)

	pts[fieldName] = sp
}

func getFieldExampleValue(field reflect.StructField) interface{} {

	// 设置时间类型的示例值
	indirectType := structx.IndirectType(field.Type)
	if collx.ArrayContains(timeTypes, indirectType.String()) {
		return json.NowJsonTime()
	}

	// 设置ID类型的示例值
	if indirectType.String() == "core.ID" {
		return "1"
	}

	// 设置普通类型的示例值
	example := cmp.Or(field.Tag.Get("example"), field.Tag.Get("default"))
	if strings.TrimSpace(example) != "" {
		return stringx.ParseByType(indirectType, example)
	} else {
		return reflect.Zero(indirectType).Interface()
	}
}

func dealAnonymousSchemaFields(field reflect.StructField, pts map[string]Schema, schemas map[string]Schema) {
	if isValidStruct(field.Type) {
		for i := 0; i < field.Type.NumField(); i++ {
			subField := field.Type.Field(i)
			dealStructSchemaField(subField, pts, schemas)
		}
	}
}

func isSkipField(field reflect.StructField) bool {
	return field.Tag.Get("json") == "-" || field.Tag.Get("openapi") == "-" || field.Tag.Get("form") == "-" || field.Tag.Get("hide") == "true"
}

func dealStructFieldPathParameter(field reflect.StructField, pms *[]PathParameter) {
	// 跳过忽略字段
	if isSkipField(field) {
		return
	}
	// 获取字段名
	fieldName := getFieldName(field)
	// 是否必填
	required := false
	if stringx.Contains(field.Tag.Get("binding"), "required") {
		required = true
	}

	// 组装字段描述
	description := cmp.Or(field.Tag.Get("comment"), fieldName)
	defVal := field.Tag.Get("default")
	if defVal != "" {
		description = fmt.Sprintf("%s 默认(%s)", description, defVal)
	}

	*pms = append(*pms, PathParameter{
		Name:        fieldName,
		In:          "query",
		Style:       "form",
		Description: description,
		Required:    required,
		Schema:      &Schema{Type: field.Type.String()},
		Example:     getFieldExampleValue(field),
	})
}

func dealAnonymousFieldsPathParameter(field reflect.StructField, pms *[]PathParameter) {
	if isValidStruct(field.Type) {
		for i := 0; i < field.Type.NumField(); i++ {
			subField := field.Type.Field(i)
			// 跳过指针字段
			if subField.Type.Kind() == reflect.Ptr {
				continue
			}
			if isSkipField(field) {
				continue
			}

			if isValidStruct(subField.Type) {
				dealAnonymousFieldsPathParameter(subField, pms)
				continue
			}

			dealStructFieldPathParameter(subField, pms)
		}
	}
}

func dealStruct(componentName string, srcType reflect.Type, schemas map[string]Schema) Schema {
	if scm, ok := schemas[componentName]; ok {
		return scm
	}
	pts := make(map[string]Schema)

	// 解析src对象，标记各个字段的描述信息
	schema := Schema{
		Title:      componentName,
		Type:       "object",
		Properties: pts,
	}

	schemas[componentName] = schema

	// 如果是指针类型
	srcType = structx.IndirectType(srcType)
	for i := 0; i < srcType.NumField(); i++ {

		field := srcType.Field(i)
		field.Type = structx.IndirectType(field.Type)

		// 跳过的字段
		if isSkipField(field) {
			continue
		}

		// 递归查找父级字段信息
		if field.Anonymous {
			dealAnonymousSchemaFields(field, pts, schemas)
			continue
		}

		dealStructSchemaField(field, pts, schemas)
	}
	return schema
}
func dealMapStruct(componentName string, srcType reflect.Type, schemas map[string]Schema) Schema {
	if scm, ok := schemas[componentName]; ok {
		return scm
	}

	elType := structx.IndirectType(srcType.Elem())
	if !isValidStruct(elType) {
		return Schema{Type: "string", AdditionalProperties: &Schema{Type: "string"}}
	}
	elComponentName := getStructName(elType)

	dealStruct(elComponentName, elType, schemas)

	// 解析src对象，标记各个字段的描述信息
	schema := Schema{
		Title: componentName,
		Type:  "object",
		AdditionalProperties: &Schema{
			Ref: "#/components/schemas/" + elComponentName,
		},
	}
	schemas[componentName] = schema
	return schema
}

func getStructName(srcType reflect.Type) string {
	// 如果是指针
	srcType = structx.IndirectType(srcType)

	pkgName := ""
	// 取倒数两个包名
	if srcType.PkgPath() != "" {
		pkgName = srcType.PkgPath()

		names := strings.Split(pkgName, "/")
		lv := 1
		if len(names) > 1 {
			lv = 2
		}
		pkgName = strings.Join(names[len(names)-lv:], ".")
	}

	name := srcType.Name()
	// 如果name里有泛型
	if strings.Contains(name, "[") && strings.Contains(name, "/") {
		// 去掉[和最后一个/之间的字符串
		replacer := stringx.SubString(name, strings.Index(name, "[")+1, strings.LastIndex(name, "/")+1)
		name = strings.Replace(name, replacer, "", 1)
	}

	return pkgName + "." + name
}

func getFieldName(field reflect.StructField) string {
	jn := field.Tag.Get("json")
	if jn != "" {
		return strings.Split(jn, ",")[0]
	}
	fm := field.Tag.Get("form")
	if fm != "" {
		return fm
	}
	return stringx.ToLowerCamel(field.Name)
}

func generateApiDoc() *ApiDoc {
	if apiDoc != nil {
		return apiDoc
	}

	app := config.Inst.Api

	paths := make(map[string]map[string]*Path)
	schemas := make(map[string]Schema)
	tags := make([]Tag, 0, 10)

	apiDoc = &ApiDoc{
		Openapi:    "3.0.3",
		Info:       Info{Title: app.Title, Version: app.Version},
		Servers:    []Server{{Url: app.Url}},
		Tags:       tags,
		Paths:      paths,
		Components: Components{schemas},
	}

	collComponents := func(src interface{}) (string, string) {
		srcType := structx.IndirectType(reflect.TypeOf(src))
		kind := srcType.Kind()
		switch kind {
		case reflect.Array, reflect.Slice:
			// 获取数组类型
			// 获取切片的元素类型（指针指向的类型）
			sliceElemType := structx.IndirectType(srcType.Elem())
			name := getStructName(sliceElemType)
			if isValidStruct(sliceElemType) {
				dealStruct(name, sliceElemType, schemas)
				// 返回结构体名
				return "array", name
			}

			return "array", name
		case reflect.Struct:
			name := getStructName(srcType)
			dealStruct(name, srcType, schemas)
			// 返回结构体名
			return "", name
		case reflect.Map:
			name := fmt.Sprintf("map«string,%s»", getStructName(srcType.Elem()))
			dealMapStruct(name, srcType, schemas)
			return "map", name
		case reflect.Bool:
			return "boolean", "boolean"
		default:
			return "", ""
		}
	}

	// 搜集get参数信息
	collGetReqStruct := func(pms []PathParameter, reqParam interface{}) []PathParameter {
		reqType := structx.IndirectType(reflect.TypeOf(reqParam))

		if isValidStruct(reqType) {
			for i := 0; i < reqType.NumField(); i++ {
				field := reqType.Field(i)
				// 忽略父级的指针字段
				if field.Type.Kind() == reflect.Ptr {
					continue
				}
				// 跳过的字段
				if isSkipField(field) {
					continue
				}
				// 递归查找父级字段信息
				if field.Anonymous {
					dealAnonymousFieldsPathParameter(field, &pms)
					continue
				}
				dealStructFieldPathParameter(field, &pms)
			}
		}
		return pms
	}

	dealResponse := func(gpath *PathDoc, path *Path) {
		resDataType := ""
		resSchemaName := ""
		if nil != gpath.resParam {
			resDataType, resSchemaName = collComponents(gpath.resParam)
		}
		if resSchemaName == "" {
			path.Responses = NewPathResponse("#/components/schemas/Base")
		} else {
			resTypeRef := fmt.Sprintf("#/components/schemas/%s", resSchemaName)
			componentName := ""
			componentRef := ""
			if resDataType == "array" {
				componentRef = fmt.Sprintf("#/components/schemas/ArrayResponse«%s»", resSchemaName)
				componentName = fmt.Sprintf("ArrayResponse«%s»", resSchemaName)
			} else if resDataType == "map" {
				componentRef = fmt.Sprintf("#/components/schemas/MapResponse«%s»", resSchemaName)
				componentName = fmt.Sprintf("MapResponse«%s»", resSchemaName)
				resDataType = ""
			} else {
				componentRef = fmt.Sprintf("#/components/schemas/Base«%s»", resSchemaName)
				componentName = fmt.Sprintf("Base«%s»", resSchemaName)
			}
			schemas[componentName] = WrapperBaseSchema(resTypeRef, resDataType)
			path.Responses = NewPathResponse(componentRef)
		}
	}

	dealRequest := func(gpath *PathDoc, path *Path) {
		// 设置请求参数类型
		if gpath.reqType == ReqTypeJson {
			// 搜集结构体组件
			reqSchemaName := ""
			if nil != gpath.reqParam {
				_, reqSchemaName = collComponents(gpath.reqParam)
			}
			if reqSchemaName != "" {
				path.RequestBody = NewRequestBodyRef("#/components/schemas/" + reqSchemaName)
			}
		} else if gpath.reqType == ReqTypeForm || gpath.reqType == ReqTypeFormData {
			// 搜集请求参数字段信息
			pms := make([]PathParameter, 0, 10)
			if nil != gpath.reqParam {
				pms = collGetReqStruct(pms, gpath.reqParam)
			}
			if len(gpath.reqParams) > 0 {
				pms = append(pms, gpath.reqParams...)
			}

			names := collx.ArrayMap(pms, func(pm PathParameter) string {
				return pm.Name
			})

			// 解析path类型的参数  /path/:param1/:param2
			for _, s := range strings.Split(gpath.path, "/") {
				arr := strings.Split(s, ":")
				if len(arr) > 1 && !collx.ArrayContains(names, arr[1]) {
					pms = append(pms, NewPathParameter(arr[1], "path", "路径参数", "string", "simple", true))
				}
			}

			path.ContentType = string(gpath.reqType)
			path.Parameters = &pms
		}
	}

	genUrl := func(group *GroupDoc, gpath *PathDoc) string {
		// 拼接绝对路径
		urls := make([]string, 0, 10)
		if group.basePath != "" && group.basePath != "/" {
			if !strings.HasPrefix(group.basePath, "/") {
				urls = append(urls, "/")
			}
			urls = append(urls, group.basePath)
			if !strings.HasPrefix(gpath.path, "/") && !strings.HasSuffix(group.basePath, "/") {
				urls = append(urls, "/")
			}
		}

		urls = append(urls, gpath.path)
		return strings.Join(urls, "")
	}

	// 添加基础response
	schemas["Base"] = WrapperBaseSchema("", "object")

	// 缓存接口分组唯一名称
	tagNameMap := make(map[string]*string)

	// 解析接口路径
	for _, group := range groupDocs {

		if group.Hide {
			continue
		}

		if tagNameMap[group.GroupName] == nil {
			tagNameMap[group.GroupName] = &group.GroupName
			tags = append(tags, Tag{
				Order: group.Order,
				Name:  group.GroupName,
			})
		}

		for _, gpath := range group.Paths {
			// 忽略隐藏的接口
			if gpath.hide {
				continue
			}

			produces := []string{gpath.produces}

			path := Path{
				Tags:        []string{group.GroupName},
				Summary:     gpath.name,
				OperationId: fmt.Sprintf("%sUsing%s", stringx.Slash2Camel(group.basePath+gpath.path), gpath.method),
				Produces:    produces,
				Description: gpath.note,
			}

			if gpath.author != "" || gpath.order != 0 {
				path.Extensions = &PathExtensions{
					Author: gpath.author,
					Order:  gpath.order,
				}
			}

			dealResponse(gpath, &path)
			dealRequest(gpath, &path)

			url := genUrl(group, gpath)

			method := strings.ToLower(gpath.method)
			if pm, ok := paths[url]; ok {
				pm[method] = &path
				paths[url] = pm
			} else {
				pm = map[string]*Path{method: &path}
				paths[url] = pm
			}
		}
	}

	apiDoc.Tags = tags
	apiDoc.Paths = paths
	apiDoc.Components.Schemas = schemas

	return apiDoc
}
