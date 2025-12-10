package service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"
)

// VoiceHotword 医疗热词服务
type VoiceHotword struct {
	base.DaoImpl[*biz.VoiceHotword]
}

func init() {
	ioc.PrepareDao(new(VoiceHotword))
}

