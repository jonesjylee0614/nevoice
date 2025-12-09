package meeting

import (
	"context"
	"encoding/json"
	"fmt"
	"gofly/internal/config"
	"gofly/internal/domain/core_service"
	"gofly/internal/domain/dto"
	"gofly/internal/domain/service"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/internal/model/core"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/httpclient"
	"gofly/pkg/utils/jsonx"
	"gofly/pkg/utils/results"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// Mdt MDT会议控制器
type Mdt struct {
	svc                     *service.MeetingMdt             `inject:""`
	dialogSvc               *service.MeetingMdtDialog       `inject:""`
	BusinessAuthRoleAccess  *core_service.BusinessAuthRoleAccess `inject:""`
	BusinessAccount         *core_service.BusinessAccount        `inject:""`
}

func init() {
	gf.RegisterRoute(&Mdt{})
}

// Get_list 获取会议列表 /meeting/mdt/get_list
func (s *Mdt) Get_list(c *gin.Context) {
	req := gf.ReqQuery(c, &dto.MeetingMdtPageReq{})
	cond := base.NewCond()
	cond.Order = "id desc"

	// 查询条件
	cond.Where(req.Title, "title like ?", "%"+req.Title+"%")
	cond.Where(req.HostName, "host_name like ?", "%"+req.HostName+"%")
	cond.Where(req.Status != nil, "status = ?", req.Status)

	if req.CreatedTime != "" {
		datetimeArr := strings.Split(req.CreatedTime, ",")
		cond.Where(req.CreatedTime, "create_time between ? and ?", datetimeArr[0]+" 00:00:00", datetimeArr[1]+" 23:59:59")
	}

	if req.StartTime != "" {
		datetimeArr := strings.Split(req.StartTime, ",")
		cond.Where(req.StartTime, "start_time between ? and ?", datetimeArr[0]+" 00:00:00", datetimeArr[1]+" 23:59:59")
	}

	list, err := s.svc.Page(c, &*req.IPage, cond)
	results.ResPage(c, *req.IPage, list, err)
}

// Get_detail 获取会议详情 /meeting/mdt/get_detail
func (s *Mdt) Get_detail(c *gin.Context) {
	idStr := c.DefaultQuery("id", "")
	id := anyx.ToInt64(idStr)

	// 获取会议基本信息
	meeting, err := s.svc.GetById(c, id)
	if err != nil {
		results.ResError(c, err)
		return
	}

	// 获取对话列表
	dialogs, _ := s.dialogSvc.ListByField(c, "meeting_id", id)

	// 解析参会人员JSON
	var participantList []dto.MeetingParticipant
	if meeting.Participants != "" {
		_ = json.Unmarshal([]byte(meeting.Participants), &participantList)
	}

	// 解析标签JSON
	var tagList []string
	if meeting.Tags != "" {
		_ = json.Unmarshal([]byte(meeting.Tags), &tagList)
	}

	// 构建响应
	dialogResList := make([]dto.MeetingMdtDialogRes, 0, len(dialogs))
	for _, d := range dialogs {
		dialogResList = append(dialogResList, dto.MeetingMdtDialogRes{MeetingMdtDialog: d})
	}

	res := &dto.MeetingMdtDetailRes{
		MeetingMdt:      meeting,
		Dialogs:         dialogResList,
		ParticipantList: participantList,
		TagList:         tagList,
	}

	results.ResObj(c, res, nil)
}

// Save 创建会议 /meeting/mdt/save
func (s *Mdt) Save(c *gin.Context) {
	req := gf.ReqBody(c, &dto.MeetingMdtCreateReq{})

	meeting := &biz.MeetingMdt{
		Title:        req.Title,
		Description:  req.Description,
		HostId:       req.HostId,
		HostName:     req.HostName,
		StartTime:    req.StartTime,
		EndTime:      req.EndTime,
		Status:       biz.MeetingStatusPending,
		Participants: "[]", // JSON类型必须有有效的默认值
		Tags:         "[]", // JSON类型必须有有效的默认值
	}

	// 序列化标签
	if len(req.Tags) > 0 {
		tagsJson, _ := json.Marshal(req.Tags)
		meeting.Tags = string(tagsJson)
	}

	_, err := s.svc.Insert(c, meeting)
	if err != nil {
		results.Failed(c, "创建会议失败", err)
		return
	}
	// 返回新创建会议的ID（GORM会自动回填ID到meeting结构体中）
	results.Success(c, "创建成功", gin.H{"id": meeting.Id}, nil)
}

// Update 更新会议 /meeting/mdt/update
func (s *Mdt) Update(c *gin.Context) {
	req := gf.ReqBody(c, &dto.MeetingMdtUpdateReq{})

	meeting := &biz.MeetingMdt{}
	meeting.Id = req.Id
	meeting.Title = req.Title
	meeting.Description = req.Description
	meeting.HostId = req.HostId
	meeting.HostName = req.HostName
	meeting.StartTime = req.StartTime
	meeting.EndTime = req.EndTime

	if req.Status != nil {
		meeting.Status = *req.Status
	}

	// 序列化标签
	if len(req.Tags) > 0 {
		tagsJson, _ := json.Marshal(req.Tags)
		meeting.Tags = string(tagsJson)
	}

	res, err := s.svc.Update(c, meeting)
	results.ResSave(c, res, err)
}

// Del 删除会议 /meeting/mdt/del
func (s *Mdt) Del(c *gin.Context) {
	ids := gf.ReqBody(c, &base.Ids{})
	res, err := s.svc.DeleteBatch(c, ids)
	results.ResDel(c, res, err)
}

// StartMeeting 开始会议 /meeting/mdt/startMeeting [POST]
func (s *Mdt) StartMeeting(c *gin.Context) {
	idStr := c.DefaultQuery("id", "")
	id := anyx.ToInt64(idStr)

	if id == 0 {
		results.ResError(c, fmt.Errorf("缺少会议ID"))
		return
	}

	// 获取会议检查状态
	meeting, err := s.svc.GetById(c, id)
	if err != nil {
		results.ResError(c, err)
		return
	}

	if meeting.Status != biz.MeetingStatusPending {
		results.ResError(c, fmt.Errorf("会议状态不允许开始"))
		return
	}

	// 更新会议状态
	updateMeeting := &biz.MeetingMdt{}
	updateMeeting.Id = id
	updateMeeting.Status = biz.MeetingStatusInProgress

	res, err := s.svc.Update(c, updateMeeting)
	results.ResSave(c, res, err)
}

// EndMeeting 结束会议 /meeting/mdt/endMeeting [POST]
func (s *Mdt) EndMeeting(c *gin.Context) {
	idStr := c.DefaultQuery("id", "")
	id := anyx.ToInt64(idStr)

	if id == 0 {
		results.ResError(c, fmt.Errorf("缺少会议ID"))
		return
	}

	// 获取会议检查状态
	meeting, err := s.svc.GetById(c, id)
	if err != nil {
		results.ResError(c, err)
		return
	}

	if meeting.Status != biz.MeetingStatusInProgress {
		results.ResError(c, fmt.Errorf("会议状态不允许结束"))
		return
	}

	// 更新会议状态
	updateMeeting := &biz.MeetingMdt{}
	updateMeeting.Id = id
	updateMeeting.Status = biz.MeetingStatusEnded

	res, err := s.svc.Update(c, updateMeeting)
	results.ResSave(c, res, err)
}

// GetDialogs 获取对话列表 /meeting/mdt/getDialogs
func (s *Mdt) GetDialogs(c *gin.Context) {
	meetingIdStr := c.DefaultQuery("meetingId", "")
	meetingId := anyx.ToInt64(meetingIdStr)
	dialogs, err := s.dialogSvc.ListByField(c, "meeting_id", meetingId)
	results.ResObj(c, dialogs, err)
}

// SaveDialog 保存对话（实时识别时调用）/meeting/mdt/saveDialog
func (s *Mdt) SaveDialog(c *gin.Context) {
	req := gf.ReqBody(c, &dto.MeetingMdtDialogCreateReq{})

	dialog := &biz.MeetingMdtDialog{
		MeetingId:        req.MeetingId,
		Seq:              req.Seq,
		SpeakerId:        req.SpeakerId,
		SpeakerName:      req.SpeakerName,
		SpeakerRole:      req.SpeakerRole,
		Recognized:       req.Recognized,
		RecognitionNote:  req.RecognitionNote,
		RecognitionScore: req.RecognitionScore,
		SpeakTime:        req.SpeakTime,
		StartOffset:      req.StartOffset,
		EndOffset:        req.EndOffset,
		DurationMs:       req.DurationMs,
		Text:             req.Text,
		AudioPath:        req.AudioPath,
	}

	res, err := s.dialogSvc.Insert(c, dialog)
	if err == nil {
		// 更新会议对话数
		go s.updateDialogCount(c, req.MeetingId)
	}
	results.ResSave(c, res, err)
}

// AssignSpeaker 指定发言人 /meeting/mdt/assignSpeaker
func (s *Mdt) AssignSpeaker(c *gin.Context) {
	req := gf.ReqBody(c, &dto.MeetingMdtAssignSpeakerReq{})

	dialog := &biz.MeetingMdtDialog{}
	dialog.Id = req.DialogId
	dialog.SpeakerId = &req.SpeakerId
	dialog.SpeakerName = req.SpeakerName
	dialog.SpeakerRole = req.SpeakerRole
	dialog.Recognized = biz.RecognizedManual
	dialog.RecognitionNote = "已人工确认身份"

	res, err := s.dialogSvc.Update(c, dialog)
	results.ResSave(c, res, err)
}

// GenerateSummary 生成AI总结 /meeting/mdt/generateSummary
func (s *Mdt) GenerateSummary(c *gin.Context) {
	idStr := c.DefaultQuery("id", "")
	id := anyx.ToInt64(idStr)

	// 更新总结状态为生成中
	meeting := &biz.MeetingMdt{}
	meeting.Id = id
	meeting.SummaryStatus = biz.SummaryStatusGenerating
	_, err := s.svc.Update(c, meeting)
	if err != nil {
		results.ResError(c, err)
		return
	}

	// 异步调用生成总结
	go func() {
		s.generateSummaryInternal(id)
	}()

	res := &dto.MeetingMdtSummaryRes{
		Status:  biz.SummaryStatusGenerating,
		Message: "AI正在生成总结...",
	}
	results.ResObj(c, res, nil)
}

// generateSummaryInternal 内部生成总结方法
func (s *Mdt) generateSummaryInternal(meetingId int64) {
	defer func() {
		if r := recover(); r != nil {
			// 恢复panic，更新状态为失败
			meeting := &biz.MeetingMdt{}
			meeting.Id = meetingId
			meeting.SummaryStatus = biz.SummaryStatusNone
			_, _ = s.svc.Update(context.Background(), meeting)
		}
	}()

	ctx := context.Background()

	// 获取会议详情
	meeting, err := s.svc.GetById(ctx, meetingId)
	if err != nil {
		return
	}

	// 获取对话列表
	dialogs, err := s.dialogSvc.ListByField(ctx, "meeting_id", meetingId)
	if err != nil {
		return
	}

	// 构建请求数据
	dialogList := make([]map[string]interface{}, 0, len(dialogs))
	for _, d := range dialogs {
		var speakTime string
		if d.SpeakTime != nil {
			speakTime = d.SpeakTime.String()
		}
		dialogList = append(dialogList, map[string]interface{}{
			"speaker_name": d.SpeakerName,
			"speaker_role": d.SpeakerRole,
			"speak_time":   speakTime,
			"text":         d.Text,
		})
	}

	reqBody := map[string]interface{}{
		"meeting_id": meetingId,
		"dialogs":    dialogList,
		"meeting_info": map[string]interface{}{
			"title":       meeting.Title,
			"description": meeting.Description,
			"host_name":   meeting.HostName,
		},
	}

	// 调用Python后端生成总结
	py := config.Inst.App.Micro[pyVoiceServer].Host
	target := py + "/meeting/mdt/generate-summary"

	request := httpclient.NewRequest(target)
	request.Timeout(time.Second * 120)
	res := request.PostJson(jsonx.Marshal(reqBody))
	body, err := res.BodyToMap()

	updateMeeting := &biz.MeetingMdt{}
	updateMeeting.Id = meetingId

	if err != nil {
		updateMeeting.SummaryStatus = biz.SummaryStatusNone
	} else if summary, ok := body["summary"].(string); ok && summary != "" {
		updateMeeting.Summary = summary
		updateMeeting.SummaryStatus = biz.SummaryStatusDone
	} else {
		updateMeeting.SummaryStatus = biz.SummaryStatusNone
	}

	_, _ = s.svc.Update(ctx, updateMeeting)
}

// GetSummaryStatus 获取总结状态 /meeting/mdt/getSummaryStatus
func (s *Mdt) GetSummaryStatus(c *gin.Context) {
	idStr := c.DefaultQuery("id", "")
	id := anyx.ToInt64(idStr)

	meeting, err := s.svc.GetById(c, id)
	if err != nil {
		results.ResError(c, err)
		return
	}

	res := &dto.MeetingMdtSummaryRes{
		Status:  meeting.SummaryStatus,
		Summary: meeting.Summary,
	}

	switch meeting.SummaryStatus {
	case biz.SummaryStatusNone:
		res.Message = "尚未生成总结"
	case biz.SummaryStatusGenerating:
		res.Message = "AI正在生成总结..."
	case biz.SummaryStatusDone:
		res.Message = "总结已生成"
	}

	results.ResObj(c, res, nil)
}

// updateDialogCount 更新会议对话数
func (s *Mdt) updateDialogCount(c *gin.Context, meetingId int64) {
	cond := base.NewCond()
	cond.Where(meetingId, "meeting_id = ?", meetingId)
	count, err := s.dialogSvc.Count(c, cond)
	if err != nil {
		return
	}
	meeting := &biz.MeetingMdt{}
	meeting.Id = meetingId
	meeting.DialogCount = count
	_, _ = s.svc.Update(c, meeting)
}

// MatchSpeaker 声纹匹配 /meeting/mdt/matchSpeaker
// 代理到Python后端
func (s *Mdt) MatchSpeaker(c *gin.Context) {
	py := config.Inst.App.Micro[pyVoiceServer].Host
	target := py + "/meeting/mdt/match-speaker"

	// 获取请求体
	var reqBody map[string]interface{}
	if err := c.ShouldBindJSON(&reqBody); err != nil {
		results.ResError(c, err)
		return
	}

	// 转发到Python后端
	request := httpclient.NewRequest(target)
	request.Timeout(time.Second * 30)
	res := request.PostJson(jsonx.Marshal(reqBody))
	body, err := res.BodyToMap()
	results.ResObj(c, body, err)
}

// GenerateSummaryAsync 异步生成AI总结 /meeting/mdt/generateSummaryAsync
// 代理到Python后端进行实际的AI生成
func (s *Mdt) GenerateSummaryAsync(c *gin.Context) {
	idStr := c.DefaultQuery("id", "")
	id := anyx.ToInt64(idStr)

	// 获取会议详情和对话列表
	meeting, err := s.svc.GetById(c, id)
	if err != nil {
		results.ResError(c, err)
		return
	}

	dialogs, err := s.dialogSvc.ListByField(c, "meeting_id", id)
	if err != nil {
		results.ResError(c, err)
		return
	}

	// 构建请求数据
	dialogList := make([]map[string]interface{}, 0, len(dialogs))
	for _, d := range dialogs {
		var speakTime string
		if d.SpeakTime != nil {
			speakTime = d.SpeakTime.String()
		}
		dialogList = append(dialogList, map[string]interface{}{
			"speaker_name": d.SpeakerName,
			"speaker_role": d.SpeakerRole,
			"speak_time":   speakTime,
			"text":         d.Text,
		})
	}

	reqBody := map[string]interface{}{
		"meeting_id": id,
		"dialogs":    dialogList,
		"meeting_info": map[string]interface{}{
			"title":       meeting.Title,
			"description": meeting.Description,
			"host_name":   meeting.HostName,
		},
	}

	// 调用Python后端生成总结
	py := config.Inst.App.Micro[pyVoiceServer].Host
	target := py + "/meeting/mdt/generate-summary"

	request := httpclient.NewRequest(target)
	request.Timeout(time.Second * 60)
	res := request.PostJson(jsonx.Marshal(reqBody))
	body, err := res.BodyToMap()

	if err != nil {
		// 更新状态为失败
		updateMeeting := &biz.MeetingMdt{}
		updateMeeting.Id = id
		updateMeeting.SummaryStatus = biz.SummaryStatusNone
		_, _ = s.svc.Update(c, updateMeeting)
		results.ResError(c, err)
		return
	}

	// 更新会议总结
	if summary, ok := body["summary"].(string); ok && summary != "" {
		updateMeeting := &biz.MeetingMdt{}
		updateMeeting.Id = id
		updateMeeting.Summary = summary
		updateMeeting.SummaryStatus = biz.SummaryStatusDone
		_, _ = s.svc.Update(c, updateMeeting)
	}

	results.ResObj(c, body, nil)
}

// Update_dialog 更新对话内容 /meeting/mdt/update_dialog
func (s *Mdt) Update_dialog(c *gin.Context) {
	req := gf.ReqBody(c, &dto.MeetingMdtDialogUpdateReq{})

	// 获取原对话
	dialog, err := s.dialogSvc.GetById(c, req.Id)
	if err != nil {
		results.ResError(c, err)
		return
	}
	if dialog == nil {
		results.ResError(c, fmt.Errorf("对话不存在"))
		return
	}

	// 更新文本
	updateDialog := &biz.MeetingMdtDialog{}
	updateDialog.Id = req.Id
	updateDialog.Text = req.Text

	res, err := s.dialogSvc.Update(c, updateDialog)
	results.ResSave(c, res, err)
}

// ClearDialogs 清空会议对话记录 /meeting/mdt/clearDialogs [POST]
// 用于会议开始后清除杂音等无效识别结果，重新开始记录
func (s *Mdt) ClearDialogs(c *gin.Context) {
	meetingIdStr := c.DefaultQuery("meetingId", "")
	meetingId := anyx.ToInt64(meetingIdStr)

	if meetingId == 0 {
		results.ResError(c, fmt.Errorf("缺少会议ID"))
		return
	}

	// 获取会议检查状态
	meeting, err := s.svc.GetById(c, meetingId)
	if err != nil {
		results.ResError(c, err)
		return
	}

	// 只允许在会议进行中时清空
	if meeting.Status != biz.MeetingStatusInProgress {
		results.ResError(c, fmt.Errorf("只有进行中的会议才能清空对话记录"))
		return
	}

	// 删除该会议的所有对话记录
	deletedCount, err := s.dialogSvc.DeleteByField(c, "meeting_id", meetingId)
	if err != nil {
		results.ResError(c, err)
		return
	}

	// 更新会议对话数为0
	updateMeeting := &biz.MeetingMdt{}
	updateMeeting.Id = meetingId
	updateMeeting.DialogCount = 0
	_, _ = s.svc.Update(c, updateMeeting)

	// 返回删除数量
	results.ResObj(c, map[string]interface{}{
		"deletedCount": deletedCount,
	}, nil)
}

// GetStaffList 获取人员列表（用于发言人选择） /meeting/mdt/getStaffList
// 复用声纹角色用户列表
func (s *Mdt) GetStaffList(c *gin.Context) {
	// 声纹角色ID，与 voice/print 保持一致
	const PrintRoleId = 7

	// 获取有声纹角色的用户ID列表
	cond := base.NewCond()
	cond.Where(true, "role_id", PrintRoleId)
	rs, _ := s.BusinessAuthRoleAccess.List(c, cond)
	uids := collx.ArrayMap(rs, func(v *core.BusinessAuthRoleAccess) int64 {
		return v.Uid
	})

	if len(uids) == 0 {
		results.Success(c, "获取成功", []dto.MeetingParticipant{}, nil)
		return
	}

	// 查询用户信息
	cond2 := base.NewCond()
	cond2.Where(true, "id", uids)
	cond2.Fields = "id,name,username,dept_id,company"
	cond2.Order = "id asc"
	list, err := s.BusinessAccount.List(c, cond2)
	if err != nil {
		results.ResError(c, err)
		return
	}

	// 转换为参会人员格式
	staffList := make([]dto.MeetingParticipant, 0, len(list))
	for _, u := range list {
		staffList = append(staffList, dto.MeetingParticipant{
			UserId:     u.Id,
			UserName:   u.Name,
			Department: u.Company, // 使用公司字段作为部门
			Role:       "",        // 角色由前端指定
		})
	}

	results.Success(c, "获取成功", staffList, nil)
}

// Perms 权限配置
func (s *Mdt) Perms() map[string][]gin.HandlerFunc {
	return nil
}
