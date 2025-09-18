"""WebSocket streaming endpoint registration."""

from __future__ import annotations

import json
import time
import traceback
import uuid

from flask_sock import Sock

from ..logging import key_logger, ws_logger
from ..session import RealtimeSpeechSession
from ..state import active_sessions, global_counters
from ..text_processing import normalize_text


def register_ws_routes(sock: Sock) -> None:
    @sock.route("/ws/recognize")
    def ws_recognize(ws):
        session_id = str(uuid.uuid4())[:8]
        ws_logger.info(f"会话开始: {session_id}")
        key_logger.info(f"session={session_id} started")
        session = RealtimeSpeechSession()
        try:
            session.set_session(session_id)
        except Exception:
            pass
        try:
            global_counters["total_connections"] += 1
            global_counters["active_connections"] += 1
            active_sessions[session_id] = {
                "start": int(time.time() * 1000),
                "chunks": 0,
                "partials": 0,
                "finals": 0,
                "last_active": int(time.time() * 1000),
                "last_partial": "",
                "last_final": "",
            }
        except Exception:
            pass

        message_count = 0
        audio_chunks_received = 0
        partial_results_sent = 0
        final_results_sent = 0

        while True:
            try:
                message = ws.receive()
                message_count += 1
                try:
                    global_counters["total_messages"] += 1
                except Exception:
                    pass

                if not message:
                    ws_logger.debug(f"会话{session_id}: 收到空消息，连接关闭")
                    break

                msg = json.loads(message)

                seq_local = None
                if "data" in msg and isinstance(msg.get("data"), dict):
                    data_obj = msg["data"]
                    status = data_obj.get("status")
                    mapped_type = "chunk"
                    if status == 0:
                        mapped_type = "start"
                    elif status == 2:
                        mapped_type = "end"

                    fmt = data_obj.get("format", "audio/L16;rate=16000")
                    fmt_lower = str(fmt).lower()
                    if "l16" in fmt_lower or "pcm" in fmt_lower:
                        audio_format = "pcm"
                    elif "webm" in fmt_lower:
                        audio_format = "webm"
                    else:
                        audio_format = "wav"

                    try:
                        if "rate=" in fmt_lower:
                            sr_txt = fmt_lower.split("rate=")[-1].split(";")[0]
                            sample_rate = int(sr_txt)
                        else:
                            sample_rate = int(msg.get("sample_rate", 16000))
                    except Exception:
                        sample_rate = 16000

                    msg_type = mapped_type
                    audio_data = data_obj.get("audio", "")
                    try:
                        seq_local = data_obj.get("seq", msg.get("seq"))
                    except Exception:
                        seq_local = None
                else:
                    msg_type = msg.get("type", "chunk")
                    audio_data = msg.get("audio", "")
                    audio_format = msg.get("format", "pcm")
                    sample_rate = msg.get("sample_rate", 16000)
                    try:
                        seq_local = msg.get("seq")
                    except Exception:
                        seq_local = None

                ws_logger.debug(
                    f"会话{session_id}: 收到消息#{message_count}, type={msg_type}, format={audio_format}"
                )

                if msg_type == "start":
                    ws_logger.info(f"会话{session_id}: 开始实时识别")
                    session.reset()
                    try:
                        active_sessions[session_id]["last_active"] = int(time.time() * 1000)
                    except Exception:
                        pass

                    response = {
                        "type": "started",
                        "message": "实时识别已开始",
                        "timestamp": int(time.time() * 1000),
                        "session_id": session_id,
                    }
                    ws.send(json.dumps(response))
                    ws_logger.debug(f"会话{session_id}: 发送started消息")
                    continue

                if msg_type == "end":
                    ws_logger.info(f"会话{session_id}: 结束实时识别，处理最终结果")
                    key_logger.info(f"session={session_id} end requested")

                    final_sentence = None
                    if session.full_sentence:
                        final_sentence = session.finalize_current_sentence()
                        if final_sentence:
                            final_sentence = normalize_text(final_sentence)
                    elif session.audio_buffer.size > 0:
                        try:
                            last_text = session.get_final_result()
                            if last_text and last_text.strip():
                                session.full_sentence = last_text.strip()
                                final_sentence = session.finalize_current_sentence()
                                if final_sentence:
                                    final_sentence = normalize_text(final_sentence)
                        except Exception:
                            pass

                    if not final_sentence:
                        fallback = session.full_sentence.strip() if session.full_sentence else ""
                        if not fallback and len(session.confirmed_sentences) > 0:
                            fallback = session.confirmed_sentences[-1].strip()
                        if fallback:
                            final_sentence = fallback

                    if final_sentence:
                        if session._is_duplicate_final(final_sentence):
                            ws_logger.info(
                                f"会话{session_id}: 跳过重复final(结束): '{final_sentence}'"
                            )
                        else:
                            segment_id = session._allocate_segment_id()
                            session._register_final(final_sentence)
                            final_results_sent += 1
                            response = {
                                "type": "final",
                                "text": final_sentence,
                                "index": len(session.confirmed_sentences) - 1,
                                "timestamp": int(time.time() * 1000),
                                "is_final": True,
                                "segment_id": segment_id,
                                "session_id": session_id,
                                "offsets": {"start_ms": None, "end_ms": None},
                            }
                            ws.send(json.dumps(response))
                            ws_logger.info(
                                f"会话{session_id}: 发送最终句子#{final_results_sent}: '{final_sentence}', segment_id={segment_id}"
                            )

                    try:
                        session.save_original_audio_files()
                    except Exception:
                        pass

                    response = {
                        "type": "session_end",
                        "message": "识别会话结束",
                        "total_sentences": len(session.confirmed_sentences),
                        "timestamp": int(time.time() * 1000),
                        "session_id": session_id,
                        "stats": {
                            "messages_received": message_count,
                            "audio_chunks_processed": audio_chunks_received,
                            "partial_results_sent": partial_results_sent,
                            "final_results_sent": final_results_sent,
                        },
                    }
                    ws.send(json.dumps(response))
                    ws_logger.info(
                        f"会话{session_id}: 结束统计 - 消息:{message_count}, 音频块:{audio_chunks_received}, 实时:{partial_results_sent}, 最终:{final_results_sent}"
                    )
                    break

                if msg_type == "reset":
                    ws_logger.info(f"会话{session_id}: 重置会话状态")
                    session.reset()
                    response = {
                        "type": "reset_confirm",
                        "message": "会话状态已重置",
                        "timestamp": int(time.time() * 1000),
                    }
                    ws.send(json.dumps(response))
                    ws_logger.debug(f"会话{session_id}: 发送reset_confirm消息")
                    continue

                if msg_type == "ping":
                    try:
                        pong = {
                            "type": "pong",
                            "ts": msg.get("ts", int(time.time() * 1000)),
                            "timestamp": int(time.time() * 1000),
                        }
                        ws.send(json.dumps(pong))
                    except Exception:
                        pass
                    continue

                if msg_type == "chunk":
                    if audio_data:
                        audio_chunks_received += 1
                        ws_logger.trace(f"会话{session_id}: 处理音频块#{audio_chunks_received}")

                        session.add_audio_chunk(audio_data, audio_format, sample_rate, seq_local)
                        try:
                            global_counters["total_chunks"] += 1
                            active_sessions[session_id]["chunks"] += 1
                            active_sessions[session_id]["last_active"] = int(time.time() * 1000)
                        except Exception:
                            pass

                        sentence_completed = session.check_sentence_complete()
                        if sentence_completed:
                            completed_sentence = session.finalize_current_sentence()
                            if completed_sentence and len(completed_sentence.strip()) >= 2:
                                completed_sentence = normalize_text(completed_sentence)
                                if session._is_duplicate_final(completed_sentence):
                                    ws_logger.info(
                                        f"会话{session_id}: 跳过重复final: '{completed_sentence}'"
                                    )
                                else:
                                    segment_id = session._allocate_segment_id()
                                    session._register_final(completed_sentence)
                                    final_results_sent += 1
                                    response = {
                                        "type": "final",
                                        "text": completed_sentence,
                                        "index": len(session.confirmed_sentences) - 1,
                                        "timestamp": int(time.time() * 1000),
                                        "is_final": True,
                                        "segment_id": segment_id,
                                        "session_id": session_id,
                                        "offsets": {"start_ms": None, "end_ms": None},
                                    }
                                    ws.send(json.dumps(response))
                                    ws_logger.info(
                                        f"会话{session_id}: 句子完成#{final_results_sent}: '{completed_sentence}', segment_id={segment_id}"
                                    )
                                    try:
                                        global_counters["total_finals"] += 1
                                        active_sessions[session_id]["finals"] += 1
                                        active_sessions[session_id]["last_final"] = completed_sentence
                                        key_logger.info(
                                            f"session={session_id} final id={segment_id}: '{completed_sentence}'"
                                        )
                                    except Exception:
                                        pass

                        partial_result = session.get_partial_result()
                        if partial_result:
                            partial_results_sent += 1
                            response = {
                                "type": "partial",
                                "text": partial_result["text"],
                                "confidence": partial_result.get("confidence", 0.0),
                                "words": partial_result.get("words", []),
                                "timestamp": int(time.time() * 1000),
                                "processing_time_ms": partial_result.get(
                                    "processing_time_ms", 0
                                ),
                                "is_final": False,
                                "session_id": session_id,
                                "text_state": partial_result.get("text_state"),
                            }
                            ws.send(json.dumps(response))
                            ws_logger.debug(
                                f"会话{session_id}: 发送实时结果#{partial_results_sent}: '{partial_result['text']}' (置信度: {partial_result.get('confidence', 0):.3f})"
                            )
                            try:
                                global_counters["total_partials"] += 1
                                active_sessions[session_id]["partials"] += 1
                                active_sessions[session_id]["last_partial"] = partial_result["text"]
                            except Exception:
                                pass
                    else:
                        ws_logger.warning(f"会话{session_id}: 收到chunk消息但无音频数据")

            except json.JSONDecodeError as exc:
                ws_logger.error(f"会话{session_id}: JSON解析失败: {exc}")
                error_response = {
                    "type": "error",
                    "message": f"消息格式错误: {exc}",
                    "timestamp": int(time.time() * 1000),
                }
                ws.send(json.dumps(error_response))

            except Exception as exc:
                error_info = traceback.format_exc()
                ws_logger.error(f"会话{session_id}: WebSocket错误详情:\n{error_info}")
                error_response = {
                    "type": "error",
                    "message": f"识别错误: {exc}",
                    "timestamp": int(time.time() * 1000),
                }
                try:
                    ws.send(json.dumps(error_response))
                except Exception:
                    ws_logger.error(f"会话{session_id}: 无法发送错误消息，连接可能已断开")
                break

        try:
            session.save_original_audio_files()
        except Exception:
            pass

        ws_logger.info(f"会话{session_id}: WebSocket连接关闭")
        key_logger.info(f"session={session_id} closed")
        try:
            global_counters["active_connections"] = max(
                0, global_counters["active_connections"] - 1
            )
            if session_id in active_sessions:
                del active_sessions[session_id]
        except Exception:
            pass
