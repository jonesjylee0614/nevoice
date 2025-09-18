from pathlib import Path


def list_audio_files(path: Path) -> None:
    if not path.exists():
        print(f"音频测试目录不存在: {path.resolve()}")
        return

    if not path.is_dir():
        print(f"音频测试路径不是目录: {path.resolve()}")
        return

    for file_path in path.iterdir():
        if file_path.is_file():
            print(file_path)


if __name__ == "__main__":
    list_audio_files(Path("0"))
