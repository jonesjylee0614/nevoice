package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
	"gofly/pkg/utils/collx"

	"github.com/gin-gonic/gin"
)

type BusinessAuthRole struct {
	base.DaoImpl[*core.BusinessAuthRole]
}

func init() {
	ioc.PrepareDao(new(BusinessAuthRole))
}

func (s *BusinessAuthRole) GetRoleIdsByUid(c *gin.Context, uid int64) []int64 {
	cond := base.NewCond()
	cond.Where(true, "uid", uid)

	list, err := s.List(c, cond)
	if err != nil {
		return nil
	}
	ids := collx.ArrayMap(list, func(val *core.BusinessAuthRole) int64 {
		return val.Id
	})
	return ids
}
func (s *BusinessAuthRole) GetRoleIdsByUIds(c *gin.Context, uids ...int64) map[int64][]int64 {
	cond := base.NewCond()
	cond.Where(true, "uid", uids)

	list, err := s.List(c, cond)
	if err != nil {
		return nil
	}

	return collx.ArrayToGroupField(list, func(val *core.BusinessAuthRole) int64 {
		return val.UID
	}, func(val *core.BusinessAuthRole) int64 {
		return val.Id
	})
}

func (s *BusinessAuthRole) GetRolesByUIds(c *gin.Context, uids ...int64) map[int64][]*core.BusinessAuthRole {
	cond := base.NewCond()
	cond.Where(true, "uid", uids)

	list, err := s.List(c, cond)
	if err != nil {
		return nil
	}

	return collx.ArrayToGroupField(list, func(val *core.BusinessAuthRole) int64 {
		return val.UID
	}, func(val *core.BusinessAuthRole) *core.BusinessAuthRole {
		return val
	})
}

func (s *BusinessAuthRole) GetRolesByUId(c *gin.Context, uid int64) []*core.BusinessAuthRole {
	cond := base.NewCond()
	cond.Where(true, "uid", uid)

	list, err := s.List(c, cond)
	if err != nil {
		return nil
	}
	return list
}

func (s *BusinessAuthRole) GetRolesByIds(c *gin.Context, ids ...int64) []*core.BusinessAuthRole {
	cond := base.NewCond()
	cond.Where(true, "id", ids)

	list, err := s.List(c, cond)
	if err != nil {
		return nil
	}
	return list
}
func (s *BusinessAuthRole) GetRulesByIds(c *gin.Context, ids ...int64) []string {

	cond := base.NewCond()
	cond.Where(true, "id", ids)

	var roles []string
	err := s.Pluck(c, cond, "rules", &roles)
	if err != nil {
		return roles
	}
	return roles
}
