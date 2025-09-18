package redis

import (
	"context"
	"encoding/json"
	"gofly/pkg/utils/anyx"
	"time"

	goredis "github.com/redis/go-redis/v9"
)

type Client struct {
	*goredis.Client
}

// Set 重构set方法，自动把value转为json
func (c *Client) Set(ctx context.Context, key string, value interface{}, expiration time.Duration) *goredis.StatusCmd {
	// 判断value是否可以转为json
	var setValue interface{}

	if anyx.IsNumber(value) { // 判断value是否为数字
		setValue = value
	} else if _, ok := value.(string); ok { // 判断value是否为string
		setValue = value
	} else if jsonValue, err := json.Marshal(value); err != nil {
		setValue = value
	} else {
		setValue = string(jsonValue)
	}

	return c.Client.Set(ctx, key, setValue, expiration)
}

/**********1.配置**********/
