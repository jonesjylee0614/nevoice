package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type BusinessAttachment struct {
	base.DaoImpl[*core.BusinessAttachment]
}

func init() {
	ioc.PrepareDao(new(BusinessAttachment))
}
