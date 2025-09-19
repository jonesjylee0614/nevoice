"""Utility helpers for optional system monitoring integration."""

from __future__ import annotations

from .logging import logger

try:  # pragma: no cover - optional dependency
    from monitoring.system_monitor import (  # type: ignore
        start_system_monitoring,
        stop_system_monitoring,
        system_monitor,
    )

    monitoring_available = True
except Exception as exc:  # pragma: no cover - defensive logging
    monitoring_available = False
    system_monitor = None  # type: ignore[assignment]
    start_system_monitoring = None  # type: ignore[assignment]
    stop_system_monitoring = None  # type: ignore[assignment]
    logger.warning(f"⚠️ 系统监控模块不可用，将跳过监控功能: {exc}")


def record_connection(active: bool) -> None:
    if not monitoring_available or system_monitor is None:
        return
    try:
        system_monitor.record_connection(active)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.debug(f"记录连接状态失败: {exc}")


def optional_start_monitoring() -> None:
    if callable(start_system_monitoring):
        try:
            start_system_monitoring()
            logger.success("🔍 系统监控已启动")
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning(f"⚠️ 系统监控启动失败: {exc}")


def optional_stop_monitoring() -> None:
    if callable(stop_system_monitoring):
        try:
            stop_system_monitoring()
            logger.info("🔍 系统监控已停止")
        except Exception:  # pragma: no cover - defensive logging
            pass
