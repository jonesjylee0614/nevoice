package base

import (
	"testing"
)

func TestQuote(t *testing.T) {

	tests := []struct {
		name   string
		want   string
		driver string
	}{
		{
			name:   "id desc, create_time asc",
			want:   "`id` desc ,`create_time` asc",
			driver: "mysql",
		}, {
			name:   "`id` desc, [create_time] asc",
			want:   "`id` desc ,`create_time` asc",
			driver: "mysql",
		}, {
			name:   "id desc",
			want:   "`id` desc",
			driver: "mysql",
		}, {
			name:   "id",
			want:   "`id`",
			driver: "mysql",
		}, {
			name:   "id",
			want:   "`id`",
			driver: "mysql",
		}, {
			name:   "id",
			want:   "\"id\"",
			driver: "pgsql",
		}, {
			name:   "id",
			want:   "[id]",
			driver: "mssql",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cond := NewCond()
			cond.Order = tt.name
			cond.driver = tt.driver
			res := cond.quoteOrder()
			if res != tt.want {
				t.Error("quoteOrder error", cond.Order, "=>", res)
			}
		})
	}

}
