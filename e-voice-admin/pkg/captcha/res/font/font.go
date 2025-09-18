package font

import (
	_ "embed"

	"github.com/golang/freetype/truetype"
)

//go:embed fzshengsksjw_cu.ttf
var fontData []byte

func GetFont() (*truetype.Font, error) {
	font, err := truetype.Parse(fontData)
	if err != nil {
		return nil, err
	}
	return font, nil
}
