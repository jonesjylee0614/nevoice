package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonGeneratecodeField struct {
	base.DaoImpl[*core.CommonGeneratecodeField]
}

func init() {
	ioc.PrepareDao(new(CommonGeneratecodeField))
}
