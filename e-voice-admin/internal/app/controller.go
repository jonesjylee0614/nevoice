package app

/**
* 引入控制器
* 请把您使用包用 _ "gofly/internal/app/home/XX"导入您编写的包 自动生成路由
* 不是使用则注释掉
* 路由规则：包路径“home/article” + 包中结构体“Cate”转小写+方法名(首字母转小写	_ "gofly/internal/app/datacenter"
 即：http://xx.com/home/article/cate/get_list
*/
import (
	_ "gofly/internal/app/common"
	_ "gofly/internal/app/dashboard"
	_ "gofly/internal/app/datacenter"
	_ "gofly/internal/app/developer"
	_ "gofly/internal/app/finetune"
	_ "gofly/internal/app/makecode"
	_ "gofly/internal/app/meeting"
	_ "gofly/internal/app/system"
	_ "gofly/internal/app/user"
	_ "gofly/internal/app/voice"
)
