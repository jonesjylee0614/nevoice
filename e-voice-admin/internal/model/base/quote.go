package base

import (
	"strings"
)

type Quoter interface {
	QuoteField(field string) string
}

var QuoterMap = map[string]Quoter{
	"mysql":     &Mysql{},
	"postgres":  &Pgsql{},
	"sqlserver": &Mssql{},
	"mssql":     &Mssql{},
}

func GetQuoter(driverName string) Quoter {
	if v, ok := QuoterMap[driverName]; ok {
		return v
	}
	// 默认是pgsql类的双引号，目前发现只有三种： mysql:``   pgsql/oracle : ""   mssql: []
	return &Pgsql{}
}

type Mysql struct {
	Quoter
}

var _ Quoter = (*Mysql)(nil)

func (s *Mysql) QuoteField(field string) string {
	return "`" + strings.TrimSpace(field) + "`"
}

type Pgsql struct {
	Quoter
}

var _ Quoter = (*Pgsql)(nil)

func (s *Pgsql) QuoteField(field string) string {
	return "\"" + strings.TrimSpace(field) + "\""
}

type Mssql struct {
	Quoter
}

var _ Quoter = (*Mssql)(nil)

func (s *Mssql) QuoteField(field string) string {
	return "[" + strings.TrimSpace(field) + "]"
}
