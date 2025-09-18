package httpclient

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/cryptox"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"strings"
	"time"
)

type RequestWrapper struct {
	client *http.Client
	url    string
	method string
	body   io.Reader
	header map[string]string
}

func (r *RequestWrapper) Url(url string) *RequestWrapper {
	r.url = url
	return r
}

func (r *RequestWrapper) Header(name, value string) *RequestWrapper {
	if r.header == nil {
		r.header = make(map[string]string)
	}
	r.header[name] = value
	return r
}

func (r *RequestWrapper) Headers(headers map[string]string) *RequestWrapper {
	r.header = headers
	return r
}
func (r *RequestWrapper) AddHeaders(headers map[string]string) *RequestWrapper {
	if r.header == nil {
		r.header = make(map[string]string)
	}
	for k, v := range headers {
		r.header[k] = v
	}
	return r
}

func (r *RequestWrapper) Basic(username, password string) *RequestWrapper {
	if r.header == nil {
		r.header = make(map[string]string)
	}
	str := username + ":" + password
	r.header["Authorization"] = "Basic " + cryptox.Base64Str(str)
	return r
}

func (r *RequestWrapper) Timeout(timeout time.Duration) *RequestWrapper {
	r.client = &http.Client{
		Timeout: timeout,
	}
	return r
}

func (r *RequestWrapper) GetByQuery(queryMap collx.M) *ResponseWrapper {
	params := collx.Map2UrlStr(queryMap)
	if strings.Contains(r.url, "?") {
		r.url += "&" + params
	} else {
		r.url += "?" + params
	}
	return r.Get()
}

func (r *RequestWrapper) Get() *ResponseWrapper {
	r.method = http.MethodGet
	r.body = nil
	return sendRequest(r)
}

func (r *RequestWrapper) Body(body io.Reader) {
	r.body = body
}
func (r *RequestWrapper) Post() *ResponseWrapper {
	r.method = http.MethodPost
	return sendRequest(r)
}

func (r *RequestWrapper) PostJson(body string) *ResponseWrapper {
	buf := bytes.NewBufferString(body)
	r.method = http.MethodPost
	r.body = buf
	if r.header == nil {
		r.header = make(map[string]string)
	}
	r.header["Content-type"] = "application/json"
	return sendRequest(r)
}

func (r *RequestWrapper) PostObj(body any) *ResponseWrapper {
	marshal, err := json.Marshal(body)
	if err != nil {
		return &ResponseWrapper{err: errors.New("解析json obj错误")}
	}
	return r.PostJson(string(marshal))
}

func (r *RequestWrapper) PutObj(body any) *ResponseWrapper {
	marshal, err := json.Marshal(body)
	if err != nil {
		return &ResponseWrapper{err: errors.New("解析json obj错误")}
	}
	buf := bytes.NewBufferString(string(marshal))
	r.method = http.MethodPut
	r.body = buf
	if r.header == nil {
		r.header = make(map[string]string)
	}
	r.header["Content-type"] = "application/json"
	return sendRequest(r)
}
func (r *RequestWrapper) Put() *ResponseWrapper {
	r.method = http.MethodPut
	return sendRequest(r)
}
func (r *RequestWrapper) Head() *ResponseWrapper {
	r.method = http.MethodHead
	return sendRequest(r)
}

func (r *RequestWrapper) Delete() *ResponseWrapper {
	r.method = http.MethodDelete
	r.body = nil
	return sendRequest(r)
}

func (r *RequestWrapper) PostForm(queryMap collx.M) *ResponseWrapper {

	params := collx.Map2UrlStr(queryMap)
	buf := bytes.NewBufferString(params)
	r.method = http.MethodPost
	r.body = buf
	if r.header == nil {
		r.header = make(map[string]string)
	}
	if r.header["Content-Type"] == "" {
		r.header["Content-Type"] = "application/x-www-form-urlencoded"
	}
	return sendRequest(r)
}

