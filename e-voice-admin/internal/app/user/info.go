package user

import (
	"gofly/internal/domain/core_service"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"math/rand"

	"github.com/gin-gonic/gin"
)

// 用于自动注册路由
type Info struct {
	CommonConfigSvc *core_service.CommonConfig `inject:""`
}

func init() {
	gf.RegisterRoute(&Info{})
}

/**
*  1获取动态
 */
type LsActivity struct {
	Id          int    `json:"id"`
	Title       string `json:"title"`
	Description string `json:"description"`
	Avatar      string `json:"avatar"`
}

// LatestActivity /user/info/latestActivity
func (api *Info) LatestActivity(c *gin.Context) {

	rootUrl := api.CommonConfigSvc.GetRootUrl(c)
	if rootUrl != "" {
		avatar := rootUrl + "resource/staticfile/avatar.png"
		list := []LsActivity{
			{
				Id:          1,
				Title:       "发布了项目 GoFly 系统",
				Description: "企业级产品设计系统",
				Avatar:      avatar,
			},
			{
				Id:          2,
				Title:       "发布了项目 GoFly 系统",
				Description: "企业级产品设计系统",
				Avatar:      avatar,
			},
		}
		results.Success(c, "获取动态", list, nil)
	} else {
		results.Success(c, "获取动态", make([]interface{}, 0), nil)
	}
}

/**
*项目
 */
type UserItem struct {
	Id     int    `json:"id"`
	Name   string `json:"name"`
	Email  string `json:"email"`
	Avatar string `json:"avatar"`
}
type projectItem struct {
	Id           int        `json:"id"`
	Name         string     `json:"name"`
	Description  string     `json:"description"`
	PeopleNumber int        `json:"peopleNumber"`
	Contributors []UserItem `json:"contributors"`
}

// ProjectList /user/info/projectList
func (api *Info) ProjectList(c *gin.Context) {
	rootUrl := api.CommonConfigSvc.GetRootUrl(c)
	avatar := rootUrl + "resource/staticfile/avatar.png"
	userlist := []UserItem{
		{
			Id:     1,
			Name:   "黄攻略",
			Email:  "gofly@163.com",
			Avatar: avatar,
		},
		{
			Id:     2,
			Name:   "黄攻略",
			Email:  "gofly@163.com",
			Avatar: avatar,
		},
	}
	list := []projectItem{
		{
			Id:           1,
			Name:         "黄攻略",
			Description:  "gofly@163.com",
			PeopleNumber: rand.Intn(50),
			Contributors: userlist,
		},
		{
			Id:           2,
			Name:         "老子",
			Description:  "gofly@163.com",
			PeopleNumber: rand.Intn(50),
			Contributors: userlist,
		},
		{
			Id:           3,
			Name:         "孔子",
			Description:  "gofly@163.com",
			PeopleNumber: rand.Intn(50),
			Contributors: userlist,
		},
	}
	results.Success(c, "项目", list, nil)
}

/**
* 我的团队
 */
type teamItem struct {
	Id           int    `json:"id"`
	Avatar       string `json:"avatar"`
	Name         string `json:"name"`
	PeopleNumber int    `json:"peopleNumber"`
}

// TeamList /user/info/teamList
func (api *Info) TeamList(c *gin.Context) {

	rootUrl := api.CommonConfigSvc.GetRootUrl(c)
	avatar := rootUrl + "resource/staticfile/avatar.png"
	list := []teamItem{
		{
			Id:           1,
			Avatar:       avatar,
			Name:         "GoFly智能应用团队",
			PeopleNumber: rand.Intn(50),
		},
		{
			Id:           2,
			Avatar:       avatar,
			Name:         "企业级产品设计团队",
			PeopleNumber: rand.Intn(50),
		},
		{
			Id:           3,
			Avatar:       avatar,
			Name:         "前端/UE小分队",
			PeopleNumber: rand.Intn(50),
		},
	}
	results.Success(c, "我的团队", list, nil)
}
func (api *Info) Perms() map[string][]gin.HandlerFunc {
	return nil
}
