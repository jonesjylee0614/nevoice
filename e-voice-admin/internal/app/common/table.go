package common

import (
	"encoding/json"
	"gofly/internal/model/base"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"

	"github.com/gin-gonic/gin"
)

type Table struct {
}

func init() {
	gf.RegisterRoute(&Table{})
}

// 数据通用排序
func (api *Table) Weigh(c *gin.Context) {
	//获取post传过来的data
	var parameter map[string]interface{}
	gf.ReqBody(c, &parameter)
	//排序的数组
	ids := parameter["ids"]
	bids, _ := json.Marshal(&ids)
	var idsArr []interface{}
	var idsArrInt []int64
	// 将字符串反解析为数组
	_ = json.Unmarshal(bids, &idsArr)
	_ = json.Unmarshal(bids, &idsArrInt)
	// ids_arr := strings.Split(ids, `,`)
	//拖动的记录ID
	_changeid := parameter["changeid"].(float64)
	changeid := int64(_changeid)
	// //操作字段
	field := parameter["field"].(string)
	// //操作的数据表
	tablename := parameter["table"].(string)
	//父级id
	// //排序方式
	orderway := parameter["orderway"].(string)
	// //主键id
	prikey := parameter["prikey"].(string)
	// 1.如果设定了pid的值,此时只匹配满足条件的ID,其它忽略
	if _, ok := parameter["pid"]; ok {
		// var hasids []map[string]interface{}
		var listId []int64
		base.GormDb.Table(tablename).Where(prikey, idsArr).Where("pid", parameter["pid"]).Pluck("id", &listId)
		idsArrInt = intersect(listId, idsArrInt)
	}
	winidsBase, _ := json.Marshal(&idsArrInt)
	var winids []interface{}
	_ = json.Unmarshal(winidsBase, &winids)
	var list []map[string]interface{}

	base.GormDb.Table(tablename).Where(prikey, winids).
		Select(prikey + "," + field).
		Order(field + " " + orderway).Find(&list)

	var sour []int64
	weighdata := make(map[interface{}]interface{})
	for _, v := range list {
		sour = append(sour, anyx.ToInt64(v[prikey]))
		weighdata[v[prikey]] = v[field]
	}
	position := array_search(changeid, idsArrInt)
	descId := sour[position] //移动到目标的ID值,取出所处改变前位置的值
	// change_id, _ := strconv.ParseInt(changeid, 8, 64) //强转int64
	changeId := changeid
	temp := difference(idsArrInt, sour)
	for k, v := range temp {
		var offset int64
		if v == changeId {
			offset = descId
		} else {
			if changeId == temp[0] {
				nk := k + 1
				if len(temp) > nk {
					offset = temp[nk]
				} else {
					offset = changeId
				}
			} else {
				nk := k - 1
				if nk >= 0 {
					offset = temp[nk]
				} else {
					offset = changeId
				}
			}
		}

		base.GormDb.Table(tablename).Where(prikey, v).Updates(map[string]interface{}{field: weighdata[offset]})
	}
	results.Success(c, "排序成功！", sour, descId)
}

// 函数在数组中搜索某个键值，并返回对应的键名
func array_search(changeid int64, arr []int64) int {
	// changeidint, _ := strconv.ParseInt(changeid, 8, 64)
	for k, v := range arr {
		if v == changeid {
			return k
		}
	}
	return -1
}

// 1.比较两个数组的值，并返回交集;2.返回数组中所有的值（不保留键名）：
func intersect(nums1 []int64, nums2 []int64) []int64 {
	m := make(map[int64]int64)
	var arr []int64
	for _, v := range nums1 {
		m[v]++
	}
	for _, v := range nums2 {
		times, ok := m[v] //v是nums2中的值,m[v]是map中的值.m[v]==times
		if ok && times > 0 {
			arr = append(arr, v)
			m[v]-- //所有出现的数字都+1,最后要减掉1
		}
	}
	return arr
}

// 2.求差集
func difference(slice1, slice2 []int64) []int64 {
	var arr []int64
	for k, v := range slice1 {
		for key, value := range slice2 {
			if k == key && v != value {
				arr = append(arr, v)
			}
		}
	}
	if len(slice1) > len(slice2) {
		sn := len(slice2)
		nArr := slice1[sn:]
		arr = ArrayMerge(arr, nArr)
	}
	return arr
}

// 数组拼接
func ArrayMerge(ss ...[]int64) []int64 {
	n := 0
	for _, v := range ss {
		n += len(v)
	}
	s := make([]int64, 0, n)
	for _, v := range ss {
		s = append(s, v...)
	}
	return s
}
func (api *Table) Perms() map[string][]gin.HandlerFunc {
	return nil
}
