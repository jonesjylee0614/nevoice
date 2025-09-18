package redis

type BaseRedis struct {
	RedisClient *Client `inject:""`
}
