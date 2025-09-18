import os


# 合并 搜狗医学词汇 文件夹下的所有txt
def merge_txt_files(folder_path):
    """
    合并指定文件夹下的所有txt文件，并返回合并后的文本内容。

    参数：
    folder_path (str): 文件夹路径

    返回：
    str: 合并后的文本内容
    """
    merged_content = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                merged_content += content

    # 输出到新文件
    output_file_path = "custom_word_freq.txt"
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(merged_content)
        print(f"合并后的文本已保存到 {output_file_path}")

merge_txt_files('./搜狗医学词汇')