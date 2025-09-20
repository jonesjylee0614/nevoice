# Copyright FunASR (https://github.com/alibaba-damo-academy/FunASR). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

workspace=`pwd`

# which gpu to train or finetune
export CUDA_VISIBLE_DEVICES="0"
# model_name from model_hub, or model_dir in local path
model_name_or_model_dir="iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
## generate train.jsonl and val.jsonl
train_data="../../../data/list/train.jsonl"
val_data="../../../data/list/val.jsonl"
max_epoch=10
# exp output dir
output_dir="./outputs"
conda_env="FunASR"
conda_path="~/miniforge3/bin"
help="""
  Usage: sh $0
  --cuda_devices <CUDA_VISIBLE_DEVICES> 指定cuda ids
  --model <model_name_or_model_dir>     模型名称或模型路径 默认 iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch
  --train_data <train_data>             训练数据路径
  --val_data <val_data>                 验证数据路径
  --data_dir <data_dir>                 数据集路径 (train.jsonl, val.jsonl)
  --output_dir <output_dir>             模型输出路径
  --conda_path <conda_path>             conda环境路径 默认 "~/miniforge3/bin"
  --conda_env <conda_env>               日志文件输出路径 默认 "FunASR"
"""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --cuda_devices)
            export CUDA_VISIBLE_DEVICES="$2"
            echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
            shift 2
            ;;
        --model)
            model_name_or_model_dir="$2"
            echo "model_name_or_model_dir: $model_name_or_model_dir"
            shift 2
            ;;
        --train_data)
            train_data="$2"
            echo "train_data: $train_data"
            shift 2
            ;;
        --val_data)
            val_data="$2"
            shift 2
            ;;
        --data_dir)
            data_dir="$2"
            train_data="${data_dir}/train.jsonl"
            val_data="${data_dir}/val.jsonl"
            shift 2
            ;;
        --output_dir)
            output_dir="$2"
            echo "output_dir: $output_dir"
            shift 2
            ;;
        --conda_env)
            conda_env="$2"
            echo "conda_env: $conda_env"
            shift 2
            ;;
        --conda_path)
            conda_path="$2"
            echo "conda_path: $conda_path"
            shift 2
            ;;
        --help)
            echo "$help"
            exit 0
            ;;
        -h)
            echo "$help"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

deepspeed_config=${workspace}/../../ds_stage1.json
gpu_num=$(echo $CUDA_VISIBLE_DEVICES | awk -F "," '{print NF}')

mkdir -p ${output_dir}

echo $DISTRIBUTED_ARGS
rm -rf ${output_dir}/model.*

export PATH=${conda_path}:$PATH
eval "$(conda shell.bash hook)"

conda activate ${conda_env} && torchrun \
--nnodes ${WORLD_SIZE:-1} \
--nproc_per_node $gpu_num \
--node_rank ${RANK:-0} \
--master_addr ${MASTER_ADDR:-127.0.0.1} \
--master_port ${MASTER_PORT:-26669} \
../../../funasr/bin/train_ds.py \
++model="$model_name_or_model_dir" \
++train_data_set_list="$train_data" \
++valid_data_set_list="$train_data" \
++dataset="AudioDataset" \
++dataset_conf.index_ds="IndexDSJsonl" \
++dataset_conf.data_split_num=1 \
++dataset_conf.batch_sampler="BatchSampler" \
++dataset_conf.batch_size=2000  \
++dataset_conf.sort_size=1024 \
++dataset_conf.batch_type="token" \
++dataset_conf.num_workers=4 \
++train_conf.max_epoch=$max_epoch \
++train_conf.log_interval=1 \
++train_conf.resume=false \
++train_conf.validate_interval=2000 \
++train_conf.save_checkpoint_interval=2000 \
++train_conf.keep_nbest_models=20 \
++train_conf.avg_nbest_model=10 \
++train_conf.use_deepspeed=false \
++train_conf.deepspeed_config=${deepspeed_config} \
++optim_conf.lr=0.0002 \
++output_dir="${output_dir}"

# 训练完成后 删除临时文件，保留最终结果
mv ${output_dir}/model.pt.best ${output_dir}/best_model.pt
rm -rf ${output_dir}/model.*
mv ${output_dir}/best_model.pt ${output_dir}/model.pt

echo "Finished training! see ${output_dir}/model.pt"