package captcha

import (
	"context"
	"gofly/pkg/ioc"
	"gofly/pkg/utils/redis"
)

type Service struct {
	RedisClient *redis.Client `inject:""`
}

type Type string

var (
	TypeClickBasic  Type = "ClickBasic"
	TypeClickShapes Type = "ClickShape"
	TypeRotateBasic Type = "RotateBasic"
	TypeSlideBasic  Type = "SlideBasic"
	TypeSlideRegion Type = "SlideRegion"
)

func init() {
	ioc.PrepareSvc(new(Service))
}

func (s *Service) Generate(ctx context.Context, ctype Type) *GetRes {
	switch ctype {
	case TypeClickBasic:
		return s.getClickBasicData(ctx)
	case TypeClickShapes:
		return s.getClickShapesData(ctx)
	case TypeRotateBasic:
		return s.getRotateBasicData(ctx)
	case TypeSlideBasic:
		return s.getSlideBasicData(ctx)
	case TypeSlideRegion:
		return s.getSlideRegionData(ctx)
	}
	return nil
}

func (s *Service) Check(ctx context.Context, c *Check) bool {
	switch c.Type {
	case TypeClickBasic:
		return s.checkClickBasic(ctx, c)
	case TypeClickShapes:
		return s.checkClickShapes(ctx, c)
	case TypeRotateBasic:
		return s.checkRotateBasic(ctx, c)
	case TypeSlideBasic:
		return s.checkSlideBasic(ctx, c)
	case TypeSlideRegion:
		return s.checkSlideRegion(ctx, c)
	}
	return false
}
