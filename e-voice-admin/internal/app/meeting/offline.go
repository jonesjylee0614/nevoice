package meeting

import (
	"context"
	"gofly/internal/config"
	"gofly/internal/domain/core_service"
	"gofly/internal/domain/dto"
	"gofly/internal/domain/service"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/internal/model/core"
	"gofly/pkg/json"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/httpclient"
	"gofly/pkg/utils/results"
	"gofly/pkg/utils/timex"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Offline struct {
	svc                     *service.MeetingOffline       `inject:""`
	MeetingOfflineDetailSvc *service.MeetingOfflineDetail `inject:""`
	BusinessAccountSvc      *core_service.BusinessAccount `inject:""`
	FinetuneVoiceDetailSvc  *service.FinetuneVoiceDetail  `inject:""`
}

func init() {
	gf.RegisterRoute(&Offline{})
}

var (
	// 语音服务配置名
	pyVoiceServer = "py_voice"
)

// Get_list 获取列表  /meeting/offline/get_list
func (s *Offline) Get_list(c *gin.Context) {
	req := gf.ReqQuery(c, &dto.MeetingOfflinePageReq{})
	cond := base.NewCond()
	cond.Order = "id desc"

	// 查询条件示例
	cond.Where(req.Title, "name like ?", "%"+req.Title+"%")

	if req.CreatedTime != "" {
		datetimeArr := strings.Split(req.CreatedTime, ",")
		cond.Where(req.CreatedTime, "create_time between ? and ?", datetimeArr[0]+" 00:00:00", datetimeArr[1]+" 23:59:59")
	}

	list, err := s.svc.Page(c, &*req.IPage, cond)
	results.ResPage(c, *req.IPage, list, err)
}

// Update 保存  /meeting/offline/update
func (s *Offline) Update(c *gin.Context) {
	req := gf.ReqBody(c, &dto.MeetingOfflineUpdateReq{})

	t := &biz.MeetingOffline{}
	t.Id = req.Id
	t.Name = req.Name
	t.MeetingTime = req.MeetingTime
	res, err := s.svc.Update(c, t)
	results.ResSave(c, res, err)
}

// Save 保存  /meeting/offline/save
func (s *Offline) Save(c *gin.Context) {

	files, form := gf.ReqMultipartForm(c, "audio")

	// 保存会议信息
	mt := &biz.MeetingOffline{}
	mt.Name = form.Value["name"][0]
	mt.MeetingTime = json.NewJsonTime(timex.ParseTime(form.Value["meetingTime"][0]))
	_, err := s.svc.Insert(c, mt)
	assert.ErrIsNilAppendErr(err, "保存会议信息失败")

	url := config.Inst.App.Micro[pyVoiceServer].Host + "/meeting/offline"
	request := httpclient.NewRequest(url)
	request.Timeout(time.Second * 30)
	sysUser := s.svc.GetSysUser(c)
	params := collx.M{
		"userid":      sysUser.Id,
		"username":    sysUser.Username,
		"meetingId":   mt.Id,
		"meetingTime": form.Value["meetingTime"][0],
	}

	res := request.PostMultipart(files, params)
	m, err := res.BodyToMap()

	if v, has := m["audio_name"]; has {
		mt.AudioPath = anyx.ToString(v)
		_, _ = s.svc.Update(c, mt)
	}

	results.ResObj(c, m, err)
}

// UpStatus 更新状态  /meeting/offline/upStatus
func (s *Offline) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	results.ResSave(c, res, err)
}

// Del 删除 /meeting/offline/del
func (s *Offline) Del(c *gin.Context) {
	ids := gf.ReqBody(c, &base.Ids{})
	res, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, res, err)
}

// GetDetail 详情 /meeting/offline/getDetail
func (s *Offline) GetDetail(c *gin.Context) {
	id := c.DefaultQuery("meetingId", "")
	res, err := s.MeetingOfflineDetailSvc.ListByField(c, "meeting_id", id)
	// 取出用户id并查询用户信息
	userIds := make([]int64, 0)
	for _, v := range res {
		if v.SpkUserId != 0 {
			userIds = append(userIds, v.SpkUserId)
		}
	}
	// 去重
	userIds = collx.Unique(userIds)
	users, _ := s.BusinessAccountSvc.ListByField(c, "id", userIds)
	um := collx.ToMapByKey(users, func(v *core.BusinessAccount) (int64, *core.BusinessAccount) {
		return v.Id, v
	})
	res2 := make([]*dto.MeetingOfflineDetailRes, 0)
	for _, re := range res {
		detail := &dto.MeetingOfflineDetailRes{}
		detail.MeetingOfflineDetail = re
		if v, has := um[re.SpkUserId]; has {
			detail.SpkUserName = v.Name
			detail.SpkUserAvatar = v.Avatar
		}
		res2 = append(res2, detail)
	}
	results.ResObj(c, res2, err)
}

// UpdateDetail 修改详情 /meeting/offline/updateDetail
func (s *Offline) UpdateDetail(c *gin.Context) {
	req := gf.ReqBody(c, &dto.MeetingOfflineDetailUpdateReq{})
	t := &biz.MeetingOfflineDetail{}
	t.Id = req.Id
	t.Text = req.Text
	t.TrainStatus = biz.TrainStatusWait
	res, err := s.MeetingOfflineDetailSvc.Update(c, t)
	// 保存训练语料
	go func() {
		ctx := context.Background()
		detail, err := s.MeetingOfflineDetailSvc.GetById(ctx, req.Id)
		if err != nil || detail == nil {
			return
		}
		s.FinetuneVoiceDetailSvc.SaveByMeetingDetail(ctx, detail)
	}()

	results.ResSave(c, res, err)
}

// TrainDetail 修改详情训练 /meeting/offline/trainDetail
func (s *Offline) TrainDetail(c *gin.Context) {
	req := gf.ReqBody(c, &dto.MeetingOfflineDetailTrainReq{})

	t := &biz.MeetingOfflineDetail{}
	t.Id = req.Id
	if req.Add {
		t.TrainStatus = biz.TrainStatusWait
	} else {
		t.TrainStatus = biz.TrainStatusNone
	}
	res, err := s.MeetingOfflineDetailSvc.Update(c, t)

	if t.TrainStatus == biz.TrainStatusWait {
		detail, err := s.MeetingOfflineDetailSvc.GetById(c, t.Id)
		if err != nil || detail == nil {
			return
		}
		s.FinetuneVoiceDetailSvc.SaveByMeetingDetail(c, detail)
	} else {
		s.FinetuneVoiceDetailSvc.DeleteByMeetingDetailId(c, t.Id)
	}

	results.ResSave(c, res, err)
}

func (s *Offline) Perms() map[string][]gin.HandlerFunc {
	return nil
}
