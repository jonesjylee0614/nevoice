package finetune

import (
	"fmt"
	"gofly/internal/config"
	"gofly/internal/domain/dto"
	"gofly/internal/domain/service"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"os"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Detail struct {
	svc *service.FinetuneVoiceDetail `inject:""`
}

func init() {
	gf.RegisterRoute(&Detail{})
}

// 获取列表
func (s *Detail) Get_list(c *gin.Context) {
	req := gf.ReqQuery(c, &dto.FinetuneVoiceDetailPageReq{})
	cond := base.NewCond()
	cond.Order = "id desc"

	// 查询条件示例
	cond.Where(req.Title, "name like ?", "%"+req.Title+"%")

	if req.CreatedTime != "" {
		datetimeArr := strings.Split(req.CreatedTime, ",")
		cond.Where(req.CreatedTime, "create_time between ? and ?", datetimeArr[0]+" 00:00:00", datetimeArr[1]+" 23:59:59")
	}

	list, err := s.svc.Page(c, &req.IPage, cond)
	results.ResPage(c, req.IPage, list, err)
}

// 修改
func (s *Detail) Update(c *gin.Context) {
	entity := gf.ReqBody(c, &biz.FinetuneVoiceDetail{})
	res, err := s.svc.Update(c, entity)
	go s.svc.UpdateWeigh(c, entity.Id)
	results.ResSave(c, res, err)
}

// 上传并新增
func (s *Detail) UploadAdd(c *gin.Context) {
	files, form := gf.ReqMultipartForm(c, "audio")

	text := form.Value["text"][0]
	if text == "" {
		results.Failed(c, "请输入内容", nil)
		return
	}

	// 手动创建的语料，会议id为0
	meetingId := 0

	// 创建目录
	path := fmt.Sprintf("%s/detail/%d", config.Inst.Voice.MeetingPath, meetingId)
	err := os.MkdirAll(path, 0755)
	assert.ErrIsNilAppendErr(err, "创建目录失败 %s")

	audioName := fmt.Sprintf("%d-%s", time.Now().UnixMilli(), files[0].FileName)
	// 音频文件绝对路径
	audioPath := fmt.Sprintf("%s/%s", path, audioName)

	// 把文件保存到指定目录
	err = files[0].WriteToPath(audioPath)
	assert.ErrIsNilAppendErr(err, "保存文件失败 %s")

	entity := &biz.FinetuneVoiceDetail{
		Text:      text,
		VoicePath: audioName, // 音频文件相对路径
	}
	res, err := s.svc.Insert(c, entity)
	go s.svc.UpdateWeigh(c, entity.Id)
	results.ResSave(c, res, err)
}

// 更新状态
func (s *Detail) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	results.ResSave(c, res, err)
}

// 删除
func (s *Detail) Del(c *gin.Context) {
	ids := gf.ReqBody(c, &base.Ids{})
	res, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, res, err)
}

// 获取详情
func (s *Detail) Get_content(c *gin.Context) {
	id := c.DefaultQuery("id", "")
	assert.Nil(id, "请传参数id")

	res, err := s.svc.GetById(c, id)
	results.ResObj(c, res, err)
}

func (s *Detail) Perms() map[string][]gin.HandlerFunc {
	return nil
}
