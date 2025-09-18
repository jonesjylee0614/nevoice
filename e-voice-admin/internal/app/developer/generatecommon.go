package developer

import (
	"bufio"
	_ "embed"
	"fmt"
	"gofly/internal/config"
	"gofly/internal/model/core"
	"gofly/pkg/utils/collx"
	"gofly/pkg/utils/filex"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/stringx"
	"io"
	"os"
	"path/filepath"
	"strings"
)

/********************************后端*****************************************/
// tablename, tablenamecate, fields string
func MakeGoCode(filePath, filename, packageName string, parameter *core.CommonGeneratecode) {
	//变量参数
	tableName := parameter.Tablename
	tableNameUpper := stringx.ToUpperCamel(tableName)
	tableNameCate := parameter.CateTablename
	// 创建go文件
	goFile := filepath.Join(filePath, filename+".go")
	//复制go文件模板到新创建文件
	copyfile := "list"
	if parameter.TplType != "" {
		copyfile = parameter.TplType
		if parameter.TplType == "contentcatelist" {
			filenameCate := filename + "cate"
			filepathCate := filepath.Join(filePath, filenameCate+".go")
			MakeBelongCate(filepathCate, filenameCate, packageName, tableNameCate, parameter.Fields)
		}
	}
	tmpParams := make(map[string]interface{})

	am := collx.ArrayToMap([]*core.CommonGeneratecode{parameter})
	for k, v := range am[0] {
		tmpParams[k] = v
	}
	tmpParams["UpFileName"] = gf.FirstUpper(filename)
	tmpParams["packageName"] = packageName
	tmpParams["tableName"] = tableName
	tmpParams["tableNameUpper"] = tableNameUpper
	tmpParams["tableNamecate"] = tableNameCate
	tmpParams["fields"] = parameter.Fields

	// controller
	ctrlPath := filepath.Join("resource/developer/codetpl/go/", copyfile+".gos")
	err := filex.ParseTempAdWrite(ctrlPath, goFile, tmpParams)
	if err != nil {
		panic(err)
	}
	// service
	err = filex.ParseTempAdWrite("resource/developer/codetpl/go/service.gos", fmt.Sprintf("internal/domain/service/%s.go", tableName), tmpParams)
	if err != nil {
		panic(err)
	}
	// dto
	err = filex.ParseTempAdWrite("resource/developer/codetpl/go/dto.gos", fmt.Sprintf("internal/domain/dto/%s.go", tableName), tmpParams)

}

// 创建数据关联的分类
func MakeBelongCate(filePath, filename, packageName, tablename, fields string) {

	params := make(map[string]interface{})
	params["UpFileName"] = gf.FirstUpper(filename)
	params["packageName"] = packageName
	params["tableName"] = tablename
	params["tableNameUpper"] = stringx.ToUpperCamel(tablename)
	params["fields"] = fields

	err := filex.ParseTempAdWrite("resource/developer/codetpl/go/contentcate.gos", filePath, params)
	if err != nil {
		panic(err)
	}
}

/**************************前端处理**********************************/
// 1修改api.ts
//packageName=包名，filename文件名
func ApitsReplay(filePath, packageName, filename string) {
	params := make(map[string]interface{})

	params["modPath"] = fmt.Sprintf("/%s/%s", packageName, filename)
	err := filex.ParseTempAdWrite(filePath, filePath, params)
	if err != nil {
		panic(err)
	}

}

// 1.1、修改data.ts字段
// file_path文件路径，tablefieldlist 字段列表
func UpFieldData(filePath string, listFields []*core.CommonGeneratecodeField) {
	f, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	buf := bufio.NewReader(f)
	var result = ""
	for {
		a, _, c := buf.ReadLine()
		if c == io.EOF {
			break
		}
		if strings.Contains(string(a), "{},") {
			relayStr := ""
			for _, listField := range listFields {
				width := ""
				// 转为驼峰
				listField.Field = stringx.ToLowerCamel(fmt.Sprint(listField.Field))

				if gf.InterfaceToInt64(listField.Width) > 0 {
					width = fmt.Sprintf("       width: %v,\n", listField.Width)
				}
				if listField.Field == "create_time" || listField.Field == "update_time" {
					relayStr += fmt.Sprintf("     {\n       title:  '%v',\n       dataIndex: '%v',\n       slotName: 'create_time',\n       align:'%v',\n%v     },\n", listField.Name, listField.Field, listField.Align, width)
				} else if listField.Field == "id" {
					relayStr += fmt.Sprintf("     {\n       title:  '%v',\n       dataIndex: '%v',\n       width: 76,\n       align:'%v',\n%v     },\n", listField.Name, listField.Field, listField.Align, width)
				} else if listField.Field == "image" {
					relayStr += fmt.Sprintf("     {\n       title:  '%v',\n       dataIndex: '%v',\n       slotName: 'image',\n       align:'%v',\n%v     },\n", listField.Name, listField.Field, listField.Align, width)
				} else if listField.Field == "status" {
					relayStr += fmt.Sprintf("     {\n       title:  '%v',\n       dataIndex: '%v',\n       slotName: 'status',\n       align:'%v',\n%v     },\n", listField.Name, listField.Field, listField.Align, width)
				} else if listField.Field == "cid" {
					relayStr += fmt.Sprintf("     {\n       title:  '%v',\n       dataIndex: 'catename',\n       align:'%v',\n%v     },\n", listField.Name, listField.Align, width)
				} else if listField.Field == "content" {
					relayStr += fmt.Sprintf("     {\n       title:  '%v',\n       dataIndex: '%v',\n       align:'%v',\n%v     },\n", listField.Name, listField.Field, listField.Align, width)
				} else {
					relayStr += fmt.Sprintf("     {\n       title:  '%v',\n       dataIndex: '%v',\n       align:'%v',\n%v     },\n", listField.Name, listField.Field, listField.Align, width)
				}
			}
			dateStr := strings.ReplaceAll(string(a), "{},", relayStr)
			result += dateStr
		} else {
			result += string(a) + "\n"
		}
	}
	fw, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666) //os.O_TRUNC清空文件重新写入，否则原文件内容可能残留
	w := bufio.NewWriter(fw)
	_, _ = w.WriteString(result)
	if err != nil {
		panic(err)
	}
	_ = w.Flush()
}

