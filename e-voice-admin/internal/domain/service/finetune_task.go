package service

import (
	"bufio"
	"fmt"
	"gofly/internal/config"
	"gofly/internal/model/base"
	"gofly/internal/model/biz"
	"gofly/pkg/ioc"
	"gofly/pkg/logx"
	"gofly/pkg/utils/assert"
	"gofly/pkg/utils/errorx"
	"gofly/pkg/utils/gf"
	"os"
	"os/exec"
	"path"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// FinetuneTask 录音范文列表
type FinetuneTask struct {
	base.DaoImpl[*biz.FinetuneTask]
	DetailSvc *FinetuneVoiceDetail `inject:""`
}

// generateTrainData 生成训练数据并写入JSONL文件
func (t FinetuneTask) generateTrainData(filePath string, list []*biz.FinetuneVoiceDetail) error {
	// 创建或打开文件
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
	if err != nil {
		return fmt.Errorf("无法创建文件: %v", err)
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	defer writer.Flush()

	count := len(list)
	// 生成随机前缀
	prefix := gf.RandString(8)

	for i, item := range list {
		// 自动生成 key，格式为 prefix + 序号（补零）
		key := fmt.Sprintf("%s_%0*d", prefix, len(fmt.Sprintf("%d", count)), i+1)
		source := item.VoicePath
		target := item.Text

		// 构造 JSON 行
		jsonLine := fmt.Sprintf(`{"key": "%s", "source": "%s", "source_len": %d, "target": "%s", "target_len": %d}`,
			key, source, len(source), target, len(target))

		// 写入文件
		_, err := writer.WriteString(jsonLine + "\n")
		if err != nil {
			return fmt.Errorf("写入文件失败: %v", err)
		}
	}

	return nil
}

func (t FinetuneTask) Start(c *gin.Context, id int64) (string, error) {
	// 结束已存在的进程
	pids := t.GetPid(c)
	if len(pids) > 0 {
		err := t.KillProcess(c, pids)
		if err != nil {
			return "", errorx.NewBiz("结束进程失败 %s", err.Error())
		}
	}

	task, err := t.GetById(c, id)
	if err != nil || task.Id == 0 {
		return "", errorx.NewBiz("任务不存在 %d", id)
	}

	timeUnix := time.Now().UnixMilli()
	outDir := fmt.Sprintf("%s/%d/%d", config.Inst.Voice.FunAsrOutputDir, id, timeUnix)
	logDir := fmt.Sprintf("%s/log", outDir)
	dataDir := fmt.Sprintf("%s/data", outDir)

	// 静默创建文件夹，包括父级目录
	t.checkDir(logDir)
	t.checkDir(dataDir)

	relativePath := fmt.Sprintf("%d/%d", id, timeUnix)

	trainData := fmt.Sprintf("%s/train.jsonl", dataDir)

	// 查询待训练的语料，组装jsonl文件
	list, err := t.DetailSvc.ListToBeFinetune(c)
	assert.ErrIsNilAppendErr(err, "查询待训练的语料失败")
	assert.IsTrue(nil != list && len(list) >= 0, "没有待训练的语料")

	err = t.generateTrainData(trainData, list)
	assert.ErrIsNilAppendErr(err, "组装jsonl文件失败")

	// FIXME 后期组装待验证的语料
	valData := trainData

	// FIXME 后期可以手动指定
	model := config.Inst.Voice.ModelTrain

	// 执行finetune.sh训练脚本
	shPath := config.Inst.Voice.FunAsrPath + "/examples/industrial_data_pretraining/paraformer/"

	// sh finetune.sh \
	// --model {指定基础模型路径} \
	// --cuda_devices {指定显卡id 如 2,3} \
	// --train_data {指定训练数据jsonl路径} \
	// --val_data {指定验证数据jsonl路径} \
	// --output_dir {指定模型输出文件夹}
	// --log_file {指定日志输出路径}

	logFile := fmt.Sprintf("%s/finetune-task.log", logDir)

	// 日志信息
	task.LogPath = fmt.Sprintf("%s/log/finetune-task.log", relativePath)
	// 生成模型地址
	task.ModelPath = fmt.Sprintf("%s/%s", relativePath, "model.pt")
	// 基础模型路径
	//task.BaseModelPath = model
	task.Status = 1
	_, err = t.Update(c, task)
	if err != nil {
		return "", err
	}

	// 启用conda环境
	// cd 到脚本所在目录
	// 执行训练脚本
	script := fmt.Sprintf(`
nohup sh finetune.sh \
	--conda_path %s \
	--conda_env %s \
	--model %s \
	--cuda_devices %s \
	--train_data %s \
	--val_data %s \
	--output_dir %s \
> %s 2>&1 &
`, config.Inst.Voice.CondaPath, config.Inst.Voice.FunAsrCondaEnvName, model, config.Inst.Voice.CudaDevices, trainData, valData, outDir, logFile)
	logx.Infof("组装训练脚本: %s", script)
	// 执行 shell 脚本
	cmd := exec.Command("bash", "-c", script)
	cmd.Dir = shPath
	output, err := cmd.CombinedOutput()

	if err != nil {
		assert.ErrIsNilAppendErr(err, "执行脚本失败")
	}
	return fmt.Sprintf("脚本执行成功: %s", string(output)), nil
}

func (t FinetuneTask) checkDir(dir string) {
	// 判断日志文件夹是否存在
	err := os.MkdirAll(dir, 0755)
	if err != nil {
		fmt.Printf("创建目录失败: %v\n", err)
		assert.ErrIsNilAppendErr(err, "创建目录失败")
	}
}

func (t FinetuneTask) GetPid(c *gin.Context) []int {
	cmd := exec.Command("bash", "-c", "nvidia-smi | grep 'FunASR' | awk '{print $5}'")
	output, err := cmd.Output()

	if err != nil {
		return []int{}
	}
	lines := strings.Split(string(output), "\n")
	var pids []int
	for _, line := range lines {
		if strings.TrimSpace(line) != "" {
			if pid, err := strconv.Atoi(strings.TrimSpace(line)); err == nil {
				pids = append(pids, pid)
			}
		}
	}
	if len(pids) == 0 {
		return []int{}
	}
	return pids
}

// 通过pid结束进程
func (t FinetuneTask) KillProcess(c *gin.Context, pids []int) error {
	for _, pid := range pids {
		cmd := exec.Command("bash", "-c", fmt.Sprintf("kill -9 %d", pid))
		output, err := cmd.Output()
		if err != nil {
			return err
		}
		logx.Infof("结束进程: pid:%d, msg: %s", pid, string(output))
	}
	return nil
}

func (t FinetuneTask) Log(c *gin.Context, id int64) (map[string]string, error) {
	m := map[string]string{
		"log":      "",
		"lastLine": "",
	}
	// 通过日志文件路径查询日志
	task, err := t.GetById(c, id)
	if err != nil || task.Id == 0 {
		return m, errorx.NewBiz("任务不存在 %d", id)
	}

	absPath := path.Join(config.Inst.Voice.FunAsrOutputDir, task.LogPath)

	file, err := os.Open(absPath)
	if err != nil {
		return m, err
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	log := ""
	lastLine := ""
	for scanner.Scan() {
		txt := scanner.Text()
		lastLine = txt
		log += txt + "\n"
	}

	m["log"] = log
	m["lastLine"] = lastLine

	return m, scanner.Err()
}

func init() {
	ioc.PrepareDao(new(FinetuneTask))
}
