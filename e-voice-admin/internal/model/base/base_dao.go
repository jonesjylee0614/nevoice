package base

import (
	"context"
	"reflect"

	"gorm.io/gorm"
)

var GormDb *gorm.DB

type Dao[T IModel] interface {
	Insert(context.Context, T) (int64, error)
	InsertBatch(ctx context.Context, ts []T) (int64, error)
	GetById(ctx context.Context, id interface{}) (T, error)
	GetByField(ctx context.Context, field string, value interface{}) (T, error)
	ListByField(ctx context.Context, field string, value interface{}) ([]T, error)
	ListByIds(ctx context.Context, id []int64) ([]T, error)
	Update(context.Context, T) (int64, error)
	InsertOrUpdate(context.Context, T) (int64, error)
	Delete(context.Context, T) (int64, error)
	DeleteBatch(context.Context, *Ids) (int64, error)
	DeleteByField(ctx context.Context, field string, value interface{}) (int64, error)
	List(ctx context.Context, cond *Cond) ([]T, error)
	// Pluck 抽取某一列的数据 res:查询结果指针
	Pluck(c context.Context, cond *Cond, field string, res interface{}) error
	Page(c context.Context, page *IPage, cond *Cond) ([]T, error)
	// Select 执行自定义sql查询 sqlStr:sql语句，listRes:查询结果指针，args:sql语句中的参数
	Select(sqlStr string, listRes interface{}, args ...interface{}) error
	// Exec 执行任意自定义sql sqlStr:sql语句，args:sql语句中的参数
	Exec(sqlStr string, args ...interface{}) (int64, error)
	Count(c context.Context, cond *Cond) (int64, error)
}

var _ Dao[IModel] = (*DaoImpl[IModel])(nil)

type DaoImpl[T IModel] struct {
	M         T
	modelType reflect.Type // 模型类型
}

func (b *DaoImpl[T]) GetModel() T {
	if b.modelType == nil {
		mt := reflect.TypeOf(b.M)
		// 检查 model 是否为指针类型
		if mt.Kind() == reflect.Ptr {
			// 获取指针指向的类型
			b.modelType = mt.Elem()
		}
	}
	newModel := reflect.New(b.modelType).Interface()
	return newModel.(T)
}

func (b *DaoImpl[T]) ByIds(ids *Ids) []T {
	var arr []T
	for _, id := range ids.Ids {
		t := b.GetModel()
		t.SetPkVal(id.Int64())
		arr = append(arr, t)
	}
	return arr
}

func (b *DaoImpl[T]) GetSysUser(c context.Context) *SysUser {
	getuser := c.Value("user")
	if nil == getuser {
		return nil
	}
	return getuser.(*SysUser)
}

func (b *DaoImpl[T]) Insert(c context.Context, t T) (int64, error) {
	t.SetCreatorInfo(b.GetSysUser(c))
	res := GormDb.Model(b.M).Create(t)
	return res.RowsAffected, res.Error
}

func (b *DaoImpl[T]) InsertBatch(c context.Context, ts []T) (int64, error) {
	user := b.GetSysUser(c)
	for _, t := range ts {
		t.SetCreatorInfo(user)
	}
	res := GormDb.Model(b.M).CreateInBatches(ts, 100) // 批量插入，每批次100条数据
	return res.RowsAffected, res.Error
}

func (b *DaoImpl[T]) GetById(c context.Context, id interface{}) (T, error) {
	t := b.GetModel()
	res := GormDb.Model(b.M).Where("id", id).First(&t)
	return t, res.Error
}

func (b *DaoImpl[T]) ListByIds(c context.Context, id []int64) (list []T, err error) {
	res := GormDb.Model(b.M).Where("id in (?)", id).Scan(&list)
	return list, res.Error
}

func (b *DaoImpl[T]) Update(c context.Context, t T) (int64, error) {
	t.SetUpdaterInfo(b.GetSysUser(c))
	res := GormDb.Model(b.M).Where("id", t.GetPkVal()).Updates(t)
	return res.RowsAffected, res.Error
}
func (b *DaoImpl[T]) InsertOrUpdate(c context.Context, t T) (int64, error) {
	if t.GetPkVal() != 0 {
		return b.Update(c, t)
	}
	return b.Insert(c, t)
}

func (b *DaoImpl[T]) Delete(c context.Context, t T) (int64, error) {

	if t.IsLogicalDelete() {
		t.SetLogicalDelete()
		t.SetUpdaterInfo(b.GetSysUser(c))
		res := GormDb.Updates(t)
		return res.RowsAffected, res.Error
	}

	res := GormDb.Where("id", t.GetPkVal()).Delete(b.GetModel())
	return res.RowsAffected, res.Error
}

func (b *DaoImpl[T]) DeleteBatch(c context.Context, ids *Ids) (int64, error) {

	if b.GetModel().IsLogicalDelete() {
		user := b.GetSysUser(c)
		var res = 0
		for _, t := range b.ByIds(ids) {
			t.SetLogicalDelete()
			t.SetUpdaterInfo(user)
			GormDb.Updates(t)
			res++
		}

		return int64(res), nil
	}

	res := GormDb.Where("id in (?)", ids.Ids).Delete(b.GetModel())
	return res.RowsAffected, res.Error
}

