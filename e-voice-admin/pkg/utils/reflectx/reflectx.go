package reflectx

import (
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"gofly/pkg/utils/structx"
	"path/filepath"
	"reflect"
	"regexp"
	"runtime"
	"strings"

	"github.com/gin-gonic/gin"
)

// GetFieldMap 获取对象的字段名和字段值
func GetFieldMap(obj interface{}) map[string]interface{} {
	// 创建一个映射来存储非零字段和值
	result := make(map[string]interface{})

	// 获取对象的值和类型
	v := reflect.ValueOf(obj)
	t := reflect.TypeOf(obj)

	if t.Kind() == reflect.Ptr {
		t = t.Elem()
	}

	// 确保传入的是一个结构体
	if t.Kind() == reflect.Struct {
		// 遍历结构体的字段
		for i := 0; i < v.NumField(); i++ {
			field := t.Field(i)
			value := v.Field(i)
			// 检查字段值是否为零值
			if !IsZeroValue(value) {
				// 如果不是零值，添加到结果映射
				result[field.Name] = value.Interface()
			}
		}
	}
	return result
}

// IsZeroValue 检查字段值是否为零值
func IsZeroValue(v reflect.Value) bool {
	// 零值是默认值，即没有初始化的值
	return v.Interface() == reflect.Zero(v.Type()).Interface()
}

// 通过反射类型获取类型名，如int,[]int,map[string]int,MyStruct
func GetTypeName(t reflect.Type) string {
	switch t.Kind() {
	case reflect.Slice, reflect.Array:
		return "[]" + GetTypeName(t.Elem())
	case reflect.Map:
		return "map[" + GetTypeName(t.Key()) + "]" + GetTypeName(t.Elem())
	case reflect.Ptr:
		return GetTypeName(t.Elem())
	default:
		return t.Name()
	}
}

// 获取结构体的所有字段，包括父级的字段
func GetAllFields(t reflect.Type) []reflect.StructField {
	fields := make([]reflect.StructField, 0)
	t = structx.IndirectType(t)
	if t.Kind() != reflect.Struct {
		return fields
	}
	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		if field.Anonymous {
			fields = append(fields, GetAllFields(field.Type)...)
		} else {
			fields = append(fields, field)
		}
	}
	return fields
}

func GetGinFnPath(fn gin.HandlerFunc) string {
	v := reflect.ValueOf(fn)
	// 获取函数指位
	pc := v.Pointer()
	fnInfo := runtime.FuncForPC(pc)
	return fnInfo.Name()
}

// GetFilepathFromInterface 通过interface{}获取文件绝对路径
func GetFilepathFromInterface(v interface{}, path string) (string, error) {
	t := reflect.TypeOf(v)
	typeName := t.String()

	// 解析文件路径（假设格式为 "文件路径:行号:列号"）
	parts := strings.SplitN(typeName, ":", 3)
	if len(parts) < 1 {
		return "", fmt.Errorf("无法解析文件路径")
	}

	relativePath := parts[0]
	absPath, err := filepath.Abs(relativePath)
	if err != nil {
		return "", err
	}

	re := regexp.MustCompile(`\*[^.]*\.`)
	absPath = re.ReplaceAllString(absPath, path+"/") + ".go"
	absPath = strings.ReplaceAll(absPath, "//", "/")

	return absPath, nil
}

// MethodCommentInfo 定义参数结构
type MethodCommentInfo struct {
	MethodName  string // path/query/header
	FilePath    string
	CommentList []string
}

// GetMethodComments 解析方法参数
func GetMethodComments(filePath, methodName string) (MethodCommentInfo, error) {
	var mci MethodCommentInfo
	mci.FilePath = filePath
	mci.MethodName = methodName
	mci.CommentList = make([]string, 0)
	fset := token.NewFileSet()
	node, err := parser.ParseFile(fset, filePath, nil, parser.ParseComments)
	if err != nil {
		return mci, nil
	}
	for _, decl := range node.Decls {
		if funcDecl, ok := decl.(*ast.FuncDecl); ok && strings.EqualFold(funcDecl.Name.Name, methodName) {
			if funcDecl.Doc != nil {
				list := funcDecl.Doc.List
				for _, commentGroup := range list {
					mci.CommentList = append(mci.CommentList, commentGroup.Text)
				}
			}
		}
	}
	return mci, nil
}
