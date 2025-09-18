package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonPicture struct {
	base.DaoImpl[*core.CommonPicture]
}

func init() {
	ioc.PrepareDao(new(CommonPicture))
}
