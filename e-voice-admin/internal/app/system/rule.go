package system

import (
	"cmp"
	"context"
	"encoding/json"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/logx"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/redis"
	"gofly/pkg/utils/results"
	"strconv"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Rule struct {
	redis.BaseRedis
	svc                *core_service.BusinessAuthRule `inject:""`
	BusinessAccountSvc *core_service.BusinessAccount  `inject:""`
}

var (
	permHKey = "rule:perms"
)

// 初始化生成路由
func init() {
	gf.RegisterRoute(&Rule{})
}

func (s *Rule) PostInject() {
	logx.Infof("刷新按钮权限缓存")

	cond := base.NewCond()
	cond.Where(true, "type", 2)
	list, err := s.svc.List(nil, cond)
	assert.ErrIsNilAppendErr(err, "获取按钮权限列表失败")

	m := collx.ToMapByKey(list, func(t *core.BusinessAuthRule) (string, string) {
		marshal, _ := json.Marshal(t)
		return strconv.FormatInt(t.Id, 10), string(marshal)
	})

	s.RedisClient.Del(context.Background(), permHKey)
	s.RedisClient.HMSet(context.Background(), permHKey, m)
}

// Get_list 1获取列表 /system/rule/get_list
func (s *Rule) Get_list(c *gin.Context) {
	list, err := s.svc.List(c, &base.Cond{
		Order: "orderNo asc",
	})
	assert.ErrIsNilAppendErr(err, "获取列表失败")

	for _, val := range list {
		if val.Title == "" {
			val.Title = val.Locale
		}
	}
	menuList := gf.GetRuleTreeArray(collx.ArrayToMap(list), 0, "")
	results.Success(c, "获取全部菜单列表", menuList, nil)
}

// Get_parent 2获取列表-获取选项列表 /system/rule/get_parent
func (s *Rule) Get_parent(c *gin.Context) {

	id := c.DefaultQuery("id", "0")

	cond := base.NewCond()
	cond.Where(true, "type", 0, 1)
	cond.Where(true, "id != ?", id)
	cond.Fields = "id,pid,title,locale,routePath"
	cond.Order = "orderNo asc"

	list, err := s.svc.List(c, cond)

	assert.ErrIsNilAppendErr(err, "获取选项列表失败")

	for _, val := range list {
		val.Title = cmp.Or(val.Title, val.Locale)
	}
	menuList := gf.GetMenuChildrenArray(collx.ArrayToMap(list), 0, "pid")
	results.Success(c, "菜单父级数据！", menuList, nil)

}

// Save 3保存、编辑菜单 /system/rule/save
func (s *Rule) Save(c *gin.Context) {
	//获取post传过来的data

	entity := gf.ReqBody(c, &core.BusinessAuthRule{})
	user := s.BusinessAccountSvc.GetSysUser(c)
	entity.UID = user.Id

	res, err := s.svc.InsertOrUpdate(c, entity)

	// 保存缓存
	if entity.Type == 2 {
		entity, _ := s.svc.GetById(c, entity.Id)
		marshal, _ := json.Marshal(entity)
		s.RedisClient.HMSet(c, permHKey, strconv.FormatInt(entity.Id, 10), string(marshal))
	}
	results.ResSave(c, res, err)
}

// UpStatus 4更新状态 /system/rule/upStatus
func (s *Rule) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	results.ResSave(c, res, err)
}

// UpOrder /system/rule/upOrder
func (s *Rule) UpOrder(c *gin.Context) {
	req := gf.ReqBody(c, &base.OrderUpd{})
	res, err := s.svc.UpdateOrder(c, req)
	results.ResSave(c, res, err)
}

// Del 删除菜单 /system/rule/del
func (s *Rule) Del(c *gin.Context) {
	//获取post传过来的data
	ids := gf.ReqBody(c, &base.Ids{})
	batch, err := s.svc.DeleteBatch(c, ids)

	// 删除缓存
	s.RedisClient.HDel(c, permHKey, ids.String()...)
	results.ResDel(c, batch, err)
}

func (s *Rule) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"rule:base":     {s.Get_list, s.Get_parent},
		"rule:edit":     {s.Save, s.UpOrder},
		"rule:del":      {s.Del},
		"rule:upStatus": {s.UpStatus},
	}
}