// Page 分页
// - fields 需要查询的字段列表，多个用逗号分割，如 "id,username,password"
// - order 排序条件(可以为空字符串) 如 "id desc"
// - where 查询条件，带占位符，如 "username like ?"
// - whereArgs 查询条件占位符的参数
func (b *DaoImpl[T]) Page(c context.Context, page *IPage, cond *Cond) (list []T, err error) {
	m := b.GetModel()

	tx := GormDb.Model(m)
	if cond.Fields != "" {
		tx = tx.Select(cond.wrapFields())
	}

	if m.IsLogicalDelete() {
		cond.Where(true, "deleted", false)
	}
	tx = cond.wrapWhere(tx)

	tx = tx.Order(cond.quoteOrder())

	tx.Count(&page.Total)

	res := tx.Limit(page.PageSize.Int()).
		Offset((page.Page.Int() - 1) * page.PageSize.Int()).
		Find(&list)
	return list, res.Error
}

func (b *DaoImpl[T]) List(c context.Context, cond *Cond) (list []T, err error) {
	m := b.GetModel()
	tx := cond.wrapWhere(GormDb.Model(m))
	if m.IsLogicalDelete() {
		tx = tx.Where("deleted = ?", false)
	}
	if cond.Fields != "" {
		tx = tx.Select(cond.wrapFields())
	}
	tx = tx.Order(cond.quoteOrder())

	res := tx.Find(&list)
	return list, res.Error
}

// 抽取某一列的数据
func (b *DaoImpl[T]) Pluck(c context.Context, cond *Cond, field string, res interface{}) error {
	m := b.GetModel()
	tx := cond.wrapWhere(GormDb.Model(m))
	if m.IsLogicalDelete() {
		tx = tx.Where("deleted = ?", false)
	}
	tx = tx.Order(cond.quoteOrder())

	tx = tx.Pluck(field, res)
	return tx.Error
}
func (b *DaoImpl[T]) First(c context.Context, cond *Cond) (T, error) {
	m := b.GetModel()
	if m.IsLogicalDelete() {
		cond.Where(true, "deleted", false)
	}

	tx := cond.wrapWhere(GormDb.Model(m))
	if cond.Fields != "" {
		tx = tx.Select(cond.wrapFields())
	}

	tx = tx.Order(cond.quoteOrder())
	var t T
	res := tx.Limit(1).First(&t)
	return t, res.Error
}

func (b *DaoImpl[T]) Select(sqlStr string, listRes interface{}, args ...interface{}) error {
	res := GormDb.Raw(sqlStr, args...).Scan(listRes)
	return res.Error
}

func (b *DaoImpl[T]) Exec(sqlStr string, args ...interface{}) (int64, error) {
	res := GormDb.Exec(sqlStr, args...)
	return res.RowsAffected, res.Error
}

func (b *DaoImpl[T]) Count(c context.Context, cond *Cond) (count int64, err error) {
	tx := GormDb.Model(b.GetModel())
	tx = cond.wrapWhere(tx)
	res := tx.Count(&count)
	return count, res.Error
}

func (b *DaoImpl[T]) UpdateWeigh(c context.Context, id int64) {
	if id == 0 {
		return
	}
	m := map[string]interface{}{
		"weigh": id,
	}
	GormDb.Model(b.M).Where("id", id).Updates(m)
}
func (b *DaoImpl[T]) UpdateStatus(c context.Context, req *StatusUpd) (int64, error) {
	tx := GormDb.Model(b.M).
		Where("id", req.Id).
		UpdateColumn("status", req.Status)
	return tx.RowsAffected, tx.Error
}
func (b *DaoImpl[T]) UpdateOrder(c context.Context, req *OrderUpd) (int64, error) {
	tx := GormDb.Model(b.M).
		Where("id", req.Id).
		UpdateColumn("orderNo", req.OrderNo)
	return tx.RowsAffected, tx.Error
}

func (b *DaoImpl[T]) GetByField(ctx context.Context, field string, value interface{}) (T, error) {
	m := b.GetModel()
	cond := NewCond()
	if m.IsLogicalDelete() {
		cond.Where(true, "deleted", false)
	}

	cond.Where(true, field, value)

	tx := cond.wrapWhere(GormDb.Model(m))
	if cond.Fields != "" {
		tx = tx.Select(cond.wrapFields())
	}

	tx = tx.Order(cond.quoteOrder())
	var t T
	res := tx.Limit(1).First(&t)
	return t, res.Error

}
func (b *DaoImpl[T]) ListByField(ctx context.Context, field string, value interface{}) ([]T, error) {
	m := b.GetModel()
	cond := NewCond()
	if m.IsLogicalDelete() {
		cond.Where(true, "deleted", false)
	}
	cond.Where(true, field, value)
	tx := cond.wrapWhere(GormDb.Model(m))
	if cond.Fields != "" {
		tx = tx.Select(cond.wrapFields())
	}
	tx = tx.Order(cond.quoteOrder())
	var list []T
	res := tx.Find(&list)
	return list, res.Error
}

func (b *DaoImpl[T]) DeleteByField(c context.Context, field string, value interface{}) (int64, error) {
	t := b.GetModel()
	if t.IsLogicalDelete() {
		t.SetLogicalDelete()
		t.SetUpdaterInfo(b.GetSysUser(c))
		res := GormDb.Where(field, value).Updates(t)
		return res.RowsAffected, res.Error
	}

	res := GormDb.Where(field, value).Delete(b.GetModel())
	return res.RowsAffected, res.Error
}
