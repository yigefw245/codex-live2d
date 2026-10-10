"""Ordered dialogue delivery, cooperative interruption, and local diagnostics."""

from collections import deque
from concurrent.futures import Future
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
import heapq
import json
import os
import threading
import time
import uuid


_current = threading.local()


class TurnCancelled(Exception):
    pass


def checkpoint():
    task = getattr(_current, 'task', None)
    if task is not None and task.cancelled.is_set():
        raise TurnCancelled('Dialogue interrupted')


def current_turn_id():
    task = getattr(_current, 'task', None)
    return task.id if task is not None else None


def cancellable_io(callback):
    """Release dialogue delivery on cancellation, even during a stalled read.

    urllib cannot cancel DNS/header waits. Its bounded I/O finishes in a daemon
    worker; the inherited turn prevents late callbacks from producing output.
    """
    task = getattr(_current, 'task', None)
    if task is None:
        return callback()
    checkpoint()
    result = Future()

    def run():
        _current.task = task
        try:
            checkpoint()
            result.set_result(callback())
        except Exception as exc:
            result.set_exception(exc)
        finally:
            _current.task = None

    threading.Thread(target=run, name='pet-model-io', daemon=True).start()
    while True:
        checkpoint()
        try:
            return result.result(timeout=0.1)
        except TimeoutError:
            if result.done():
                return result.result()


def mark(name, **fields):
    task = getattr(_current, 'task', None)
    if task is not None:
        task.diagnostics.event(name, task.id, **fields)


@contextmanager
def stage(name):
    task = getattr(_current, 'task', None)
    if task is None:
        yield
    else:
        with task.diagnostics.span(name, task.id):
            yield


class Diagnostics:
    def __init__(self, path):
        self.path = path
        self.run = uuid.uuid4().hex[:12]
        self._lock = threading.Lock()

    def event(self, name, turn=None, **fields):
        record = dict(ts=datetime.now().astimezone().isoformat(), run=self.run,
                      event=name, turn=turn, **fields)
        try:
            with self._lock:
                if os.path.isfile(self.path) and os.path.getsize(self.path) > 2097152:
                    os.replace(self.path, self.path + '.1')
                with open(self.path, 'a', encoding='utf-8') as stream:
                    stream.write(json.dumps(record, ensure_ascii=False) + '\n')
        except OSError:
            pass

    @contextmanager
    def span(self, name, turn=None):
        started = time.monotonic()
        self.event(name + '.start', turn)
        outcome = 'ok'
        try:
            yield
        except TurnCancelled:
            outcome = 'cancelled'
            raise
        except Exception as exc:
            outcome = type(exc).__name__
            raise
        finally:
            self.event(name + '.end', turn, outcome=outcome,
                       duration_ms=round((time.monotonic() - started) * 1000))


@dataclass
class _Task:
    source: str
    callback: object
    diagnostics: Diagnostics
    priority: int
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    future: Future = field(default_factory=Future)
    cancelled: threading.Event = field(default_factory=threading.Event)
    queued_at: float = field(default_factory=time.monotonic)


