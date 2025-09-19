"""Debug utilities for recorded sessions."""

from __future__ import annotations

import json
import os

from flask import Blueprint, send_file


def create_debug_blueprint() -> Blueprint:
    bp = Blueprint("voice_debug", __name__)

    @bp.route("/voice/debug/sessions", methods=["GET"])
    def list_debug_sessions():
        try:
            sessions_dir = "data/temp"
            if not os.path.exists(sessions_dir):
                return {"error": "调试目录不存在"}, 404

            sessions = []
            for item in os.listdir(sessions_dir):
                session_path = os.path.join(sessions_dir, item)
                if os.path.isdir(session_path) and item.startswith("session_"):
                    wav_files = []
                    pcm_files = []
                    stats_file = None
                    for file_name in os.listdir(session_path):
                        if file_name.endswith(".wav"):
                            wav_files.append(file_name)
                        elif file_name.endswith(".pcm"):
                            pcm_files.append(file_name)
                        elif file_name == "audio_stats.json":
                            stats_file = file_name

                    if wav_files or pcm_files:
                        sessions.append(
                            {
                                "session_id": item,
                                "path": session_path,
                                "wav_files": wav_files,
                                "pcm_files": pcm_files,
                                "has_stats": stats_file is not None,
                                "created_time": os.path.getctime(session_path),
                            }
                        )

            sessions.sort(key=lambda x: x["created_time"], reverse=True)
            return {"sessions": sessions}
        except Exception as exc:
            return {"error": f"获取会话列表失败: {exc}"}, 500

    @bp.route("/voice/debug/sessions/<session_id>/download/<filename>", methods=["GET"])
    def download_debug_audio(session_id: str, filename: str):
        try:
            if ".." in filename or "/" in filename or "\\" in filename:
                return {"error": "非法文件名"}, 400

            session_path = os.path.join("data/temp", session_id)
            if not os.path.exists(session_path):
                return {"error": "会话不存在"}, 404

            file_path = os.path.join(session_path, filename)
            if not os.path.exists(file_path):
                return {"error": "文件不存在"}, 404

            if filename.endswith(".wav"):
                mime_type = "audio/wav"
            elif filename.endswith(".pcm"):
                mime_type = "application/octet-stream"
            elif filename.endswith(".json"):
                mime_type = "application/json"
            else:
                mime_type = "application/octet-stream"

            return send_file(file_path, mimetype=mime_type, as_attachment=True, download_name=filename)
        except Exception as exc:
            return {"error": f"下载文件失败: {exc}"}, 500

    @bp.route("/voice/debug/sessions/<session_id>/stats", methods=["GET"])
    def get_session_stats(session_id: str):
        try:
            session_path = os.path.join("data/temp", session_id)
            stats_path = os.path.join(session_path, "audio_stats.json")
            if not os.path.exists(stats_path):
                return {"error": "统计信息不存在"}, 404

            with open(stats_path, "r", encoding="utf-8") as f:
                stats = json.load(f)
            return {"stats": stats}
        except Exception as exc:
            return {"error": f"获取统计信息失败: {exc}"}, 500

    return bp
