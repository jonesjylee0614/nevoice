package logx

import (
	"cmp"
	"context"
	"fmt"
	"gofly/internal/config"
	"log/slog"
	"regexp"
	"runtime"
	"strings"

	"github.com/pkg/errors"
)

var (
	lc         config.Log
	versionReg = regexp.MustCompile(`@[^/]+`)
)

func init() {
	config.AddAfterConfigFn(InitLog)
}

func InitLog(c *config.Config) {
	lc = c.Log
	lc.SetLevel()
	lc.Filename = cmp.Or(lc.Filename, fmt.Sprintf("%s.log", config.Inst.App.Name))
	lc.MaxSize = cmp.Or(lc.MaxSize, 100) // 默认100M
	lc.MaxAge = cmp.Or(lc.MaxAge, 7)     // 默认7天

	// 如果输出日志到文件，取消彩色日志
	if lc.Filepath != "" {
		fmt.Println(fmt.Sprintf("启用了文件存放日志，请查看: %s/%s", lc.Filepath, lc.Filename))
		lc.Color = 2
	}
	var handler slog.Handler
	if lc.IsJsonType() {
		handler = NewJsonHandler(lc)
	} else {
		handler = NewTextHandler(lc)
	}
	slog.SetDefault(slog.New(handler))
	slog.SetLogLoggerLevel(lc.GetLevel())
}

func Printf(format string, args ...any) {
	Log(context.Background(), 4, slog.LevelInfo, fmt.Sprintf(format, args...))
}

func Debugf(format string, args ...any) {
	Log(context.Background(), 4, slog.LevelDebug, fmt.Sprintf(format, args...))
}

func Infof(format string, args ...any) {
	Log(context.Background(), 4, slog.LevelInfo, fmt.Sprintf(format, args...))
}

func Warnf(format string, args ...any) {
	Log(context.Background(), 4, slog.LevelWarn, fmt.Sprintf(format, args...))
}

func Debugfi(format string, i int, args ...any) {
	Log(context.Background(), i, slog.LevelDebug, fmt.Sprintf(format, args...))
}

func Infofi(format string, i int, args ...any) {
	Log(context.Background(), i, slog.LevelInfo, fmt.Sprintf(format, args...))
}

func Warnfi(format string, i int, args ...any) {
	Log(context.Background(), i, slog.LevelWarn, fmt.Sprintf(format, args...))
}

func ErrorNoStack(msg string) {
	Log(context.Background(), 4, slog.LevelError, msg)
}

func Error(msg string, err error) {
	Errori(msg, 5, err)
}

// 错误记录，并将堆栈信息添加至msg里，默认记录10个堆栈信息
func Errori(msg string, i int, err error) {

	err = errors.WithStack(err)
	errStack := fmt.Sprintf("%+v", err)
	// 从堆栈信息中找到logx.Error
	index := strings.Index(errStack, "/logx.Error")
	if index != -1 {
		errStack = errStack[index+1:]
	}

	// 从堆栈信息中删除logx.Error
	index = findNthIndex(errStack, '\n', 2)
	if index != -1 {
		errStack = errStack[index+1:]
	}

	msg = fmt.Sprintf("%s %s\n%s", msg, err.Error(), errStack)

	Log(context.Background(), i, slog.LevelError, msg)
}

func Errorf(format string, args ...any) {
	Errorfi(format, 5, args...)
}

func Errorfi(format string, i int, args ...any) {
	err := fmt.Errorf(format, args...)

	err = errors.WithStack(err)
	errStack := fmt.Sprintf("%+v", err)
	// 从堆栈信息中找到logx.Error
	index := strings.Index(errStack, "/logx.Error")
	if index != -1 {
		errStack = errStack[index+1:]
	}

	// 从堆栈信息中删除logx.Error
	index = findNthIndex(errStack, '\n', 2)
	if index != -1 {
		errStack = errStack[index+1:]
	}

	msg := fmt.Sprintf("%s\n%s", err.Error(), errStack)

	Log(context.Background(), i, slog.LevelError, msg)

}

func findNthIndex(s string, char rune, n int) int {
	index := -1
	for i, c := range s {
		if c == char {
			n--
			if n == 0 {
				index = i
				break
			}
		}
	}
	return index
}

func Panicf(format string, args ...any) {
	msg := fmt.Sprintf(format, args...)
	panic(msg)
}

func PanicError(err error) {
	Error("", err)
	panic(err)
}

func Log(ctx context.Context, i int, level slog.Level, msg string) {
	if lc.GetLevel() <= level {
		slog.Log(ctx, level, msg, getCommonAttrs(i)...)
	}
}

func getCommonAttrs(i int) []any {
	commonAttrs := make([]any, 0)

	var pcs [1]uintptr
	runtime.Callers(i, pcs[:]) //需要调试skip 直到拿到最初调用logx.xxx的地方
	fs := runtime.CallersFrames(pcs[:])
	f, _ := fs.Next()

	// 过滤框架包名
	filepath := f.File

	source := &Source{
		File: filepath,
		Line: f.Line,
	}

	commonAttrs = append(commonAttrs, slog.SourceKey, source)
	return commonAttrs
}

type Source struct {
	// Function is the package path-qualified function name containing the
	// source line. If non-empty, this string uniquely identifies a single
	// function in the program. This may be the empty string if not known.
	File string `json:"file"`
	// File and Line are the file name and line number (1-based) of the source
	// line. These may be the empty string and zero, respectively, if not known.
	Line int `json:"line"`
}

func (s Source) String() string {
	return fmt.Sprintf("%s:%d", s.File, s.Line)
}

// An Attr is a key-value pair.
type Attr = slog.Attr

// String returns an Attr for a string value.
func String(key, value string) Attr {
	return slog.String(key, value)
}

// Int64 returns an Attr for an int64.
func Int64(key string, value int64) Attr {
	return slog.Int64(key, value)
}

// Bool returns an Attr for an bool.
func Bool(key string, value bool) Attr {
	return slog.Bool(key, value)
}
