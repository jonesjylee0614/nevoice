package jsonx

import (
	"encoding/json"
	"gofly/pkg/logx"
)

func Marshal(v interface{}) string {
	marshal, err := json.Marshal(v)
	if err != nil {
		logx.Error("json marshal error", err)
		return ""
	}
	return string(marshal)
}
