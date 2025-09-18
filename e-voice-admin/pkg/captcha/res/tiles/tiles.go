package tiles

import (
	"bytes"
	_ "embed"
	"gofly/pkg/captcha/capts/slide"
	"image/png"
)

var (
	//go:embed tile-shadow-1.png
	shadow1 []byte
	//go:embed tile-shadow-2.png
	shadow2 []byte
	//go:embed tile-shadow-3.png
	shadow3 []byte
	//go:embed tile-shadow-4.png
	shadow4 []byte

	//go:embed tile-mask-1.png
	mask1 []byte
	//go:embed tile-mask-2.png
	mask2 []byte
	//go:embed tile-mask-3.png
	mask3 []byte
	//go:embed tile-mask-4.png
	mask4 []byte

	//go:embed tile-1.png
	overlay1 []byte
	//go:embed tile-2.png
	overlay2 []byte
	//go:embed tile-3.png
	overlay3 []byte
	//go:embed tile-4.png
	overlay4 []byte

	TilesImages = make([]*slide.GraphImage, 4)
)

func init() {
	shadows := [][]byte{
		shadow1,
		shadow2,
		shadow3,
		shadow4,
	}
	masks := [][]byte{
		mask1,
		mask2,
		mask3,
		mask4,
	}
	overlays := [][]byte{
		overlay1,
		overlay2,
		overlay3,
		overlay4,
	}

	for i := 0; i < 4; i++ {
		shadow, _ := png.Decode(bytes.NewReader(shadows[i]))
		mask, _ := png.Decode(bytes.NewReader(masks[i]))
		overlay, _ := png.Decode(bytes.NewReader(overlays[i]))
		TilesImages[i] = &slide.GraphImage{
			ShadowImage:  shadow,
			MaskImage:    mask,
			OverlayImage: overlay,
		}
	}
}
