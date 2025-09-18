package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonMessage struct {
	base.DaoImpl[*core.CommonMessage]
}

func init() {
	ioc.PrepareDao(new(CommonMessage))
}
