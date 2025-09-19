"""Basic health and placeholder endpoints."""

from __future__ import annotations

import traceback

from flask import Blueprint, jsonify, request


def create_basic_blueprint() -> Blueprint:
    bp = Blueprint("basic", __name__)

    @bp.route("/")
    def index():
        return "success"

    @bp.route("/embedding", methods=["POST"])
    def embedding_and_return():
        try:
            request.get_json()
            return jsonify({"success": True})
        except Exception as exc:
            print(f"Embedding处理错误: {traceback.format_exc()}")
            return {"error": f"Embedding处理失败: {exc}"}, 500

    return bp
