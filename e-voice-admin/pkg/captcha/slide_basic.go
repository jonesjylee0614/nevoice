package captcha

import (
	"context"
	"encoding/json"
	"gofly/pkg/captcha/capts/slide"
	"gofly/pkg/logx"
	"gofly/pkg/utils/cryptox"
	"math"
)

func (s *Service) getSlideBasicData(ctx context.Context) *GetRes {
	captData, _ := slideBasicCapt.Generate()

	blockData := captData.GetData()

	masterImageBase64, _ := captData.GetMasterImage().ToBase64()
	tileImageBase64, _ := captData.GetTileImage().ToBase64()

	dotsByte, _ := json.Marshal(blockData)
	key := cryptox.Md5(string(dotsByte))
	s.RedisClient.Set(ctx, captchaKeyPrefix+key, blockData, captchaExpiration)

	return &GetRes{
		Type:        TypeSlideBasic,
		CaptchaKey:  key,
		ImageBase64: masterImageBase64,
		ThumbBase64: tileImageBase64,
		Tile: &Tile{
			Width:  blockData.Width,
			Height: blockData.Height,
			X:      blockData.TileX,
			Y:      blockData.TileY,
		},
	}
}

func (s *Service) checkSlideBasic(ctx context.Context, f *Check) bool {
	key := captchaKeyPrefix + f.Secret
	defer s.RedisClient.Del(ctx, key)

	result, err := s.RedisClient.Get(ctx, key).Result()
	if result == "" {
		return false
	}
	block := &slide.Block{}
	err = json.Unmarshal([]byte(result), block)
	if err != nil {
		logx.Error("取出redis数据失败", err)
	}

	// 如果点位x坐标距离在5以内，则验证通过
	if math.Abs(float64(block.X-f.Position.X)) < 10 {
		return true
	}

	return false
}
