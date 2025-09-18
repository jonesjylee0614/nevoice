package base

type IModel interface {
	GetPkVal() int64
	SetPkVal(int64)
	SetCreatorInfo(*SysUser)
	SetUpdaterInfo(*SysUser)
	IsLogicalDelete() bool
	SetLogicalDelete()
	IsBiz() bool   // 是否是saas多租户
	GetBiz() int64 // 获取saas租户id
}
