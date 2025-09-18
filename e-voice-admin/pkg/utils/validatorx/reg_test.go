package validatorx

import (
	"testing"
)

func TestReg(t *testing.T) {
	reg := RegexpMap["username"]
	str := reg.Msg
	t.Log(str)
	t.Log(reg.Reg.String())
}
