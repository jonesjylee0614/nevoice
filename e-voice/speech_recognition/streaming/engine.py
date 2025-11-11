"""StreamingEngine push/flush 实现骨架。"""

from __future__ import annotations

import time
from typing import Iterable, List, Optional

from loguru import logger

from .loader import ModelLoader, ModelBundle
from .state import StreamingState
from .text_accumulator import TextAccumulator


class StreamingEngine:
    """处理音频 chunk 并输出识别事件骨架。"""

    def __init__(self, bundle: Optional[ModelBundle] = None) -> None:
        self._bundle = bundle or ModelLoader.current().load()

    def push(self, audio_chunk: bytes, state: StreamingState) -> List[dict]:
        state.mark_activity(int(time.time() * 1000))
        state.pending_audio.append(audio_chunk)
        state.pending_offline_audio.append(audio_chunk)

        logger.debug(
            "[engine] session=%s push chunk=%d len=%d",
            state.session_id,
            len(state.pending_audio),
            len(audio_chunk),
        )

        if self._bundle.online_asr is None:
            return []

        try:
            audio_bytes = b"".join(state.pending_audio)
            result = self._bundle.online_asr.generate(
                input=audio_bytes,
                **state.online_cache,
            )[0]
        except AttributeError:
            return []
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("[engine] online inference error: %s", exc)
            return []

        if not result or not result.get("text"):
            return []

        partial_text = result["text"]
        state.online_cache = result.get("cache", state.online_cache)
        accumulator: TextAccumulator = state.text_accumulator or TextAccumulator()
        state.text_accumulator = accumulator
        revision = state.next_revision()
        snapshot = accumulator.update_partial(partial_text, revision)
        segment_id = state.ensure_segment()
        event = {
            "type": "partial",
            "mode": "realtime",
            "revision": revision,
            "text": partial_text,
            "is_final": False,
            "session_id": state.session_id,
            "segment_id": segment_id,
            "text_state": snapshot,
        }
        state.pending_audio.clear()
        return [event]

    def flush(self, state: StreamingState) -> Iterable[dict]:
        if not state.pending_offline_audio or self._bundle.offline_asr is None:
            return []

        logger.debug("[engine] session=%s flush offline", state.session_id)
        audio_bytes = b"".join(state.pending_offline_audio)
        state.pending_offline_audio.clear()

        try:
            offline_result = self._bundle.offline_asr.generate(
                input=audio_bytes,
                **state.offline_cache,
            )[0]
        except AttributeError:
            return []
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("[engine] offline inference error: %s", exc)
            return []

        text = offline_result.get("text", "")
        if not text:
            return []

        # 标点与 ITN
        if self._bundle.punc is not None:
            try:
                punc_result = self._bundle.punc.generate(
                    input=text, **state.metrics.get("punc", {})
                )[0]
                text = punc_result.get("text", text)
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("[engine] punctuation failed: %s", exc)
        if self._bundle.itn is not None:
            try:
                itn_result = self._bundle.itn.generate(input=text)[0]
                text = itn_result.get("text", text)
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("[engine] itn failed: %s", exc)

        accumulator: TextAccumulator = state.text_accumulator or TextAccumulator()
        state.text_accumulator = accumulator
        snapshot = accumulator.apply_correction(text)
        revision = state.revision
        segment_id = state.ensure_segment()
        event = {
            "type": "correction",
            "mode": "offline" if state.mode != "online" else "realtime",
            "revision": revision,
            "text": text,
            "is_final": True,
            "session_id": state.session_id,
            "segment_id": segment_id,
            "text_state": snapshot,
        }
        return [event]

