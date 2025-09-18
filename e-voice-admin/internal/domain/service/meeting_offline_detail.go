package service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"
)

// MeetingOfflineDetail 离线会议详情
type MeetingOfflineDetail struct {
	base.DaoImpl[*biz.MeetingOfflineDetail]
}

func init() {
	ioc.PrepareDao(new(MeetingOfflineDetail))
}
