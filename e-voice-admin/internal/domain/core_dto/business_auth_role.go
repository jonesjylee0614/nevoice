package core_dto

import (
	"gofly/internal/model/core"
)

type BusinessAuthRoleSaveReq struct {
	*core.BusinessAuthRole
	Menu []int64 `json:"menu"`
}
