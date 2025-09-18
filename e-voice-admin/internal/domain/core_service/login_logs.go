package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type LoginLog struct {
	base.DaoImpl[*core.LoginLog]
}

func init() {
	ioc.PrepareDao(new(LoginLog))
}
