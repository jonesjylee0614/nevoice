"""Utility helpers for optional system monitoring integration."""

from __future__ import annotations

import os
from .logging import logger

# 读取监控配置
def _get_monitoring_enabled() -> bool:
    """从配置文件读取监控开关状态。"""
    try:
        import configparser
        env = os.environ.get("EVOICE_ENV", "dev")
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", f"{env}.ini")
        
        if not os.path.exists(config_path):
            # 如果环境特定配置不存在，尝试默认配置
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "dev.ini")
        
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')
            if config.has_option('monitoring', 'enabled'):
                return config.getboolean('monitoring', 'enabled')
        
        # 默认禁用监控
        return False
    except Exception as exc:
        logger.warning(f"读取监控配置失败，默认禁用监控: {exc}")
        return False


# 读取配置决定是否启用监控
_monitoring_config_enabled = _get_monitoring_enabled()

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
    if not monitoring_available or system_monitor is None or not _monitoring_config_enabled:
        return
    try:
        system_monitor.record_connection(active)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.debug(f"记录连接状态失败: {exc}")


def optional_start_monitoring() -> None:
    """根据配置启动系统监控。
    
    只有在配置文件中 [monitoring] enabled = true 时才会启动。
    """
    if not _monitoring_config_enabled:
        logger.info("🔍 系统监控已禁用 (配置: monitoring.enabled = false)")
        return
    
    if callable(start_system_monitoring):
        try:
            start_system_monitoring()
            logger.success("🔍 系统监控已启动")
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning(f"⚠️ 系统监控启动失败: {exc}")


def optional_stop_monitoring() -> None:
    """停止系统监控。"""
    if not _monitoring_config_enabled:
        return
    
    if callable(stop_system_monitoring):
        try:
            stop_system_monitoring()
            logger.info("🔍 系统监控已停止")
        except Exception:  # pragma: no cover - defensive logging
            pass
