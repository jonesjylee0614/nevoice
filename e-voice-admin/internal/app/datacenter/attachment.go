package datacenter

import (
	"fmt"
	"gofly/internal/domain/core_dto"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/filex"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"strings"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Attachment struct {
	BusinessAccountSvc   *core_service.BusinessAccount    `inject:""`
	svc                  *core_service.BusinessAttachment `inject:""`
	CommonConfigSvc      *core_service.CommonConfig       `inject:""`
	CommonPictureSvc     *core_service.CommonPicture      `inject:""`
	CommonPictureCateSvc *core_service.CommonPictureCate  `inject:""`
}

func init() {
	gf.RegisterRoute(&Attachment{})
}

// Get_list 获取列表 /datacenter/attachment/get_list
func (s *Attachment) Get_list(c *gin.Context) {
	user := s.BusinessAccountSvc.GetSysUser(c)

	req := gf.ReqQuery(c, &core_dto.AttachmentPage{})

	cond := base.NewCond()
	cond.Fields = "id,url,type,title,mimetype,cover_url,create_time,pid"
	cond.Order = "id desc"
	cond.Where(true, "type != ?", 1)
	cond.Where(req.Status, "status", req.Status)
	cond.Where(req.Name, "name like ?", "%"+req.Name+"%")
	if req.CreatedTime != "" {
		datetimeArr := strings.Split(req.CreatedTime, ",")
		cond.Where(req.CreatedTime, "create_time between ? and ?", datetimeArr[0]+" 00:00:00", datetimeArr[1]+" 23:59:59")
	}
	list, err := s.svc.Page(c, &req.IPage, cond)

	if err != nil {
		results.Failed(c, err.Error(), nil)
	} else {
		rootUrl := s.CommonConfigSvc.GetRootUrl(c)
		for _, val := range list {
			if rootUrl != "" && val.URL != "" && !strings.HasPrefix(val.URL, "http") {
				val.URL = rootUrl + val.URL
			}
			if rootUrl != "" && val.CoverURL != "" && !strings.HasPrefix(val.CoverURL, "http") {
				val.CoverURL = rootUrl + val.CoverURL
			}
		}

		countCond := base.NewCond()
		countCond.Where(true, "type", 0)
		allNumber, _ := s.svc.Count(c, countCond)

		var useSize int64

		base.GormDb.Model(&core.BusinessAttachment{}).
			Where("type", 0).
			Select("sum(filesize) as useSize").
			Scan(&useSize)

		account, _ := s.BusinessAccountSvc.GetById(c, user.Id)

		datainfo := map[string]interface{}{"allnumber": allNumber, "usesize": useSize, "fileSize": account.FileSize}
		results.Success(c, "获取全部列表", map[string]interface{}{
			"datainfo": datainfo,
			"page":     req.IPage.Page,
			"pageSize": req.IPage.PageSize,
			"total":    req.IPage.Total,
			"items":    list}, nil)
	}
}

// Get_pictureCate 获取分类列表 /datacenter/attachment/get_pictureCate
func (s *Attachment) Get_pictureCate(c *gin.Context) {

	cond := base.NewCond()
	cond.Fields = "id,name,type"
	cond.Where(true, "status", 0)
	cond.Order = "weigh desc,id desc"

	list, err := s.CommonPictureCateSvc.List(c, cond)
	results.ResObj(c, list, err)
}

// Get_picture 获取图片库列表 /datacenter/attachment/get_picture
func (s *Attachment) Get_picture(c *gin.Context) {

	req := gf.ReqQuery(c, &core_dto.CommonPicturePage{})
	cond := base.NewCond()
	cond.Fields = "id,cid,url,type,title,mimetype,cover_url,create_time"
	cond.Order = "id desc"
	cond.Where(true, "status", 0)
	cond.Where(true, "type", req.Type)
	cond.Where(req.Cid, "type", req.Type)
	cond.Where(req.Title, "title like ?", "%"+req.Title+"%")
	if req.CreatedTime != "" {
		datetimeArr := strings.Split(req.CreatedTime, ",")
		cond.Where(req.CreatedTime, "create_time between ? and ?", datetimeArr[0]+" 00:00:00", datetimeArr[1]+" 23:59:59")
	}
	list, err := s.CommonPictureSvc.Page(c, &req.IPage, cond)
	if err != nil {
		results.Failed(c, err.Error(), nil)
	} else {
		rootUrl := s.CommonConfigSvc.GetRootUrl(c)
		for _, val := range list {
			if rootUrl != "" && val.URL != "" && !strings.HasPrefix(val.URL, "http") {
				val.URL = rootUrl + val.URL
			}
		}
		results.Success(c, "获取全部列表", map[string]interface{}{
			"page":     req.IPage.Page,
			"pageSize": req.IPage.PageSize,
			"total":    req.IPage.Total,
			"items":    list}, nil)
	}
}

