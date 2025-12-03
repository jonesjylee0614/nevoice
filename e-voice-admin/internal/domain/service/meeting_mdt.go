package service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"
)

// MeetingMdt MDT会议服务
type MeetingMdt struct {
	base.DaoImpl[*biz.MeetingMdt]
}

func init() {
	ioc.PrepareDao(new(MeetingMdt))
}

