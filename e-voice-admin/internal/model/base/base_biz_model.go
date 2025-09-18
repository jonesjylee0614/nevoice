package base

// AppIdModel saas多租户id
type AppIdModel struct {
	DeleteModel
	AppId int64 `gorm:"column:app_id;comment:租户id" json:"appId"`
}

func (b *AppIdModel) IsBiz() bool   { return true }
func (b *AppIdModel) GetBiz() int64 { return b.AppId }
