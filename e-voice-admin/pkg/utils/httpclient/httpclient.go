package httpclient

import (
	"net/http"
	"time"
)

var (
	transport = http.DefaultTransport.(*http.Transport).Clone()

	DefaultClient = &http.Client{
		//  默认超时 5秒
		Timeout:   time.Duration(5) * time.Second,
		Transport: transport,
	}
)

func init() {
	// 设置能复用的连接数，默认只有2个
	transport.MaxIdleConnsPerHost = 100
}

// NewRequest 创建一个请求, 使用默认的客户端，默认超时时间 5 秒
func NewRequest(url string) *RequestWrapper {
	return &RequestWrapper{url: url, client: DefaultClient}
}

// NewRequestWithCustomClient 创建一个自定义http客户端的请求
func NewRequestWithCustomClient(url string, client *http.Client) *RequestWrapper {
	return &RequestWrapper{url: url, client: client}
}

// NewRequestWithTimeout 创建一个请求, 手动设置超时时间 秒
func NewRequestWithTimeout(url string, timeoutSecond int) *RequestWrapper {
	return &RequestWrapper{url: url, client: &http.Client{
		Timeout: time.Duration(timeoutSecond) * time.Second,
	}}
}
