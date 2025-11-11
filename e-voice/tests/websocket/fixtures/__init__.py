"""Streaming WebSocket fixture helpers."""

from __future__ import annotations

from pathlib import Path


def load_fixture(name: str) -> bytes:
    path = Path(__file__).resolve().parent / name
    with path.open("rb") as fp:
        return fp.read()

