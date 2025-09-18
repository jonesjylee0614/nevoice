package core_dto

import (
	"gofly/internal/model/core"
)

type CommonGenerateCodeListField struct {
	*core.CommonGeneratecodeField
	Required bool `json:"required"`
	IsForm   bool `json:"isform"`
	IsList   bool `json:"islist"`
	IsOrder  bool `json:"isorder"`
	IsSearch bool `json:"issearch"`
}
