package collx

import (
	"encoding/json"
	"gofly/pkg/utils/dt"
	"reflect"
	"strings"
)

// 数组比较
// 依次返回，新增值，删除值，以及不变值
func ArrayCompare[T comparable](newArr []T, oldArr []T) ([]T, []T, []T) {
	newSet := make(map[T]bool)
	oldSet := make(map[T]bool)

	// 将新数组和旧数组的元素分别添加到对应的哈希集合中
	for _, elem := range newArr {
		newSet[elem] = true
	}
	for _, elem := range oldArr {
		oldSet[elem] = true
	}

	var (
		added      []T
		deleted    []T
		unmodified []T
	)

	// 遍历新数组，根据元素是否存在于旧数组进行分类
	for _, elem := range newArr {
		if oldSet[elem] {
			unmodified = append(unmodified, elem)
		} else {
			added = append(added, elem)
		}
	}

	// 遍历旧数组，找出被删除的元素
	for _, elem := range oldArr {
		if !newSet[elem] {
			deleted = append(deleted, elem)
		}
	}

	return added, deleted, unmodified
}

// 判断数组中是否含有指定元素
func ArrayContains[T comparable](arr []T, el T) bool {
	for _, v := range arr {
		if v == el {
			return true
		}
	}
	return false
}

// 判断数组中是否含有任一
func ArrayContainsAny[T comparable](src []T, target []T) bool {
	for _, v := range src {
		if ArrayContains(target, v) {
			return true
		}
	}
	return false
}

func ArrayContainAll[T comparable](src []T, target []T) bool {
	// 判断src包含target中所有对象
	if len(src) < len(target) {
		return false
	}
	for _, v := range target {
		if !ArrayContains(src, v) {
			return false
		}
	}

	return true
}

// 数组转为map
// @param keyFunc key的主键
func ArrayToMap(slice interface{}) []dt.Map {
	// 获取切片的反射值
	sliceValue := reflect.ValueOf(slice)
	if sliceValue.Kind() != reflect.Slice {
		return nil
	}

	// 获取切片元素的类型
	elemType := sliceValue.Type().Elem()
	if elemType.Kind() != reflect.Struct && elemType.Kind() != reflect.Ptr {
		return nil
	}

	// 创建结果 map 切片
	resultMapSlice := make([]dt.Map, sliceValue.Len())

	// 遍历切片中的每个元素
	for i := 0; i < sliceValue.Len(); i++ {
		elem := sliceValue.Index(i)
		if elem.Kind() == reflect.Ptr {
			elem = elem.Elem()
		}
		elemMap, _ := structToMapViaJSON(elem.Interface())
		resultMapSlice[i] = elemMap
	}

	return resultMapSlice
}

// ToMapByKey 将 slice 转换为 map，key 由元素的指定字段生成
func ToMapByKey[T any, K comparable, V any](slice []T, keyFunc func(T) (K, V)) map[K]V {
	result := make(map[K]V, len(slice))
	for _, item := range slice {
		k, v := keyFunc(item)
		result[k] = v
	}
	return result
}

func struct2Map(elem reflect.Value, elemMap dt.Map) {
	// 遍历结构体的每个字段
	for j := 0; j < elem.NumField(); j++ {
		field := elem.Type().Field(j)
		// 如果字段是结构体，则递归调用
		if field.Type.Kind() == reflect.Struct {
			struct2Map(elem.Field(j), elemMap)
			continue
		}
		jsonTag := field.Tag.Get("json")
		if jsonTag == "" {
			continue
		}
		elemMap[jsonTag] = elem.Field(j).Interface()
	}
}

func structToMapViaJSON(item interface{}) (map[string]interface{}, error) {
	result := make(map[string]interface{})

	// 先转换为 JSON bytes
	jsonBytes, err := json.Marshal(item)
	if err != nil {
		return nil, err
	}

	// 再将 JSON bytes 解析为 map
	err = json.Unmarshal(jsonBytes, &result)
	if err != nil {
		return nil, err
	}

	return result, nil
}

// 数组映射，即将一数组元素通过映射函数转换为另一数组
func ArrayMap[T any, K comparable](arr []T, mapFunc func(val T) K) []K {
	res := make([]K, len(arr))
	for i, val := range arr {
		res[i] = mapFunc(val)
	}
	return res
}