// UpFieldAddForm
// 2.1、修改AddForm.vue字段
// filePath 文件路径，tableFieldList 字段
func UpFieldAddForm(filePath string, fields interface{}, formFields []*core.CommonGeneratecodeField) {
	f, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer func(f *os.File) {
		_ = f.Close()
	}(f)
	buf := bufio.NewReader(f)
	var result = ""
	//处理数据
	fieldData := ""    //数据字段初始
	relayHtml := ""    //HTML模板
	replaceFile := ""  //替换附件字段
	replaceImage := "" //替换图片字段
	for _, webJson := range formFields {
		valueStr := stringx.ToLowerCamel(webJson.Field)
		labelStr := webJson.Name
		typeStr := webJson.Formtype
		isRequired := webJson.Required
		if strings.Contains(valueStr, "file") {
			replaceFile = valueStr
		}
		if strings.Contains(valueStr, "image") {
			replaceImage = valueStr
		}
		if valueStr != "id" {
			defval := "''"
			if typeStr == "number" {
				defval = "0"
			}
			fieldData += fmt.Sprintf("  %v: %v,\n", valueStr, defval)
		}
		//处理html模版
		if valueStr != "content" && valueStr != "id" && valueStr != "create_time" && valueStr != "updatetime" {
			if typeStr == "textarea" {
				ruleStr := ""
				if isRequired == 1 {
					ruleStr = fmt.Sprintf(":rules=\"%v\"", "[{required:true,message:'请填写"+labelStr+"'}]")
				}
				relayHtml += fmt.Sprintf("                    <ACol :span=\"12\">\n                      <AFormItem field=\"%v\" label=\"%v\" %v >\n                          <ATextarea v-model=\"formData.%v\" placeholder=\"请填%v\" :auto-size=\"{minRows:3,maxRows:5}\"/>\n                      </AFormItem>\n                    </ACol>\n", valueStr, labelStr, ruleStr, valueStr, labelStr)
			} else if typeStr == "number" && valueStr != "cid" {
				ruleStr := ""
				if isRequired == 1 {
					ruleStr = fmt.Sprintf(":rules=\"%v\"", "[{required:true,message:'请填写"+labelStr+"'}]")
				}
				relayHtml += fmt.Sprintf("                    <ACol :span=\"12\">\n                      <AFormItem field=\"%v\" label=\"%v\" %v >\n                          <AInputNumber v-model=\"formData.%v\" placeholder=\"请填%v\" />\n                      </AFormItem>\n                    </ACol>\n", valueStr, labelStr, ruleStr, valueStr, labelStr)
			} else if typeStr == "time" {
				ruleStr := ""
				if isRequired == 1 {
					ruleStr = fmt.Sprintf(":rules=\"%v\"", "[{required:true,message:'请填写"+labelStr+"'}]")
				}
				relayHtml += fmt.Sprintf("                    <ACol :span=\"12\">\n                      <AFormItem field=\"%v\" label=\"%v\" %v >\n                          <ADatePicker v-model=\"formData.%v\" show-time placeholder=\"请填%v\" />\n                      </AFormItem>\n                    </ACol>\n", valueStr, labelStr, ruleStr, valueStr, labelStr)
			} else if typeStr == "radio" {
				ruleStr := ""
				if isRequired == 1 {
					ruleStr = fmt.Sprintf(":rules=\"%v\"", "[{required:true,message:'请选择"+labelStr+"'}]")
				}
				relayHtml += fmt.Sprintf("                    <ACol :span=\"12\">\n                      <AFormItem field=\"%v\" label=\"%v\" %v >\n                          <ARadioGroup v-model=\"formData.%v\" :options=\"SHoptions\" />\n                      </AFormItem>\n                    </ACol>\n", valueStr, labelStr, ruleStr, valueStr)
			} else if typeStr == "image" {
				relayHtml += "                    " + `<ACol :span="24">
											<AFormItem field="image" label="` + labelStr + `" style="margin-bottom:15px;">
												 <ImgUpload v-model="formData.avatar" />
											</AFormItem>
										</ACol>` + "\n"
			} else if typeStr == "images" {
				relayHtml += "                    " + `<ACol :span="24">
											<AFormItem field="image" label="` + labelStr + `" style="margin-bottom:15px;">
												 <ImgUpload v-model="formData.avatar" multi />
											</AFormItem>
										</ACol>` + "\n"
			} else if typeStr == "file" {
				relayHtml += "                  " + `<ACol :span="12">
                                    <AFormItem field="file_link" label="` + labelStr + `" style="margin-bottom:15px;">
										<FileUpload v-model="formData.` + valueStr + `" accept=".zip,.rar,.mp3,.wav,.mp4,.jpg,.png,.gif,.jpeg" />
                                    </AFormItem>
                                    </ACol>` + "\n"
			} else if typeStr == "text" { //文本输入框
				ruleStr := ""
				if isRequired == 1 {
					ruleStr = fmt.Sprintf(":rules=\"%v\"", "[{required:true,message:'请填写"+labelStr+"'}]")
				}
				relayHtml += fmt.Sprintf("                    <ACol :span=\"12\">\n                      <AFormItem field=\"%v\" label=\"%v\" %v >\n                          <AInput v-model=\"formData.%v\" placeholder=\"请填%v\" />\n                      </AFormItem>\n                    </ACol>\n", valueStr, labelStr, ruleStr, valueStr, labelStr)
			}
		}
	}
	for {
		a, _, c := buf.ReadLine()
		if c == io.EOF {
			break
		}
		fieldsStr := gf.InterfaceTostring(fields)
		fieldsArr := strings.Split(fieldsStr, `,`)
		if strings.Contains(string(a), "isEditor=ref(false)") && gf.IsContainString(fieldsArr, "content") {
			dateStr := strings.ReplaceAll(string(a), "isEditor=ref(false)", "isEditor=ref(true)")
			result += dateStr + "\n"
		} else if strings.Contains(string(a), "replaceField:null") {
			dateStr := strings.ReplaceAll(string(a), "replaceField:null", fieldData)
			result += dateStr + "\n"
		} else if strings.Contains(string(a), "['replaceFile']") && replaceFile != "" {
			dateStr := strings.ReplaceAll(string(a), "['replaceFile']", "."+replaceFile)
			result += dateStr + "\n"
		} else if strings.Contains(string(a), "['replaceimage']") && replaceImage != "" {
			dateStr := strings.ReplaceAll(string(a), "['replaceimage']", "."+replaceImage)
			result += dateStr + "\n"
		} else if strings.Contains(string(a), "<!--replaceTpl-->") {
			dateStr := strings.ReplaceAll(string(a), "<!--replaceTpl-->", relayHtml)
			result += dateStr
		} else {
			result += string(a) + "\n"
		}
	}
	fw, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666) //os.O_TRUNC清空文件重新写入，否则原文件内容可能残留
	w := bufio.NewWriter(fw)
	_, _ = w.WriteString(result)
	if err != nil {
		panic(err)
	}
	_ = w.Flush()
}

