package logx

import (
	"context"
	"fmt"
	"gofly/internal/config"
	"log"
	"log/slog"
)

type CustomTextHandler struct {
	slog.Handler
	l *log.Logger
}

func (h *CustomTextHandler) Enabled(ctx context.Context, l slog.Level) bool {
	return lc.GetLevel() <= l
}

func (h *CustomTextHandler) Handle(ctx context.Context, r slog.Record) error {
	level := r.Level.String()
	timeStr := r.Time.Format("2006-01-02 15:04:05.000")

	attrsStr := ""
	r.Attrs(func(a slog.Attr) bool {
		// 如果是source，则忽略key，简洁些
		if a.Key == slog.SourceKey {
			attrsStr += fmt.Sprintf("%s", a.Value.Any())
			return true
		}
		return true
	})
	if attrsStr != "" {
		attrsStr = " " + attrsStr
	}

	// 格式为：time [level] [key=value][key2=value2] : message
	timeStr = getColorMsg(timeStr, slog.LevelDebug)
	levelStr := getColorMsg(level, r.Level)
	attrsStr = getColorMsg(attrsStr, slog.LevelInfo)
	msgStr := getColorMsg(r.Message, r.Level)

	msg := fmt.Sprintf("%s [%s]%s \r\n  %s", timeStr, levelStr, attrsStr, msgStr)
	h.l.Println(msg)
	return nil
}

func getColorMsg(msg string, level slog.Level) string {

	if lc.Color != 1 {
		return msg
	}

	if level == slog.LevelDebug {
		return "\033[37m" + msg + "\033[0m"
	} else if level == slog.LevelInfo {
		return "\033[34m" + msg + "\033[0m"
	} else if level == slog.LevelWarn {
		return "\033[33m" + msg + "\033[0m"
	} else if level == slog.LevelError {
		return "\033[31m" + msg + "\033[0m"
	}
	return msg
}

func NewTextHandler(config config.Log) *CustomTextHandler {
	opts := &slog.HandlerOptions{
		Level:     config.GetLevel(),
		AddSource: true, // 统一由添加公共commonAttrs时判断添加
	}

	out := config.GetLogOut()
	return &CustomTextHandler{
		Handler: slog.NewTextHandler(out, opts),
		l:       log.New(out, "", 0),
	}
}
