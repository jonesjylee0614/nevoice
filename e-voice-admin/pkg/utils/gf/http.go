package gf

import (
	"gofly/pkg/utils/httpclient"
	"io"
)

// NewHttpRequest 创建一个HTTP请求
func NewHttpRequest(url string) *httpclient.RequestWrapper {
	return httpclient.NewRequest(url)
}

// MustReadAll 读取所有数据，如果出错则panic
func MustReadAll(reader io.Reader) []byte {
	data, err := io.ReadAll(reader)
	if err != nil {
		panic(err)
	}
	return data
}
