package openapi

import (
	"reflect"
	"testing"
)

func TestNewRequestBody(t *testing.T) {

	u := NewRequestBodyRef("testref")
	u2 := NewRequestBodyItem("testref", "itemType", "itemFormat")

	t.Log(u)
	t.Log(u2)
}

type User struct {
	Name string
}

func TestArrayType(t *testing.T) {

	list := make([]User, 1)
	list = append(list, User{Name: "test"})

	types := reflect.TypeOf(list)

	t.Log(types.String())
}
