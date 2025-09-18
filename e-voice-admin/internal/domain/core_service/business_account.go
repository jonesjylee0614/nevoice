package core_service

import (
	"context"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
)

type BusinessAccount struct {
	base.DaoImpl[*core.BusinessAccount]
}

func init() {
	ioc.PrepareDao(new(BusinessAccount))
}

func (s *BusinessAccount) GetByAk(c context.Context, ak string) *core.BusinessAccount {

	cond := base.NewCond()
	cond.Where(true, "ak", ak)
	list, err := s.List(c, cond)
	if err != nil {
		return nil
	}
	if len(list) > 0 {
		return list[0]
	}
	return nil
}
