package logx

import (
	"context"
	"gofly/internal/config"
	"log"
	"log/slog"
	"time"
)

type CustomJSONHandler struct {
	slog.Handler
	l *log.Logger
}

func (h *CustomJSONHandler) Enabled(ctx context.Context, l slog.Level) bool {
	return lc.GetLevel() <= l
}

func NewJsonHandler(config config.Log) *CustomJSONHandler {
	replace := func(groups []string, a slog.Attr) slog.Attr {
		// 格式化时间.
		if a.Key == slog.TimeKey && len(groups) == 0 {
			return slog.Attr{Key: "time", Value: slog.StringValue(time.Now().Local().Format("2006-01-02 15:04:05.000"))}
		}
		return a
	}

	return &CustomJSONHandler{
		Handler: slog.NewJSONHandler(config.GetLogOut(), &slog.HandlerOptions{
			AddSource:   false, // 统一由添加公共commonAttrs时判断添加
			ReplaceAttr: replace,
		}),
		l: log.New(config.GetLogOut(), "", 0),
	}
}