/********************************************卸载前后端********************************/
// 卸载/删除文件
func UnInstallCodeFile(data *core.CommonGeneratecode) {
	//1.删除后端代码
	//go文件目录
	filePathGoRoot := filepath.Join("app/", data.APIPath)
	//go文件
	appGoPath := filepath.Join(filePathGoRoot, data.APIFilename)
	if _, err := os.Stat(appGoPath); err == nil {
		//1.文件存在删除文件
		_ = os.Remove(appGoPath)
		if data.TplType == "contentcatelist" {
			filenameArr := strings.Split(data.APIFilename, `.`)
			filecategoPath := filepath.Join(filePathGoRoot, filenameArr[0]+"cate.go")
			_ = os.Remove(filecategoPath)
		}
		//2.删除文件夹
		dir, _ := os.ReadDir(filePathGoRoot)
		if len(dir) == 0 {
			_ = os.RemoveAll(filePathGoRoot)
			//3.移除路由
			CheckApiRemoveController(data.APIPath)
		}
	}
	// 删除service
	_ = os.Remove(filepath.Join("domain/service/", data.Tablename+".go"))
	// 删除dto
	_ = os.Remove(filepath.Join("domain/dto/", data.Tablename+".go"))

	//2.2 删除views下代码
	componentArr := strings.Split(data.Component, `/`)
	if data.Component != "" {
		componentPathArr := strings.Split(data.Component, componentArr[len(componentArr)-1])
		vuePath := filepath.Join(config.Inst.App.Vueobjroot, "/src/views/", componentPathArr[0]) //前端文件路径
		if _, err := os.Stat(vuePath); err == nil {
			_ = os.RemoveAll(vuePath)
			//2.3.模块目录文件夹
			vueModelPath := filepath.Join(config.Inst.App.Vueobjroot, "/src/views/", componentArr[0])
			dirs, _ := os.ReadDir(vueModelPath)
			if len(dirs) == 0 {
				_ = os.RemoveAll(vueModelPath)
			}
		}
	}

}
