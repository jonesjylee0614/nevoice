
# 读取文件 custom_word_freq.txt
# 每行调用语音生成，生成语音到当前文件夹 ./v 文件夹下
# 组装 train.jsonl 格式为 {"key": "", "source": "", "source_len": 90, "target": "", "target_len": 13}
# key：自动生成uuid  source：输入文件  source_len：文本长度  target：输入文字  target_len：文本长度


import uuid
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# from demo_duoren import zhibei_emo
from aliyun import qwen_tts

# 确保输出目录存在
os.makedirs('./v_qwen', exist_ok=True)
os.makedirs('./output', exist_ok=True)


def process_line(line):
    """
    处理单行文本：生成语音并返回JSON数据
    """
    line = line.strip()
    if not line:  # 跳过空行
        return None

    # 生成唯一标识符
    unique_id = str(uuid.uuid4())

    # 生成语音文件路径
    output_wav_path = f'./v_qwen/{unique_id}.wav'

    # 调用语音生成函数
    # zhibei_emo(text=line, out_path=output_wav_path)

    qwen_tts(text=line, out_path=output_wav_path)

    print(f'Generated speech for line:[{line}] ,path:[{output_wav_path}]')

    # 组装 JSON 数据
    data = {
        "key": unique_id,
        "source": output_wav_path,
        "source_len": len(line),  # 这里应该是音频时长，暂时用文本长度代替
        "target": line,
        "target_len": len(line)
    }

    return data


def generate_speech_and_json(input_file='custom_word_freq.txt', max_workers=3):
    # 读取输入文件并处理每一行
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # 使用线程池执行语音生成
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_line = {executor.submit(process_line, line): line for line in lines}

        # 收集结果并写入JSONL文件
        with open('./output/train.jsonl', 'a', encoding='utf-8') as jsonl_file:
            for future in as_completed(future_to_line):
                try:
                    result = future.result()
                    if result:
                        # 写入 JSONL 文件
                        jsonl_file.write(json.dumps(result, ensure_ascii=False) + '\n')
                except Exception as exc:
                    line = future_to_line[future]
                    print(f'Line {line} generated an exception: {exc}')

# 执行主函数
if __name__ == "__main__":
    generate_speech_and_json()
