package gf

import "testing"

func TestGenValidateCode(t *testing.T) {
	code := GenValidateCode(6)
	t.Log(code)
}
