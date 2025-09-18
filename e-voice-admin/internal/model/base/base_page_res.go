package base

type PageResult[T any] struct {
	Page     int64 `json:"page"`
	PageSize int64 `json:"pageSize"`
	Total    int64 `json:"total"`
	Items    []T   `json:"items"`
}
