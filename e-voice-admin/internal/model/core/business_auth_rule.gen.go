package core

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

const TableNameBusinessAuthRule = "business_auth_rule"

// BusinessAuthRule C端-菜单
type BusinessAuthRule struct {
	base.Model
	UID                int64  `gorm:"column:uid;not null;comment:添加用户" json:"uid"`                                                        // 添加用户
	Title              string `gorm:"column:title;not null;comment:菜单名称" json:"title"`                                                    // 菜单名称
	Locale             string `gorm:"column:locale;comment:中英文标题key" json:"locale"`                                                       // 中英文标题key
	OrderNo            int64  `gorm:"column:orderNo;not null;comment:排序" json:"orderNo"`                                                  // 排序
	Type               int64  `gorm:"column:type;not null;comment:类型 0=目录，1=菜单，2=按钮" json:"type"`                                         // 类型 0=目录，1=菜单，2=按钮
	Pid                int64  `gorm:"column:pid;not null;comment:上一级" json:"pid"`                                                         // 上一级
	Icon               string `gorm:"column:icon;not null;comment:图标" json:"icon"`                                                        // 图标
	RoutePath          string `gorm:"column:routePath;not null;comment:路由地址" json:"routePath"`                                            // 路由地址
	RouteName          string `gorm:"column:routeName;not null;comment:路由名称" json:"routeName"`                                            // 路由名称
	Component          string `gorm:"column:component;not null;comment:组件路径" json:"component"`                                            // 组件路径
	Redirect           string `gorm:"column:redirect;comment:重定向地址" json:"redirect"`                                                      // 重定向地址
	Permission         string `gorm:"column:permission;comment:权限标识" json:"permission"`                                                   // 权限标识
	Status             *int64 `gorm:"column:status;not null;comment:状态 0=启用1=禁用;default:0" json:"status"`                                 // 状态 0=启用1=禁用
	IsExt              *int64 `gorm:"column:isExt;not null;comment:是否外链 0=否1=是;default:0" json:"isExt"`                                   // 是否外链 0=否1=是
	Keepalive          *int64 `gorm:"column:keepalive;not null;comment:是否缓存 0=否1=是;default:0" json:"keepalive"`                           // 是否缓存 0=否1=是
	RequiresAuth       *int64 `gorm:"column:requiresAuth;not null;default:1;comment:是否需要登录鉴权 0=否1=是;default:1" json:"requiresAuth"`       // 是否需要登录鉴权 0=否1=是
	HideInMenu         *int64 `gorm:"column:hideInMenu;not null;comment:是否在左侧菜单中隐藏该项 0=否1=是;default:0" json:"hideInMenu"`                 // 是否在左侧菜单中隐藏该项 0=否1=是
	HideChildrenInMenu *int64 `gorm:"column:hideChildrenInMenu;not null;comment:强制在左侧菜单中显示单项 0=否1=是;default:0" json:"hideChildrenInMenu"` // 强制在左侧菜单中显示单项 0=否1=是
	ActiveMenu         *int64 `gorm:"column:activeMenu;not null;comment:高亮设置的菜单项 0=否1=是;default:1" json:"activeMenu"`                     // 高亮设置的菜单项 0=否1=是
	NoAffix            *int64 `gorm:"column:noAffix;not null;comment:如果设置为true，标签将不会添加到tab-bar中 0=否1=是;default:0" json:"noAffix"`         // 如果设置为true，标签将不会添加到tab-bar中 0=否1=是
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&BusinessAuthRule{})
}

// TableName BusinessAuthRule's table name
func (*BusinessAuthRule) TableName() string {
	return TableNameBusinessAuthRule
}
