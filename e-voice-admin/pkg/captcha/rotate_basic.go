package captcha

import (
	"context"
	"encoding/json"
	"gofly/pkg/captcha/capts/rotate"
	"gofly/pkg/logx"
	"gofly/pkg/utils/cryptox"
	"math"
)

func (s *Service) getRotateBasicData(ctx context.Context) *GetRes {
	captData, _ := rotateBasicCapt.Generate()
	blockData := captData.GetData()

	masterImageBase64, _ := captData.GetMasterImage().ToBase64()
	thumbImageBase64, _ := captData.GetThumbImage().ToBase64()

	dotsByte, _ := json.Marshal(blockData)
	key := cryptox.Md5(string(dotsByte))
	s.RedisClient.Set(ctx, captchaKeyPrefix+key, blockData, captchaExpiration)

	return &GetRes{
		Type:        TypeRotateBasic,
		CaptchaKey:  key,
		ImageBase64: masterImageBase64,
		ThumbBase64: thumbImageBase64,
	}
}

func (s *Service) checkRotateBasic(ctx context.Context, f *Check) bool {
	key := captchaKeyPrefix + f.Secret
	defer s.RedisClient.Del(ctx, key)
	result, _ := s.RedisClient.Get(ctx, key).Result()
	if result == "" {
		return false
	}
	block := &rotate.Block{}
	if err := json.Unmarshal([]byte(result), block); err != nil {
		logx.Error("json反序列化失败", err)
		return false
	}
	// 如果请求角度+随机角度和360误差在5以内，则验证通过
	if math.Abs(float64(block.Angle+f.Angle-360)) < 10 {
		return true
	}
	return false
}
