package timex

import (
	"context"
	"database/sql"
	"encoding/json"
	"time"
)

const DefaultDateTimeFormat = "2006-01-02 15:04:05"

func DefaultFormat(time time.Time) string {
	return time.Format(DefaultDateTimeFormat)
}

func NewNullTime(t time.Time) NullTime {
	return NullTime{
		NullTime: sql.NullTime{
			Time:  t,
			Valid: !t.IsZero(),
		},
	}
}

type NullTime struct {
	sql.NullTime
}

func (nt *NullTime) UnmarshalJSON(bytes []byte) error {
	if len(bytes) == 0 {
		nt.NullTime = sql.NullTime{}
		return nil
	}
	var t time.Time
	if err := json.Unmarshal(bytes, &t); err != nil {
		return err
	}
	if t.IsZero() {
		nt.NullTime = sql.NullTime{}
		return nil
	}
	nt.NullTime = sql.NullTime{
		Valid: true,
		Time:  t,
	}
	return nil
}

func (nt *NullTime) MarshalJSON() ([]byte, error) {
	if !nt.Valid || nt.Time.IsZero() {
		return json.Marshal(nil)
	}
	return json.Marshal(nt.Time)
}

func SleepWithContext(ctx context.Context, d time.Duration) {
	timer := time.NewTimer(d)
	defer timer.Stop()
	select {
	case <-timer.C:
	case <-ctx.Done():
	}
}

// To0TimeDuration 计算当前时间到今日0点的时间差
func To0TimeDuration() time.Duration {
	now := time.Now()
	midnight := time.Date(now.Year(), now.Month(), now.Day()+1, 0, 0, 0, 0, now.Location())
	// 计算当前时间到今天0点的时间差
	diff := midnight.Sub(now)
	return diff
}

// 转换任意字符串为时间

// 支持的日期时间格式模板（按优先级排序）
var timeFormats = []string{
	time.DateTime,
	time.DateOnly,
	time.TimeOnly,
	"2006/01/02 15:04:05",
	"2006/01/02",
	"2006年01月02日",
	"2006年01月02日 15:04:05",
	time.Layout,
	time.ANSIC,
	time.UnixDate,
	time.RubyDate,
	time.RFC822,
	time.RFC822Z,
	time.RFC850,
	time.RFC1123,
	time.RFC1123Z,
	time.RFC3339,
	time.RFC3339Nano,
	time.Kitchen,
	time.Stamp,
	time.StampMilli,
	time.StampMicro,
	time.StampNano,
}

// ParseTime 解析字符串为 time.Time
func ParseTime(str string) time.Time {
	for _, layout := range timeFormats {
		t, err := time.Parse(layout, str)
		if err == nil {
			return t
		}
	}
	return time.Now()
}
