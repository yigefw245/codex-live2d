"""桌宠本地记忆模块：短期记忆（对话流水）+ 长期记忆（事实库 + 语义检索）。

设计：
- 短期记忆：memory/short_term.jsonl，按时间保存最近若干条对话（可设条数与保留时长），
  重启后自动恢复，替代原先只存在内存里的 chat_history。
- 长期记忆：memory/long_term.json，每轮对话后用聊天模型提炼值得记住的事实，
  自动合并去重、按重要度/新鲜度保留上限；回复前用 Embedding 语义检索召回
  最相关的事实注入提示词（未配置 Embedding Key 时自动退化为本地关键词匹配）。

所有数据都保存在项目本地 memory/ 目录，不依赖外部数据库。
"""

import json
from collections import deque
import copy
import os
import re
import threading
import time
import urllib.request
import uuid
from datetime import datetime

MIN_EXTRACT_INTERVAL = 15  # 两次长期记忆提炼之间的最短秒数，避免高频对话时反复调用模型
EMBED_BATCH_SIZE = 10  # DashScope embeddings 单次请求的输入上限


def _now_ts():
    return time.time()


def _time_note():
    now = datetime.now()
    week = "一二三四五六日"
    return f"现在是 {now:%Y-%m-%d %H:%M}，星期{week[now.weekday()]}"


def _tokens(text):
    """把文本切成 CJK 二元组 + ASCII 词，用于本地相似度计算。"""
    text = str(text or "").lower()
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    grams = {"".join(cjk[i : i + 2]) for i in range(len(cjk) - 1)}
    grams.update(re.findall(r"[a-z0-9]+", text))
    return grams


