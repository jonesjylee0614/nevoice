package idx

import (
	"gofly/pkg/logx"
	"gofly/pkg/utils/cryptox"

	"github.com/google/uuid"
)

func UuidStr() string {
	id, _ := uuid.NewV7()
	return id.String()
}

// UuidMd5 uuid 生成的前缀有时候是一样的，在需要取短码的时候，用md5加密一下，可以解决这个问题
func UuidMd5() string {
	return cryptox.Md5(UuidStr())
}

func Uuid() uuid.UUID {
	id, _ := uuid.NewV7()
	return id
}

func Sha1(uuidKey string, data []byte) string {
	space, err := uuid.Parse(uuidKey)
	if err != nil {
		logx.Error("转换uuid字符串出错", err)
		return ""
	}
	return uuid.NewSHA1(space, data).String()
}
