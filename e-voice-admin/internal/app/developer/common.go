package developer

import (
	"bufio"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

// 1.1 检查该类是否添加到控制器
func CheckIsAddController(path string) {
	filePath := filepath.Join("internal/app/controller.go")
	//1判断文件没有则添加
	if _, err := os.Stat(filePath); err != nil {
		if os.IsNotExist(err) {
			_, _ = os.Create(filePath)
			//复制文件
			err := CopyFileContents("resource/developer/codetpl/go/controller.gos", filePath)
			if err != nil {
				panic(err)
			}
		}
	}
	conPath := "gofly/internal/app/" + path
	f, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	buf := bufio.NewReader(f)
	var result = ""
	has := false
	for {
		a, _, c := buf.ReadLine()
		if c == io.EOF {
			break
		}
		if strings.Contains(string(a), conPath) {
			has = true
		}
		result += string(a) + "\n"
	}
	if has == false {
		addStr := "	_ \"" + conPath + "\""
		dateStr := strings.ReplaceAll(result, ")", addStr)
		result = dateStr + ")\n"
	}
	fw, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666) //os.O_TRUNC清空文件重新写入，否则原文件内容可能残留
	if err != nil {
		panic(err)
	}
	w := bufio.NewWriter(fw)
	_, _ = w.WriteString(result)
	_ = w.Flush()
	_ = fw.Close()
}

// 1.2 存在控制器则移除
func CheckApiRemoveController(path string) {
	filePath := filepath.Join("app/controller.go")
	if _, err := os.Stat(filePath); os.IsNotExist(err) { //不存在
		return
	}
	conPath := "gofly/internal/app/" + path
	f, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	buf := bufio.NewReader(f)
	var result = ""
	for {
		a, _, c := buf.ReadLine()
		if c == io.EOF {
			break
		}
		if strings.Contains(string(a), conPath) { //存在路由则移除
			// datestr := strings.ReplaceAll(string(a), gf.FirstUpper(methods), "get_list")
			// result += datestr + "\n"
			continue
		} else {
			result += string(a) + "\n"
		}
	}
	fw, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666) //os.O_TRUNC清空文件重新写入，否则原文件内容可能残留
	w := bufio.NewWriter(fw)
	_, _ = w.WriteString(result)
	if err != nil {
		panic(err)
	}
	_ = w.Flush()
	_ = fw.Close()
}

// 2.1检查器模块是否存在app下的控制器不存在则添加
func CheckIsAddAppController(modelname string) {
	filePath := filepath.Join("app/controller.go")
	conPath := "gofly/internal/app/" + modelname
	f, err := os.Open(filePath)
	if err != nil {
		fmt.Print(err)
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	buf := bufio.NewReader(f)
	var result = ""
	ishase := false
	for {
		a, _, c := buf.ReadLine()
		if c == io.EOF {
			break
		}
		if strings.Contains(string(a), conPath) {
			ishase = true
		}
		result += string(a) + "\n"
	}
	if ishase == false {
		addstr := "	_ \"" + conPath + "\""
		datestr := strings.ReplaceAll(result, ")", addstr)
		result = datestr + ")\n"
	}
	fw, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666) //os.O_TRUNC清空文件重新写入，否则原文件内容可能残留
	w := bufio.NewWriter(fw)
	_, _ = w.WriteString(result)
	if err != nil {
		panic(err)
	}
	_ = w.Flush()
	_ = fw.Close()
}

// 2.2 存在APP控制器则移除
func CheckApiRemoveAppController(modelname string) {
	filePath := filepath.Join("app/controller.go")
	if _, err := os.Stat(filePath); os.IsNotExist(err) { //不存在
		return
	}
	conPath := "gofly/internal/app/" + modelname
	f, err := os.Open(filePath)
	if err != nil {
		fmt.Println(err)
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	buf := bufio.NewReader(f)
	var result = ""
	for {
		a, _, c := buf.ReadLine()
		if c == io.EOF {
			break
		}
		if strings.Contains(string(a), conPath) { //存在路由则移除
			continue
		} else {
			result += string(a) + "\n"
		}
	}
	fw, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666) //os.O_TRUNC清空文件重新写入，否则原文件内容可能残留
	w := bufio.NewWriter(fw)
	_, _ = w.WriteString(result)
	if err != nil {
		panic(err)
	}
	_ = w.Flush()
	_ = fw.Close()
}

// 单个文件复制
// 将 src 的文件内容拷贝到了 dst 里面
func CopyFileContents(src, dst string) (err error) {
	in, err := os.Open(src)
	if err != nil {
		return
	}
	defer func(in *os.File) {
		_ = in.Close()
	}(in)
	out, err := os.Create(dst)
	if err != nil {
		return
	}
	defer func() {
		cerr := out.Close()
		if err == nil {
			err = cerr
		}
	}()
	if _, err = io.Copy(out, in); err != nil {
		return
	}
	err = out.Sync()
	return
}

// 整个文件复制
// 复制整个文件夹下文件到另个文件夹
func CopyAllDir(targetPath string, destPath string) error {
	err := filepath.Walk(targetPath, func(path string, info fs.FileInfo, err error) error {
		if err != nil {
			return err
		}
		destPath := filepath.Join(destPath, path[len(targetPath):])
		//如果是个文件夹则创建这个文件夹
		if info.IsDir() {
			return os.MkdirAll(destPath, info.Mode())
		}
		//如果是文件则生成这个文件
		return copyFile(path, destPath)
	})
	return err
}

// 复制单个文件
func copyFile(srcFile, destFile string) error {
	src, err := os.Open(srcFile)
	if err != nil {
		return err
	}
	defer func(src *os.File) {
		_ = src.Close()
	}(src)
	//创建复制的文件
	dest, err := os.Create(destFile)
	if err != nil {
		return err
	}
	defer func(dest *os.File) {
		_ = dest.Close()
	}(dest)
	//复制内容到文件
	_, err = io.Copy(dest, src)
	if err != nil {
		return err
	}
	//让复制的文件将内容存到硬盘而不是缓存
	err = dest.Sync()
	if err != nil {
		return err
	}
	return nil
}
