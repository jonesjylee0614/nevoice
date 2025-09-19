"""Hotword management endpoints."""

from __future__ import annotations

import time

from flask import Blueprint, jsonify, request

from ..hotwords import get_hotword_manager
from ..logging import logger


def create_hotword_blueprint() -> Blueprint:
    bp = Blueprint("hotwords", __name__)

    @bp.route("/api/hotwords", methods=["GET"])
    def get_hotwords():
        try:
            manager = get_hotword_manager()
            hotwords = manager.get_all_hotwords()
            return jsonify(
                {
                    "hotwords": hotwords,
                    "count": len(hotwords),
                    "timestamp": int(time.time() * 1000),
                }
            )
        except Exception as exc:
            logger.error(f"获取热词失败: {exc}")
            return {"error": str(exc)}, 500

    @bp.route("/api/hotwords/add", methods=["POST"])
    def add_hotword():
        try:
            data = request.get_json()
            if not data or "wrong_word" not in data or "correct_word" not in data:
                return {"error": "缺少必要参数: wrong_word, correct_word"}, 400

            wrong_word = data["wrong_word"].strip()
            correct_word = data["correct_word"].strip()
            source = data.get("source", "api")

            if not wrong_word or not correct_word:
                return {"error": "错误词和正确词不能为空"}, 400

            manager = get_hotword_manager()
            manager.add_dynamic_hotword(wrong_word, correct_word, source)

            return jsonify(
                {
                    "success": True,
                    "message": f"成功添加热词映射: '{wrong_word}' -> '{correct_word}'",
                    "hotword": {
                        "wrong_word": wrong_word,
                        "correct_word": correct_word,
                        "source": source,
                    },
                }
            )
        except Exception as exc:
            logger.error(f"添加热词失败: {exc}")
            return {"error": str(exc)}, 500

    @bp.route("/api/hotwords/learn", methods=["POST"])
    def learn_from_correction():
        try:
            data = request.get_json()
            if not data or "original_text" not in data or "corrected_text" not in data:
                return {"error": "缺少必要参数: original_text, corrected_text"}, 400

            original_text = data["original_text"].strip()
            corrected_text = data["corrected_text"].strip()

            if not original_text or not corrected_text:
                return {"error": "原始文本和纠正文本不能为空"}, 400

            if original_text == corrected_text:
                return {"error": "原始文本和纠正文本相同，无需学习"}, 400

            manager = get_hotword_manager()
            manager.learn_from_correction(original_text, corrected_text)

            return jsonify(
                {
                    "success": True,
                    "message": "用户纠错学习完成",
                    "learning": {
                        "original_text": original_text,
                        "corrected_text": corrected_text,
                    },
                }
            )
        except Exception as exc:
            logger.error(f"纠错学习失败: {exc}")
            return {"error": str(exc)}, 500

    @bp.route("/api/hotwords/suggestions", methods=["GET"])
    def get_hotword_suggestions():
        try:
            partial_text = request.args.get("text", "").strip()
            limit = int(request.args.get("limit", 5))

            if not partial_text:
                return {"error": "缺少查询文本参数"}, 400

            manager = get_hotword_manager()
            suggestions = manager.get_hotword_suggestions(partial_text, limit)

            return jsonify(
                {
                    "suggestions": suggestions,
                    "query": partial_text,
                    "count": len(suggestions),
                }
            )
        except Exception as exc:
            logger.error(f"获取热词建议失败: {exc}")
            return {"error": str(exc)}, 500

    @bp.route("/api/hotwords/cleanup", methods=["POST"])
    def cleanup_hotwords():
        try:
            data = request.get_json() or {}
            days_threshold = int(data.get("days_threshold", 90))

            manager = get_hotword_manager()
            removed_count = manager.cleanup_old_hotwords(days_threshold)

            return jsonify(
                {
                    "success": True,
                    "message": f"清理完成，删除了{removed_count}个长期未使用的热词",
                    "removed_count": removed_count,
                    "days_threshold": days_threshold,
                }
            )
        except Exception as exc:
            logger.error(f"清理热词失败: {exc}")
            return {"error": str(exc)}, 500

    @bp.route("/api/hotwords/stats", methods=["GET"])
    def get_hotword_stats():
        try:
            manager = get_hotword_manager()
            stats = {
                "static_count": len(manager.static_hotwords),
                "dynamic_count": len(manager.dynamic_hotwords),
                "user_learning_count": len(manager.user_corrections),
                "total_count": len(manager.get_all_hotwords()),
                "usage_stats": dict(list(manager.hotword_usage_stats.items())[:10]),
            }
            return jsonify(stats)
        except Exception as exc:
            logger.error(f"获取热词统计失败: {exc}")
            return {"error": str(exc)}, 500

    return bp
