#!/usr/bin/env python3
"""
语音识别调试和测试脚本

功能：
1. 启动语音识别服务器
2. 生成详细的调试日志
3. 提供基本的测试功能

使用方法：
python test_speech_recognition.py
"""

import os
import subprocess
import sys
import threading
import time
from datetime import datetime

from config.config import conf

voice_conf = conf['voice']


def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")

    # 检查Python版本
    python_version = sys.version_info
    print(f"  Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version < (3, 8):
        print("  ❌ Python版本过低，需要3.8+")
        return False

    # 检查必要的依赖包
    required_packages = [
        'flask', 'flask_sock', 'flask_socketio', 'flask_cors',
        'loguru', 'numpy', 'soundfile', 'torch', 'pydub'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} 缺失")

    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False

    # 检查日志目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("  ✅ 创建logs目录")
    else:
        print("  ✅ logs目录存在")

    # 检查数据目录
    if not os.path.exists(f'{voice_conf['temp_path']}'):
        os.makedirs('data/temp', exist_ok=True)
        print("  ✅ 创建data/temp目录")
    else:
        print("  ✅ data/temp目录存在")

    return True


def clear_old_logs():
    """清理旧的日志文件"""
    print("🧹 清理旧日志...")

    log_files = [
        'logs/websocket_speech.log',
        'logs/audio_processing.log',
        'logs/recognition_results.log',
        'logs/error.log'
    ]

    for log_file in log_files:
        if os.path.exists(log_file):
            # 备份现有日志
            backup_name = f"{log_file}.backup.{int(time.time())}"
            os.rename(log_file, backup_name)
            print(f"  📦 备份: {log_file} -> {backup_name}")

    print("  ✅ 日志清理完成")


def start_server():
    """启动语音识别服务器"""
    print("🚀 启动语音识别服务器...")

    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    env['PORT'] = '8210'

    # 启动服务器
    cmd = [sys.executable, 'rest.py']

    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        print(f"  🎯 进程ID: {process.pid}")
        print(f"  🌐 服务地址: http://localhost:8210")
        print(f"  📊 测试页面: http://localhost:8210/../tests/pages/speech-recognition-test.html")
        print("  📋 按 Ctrl+C 停止服务器")

        # 实时输出日志
        def output_reader():
            for line in iter(process.stdout.readline, ''):
                if line:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] {line.rstrip()}")

        output_thread = threading.Thread(target=output_reader)
        output_thread.daemon = True
        output_thread.start()

        # 等待进程
        try:
            while True:
                if process.poll() is not None:
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n🛑 收到停止信号，关闭服务器...")
            process.terminate()

            # 等待进程结束
            try:
                process.wait(timeout=5)
                print("  ✅ 服务器已正常关闭")
            except subprocess.TimeoutExpired:
                print("  ⚠️ 强制终止服务器")
                process.kill()
                process.wait()

        return process.returncode

    except Exception as e:
        print(f"  ❌ 启动失败: {str(e)}")
        return 1


def show_log_info():
    """显示日志文件信息"""
    print("\n📊 日志文件说明:")
    log_descriptions = [
        ("logs/websocket_speech.log", "WebSocket连接和消息处理详细日志"),
        ("logs/audio_processing.log", "音频数据处理和格式转换日志"),
        ("logs/recognition_results.log", "语音识别结果和性能统计"),
        ("logs/error.log", "错误和异常信息日志")
    ]

    for log_file, description in log_descriptions:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"  📁 {log_file} ({size} bytes) - {description}")
        else:
            print(f"  📁 {log_file} (未创建) - {description}")


def main():
    """主函数"""
    print("=" * 60)
    print("🎤 E-Voice 语音识别调试工具")
    print("=" * 60)

    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请修复后重试")
        return 1

    # 清理日志
    clear_old_logs()

    # 显示日志信息
    show_log_info()

    print("\n" + "=" * 60)
    print("🎯 准备启动服务器...")
    print("   在浏览器中打开测试页面进行调试")
    print("   所有操作会记录到详细的日志文件中")
    print("=" * 60)

    # 启动服务器
    return start_server()


if __name__ == "__main__":
    sys.exit(main())
