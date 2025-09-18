package logx

import (
	"testing"
)

func TestName(t *testing.T) {

	str := "/go/framework/pkg/config@v1.4.1-0.20250115031210-3fd1077bd075/xae/snowflake.go:34"
	result := versionReg.ReplaceAllString(str, "")
	if result != "/go/framework/pkg/config/xae/snowflake.go:34" {
		t.Fatal("替换失败")
	}
	t.Log(result)

	Warnf("123")
}
