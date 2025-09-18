package gf

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

// 更新配置文件
func UpConfFieldData(path string, parameter map[string]interface{}) error {
	filePath := filepath.Join(path, "/resource/config.yml")
	f, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	buf := bufio.NewReader(f)
	var result = ""
	var isHose = false
	for {
		isHose = false
		a, _, c := buf.ReadLine()
		if c == io.EOF {
			break
		}
		for keys, Val := range parameter {
			if strings.Contains(string(a), keys) {
				isHose = true
				dateStr := strings.ReplaceAll(string(a), string(a), fmt.Sprintf("     %v: %v\n", keys, Val))
				result += dateStr
			}
		}
		if !isHose {
			result += string(a) + "\n"
		}
	}
	fw, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666) //os.O_TRUNC清空文件重新写入，否则原文件内容可能残留
	if err != nil {
		panic(err)
	}
	w := bufio.NewWriter(fw)
	_, _ = w.WriteString(result)
	_ = w.Flush()
	return nil
}
