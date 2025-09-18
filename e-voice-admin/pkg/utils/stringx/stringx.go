package stringx

import (
	"bytes"
	"gofly/pkg/utils/structx"
	"reflect"
	"regexp"
	"strconv"
	"strings"
	"text/template"

	"golang.org/x/text/cases"
	"golang.org/x/text/language"
)

// 逻辑空字符串（由于gorm更新结构体只更新非零值，所以使用该值最为逻辑空字符串，方便更新结构体）
const LogicEmptyStr = "-"

// 是否为逻辑上空字符串
func IsLogicEmpty(str string) bool {
	return str == "" || str == LogicEmptyStr
}

// 可判断中文
func Len(str string) int {
	return len([]rune(str))
}

// 去除字符串左右空字符
func Trim(str string) string {
	return strings.Trim(str, " ")
}

// 去除字符串左右空字符与\n\r换行回车符
func TrimSpaceAndBr(str string) string {
	return strings.TrimFunc(str, func(r rune) bool {
		s := string(r)
		return s == " " || s == "\n" || s == "\r"
	})
}

func SubString(str string, begin, end int) (substr string) {
	// 将字符串的转换成[]rune
	rs := []rune(str)
	lth := len(rs)

	// 简单的越界判断
	if begin < 0 {
		begin = 0
	}
	if begin >= lth {
		begin = lth
	}
	if end > lth {
		end = lth
	}

	// 返回子串
	return string(rs[begin:end])
}

func Camel2Underline(name string) string {
	if name == "" {
		return ""
	}

	temp := strings.Split(name, "_")
	var s string
	for _, v := range temp {
		vv := []rune(v)
		if len(vv) > 0 {
			if vv[0] >= 'a' && vv[0] <= 'z' { //首字母大写
				vv[0] -= 32
			}
			s += string(vv)
		}
	}

	return s
}

// Slash2Camel 斜杠转驼峰 如：/user/info => UserInfo
func Slash2Camel(str string) string {
	words := strings.Split(str, "/")
	var camelCase []string
	for _, word := range words {
		camelCase = append(camelCase, cases.Title(language.English).String(word))
	}
	return strings.Join(camelCase, "")
}

func ToCamel(str string, firstLower bool) string {
	// 根据分隔符 "-" 或 "_" 分割字符串
	parts := strings.FieldsFunc(str, func(r rune) bool {
		return r == '-' || r == '_'
	})

	// 拼接首字母大写的单词
	var result strings.Builder
	for i, part := range parts {
		if part == "" {
			continue
		}
		// 将单词的首字母大写
		upperFirst := ""
		if i == 0 && firstLower {
			upperFirst = strings.ToLower(string(part[0])) + part[1:]
		} else {
			upperFirst = strings.ToUpper(string(part[0])) + part[1:]
		}
		result.WriteString(upperFirst)
	}

	// 返回转换后的驼峰命名字符串
	return result.String()

}

// 首字母小写驼峰
func ToLowerCamel(str string) string {
	return ToCamel(str, true)
}

// 首字母大写驼峰
func ToUpperCamel(str string) string {
	return ToCamel(str, false)
}

func UnicodeIndex(str, substr string) int {
	// 子串在字符串的字节位置
	result := strings.Index(str, substr)
	if result >= 0 {
		// 获得子串之前的字符串并转换成[]byte
		prefix := []byte(str)[0:result]
		// 将子串之前的字符串转换成[]rune
		rs := []rune(string(prefix))
		// 获得子串之前的字符串的长度，便是子串在字符串的字符位置
		result = len(rs)
	}

	return result
}

// 字符串模板解析
func TemplateResolve(temp string, data any) string {
	t, _ := template.New("string-temp").Parse(temp)
	var tmplBytes bytes.Buffer

	err := t.Execute(&tmplBytes, data)
	if err != nil {
		panic(err)
	}
	return tmplBytes.String()
}

