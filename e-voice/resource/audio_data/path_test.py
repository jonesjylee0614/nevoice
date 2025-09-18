from pathlib import Path

folder_path = Path('0')
file_paths = [file for file in folder_path.iterdir() if file.is_file()]

for file_path in file_paths:
    print(file_path)
