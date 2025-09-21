package config

import (
	"io"
	"log/slog"
	"os"
	"path"
	"strings"

	"gopkg.in/natefinch/lumberjack.v2"
)

// 数据数据库配置
type DBconf struct {
	Driver   string `yaml:"driver"`
	Hostname string `yaml:"hostname"`
	Hostport string `yaml:"hostport"`
	Username string `yaml:"username"`
	Password string `yaml:"password"`
	Database string `yaml:"database"`
	Prefix   string `yaml:"prefix"`
}

// Redis配置
type Redis struct {
	Host     string `yaml:"host,omitempty"`
	Port     string `yaml:"port,omitempty"`
	Password string `yaml:"password,omitempty"`
	Db       int    `yaml:"db,omitempty"`
}

// 应用配置
type App struct {
	Name                string           `yaml:"name"`
	Port                string           `yaml:"port"`
	ContextPath         string           `yaml:"context-path,omitempty"` // 请求路径上下文
	Version             string           `yaml:"version"`
	Env                 string           `yaml:"env"`
	Apisecret           string           `yaml:"apisecret"`
	AllowCros           bool             `yaml:"allow-cros"`   // 是否允许跨域，设置后allow-origin才生效
	AllowOrigin         string           `yaml:"allow-origin"` // 允许的跨域请求源，默认*
	Allowurl            string           `yaml:"allowurl"`
	TokenOutTime        string           `yaml:"tokenouttime"` // token过期时间，分钟
	CPUnum              string           `yaml:"cpunum"`
	Domain              string           `yaml:"domain"`
	Vueobjroot          string           `yaml:"vueobjroot"`
	CompanyPrivateHouse string           `yaml:"companyPrivateHouse"`
	Rootview            string           `yaml:"rootview"`
	RunlogType          string           `yaml:"runlogtype"`
	NoVerifyTokenRoot   string           `yaml:"noVerifyTokenRoot"`
	NoVerifyAPIRoot     string           `yaml:"noVerifyAPIRoot"`
	NoVerifyToken       string           `yaml:"noVerifyToken"`
	NoVerifyAPI         string           `yaml:"noVerifyAPI"`
	ResMsgName          string           `yaml:"ResMsgName" default:"message"`        // 返回结果中msg字段的名称
	ResCodeName         string           `yaml:"ResCodeName" default:"code"`          // 返回结果中code字段的名称
	ResDataName         string           `yaml:"ResDataName" default:"data"`          // 返回结果中data字段的名称
	DefaultSuccessMsg   string           `yaml:"DefaultSuccessMsg" default:"success"` // 默认成功消息
	StartTime           int64            `yaml:"-"`
	Micro               map[string]Micro `yaml:"micro"` // 微服务配置
}

func (a *App) IsDev() bool {
	return strings.Contains(strings.ToLower(a.Env), "dev")
}

func (a *App) IsTest() bool {
	return strings.Contains(strings.ToLower(a.Env), "test")
}

func (a *App) IsProd() bool {
	return strings.Contains(strings.ToLower(a.Env), "prod")
}

// JWT验证
type Jwt struct {
	Secret string `json:"secret" yaml:"secret"`
	JwtTtl int64  `json:"jwt_ttl" yaml:"jwt_ttl"` // token 有效期（秒）
}

type Api struct {
	Enable       bool   `json:"enable" yaml:"enable"`
	Title        string `json:"title" yaml:"title,omitempty" default:"api文档"`              // 文档标题
	Version      string `json:"version" yaml:"version,omitempty" default:"1.0"`            // 文档版本
	Url          string `json:"url" yaml:"url,omitempty"`                                  // 接口地址
	IncludePaths string `json:"includePaths" yaml:"include-paths,omitempty" default:"/**"` // 允许访问文档的接口路径，如 /**(默认)
	ExcludePaths string `json:"excludePaths" yaml:"exclude-paths,omitempty"`               // 隐藏的接口路径,如 /sys/**，从include中排除
	Username     string `json:"username" yaml:"username,omitempty"`
	Password     string `json:"password" yaml:"password,omitempty"`
}

