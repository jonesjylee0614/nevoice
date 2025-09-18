package common

/**
* 系统消息
 */
import (
	"context"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/redis"
	"gofly/pkg/utils/results"
	"time"

	"github.com/gin-gonic/gin"
)

func init() {
	gf.RegisterRoute(&Message{})
}

type Message struct {
	redis.BaseRedis
	svc *core_service.CommonMessage `inject:""`
}

// Get_list /common/message/get_list
func (s *Message) Get_list(c *gin.Context) {
	// redis使用示例
	s.RedisClient.Set(context.Background(), "common_message", 0, 1*time.Second)

	sysUser := s.svc.GetSysUser(c)

	cond := base.NewCond()
	cond.Fields = "id,type,title,path,content,isread,create_time,update_time"
	cond.Order = "id desc"

	cond.Where(true, "usertype", 0, 1) //用户类型
	cond.Where(true, "touid", sysUser.Id)

	list, err := s.svc.List(c, cond)
	assert.ErrIsNilAppendErr(err, "加载数据失败")

	results.Success(c, "获取全部列表", map[string]interface{}{
		"total": len(list),
		"items": list,
	}, nil)

}

// 设置为已读 /common/message/read
func (s *Message) Read(c *gin.Context) {
	ids := gf.ReqBody(c, &base.Ids{})

	tx := base.GormDb.Model(s.svc.GetModel()).Where("id", ids.Ids).Updates(&core.CommonMessage{Isread: true})

	results.ResSave(c, tx.RowsAffected, tx.Error)
}

func (s *Message) Perms() map[string][]gin.HandlerFunc {
	return nil
}