func ReverStrTemplate(temp, str string, res map[string]any) {
	index := UnicodeIndex(temp, "{")
	ei := UnicodeIndex(temp, "}") + 1
	next := Trim(temp[ei:])
	nextContain := UnicodeIndex(next, "{")
	nextIndexValue := next
	if nextContain != -1 {
		nextIndexValue = SubString(next, 0, nextContain)
	}
	key := temp[index+1 : ei-1]
	// 如果后面没有内容了，则取字符串的长度即可
	var valueLastIndex int
	if nextIndexValue == "" {
		valueLastIndex = Len(str)
	} else {
		valueLastIndex = UnicodeIndex(str, nextIndexValue)
	}
	value := Trim(SubString(str, index, valueLastIndex))
	res[key] = value
	// 如果后面的还有需要解析的，则递归调用解析
	if nextContain != -1 {
		ReverStrTemplate(next, Trim(SubString(str, UnicodeIndex(str, value)+Len(value), Len(str))), res)
	}
}

func TruncateStr(s string, length int) string {
	if length >= len(s) {
		return s
	}
	var last int
	for i := range s {
		if i > length {
			break
		}
		last = i
	}
	return s[:last]
}

func ParseInt64(numStr string) int64 {
	numStr = strings.Trim(numStr, " ")
	if "" == numStr {
		return 0
	}
	res, _ := strconv.ParseInt(numStr, 10, 64)
	return res
}

var sizePattern = regexp.MustCompile(`(?i)^(\d+)([kmg]b?)?$`)

// 正则解析字符串  100MB 100KB 100M 100G 10240 忽略大小写，转换为字节
func ParseSize(sizeStr string) int64 {
	sizeStr = strings.Trim(sizeStr, " ")
	matches := sizePattern.FindStringSubmatch(sizeStr)
	if matches == nil {
		return 0
	}

	value := ParseInt64(matches[1])

	unit := strings.ToLower(matches[2])
	switch unit {
	case "kb", "k":
		return value * 1024
	case "mb", "m":
		return value * 1024 * 1024
	case "gb", "g":
		return value * 1024 * 1024 * 1024
	default:
		return value
	}
}

// 解析路径并提取文件名
func ParsePathAndGetFilename(path string) (folder string, fixedPath string, filename string) {
	// 确保路径以 '/' 开头
	if !strings.HasPrefix(path, "/") {
		path = "/" + path
	}

	// 去除路径末尾的 '/'
	path = strings.TrimSuffix(path, "/")

	// 提取文件名
	parts := strings.Split(path, "/")
	filename = parts[len(parts)-1]
	// 提取文件夹路径
	folder = strings.Join(parts[:len(parts)-1], "/")

	fixedPath = path

	return folder, fixedPath, filename
}

func Contains(srcStr, subStr string) bool {
	if srcStr == "" || subStr == "" {
		return false
	}
	return strings.Contains(srcStr, subStr)
}

// GetPathPrefix 从字符串中提取路径前缀 如 /a/b/c 返回 /a
func GetPathPrefix(s string) string {
	// 使用 strings.SplitN 分割字符串，最多分割两次
	parts := strings.SplitN(s, "/", 12)
	if len(parts) < 2 {
		return ""
	}
	// 返回前两个部分，中间加上 /
	return "/" + parts[1]
}

// 把示例值转换为给定的类型
func ParseByType(tp reflect.Type, value string) interface{} {
	value = strings.TrimSpace(value)

	switch structx.IndirectType(tp).Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		parseInt, err := strconv.ParseInt(value, 10, 64)
		if err != nil {
			return 0
		}
		return parseInt
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		parseInt, err := strconv.ParseUint(value, 10, 64)
		if err != nil {
			return 0
		}
		return parseInt
	case reflect.Float32, reflect.Float64:
		float, err := strconv.ParseFloat(value, 64)
		if err != nil {
			return 0.0
		}
		return float
	case reflect.String:
		return value
	case reflect.Bool:
		parseBool, err := strconv.ParseBool(value)
		if err != nil {
			return false
		}
		return parseBool
	default:
		return nil
	}
}
