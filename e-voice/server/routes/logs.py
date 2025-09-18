"""Log viewing endpoints."""

from __future__ import annotations

import os

from flask import Blueprint

from ..logging import logger


def create_logs_blueprint() -> Blueprint:
    bp = Blueprint("logs", __name__)

    @bp.route("/logs/websocket", methods=["GET"])
    def get_websocket_logs():
        try:
            log_file = "logs/websocket_speech.log"
            if not os.path.exists(log_file):
                return "日志文件不存在", 404
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_lines = lines[-1000:] if len(lines) > 1000 else lines
            return "".join(recent_lines), 200
        except Exception as exc:
            logger.error(f"获取WebSocket日志失败: {exc}")
            return f"获取日志失败: {exc}", 500

    @bp.route("/logs/audio", methods=["GET"])
    def get_audio_logs():
        try:
            log_file = "logs/audio_processing.log"
            if not os.path.exists(log_file):
                return "日志文件不存在", 404
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_lines = lines[-1000:] if len(lines) > 1000 else lines
            return "".join(recent_lines), 200
        except Exception as exc:
            logger.error(f"获取音频处理日志失败: {exc}")
            return f"获取日志失败: {exc}", 500

    @bp.route("/logs/recognition", methods=["GET"])
    def get_recognition_logs():
        try:
            log_file = "logs/recognition_results.log"
            if not os.path.exists(log_file):
                return "日志文件不存在", 404
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_lines = lines[-500:] if len(lines) > 500 else lines
            return "".join(recent_lines), 200
        except Exception as exc:
            logger.error(f"获取识别结果日志失败: {exc}")
            return f"获取日志失败: {exc}", 500

    @bp.route("/logs/key", methods=["GET"])
    def get_key_logs():
        try:
            log_file = "logs/realtime_key.log"
            if not os.path.exists(log_file):
                return "日志文件不存在", 404
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_lines = lines[-1000:] if len(lines) > 1000 else lines
            return "".join(recent_lines), 200
        except Exception as exc:
            logger.error(f"获取关键日志失败: {exc}")
            return f"获取日志失败: {exc}", 500

    return bp
