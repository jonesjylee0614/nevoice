package voice

import (
	"gofly/internal/domain/core_service"
	"gofly/internal/domain/service"
)

// 用于自动注册路由
type MeetingOffline struct {
	svc                    *service.VoicePrint                  `inject:""`
	BusinessAccount        *core_service.BusinessAccount        `inject:""`
	BusinessAuthRoleAccess *core_service.BusinessAuthRoleAccess `inject:""`
}
