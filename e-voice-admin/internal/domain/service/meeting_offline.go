package service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"
)

// MeetingOffline 录音范文列表
type MeetingOffline struct {
	base.DaoImpl[*biz.MeetingOffline]
}

func init() {
	ioc.PrepareDao(new(MeetingOffline))
}
