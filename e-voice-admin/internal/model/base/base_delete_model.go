package base

import "gofly/pkg/json"

// DeleteModel 逻辑删除
type DeleteModel struct {
	Model
	Deleted   bool           `gorm:"comment:是否删除;type:boolean;default:false" json:"deleted"`
	DeletedAt *json.JsonTime `gorm:"comment:删除时间" json:"deletedAt"`
}

func (b *DeleteModel) IsLogicalDelete() bool {
	return true
}
func (b *DeleteModel) SetLogicalDelete() {
	b.Deleted = true
	b.DeletedAt = json.NowJsonTime()
}
