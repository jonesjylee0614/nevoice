package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonPictureCate struct {
	base.DaoImpl[*core.CommonPictureCate]
}

func init() {
	ioc.PrepareDao(new(CommonPictureCate))
}
