package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type BusinessAuthDept struct {
	base.DaoImpl[*core.BusinessAuthDept]
}

func init() {
	ioc.PrepareDao(new(BusinessAuthDept))
}
