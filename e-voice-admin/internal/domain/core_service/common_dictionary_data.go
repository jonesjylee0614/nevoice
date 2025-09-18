package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonDictionaryData struct {
	base.DaoImpl[*core.CommonDictionaryData]
}

func init() {
	ioc.PrepareDao(new(CommonDictionaryData))
}
