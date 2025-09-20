# 源码地址

https://github.com/modelscope/FunASR/blob/main/examples/industrial_data_pretraining/paraformer/finetune.sh

## 1 拉取源码

```
git clone https://github.com/modelscope/FunASR.git
```

复制 [finetune.sh](finetune.sh) 文件到 `FunASR/examples/industrial_data_pretraining/paraformer` 目录下

## FunASR 微调训练指南

1. 环境准备

操作系统: 推荐使用 Linux 系统（如 Ubuntu 22.04）。

Python 版本: 建议使用较新版本。

深度学习框架: PyTorch 2.1.3 或更高版本。

GPU 支持: 配置 CUDA 12.1 或兼容版本，推荐高性能 GPU（如 V100 或 3090）。

安装必要依赖：

```
conda activate funasr
pip install -U modelscope funasr chardet torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 pytorch-cuda==12.1
```

2. 数据准备

数据格式要求：音频文件为 16KHz 单声道，文本标注为 UTF-8 格式。

转换数据为 JSONL 格式：

```
{"key": "", "source": "", "source_len": 90, "target": "", "target_len": 13}
{"key": "", "source": "", "source_len": 88, "target": "", "target_len": 8}
```

```
key 唯一标识符
source 源文件url或地址
source_len 源文件长度
target 识别结果
target_len 识别结果长度,如果无空格,则为字符串长度,如果有空格,则为单词数或句子数
```

将生成的 `train.jsonl` 和 `val.jsonl` 文件放入指定目录。

3. 模型下载与配置

从 ModelScope 下载预训练模型：

git clone https://www.modelscope.cn/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-online.git
/path/to/model
确保模型目录包含以下文件：

```
tokens.json：词汇表文件。
am.mvn：音频特征归一化文件。
model.pt：模型参数文件。
config.yaml：配置文件。
```

4. 微调过程

进入微调脚本目录并修改参数：

```
cd FunASR/examples/industrial_data_pretraining/paraformer_streaming
vim finetune.sh
```

调整以下参数：

```
export CUDA_VISIBLE_DEVICES="0" # 设置 GPU 设备
model_name_or_model_dir: 设置为预训练模型路径。
batch_size: 根据显存大小调整（如 2000）。
max_epoch: 设置期望的训练轮数。
```

参数释义:

```

DISTRIBUTED_ARGS="
    --nnodes ${WORLD_SIZE:-1} \
    --nproc_per_node $gpu_num \
    --node_rank ${RANK:-0} \
    --master_addr ${MASTER_ADDR:-127.0.0.1} \
    --master_port ${MASTER_PORT:-26669}
"
--nnodes ${WORLD_SIZE:-1}
指定分布式训练的节点数量
${WORLD_SIZE:-1} 表示如果环境变量 WORLD_SIZE 未设置，则默认为 1
--nproc_per_node $gpu_num
每个节点上使用的进程数（通常是GPU数量）
$gpu_num 从 CUDA_VISIBLE_DEVICES 计算得出
--node_rank ${RANK:-0}
当前节点在分布式训练中的排名
${RANK:-0} 表示如果环境变量 RANK 未设置，则默认为 0
--master_addr ${MASTER_ADDR:-127.0.0.1}
主节点的IP地址
用于节点间通信，默认为本地地址
--master_port ${MASTER_PORT:-26669}
主节点通信端口
默认端口号为 26669


训练脚本参数
传递给 ../../../funasr/bin/train_ds.py 的参数含义：
模型配置
++model: 指定要使用的模型名称或路径
++dataset: 使用的数据集类型 (AudioDataset)
++dataset_conf: 数据集相关配置
数据集配置
++train_data_set_list: 训练数据文件路径
++valid_data_set_list: 验证数据文件路径
++dataset_conf.index_ds: 索引数据集类型 (IndexDSJsonl)
++dataset_conf.batch_sampler: 批次采样器类型 (BatchSampler)
++dataset_conf.batch_size: 批次大小 (2000 tokens)
++dataset_conf.batch_type: 批次类型 (token)
++dataset_conf.num_workers: 数据加载进程数 (4)
训练配置
++train_conf.max_epoch: 最大训练轮数 (10)
++train_conf.log_interval: 日志打印间隔 (1)
++train_conf.resume: 是否恢复训练 (true)
++train_conf.validate_interval: 验证间隔 (2000 steps)
++train_conf.save_checkpoint_interval: 模型保存间隔 (2000 steps)
++optim_conf.lr: 学习率 (0.0002)
++output_dir: 输出目录
这些参数控制着分布式训练的各个方面，包括硬件资源分配、数据处理和训练过程控制。
```

运行微调脚本：

```
`sh finetune.sh \
--model {指定模型路径} \
--cuda_devices {指定GPU设备id，多个用逗号隔开} \
--train_data {训练数据jsonl路径} --val_data {验证数据jsonl路径}` \
--output_dir {指定输出路径}
```

微调完成后，模型`model.pt`会保存在 `FunASR/examples/industrial_data_pretraining/paraformer/outputs/` 目录下。

5. 验证微调后的模型

使用 Python 验证：

```
from funasr import AutoModel

model = AutoModel(model="/path/to/outputs")
res = model.generate(input="test.wav")
print(res)
```

最佳实践

确保微调数据与预训练数据分布相似，数据量建议不少于 100 小时。

使用学习率预热和早停策略防止过拟合。
定期在验证集上评估性能，保存最佳模型检查点。
通过以上步骤，您可以成功完成 FunASR 的微调并提升语音识别性能。

## 强制使用本地缓存模型

1、找到/home/leozy/miniconda3/envs/e-voice/lib/python3.12/site-packages/modelscope/hub/snapshot_download.py
2、在 `if local_files_only:`前添加以下代码
```
# ==================== 强制使用本地缓存补丁 ====================
    # 优先检查本地缓存中是否已存在模型文件（通常数量大于1）
    if len(cache.cached_files) > 1:
        # 如果有，打印一条提示信息（可选），然后直接返回本地路径，中断后续所有操作。
        print("Found local model cache, using it directly. To re-download, delete the model folder.")
        return cache.get_root_location()
    else:
        # 如果本地没有缓存，为防止上游错误地传入 local_files_only=True 导致下载失败，
        # 在这里强制将其设为 False，确保能够继续执行下载流程。
        local_files_only = False
    # ===============================================================
```