class DialogueRuntime:
    """One dialogue consumer; user input outranks pending ambient reactions."""

    def __init__(self, diagnostics, on_interrupt=None, on_state=None):
        self.diagnostics = diagnostics
        self.on_interrupt = on_interrupt
        self.on_state = on_state
        self._condition = threading.Condition()
        self._pending = []
        self._sequence = 0
        self._active = None
        self._closed = False
        self.last_user_at = 0.0
        self._events = deque(maxlen=12)
        self._worker = threading.Thread(target=self._run, daemon=True,
                                        name='pet-dialogue')
        self._worker.start()

    @property
    def busy(self):
        with self._condition:
            return self._active is not None or bool(self._pending)

    def submit(self, source, callback, priority=0, turn_id=None):
        task = _Task(source, callback, self.diagnostics, priority)
        if turn_id:
            task.id = turn_id
        cancelled = []
        stop_output = False
        with self._condition:
            if self._closed:
                task.future.set_exception(TurnCancelled('Runtime closed'))
                return task.future
            if priority == 0:
                self.last_user_at = time.monotonic()
                for _, _, pending in self._pending:
                    if pending.priority > 0:
                        pending.cancelled.set()
                        cancelled.append(pending)
                self._pending = [entry for entry in self._pending
                                 if not entry[2].cancelled.is_set()]
                heapq.heapify(self._pending)
                if self._active is not None and self._active.priority > 0:
                    self._active.cancelled.set()
                    stop_output = True
                if stop_output and self.on_interrupt:
                    self.on_interrupt()
            self._sequence += 1
            heapq.heappush(self._pending, (priority, self._sequence, task))
            self.diagnostics.event('dialogue.queued', task.id, source=source)
            if self.on_state:
                self.on_state(True)
            self._condition.notify()
        for pending in cancelled:
            if not pending.future.done():
                pending.future.set_exception(TurnCancelled('Superseded by user input'))
        return task.future

    def interrupt(self):
        with self._condition:
            tasks = [entry[2] for entry in self._pending]
            self._pending.clear()
            active = self._active
            if active is not None:
                active.cancelled.set()
            if self.on_interrupt:
                self.on_interrupt()
            if self.on_state:
                self.on_state(active is not None)
            if self.on_state:
                self.on_state(active is not None)
        for task in tasks:
            task.cancelled.set()
            if not task.future.done():
                task.future.set_exception(TurnCancelled('Interrupted before delivery'))
        self.diagnostics.event('dialogue.interrupt', active.id if active else None)

    def note(self, kind, text):
        with self._condition:
            self._events.append((time.monotonic(), kind, str(text)[:350]))

    def recent_events(self):
        cutoff = time.monotonic() - 600
        with self._condition:
            return '\n'.join(f'- {kind}: {text}' for ts, kind, text in self._events
                             if ts >= cutoff)

    def _run(self):
        while True:
            with self._condition:
                self._condition.wait_for(lambda: self._closed or self._pending)
                if self._closed:
                    return
                _, _, task = heapq.heappop(self._pending)
                self._active = task
            _current.task = task
            try:
                self.diagnostics.event('dialogue.started', task.id, source=task.source,
                                      queue_ms=round((time.monotonic() - task.queued_at) * 1000))
                with self.diagnostics.span('dialogue', task.id):
                    if not task.future.set_running_or_notify_cancel():
                        continue
                    checkpoint()
                    result = task.callback()
                    checkpoint()
                task.future.set_result(result)
            except Exception as exc:
                task.future.set_exception(exc)
            finally:
                _current.task = None
                with self._condition:
                    self._active = None
                    if self.on_state:
                        self.on_state(bool(self._pending))

    def close(self):
        with self._condition:
            self._closed = True
            self._condition.notify_all()
        self.interrupt()
        if threading.current_thread() is not self._worker:
            self._worker.join(timeout=1)


def estimate_tokens(text):
    # Conservative estimate for mixed Chinese / ASCII; no model download needed.
    text = str(text)
    return sum(1 if ord(char) > 127 else 0.35 for char in text) + 8


def dialogue_messages(persona, history, text, memory_note=None, budget=6000):
    messages = [{'role': 'system', 'content': persona}]
    if memory_note:
        messages.append({'role': 'system', 'content': memory_note})
    user = {'role': 'user', 'content': text}
    available = budget - sum(estimate_tokens(item['content'])
                             for item in messages + [user])
    if available < 0:
        raise ValueError('Input and persona exceed the context budget')
    retained = []
    for item in reversed(history):
        cost = estimate_tokens(item['content'])
        if cost > available:
            break
        retained.insert(0, dict(item))
        available -= cost
    while retained and retained[0]['role'] == 'assistant':
        retained.pop(0)
    return messages + retained + [user]
