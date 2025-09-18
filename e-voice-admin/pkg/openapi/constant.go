package openapi

type ReqType string

const (
	ReqTypeJson     ReqType = "application/json"
	ReqTypeForm     ReqType = "application/x-www-form-urlencoded"
	ReqTypeFormData ReqType = "multipart/form-data"

	ProduceJson = "application/json"
)