// Save 保存 /datacenter/attachment/save
func (s *Attachment) Save(c *gin.Context) {

	entity := gf.ReqBody(c, &core.BusinessAttachment{})

	if entity.Id == 0 {

		cond := base.NewCond()
		cond.Where(true, "pid", entity.Pid)
		cond.Where(true, "title like ?", "%"+entity.Title+"%")
		count, err := s.svc.Count(c, cond)
		entity.Title = fmt.Sprintf("%s%v", entity.Title, count+1)

		_, err = s.svc.Insert(c, entity)
		assert.ErrIsNilAppendErr(err, "添加失败")
		//更新排序
		s.svc.UpdateWeigh(c, entity.Id)
		res, err := s.svc.GetById(c, entity.Id)
		results.ResObj(c, res, err)
	} else {
		res, err := s.svc.Update(c, entity)
		results.ResObj(c, res, err)
	}
}

// Del 删除 /datacenter/attachment/del
func (s *Attachment) Del(c *gin.Context) {

	req := gf.ReqBody(c, &base.Ids{})
	res, err := s.svc.DeleteBatch(c, req)
	assert.ErrIsNilAppendErr(err, "删除失败")

	results.Success(c, "删除成功！", res, nil)

	cond := base.NewCond()
	cond.Fields = "url"
	cond.Where(true, "id", req.Ids)
	cond.Where(true, "type != ", 1)
	list, _ := s.svc.List(c, cond)

	if len(list) > 0 {
		for _, val := range list {
			filex.DelFile(val.URL)
		}
	}
}

// Get_myFiles 获取我的附件 /datacenter/attachment/get_myFiles
func (s *Attachment) Get_myFiles(c *gin.Context) {
	//当前用户
	req := gf.ReqQuery(c, &core_dto.MyAttachmentReq{})

	cond1 := base.NewCond()
	cond1.Fields = "id,pid,name,title,type,url,filesize,mimetype,storage,cover_url,is_common"
	cond1.Order = "type desc,weigh desc,id desc"
	cond1.Where(true, "pid", req.Pid)
	cond1.Where(req.Searchword, "title like ?", "%"+req.Searchword+"%")
	cond1.Where(req.Filetype == "video", "type", 1, 2)
	cond1.Where(req.Filetype != "video", "type", 1, 0)

	list, err := s.svc.List(c, cond1)
	assert.ErrIsNilAppendErr(err, "加载数据失败")
	rootUrl := s.CommonConfigSvc.GetRootUrl(c)

	for _, val := range list {
		if rootUrl != "" && val.URL != "" && !strings.HasPrefix(val.URL, "http") {
			val.URL = rootUrl + val.URL
		}
		if rootUrl != "" && val.CoverURL != "" && !strings.HasPrefix(val.CoverURL, "http") {
			val.CoverURL = rootUrl + val.CoverURL
		}
	}

	cond := base.NewCond()
	cond.Where(true, "pid", req.Pid)
	cond.Where(true, "is_common", 1)
	cond.Fields = "id,pid,name,title,type,url,filesize,mimetype,storage,cover_url,is_common"
	cond.Order = "type desc,weigh desc,id desc"

	commonList, _ := s.svc.List(c, cond)

	if len(list) != 0 {
		list = append(list, commonList...)
	} else {
		list = commonList
	}
	var totalCount int64
	//获取目录菜单
	allids := getAllParentIds(c, s.svc, req.Pid)
	allids = append(allids, req.Pid)
	cond = base.NewCond()
	cond.Where(true, "id", allids)
	cond.Fields = "id,pid,title"

	dirmenu, err := s.svc.List(c, cond)

	results.ResObj(c, map[string]interface{}{
		"total":   totalCount,
		"dirmenu": dirmenu,
		"allids":  allids,
		"items":   list,
	}, err)
}

// 递归查所有的顶级pid
func getAllParentIds(c *gin.Context, BusinessAttachmentSvc *core_service.BusinessAttachment, id interface{}) []interface{} {
	var parentIds []interface{}
	entity, err := BusinessAttachmentSvc.GetById(c, id)
	if err == nil && nil != entity && entity.Pid != 0 {
		parentIds = append(parentIds, entity.Pid)
		parentIds = append(parentIds, getAllParentIds(c, BusinessAttachmentSvc, entity.Pid)...)
	}
	return parentIds
}

// UpImgPid 更新图片目录 /datacenter/attachment/upImgPid
func (s *Attachment) UpImgPid(c *gin.Context) {
	//获取post传过来的data
	req := gf.ReqBody(c, &core_dto.UpImgPidReq{})
	entity := &core.BusinessAttachment{
		Pid: req.Pid,
	}
	entity.Id = req.Imgid

	update, err := s.svc.Update(c, entity)
	results.ResSave(c, update, err)

}
func (s *Attachment) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"atta:base": {s.Get_list},
		"atta:del":  {s.Del},
	}
}
