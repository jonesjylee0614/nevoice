package captcha

import (
	"context"
	"encoding/json"
	"gofly/pkg/captcha/capts/click"
	"gofly/pkg/utils/cryptox"
	"math"
)

func (s *Service) getClickBasicData(ctx context.Context) *GetRes {
	captData, _ := clickTextCapt.Generate()
	dotData := captData.GetData()
	masterImageBase64, _ := captData.GetMasterImage().ToBase64()
	thumbImageBase64, _ := captData.GetThumbImage().ToBase64()

	dotsByte, _ := json.Marshal(dotData)
	key := cryptox.Md5(string(dotsByte))
	s.RedisClient.Set(ctx, captchaKeyPrefix+key, dotData, captchaExpiration)

	return &GetRes{
		CaptchaKey:  key,
		ImageBase64: masterImageBase64,
		ThumbBase64: thumbImageBase64,
		Type:        TypeClickBasic,
	}
}

func (s *Service) checkClickBasic(ctx context.Context, f *Check) bool {
	key := captchaKeyPrefix + f.Secret
	defer s.RedisClient.Del(ctx, key)

	result, _ := s.RedisClient.Get(ctx, key).Result()
	if result == "" {
		return false
	}
	var dots map[int]*click.Dot
	_ = json.Unmarshal([]byte(result), &dots)
	if len(dots) == len(f.Points) {
		for i := 0; i < len(f.Points); i++ {
			point := f.Points[i]
			dltSize := ClickImgSize / 2
			dot := dots[f.Points[i].Index-1]
			// 如果点位误差在5px外，retrun false
			if math.Abs(float64(dot.X+dltSize-point.X)) > 10 || math.Abs(float64(dot.Y+dltSize-point.Y)) > 10 {
				return false
			}
		}
		// 全部点位校验完毕
		return true
	}

	return false
}
