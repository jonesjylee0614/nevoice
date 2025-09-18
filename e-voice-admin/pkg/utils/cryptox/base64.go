package cryptox

import "encoding/base64"

func Base64(data []byte) string {
	return base64.StdEncoding.EncodeToString(data)
}
func Base64Str(str string) string {
	return Base64([]byte(str))
}
func Base64Decode(data string) ([]byte, error) {
	return base64.StdEncoding.DecodeString(data)
}
