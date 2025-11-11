"""StreamingEngine behaviour tests."""

from __future__ import annotations

from typing import Dict

import pytest

from ...speech_recognition.streaming.engine import StreamingEngine
from ...speech_recognition.streaming.state import StreamingState
from ...speech_recognition.streaming.text_accumulator import TextAccumulator
from .fixtures.sample_chunks import chunk_pcm, chunk_sequence


class DummyModel:
    def __init__(self, outputs: Dict[str, Dict[str, str]] | None = None) -> None:
        self.outputs = outputs or {}

    def generate(self, *, input, **kwargs):  # type: ignore[override]
        key = "online" if kwargs == {} else "offline"
        if key == "online":
            result = self.outputs.get("online", {"text": "hello"})
            result = {**result}
            result.setdefault("cache", {})
        else:
            result = self.outputs.get("offline", {"text": "world"})
        return [result]


class DummyBundle:
    def __init__(self) -> None:
        self.vad = MagicMock()
        self.online_asr = DummyModel({"online": {"text": "part"}})
        self.offline_asr = DummyModel({"offline": {"text": "final"}})
        self.punc = DummyModel({"offline": {"text": "final."}})
        self.itn = DummyModel({"offline": {"text": "Final."}})


@pytest.fixture
def state() -> StreamingState:
    streaming_state = StreamingState(
        session_id="sess",
        request_id="req",
        chunk_interval=40,
        sample_rate=16000,
        hotwords={},
    )
    streaming_state.text_accumulator = TextAccumulator()
    return streaming_state


@pytest.fixture
def engine() -> StreamingEngine:
    return StreamingEngine(bundle=DummyBundle())


def test_push_returns_partial(engine: StreamingEngine, state: StreamingState) -> None:
    events = engine.push(chunk_pcm(), state)
    assert len(events) == 1
    event = events[0]
    assert event["type"] == "partial"
    assert event["text"] == "part"
    assert event["segment_id"].startswith("seg-")


def test_flush_returns_correction(engine: StreamingEngine, state: StreamingState) -> None:
    engine.push(chunk_pcm(), state)
    events = list(engine.flush(state))
    assert len(events) == 1
    event = events[0]
    assert event["type"] == "correction"
    assert event["text"] == "Final."
    assert event["is_final"] is True


def test_flush_without_audio(engine: StreamingEngine, state: StreamingState) -> None:
    events = list(engine.flush(state))
    assert events == []


def test_push_without_online_model(state: StreamingState) -> None:
    engine = StreamingEngine(bundle=DummyBundle())
    engine._bundle.online_asr = None  # type: ignore[attr-defined]
    events = engine.push(chunk_pcm(), state)
    assert events == []


def test_push_handles_empty_text(engine: StreamingEngine, state: StreamingState) -> None:
    engine._bundle.online_asr.outputs["online"] = {"text": ""}
    events = engine.push(chunk_silence(), state)
    assert events == []


def test_streaming_sequence(engine: StreamingEngine, state: StreamingState) -> None:
    seq = chunk_sequence()
    for chunk in seq:
        engine.push(chunk, state)
    events = list(engine.flush(state))
    assert events
    final = events[-1]
    assert final["type"] in {"correction", "final"}

