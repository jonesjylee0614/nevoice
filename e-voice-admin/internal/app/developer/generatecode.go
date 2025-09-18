package developer

import (
	"gofly/internal/config"
	"gofly/internal/domain/core_dto"
	"gofly/internal/domain/core_service"
	"gofly/internal/model/base"
	"gofly/internal/model/core"
	"gofly/internal/model/dialect"
	"gofly/internal/model/dialect/meta"
	"gofly/pkg/utils/anyx"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"gofly/pkg/utils/structx"
	"os"
	"path/filepath"
	"reflect"
	"strings"

	"github.com/gin-gonic/gin"
)

type Generatecode struct {
	svc                 *core_service.CommonGeneratecode      `inject:""`
	fieldSvc            *core_service.CommonGeneratecodeField `inject:""`
	BusinessAccountSvc  *core_service.BusinessAccount         `inject:""`
	BusinessAuthRuleSvc *core_service.BusinessAuthRule        `inject:""`
}

func init() {
	gf.RegisterRoute(&Generatecode{})
}

// Get_list 获取列表 /developer/generatecode/get_list
func (s *Generatecode) Get_list(c *gin.Context) {

	req := gf.ReqQuery(c, &core_dto.CommonGeneratecodePageReq{})
	cond := base.NewCond()

	cond.Where(true, "status", 0)
	cond.Where(req.Name, "tablename like ?", "%"+req.Name+"%")
	cond.Order = "id desc"
	list, err := s.svc.Page(c, &req.IPage, cond)
	results.ResPage(c, req.IPage, list, err)
}

// Get_dbfield 获取数据表字段 /developer/generatecode/get_dbfield
func (s *Generatecode) Get_dbfield(c *gin.Context) {

	tablename := c.DefaultQuery("tablename", "")
	assert.IsTrue(tablename != "", "请传数据表名称")

	columnInfos := dialect.GetByDriverName(config.Inst.DBconf.Driver).Columns(tablename)

	var columnList []interface{}
	for _, info := range columnInfos {
		if info.ColumnComment == "" && info.ColumnName == "id" {
			info.ColumnComment = "ID"
		}
		columnList = append(columnList, map[string]interface{}{"value": info.ColumnName, "label": info.ColumnComment, "type": info.DataType})

	}
	results.Success(c, "获取数据表字段", columnList, nil)
}

// Get_tablelist 获取数据库列表 /developer/generatecode/get_tablelist
func (s *Generatecode) Get_tablelist(c *gin.Context) {

	id := c.DefaultQuery("id", "")

	cond := base.NewCond()
	cond.Fields = "tablename as value,comment as label"
	cond.Order = "id desc"
	cond.Where(true, "status", 0)
	cond.Where(true, "id !=", id)
	res, err := s.svc.List(c, cond)
	results.ResObj(c, res, err)
}

// UpCodeTable 更新生成代码的数据表 /developer/generatecode/upCodeTable
func (s *Generatecode) UpCodeTable(c *gin.Context) {
	//获取数据库名
	var tableNames []string
	cond := base.NewCond()
	cond.Order = "tablename asc"
	_ = s.svc.Pluck(c, cond, "tablename", &tableNames)

	tableInfos := dialect.GetByDriverName(config.Inst.DBconf.Driver).Tables()

	var gcs []*core.CommonGeneratecode
	for _, val := range tableInfos {
		gc := &core.CommonGeneratecode{
			Tablename: val.TableName,
			Comment:   val.TableComment,
			RuleName:  val.TableComment,
			TableRows: val.TableRows,
			Engine:    "",
		}

		// 修改表信息
		if collx.ArrayContains(tableNames, val.TableName) {
			gc.RuleName = ""
			base.GormDb.Table(gc.TableName()).Where("tablename", val.TableName).Updates(gc)
		} else {
			gcs = append(gcs, gc)
		}
	}
	// 新增表信息
	if len(gcs) > 0 {
		res, err := s.svc.InsertBatch(c, gcs)
		results.ResSave(c, res, err)
	} else {
		results.Success(c, "已更新全部", tableInfos, nil)
	}
}

