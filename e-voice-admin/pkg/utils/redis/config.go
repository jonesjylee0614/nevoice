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

	// 使用 Ping 命令测试连接（兼容旧版Redis）
	pong, err := t.Ping(context.Background()).Result()
	if err != nil {
		logx.Error("redis连接失败", err)
	} else {
		logx.Infof("redis连接成功: %s", pong)
	}

	ioc.Register(&Client{t})
}
