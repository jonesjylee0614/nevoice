package bc

import (
	"bytes"
	_ "embed"
	"image"
	"image/jpeg"
)

var (
	//go:embed 1.jpeg
	image1 []byte
	//go:embed 2.jpeg
	image2 []byte
	//go:embed 3.jpeg
	image3 []byte
	//go:embed 4.jpeg
	image4 []byte
	//go:embed 5.jpeg
	image5 []byte
	//go:embed 6.jpeg
	image6 []byte
	//go:embed 7.jpeg
	image7 []byte
	//go:embed 8.jpeg
	image8 []byte
	//go:embed 9.jpeg
	image9 []byte
	//go:embed 10.jpeg
	image10 []byte

	Backgrounds = make([]image.Image, 10)
)

func init() {
	images := [][]byte{
		image1,
		image2,
		image3,
		image4,
		image5,
		image6,
		image7,
		image8,
		image9,
		image10,
	}
	for i := 0; i < 10; i++ {
		img, _ := jpeg.Decode(bytes.NewReader(images[i]))
		Backgrounds[i] = img
	}
}
