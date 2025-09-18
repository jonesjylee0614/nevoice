package user

import (
	"cmp"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/core"
	"gofly/pkg/utils/dt"

	"github.com/gin-gonic/gin"
)

// 获取权限菜单
func GetMenuArray(c *gin.Context, svc *core_service.BusinessAuthRule, menus []*core.BusinessAuthRule, parentId int64) []dt.Map {
	var returnList []dt.Map
	for _, v := range menus {
		if v.Pid == parentId {
			midItem := map[string]interface{}{
				"path":      v.RoutePath,
				"name":      v.RouteName,
				"component": v.Component,
			}
			children := GetMenuArray(c, svc, menus, v.Id)
			if children != nil {
				midItem["children"] = children
			}
			//1.标题
			meta := map[string]interface{}{
				"locale": cmp.Or(v.Locale, v.Title),
				"id":     v.Id,
			}
			//2.重定向
			if v.Redirect != "" {
				midItem["redirect"] = v.Redirect
			}
			//3.隐藏子菜单
			if *v.HideChildrenInMenu == 1 {
				meta["hideChildrenInMenu"] = true
			}

			//3.图标
			if v.Icon != "" {
				meta["icon"] = v.Icon
			}
			//4.缓存
			if *v.Keepalive != 1 {
				meta["ignoreCache"] = true
			}
			//5.隐藏菜单
			if *v.HideInMenu == 1 {
				meta["hideInMenu"] = true
			}
			//6.在标签隐藏
			if *v.NoAffix == 1 {
				meta["noAffix"] = true
			}
			//7.详情页在本业打开-用于配置详情页时左侧激活的菜单路径
			if *v.ActiveMenu == 1 {
				meta["activeMenu"] = true
			}
			//8.是否需要登录鉴权
			if *v.RequiresAuth == 1 {
				meta["requiresAuth"] = true
			}

			//赋值
			midItem["meta"] = meta
			returnList = append(returnList, midItem)
		}
	}
	return returnList
}