def _jaccard(a, b):
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _cosine(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / (na * nb)


class _EmbeddingClient:
    """OpenAI 兼容的向量接口（默认 DashScope text-embedding-v3）。"""

    def __init__(self, cfg):
        cfg = cfg or {}
        self.base = str(cfg.get("base_url") or "").strip().rstrip("/")
        self.key = str(cfg.get("api_key") or "").strip()
        self.model = str(cfg.get("model") or "text-embedding-v3").strip()

    def ready(self):
        return bool(self.base and self.key and self.model)

    def embed(self, texts, timeout=30):
        body = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float",
        }
        request = urllib.request.Request(
            self.base + "/embeddings",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.key,
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        rows = sorted(data.get("data") or [], key=lambda x: x.get("index", 0))
        return [row.get("embedding") or [] for row in rows]


class PetMemory:
    """桌宠本地记忆：短期对话流水 + 长期事实库。"""

    def __init__(self, cfg, base_dir, diagnostics=None):
        self.cfg = dict(cfg or {})
        self.enabled = bool(self.cfg.get("enabled", True))
        self.memory_dir = os.path.join(base_dir, "memory")
        self.short_path = os.path.join(self.memory_dir, "short_term.jsonl")
        self.long_path = os.path.join(self.memory_dir, "long_term.json")
        self.summary_path = os.path.join(self.memory_dir, "summary.json")
        self.diagnostics = diagnostics
        self._lock = threading.RLock()
        self._persist_lock = threading.RLock()
        self._work = threading.Condition()
        self._pending = deque()
        self._closed = False
        self._generation = 0
        self._embed = _EmbeddingClient(self.cfg.get("embedding") or {})
        self._embed_ok = self._embed.ready()
        self._embedding_retry_at = 0.0
        self._last_extract_ts = 0.0
        self.short_term = self._load_short_term()
        self.long_term = self._load_long_term()
        try:
            with open(self.summary_path, encoding="utf-8") as stream:
                self.summary = str(json.load(stream).get("summary") or "")
        except (OSError, ValueError, AttributeError):
            self.summary = ""
        self._worker = threading.Thread(target=self._memory_worker, daemon=True,
                                        name="pet-memory")
        self._worker.start()

    # ---------- 通用参数 ----------

    def _max_short(self):
        try:
            return max(5, int(self.cfg.get("short_term_max_messages", 40)))
        except (TypeError, ValueError):
            return 40

    def _max_hours(self):
        try:
            return max(0.5, float(self.cfg.get("short_term_max_hours", 24)))
        except (TypeError, ValueError):
            return 24.0

    def _max_entries(self):
        try:
            return max(20, int(self.cfg.get("long_term_max_entries", 200)))
        except (TypeError, ValueError):
            return 200

    def _prune_short(self, items):
        cutoff = _now_ts() - self._max_hours() * 3600
        items = [it for it in items if it.get("ts", 0) >= cutoff]
        return items[-self._max_short() :]

    def _prune_long(self):
        limit = self._max_entries()
        if len(self.long_term) <= limit:
            return
        self.long_term.sort(
            key=lambda e: (int(e.get("importance", 1)), e.get("updated_at", 0)),
            reverse=True,
        )
        self.long_term = self.long_term[:limit]

    # ---------- 短期记忆 ----------

    def _load_short_term(self):
        items = []
        try:
            with open(self.short_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        items.append(json.loads(line))
                    except Exception:
                        continue
        except FileNotFoundError:
            pass
        except Exception:
            pass
        return self._prune_short(items)

    def _save_short_term(self):
        self._save_snapshot(self.short_path, "short_term", jsonl=True)

    def _save_snapshot(self, path, attribute, jsonl=False):
        try:
            with self._persist_lock:
                with self._lock:
                    data = copy.deepcopy(getattr(self, attribute))
                os.makedirs(self.memory_dir, exist_ok=True)
                tmp = path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as stream:
                    if jsonl:
                        for item in data:
                            stream.write(json.dumps(item, ensure_ascii=False) + "\n")
                    else:
                        if attribute == "summary":
                            data = {"summary": data}
                        json.dump(data, stream, ensure_ascii=False, indent=2)
                os.replace(tmp, path)
        except OSError as exc:
            if self.diagnostics:
                self.diagnostics.event("memory.persist_error", error=type(exc).__name__)

    def short_term_entries(self):
        with self._lock:
            return list(self.short_term)

    def short_term_messages(self, limit=None):
        """返回可注入聊天的最近消息（只含 user/assistant 角色）。"""
        with self._lock:
            items = list(self.short_term)
        messages = []
        for item in items:
            speaker = item.get("speaker") or item.get("role")
            if speaker not in ("user", "assistant"):
                continue
            content = str(item.get("content") or "").strip()
            if not content:
                continue
            messages.append({"role": speaker, "content": content})
        if limit:
            messages = messages[-int(limit) :]
        return messages

    def record_line(self, speaker, content, source="chat"):
        """记录单条消息（如主动发言/读屏的回复）。"""
        if not self.enabled:
            return
        item = {
            "ts": _now_ts(),
            "speaker": str(speaker),
            "content": str(content or "").strip(),
            "source": str(source),
        }
        with self._lock:
            self.short_term.append(item)
            self.short_term = self._prune_short(self.short_term)
        self._save_short_term()

    def record_turn(self, user_text, reply, source="chat", extract=False, chat_client=None):
        """记录一轮对话（用户 + 回复），可选做长期记忆提炼。"""
        if not self.enabled:
            return
        with self._lock:
            generation = self._generation
            self.short_term.append(
                {
                    "ts": _now_ts(),
                    "speaker": "user",
                    "content": str(user_text or "").strip(),
                    "source": str(source),
                }
            )
            self.short_term.append(
                {
                    "ts": _now_ts(),
                    "speaker": "assistant",
                    "content": str(reply or "").strip(),
                    "source": str(source),
                }
            )
            self.short_term = self._prune_short(self.short_term)
        self._save_short_term()
        if (
            extract
            and chat_client is not None
            and self.cfg.get("long_term_extract", True)
        ):
            with self._work:
                if not self._closed:
                    self._pending.append((chat_client, user_text, reply, source,
                                          generation))
                    self._work.notify()

    # ---------- 长期记忆 ----------

    def _load_long_term(self):
        try:
            with open(self.long_path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = data.get("entries") or []
            return [
                e
                for e in data
                if isinstance(e, dict) and str(e.get("content") or "").strip()
            ]
        except FileNotFoundError:
            return []
        except Exception:
            return []

    def _save_long_term(self):
        self._save_snapshot(self.long_path, "long_term")

    def long_term_entries(self):
        with self._lock:
            return copy.deepcopy(self.long_term)

    def _similarity(self, a, b):
        """两条事实的相似度：优先用向量，其次本地 n-gram。"""
        emb_a = a.get("embedding") if isinstance(a, dict) else None
        emb_b = b.get("embedding") if isinstance(b, dict) else None
        score = _cosine(emb_a or [], emb_b or [])
        if score > 0:
            return score
        text_a = a if isinstance(a, str) else a.get("content", "")
        text_b = b if isinstance(b, str) else b.get("content", "")
        return _jaccard(text_a, text_b)

    def _merge_fact(self, content, importance, source="chat"):
        """只合并完全重复的事实，保留偏好变化和各自的观测时间。"""
        content = str(content or "").strip().replace("\n", " ")[:200]
        if not content:
            return
        now = _now_ts()
        best = None
        for entry in self.long_term:
            # Similar wording can express opposite preferences. Only exact
            # duplicates are merged; dated observations retain their origin.
            if entry.get("content", "").strip() == content:
                best = entry
                break
        if best is not None:
            best["importance"] = max(int(best.get("importance", 3)), int(importance))
            best["updated_at"] = now
            return
        self.long_term.append(
            {
                "id": "m" + uuid.uuid4().hex[:16],
                "content": content,
                "importance": max(1, min(5, int(importance))),
                "created_at": now,
                "updated_at": now,
                "hit_count": 0,
                "embedding": None,
                "source": source,
            }
        )

    def _embed_entries(self, entries):
        """批量补齐长期记忆的向量（只处理缺失项，失败后自动降级为关键词匹配）。"""
        if not self._embed_ok or time.monotonic() < self._embedding_retry_at:
            return
        pending = [e for e in entries if not e.get("embedding")]
        for i in range(0, len(pending), EMBED_BATCH_SIZE):
            batch = pending[i : i + EMBED_BATCH_SIZE]
            try:
                vectors = self._embed.embed([e["content"] for e in batch], timeout=30)
            except Exception:
                self._embedding_retry_at = time.monotonic() + 60
                return
            for entry, vector in zip(batch, vectors):
                if vector:
                    entry["embedding"] = [round(x, 6) for x in vector]

    def _memory_worker(self):
        while True:
            with self._work:
                self._work.wait_for(lambda: self._closed or self._pending)
                if self._closed:
                    return
                delay = max(0, self._last_extract_ts + MIN_EXTRACT_INTERVAL - _now_ts())
                if delay:
                    self._work.wait(timeout=delay)
                    continue
                client = self._pending[0][0]
                batch = []
                while self._pending and self._pending[0][0] is client and len(batch) < 10:
                    batch.append(self._pending.popleft())
                self._last_extract_ts = _now_ts()
            if not self.enabled:
                continue
            transcript = "\n".join(f"使用者：{item[1]}\n你：{item[2]}" for item in batch)
            try:
                self._extract(client, transcript, "", source=",".join(sorted({item[3] for item in batch})),
                              generation=batch[-1][4])
            except Exception as exc:
                if self.diagnostics:
                    self.diagnostics.event("memory.extract_error", error=type(exc).__name__)

    def _extract(self, chat_client, user_text, reply, source="chat", generation=None):
        """用聊天模型从一轮对话里提炼长期记忆；失败时静默跳过。"""
        with self._lock:
            previous_summary = self.summary
        if generation is None:
            generation = self._generation
        prompt = (
            "你是记忆提取器。根据下面这轮对话，提取值得长期记住的事实，"
            "比如使用者的姓名、身份、喜好、习惯、重要经历、约定、当前关心的事等。\n"
            f"使用者说：{user_text}\n"
            f"你说：{reply}\n"
            f"此前的对话摘要：{previous_summary}\n"
            '只输出 JSON 对象：{"facts": [{"content": "事实，一句话，用第三人称概括", '
            '"importance": 1到5的数字}], "summary": "更新后的对话摘要，最多600字"}。'
            "摘要保留正在讨论的话题、未完成的约定和任务，合并此前摘要与新对话。"
            "facts 只记使用者明确表达或已经确认的事实，不把你的猜测当成事实。"
            "偏好变化时保留变化的含义；没有值得记住的事实时 facts 为 []。"
            "不要输出其它任何文字。"
        )
        try:
            started = time.monotonic()
            raw = chat_client.raw_complete(
                [{"role": "system", "content": prompt}], max_tokens=1000, timeout=25)
        except Exception:
            return
        if self.diagnostics:
            self.diagnostics.event("memory.extracted",
                                   duration_ms=round((time.monotonic() - started) * 1000))
        summary = None
        try:
            obj = json.loads(str(raw).strip().removeprefix("```json").removesuffix("```").strip())
            if isinstance(obj, dict):
                summary = obj.get("summary")
                raw = json.dumps(obj.get("facts") or [], ensure_ascii=False)
        except (ValueError, TypeError):
            pass
        facts = self._parse_facts(raw)
        with self._lock:
            if generation != self._generation or self._closed or not self.enabled:
                return
            for content, importance in facts:
                self._merge_fact(content, importance, source)
            if isinstance(summary, str) and summary.strip():
                self.summary = summary.strip()[:1200]
            self._prune_long()
            pending = copy.deepcopy(self.long_term)
        self._save_long_term()
        self._save_snapshot(self.summary_path, "summary")
        self._embed_entries(pending)
        with self._lock:
            if generation != self._generation or self._closed or not self.enabled:
                return
            vectors = {entry["id"]: entry for entry in pending if entry.get("embedding")}
            for entry in self.long_term:
                candidate = vectors.get(entry["id"])
                if candidate and entry["content"] == candidate["content"]:
                    entry["embedding"] = candidate["embedding"]
        self._save_long_term()
        self._save_snapshot(self.summary_path, "summary")

    @staticmethod
    def _parse_facts(raw):
        text = str(raw or "").strip()
        start = text.find("[")
        end = text.rfind("]")
        if start < 0 or end <= start:
            return []
        try:
            data = json.loads(text[start : end + 1])
        except Exception:
            return []
        facts = []
        for item in data if isinstance(data, list) else []:
            if not isinstance(item, dict):
                continue
            content = str(item.get("content") or "").strip()
            if not content:
                continue
            try:
                importance = int(item.get("importance", 3))
            except (TypeError, ValueError):
                importance = 3
            facts.append((content, importance))
        return facts

    # ---------- 检索 ----------

    def _base_score(self, entry, sim):
        return (
            0.55 * sim
            + 0.2 * (int(entry.get("importance", 3)) / 5.0)
            + 0.1 * min(1.0, int(entry.get("hit_count", 0)) / 8.0)
            + 0.15 * max(0.0, 1.0 - (self._age_days(entry) / 14.0))
        )

    @staticmethod
    def _age_days(entry):
        try:
            return max(0.0, (_now_ts() - float(entry.get("updated_at", 0))) / 86400.0)
        except (TypeError, ValueError):
            return 0.0

    def _scored_memories(self, text):
        """计算每条长期记忆与当前话题的 (相似度, 综合分)；embedding 失败时自动降级关键词。"""
        with self._lock:
            entries = copy.deepcopy(self.long_term)
        use_emb = (bool(self.cfg.get("use_embedding", True)) and self._embed_ok
                   and time.monotonic() >= self._embedding_retry_at
                   and all(entry.get("embedding") for entry in entries))
        vector = None
        if use_emb:
            try:
                (vector,) = self._embed.embed([text], timeout=2)
            except Exception:
                self._embedding_retry_at = time.monotonic() + 60
                use_emb = False
        results = []
        for entry in entries:
            if use_emb and entry.get("embedding"):
                sim = _cosine(vector, entry.get("embedding") or [])
            else:
                sim = _jaccard(text, entry.get("content", ""))
            results.append((entry, sim, self._base_score(entry, sim)))
        return results, use_emb

    def recall(self, text, top_k=None):
        """按相关度召回长期记忆；没有相关记忆时返回 None（纯人设回答）。"""
        if not self.enabled or not self.long_term:
            return None
        if top_k is None:
            try:
                top_k = max(1, int(self.cfg.get("recall_top_k", 5)))
            except (TypeError, ValueError):
                top_k = 5
        scored, use_emb = self._scored_memories(text)
        # 相关度过滤：语义检索要求余弦相似度达标，关键词检索要求至少有一个词/字重叠
        min_sim = 0.35 if use_emb else 0.0
        top = sorted(
            (item for item in scored if item[1] > min_sim),
            key=lambda item: item[2],
            reverse=True,
        )[:top_k]
        if not top:
            return None
        now = _now_ts()
        lines = []
        with self._lock:
            live = {entry["id"]: entry for entry in self.long_term}
            for entry, _sim, _score in top:
                current = live.get(entry["id"])
                if current is None:
                    continue
                current["hit_count"] = int(current.get("hit_count", 0)) + 1
                current["last_recalled_at"] = now
                stamp = datetime.fromtimestamp(entry.get("updated_at", now)).strftime("%Y-%m-%d")
                lines.append(f"- [{stamp}] {entry.get('content', '')}")
        self._save_long_term()
        return (
            _time_note()
            + "\n【长期记忆】你记得这些事：\n"
            + "\n".join(lines)
            + "\n（请始终以人物设定为准、保持角色语气；记忆只是背景，"
            "如与人设冲突以人设为准，不要逐条复述，也不要说'根据我的记忆'。）"
        )

    def dialogue_context(self, text, history_limit=None, top_k=None):
        """所有对话共用的上下文：短期记忆为主，长期记忆按相关度补充；都没有则按人设回答。

        返回 (history, memory_note)：history 为短期记忆消息列表，
        memory_note 为相关长期记忆提示词（无相关记忆时为 None）。
        history_limit 用于限制短期记忆条数（主动发言/读屏这类轻量场景）。
        """
        if not self.enabled:
            return [], None
        history = self.short_term_messages(limit=history_limit)
        memory_note = self.recall(text, top_k=top_k)
        with self._lock:
            summary = self.summary
        if summary:
            memory_note = (memory_note or _time_note()) + "\n【此前对话摘要】\n" + summary
        if not history and memory_note is None:
            return [], None
        return history, memory_note

    # ---------- 管理 ----------

    def clear(self):
        """清空全部短期与长期记忆（文件同步重置）。"""
        with self._work:
            with self._lock:
                self._generation += 1
                self.short_term = []
                self.long_term = []
                self.summary = ""
            self._pending.clear()
        self._save_short_term()
        self._save_long_term()
        self._save_snapshot(self.summary_path, "summary")

    def close(self):
        with self._work:
            self._closed = True
            self._pending.clear()
            self._work.notify_all()
        self._worker.join(timeout=1)
