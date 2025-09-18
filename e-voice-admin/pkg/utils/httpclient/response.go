package httpclient

import (
	"encoding/json"
	"errors"
	"fmt"
	"gofly/pkg/logx"
	"io"
	"net/http"
)

type ResponseWrapper struct {
	resp      *http.Response
	err       error
	bodyBytes []byte
	bodyRead  bool
}

func (r *ResponseWrapper) readBody() error {
	var err error
	if !r.bodyRead {
		r.bodyBytes, err = r.BodyBytes()
	}
	r.bodyRead = true
	return err
}

// 将响应体通过json解析转为指定结构体
func (r *ResponseWrapper) BodyToObj(objPtr any) error {
	err := r.readBody()
	if err != nil {
		return err
	}

	err = json.Unmarshal(r.bodyBytes, &objPtr)
	if err != nil {
		return fmt.Errorf("解析响应体-json解析失败-%s", err.Error())
	}
	return nil
}

// 将响应体转为strings
func (r *ResponseWrapper) BodyToString() (string, error) {
	err := r.readBody()
	if err != nil {
		return "", err
	}
	return string(r.bodyBytes), nil
}

// 将响应体通过json解析转为map
func (r *ResponseWrapper) BodyToMap() (map[string]any, error) {
	var res map[string]any
	return res, r.BodyToObj(&res)
}

// 获取响应体的字节数组
func (r *ResponseWrapper) BodyBytes() ([]byte, error) {
	resp, err := r.GetHttpResp()
	if err != nil {
		return nil, err
	}

	body, err := io.ReadAll(resp.Body)
	defer resp.Body.Close()

	if err != nil {
		return nil, fmt.Errorf("读取响应体数据失败-%s", err.Error())
	}
	return body, err
}

// 获取http响应结果结构体
func (r *ResponseWrapper) GetHttpResp() (*http.Response, error) {
	if r.err != nil {
		return nil, fmt.Errorf("请求失败-%s", r.err.Error())
	}
	if r.resp == nil {
		return nil, errors.New("请求失败-响应结构体为空,请检查请求url等信息")
	}

	statusCode := r.resp.StatusCode
	if isFailureStatusCode(statusCode) {
		logx.Warnf("请求响应状态码为为失败状态: %v", statusCode)
	}

	return r.resp, nil
}
