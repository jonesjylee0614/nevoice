package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type CommonVerifyCode struct {
	base.DaoImpl[*core.CommonVerifyCode]
}

func init() {
	ioc.PrepareDao(new(CommonVerifyCode))
}
