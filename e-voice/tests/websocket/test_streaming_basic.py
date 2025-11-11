import json
from unittest.mock import MagicMock

import pytest

from ...server.routes.ws_v2 import _send_events
from ...speech_recognition.streaming.state import StreamingState
from .fixtures.sample_chunks import chunk_sequence


@pytest.fixture
def state():
    return StreamingState(
        session_id="sess-test",
        request_id="req-test",
        chunk_interval=40,
        sample_rate=16000,
        hotwords={},
    )


def test_send_events_enriches_fields(state):
    ws = MagicMock()
    events = [{"type": "partial", "text": "hello"}]
    _send_events(ws, events, state, "req-test")
    payload = json.loads(ws.send.call_args[0][0])
    assert payload["session_id"] == state.session_id
    assert payload["request_id"] == "req-test"
    assert payload["segment_id"].startswith("seg-")
    assert payload["mode"] == "realtime"


def test_send_events_correction_mode(state):
    ws = MagicMock()
    events = [{"type": "correction", "text": "hello", "mode": "offline", "is_final": True}]
    _send_events(ws, events, state, "req-test")
    payload = json.loads(ws.send.call_args[0][0])
    assert payload["mode"] == "offline"
    assert payload["is_final"] is True
    assert payload["segment_id"].startswith("seg-")


def test_send_events_attaches_metadata(state):
    ws = MagicMock()
    events = [{"type": "partial", "text": "你好", "confidence": 0.87}]
    state.hotwords = {"custom": 1.2}
    _send_events(ws, events, state, "req-meta")
    payload = json.loads(ws.send.call_args[0][0])
    assert payload["mode"] == "realtime"
    assert payload["confidence"] == pytest.approx(0.87)
    assert payload["metadata"]["hotwords"] == ["custom"]


def test_send_events_includes_preferences(state):
    ws = MagicMock()
    events = [{"type": "started", "text": ""}]
    _send_events(ws, events, state, "req-pref")
    payload = json.loads(ws.send.call_args[0][0])
    assert "preferences" not in payload["metadata"]


def test_send_events_handles_dual_mode(state):
    ws = MagicMock()
    events = [
        {"type": "partial", "text": "foo", "revision": 1},
        {"type": "correction", "text": "foo bar", "mode": "offline", "revision": 2},
    ]
    _send_events(ws, events, state, "req-dual")
    partial_payload = json.loads(ws.send.call_args_list[0][0][0])
    correction_payload = json.loads(ws.send.call_args_list[1][0][0])
    assert partial_payload["revision"] == 1
    assert correction_payload["mode"] == "offline"
    assert correction_payload["revision"] == 2
    assert "route" not in correction_payload["metadata"]


def test_chunk_sequence_fixture():
    seq = chunk_sequence()
    assert len(seq) == 3
    assert seq[0] == seq[1]
    assert seq[2] != seq[0]