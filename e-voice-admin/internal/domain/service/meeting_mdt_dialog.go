package service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"
)

// MeetingMdtDialog MDT会议对话服务
type MeetingMdtDialog struct {
	base.DaoImpl[*biz.MeetingMdtDialog]
}

func init() {
	ioc.PrepareDao(new(MeetingMdtDialog))
}

