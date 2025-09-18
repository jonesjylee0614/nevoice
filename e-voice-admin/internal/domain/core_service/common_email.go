package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonEmail struct {
	base.DaoImpl[*core.CommonEmail]
}

func init() {
	ioc.PrepareDao(new(CommonEmail))
}
