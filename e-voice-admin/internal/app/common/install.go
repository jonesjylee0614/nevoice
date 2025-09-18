package common

import (
	"archive/zip"
	"bufio"
	"fmt"
	"gofly/internal/config"
	"gofly/internal/domain/core_service"
	"gofly/internal/model"
	"gofly/internal/model/core"
	"gofly/pkg/logx"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"io"
	"io/fs"
	"net/http"
	"os"
	"path"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

/**
* 项目安装
 */
type Install struct {
	BusinessAccountSvc *core_service.BusinessAccount `inject:""`
}

func init() {
	gf.RegisterRoute(&Install{})
}

// 安装页面
func (s *Install) Index(context *gin.Context) {
	dir, err := os.Getwd()
	assert.ErrIsNilAppendErr(err, "项目路径获取失败 %s")

	filePath := filepath.Join(dir, "/resource/developer/template/install.lock")
	if _, err := os.Stat(filePath); err == nil {
		context.HTML(http.StatusOK, "isinstall.html", gin.H{
			"title": "已经安装页面",
		})
	} else {
		context.HTML(http.StatusOK, "install.html", gin.H{
			"title": "安装页面",
		})
	}
}

// 安装
func (s *Install) Save(c *gin.Context) {
	var parameter map[string]interface{}
	gf.ReqBody(c, &parameter)

	dir, err := os.Getwd() //获取当前路径
	assert.ErrIsNilAppendErr(err, "项目路径获取失败 %s")

	model.CreateDataBase(parameter["driver"], parameter["username"], parameter["password"], parameter["hostname"], parameter["hostport"], parameter["database"])
	//2.修改数据库配置
	cferr := gf.UpConfFieldData(dir, parameter)
	assert.ErrIsNilAppendErr(cferr, "修改数据库配置失败 %s")

	model.InitDb(config.Inst) //初始化数据
	time.Sleep(time.Second * 3)
	//3创建数据库
	//2.1导入基础数据库配置
	SqlPath := filepath.Join(dir, fmt.Sprintf("/resource/developer/template/gofly_basedb_%v.sql", parameter["driver"]))
	sqls, sqlerr := os.ReadFile(SqlPath)
	assert.ErrIsNilAppendErr(sqlerr, "数据库文件不存在：%s")

	sqlArr := strings.Split(string(sqls), ";")
	for _, sql := range sqlArr {
		sql = strings.TrimSpace(sql)
		if sql == "" {
			continue
		}
		_, _ = model.ExecSql(sql)
	}
	//4.修改后台账号
	salt := anyx.ToString(time.Now().UnixMilli())
	businesspass := anyx.ToString(parameter["businessPassword"]) + salt

	uc := &core.BusinessAccount{
		Username: anyx.ToString(parameter["businessUsername"]),
		Password: gf.Md5(businesspass),
		Salt:     salt,
	}
	uc.Id = 1
	_, _ = s.BusinessAccountSvc.Update(c, uc)

	//5.创建安装锁文件
	filePath := filepath.Join(dir, "/resource/developer/template/install.lock")
	_, _ = os.Create(filePath)
	//6.安装前端页面
	if _, ok := parameter["vuepath"]; ok && parameter["vuepath"] != "" {
		parameter["vueobjroot"] = filepath.Join(gf.InterfaceTostring(parameter["vuepath"]), "") //更新前端路径
		//6.1 如果没有filepath文件目录就创建一个
		filePath := fmt.Sprintf("%v", parameter["vuepath"])
		if _, err := os.Stat(filePath); err != nil {
			if !os.IsExist(err) {
				_ = os.MkdirAll(filePath, os.ModePerm)
			}
		}
		//6.2 复制前端文件到指定位置
		vuesourePath := filepath.Join(dir, "/resource/developer/template/vuecode/")
		_ = CopyDir(vuesourePath, filePath)
		//6.3 解压文件
		frontVuePath := filepath.Join(filePath, "/front.zip")
		_ = Unzip(frontVuePath, filePath)
		//6.4 删除zip文件
		_ = os.RemoveAll(frontVuePath)
	}
	results.Success(c, "安装成功,去前端刷新试试！", parameter, nil)
}

// 移除admin控制器 判断存在则移除
func ChecAdminRemoveController() {
	filePath := filepath.Join("app/controller.go")
	con_path := "gofly/internal/app/admin"
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
		if strings.Contains(string(a), con_path) { //存在路由则移除
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
}

// DeCompress 解压文件 返回解压的目录
// zipFile 完整文件路径，dest文件目录
func DeCompress(zipFile, dest string) (string, error) {
	// 打开zip文件
	reader, err := zip.OpenReader(zipFile)
	if err != nil {
		return "", err
	}
	defer func() {
		err := reader.Close()
		if err != nil {
			logx.Infof(fmt.Sprintf("解压文件关闭失败: %v\n", err.Error()))
		}
	}()
	var (
		first string // 记录第一次的解压的名字
		order int    = 0
	)
	for _, file := range reader.File {
		rc, err := file.Open()
		if err != nil {
			return "", err
		}
		filename := filepath.Join(dest, file.Name)
		//记录第一次的名字
		if order == 0 {
			first = filename
		}
		order += 1
		if file.FileInfo().IsDir() {
			err = os.MkdirAll(filename, 0755)
			if err != nil {
				return "", err
			}
		} else {
			w, err := os.Create(filename)
			if err != nil {
				return "", err
			}
			//defer w.Close()
			_, err = io.Copy(w, rc)
			if err != nil {
				return "", err
			}
			iErr := w.Close()
			if iErr != nil {
				logx.Infof(fmt.Sprintf("[unzip]: close io %s\n", iErr.Error()))
			}
			fErr := rc.Close()
			if fErr != nil {
				logx.Infof(fmt.Sprintf("[unzip]: close io %s\n", fErr.Error()))
			}
		}
	}
	return first, nil
}

// Unzip decompresses a zip file to specified directory.
// Note that the destination directory don't need to specify the trailing path separator.
// If the destination directory doesn't exist, it will be created automatically.
func Unzip(zipath, dir string) error {
	// Open zip file.
	reader, err := zip.OpenReader(zipath)
	if err != nil {
		return err
	}
	defer func(reader *zip.ReadCloser) {
		_ = reader.Close()
	}(reader)
	for _, file := range reader.File {
		if err := unzipFile(file, dir); err != nil {
			return err
		}
	}
	return nil
}

func unzipFile(file *zip.File, dir string) error {
	// Prevent path traversal vulnerability.
	// Such as if the file name is "../../../path/to/file.txt" which will be cleaned to "path/to/file.txt".
	name := strings.TrimPrefix(filepath.Join(string(filepath.Separator), file.Name), string(filepath.Separator))
	filePath := path.Join(dir, name)

	// Create the directory of file.
	if file.FileInfo().IsDir() {
		if err := os.MkdirAll(filePath, os.ModePerm); err != nil {
			return err
		}
		return nil
	}
	if err := os.MkdirAll(filepath.Dir(filePath), os.ModePerm); err != nil {
		return err
	}

	// Open the file.
	r, err := file.Open()
	if err != nil {
		return err
	}
	defer func(r io.ReadCloser) {
		_ = r.Close()
	}(r)

	// Create the file.
	w, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer func(w *os.File) {
		_ = w.Close()
	}(w)

	// Save the decompressed file content.
	_, err = io.Copy(w, r)
	return err
}

// 2复制整个文件夹下文件到另个文件夹 targetPath文件夹，destPath复制的文件
func CopyDir(targetPath string, destPath string) error {
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
func (s *Install) Perms() map[string][]gin.HandlerFunc {
	return nil
}
