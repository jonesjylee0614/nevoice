package core_service

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/ioc"
	"gofly/pkg/utils/collx"

	"github.com/gin-gonic/gin"
)

type BusinessAuthRoleAccess struct {
	base.DaoImpl[*core.BusinessAuthRoleAccess]
}

func init() {
	ioc.PrepareDao(new(BusinessAuthRoleAccess))
}
func (s *BusinessAuthRoleAccess) GetRoleAccessIdsByUIds(c *gin.Context, uids ...int64) map[int64][]int64 {
	cond := base.NewCond()
	cond.Where(true, "uid", uids)

	list, err := s.List(c, cond)
	if err != nil {
		return nil
	}

	return collx.ArrayToGroupField(list, func(val *core.BusinessAuthRoleAccess) int64 {
		return val.Uid
	}, func(val *core.BusinessAuthRoleAccess) int64 {
		return val.RoleID
	})
}

func (s *BusinessAuthRoleAccess) GetRoleAccessIdsByUId(c *gin.Context, uid int64) []int64 {
	cond := base.NewCond()
	cond.Where(true, "uid", uid)

	var roleIds []int64
	err := s.Pluck(c, cond, "role_id", &roleIds)
	if err != nil {
		return nil
	}

	return roleIds
}

// 添加授权
func (s *BusinessAuthRoleAccess) AppRoleAccess(c *gin.Context, roleids []int64, uid int64) {
	//批量提交
	md := s.GetModel()
	base.GormDb.Table(md.TableName()).Where("uid", uid).Delete(md)

	var saveArr []*core.BusinessAuthRoleAccess
	for _, val := range roleids {
		saveArr = append(saveArr, &core.BusinessAuthRoleAccess{
			Uid:    uid,
			RoleID: val,
		})
	}
	_, _ = s.InsertBatch(c, saveArr)
}
