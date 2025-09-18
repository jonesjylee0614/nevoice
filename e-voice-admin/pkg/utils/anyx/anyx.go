package anyx

import (
	"encoding/json"
	"fmt"
	"reflect"
	"strconv"
	"time"
)

func IsBlank(value any) bool {
	if value == nil {
		return true
	}
	rValue := reflect.ValueOf(value)
	if rValue.Kind() == reflect.Ptr {
		rValue = rValue.Elem()
	}

	switch rValue.Kind() {
	case reflect.String:
		return rValue.Len() == 0
	case reflect.Bool:
		return !rValue.Bool()
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return rValue.Int() == 0
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		return rValue.Uint() == 0
	case reflect.Float32, reflect.Float64:
		return rValue.Float() == 0
	case reflect.Interface:
		return rValue.IsNil()
	case reflect.Slice:
		return rValue.IsNil() || rValue.Len() == 0
	case reflect.Invalid:
		return true
	default:
		return reflect.DeepEqual(rValue.Interface(), reflect.Zero(rValue.Type()).Interface())
	}
}

// any to string
func ToString(value any) string {
	// interface 转 string
	if value == nil {
		return ""
	}

	switch it := value.(type) {
	case string:
		return it
	case error:
		return it.Error()
	case float64:
		return strconv.FormatFloat(it, 'f', -1, 64)
	case float32:
		return strconv.FormatFloat(float64(it), 'f', -1, 64)
	case int:
		return strconv.Itoa(it)
	case uint, int8, uint8, int16, uint16, int32, uint32, int64, uint64:
		return fmt.Sprintf("%d", it)
	case []byte:
		return string(it)
	default:
		newValue, _ := json.Marshal(value)
		return string(newValue)
	}
}

// DeepZero 初始化对象
// 如 T 为基本类型或结构体，则返回零值
// 如 T 为指向基本类型或结构体的指针，则返回指向零值的指针
func DeepZero[T any]() T {
	var data T
	typ := reflect.TypeOf(data)
	kind := typ.Kind()
	if kind == reflect.Pointer {
		return reflect.New(typ.Elem()).Interface().(T)
	}
	return data
}

// IsNumber 检查一个 interface{} 是否是数字类型
func IsNumber(value interface{}) bool {
	switch value.(type) {
	case int, int8, int16, int32, int64:
		return true
	case uint, uint8, uint16, uint32, uint64:
		return true
	case float32, float64:
		return true
	default:
		return false
	}
}
func indirect(a interface{}) interface{} {
	if a == nil {
		return nil
	}
	if t := reflect.TypeOf(a); t.Kind() != reflect.Ptr {
		// Avoid creating a reflect.Value if it's not a pointer.
		return a
	}
	v := reflect.ValueOf(a)
	for v.Kind() == reflect.Ptr && !v.IsNil() {
		v = v.Elem()
	}
	return v.Interface()
}
func toInt(v interface{}) (int, bool) {
	switch v := v.(type) {
	case int:
		return v, true
	case time.Weekday:
		return int(v), true
	case time.Month:
		return int(v), true
	default:
		return 0, false
	}
}

// ToIntE casts an interface to an int type.
func ToIntE(i interface{}) (int, error) {
	i = indirect(i)

	intv, ok := toInt(i)
	if ok {
		return intv, nil
	}

	switch s := i.(type) {
	case int64:
		return int(s), nil
	case int32:
		return int(s), nil
	case int16:
		return int(s), nil
	case int8:
		return int(s), nil
	case uint:
		return int(s), nil
	case uint64:
		return int(s), nil
	case uint32:
		return int(s), nil
	case uint16:
		return int(s), nil
	case uint8:
		return int(s), nil
	case float64:
		return int(s), nil
	case float32:
		return int(s), nil
	case string:
		v, err := strconv.ParseInt(trimZeroDecimal(s), 0, 0)
		if err == nil {
			return int(v), nil
		}
		return 0, fmt.Errorf("unable to cast %#v of type %T to int64", i, i)
	case json.Number:
		return ToIntE(string(s))
	case bool:
		if s {
			return 1, nil
		}
		return 0, nil
	case nil:
		return 0, nil
	default:
		return 0, fmt.Errorf("unable to cast %#v of type %T to int", i, i)
	}
}
func trimZeroDecimal(s string) string {
	var foundZero bool
	for i := len(s); i > 0; i-- {
		switch s[i-1] {
		case '.':
			if foundZero {
				return s[:i-1]
			}
		case '0':
			foundZero = true
		default:
			return s
		}
	}
	return s
}

// ToInt casts an interface to an int type.
func ToInt(i interface{}) int {
	v, _ := ToIntE(i)
	return v
}

func ToInt64(i interface{}) int64 {
	v, _ := ToIntE(i)
	return int64(v)
}

// IsString 检查一个 interface{} 是否是字符串类型
func IsString(value interface{}) bool {
	switch value.(type) {
	case string:
		return true
	default:
		return false
	}
}

// IsSlice 是否是切片类型
func IsSlice(value interface{}) bool {
	return reflect.ValueOf(value).Kind() == reflect.Slice
}

func IsMap(value interface{}) bool {
	return reflect.ValueOf(value).Kind() == reflect.Map
}

func IsStruct(value interface{}) bool {
	return reflect.ValueOf(value).Kind() == reflect.Struct
}

// IsPointer 是否是指针
func IsPointer(value interface{}) bool {
	return reflect.ValueOf(value).Kind() == reflect.Pointer
}

// IsArray 是否是数组，数组的大小是固定的，如：[3]int{1,2,3}，而切片则可以动态地调整其容量，如：[]int{1,2,3}
func IsArray(value interface{}) bool {
	return reflect.ValueOf(value).Kind() == reflect.Array
}
