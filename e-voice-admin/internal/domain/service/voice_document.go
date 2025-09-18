package service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"
)

// VoiceDocument 录音范文列表
type VoiceDocument struct {
	base.DaoImpl[*biz.VoiceDocument]
}

func init() {
	ioc.PrepareDao(new(VoiceDocument))
}
