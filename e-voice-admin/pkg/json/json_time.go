package json

import (
	"database/sql/driver"
	"fmt"
	"gofly/pkg/utils/timex"
	"strconv"
	"strings"
	"time"
)

type JsonTime struct {
	time.Time
}

func NewJsonTime(t time.Time) *JsonTime {
	return &JsonTime{
		Time: t,
	}
}

func NowJsonTime() *JsonTime {
	return &JsonTime{
		Time: time.Now(),
	}
}

func (j JsonTime) MarshalJSON() ([]byte, error) {
	var stamp = fmt.Sprintf("\"%s\"", j.Format(time.DateTime))
	return []byte(stamp), nil
}

func (j *JsonTime) UnmarshalJSON(b []byte) error {
	s := strings.ReplaceAll(string(b), "\"", "")

	t := timex.ParseTime(s)
	*j = *NewJsonTime(t)
	return nil
}

// 这里不要手贱给他改成指针了，否则字段入库报错
func (j JsonTime) Value() (driver.Value, error) {
	var zeroTime time.Time
	if j.Time.UnixNano() == zeroTime.UnixNano() {
		return nil, nil
	}
	return j.Time, nil
}

func (j *JsonTime) Scan(v any) error {

	if value, ok := v.(time.Time); ok {
		*j = JsonTime{Time: value}
		return nil
	} else if value, ok := v.(*time.Time); ok {
		*j = JsonTime{Time: *value}
		return nil
	} else if value, ok := v.(*JsonTime); ok {
		*j = *value
		return nil
	} else if value, ok := v.(JsonTime); ok {
		*j = value
		return nil
	} else if value, ok := v.(int64); ok {
		*j = JsonTime{Time: time.UnixMilli(value)}
		return nil
	} else if value, ok := v.([]uint8); ok {
		num, _ := strconv.ParseInt(string(value), 10, 64)
		*j = JsonTime{Time: time.UnixMilli(num)}
		return nil
	}
	return nil
}
