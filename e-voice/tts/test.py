import json
import os


def delete_zero_size_files(folder_path):
    """
    删除指定文件夹中大小为0的文件
    
    Args:
        folder_path (str): 文件夹路径
    """
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹 {folder_path} 不存在")
        return

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 检查是否为文件（而不是文件夹）
        if os.path.isfile(file_path):
            # 检查文件大小是否为0
            if os.path.getsize(file_path) == 0:
                try:
                    os.remove(file_path)    
                    print(f"已删除: {file_path}")
                except Exception as e:
                    print(f"删除失败 {file_path}: {e}")


def clean_unused_wav_files(wav_folder_path, jsonl_file_path):
    """
    删除在train.jsonl文件中不存在的wav文件
    """
    # 读取train.jsonl文件中的所有key
    existing_keys = set()
    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            existing_keys.add(data['key'])

    # 遍历wav文件夹中的所有wav文件
    deleted_count = 0
    for filename in os.listdir(wav_folder_path):
        if filename.endswith('.wav'):
            # 提取文件名（不含扩展名）作为key
            key = os.path.splitext(filename)[0]
            # 如果key不在train.jsonl中，则删除该文件
            if key not in existing_keys:
                file_path = os.path.join(wav_folder_path, filename)
                os.remove(file_path)
                deleted_count += 1
                print(f"已删除: {filename}")

    print(f"总共删除了 {deleted_count} 个未使用的wav文件")


# 读取原始文件并去重
def remove_duplicates(input_file, output_file):
    """
    从输入文件读取词汇，去重后写入输出文件
    """
    # 使用集合(set)来自动去重
    unique_words = set()

    # 读取原始文件
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 去除行末的换行符和空格
            word = line.strip()
            # 添加到集合中（自动去重）
            if word:  # 确保不是空行
                unique_words.add(word)

    # 将去重后的词汇写入新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted(unique_words):  # 排序后写入，保证顺序一致
            f.write(word + '\n')

def deduplicate_jsonl(input_file, output_file):
    """
    对JSONL文件中的target字段去重，并打印出重复的文本及详细信息
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    seen_targets = {}  # 存储target和对应的首次出现的数据
    unique_entries = []
    duplicate_entries = []  # 存储重复的条目

    # 读取并去重
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            target = data['target']

            if target not in seen_targets:
                seen_targets[target] = data
                unique_entries.append(data)
            else:
                # 如果target已经存在，记录为重复项
                duplicate_entries.append({
                    'duplicate': data,
                    'first_occurrence': seen_targets[target]
                })

    # 打印重复的文本及详细信息
    if duplicate_entries:
        print("发现重复的target:")
        for entry in duplicate_entries:
            dup = entry['duplicate']
            first = entry['first_occurrence']
            print(f"  重复文本: {dup['target']}")
            print(f"    首次出现: key={first['key']}, source={first['source']}")
            print(f"    重复条目: key={dup['key']}, source={dup['source']}")
    else:
        print("未发现重复的target")

    # 写入去重后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in unique_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    return len(duplicate_entries)  # 返回重复数量
def sort_words_by_pinyin_first_letter(input_file, output_file=None):
    """
    按拼音首字母对文件内容排序（只按首字母）
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径，如果为None则覆盖原文件
    """
    try:
        from pypinyin import lazy_pinyin
    except ImportError:
        print("请先安装pypinyin库: pip install pypinyin")
        return

    # 如果没有指定输出文件，则覆盖原文件
    if output_file is None:
        output_file = input_file

    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 去除每行末尾的换行符并过滤空行
    words = [line.strip() for line in lines if line.strip()]

    # 按拼音首字母排序
    def get_first_letter(word):
        # 获取第一个字符的拼音首字母
        if word:
            pinyin_list = lazy_pinyin(word[0])
            if pinyin_list:
                return pinyin_list[0][0].upper() if pinyin_list[0] else ''
        return ''

    sorted_words = sorted(words, key=get_first_letter)

    # 写入排序后的内容
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted_words:
            f.write(word + '\n')

    print(f"已按拼音首字母排序完成，结果保存到 {output_file}")

def sort_jsonl_by_pinyin_detailed(input_file, output_file=None):
    """
    对JSONL文件中的target字段按拼音首字母排序（显示详细信息）
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径，如果为None则覆盖原文件
    """
    try:
        from pypinyin import lazy_pinyin
    except ImportError:
        print("请先安装pypinyin库: pip install pypinyin")
        return

    # 如果没有指定输出文件，则覆盖原文件
    if output_file is None:
        output_file = input_file

    # 读取所有数据
    data_entries = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            data_entries.append(data)

    print(f"排序前的前10个target: {[entry['target'] for entry in data_entries[:10]]}")

    # 按target字段的拼音首字母排序
    def get_pinyin_key(entry):
        target = entry['target']
        # 获取target的完整拼音
        return ''.join(lazy_pinyin(target))

    sorted_entries = sorted(data_entries, key=get_pinyin_key)

    # 写入排序后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in sorted_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"排序后的前10个target: {[entry['target'] for entry in sorted_entries[:10]]}")
    print(f"已按拼音首字母排序完成，结果保存到 {output_file}")


def pick_untrained_words(words_file, jsonl_file, words2_file=None):
    # 读取words.txt中的所有词语
    with open(words_file, 'r', encoding='utf-8') as f:
        words = set(line.strip() for line in f.readlines())
    
    # 读取train.jsonl中的所有target字段值
    import json
    
    targets = set()
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():  # 跳过空行
                data = json.loads(line.strip())
                targets.add(data['target'])
    
    # 找出在words.txt中但不在train.jsonl的target字段中的词语
    missing_words = words - targets
    
    # 将结果保存到words2.txt
    with open(words2_file, 'w', encoding='utf-8') as f:
        for word in sorted(missing_words):
            f.write(word + '\n')
    
    print(f"找到 {len(missing_words)} 个在words.txt中但不在train.jsonl的target字段中的词语")
    print("结果已保存到 words2.txt")

if __name__ == '__main__':
    # 删除大小为0的文件
    # folder_path = "/home/leozy/Desktop/developer/git/python/evoice/tts-voice/v"  # 替换为实际的文件夹路径
    # delete_zero_size_files(folder_path)

    # 删除在train.jsonl文件中不存在的wav文件
    # wav_folder = "/home/leozy/Desktop/developer/git/python/evoice/tts-voice/v"  # wav文件夹路径
    jsonl_file = "/home/leozy/Desktop/developer/git/python/evoice/tts-voice/output/train.jsonl"      # train.jsonl文件路径
    # clean_unused_wav_files(wav_folder, jsonl_file)


    # 执行去重操作
    # remove_duplicates('custom_word_freq.txt', 'words2.txt')
    # print("去重完成，结果已保存到 words2.txt")

    # 执行去重操作
    # deduplicate_jsonl(jsonl_file, 'train2.jsonl')
    # print("去重完成，结果已保存到 train2.jsonl")

    # 排序
    # sort_jsonl_by_pinyin_detailed(jsonl_file, 'train_sorted.jsonl')
    
    # # 排序
    # sort_words_by_pinyin_first_letter('words2.txt', 'custom_word_freq.txt')
    # print("文件内容已按行排序，结果保存到 custom_word_freq.txt")

    pick_untrained_words('custom_word_freq.txt', jsonl_file, 'words2.txt')
    
    print("Done")
    