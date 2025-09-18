package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonGeneratecode struct {
	base.DaoImpl[*core.CommonGeneratecode]
}

func init() {
	ioc.PrepareDao(new(CommonGeneratecode))
}
