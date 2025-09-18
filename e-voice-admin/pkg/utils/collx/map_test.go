package collx

import "testing"

func TestMap(t *testing.T) {
	mp := M{"a": "1", "b": []int{1, 2, 3}, "c": int64(123)}

	str := Map2UrlStr(mp)

	println(str)
}
