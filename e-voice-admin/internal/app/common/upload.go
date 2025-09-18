package common

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

func init() {
	gf.RegisterRoute(&Upload{})
}

type Upload struct {
	BusinessAccountSvc    *core_service.BusinessAccount    `inject:""`
	CommonConfigSvc       *core_service.CommonConfig       `inject:""`
	BusinessAttachmentSvc *core_service.BusinessAttachment `inject:""`
}

// Image 上传单文件 /common/upload/image
func (s *Upload) Image(c *gin.Context) {
	// 单个文件
	pid := c.DefaultPostForm("pid", "")
	file, err := c.FormFile("file")
	if err != nil {
		return
	}
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

	if err == nil { //文件已经存在
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
		nameStr := md5Str(fmt.Sprintf("%v%s", nowTime, filenameArr[0]))                      //组装文件保存名字
		fileFilename := fmt.Sprintf("%s%s%s", nameStr, ".", filenameArr[len(filenameArr)-1]) //文件加.后缀
		path := "/common/uploadfile/get_image?url=" + filePath + fileFilename
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
			results.Success(c, "上传成功", att, nil)
		}
	}
}

// 1.文件
func (s *Upload) File(c *gin.Context) {
	// 单个文件
	pid := c.DefaultPostForm("pid", "")
	filetype := c.DefaultPostForm("filetype", "image") //文件类型
	file, err := c.FormFile("file")
	if err != nil {
		results.Failed(c, "获取数据失败，", err)
		return
	}
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

// 编辑器保存第三方图片到本地
func (s *Upload) ThirdImage(c *gin.Context) {
	params, _ := gf.RequestParam(c)
	if url, ok := params["url"]; !ok || url == "" {
		c.JSON(200, gin.H{
			"code":   400,
			"result": false,
			"data": map[string]interface{}{
				"url": "",
			},
			"message": "地址无效",
		})
	} else {
		filePath := fmt.Sprintf("%s%s%s", "resource/uploads/", time.Now().Format("20060102"), "/")
		if _, err := os.Stat(filePath); err != nil {
			if !os.IsExist(err) {
				_ = os.MkdirAll(filePath, os.ModePerm)
			}
		}
		nowTime := time.Now().UnixMilli() //当前时间
		localPicName := fmt.Sprintf("%vthir_%v", filePath, nowTime)
		imgtype, err := gf.DownPic(gf.InterfaceTostring(params["url"]), localPicName)

		rootUrl := s.CommonConfigSvc.GetRootUrl(c)

		c.JSON(200, gin.H{
			"code":    200,
			"result":  true,
			"err":     err,
			"status":  "done",
			"url":     fmt.Sprintf("%s%s%s", rootUrl, localPicName, imgtype),
			"message": "上传成功",
		})
	}
}
func (s *Upload) Perms() map[string][]gin.HandlerFunc {
	return nil
}
