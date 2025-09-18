package json

import (
	"encoding/json"
	"fmt"
	"strconv"
)

// JsonInt64 自定义 int64 类型,
// 支持string反序列化为int64，支持序列化为string，
// 用于解决json反序列化int64丢失精度的问题
//
// 本类型作用于zorm主键字段，兼容增删改查
//
// 代码中可以用 Int64 、 String 函数快速转换成想要的数据类型
type JsonInt64 int64

// NewJsonInt64 创建一个 JsonInt64
func NewJsonInt64(t int64) *JsonInt64 {
	jsonInt64 := JsonInt64(t)
	return &jsonInt64
}

// NewJsonInt64Slice 创建一个 JsonInt64 数组
func NewJsonInt64Slice(ts ...int64) []*JsonInt64 {
	slice := make([]*JsonInt64, len(ts))
	if len(ts) == 0 {
		return slice
	}
	for i, t := range ts {
		slice[i] = NewJsonInt64(t)
	}
	return slice
}

func (i *JsonInt64) UnmarshalJSON(data []byte) error {
	// 尝试将 JSON 值解析为 string
	var str string
	if err := json.Unmarshal(data, &str); err == nil {
		parseInt, err := strconv.ParseInt(str, 10, 64)
		if err != nil {
			return err
		}
		*i = JsonInt64(parseInt)
		return nil
	}

	// 尝试将 JSON 值解析为 int64
	var v int64
	if err := json.Unmarshal(data, &v); err == nil {
		*i = JsonInt64(v)
		return nil
	}

	return nil
}

func (i *JsonInt64) MarshalJSON() ([]byte, error) {
	return []byte(fmt.Sprintf("\"%v\"", *i)), nil
}

// String 转string
func (i *JsonInt64) String() string {
	return fmt.Sprintf("%v", *i)
}

// Int64 转int64
func (i *JsonInt64) Int64() int64 {
	return int64(*i)
}
func (i *JsonInt64) Int() int {
	return int(*i)
}

func (i *JsonInt64) IsValid() bool {
	return i != nil && *i != 0
}