// Save 保存-生成代码 /developer/generatecode/save
func (s *Generatecode) Save(c *gin.Context) {

	req := gf.ReqBody(c, &core_dto.CommonGeneratecodeSave{})
	codeData := req.CodeData

	//更新字段列表数据
	for _, field := range req.Fields {
		gfield := field.CommonGeneratecodeField
		gfield.GeneratecodeID = codeData.Id
		gfield.Required = anyx.ToInt(field.Required)
		gfield.Isform = anyx.ToInt(field.IsForm)
		gfield.Islist = anyx.ToInt(field.IsList)
		gfield.Isorder = anyx.ToInt(field.Isorder)
		gfield.Issearch = anyx.ToInt(field.IsSearch)

		// 需要支持修改0值
		m := make(map[string]interface{})
		structx.ToMap(structx.Indirect(reflect.ValueOf(gfield)), m)
		base.GormDb.Table(gfield.TableName()).Where("id", gfield.Id).Updates(m)
	}
	user := s.BusinessAccountSvc.GetSysUser(c)

	//1生成菜单
	// 查询是否存在菜单
	rc := base.NewCond()
	rc.Where(true, "routePath", codeData.RoutePath)
	rc.Or(true, "routeName", codeData.RouteName)
	findRule, err := s.BusinessAuthRuleSvc.First(c, rc)

	if err != nil {
		rule := &core.BusinessAuthRule{
			Title:     codeData.RuleName,
			Type:      1,
			UID:       user.Id,
			Icon:      codeData.Icon,
			RoutePath: codeData.RoutePath,
			RouteName: codeData.RouteName,
			Pid:       codeData.Pid,
			Component: codeData.Component,
		}
		_, err := s.BusinessAuthRuleSvc.Insert(c, rule)
		assert.ErrIsNil(err, "添加菜单失败")

		rule2 := &core.BusinessAuthRule{}
		rule2.Id = rule.Id
		rule2.OrderNo = rule.Id
		_, _ = s.BusinessAuthRuleSvc.Update(c, rule2)
		codeData.RuleID = rule.Id
	} else {
		codeData.RuleID = findRule.Id
	}

	//菜单添加好后添加代码
	/***************************后端**************************/
	filePath := filepath.Join("internal/app/", codeData.APIPath)
	//1. 如果没有filepath文件目录就创建一个
	if _, err := os.Stat(filePath); err != nil {
		if !os.IsExist(err) {
			_ = os.MkdirAll(filePath, os.ModePerm)
		}
	}
	//2. 替换文件内容
	filenameArr := strings.Split(codeData.APIFilename, `.`) //文件名称
	packgenameArr := strings.Split(codeData.APIPath, `/`)
	//2.1 模块名称
	//2.2 文件名称
	filename := "index"
	if len(filenameArr) > 0 {
		filename = filenameArr[0]
	}
	//2.3 包名
	packageName := ""
	if len(packgenameArr) > 0 {
		packageName = packgenameArr[len(packgenameArr)-1]
	}
	//创建后端代码

	// 列表展示字段
	fc1 := base.NewCond()
	fc1.Where(true, "generatecode_id", codeData.Id)
	fc1.Where(true, "islist", 1)
	fc1.Order = "list_weigh asc,id asc"
	fc1.Fields = "id,name,field,align,width"

	var listFieldNames []string
	listFields, _ := s.fieldSvc.List(c, fc1)
	listFieldNames = collx.ArrayMap(listFields, func(val *core.CommonGeneratecodeField) string {
		return val.Field
	})

	if len(listFieldNames) > 0 {
		var strArr []string
		// 没勾选id也要查询出id，否则修改数据时，id为空
		if !collx.ArrayContains(listFieldNames, "id") {
			strArr = append(strArr, "id")
		}
		for _, v := range listFieldNames {
			strArr = append(strArr, v)
		}
		codeData.Fields = strings.Join(strArr, ",")
	} else {
		codeData.Fields = ""
	}
	go MakeGoCode(filePath, filename, packageName, codeData)
	//3. 查看是否添加文件到控制器文件
	go CheckIsAddController(codeData.APIPath)
	/******************************前端******************************/
	componentArr := strings.Split(codeData.Component, `/`)
	componentpahArr := strings.Split(codeData.Component, componentArr[len(componentArr)-1])
	vuePath := filepath.Join(config.Inst.App.Vueobjroot, "/src/views/", componentpahArr[0]) //前端文件路径
	//1. 如果没有filepath文件目录就创建一个
	if _, err := os.Stat(vuePath); err != nil {
		if !os.IsExist(err) {
			_ = os.MkdirAll(vuePath, os.ModePerm)
		}
	}
	//2. 复制前端模板到新创建文件夹下
	_ = CopyAllDir(filepath.Join("resource/developer/codetpl/vue/", codeData.TplType), vuePath)
	//3. 修改模板文件内容
	if codeData.TplType == "contentcatelist" { //如果是关联分类则更新分类api.ts
		ApitsReplay(filepath.Join(vuePath, "cate/api.ts"), packageName, filename+"cate")
	}
	//修改api/index.ts文件
	ApitsReplay(filepath.Join(vuePath, "api/index.ts"), packageName, filename)

	//替换data.ts
	UpFieldData(filepath.Join(vuePath, "data.ts"), listFields)

	//替换AddForm.vue表单
	fc2 := base.NewCond()
	fc2.Fields = "id,name,field,required,formtype,datatable,datatablename"
	fc2.Order = "field_weigh asc,id asc"
	fc2.Where(true, "generatecode_id", codeData.Id)
	fc2.Where(true, "isform", 1)

	formFields, _ := s.fieldSvc.List(c, fc2)

	UpFieldAddForm(filepath.Join(vuePath, "AddForm.vue"), codeData.Fields, formFields) //更新表单
	/*************最后更新代码生成表数据***************************/
	codeData.IsInstall = 1

	res, err := s.svc.Update(c, codeData)
	results.ResSave(c, res, err)

}

