package core_dto

import (
	"gofly/internal/model/base"
	"gofly/internal/model/core"
)

type CommonGeneratecodePageReq struct {
	base.IPage
	Name string `form:"name" json:"name"`
}

type CommonGeneratecodeDel struct {
	Id        int64 `json:"id" binding:"required"`
	IsInstall int64 `json:"is_install"`
}

type CommonGeneratecodeSave struct {
	CodeData *core.CommonGeneratecode       `json:"codeData"`
	Fields   []*CommonGenerateCodeListField `json:"list"`
}
