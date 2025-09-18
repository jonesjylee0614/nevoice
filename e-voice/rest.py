"""E-Voice REST entrypoint."""

from __future__ import annotations

import os

from server import create_app
from server.monitoring import optional_start_monitoring, optional_stop_monitoring

app, socketio, sock = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8210))

    print("E-Voice REST API服务器启动中...")
    print(f"监听端口: {port}")
    print(f"健康检查: http://localhost:{port}/")
    print("API文档参考: tests/README.md")

    optional_start_monitoring()
    try:
        socketio.run(app, host="0.0.0.0", port=port)
    finally:
        optional_stop_monitoring()