// UpStatus 更新状态 /developer/generatecod/upStatus
func (s *Generatecode) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	results.ResSave(c, res, err)
}

// Del 删除/卸载 /developer/generatecode/del
func (s *Generatecode) Del(c *gin.Context) {
	//获取post传过来的data
	req := gf.ReqBody(c, &core_dto.CommonGeneratecodeDel{})

	if req.IsInstall == 1 { //卸载

		if ok, err := commonUninstall(c, s, req.Id); ok > 0 {
			t := &core.CommonGeneratecode{
				IsInstall: 2,
			}
			t.Id = req.Id
			_, _ = s.svc.Update(c, t)
			results.Success(c, "卸载成功！", nil, nil)
		} else {
			results.Failed(c, "卸载失败", err)
		}
	} else { //删除
		t := &core.CommonGeneratecode{}
		t.Id = req.Id

		res, err := s.svc.Delete(c, t)
		if err != nil {
			return
		}
		results.ResDel(c, res, err)
	}
}

// Uninstallcode 卸载 /developer/generatecode/uninstallcode
func (s *Generatecode) Uninstallcode(c *gin.Context) {
	//获取post传过来的data
	var parameter map[string]interface{}
	gf.ReqBody(c, &parameter)
	res, err := commonUninstall(c, s, parameter["id"])
	results.ResDel(c, res, err)
}

// 卸载通用方法
func commonUninstall(c *gin.Context, s *Generatecode, id interface{}) (int64, error) {

	entity, err := s.svc.GetById(c, id)
	if err != nil {
		return 0, err
	}
	filePath := filepath.Join("app/", entity.APIPath)
	//判断后端代码是否存在删除后端代码
	filegoPath := filepath.Join(filePath, entity.APIFilename)
	if _, err := os.Stat(filegoPath); err == nil {
		//删除菜单
		r := &core.BusinessAuthRule{}
		r.Id = entity.RuleID
		_, _ = s.BusinessAuthRuleSvc.Delete(c, r)

		// 修改状态为已卸载
		t := &core.CommonGeneratecode{}
		t.IsInstall = 2
		t.Id = entity.Id
		_, _ = s.svc.Update(c, t)
		UnInstallCodeFile(entity)
	}

	return 1, nil

}

