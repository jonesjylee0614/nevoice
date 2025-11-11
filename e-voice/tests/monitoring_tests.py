import pytest

from monitoring.streaming_metrics import StreamingMetrics


def test_streaming_metrics_to_dict():
    metrics = StreamingMetrics(stream_latency_ms=120.5, correction_latency_ms=980.0, active_sessions=3)
    metrics.extras["custom"] = 42.0
    data = metrics.to_dict()
    assert data["stream_latency_ms"] == 120.5
    assert data["correction_latency_ms"] == 980.0
    assert data["active_sessions"] == 3.0
    assert data["custom"] == 42.0
