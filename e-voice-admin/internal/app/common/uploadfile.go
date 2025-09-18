package common

import (
	"bytes"
	"context"
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

func init() {
	gf.RegisterRoute(&Uploadfile{})
}

type Uploadfile struct {
	BusinessAccountSvc    *core_service.BusinessAccount    `inject:""`
	BusinessAttachmentSvc *core_service.BusinessAttachment `inject:""`
	CommonConfigSvc       *core_service.CommonConfig       `inject:""`
}

// 1.上传单文件
func (s *Uploadfile) Onefile(c *gin.Context) {
	// 单个文件
	pid := c.DefaultPostForm("pid", "")
	filetype := c.DefaultPostForm("filetype", "image") //文件类型
	file, err := c.FormFile("file")
	assert.ErrIsNilAppendErr(err, "获取数据失败，%s")

	nowTime := time.Now().UnixMilli() //当前时间

	rootUrl := s.CommonConfigSvc.GetRootUrl(c)
	//判断文件是否已经传过
	fileContent, _ := file.Open()
	var byteContainer []byte
	byteContainer = make([]byte, 1000000)
	_, _ = fileContent.Read(byteContainer)
	mD5 := md5.New()
	mD5.Write(byteContainer)
	sha1Str := hex.EncodeToString(mD5.Sum(nil))
	//查找该用户是否传过

	cond := base.NewCond()
	cond.Where(true, "sha1", sha1Str)
	attachment, err := s.BusinessAttachmentSvc.First(c, cond)

	if attachment != nil && err == nil { //文件是否已经存在
		cond := base.NewCond()
		cond.Order = "weigh desc"
		maxAtt, err := s.BusinessAttachmentSvc.First(c, cond)
		if maxAtt != nil && err == nil {
			maxAtt.Weigh = maxAtt.Weigh + 1
			_, _ = s.BusinessAttachmentSvc.Update(c, maxAtt)
		}
		attachment.URL = rootUrl + attachment.URL
		results.Success(c, "文件已上传", attachment, nil)
	} else {
		filePath := fmt.Sprintf("%s%s%s", "resource/uploads/", time.Now().Format("20060102"), "/")
		//如果没有filepath文件目录就创建一个
		if _, err := os.Stat(filePath); err != nil {
			if !os.IsExist(err) {
				_ = os.MkdirAll(filePath, os.ModePerm)
			}
		}
		//上传到的路径
		filenameArr := strings.Split(file.Filename, ".")
		//重新名片-lunix系统不支持中文
		nameStr := md5Str(fmt.Sprintf("%v%s", nowTime, filenameArr[0]))     //组装文件保存名字
		fileFilename := fmt.Sprintf("%s%s%s", nameStr, ".", filenameArr[1]) //文件加.后缀
		path := filePath + fileFilename
		// 上传文件到指定的目录
		err = c.SaveUploadedFile(file, path)
		if err != nil { //上传失败
			c.JSON(200, gin.H{
				"uid":      sha1Str,
				"name":     file.Filename,
				"status":   "error",
				"response": "上传失败",
				"time":     nowTime,
			})
		} else { //上传成功
			//保存数据
			dir, _ := filepath.Abs(filepath.Dir(os.Args[0]))
			var ftype int64 = 0
			var coverUrl = ""
			if filetype == "video" {
				ftype = 2
				videopath := fmt.Sprintf("./%s", path)
				pathroot := strings.Split(path, ".")
				imgpath := fmt.Sprintf("./%s", pathroot[0])
				fname, err := GetSnapshot(videopath, imgpath, 1)
				if err == nil {
					coverUrl = fname
				}
			}

			att := &core.BusinessAttachment{
				Type:     ftype,
				Pid:      anyx.ToInt64(pid),
				Sha1:     sha1Str,
				Title:    filenameArr[0],
				Name:     file.Filename,
				URL:      path,
				CoverURL: coverUrl,
				Storage:  dir + "/" + path,
				Filesize: file.Size,
				Mimetype: file.Header["Content-Type"][0],
			}

			//保存数据
			_, _ = s.BusinessAttachmentSvc.Insert(c, att)
			//更新排序
			s.BusinessAttachmentSvc.UpdateWeigh(c, att.Id)
			//返回数据
			att.URL = rootUrl + att.URL
			results.Success(c, "上传成功", att, nil)
		}
	}
}

// 2. 获取视频中最后一帧的图片 url=视频地址,path=图片地址
func getLastFrame(url string, path string, ffmpegPath string) string {
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(50000)*time.Millisecond)
	cmd := exec.CommandContext(ctx, ffmpegPath,
		"-loglevel", "error",
		"-y",
		"-ss", "13",
		"-t", "1",
		"-i", url,
		"-vframes", "1",
		path+".jpg")
	defer cancel()
	var stderr bytes.Buffer
	cmd.Stderr = &stderr
	var outputerror string
	err := cmd.Run()
	if err != nil {
		outputerror += fmt.Sprintf("lastframecmd—err1:%v;", err)
	}
	if stderr.Len() != 0 {
		outputerror += fmt.Sprintf("lastframestd—err2:%v;", stderr.String())
	}
	if ctx.Err() != nil {
		outputerror += fmt.Sprintf("lastframectx—err3:%v;", ctx.Err())
	}
	return path + ".jpg"
}

// Get_image 显示图片 /common/uploadfile/get_image
func (s *Uploadfile) Get_image(c *gin.Context) {
	imageName := c.Query("url")
	imgrul := strings.Split(imageName, "?")
	c.File(imgrul[0])
}

// 4.显示图片base64
func (s *Uploadfile) Get_imagebase(c *gin.Context) {
	imageName := c.Query("url")
	file, _ := os.ReadFile(imageName)
	_, _ = c.Writer.WriteString(string(file))
}
func (s *Uploadfile) Perms() map[string][]gin.HandlerFunc {
	return nil
}
