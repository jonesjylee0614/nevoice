"""Hotword management endpoints - 热词缓存刷新接口"""

from __future__ import annotations

import time

from flask import Blueprint, jsonify

from ..logging import logger

# 同音词修正器的热词刷新
try:
    from zh_correct.homophone_corrector import reload_hotwords as reload_homophone_hotwords, get_corrector
    HOMOPHONE_CORRECTOR_AVAILABLE = True
except ImportError:
    HOMOPHONE_CORRECTOR_AVAILABLE = False
    reload_homophone_hotwords = None
    get_corrector = None


def create_hotword_blueprint() -> Blueprint:
    bp = Blueprint("hotwords", __name__)

    @bp.route("/api/hotwords/reload", methods=["POST"])
    def reload_hotwords():
        """重新加载同音词修正器的热词缓存（从数据库）
        
        Go 后端在热词变更时调用此接口刷新 Python 端的热词缓存
        """
        try:
            if not HOMOPHONE_CORRECTOR_AVAILABLE:
                return {"error": "同音词修正器不可用"}, 500
            
            # 重新加载热词
            reload_homophone_hotwords()
            
            # 获取加载后的统计信息
            corrector = get_corrector()
            stats = corrector.get_stats()
            
            logger.info(f"热词缓存刷新成功: {stats}")
            
            return jsonify({
                "success": True,
                "message": "热词缓存刷新成功",
                "stats": stats,
                "timestamp": int(time.time() * 1000),
            })
        except Exception as exc:
            logger.error(f"热词缓存刷新失败: {exc}")
            return {"error": str(exc)}, 500

    @bp.route("/api/hotwords/stats", methods=["GET"])
    def get_hotword_stats():
        """获取热词统计信息"""
        try:
            if not HOMOPHONE_CORRECTOR_AVAILABLE:
                return {"error": "同音词修正器不可用"}, 500
            
            corrector = get_corrector()
            stats = corrector.get_stats()
            return jsonify(stats)
        except Exception as exc:
            logger.error(f"获取热词统计失败: {exc}")
            return {"error": str(exc)}, 500

    return bp
