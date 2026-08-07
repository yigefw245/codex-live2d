import datetime
import glob
import json
import os
import sqlite3
import time

LOGS_DB = os.path.join(os.path.expanduser("~"), ".codex", "logs_2.sqlite")
FAULT_WINDOW = 15
THINKING_GAP = 5
IDLE_GAP = 25


def _tail(path, size=262144):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        length = f.tell()
        start = max(0, length - size)
        f.seek(start)
        data = f.read().decode("utf-8", errors="replace")
    if start > 0:
        newline = data.find("\n")
        if newline != -1:
            data = data[newline + 1 :]
    return data


def _read_recent_logs(after_ts, limit=2500):
    try:
        conn = sqlite3.connect(
            f"file:{LOGS_DB}?mode=ro", uri=True, timeout=2
        )
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT ts, thread_id, target, feedback_log_body "
            "FROM logs WHERE ts >= ? ORDER BY id DESC LIMIT ?",
            (after_ts, limit),
        ).fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def _message_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") in ("input_text", "output_text", "text"):
                text = item.get("text", "")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return ""


def _clean(text, limit=80):
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[: max(0, limit - 1)] + "…"
    return text


def _user_text(payload):
    if payload.get("type") == "user_message":
        text = payload.get("message")
        if isinstance(text, str):
            return text
    content = payload.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return _message_text(content)
    return ""


def get_codex_status():
    root = os.path.join(os.path.expanduser("~"), ".codex", "sessions")
    files = glob.glob(os.path.join(root, "**", "rollout-*.jsonl"), recursive=True)
    if not files:
        return {
            "active": False,
            "task": None,
            "model": None,
            "progress": None,
            "elapsed": None,
            "tokens": None,
            "last_finished": None,
        }
    path = max(files, key=os.path.getmtime)
    task = None
    model = None
    progress = None
    started_at = None
    total_tokens = None
    last_finished = None
    try:
        for line in _tail(path).splitlines():
            obj = json.loads(line)
            payload = obj.get("payload", {})
            ptype = payload.get("type")
            if ptype == "task_started":
                started = payload.get("started_at")
                if isinstance(started, (int, float)):
                    started_at = float(started)
            elif ptype == "token_count":
                info = payload.get("info") or {}
                usage = info.get("total_token_usage") or {}
                tokens = usage.get("total_tokens")
                if isinstance(tokens, (int, float)):
                    total_tokens = int(tokens)
            elif ptype == "task_complete":
                completed = payload.get("completed_at")
                if isinstance(completed, (int, float)):
                    last_finished = float(completed)
            if ptype in ("user_message", "message") and payload.get("role") in (
                None,
                "user",
            ):
                text = _user_text(payload)
                if (
                    text
                    and "<environment_context>" not in text
                    and "permissions instructions" not in text
                ):
                    marker = "My request for Codex:"
                    if marker in text:
                        text = text.split(marker, 1)[1]
                    task = _clean(text)
            if ptype == "agent_message" and payload.get("phase") == "commentary":
                message = payload.get("message")
                if isinstance(message, str) and message.strip():
                    progress = _clean(message)
            elif ptype == "task_complete":
                message = payload.get("last_agent_message")
                if isinstance(message, str) and message.strip():
                    progress = _clean(message)
            thread_settings = payload.get("thread_settings")
            if isinstance(thread_settings, dict) and thread_settings.get("model"):
                model = str(thread_settings["model"])
            elif payload.get("model"):
                model = str(payload["model"])
    except Exception:
        pass

    now = time.time()
    rows = _read_recent_logs(now - 120)
    sse_ts = None
    fault_ts = None
    thinking_ts = None
    working_ts = None
    thread_ts = {}
    for ts, tid, target, body in rows:
        if target == "codex_api::sse::responses" and body.startswith("SSE event: "):
            sse_ts = max(sse_ts or 0, ts)
            try:
                event = json.loads(body[len("SSE event: ") :])
                etype = event.get("type", "")
                resp = event.get("response") or {}
                if (
                    "fail" in etype.lower()
                    or "error" in etype.lower()
                    or resp.get("status") == "failed"
                    or resp.get("error")
                ):
                    fault_ts = max(fault_ts or 0, ts)
                item = event.get("item") or {}
                itype = item.get("type", "")
                if etype in (
                    "response.reasoning_text.delta",
                    "response.reasoning_text.done",
                    "response.content_part.delta",
                    "response.content_part.done",
                ) or (etype == "response.output_item.done" and itype in ("reasoning", "message")):
                    thinking_ts = max(thinking_ts or 0, ts)
                elif (
                    "function_call" in etype
                    or "tool" in etype.lower()
                    or (etype == "response.output_item.done" and itype == "function_call")
                ):
                    working_ts = max(working_ts or 0, ts)
            except Exception:
                pass
        if tid:
            thread_ts[tid] = max(thread_ts.get(tid, 0), ts)

    active_thread = max(thread_ts, key=thread_ts.get) if thread_ts else None
    last_activity = max(sse_ts or 0, thread_ts.get(active_thread, 0))

    if fault_ts and (now - fault_ts) < FAULT_WINDOW:
        state = "fault"
    elif (now - last_activity) > IDLE_GAP:
        state = "idle"
    elif (now - last_activity) > THINKING_GAP:
        state = "completed"
    elif working_ts and working_ts >= (thinking_ts or 0):
        state = "working"
    else:
        state = "thinking"

    return {
        "state": state,
        "active": state != "idle",
        "task": task,
        "model": model,
        "progress": progress,
        "elapsed": (
            int(time.time() - started_at)
            if state == "thinking" and started_at is not None
            else None
        ),
        "tokens": total_tokens,
        "last_finished": (
            datetime.datetime.fromtimestamp(last_finished).strftime("%H:%M")
            if last_finished is not None
            else None
        ),
    }
