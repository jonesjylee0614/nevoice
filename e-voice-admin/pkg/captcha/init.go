package captcha

import (
	"gofly/pkg/captcha/capts/base/option"
	"gofly/pkg/captcha/capts/click"
	"gofly/pkg/captcha/capts/rotate"
	"gofly/pkg/captcha/capts/slide"
	"gofly/pkg/captcha/res/bc"
	"gofly/pkg/captcha/res/chars"
	"gofly/pkg/captcha/res/font"
	"gofly/pkg/captcha/res/tiles"
	"gofly/pkg/logx"
	"time"

	"github.com/golang/freetype/truetype"
)

var clickTextCapt click.Captcha
var clickShapeCapt click.Captcha
var rotateBasicCapt rotate.Captcha
var slideBasicCapt slide.Captcha
var slideRegionCapt slide.Captcha

var captchaKeyPrefix = "captcha:cache:key:"
var captchaExpiration = time.Minute * 10
var ClickImgSize = 28

func init() {
	bgSize := option.Size{Width: 310, Height: 155}
	clickTileSize := option.RangeVal{Min: ClickImgSize - 1, Max: ClickImgSize + 1}

	clickTextCaptBuilder := click.NewBuilder(
		click.WithImageSize(bgSize),
		click.WithRangeLen(option.RangeVal{Min: 4, Max: 6}),       // 生成的图形总数，包括干扰项
		click.WithRangeVerifyLen(option.RangeVal{Min: 3, Max: 4}), // 需要选择的图形数
		click.WithRangeSize(clickTileSize),
		click.WithRangeThumbBgDistort(1),
		click.WithIsThumbNonDeformAbility(true),
	)

	rotateBasicCaptBuilder := rotate.NewBuilder(
		rotate.WithImageSquareSize(155),
		rotate.WithRangeThumbImageSquareSize([]int{60, 70}),
	)

	slideBasicCaptBuilder := slide.NewBuilder(
		slide.WithImageSize(bgSize),
		slide.WithRangeGraphSize(option.RangeVal{Min: 50, Max: 50}),
		slide.WithGenGraphNumber(2),
		slide.WithEnableGraphVerticalRandom(false),
	)

	slideRegionCaptBuilder := slide.NewBuilder(
		slide.WithImageSize(bgSize),
		slide.WithRangeGraphSize(option.RangeVal{Min: 50, Max: 50}),
		slide.WithGenGraphNumber(2),
		slide.WithEnableGraphVerticalRandom(true),
	)

	// fonts
	fonts, err := font.GetFont()
	if err != nil {
		logx.Error("", err)
	}

	// set resources
	clickTextCaptBuilder.SetResources(
		click.WithChars(chars.GetChineseChars()),
		click.WithFonts([]*truetype.Font{fonts}),
		click.WithBackgrounds(bc.Backgrounds),
	)

	// set resources
	rotateBasicCaptBuilder.SetResources(
		rotate.WithImages(bc.Backgrounds),
	)

	// set resources
	slideBasicCaptBuilder.SetResources(
		slide.WithGraphImages(tiles.TilesImages),
		slide.WithBackgrounds(bc.Backgrounds),
	)
	// set resources
	slideRegionCaptBuilder.SetResources(
		slide.WithGraphImages(tiles.TilesImages),
		slide.WithBackgrounds(bc.Backgrounds),
	)

	clickTextCapt = clickTextCaptBuilder.Make()
	clickShapeCapt = clickTextCaptBuilder.Make()
	rotateBasicCapt = rotateBasicCaptBuilder.Make()
	slideBasicCapt = slideBasicCaptBuilder.Make()
	slideRegionCapt = slideRegionCaptBuilder.Make()

}
