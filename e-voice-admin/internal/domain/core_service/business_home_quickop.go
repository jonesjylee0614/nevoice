package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type BusinessHomeQuickop struct {
	base.DaoImpl[*core.BusinessHomeQuickop]
}

func init() {
	ioc.PrepareDao(new(BusinessHomeQuickop))
}
