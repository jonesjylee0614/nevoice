package gf

import (
	"archive/zip"
	"io"
	"os"
	"strings"
)

// 压缩文件
// files 文件数组，可以是不同dir下的文件或者文件夹
// dest 压缩文件存放地址
func Compress(file *os.File, dest string) error {
	d, _ := os.Create(dest)
	defer func(d *os.File) {
		_ = d.Close()
	}(d)
	zw := zip.NewWriter(d)
	defer func(zw *zip.Writer) {
		_ = zw.Close()
	}(zw)
	err := compress(file, "", zw)
	if err != nil {
		return err
	}
	return nil
}

func compress(file *os.File, prefix string, zw *zip.Writer) error {
	info, err := file.Stat()
	if err != nil {
		return err
	}
	if info.IsDir() {
		if prefix == "" {
			prefix = info.Name()
		} else {
			prefix = prefix + "/" + info.Name()
		}
		fileInfos, err := file.Readdir(-1)
		if err != nil {
			return err
		}
		for _, fi := range fileInfos {
			f, err := os.Open(file.Name() + "/" + fi.Name())
			defer func(f *os.File) {
				_ = f.Close()
			}(f)
			if err != nil {
				return err
			}
			err = compress(f, prefix, zw)
			if err != nil {
				return err
			}
		}
	} else {
		header, err := zip.FileInfoHeader(info)
		if prefix != "" {
			header.Name = prefix + "/" + header.Name
		}
		if err != nil {
			return err
		}
		writer, err := zw.CreateHeader(header)
		if err != nil {
			return err
		}
		_, err = io.Copy(writer, file)
		_ = file.Close()
		if err != nil {
			return err
		}
	}
	return nil
}

// 解压
func DeCompress(zipFile, dest string) error {
	reader, err := zip.OpenReader(zipFile)
	if err != nil {
		return err
	}
	defer func(reader *zip.ReadCloser) {
		_ = reader.Close()
	}(reader)
	for _, file := range reader.File {
		rc, err := file.Open()
		if err != nil {
			return err
		}
		defer func(rc io.ReadCloser) {
			_ = rc.Close()
		}(rc)
		filename := dest + file.Name
		err = os.MkdirAll(getDir(filename), 0755)
		if err != nil {
			return err
		}
		w, err := os.Create(filename)
		if err != nil {
			return err
		}
		defer func(w *os.File) {
			_ = w.Close()
		}(w)
		_, err = io.Copy(w, rc)
		if err != nil {
			return err
		}
		_ = w.Close()
		_ = rc.Close()
	}
	return nil
}

func getDir(path string) string {
	return subString(path, 0, strings.LastIndex(path, "/"))
}

func subString(str string, start, end int) string {
	rs := []rune(str)
	length := len(rs)

	if start < 0 || start > length {
		panic("start is wrong")
	}

	if end < start || end > length {
		panic("end is wrong")
	}

	return string(rs[start:end])
}
