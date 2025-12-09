package config

import (
	"flag"
	"fmt"
	"gofly/pkg/utils/structx"
	"os"
	"path/filepath"
	"time"

	"gopkg.in/yaml.v2"
)

type Config struct {
	DBconf DBconf `yaml:"dbconf"`
	Redis  Redis  `yaml:"redis"`
	App    App    `yaml:"app"`
	Api    Api    `yaml:"api"`
	Jwt    Jwt    `yaml:"jwt"`
	Log    Log    `yaml:"log"`
	Voice  Voice  `yaml:"voice"`
}

var Inst = &Config{}

type AfterConfigFn = func(*Config)

var afterConfigFns []func(*Config)

func AddAfterConfigFn(fn AfterConfigFn) {
	afterConfigFns = append(afterConfigFns, fn)
}

type StartParams struct {
	// 服务名
	AppName string
	// 项目环境
	EnvName    string
	ConfigPath string
}

// 读取Yaml配置文件，并转换成Config对象  struct结构
func (c *Config) InitConfig() *Config {

	// 获取配置文件
	path, _ := filepath.Abs(Sp.ConfigPath)

	if _, err := os.Stat(path); err != nil {
		panic(fmt.Sprintf("\n 配置文件不存在：%s", Sp.ConfigPath))

	}

	yamlFileBytes, err := os.ReadFile(path)
	err = yaml.Unmarshal(yamlFileBytes, &c)
	if err != nil {
		panic(err)
	}

	structx.SetDefaults(c)

	for _, fn := range afterConfigFns {
		fn(c)
	}

	return c
}

var Sp = &StartParams{
	AppName:    "app",
	EnvName:    "dev",
	ConfigPath: "./resource/config.yml",
}

func (c *Config) InitFlag() *StartParams {
	c.App.StartTime = time.Now().UnixMilli()

	envName := flag.String("e", Sp.EnvName, "项目环境名")
	configPath := flag.String("c", "", "项目配置文件路径")
	flag.Parse()

	Sp.EnvName = *envName

	//获取项目的执行路径
	if *configPath != "" {
		// 优先使用命令行指定的配置文件路径
		Sp.ConfigPath = *configPath
	} else if Sp.EnvName != "" && Sp.EnvName != "dev" {
		// 非 dev 环境，使用环境对应的配置文件
		Sp.ConfigPath = fmt.Sprintf("./resource/config-%s.yml", Sp.EnvName)
	}
	// dev 环境且未指定配置文件时，保持默认的 ./resource/config.yml
	return Sp
}

func (c *Config) GetGinMode() string {
	if c.App.IsDev() {
		return "debug"
	}
	if c.App.IsProd() {
		return "release"
	}
	if c.App.IsTest() {
		return "test"
	}
	return "debug"
}