func (a Api) IsEnable() bool {
	// 生产环境强制不开启
	if Inst.App.IsProd() {
		return false
	}
	return a.Enable
}

type Log struct {
	Level   string     `yaml:"level"` // debug | info | warn | error ，默认 info
	level   slog.Level `yaml:"-"`     // 经计算后的日志等级
	leveled bool       `yaml:"-"`

	EnableSqlLog    bool `yaml:"enable-sql-log"`
	EnableIocLog    bool `yaml:"enable-ioc-log"`    // ioc 日志
	EnableRouterLog bool `yaml:"enable-router-log"` // 路由日志

	Type string `yaml:"type"` // 日志类型；text | json

	Filename string `yaml:"filename"` // 日志文件名 默认为项目名
	Filepath string `yaml:"filepath"` // 日志路径 不配置path则无文件输出，指定的目录需要有足够读写权限
	MaxSize  int    `yaml:"max-size"` // 日志文件的最大大小（以兆字节为单位）。当日志文件大小达到该值时，将触发切割操作，默认为 100 兆字节
	MaxAge   int    `yaml:"max-age"`  // 根据文件名中的时间戳，设置保留旧日志文件的最大天数。一天被定义为 24 小时
	Compress bool   `yaml:"compress"` // 是否使用 gzip 压缩方式压缩轮转后的日志文件

	Color int `yaml:"color"` // 是否允许颜色 1是 非1否

	writer io.Writer `yaml:"writer"`
}

// 获取日志输出源
func (c *Log) GetLogOut() io.Writer {
	if c.writer != nil {
		return c.writer
	}
	var writer io.Writer
	writer = os.Stdout
	// 设置文件路径，未配置则不启用日志文件
	if c.Filepath != "" {
		writer = &lumberjack.Logger{
			Filename:  path.Join(c.Filepath, c.Filename),
			MaxSize:   c.MaxSize,
			MaxAge:    c.MaxAge,
			Compress:  c.Compress,
			LocalTime: true,
		}
	}

	c.writer = writer
	return writer
}

// 获取日志级别
func (c *Log) GetLevel() slog.Level {
	if c.leveled {
		return c.level
	}

	c.leveled = true
	switch strings.ToLower(c.Level) {
	case "error":
		c.level = slog.LevelError
	case "warn", "warning":
		c.level = slog.LevelWarn
	case "info":
		c.level = slog.LevelInfo
	case "debug":
		c.level = slog.LevelDebug
	default:
		c.level = slog.LevelInfo
	}

	return c.level
}

func (c *Log) SetLevel() {
	c.level = c.GetLevel()
}

func (c *Log) IsJsonType() bool {
	return c.Type == "json"
}

func (c *Log) IsDebug() bool {
	return strings.ToLower(c.Level) == "debug"
}

type Micro struct {
	Host string `yaml:"host" default:"http://127.0.0.1:8210"`
}

type Voice struct {
	// 用户声纹存放路径 后面拼接用户id/声纹文件名即可访问
	PrintPath   string `yaml:"print-path" default:"/data/voice/print/"`
	MeetingPath string `yaml:"meeting-path" default:"/data/meeting/offline/"`

	FunAsrPath         string `yaml:"fun-asr-path" default:"/data/voice/FunASR/"`
	CondaPath          string `yaml:"conda-path" default:"/home/leozy/miniforge3/bin"`
	FunAsrCondaEnvName string `yaml:"fun-asr-conda-env-name" default:"FunASR"`
	CudaDevices        string `yaml:"cuda-devices" default:"0"`
	FunAsrOutputDir    string `yaml:"fun-asr-output-dir" default:"/data/voice/finetune/output"`
	ModelTest          string `yaml:"model-test" default:"/home/leozy/.cache/model/speech_test"`
	ModelTrain         string `yaml:"model-train" default:"/home/leozy/.cache/model/speech_train"`
}