func Unique[T comparable](slice []T) []T {
	m := make(map[T]struct{})
	var res []T
	for _, t := range slice {
		if _, ok := m[t]; !ok {
			m[t] = struct{}{}
			res = append(res, t)
		}
	}
	return res
}

// 将数组或切片按固定大小分割成小数组
func ArrayChunk[T any](arr []T, chunkSize int) [][]T {
	var chunks [][]T
	for i := 0; i < len(arr); i += chunkSize {
		end := i + chunkSize
		if end > len(arr) {
			end = len(arr)
		}
		chunks = append(chunks, arr[i:end])
	}
	return chunks
}

// 将数组切割为指定个数的子数组，并尽可能均匀
func ArraySplit[T any](arr []T, numGroups int) [][]T {
	if numGroups > len(arr) {
		numGroups = len(arr)
	}
	// 创建一个存放子数组的切片
	subArrays := make([][]T, numGroups)

	if 0 == numGroups {
		return subArrays
	}
	// 计算每个子数组的大小
	size := len(arr) / numGroups
	remainder := len(arr) % numGroups

	// 分割数组为子数组
	start := 0
	for i := range subArrays {
		subSize := size
		if i < remainder {
			subSize++
		}
		subArrays[i] = arr[start : start+subSize]
		start += subSize
	}

	return subArrays
}

// reduce操作
func ArrayReduce[T any, V any](arr []T, initialValue V, reducer func(V, T) V) V {
	value := initialValue
	for _, a := range arr {
		value = reducer(value, a)
	}
	return value
}

// 数组元素移除操作
func ArrayRemoveFunc[T any](arr []T, isDeleteFunc func(T) bool) []T {
	var newArr []T
	for _, a := range arr {
		if !isDeleteFunc(a) {
			newArr = append(newArr, a)
		}
	}
	return newArr
}

// 数组元素去重
func ArrayDeduplicate[T comparable](arr []T) []T {
	encountered := map[T]bool{}
	result := []T{}

	for v := range arr {
		if !encountered[arr[v]] {
			encountered[arr[v]] = true
			result = append(result, arr[v])
		}
	}

	return result
}

// ArrayAnyMatches 给定字符串是否包含指定数组中的任意字符串， 如：["time", "date"] , substr : timestamp，返回true
func ArrayAnyMatches(arr []string, subStr string) bool {
	for _, itm := range arr {
		if strings.Contains(subStr, itm) {
			return true
		}
	}
	return false
}

// ArrayAnyContains 给定数组是否包含指定字符串
func ArrayAnyContains(arr []string, subStr string) bool {
	for _, itm := range arr {
		if itm == subStr {
			return true
		}
	}
	return false
}

// ArrayFilter 过滤函数，根据提供的条件函数将切片中的元素进行过滤
func ArrayFilter[T any](array []T, fn func(T) bool) []T {
	var filtered []T
	for _, val := range array {
		if fn(val) {
			filtered = append(filtered, val)
		}
	}
	return filtered
}

// ArrayUnique 根据对象的指定字段对切片进行去重
// T 为切片元素类型
// K 为用于去重的字段类型（必须是可比较的类型）
// keyFunc 是一个函数，用于从对象中提取用于去重的键
func ArrayUnique[T any, K comparable](arr []T, keyFunc func(T) K) []T {
	// 创建一个map用于存储已经出现过的key
	seen := make(map[K]struct{})
	// 创建结果切片
	result := make([]T, 0)

	// 遍历原始切片
	for _, item := range arr {
		// 获取用于去重的key
		key := keyFunc(item)
		// 如果key没有出现过，则添加到结果中
		if _, exists := seen[key]; !exists {
			seen[key] = struct{}{}
			result = append(result, item)
		}
	}

	return result
}

// 以自定义字段分组
func ArrayToGroup[T any, K comparable](arr []T, keyFunc func(T) K) map[K][]T {
	res := make(map[K][]T)
	for _, val := range arr {
		key := keyFunc(val)
		if _, ok := res[key]; !ok {
			res[key] = make([]T, 0)
		}
		res[key] = append(res[key], val)
	}
	return res
}

// 以字段为key，值为value分组
func ArrayToGroupField[T any, K comparable, V comparable](arr []T, keyFunc func(T) K, valueFunc func(T) V) map[K][]V {
	res := make(map[K][]V)
	for _, val := range arr {
		key := keyFunc(val)
		if _, ok := res[key]; !ok {
			res[key] = make([]V, 0)
		}
		res[key] = append(res[key], valueFunc(val))
	}
	return res
}
