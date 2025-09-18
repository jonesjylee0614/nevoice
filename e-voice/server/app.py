"""Application factory for the E-Voice REST service."""

from __future__ import annotations

from typing import Tuple

from flask import Flask
from flask_cors import CORS
from flask_sock import Sock
from flask_socketio import SocketIO

from config.config import conf
from rest_meeting import meeting_app
from rest_prints import print_app

from .audio_utils import init_audio_utils
from .logging import configure_logging
from .routes.basic import create_basic_blueprint
from .routes.debug import create_debug_blueprint
from .routes.hotwords import create_hotword_blueprint
from .routes.logs import create_logs_blueprint
from .routes.socketio_events import register_socketio_events
from .routes.status import create_status_blueprint
from .routes.voice import create_voice_blueprint
from .routes.ws import register_ws_routes


def create_app() -> Tuple[Flask, SocketIO, Sock]:
    configure_logging()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret!"
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.register_blueprint(print_app)
    app.register_blueprint(meeting_app)
    app.json.ensure_ascii = False

    socketio = SocketIO(app, cors_allowed_origins="*")
    sock = Sock(app)

    voice_conf = conf["voice"]
    init_audio_utils(voice_conf)

    app.register_blueprint(create_basic_blueprint())
    app.register_blueprint(create_voice_blueprint(voice_conf))
    app.register_blueprint(create_debug_blueprint())
    app.register_blueprint(create_logs_blueprint())
    app.register_blueprint(create_hotword_blueprint())
    app.register_blueprint(create_status_blueprint())

    register_socketio_events(socketio)
    register_ws_routes(sock)

    return app, socketio, sock
