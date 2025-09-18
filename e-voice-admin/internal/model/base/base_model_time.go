package base

import "gofly/pkg/json"

// IdModel 只有Id字段
type TimeModel struct {
	IdModel
	CreateTime *json.JsonTime `gorm:"column:create_time;comment:创建时间;autoCreateTime" json:"createTime"`
	UpdateTime *json.JsonTime `gorm:"column:update_time;comment:更新时间;autoUpdateTime" json:"updateTime"`
}

func (b *TimeModel) SetCreatorInfo(u *SysUser) {
	b.CreateTime = json.NowJsonTime()
	b.SetUpdaterInfo(u)
}
func (b *TimeModel) SetUpdaterInfo(*SysUser) {
	b.UpdateTime = json.NowJsonTime()
}
