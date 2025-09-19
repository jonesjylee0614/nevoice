"""Realtime status endpoints."""

from __future__ import annotations

import time

from flask import Blueprint, jsonify

from ..logging import logger
from ..state import active_sessions, global_counters


def create_status_blueprint() -> Blueprint:
    bp = Blueprint("status", __name__)

    @bp.route("/ws/status", methods=["GET"])
    def get_ws_status():
        try:
            sessions = []
            for sid, info in active_sessions.items():
                session_info = {"session_id": sid}
                session_info.update(info)
                sessions.append(session_info)
            return jsonify(
                {
                    "counters": global_counters,
                    "active_sessions": sessions,
                    "time": int(time.time() * 1000),
                }
            )
        except Exception as exc:
            logger.error(f"获取WS状态失败: {exc}")
            return {"error": str(exc)}, 500

    return bp
