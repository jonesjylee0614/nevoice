package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonDictionaryTable struct {
	base.DaoImpl[*core.CommonDictionaryTable]
}

func init() {
	ioc.PrepareDao(new(CommonDictionaryTable))
}
