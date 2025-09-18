package gf

import (
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/dt"
)

// 获取树状数组
func GetTreeArray(num []dt.Map, pid int64, itemprefix string) []dt.Map {
	childs := ToolFar(num, pid) //获取pid下的所有数据
	var chridnum []dt.Map
	if childs != nil {
		var number = 1
		var total = len(childs)
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
			v["children"] = GetTreeArray(num, anyx.ToInt64(v["id"]), itemprefix+k+"&nbsp;")
			chridnum = append(chridnum, v)
			number++
		}
	}
	return chridnum
}

// 获取菜单树形
func GetRuleTreeArray(num []dt.Map, pid int64, itemprefix string) []dt.Map {
	if nil == num || len(num) == 0 {
		return make([]dt.Map, 0)
	}
	childs := ToolFar(num, pid) //获取pid下的所有数据
	var chridnum []dt.Map
	if childs != nil {
		var number = 1
		for _, v := range childs {
			j := ""
			k := ""
			spacer := ""
			if itemprefix != "" {
				spacer = itemprefix + j
			}
			v["spacer"] = spacer
			v["children"] = GetTreeArray(num, anyx.ToInt64(v["id"]), itemprefix+k+"&nbsp;")
			chridnum = append(chridnum, v)
			number++
		}
	}
	return chridnum
}

// 获取菜单树形-打包代码菜单
func GetRuleTreeArrayByPack(num []dt.Map, pid int64) []dt.Map {
	childs := ToolFar(num, pid) //获取pid下的所有数据
	var chridnum []dt.Map
	if childs != nil {
		for _, v := range childs {
			id := anyx.ToInt64(v["id"])
			newdata := GetRuleTreeArrayByPack(num, id)
			if newdata != nil {
				v["children"] = GetRuleTreeArrayByPack(num, id)
			}
			chridnum = append(chridnum, v)
		}
	}
	return chridnum
}

// 获取菜单子树结构
func GetMenuChildrenArray(pdata []dt.Map, parentId int64, pidFile string) []dt.Map {
	if nil == pdata || len(pdata) == 0 {
		return make([]dt.Map, 0)
	}
	var returnList []dt.Map
	for _, v := range pdata {
		if anyx.ToInt64(v[pidFile]) == parentId {
			children := GetMenuChildrenArray(pdata, anyx.ToInt64(v["id"]), pidFile)
			if children != nil {
				v["children"] = children
			}
			returnList = append(returnList, v)
		}
	}
	return returnList
}

// 获取菜单子树结构
func GetMenuChildrenArraylist(pdata []dt.Map, parentId int64) []dt.Map {
	var returnList []dt.Map
	for _, v := range pdata {
		if anyx.ToInt64(v["pid"]) == parentId {
			children := GetMenuChildrenArraylist(pdata, anyx.ToInt64(v["value"]))
			if children != nil {
				v["children"] = children
			}
			returnList = append(returnList, v)
		}
	}
	return returnList
}

// 获取pid下所有数组
func ToolFar(data []dt.Map, pid int64) []dt.Map {
	var mapString []dt.Map
	for _, v := range data {
		if anyx.ToInt64(v["pid"]) == pid {
			mapString = append(mapString, v)
		}
	}
	return mapString
}

// 2.将getTreeArray的结果返回为二维数组
func GetTreeList_txt(data []dt.Map, field string) []dt.Map {
	var midleArr []dt.Map
	for _, v := range data {
		var children []dt.Map
		if _, ok := v["children"]; ok {
			children = v["children"].([]dt.Map)
		} else {
			children = make([]dt.Map, 0)
		}
		delete(v, "children")
		v[field+"_txt"] = v["spacer"].(string) + " " + v[field+""].(string)
		if len(children) > 0 {
			v["haschild"] = 1
		} else {
			v["haschild"] = 0
		}
		if _, ok := v["id"]; ok {
			midleArr = append(midleArr, v)
		}
		if len(children) > 0 {
			newarr := GetTreeList_txt(children, field)
			midleArr = ArrayMerge_x(midleArr, newarr)
		}
	}
	return midleArr
}

// 数组拼接
func ArrayMerge_x(ss ...[]dt.Map) []dt.Map {
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
