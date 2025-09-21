package finetune

import (
	"gofly/internal/config"
	"gofly/internal/domain/dto"
	"gofly/internal/domain/service"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/filex"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/httpclient"
	"gofly/pkg/utils/results"
	"path"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Task struct {
	svc *service.FinetuneTask `inject:""`
}

func init() {
	gf.RegisterRoute(&Task{})
}

var (
	pyVoiceServer = "py_voice"
)

// 获取列表 /finetune/task/get_list
func (s *Task) Get_list(c *gin.Context) {
	req := gf.ReqQuery(c, &dto.FinetuneTaskPageReq{})
	cond := base.NewCond()
	cond.Order = "id desc"

	// 查询条件示例
	cond.Where(req.Title, "name like ?", "%"+req.Title+"%")

	if req.CreatedTime != "" {
		datetimeArr := strings.Split(req.CreatedTime, ",")
		cond.Where(req.CreatedTime, "create_time between ? and ?", datetimeArr[0]+" 00:00:00", datetimeArr[1]+" 23:59:59")
	}

	list, err := s.svc.Page(c, req.IPage, cond)
	results.ResPage(c, *req.IPage, list, err)
}

// 保存 /finetune/task/save
func (s *Task) Save(c *gin.Context) {
	entity := gf.ReqBody(c, &biz.FinetuneTask{})
	res, err := s.svc.InsertOrUpdate(c, entity)
	go s.svc.UpdateWeigh(c, entity.Id)
	results.ResSave(c, res, err)
}

// 开始微调 /finetune/task/start
func (s *Task) Start(c *gin.Context) {
	req := gf.ReqBody(c, &base.ReqId{})
	res, err := s.svc.Start(c, req.Id)
	results.ResObj(c, res, err)
}

// 查看微调日志 /finetune/task/log
func (s *Task) Log(c *gin.Context) {
	req := gf.ReqBody(c, &base.ReqId{})
	res, err := s.svc.Log(c, req.Id)
	results.ResObj(c, res, err)
}

// 测试微调后的模型，模型会重新实例化到python，所以会比较慢，是正常的 /finetune/task/testModel
func (s *Task) TestModel(c *gin.Context) {
	files, form := gf.ReqMultipartForm(c, "audio")
	request := httpclient.NewRequest(config.Inst.App.Micro[pyVoiceServer].Host + "/model/test_model")
	request.Timeout(time.Second * 30)

	taskId := form.Value["taskId"][0]
	// 把task对应的model.pt文件复制到speech_test目录下
	task, err := s.svc.GetById(c, taskId)
	assert.ErrIsNilAppendErr(err, "任务ID不存在 %s")

	src := path.Join(config.Inst.Voice.FunAsrOutputDir, task.ModelPath)
	dest := path.Join(config.Inst.Voice.ModelTest, "/model.pt")
	err = filex.CopyFile(src, dest)
	assert.ErrIsNilAppendErr(err, "复制模型文件出错 %s")

	res := request.PostMultipart(files, collx.M{})
	m, err := res.BodyToMap()
	results.ResObj(c, m, err)
}

func (s *Task) AdoptModel(c *gin.Context) {
	req := gf.ReqBody(c, &base.ReqId{})

	// 把task对应的model.pt文件复制到speech_train目录下
	task, err := s.svc.GetById(c, req.Id)
	assert.ErrIsNilAppendErr(err, "任务ID不存在 %s")

	src := path.Join(config.Inst.Voice.FunAsrOutputDir, task.ModelPath)
	dest := path.Join(config.Inst.Voice.ModelTrain, "/model.pt")
	err = filex.CopyFile(src, dest)
	assert.ErrIsNilAppendErr(err, "复制模型文件出错 %s")

	// 重载模型
	request := httpclient.NewRequest(config.Inst.App.Micro[pyVoiceServer].Host + "/model/adopt_model")
	request.Timeout(time.Second * 30)
	res := request.Post()
	m, err := res.BodyToMap()
	results.ResObj(c, m, err)
}

// 删除 /finetune/task/del
func (s *Task) Del(c *gin.Context) {
	ids := gf.ReqBody(c, &base.Ids{})
	res, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, res, err)
}

// 获取详情
func (s *Task) Get_content(c *gin.Context) {
	id := c.DefaultQuery("id", "")
	assert.Nil(id, "请传参数id")

	res, err := s.svc.GetById(c, id)
	results.ResObj(c, res, err)
}

func (s *Task) Perms() map[string][]gin.HandlerFunc {
	return nil
}
