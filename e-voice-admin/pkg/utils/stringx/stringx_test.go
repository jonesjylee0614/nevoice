package stringx

import (
	"strconv"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestTruncateStr(t *testing.T) {
	testCases := []struct {
		data   string
		length int
		want   string
	}{
		{"123一二三", 0, ""},
		{"123一二三", 1, "1"},
		{"123一二三", 3, "123"},
		{"123一二三", 4, "123"},
		{"123一二三", 5, "123"},
		{"123一二三", 6, "123一"},
		{"123一二三", 7, "123一"},
		{"123一二三", 11, "123一二"},
		{"123一二三", 12, "123一二三"},
		{"123一二三", 13, "123一二三"},
	}
	for _, tc := range testCases {
		t.Run(strconv.Itoa(tc.length), func(t *testing.T) {
			got := TruncateStr(tc.data, tc.length)
			require.Equal(t, tc.want, got)
		})
	}
}

func TestSlash2Camel(t *testing.T) {
	str := "cfcg-test/biz/entity/form.TestEntityForm"

	s := Slash2Camel(str)
	t.Log(s)
}

func TestParseSize(t *testing.T) {
	t.Log(ParseSize("10001"))
	t.Log(ParseSize("10m"))
	t.Log(ParseSize("10Mb"))
	t.Log(ParseSize("1g"))
	t.Log(ParseSize("1gb"))
	t.Log(ParseSize("1kb"))
}

func TestParsePathAndGetFilename(t *testing.T) {
	t.Log(ParsePathAndGetFilename("/test/t1/1.jpg"))
	t.Log(ParsePathAndGetFilename("/test/t1/1"))
	t.Log(ParsePathAndGetFilename("test/t1/2.jpg/"))
}
