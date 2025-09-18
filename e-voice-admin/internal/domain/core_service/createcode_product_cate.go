package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CreatecodeProductCate struct {
	base.DaoImpl[*core.CreatecodeProductCate]
}

func init() {
	ioc.PrepareDao(new(CreatecodeProductCate))
}
