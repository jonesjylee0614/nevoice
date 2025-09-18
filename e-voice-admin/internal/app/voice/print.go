package voice

import (
	"gofly/internal/config"
	"gofly/internal/domain/core_service"
	"gofly/internal/domain/dto"
	"gofly/internal/domain/service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/httpclient"
	"gofly/pkg/utils/jsonx"
	"gofly/pkg/utils/results"
	"time"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Print struct {
	svc                    *service.VoicePrint                  `inject:""`
	BusinessAccount        *core_service.BusinessAccount        `inject:""`
	BusinessAuthRoleAccess *core_service.BusinessAuthRoleAccess `inject:""`
}

var (
	// PrintRoleId 写死声纹角色id为26
	PrintRoleId = 26

	// 语音服务配置名
	pyVoiceServer = "py_voice"
)

func init() {
	gf.RegisterRoute(&Print{})
}

// GetUserList 查询拥有声纹角色的用户 /voice/print/getUserList
func (s *Print) GetUserList(c *gin.Context) {
	req := gf.ReqQuery(c, &dto.VoicePrintPageReq{})

	cond := base.NewCond()
	cond.Where(true, "role_id", PrintRoleId)
	rs, _ := s.BusinessAuthRoleAccess.List(c, cond)
	uids := collx.ArrayMap(rs, func(v *core.BusinessAuthRoleAccess) int64 {
		return v.Uid
	})

	cond2 := base.NewCond()
	cond2.Where(true, "id", uids)

	cond2.Fields = "id,status,name,username,nickname,avatar,tel,mobile,email,dept_id,remark,city,address,company,create_time,update_time"
	cond2.Order = "id asc"
	cond2.Where(req.Name, "username like ? or name like ?", "%"+req.Name+"%", "%"+req.Name+"%")
	list, err := s.BusinessAccount.Page(c, &req.IPage, cond2)
	results.ResPage(c, req.IPage, list, err)
}

// GetUserPrints 获取用户声纹列表 /voice/print/getUserPrints
func (s *Print) GetUserPrints(c *gin.Context) {
	req := gf.ReqQuery(c, &dto.VoiceUserPrintPageReq{})

	request := httpclient.NewRequest(config.Inst.App.Micro[pyVoiceServer].Host + "/prints/get_user_prints")
	params := map[string]any{
		"userid": req.UserId.Int64(),
		"page":   req.Page.Int64(),
		"limit":  req.PageSize.Int64(),
	}
	res := request.PostJson(jsonx.Marshal(params))
	r := &dto.VoiceUserPrintPageRes{}
	err := res.BodyToObj(r)
	req.IPage.Total = r.Total
	results.ResPage(c, req.IPage, r.Data, err)
}

// SaveUserPrint 保存用户声纹信息 /voice/print/saveUserPrint
func (s *Print) SaveUserPrint(c *gin.Context) {
	files, form := gf.ReqMultipartForm(c, "audio")

	request := httpclient.NewRequest(config.Inst.App.Micro[pyVoiceServer].Host + "/voice-register")
	request.Timeout(time.Second * 30)
	params := collx.M{
		"userid":   anyx.ToInt64(form.Value["userId"][0]),
		"username": form.Value["userName"][0],
	}
	res := request.PostMultipart(files, params)
	m, err := res.BodyToMap()
	results.ResObj(c, m, err)
}

// Del 删除 /voice/print/del
func (s *Print) Del(c *gin.Context) {
	req := gf.ReqBody(c, &dto.VoiceUserPrintDelReq{})

	request := httpclient.NewRequest(config.Inst.App.Micro[pyVoiceServer].Host + "/prints/del")
	params := collx.M{
		"userid": req.UserId.Int64(),
		"doc_id": req.DocId,
	}
	res := request.PostJson(jsonx.Marshal(params))
	m, err := res.BodyToMap()
	results.ResObj(c, m, err)
}

// Identify 声纹鉴定 /voice/print/identify
func (s *Print) Identify(c *gin.Context) {
	files, _ := gf.ReqMultipartForm(c, "audio")
	request := httpclient.NewRequest(config.Inst.App.Micro[pyVoiceServer].Host + "/prints/identify")
	request.Timeout(time.Second * 30)
	params := collx.M{}
	res := request.PostMultipart(files, params)

	r1 := &dto.VoiceUserPrintIdentifyRes{}
	err := res.BodyToObj(r1)
	assert.ErrIsNilAppendErr(err, "获取接口数据失败 %s")

	r2 := &dto.UserPrintIdentifyRes{}
	r2.Txt = r1.Txt
	userid := ensureUserId(r1.Data)
	user, err := s.BusinessAccount.GetById(c, userid)
	if err == nil {
		r2.User = user.Clean()
	} else {
		r2.User = core.UnknownUser()
	}
	results.ResObj(c, r2, nil)
}

// 从获取到的用户信息中,根据score筛选出最高得分的
func ensureUserId(arr []dto.VoiceUserPrintIdentifyData) int64 {

	// 未知用户
	if len(arr) == 0 {
		return 0
	}

	userIds := collx.ArrayMap(arr, func(val dto.VoiceUserPrintIdentifyData) int64 {
		return val.Userid.Int64()
	})

	// 如果只有一个userId,则直接返回
	if len(collx.Unique(userIds)) == 1 {
		return arr[0].Userid.Int64()
	}

	// 如果有多个userId,则计算每个人的score之和,分数多的为最终结果
	us := make(map[int64]float64)

	// 分数排名权重
	sm := map[int]float64{
		1: 2,
		2: 1.5,
		3: 1.3,
		4: 1.2,
		5: 1,
	}

	for i, v := range arr {
		userId := v.Userid.Int64()
		if _, has := us[userId]; !has {
			us[userId] = float64(0)
		}
		// 根据权重计算得分
		if q, has := sm[i+1]; has {
			us[userId] += v.Score * q
		} else {
			us[userId] += v.Score
		}
	}

	// 取分数最大的人
	userId, _ := findMaxValueKey(us)
	if userId > 0 {
		for _, data := range arr {
			if data.Userid.Int64() == userId {
				return userId
			}
		}
	}

	return 0
}

func findMaxValueKey(m map[int64]float64) (int64, bool) {
	var maxKey int64
	var maxValue float64
	var initialized bool

	for k, v := range m {
		if !initialized {
			maxKey = k
			maxValue = v
			initialized = true
		} else if v > maxValue {
			maxKey = k
			maxValue = v
		}
	}

	return maxKey, initialized // 如果 map 为空，返回 false
}

func (s *Print) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"print:base": {s.GetUserList, s.GetUserPrints},
		"print:edit": {s.SaveUserPrint},
		"print:del":  {s.Del},
	}
}
