package errorx

import "fmt"

type FeignError struct {
	*BizError
	AppName string
	TraceId string
}

func (e *FeignError) String() string {
	return fmt.Sprintf("feign调用出错: %s, traceId [%s], %s", e.AppName, e.TraceId, e.err)
}

func NewClientError(code int, msg, appName, traceId string) *FeignError {
	return &FeignError{
		BizError: NewBizCode(code, msg),
		AppName:  appName,
		TraceId:  traceId,
	}
}
