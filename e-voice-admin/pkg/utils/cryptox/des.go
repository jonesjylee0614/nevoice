package cryptox

import (
	"bytes"
	"crypto/cipher"
	"crypto/des"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"fmt"
)

// DES加密函数
func DesEncrypt(data, key []byte) (string, error) {
	block, err := des.NewTripleDESCipher(key)
	if err != nil {
		return "", err
	}
	// 对数据进行填充
	data = desPkcs7Padding(data, des.BlockSize)

	// 创建一个初始化向量
	iv := make([]byte, des.BlockSize)
	if _, err := rand.Read(iv); err != nil {
		return "", err
	}
	// 创建加密器
	mode := cipher.NewCBCEncrypter(block, iv)

	// 加密
	encrypted := make([]byte, len(data))
	mode.CryptBlocks(encrypted, data)

	// 将IV和加密数据组合
	result := append(iv, encrypted...)

	// 使用Base64编码
	return base64.StdEncoding.EncodeToString(result), nil
}

func DesDecrypt(data string, key []byte) (string, error) {
	// Base64解码
	ciphertext, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return "", err
	}

	block, err := des.NewTripleDESCipher(key)
	if err != nil {
		return "", err
	}

	// 确保密文长度正确
	if len(ciphertext) < des.BlockSize {
		return "", fmt.Errorf("ciphertext too short")
	}

	// 提取IV
	iv := ciphertext[:des.BlockSize]
	ciphertext = ciphertext[des.BlockSize:]
	// 创建解密器
	mode := cipher.NewCBCDecrypter(block, iv)
	// 解密仍然用已存在的切片接收结果，无需重新创建切片
	mode.CryptBlocks(ciphertext, ciphertext)
	// 去除填充
	res, err := desPkcs7UnPadding(ciphertext)
	return string(res), err
}

// pkcs7Padding 填充
func desPkcs7Padding(data []byte, blockSize int) []byte {
	//判断缺少几位长度。最少1，最多 blockSize
	padding := blockSize - len(data)%blockSize
	//补足位数。把切片[]byte{byte(padding)}复制padding个
	padText := bytes.Repeat([]byte{byte(padding)}, padding)
	return append(data, padText...)
}

// pkcs7UnPadding 填充的反向操作
func desPkcs7UnPadding(data []byte) ([]byte, error) {
	length := len(data)
	if length == 0 {
		return nil, errors.New("加密字符串错误！")
	}
	//获取填充的个数
	unPadding := int(data[length-1])
	if unPadding > length || unPadding > 32 {
		return nil, errors.New("解密字符串时去除填充个数超出字符串长度")
	}
	return data[:(length - unPadding)], nil
}
