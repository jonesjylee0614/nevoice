package base

// IdModel 只有Id字段
type IdModel struct {
	Id int64 `gorm:"column:id;primaryKey;autoIncrement:true;comment:主键ID" json:"id"`
}

func (b *IdModel) GetPkVal() int64 {
	return b.Id
}
func (b *IdModel) SetPkVal(id int64) {
	b.Id = id
}
func (b *IdModel) SetCreatorInfo(*SysUser) {}
func (b *IdModel) SetUpdaterInfo(*SysUser) {}
func (b *IdModel) IsLogicalDelete() bool   { return false }
func (b *IdModel) SetLogicalDelete()       {}
func (b *IdModel) IsBiz() bool             { return false }
func (b *IdModel) GetBiz() int64           { return 0 }
