package core

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

const TableNameBusinessAccount = "business_account"

// BusinessAccount 用户端-用户信息
type BusinessAccount struct {
	base.Model
	UID           int64  `gorm:"column:uid;not null;comment:添加用户" json:"uid"`                                // 添加用户
	DeptID        int64  `gorm:"column:dept_id;not null;comment:部门id" json:"dept_id"`                        // 部门id
	Username      string `gorm:"column:username;not null;comment:用户账号" json:"username"`                      // 用户账号
	Password      string `gorm:"column:password;not null;comment:密码" json:"password"`                        // 密码
	Salt          string `gorm:"column:salt;not null;comment:密码盐" json:"salt"`                               // 密码盐
	Name          string `gorm:"column:name;not null;default:0;comment:姓名" json:"name"`                      // 姓名
	Nickname      string `gorm:"column:nickname;not null;comment:昵称" json:"nickname"`                        // 昵称
	Avatar        string `gorm:"column:avatar;not null;comment:头像" json:"avatar"`                            // 头像
	Tel           string `gorm:"column:tel;not null;comment:备用电话用户自己填写" json:"tel"`                          // 备用电话用户自己填写
	Mobile        string `gorm:"column:mobile;not null;comment:手机号码" json:"mobile"`                          // 手机号码
	Email         string `gorm:"column:email;not null;comment:邮箱" json:"email"`                              // 邮箱
	LastLoginIP   string `gorm:"column:lastLoginIp;not null;comment:最后登录IP" json:"lastLoginIp"`              // 最后登录IP
	LastLoginTime int64  `gorm:"column:lastLoginTime;not null;comment:最后登录时间" json:"lastLoginTime"`          // 最后登录时间
	Status        int64  `gorm:"column:status;not null;comment:状态0=正常，1=禁用" json:"status"`                   // 状态1=正常，2=禁用
	Validtime     int64  `gorm:"column:validtime;not null;comment:账号有效时间0=无限" json:"validtime"`              // 账号有效时间0=无限
	Address       string `gorm:"column:address;not null;comment:地址" json:"address"`                          // 地址
	City          string `gorm:"column:city;not null;comment:城市" json:"city"`                                // 城市
	Remark        string `gorm:"column:remark;not null;comment:描述" json:"remark"`                            // 描述
	Company       string `gorm:"column:company;not null;comment:公司名称" json:"company"`                        // 公司名称
	Province      string `gorm:"column:province;not null;comment:省份" json:"province"`                        // 省份
	Area          string `gorm:"column:area;not null;comment:地区" json:"area"`                                // 地区
	FileSize      uint64 `gorm:"column:fileSize;not null;default:3787456512;comment:附件存储空间" json:"fileSize"` // 附件存储空间
	Loginstatus   bool   `gorm:"column:loginstatus;comment:登录状态" json:"loginstatus"`                         // 登录状态
	AppKey        string `gorm:"column:appkey;comment:appkey;uniqueIndex:unique_idx;type:varchar(50);" json:"appKey"`
	AppKeySecret  string `gorm:"column:appKeySecret;comment:appKeySecret;type:varchar(100);" json:"appKeySecret"`
}

func UnknownUser() *BusinessAccount {
	return &BusinessAccount{
		Name:     "未知",
		Username: "未知",
		Nickname: "未知",
	}
}
func (a *BusinessAccount) Clean() *BusinessAccount {
	a.Password = ""
	a.Salt = ""

	return a
}

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&BusinessAccount{})
}

// TableName BusinessAccount's table name
func (*BusinessAccount) TableName() string {
	return TableNameBusinessAccount
}
