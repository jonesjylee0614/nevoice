package base

import (
	"cmp"
	"gofly/internal/config"
	"gofly/pkg/utils/anyx"
	"regexp"
	"strings"

	"gorm.io/gorm"
)

type Cond struct {
	Order  string
	Fields string
	Limit  int64
	wheres []where
	driver string
}

type where struct {
	op    string
	query string
	args  []interface{}
}

func NewCond() *Cond {
	return &Cond{
		wheres: []where{},
		driver: cmp.Or(config.Inst.DBconf.Driver, "mysql"),
	}
}

func (c *Cond) Where(noneZeroVal interface{}, query string, args ...interface{}) {
	if anyx.IsBlank(noneZeroVal) {
		return
	}
	c.wheres = append(c.wheres, where{
		op:    "and",
		query: query,
		args:  args,
	})
}

func (c *Cond) Or(noneZeroVal interface{}, query string, args ...interface{}) {
	if anyx.IsBlank(noneZeroVal) {
		return
	}
	c.wheres = append(c.wheres, where{
		op:    "or",
		query: query,
		args:  args,
	})
}

// 编译正则表达式，匹配 \" ` [ ]
var re = regexp.MustCompile("[`\\[\\]]")

// 2情况，包含 desc 或 asc 不包含任意
// quoteOrder 给字段添上各个数据库的引号
func (c *Cond) quoteOrder() string {
	if c.Order == "" {
		return ""
	}
	// 替换匹配到的字符为空字符串
	c.Order = re.ReplaceAllString(c.Order, "")

	quoter := GetQuoter(config.Inst.DBconf.Driver)

	var arr []string

	for _, s := range strings.Split(c.Order, ",") {
		ord := strings.Split(strings.TrimSpace(s), " ") // 0:字段名 1:排序方式
		if len(ord) == 2 {
			arr = append(arr, quoter.QuoteField(ord[0])+" "+ord[1])
		} else {
			arr = append(arr, quoter.QuoteField(ord[0]))
		}
	}
	return strings.Join(arr, " ,")
}

func (c *Cond) wrapWhere(tx *gorm.DB) *gorm.DB {
	for _, w := range c.wheres {
		if strings.Contains(strings.ToLower(w.query), "between") || strings.Contains(w.query, " or ") || strings.Contains(w.query, " and ") {
			if w.op == "and" {
				tx.Where(w.query, w.args...)
			} else {
				tx.Or(w.query, w.args...)
			}
			continue
		}
		if len(w.args) == 1 {
			if w.op == "and" {
				tx.Where(w.query, w.args[0])
			} else {
				tx.Or(w.query, w.args[0])
			}
			continue
		}
		if len(w.args) > 1 {
			if w.op == "and" {
				tx.Where(w.query, w.args)
			} else {
				tx.Or(w.query, w.args)
			}
			continue
		}
	}
	return tx
}

func (c *Cond) wrapFields() string {
	quoter := GetQuoter(c.driver)
	var arr []string
	for _, s := range strings.Split(c.Fields, ",") {
		arr = append(arr, quoter.QuoteField(s))
	}
	return strings.Join(arr, " ,")
}
