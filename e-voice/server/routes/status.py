"""Realtime status endpoints."""

from __future__ import annotations

import time

from flask import Blueprint, jsonify

from ..logging import logger
from ..state import active_sessions, global_counters
from speech_recognition.streaming.loader import ModelLoader


def create_status_blueprint() -> Blueprint:
    bp = Blueprint("status", __name__)

    @bp.route("/ws/status", methods=["GET"])
    def get_ws_status():
        """获取 WebSocket 状态。"""
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

    @bp.route("/api/health", methods=["GET"])
    def health_check():
        """
        健康检查端点。
        
        返回服务状态和 FunASR 模型加载情况。
        """
        try:
            loader = ModelLoader.current()
            health_info = loader.health_check()
            
            status = "healthy"
            
            # 如果模型未加载成功，则标记为 degraded
            models = health_info.get("models", {})
            if not models.get("asr_online") and not models.get("asr"):
                status = "degraded"
            
            return jsonify({
                "status": status,
                "time": int(time.time() * 1000),
                "streaming": health_info,
            })
        except Exception as exc:
            logger.error(f"健康检查失败: {exc}")
            return jsonify({
                "status": "unhealthy",
                "error": str(exc),
                "time": int(time.time() * 1000),
            }), 500

    @bp.route("/api/streaming/config", methods=["GET"])
    def get_streaming_config():
        """
        获取流式识别配置。
        
        返回当前 FunASR 配置信息。
        """
        try:
            loader = ModelLoader.current()
            config = loader.config
            
            return jsonify({
                "mode": config.get("mode", {}),
                "audio": config.get("audio", {}),
                "features": config.get("features", {}),
                "itn": config.get("itn", {}),
                "resources": config.get("resources", {}),
            })
        except Exception as exc:
            logger.error(f"获取流式配置失败: {exc}")
            return {"error": str(exc)}, 500

    @bp.route("/api/streaming/models", methods=["GET"])
    def get_streaming_models():
        """
        获取流式识别模型状态。
        
        返回已加载模型的详细信息。
        """
        try:
            loader = ModelLoader.current()
            config = loader.config
            
            result = {
                "models": {},
                "load_time_ms": None,
            }
            
            # 获取模型信息
            try:
                bundle = loader.get_bundle()
                result["models"] = {
                    "asr": {
                        "loaded": bundle.model_asr is not None,
                        "model": config.get("models", {}).get("asr", {}).get("model"),
                    },
                    "asr_online": {
                        "loaded": bundle.model_asr_online is not None,
                        "model": config.get("models", {}).get("asr_online", {}).get("model"),
                    },
                    "vad": {
                        "loaded": bundle.model_vad is not None,
                        "model": config.get("models", {}).get("vad", {}).get("model"),
                    },
                    "punc": {
                        "loaded": bundle.model_punc is not None,
                        "model": config.get("models", {}).get("punc", {}).get("model"),
                    },
                }
                result["load_time_ms"] = bundle.load_time_ms
            except Exception as e:
                logger.warning(f"获取模型信息失败: {e}")
            
            return jsonify(result)
        except Exception as exc:
            logger.error(f"获取模型状态失败: {exc}")
            return {"error": str(exc)}, 500

    return bp
