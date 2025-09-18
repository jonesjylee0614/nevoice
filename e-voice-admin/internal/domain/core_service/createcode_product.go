package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CreatecodeProduct struct {
	base.DaoImpl[*core.CreatecodeProduct]
}

func init() {
	ioc.PrepareDao(new(CreatecodeProduct))
}
