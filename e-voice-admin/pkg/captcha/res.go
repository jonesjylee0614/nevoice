package captcha

type GetRes struct {
	Type        Type   `json:"type" comment:"验证码类型"`
	CaptchaKey  string `json:"captchaKey" comment:"验证码key"`
	ImageBase64 string `json:"imageBase64" comment:"底图base64"`
	ThumbBase64 string `json:"thumbBase64" comment:"验证图base64"`
	Tile        *Tile  `json:"tile,omitempty" comment:"验证图初始坐标信息"`
}
type Tile struct {
	Width  int `json:"width" comment:"宽"`
	Height int `json:"height" comment:"高"`
	X      int `json:"x" comment:"x坐标"`
	Y      int `json:"y" comment:"y坐标"`
}

type Check struct {
	Type     Type    `json:"type" comment:"验证码类型"`
	Points   []Point `json:"points" comment:"点选坐标列表"`
	Angle    int     `json:"angle" comment:"旋转角度"`
	Position Point   `json:"position" comment:"滑动滑块位置"`
	Secret   string  `json:"secret" comment:"用于aes加密的Secret"`
}
type Point struct {
	Index int `json:"index" comment:""`
	Key   int `json:"key" comment:""`
	X     int `json:"x" comment:"x坐标"`
	Y     int `json:"y" comment:"y坐标"`
}
