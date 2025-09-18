package redis

import (
	"context"
	"fmt"
	"gofly/internal/config"
	"gofly/pkg/ioc"
	"gofly/pkg/logx"
	"time"

	goredis "github.com/redis/go-redis/v9"
)

func init() {
	config.AddAfterConfigFn(InitRedisClient)
}
func InitRedisClient(c *config.Config) {
	if c.Redis.Host == "" {
		return
	}
	t := goredis.NewClient(&goredis.Options{
		Addr:        fmt.Sprintf("%s:%s", c.Redis.Host, c.Redis.Port), // 连接地址
		Password:    c.Redis.Password,                                 // 密码
		DB:          c.Redis.Db,                                       // 数据库编号
		DialTimeout: 1 * time.Second,                                  // 链接超时
	})

	id := t.ClientID(context.Background())
	if id.Err() != nil {
		logx.Error("redis连接接失败", id.Err())
	} else {
		logx.Infof("redis连接成功")
	}

	ioc.Register(&Client{t})
}
