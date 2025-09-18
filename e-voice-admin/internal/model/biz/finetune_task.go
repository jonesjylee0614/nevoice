package biz

import (
	"gofly/internal/model"
	"gofly/internal/model/base"
)

// FinetuneTask 模型微调记录
type FinetuneTask struct {
	base.Model
	Name string `gorm:"size:200;comment:微调任务名;index" json:"name"`
	// 基础模型路径，可以根据已完成微调的模型进行微调
	BaseModelPath string `gorm:"size:1000;comment:基础模型路径" json:"baseModelPath"`
	// 训练完成后转移模型产物到新的路径，且记录此路径到 modelPath
	ModelPath string `gorm:"size:1000;comment:模型产物路径" json:"modelPath"`
	// 训练完成后保存训练日志
	LogPath string `gorm:"size:1000;comment:日志路径" json:"logPath"`
	// 同时只能有一个运行中的微调
	Status int `gorm:"comment:运行状态 1训练中 2训练完成 3未训练;type:int;default:3;index;" json:"status"`
}

var (
	StatusTraining   = 1 // 训练中
	StatusTrained    = 2 // 训练完成
	StatusNotTrained = 3 // 未训练
)

func init() {
	// 需要自动维护表结构
	model.AddInitModel(&FinetuneTask{})
}

func (v FinetuneTask) TableName() string {
	return "finetune_task"
}
