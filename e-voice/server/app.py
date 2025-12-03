"""Application factory for the E-Voice REST service."""

from __future__ import annotations

import os
from typing import Tuple

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sock import Sock
from flask_socketio import SocketIO

from config.config import conf
from rest_meeting import meeting_app
from rest_prints import print_app
from .audio_utils import init_audio_utils
from .logging import configure_logging, logger
from .routes.basic import create_basic_blueprint
from .routes.debug import create_debug_blueprint
from .routes.hotwords import create_hotword_blueprint
from .routes.logs import create_logs_blueprint
from .routes.model import create_model_blueprint
from .routes.socketio_events import register_socketio_events
from .routes.status import create_status_blueprint
from .routes.voice import create_voice_blueprint
from .routes.ws import register_ws_routes
from .routes.meeting_mdt import bp as meeting_mdt_bp
from speech_recognition.streaming.loader import ModelLoader


def create_app() -> Tuple[Flask, SocketIO, Sock]:
    configure_logging()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret!"
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.register_blueprint(print_app)
    app.register_blueprint(meeting_app)
    app.register_blueprint(meeting_mdt_bp)  # MDT会议接口
    app.json.ensure_ascii = False

    socketio = SocketIO(app, cors_allowed_origins="*")
    sock = Sock(app)

    voice_conf = conf["voice"]
    init_audio_utils(voice_conf)
    
    # 加载 FunASR 模型
    logger.info("开始加载 FunASR 模型...")
    loader = ModelLoader.current()
    loader.load()
    logger.info("FunASR 模型加载完成")

    app.register_blueprint(create_basic_blueprint())
    app.register_blueprint(create_voice_blueprint(voice_conf))
    app.register_blueprint(create_debug_blueprint())
    app.register_blueprint(create_logs_blueprint())
    app.register_blueprint(create_hotword_blueprint())
    app.register_blueprint(create_status_blueprint())
    app.register_blueprint(create_model_blueprint())
    register_ws_routes(sock)

    register_socketio_events(socketio)
    
    # 静态文件服务：音频片段
    @app.route('/data/meeting/audio_segments/<path:filename>')
    def serve_audio_segment(filename):
        """提供音频片段文件的访问"""
        audio_dir = os.path.join(os.getcwd(), 'data', 'meeting', 'audio_segments')
        return send_from_directory(audio_dir, filename)

    return app, socketio, sock
