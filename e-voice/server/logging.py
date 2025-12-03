"""Logging configuration for the E-Voice service."""

from __future__ import annotations

import os
from typing import Dict

from loguru import logger

__all__ = [
    "logger",
    "ws_logger",
    "audio_logger",
    "recognition_logger",
    "key_logger",
    "configure_logging",
]

_ws_logger = None
_audio_logger = None
_recognition_logger = None
_key_logger = None
_configured = False


def configure_logging() -> Dict[str, object]:
    """Configure the structured loggers used by the REST service.

    The original rest.py file performed this configuration at import time.
    During the refactor the behaviour must remain identical, therefore we
    lazily configure the loggers the first time this function is invoked and
    reuse the same bound loggers afterwards.
    """

    global _configured, _ws_logger, _audio_logger, _recognition_logger, _key_logger

    if _configured:
        return {
            "logger": logger,
            "ws_logger": _ws_logger,
            "audio_logger": _audio_logger,
            "recognition_logger": _recognition_logger,
            "key_logger": _key_logger,
        }

    os.makedirs("logs", exist_ok=True)

    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        colorize=True,
    )
    # 记录启动与总览日志到独立文件，便于排查启动配置/设备信息
    logger.add(
        "logs/startup.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8",
    )

    _ws_logger = logger.bind(component="ws")
    _ws_logger.add(
        "logs/websocket_speech.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[component]} | {function}:{line} | {message}",
        rotation="50 MB",
        retention="7 days",
        encoding="utf-8",
        filter=lambda record: record["extra"].get("component") == "ws",
    )

    logger.add(
        "logs/error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {function}:{line} | {message}\n{exception}",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8",
    )

    _audio_logger = logger.bind(component="audio")
    _audio_logger.add(
        "logs/audio_processing.log",
        level="TRACE",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[component]} | {function}:{line} | {message}",
        rotation="100 MB",
        retention="3 days",
        encoding="utf-8",
        filter=lambda record: record["extra"].get("component") == "audio",
    )

    _recognition_logger = logger.bind(component="recognition")
    _recognition_logger.add(
        "logs/recognition_results.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[component]} | {message}",
        rotation="50 MB",
        retention="7 days",
        encoding="utf-8",
        filter=lambda record: record["extra"].get("component") == "recognition",
    )

    _key_logger = logger.bind(component="key")
    _key_logger.add(
        "logs/realtime_key.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[component]} | {message}",
        rotation="20 MB",
        retention="14 days",
        encoding="utf-8",
        filter=lambda record: record["extra"].get("component") == "key",
    )

    logger.info("日志系统初始化完成")
    logger.info("WebSocket语音识别日志: logs/websocket_speech.log")
    logger.info("音频处理日志: logs/audio_processing.log")
    logger.info("识别结果日志: logs/recognition_results.log")
    logger.info("错误日志: logs/error.log")

    _configured = True
    return {
        "logger": logger,
        "ws_logger": _ws_logger,
        "audio_logger": _audio_logger,
        "recognition_logger": _recognition_logger,
        "key_logger": _key_logger,
    }


loggers = configure_logging()
logger = loggers["logger"]
ws_logger = loggers["ws_logger"]
audio_logger = loggers["audio_logger"]
recognition_logger = loggers["recognition_logger"]
key_logger = loggers["key_logger"]
