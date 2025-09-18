package gf

import (
	"bufio"
	"fmt"
	"image/gif"
	"image/jpeg"
	"image/png"
	"io"
	"net/http"
	"os"
	"strings"

	"github.com/pkg/errors"
)

// 覆盖写入文件
// filePath文件路径
func WriteToFile(filePath string, content string) error {
	if _, err := os.Stat(filePath); err != nil {
		if !os.IsExist(err) {
			pathStrArr := strings.Split(filePath, `/`)
			pathDirs := strings.Split(filePath, pathStrArr[len(pathStrArr)-1])
			_ = os.MkdirAll(pathDirs[0], os.ModePerm)
			_, _ = os.Create(filePath)
		}
	}
	f, err := os.OpenFile(filePath, os.O_WRONLY|os.O_TRUNC|os.O_CREATE, 0644)
	if err != nil {
		fmt.Println("file create failed. err: " + err.Error())
	} else {
		n, _ := f.Seek(0, io.SeekEnd)
		_, err = f.WriteAt([]byte(content), n)
		defer func(f *os.File) {
			_ = f.Close()
		}(f)
	}
	return err
}

// 逐行读取文件
// filePath文件路径
func ReaderFileByline(filePath string) []interface{} {
	f, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	buf := bufio.NewReader(f)
	var list []interface{}
	for {
		line, _, err := buf.ReadLine()
		if err == io.EOF {
			break
		}
		list = append(list, string(line))
	}
	return list
}

// 一次性读取全部文件
// filePath文件路径
func ReaderFileBystring(filePath string) string {
	file, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer func(file *os.File) {
		_ = file.Close()
	}(file)
	bytes, err := io.ReadAll(file)
	if err != nil {
		panic(err.Error())
	}
	return string(bytes)
}

// DownPic 远程下载图片
func DownPic(src, dest string) (string, error) {
	re, err := http.Get(src)
	if err != nil {
		return "", err
	}
	defer func(Body io.ReadCloser) {
		_ = Body.Close()
	}(re.Body)
	fix := "png"
	if idx := strings.LastIndex(src, "."); idx != -1 {
		fix = strings.ToLower(src[idx+1:])
		if strings.Contains(fix, "?") {
			fix_arr := strings.Split(fix, "?")
			fix = fix_arr[0]
		}
	}
	if fix == "" {
		return "", errors.Errorf("unknow pic type, pic path: %s", src)
	}
	thumbF, err := os.OpenFile(dest+"."+fix, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return "", err
	}
	defer func(thumbF *os.File) {
		_ = thumbF.Close()
	}(thumbF)
	if fix == "jpeg" || fix == "jpg" {
		img, err := jpeg.Decode(re.Body)
		if err != nil {
			return "", err
		}
		if err = jpeg.Encode(thumbF, img, &jpeg.Options{Quality: 40}); err != nil {
			return "", err
		}
	} else if fix == "png" {
		img, err := png.Decode(re.Body)
		if err != nil {
			return "", err
		}
		if err = png.Encode(thumbF, img); err != nil {
			return "", err
		}
	} else if fix == "gif" {
		img, err := gif.Decode(re.Body)
		if err != nil {
			return "", err
		}
		if err = gif.Encode(thumbF, img, nil); err != nil {
			return "", err
		}
	} else {
		return "", errors.New("不支持的格式")
	}
	return "." + fix, nil
}
