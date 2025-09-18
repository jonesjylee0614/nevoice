package test

import (
	"gofly/pkg/json"
	"gofly/pkg/utils/structx"
	"testing"
	"time"
)

type TestStruct struct {
	TestTime1  *json.JsonTime         `json:"testTime1" default:"2018-12-01 12:30:01" `
	TestInt    int                    `json:"testInt" default:"2"`
	TestBool   bool                   `json:"testBool" default:"true"`
	TestFloat  float64                `json:"testFloat" default:"2.2"`
	TestString string                 `json:"testString" default:"string1"`
	TestArray  []string               `json:"testArray" default:"[1,2,3]"`
	TestMap    map[string]interface{} `json:"testMap" default:"{a:1,b:2}"`
	TestTime2  time.Time              `json:"testTime2" default:"2018-12-01 12:30:01" `
}

func TestName(t *testing.T) {
	s := &TestStruct{}
	structx.SetDefaults(s)
	t.Log(s)

}
