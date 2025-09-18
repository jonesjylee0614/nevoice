package cryptox

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"fmt"
	"io"
)

// AesEncrypt CBC 模式加密
func AesEncrypt(plainText, key []byte) (string, error) {
	// 生成 AES 块
	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}

	// PKCS7 填充
	plainText = aesPkcs7Padding(plainText, block.BlockSize())

	// 生成随机 IV
	cipherText := make([]byte, aes.BlockSize+len(plainText))
	iv := cipherText[:aes.BlockSize]
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return "", err
	}

	// CBC 加密
	mode := cipher.NewCBCEncrypter(block, iv)
	mode.CryptBlocks(cipherText[aes.BlockSize:], plainText)

	// 返回 base64 编码后的密文
	return base64.StdEncoding.EncodeToString(cipherText), nil
}

// pkcs7Padding 填充
func aesPkcs7Padding(data []byte, blockSize int) []byte {
	//判断缺少几位长度。最少1，最多 blockSize
	padding := blockSize - len(data)%blockSize
	//补足位数。把切片[]byte{byte(padding)}复制padding个
	padText := bytes.Repeat([]byte{byte(padding)}, padding)
	return append(data, padText...)
}

// PKCS7 去除填充
func aesPkcs7UnPadding(data []byte) ([]byte, error) {
	length := len(data)
	if length == 0 {
		return nil, errors.New("数据长度为0")
	}
	padding := int(data[length-1])
	if padding > length || padding > aes.BlockSize {
		return nil, errors.New("invalid padding size")
	}
	return data[:length-padding], nil
}

// AesDecrypt CBC 模式解密
func AesDecrypt(cipherTextBase64 string, key []byte) (string, error) {
	// 解码 base64 密文
	cipherText, err := base64.StdEncoding.DecodeString(cipherTextBase64)
	if err != nil {
		return "", err
	}

	// 生成 AES 块
	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}

	if len(cipherText) < aes.BlockSize {
		return "", errors.New(fmt.Sprintf("密文过短，长度最短不能低于:%v", aes.BlockSize))
	}

	// 读取 IV
	iv := cipherText[:aes.BlockSize]
	cipherText = cipherText[aes.BlockSize:]

	// CBC 解密
	mode := cipher.NewCBCDecrypter(block, iv)
	mode.CryptBlocks(cipherText, cipherText)

	// 去除 PKCS7 填充
	plainText, err := aesPkcs7UnPadding(cipherText)
	if err != nil {
		return "", err
	}

	return string(plainText), nil
}