// GetContent 获取内容  /developer/generatecode/getContent
func (s *Generatecode) GetContent(c *gin.Context) {
	id := c.DefaultQuery("id", "")
	assert.NotBlank(id, "请传参数id")

	data, err := s.svc.GetById(c, id)

	assert.IsTrue(data != nil && err == nil, "生成数据表不存在")

	var fieldDataList []*core.CommonGeneratecodeField

	fieldInfos := dialect.GetByDriverName(config.Inst.DBconf.Driver).Columns(data.Tablename)

	// 取出所有字段名
	dbFieldNames := make([]string, 0)
	fieldMap := make(map[string]meta.Column)
	for _, field := range fieldInfos {
		dbFieldNames = append(dbFieldNames, field.ColumnName)
		fieldMap[field.ColumnName] = field
	}

	// 查出已经有的字段
	fc1 := base.NewCond()
	fc1.Where(true, "generatecode_id", id)
	var existFieldNames []string
	_ = s.fieldSvc.Pluck(c, fc1, "field", &existFieldNames)
	// 对比哪些要新增，哪些要删除，哪些要修改(字段备注)
	adds, dels, upds := collx.ArrayCompare(dbFieldNames, existFieldNames)
	weigh := len(existFieldNames)
	// 新增
	for _, addName := range adds {
		field := fieldMap[addName]

		colName := strings.ToLower(field.ColumnName)
		if field.ColumnComment == "" && field.ColumnName == "id" {
			field.ColumnComment = "ID"
		}
		formType := "text"
		searchType := "text"
		isOrder := 0
		if field.ColumnName == "id" {
			isOrder = 1
		}
		defValue := "[]"
		if strings.Contains(strings.ToLower(field.DataType), "int") {
			formType = "number"
		} else if strings.Contains(strings.ToLower(field.DataType), "char") && field.CharMaxLength >= 225 {
			formType = "textarea"
		} else if strings.ToLower(field.DataType) == "text" {
			formType = "editor"
		} else if strings.ToLower(field.DataType) == "enum" {
			formType = "select"
			searchType = "select"
		} else if strings.HasSuffix(colName, "date") {
			formType = "date"
		} else if strings.HasSuffix(colName, "datetime") {
			formType = "datetime"
		} else if strings.HasSuffix(colName, "time") {
			formType = "time"
		} else if strings.HasSuffix(colName, "image") {
			formType = "image"
		} else if strings.HasSuffix(colName, "images") {
			formType = "images"
		} else if strings.HasSuffix(colName, "file") {
			formType = "file"
		} else if strings.HasSuffix(colName, "files") {
			formType = "files"
		}
		weigh++
		fieldDataList = append(fieldDataList, &core.CommonGeneratecodeField{
			GeneratecodeID: anyx.ToInt64(id),
			Name:           field.ColumnComment,
			Field:          field.ColumnName,
			Formtype:       formType,
			DefValue:       defValue,
			Searchtype:     searchType,
			Isorder:        isOrder,
			ListWeigh:      int64(weigh),
			FieldWeigh:     int64(weigh),
			SearchWeigh:    int64(weigh),
		})
	}
	if len(fieldDataList) > 0 {
		_, _ = s.fieldSvc.InsertBatch(c, fieldDataList)
	}

	// 删除
	if len(dels) > 0 {
		base.GormDb.Table(s.fieldSvc.GetModel().TableName()).
			Where("generatecode_id", id).
			Where("field", dels).Delete(s.fieldSvc.GetModel())
	}
	// 修改
	if len(upds) > 0 {
		for _, updName := range upds {
			field := fieldMap[updName]
			base.GormDb.Table(s.fieldSvc.GetModel().TableName()).
				Where("generatecode_id", id).
				Where("field", updName).
				Update("name", field.ColumnComment)
		}
	}

	fc := base.NewCond()
	fc.Where(true, "generatecode_id", id)

	baseFields := "id,name,field"
	formFields := "isform,required,formtype,datatable,datatablename,field_weigh"
	listFields := "islist,isorder,align,width,list_weigh"
	searchFields := "issearch,searchway,searchtype,search_weigh"

	fc.Fields = baseFields + "," + formFields + "," + listFields + "," + searchFields
	fc.Order = "id asc"

	list1, _ := s.fieldSvc.List(c, fc)
	list := collx.ArrayMap(list1, func(item *core.CommonGeneratecodeField) *core_dto.CommonGenerateCodeListField {
		f := &core_dto.CommonGenerateCodeListField{
			CommonGeneratecodeField: item,
			IsForm:                  item.Isform == 1,
			Required:                item.Required == 1,
			IsList:                  item.Islist == 1,
			IsOrder:                 item.Isorder == 1,
			IsSearch:                item.Issearch == 1,
		}
		return f
	})
	results.Success(c, "获取生成表单信息成功！", gf.Map{"data": data, "list": list}, nil)

}
func (s *Generatecode) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"gen:base": {s.Get_list, s.Get_dbfield, s.Get_tablelist, s.UpCodeTable, s.Save, s.UpStatus, s.Del, s.Uninstallcode, s.GetContent},
	}
}
