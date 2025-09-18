package service

import (
	"context"
	"fmt"
	"gofly/internal/config"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"

	"github.com/gin-gonic/gin"
)

// FinetuneVoiceDetail 录音范文列表
type FinetuneVoiceDetail struct {
	base.DaoImpl[*biz.FinetuneVoiceDetail]
}

func init() {
	ioc.PrepareDao(new(FinetuneVoiceDetail))
}

func (s *FinetuneVoiceDetail) SaveByMeetingDetail(c context.Context, detail *biz.MeetingOfflineDetail) {

	// 根据会议详情id查询是否存在，是则赋值id
	vd := &biz.FinetuneVoiceDetail{
		VoicePath:       detail.WavPath,
		Text:            detail.Text,
		MeetingDetailId: detail.Id,
		MeetingId:       detail.MeetingId,
	}
	vd2, err := s.GetByField(c, "meeting_detail_id", vd.MeetingDetailId)
	if err == nil && vd2 != nil && vd2.Id != 0 {
		vd.Id = vd2.Id
	}
	_, _ = s.InsertOrUpdate(c, vd)
}

func (s *FinetuneVoiceDetail) DeleteByMeetingDetailId(c *gin.Context, id int64) {
	_, _ = s.DeleteByField(c, "meeting_detail_id", id)
}

func (s *FinetuneVoiceDetail) ListToBeFinetune(c *gin.Context) ([]*biz.FinetuneVoiceDetail, error) {
	cond := base.NewCond()
	cond.Where(true, "finetune_id <= 0")
	list, err := s.List(c, cond)
	if err != nil {
		return nil, err
	}
	// 组装成全路径
	for _, v := range list {
		v.VoicePath = fmt.Sprintf("%s/detail/%d/%s", config.Inst.Voice.MeetingPath, v.MeetingId, v.VoicePath)
	}
	return list, err
}
