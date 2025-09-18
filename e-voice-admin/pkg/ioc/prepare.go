package ioc

import (
	"gofly/pkg/logx"
)

type PrepareBean struct {
	bean any
	opts []ComponentOption
}

var (
	beanTypeSvc  = "svc"
	beanTypeDao  = "dao"
	beanTypeCtrl = "ctrl"
	beanTypes    = []string{beanTypeSvc, beanTypeDao, beanTypeCtrl}
)

var prepareBeanMap = make(map[string][]*PrepareBean)

func (c *container) prepareDao(bean any, opts ...ComponentOption) {
	c.prepareBean(beanTypeDao, bean, opts...)
}

func (c *container) prepareSvc(bean any, opts ...ComponentOption) {
	c.prepareBean(beanTypeSvc, bean, opts...)
}

func (c *container) prepareCtrl(bean any, opts ...ComponentOption) {
	c.prepareBean(beanTypeCtrl, bean, opts...)
}

func (c *container) prepareBean(beanType string, bean any, opts ...ComponentOption) {
	var list []*PrepareBean
	if ls, ok := prepareBeanMap[beanType]; ok {
		list = ls
	} else {
		list = []*PrepareBean{}
	}
	list = append(list, &PrepareBean{bean: bean, opts: opts})
	prepareBeanMap[beanType] = list
}

func RegisterPrepare() {

	defer func() {
		prepareBeanMap = nil
	}()

	for _, beanType := range beanTypes {
		if ls, ok := prepareBeanMap[beanType]; ok {
			logx.Infof("[ioc] 注册[%s] %d 个", beanType, len(ls))
			for _, bean := range ls {
				Register(bean.bean, bean.opts...)
			}
		}
	}

}
