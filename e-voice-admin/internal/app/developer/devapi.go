package developer

import (
	"gofly/internal/config"
	"gofly/internal/model/dialect"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"strings"

	"github.com/gin-gonic/gin"
)

type Devapi struct {
}

func init() {
	gf.RegisterRoute(&Devapi{})
}

// Get_tables 获取锁数据表 /developer/devapi/get_tables
func (api *Devapi) Get_tables(c *gin.Context) {

	tableInfos := dialect.GetByDriverName(config.Inst.DBconf.Driver).Tables()

	var talbeList []interface{}
	for _, info := range tableInfos {
		if !strings.HasPrefix(info.TableName, "admin_") && !strings.HasPrefix(info.TableName, "login_") && strings.ToLower(info.TableName) != "attachment" {
			talbeList = append(talbeList, map[string]interface{}{"name": info.TableName, "title": info.TableComment})
		}
	}
	results.Success(c, "获取数据表", talbeList, nil)
}
func (api *Devapi) Perms() map[string][]gin.HandlerFunc {
	return nil
}
