package service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"
)

// VoicePrint 录音范文列表
type VoicePrint struct {
	base.DaoImpl[*biz.VoicePrint]
}

func init() {
	ioc.PrepareDao(new(VoicePrint))
}
