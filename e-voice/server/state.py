"""Shared realtime session state."""

from __future__ import annotations

active_sessions = {}

global_counters = {
    "total_connections": 0,
    "active_connections": 0,
    "total_messages": 0,
    "total_chunks": 0,
    "total_partials": 0,
    "total_finals": 0,
}
