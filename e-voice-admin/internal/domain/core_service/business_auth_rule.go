package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/gf"
	"sort"

	"github.com/gin-gonic/gin"
)

type BusinessAuthRule struct {
	base.DaoImpl[*core.BusinessAuthRule]
}

func init() {
	ioc.PrepareDao(new(BusinessAuthRule))
}

// 获取子菜单包含的父级ID
func (s *BusinessAuthRule) GetRulesID(c *gin.Context, ids []int64) []int64 {

	res := append([]int64{}, ids...)

	rules, _ := s.ListByIds(c, ids)
	pids := collx.ArrayMap(rules, func(val *core.BusinessAuthRule) int64 {
		return val.Pid
	})

	for len(pids) > 0 {
		rules, _ = s.ListByIds(c, pids)
		pids = collx.ArrayMap(rules, func(val *core.BusinessAuthRule) int64 {
			return val.Pid
		})
		res = append(res, pids...)
	}

	// 去重
	res = collx.Unique(res)

	return res
}

func (s *BusinessAuthRule) ListByMenuIds(c *gin.Context, menuIds []string) ([]*core.BusinessAuthRule, []*core.BusinessAuthRule, error) {
	cond := s.baseCond()
	var rules []*core.BusinessAuthRule

	if !collx.ArrayContains(menuIds, "*") {
		roleIds := gf.RulesMerge(menuIds)
		var selectedIds []int64
		// 递归查询父级资源，如果是菜单，给了按钮，则默认能有菜单权限
		s.ListAllParents(c, roleIds, selectedIds, &rules)
	} else {
		// 直接查询
		rules, _ = s.List(c, cond)
	}
	// 菜单资源
	menus := collx.ArrayRemoveFunc(rules, func(val *core.BusinessAuthRule) bool {
		return val.Type == 2
	})
	// 按钮资源
	perms := collx.ArrayFilter(rules, func(val *core.BusinessAuthRule) bool {
		return val.Type == 2
	})
	sort.Slice(menus, func(i, j int) bool {
		return menus[i].OrderNo < menus[j].OrderNo
	})
	return menus, perms, nil
}
func (s *BusinessAuthRule) ListPermsByRuleIds(c *gin.Context, menuIds []string) ([]string, error) {
	cond := s.baseCond()
	cond.Where(true, "type", 2)

	roleIds := gf.RulesMerge(menuIds)
	cond.Where(true, "id", roleIds)
	list, err := s.List(c, cond)
	perms := collx.ArrayMap(list, func(val *core.BusinessAuthRule) string {
		return val.Permission
	})
	return perms, err
}

func (s *BusinessAuthRule) baseCond() *base.Cond {
	cond := base.NewCond()
	cond.Where(true, "status", 0)
	cond.Where(true, "type", 0, 1, 2)
	cond.Order = "orderNo asc"
	return cond
}

func (s *BusinessAuthRule) ListAllParents(c *gin.Context, roleIds []int64, selectedIds []int64, rules *[]*core.BusinessAuthRule) {

	roleIds = collx.ArrayRemoveFunc(roleIds, func(val int64) bool {
		return collx.ArrayContains(selectedIds, val)
	})
	if len(roleIds) == 0 {
		return
	}
	cond := s.baseCond()
	// 递归查询所有父级菜单
	cond.Where(true, "id", roleIds)
	menus, _ := s.List(c, cond)

	*rules = append(*rules, menus...)
	selectedIds = append(selectedIds, roleIds...)
	var ids []int64
	for _, menu := range menus {
		if !collx.ArrayContains(selectedIds, menu.Pid) {
			ids = append(ids, menu.Pid)
		}
	}

	s.ListAllParents(c, ids, selectedIds, rules)

}
