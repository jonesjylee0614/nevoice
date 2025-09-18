package core_dto

type BusinessAuthRuleMenu struct {
	Id       int64                   `json:"id"`
	Pid      int64                   `json:"pid"`
	Title    string                  `json:"title"`
	Children []*BusinessAuthRuleMenu `json:"children,omitempty"`
}
