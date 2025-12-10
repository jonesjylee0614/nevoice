package voice

import (
	"bufio"
	"fmt"
	"gofly/internal/config"
	"gofly/internal/domain/dto"
	"gofly/internal/domain/service"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/logx"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/gf"
	"gofly/pkg/utils/results"
	"io"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
)

// Hotword 热词管理控制器
type Hotword struct {
	svc *service.VoiceHotword `inject:""`
}

func init() {
	gf.RegisterRoute(&Hotword{})
}

// Get_list 获取列表 /voice/hotword/get_list
func (s *Hotword) Get_list(c *gin.Context) {
	req := gf.ReqQuery(c, &dto.VoiceHotwordPageReq{})
	cond := base.NewCond()

	// 查询条件
	cond.Where(req.Word, "word like ?", "%"+req.Word+"%")

	if req.CreatedTime != "" {
		datetimeArr := strings.Split(req.CreatedTime, ",")
		cond.Where(req.CreatedTime, "create_time between ? and ?", datetimeArr[0]+" 00:00:00", datetimeArr[1]+" 23:59:59")
	}
	cond.Order = "id desc"

	list, err := s.svc.Page(c, &req.IPage, cond)
	results.ResPage(c, req.IPage, list, err)
}

// Save 保存 /voice/hotword/save
func (s *Hotword) Save(c *gin.Context) {
	entity := gf.ReqBody(c, &biz.VoiceHotword{})

	// 去除前后空格
	entity.Word = strings.TrimSpace(entity.Word)
	if entity.Word == "" {
		results.ResError(c, fmt.Errorf("热词内容不能为空"))
		return
	}

	// 检查是否已存在（新增时检查）
	if entity.Id == 0 {
		cond := base.NewCond()
		cond.Where(true, "word = ?", entity.Word)
		existing, _ := s.svc.First(c, cond)
		if existing != nil {
			results.ResError(c, fmt.Errorf("热词【%s】已存在", entity.Word))
			return
		}
	}

	res, err := s.svc.InsertOrUpdate(c, entity)
	if err == nil {
		// 异步同步到文件
		go s.syncToFile()
	}
	results.ResSave(c, res, err)
}

// UpStatus 更新状态 /voice/hotword/upStatus
func (s *Hotword) UpStatus(c *gin.Context) {
	req := gf.ReqBody(c, &base.StatusUpd{})
	res, err := s.svc.UpdateStatus(c, req)
	if err == nil {
		// 异步同步到文件
		go s.syncToFile()
	}
	results.ResSave(c, res, err)
}

// Del 删除 /voice/hotword/del
func (s *Hotword) Del(c *gin.Context) {
	ids := gf.ReqBody(c, &base.Ids{})
	res, err := s.svc.DeleteBatch(c, ids)
	if err == nil {
		// 异步同步到文件
		go s.syncToFile()
	}
	results.ResDel(c, res, err)
}

// Get_detail 获取详情 /voice/hotword/get_detail
func (s *Hotword) Get_detail(c *gin.Context) {
	id := c.DefaultQuery("id", "")
	assert.Nil(id, "请传参数id")

	res, err := s.svc.GetById(c, id)
	results.ResObj(c, res, err)
}

