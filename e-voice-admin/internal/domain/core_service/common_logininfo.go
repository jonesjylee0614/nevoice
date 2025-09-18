package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonLogininfo struct {
	base.DaoImpl[*core.CommonLogininfo]
}

func init() {
	ioc.PrepareDao(new(CommonLogininfo))
}
