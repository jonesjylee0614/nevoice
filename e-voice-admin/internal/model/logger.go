package model

import (
	"context"
	"gofly/pkg/logx"
	"time"

	"gorm.io/gorm/logger"
)

type Logger struct {
	LogLevel logger.LogLevel
}

var _ logger.Interface = (*Logger)(nil)

func (l *Logger) Info(ctx context.Context, s string, i ...interface{}) {
	if l.LogLevel < logger.Info {
		return
	}
	logx.Infof(s, i...)
}

func (l *Logger) Warn(ctx context.Context, s string, i ...interface{}) {
	if l.LogLevel < logger.Warn {
		return
	}
	logx.Warnf(s, i...)
}

func (l *Logger) Error(ctx context.Context, s string, i ...interface{}) {
	if l.LogLevel < logger.Error {
		return
	}
	logx.Errorf(s, i...)
}

func (l *Logger) Trace(ctx context.Context, begin time.Time, fc func() (sql string, rowsAffected int64), err error) {
	if l.LogLevel <= logger.Silent {
		return
	}
	elapsed := time.Since(begin)
	sql, rows := fc()
	i := 8
	if rows == -1 {
		logx.Infofi("[%.3fms] - %s", i, float64(elapsed.Nanoseconds())/1e6, sql)
	} else {
		logx.Infofi("[%.3fms] [rows:%v] %s", i, float64(elapsed.Nanoseconds())/1e6, rows, sql)
	}
}

func (l *Logger) LogMode(level logger.LogLevel) logger.Interface {
	l.LogLevel = level
	return l
}