// Import 批量导入 /voice/hotword/import [POST]
func (s *Hotword) Import(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		results.ResError(c, fmt.Errorf("请上传文件"))
		return
	}

	// 检查文件类型
	if !strings.HasSuffix(file.Filename, ".txt") {
		results.ResError(c, fmt.Errorf("仅支持 .txt 文件"))
		return
	}

	// 打开文件
	f, err := file.Open()
	if err != nil {
		results.ResError(c, fmt.Errorf("无法读取文件"))
		return
	}
	defer f.Close()

	// 读取文件内容
	reader := bufio.NewReader(f)
	var words []string
	for {
		line, err := reader.ReadString('\n')
		word := strings.TrimSpace(line)
		if word != "" {
			words = append(words, word)
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			results.ResError(c, fmt.Errorf("读取文件失败: %v", err))
			return
		}
	}

	if len(words) == 0 {
		results.ResError(c, fmt.Errorf("文件中没有有效内容"))
		return
	}

	// 批量插入（忽略重复）
	successCount := 0
	skipCount := 0
	for _, word := range words {
		entity := &biz.VoiceHotword{
			Word:   word,
			Status: 1,
		}

		// 检查是否已存在
		cond := base.NewCond()
		cond.Where(true, "word = ?", word)
		existing, _ := s.svc.First(c, cond)
		if existing != nil {
			skipCount++
			continue
		}

		_, err := s.svc.Insert(c, entity)
		if err == nil {
			successCount++
		}
	}

	// 同步到文件
	go s.syncToFile()

	results.Success(c, "导入完成", gin.H{
		"total":   len(words),
		"success": successCount,
		"skip":    skipCount,
	}, nil)
}

// Export 导出 /voice/hotword/export [GET]
func (s *Hotword) Export(c *gin.Context) {
	cond := base.NewCond()
	cond.Where(true, "status = ?", 1) // 只导出启用的

	list, err := s.svc.List(c, cond)
	if err != nil {
		results.ResError(c, err)
		return
	}

	// 生成文件内容
	var content strings.Builder
	for _, item := range list {
		content.WriteString(item.Word)
		content.WriteString("\n")
	}

	// 设置响应头
	c.Header("Content-Type", "text/plain; charset=utf-8")
	c.Header("Content-Disposition", "attachment; filename=hotwords.txt")
	c.String(200, content.String())
}

// Sync 手动同步到文件 /voice/hotword/sync [POST]
func (s *Hotword) Sync(c *gin.Context) {
	err := s.syncToFile()
	if err != nil {
		results.ResError(c, fmt.Errorf("同步失败: %v", err))
		return
	}
	results.Success(c, "同步成功", nil, nil)
}

// syncToFile 同步热词到文件
func (s *Hotword) syncToFile() error {
	filePath := config.Inst.Voice.HotwordFilePath
	if filePath == "" {
		logx.Warnf("热词文件路径未配置，跳过同步")
		return nil
	}

	// 查询所有启用的热词
	cond := base.NewCond()
	cond.Where(true, "status = ?", 1)
	cond.Order = "word asc"

	list, err := s.svc.List(nil, cond)
	if err != nil {
		logx.Errorf("查询热词失败: %v", err)
		return err
	}

	// 生成文件内容
	var content strings.Builder
	for _, item := range list {
		content.WriteString(item.Word)
		content.WriteString("\n")
	}

	// 写入文件
	err = os.WriteFile(filePath, []byte(content.String()), 0644)
	if err != nil {
		logx.Errorf("写入热词文件失败: %v", err)
		return err
	}

	logx.Infof("热词已同步到文件: %s, 共 %d 条", filePath, len(list))
	return nil
}

// Get_stats 获取统计信息 /voice/hotword/get_stats [GET]
func (s *Hotword) Get_stats(c *gin.Context) {
	// 总数
	totalCond := base.NewCond()
	total, _ := s.svc.Count(c, totalCond)

	// 启用数
	enabledCond := base.NewCond()
	enabledCond.Where(true, "status = ?", 1)
	enabled, _ := s.svc.Count(c, enabledCond)

	// 禁用数
	disabled := total - enabled

	results.Success(c, "获取成功", gin.H{
		"total":    total,
		"enabled":  enabled,
		"disabled": disabled,
	}, nil)
}

func (s *Hotword) Perms() map[string][]gin.HandlerFunc {
	return map[string][]gin.HandlerFunc{
		"vh:base":     {s.Get_list, s.Get_stats},
		"vh:edit":     {s.Save, s.Get_detail},
		"vh:del":      {s.Del},
		"vh:upStatus": {s.UpStatus},
		"vh:import":   {s.Import},
		"vh:export":   {s.Export},
		"vh:sync":     {s.Sync},
	}
}

