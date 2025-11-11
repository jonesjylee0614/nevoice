"""Sample PCM chunks used across streaming tests."""

from __future__ import annotations

import base64
from pathlib import Path

SILENCE_16K_MONO = b"\x00" * 320


def chunk_sequence() -> list[bytes]:
    """Return a deterministic sequence of PCM chunks for streaming tests."""
    base = chunk_pcm()
    return [base, base, SILENCE_16K_MONO]


def chunk_pcm() -> bytes:
    data = (
        "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAACR1DUgAAAAAAAB//w8AAP8PAAAfDwAAHw8AAD8P"
    )
    return base64.b64decode(data)


def chunk_silence() -> bytes:
    return SILENCE_16K_MONO


def chunk_from_file(name: str) -> bytes:
    fixture_dir = Path(__file__).resolve().parent
    return (fixture_dir / name).read_bytes()

