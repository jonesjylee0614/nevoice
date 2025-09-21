package filex

import (
	"fmt"
	"gofly/pkg/utils/stringx"
	"io"
	"os"
)

func WriteString(filePath, content string) error {
	//os.O_TRUNC清空文件重新写入，否则原文件内容可能残留
	f, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666)
	if err != nil {
		fmt.Println("文件打开失败", err)
		return err
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	_, err = f.WriteString(content)
	if err != nil {
		fmt.Println("文件写入失败", err)
		return err
	}
	return nil
}

func ParseTempAdWrite(tmpPath string, filePath string, params any) error {
	temp1, err := ReadFile(tmpPath)
	if err != nil {
		return err
	}

	parse1, err := stringx.TemplateParse(temp1, params)
	if err != nil {
		return err
	}
	err = WriteString(filePath, parse1)
	return err
}

func Exists(filepath string) bool {
	if _, err := os.Stat(filepath); os.IsNotExist(err) {
		return true
	}
	return false
}

func ReadFile(filePath string) (string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	content, err := os.ReadFile(filePath)
	if err != nil {
		return "", err
	}
	return string(content), nil
}

// DelFile 删除本地附件
func DelFile(fileList ...string) {
	for _, val := range fileList {
		_ = os.Remove(val)
	}
}

func CopyFile(src, dest string) error {
	// 打开源文件
	sourceFile, err := os.Open(src)
	if err != nil {
		return err
	}
	defer sourceFile.Close()

	// 创建目标文件（如果存在则覆盖）
	destFile, err := os.Create(dest)
	if err != nil {
		return err
	}
	defer destFile.Close()

	// 复制文件内容
	_, err = io.Copy(destFile, sourceFile)
	if err != nil {
		return err
	}

	// 确保数据写入磁盘
	err = destFile.Sync()
	if err != nil {
		return err
	}

	return nil
}
