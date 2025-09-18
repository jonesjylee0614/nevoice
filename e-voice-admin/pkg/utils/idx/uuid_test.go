package idx

import (
	"testing"
)

func TestUuid(t *testing.T) {
	str := UuidStr()
	t.Log(str)

}

func TestSha1(t *testing.T) {
	str := Sha1("6ba7b810-9dad-11d1-80b4-00c04fd430c8", []byte("123"))
	t.Log(str)
}
