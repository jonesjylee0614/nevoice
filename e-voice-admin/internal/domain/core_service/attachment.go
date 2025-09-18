package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type Attachment struct {
	base.DaoImpl[*core.Attachment]
}

func init() {
	ioc.PrepareDao(new(Attachment))
}
