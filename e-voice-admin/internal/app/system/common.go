package system

import (
	"gofly/internal/domain/core_dto"
	"gofly/pkg/utils/anyx"
	"strings"

	"gofly/pkg/utils/dt"
)

// 获取菜单子树结构
func GetMenuChildrenArray(pdata []dt.Map, parentId int64) []dt.Map {
	var returnList []dt.Map
	for _, v := range pdata {
		pid := anyx.ToInt64(v["pid"])
		if pid == parentId {
			children := GetMenuChildrenArray(pdata, pid)
			if children != nil {
				v["children"] = children
			}
			returnList = append(returnList, v)
		}
	}
	return returnList
}

func GetMenuChildrenArray2(pdata []*core_dto.BusinessAuthRuleMenu, parentId int64) []*core_dto.BusinessAuthRuleMenu {
	var returnList []*core_dto.BusinessAuthRuleMenu
	for _, v := range pdata {
		if v.Pid == parentId {
			v.Children = GetMenuChildrenArray2(pdata, v.Id)
			returnList = append(returnList, v)
		}
	}
	return returnList
}

// tool-获取树状数组
func GetTreeArray(num []dt.Map, pid int64, itemprefix string) []dt.Map {
	childs := ToolFar(num, pid) //获取pid下的所有数据
	var chridnum []dt.Map
	if childs != nil {
		var number int = 1
		var total int = len(childs)
		for _, v := range childs {
			j := ""
			k := ""
			if number == total {
				j += "└"
				k = ""
				if itemprefix != "" {
					k = "&nbsp;"
				}

			} else {
				j += "├"
				k = ""
				if itemprefix != "" {
					k = "│"
				}
			}
			spacer := ""
			if itemprefix != "" {
				spacer = itemprefix + j
			}
			v["spacer"] = spacer
			v["childlist"] = GetTreeArray(num, anyx.ToInt64(v["id"]), itemprefix+k+"&nbsp;")
			chridnum = append(chridnum, v)
			number++
		}
	}
	return chridnum
}

// 2.将getTreeArray的结果返回为二维数组
func getTreeList_txt(data []dt.Map, field string) []dt.Map {
	var midleArr []dt.Map
	for _, v := range data {
		var childlist []dt.Map
		if _, ok := v["childlist"]; ok {
			childlist = v["childlist"].([]dt.Map)
		} else {
			childlist = make([]dt.Map, 0)
		}
		delete(v, "childlist")
		v[field+"_txt"] = v["spacer"].(string) + " " + v[field+""].(string)
		if len(childlist) > 0 {
			v["haschild"] = 1
		} else {
			v["haschild"] = 0
		}
		if _, ok := v["id"]; ok {
			midleArr = append(midleArr, v)
		}
		if len(childlist) > 0 {
			newarr := getTreeList_txt(childlist, field)
			midleArr = ArrayMerge(midleArr, newarr)
		}
	}
	return midleArr
}

// base_tool-获取pid下所有数组
func ToolFar(data []dt.Map, pid int64) []dt.Map {
	var mapString []dt.Map
	for _, v := range data {
		if anyx.ToInt64(v["pid"]) == pid {
			mapString = append(mapString, v)
		}
	}
	return mapString
}

// 数组拼接
func ArrayMerge(ss ...[]dt.Map) []dt.Map {
	n := 0
	for _, v := range ss {
		n += len(v)
	}
	s := make([]dt.Map, 0, n)
	for _, v := range ss {
		s = append(s, v...)
	}
	return s
}

// 三元表达式、三目运算 f(2>3, "大于", false)
func If(condition bool, trueVal, falseVal interface{}) interface{} {
	if condition {
		return trueVal
	}
	return falseVal
}

// 把字符串打散为数组
func Axplode(data interface{}) []interface{} {
	var ruleIdsArr []interface{}
	idsArr := strings.Split(data.(string), `,`)
	for _, intv := range idsArr {
		ruleIdsArr = append(ruleIdsArr, intv)
	}
	return ruleIdsArr
}
