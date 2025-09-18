package base

import (
	"context"
	"fmt"
	"gofly/pkg/json"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/redis"

	"github.com/dgrijalva/jwt-go"
)

// 用户信息类，作为生成token的参数
type SysUser struct {
	Id       int64  `json:"id"`
	Openid   string `json:"openid"`   // 微信openid
	Name     string `json:"name"`     // 姓名
	Username string `json:"username"` // 用户名
	AllPerm  bool   `json:"allPerm"`  // 是否拥有所有权限，权限列表查出来为*
	//jwt-go提供的标准claim
	jwt.StandardClaims
}

func (s *SysUser) GetPermKey() string {
	return fmt.Sprintf("user:login:perm:%d", s.Id)
}
func (s *SysUser) ResetPerms(c context.Context, client *redis.Client, perms []string) {
	m := collx.ToMapByKey(perms, func(perm string) (string, string) {
		return perm, "1"
	})
	key := s.GetPermKey()
	client.Del(c, key)
	client.HMSet(c, key, m)
}

type Model struct {
	IdModel
	TimeModel

	CreatorId   int64  `gorm:"comment:创建人ID" json:"creatorId"`
	CreatorName string `gorm:"comment:创建人名称;size:200" json:"creatorName"`

	UpdaterId   int64  `gorm:"comment:更新人ID" json:"updaterId"`
	UpdaterName string `gorm:"comment:更新人名称;size:200" json:"updaterName"`
}

func (b *Model) GetPkVal() int64 {
	return b.Id
}
func (b *Model) SetCreatorInfo(u *SysUser) {
	if nil != u {
		b.CreatorId = u.Id
		b.CreatorName = u.Name
	}
	b.CreateTime = json.NowJsonTime()
	b.SetUpdaterInfo(u)
}
func (b *Model) SetUpdaterInfo(u *SysUser) {
	if nil != u {
		b.UpdaterId = u.Id
		b.UpdaterName = u.Name
	}
	b.UpdateTime = json.NowJsonTime()
}
