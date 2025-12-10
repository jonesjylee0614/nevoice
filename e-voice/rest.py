"""E-Voice REST entrypoint."""

from __future__ import annotations

import os
import signal
import sys

from server import create_app
from server.monitoring import optional_start_monitoring, optional_stop_monitoring

app, socketio, sock = create_app()

# 全局标志用于优雅关闭
_shutdown_requested = False


def _signal_handler(signum, frame):
    """处理 Ctrl+C 信号，确保快速退出"""
    global _shutdown_requested
    if _shutdown_requested:
        # 第二次 Ctrl+C，强制退出
        print("\n强制退出...")
        sys.exit(1)
    
    _shutdown_requested = True
    print("\n正在关闭服务器...")
    optional_stop_monitoring()
    sys.exit(0)


if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    
    port = int(os.environ.get("PORT", 8210))

    print("E-Voice REST API服务器启动中...")
    print(f"监听端口: {port}")
    print(f"健康检查: http://localhost:{port}/")
    print("API文档参考: tests/README.md")

    optional_start_monitoring()
    try:
        # 使用 threading 模式而不是 eventlet，以便信号处理正常工作
        socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
    finally:
        optional_stop_monitoring()