func (r *RequestWrapper) PostMultipart(files []MultipartFile, reqParams collx.M) *ResponseWrapper {
	buf := &bytes.Buffer{}
	// 文件写入 buf
	writer := multipart.NewWriter(buf)
	for _, uploadFile := range files {
		var reader io.Reader
		// 如果文件路径不为空，则读取该路径文件，否则使用bytes
		if uploadFile.FilePath != "" {
			file, err := os.Open(uploadFile.FilePath)
			if err != nil {
				return &ResponseWrapper{err: err}
			}
			defer file.Close()
			reader = file
		} else {
			reader = uploadFile.Reader
		}

		part, err := writer.CreateFormFile(uploadFile.FieldName, uploadFile.FileName)
		if err != nil {
			return &ResponseWrapper{err: err}
		}
		_, err = io.Copy(part, reader)
		if err != nil {
			return &ResponseWrapper{err: err}
		}
	}
	// 如果有其他参数，则写入body
	for k, v := range reqParams {
		if err := writer.WriteField(k, anyx.ToString(v)); err != nil {
			return &ResponseWrapper{err: err}
		}
	}
	if err := writer.Close(); err != nil {
		return &ResponseWrapper{err: err}
	}

	r.method = "POST"
	r.body = buf
	if r.header == nil {
		r.header = make(map[string]string)
	}
	r.header["Content-type"] = writer.FormDataContentType()
	return sendRequest(r)
}

func SendMultipartRequest(url string, fieldName string, reader io.Reader, formParams map[string]string) error {
	// 创建缓冲区来保存请求体
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile(fieldName, "test.txt") // "file" 是字段名，"test.txt" 是文件名
	if err != nil {
		return fmt.Errorf("创建文件字段失败: %v", err)
	}
	_, err = io.Copy(part, reader)
	if err != nil {
		return fmt.Errorf("写入文件失败: %v", err)
	}

	// 添加其他表单参数
	for key, value := range formParams {
		err := writer.WriteField(key, value)
		if err != nil {
			return fmt.Errorf("写入表单字段失败: %v", err)
		}
	}

	// 关闭 writer 以确保正确结束边界
	err = writer.Close()
	if err != nil {
		return fmt.Errorf("关闭 writer 失败: %v", err)
	}

	// 发送 POST 请求
	req, err := http.NewRequest("POST", url, body)
	if err != nil {
		return fmt.Errorf("创建请求失败: %v", err)
	}
	req.Header.Set("Content-Type", writer.FormDataContentType()) // 设置正确的 Content-Type

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("发送请求失败: %v", err)
	}
	defer resp.Body.Close()

	return nil
}

func sendRequest(rw *RequestWrapper) *ResponseWrapper {
	respWrapper := &ResponseWrapper{}

	req, err := http.NewRequest(rw.method, rw.url, rw.body)
	if err != nil {
		respWrapper.err = fmt.Errorf("创建请求错误-%s", err.Error())
		return respWrapper
	}
	setRequestHeader(req, rw.header)
	resp, err := rw.client.Do(req)
	r := &ResponseWrapper{resp: resp, err: err}
	return r
}

func setRequestHeader(req *http.Request, header map[string]string) {
	req.Header.Set("User-Agent", "golang/cqliving-framework")
	for k, v := range header {
		req.Header.Set(k, v)
	}
}

func isFailureStatusCode(statusCode int) bool {
	return statusCode < http.StatusOK || statusCode >= http.StatusBadRequest
}

type MultipartFile struct {
	FieldName string    // 字段名
	FileName  string    // 文件名
	FilePath  string    // 文件路径，文件路径不为空，则优先读取文件路径的内容
	Reader    io.Reader // 文件
}

func (f MultipartFile) WriteToPath(path string) error {
	file, err := os.Create(path)
	if err != nil {
		return err
	}
	defer file.Close()
	_, err = io.Copy(file, f.Reader)
	return err
}
