"""Soullink Emotion SDK 本地侧服务管理器。

负责启动 / 停止 Node 侧服务（tools/soullink/server.mjs），该服务运行 SDK 的
Embedding 情绪分类器和 DashScope TTS。API Key 只保存在本地 config，不会
出现在浏览器端。
"""

import json
import os
import shutil
import socket
import subprocess
import threading
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOULLINK_DIR = os.path.join(BASE_DIR, "tools", "soullink")
RUN_DIR = os.path.join(SOULLINK_DIR, "run")
CONFIG_PATH = os.path.join(RUN_DIR, "soullink-config.json")
LOG_PATH = os.path.join(RUN_DIR, "soullink.log")


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class SoullinkRunner:
    def __init__(self):
        self.proc = None
        self.port = None
        self.ready = False
        self._log_file = None
        self._lock = threading.Lock()
        self._log_cursor = 0

    def node_path(self):
        return shutil.which("node")

    def start(self, cfg):
        """启动侧服务。cfg 为读屏幕/聊天之外的 soullink 配置（embedding/tts）。"""
        with self._lock:
            if self.proc is not None and self.proc.poll() is None:
                return True
            node = self.node_path()
            if not node:
                raise RuntimeError("未找到 Node.js，Soullink 功能需要 Node 18+")
            os.makedirs(RUN_DIR, exist_ok=True)
            self.port = _free_port()
            payload = {
                "embedding": cfg.get("embedding") or {},
                "tts": cfg.get("tts") or {},
                "cache_dir": os.path.join(SOULLINK_DIR, "cache", "embeddings"),
            }
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            self._log_file = open(LOG_PATH, "a", encoding="utf-8", errors="replace")
            self.proc = subprocess.Popen(
                [
                    node,
                    os.path.join(SOULLINK_DIR, "server.mjs"),
                    "--port",
                    str(self.port),
                    "--config",
                    CONFIG_PATH,
                ],
                cwd=SOULLINK_DIR,
                stdout=self._log_file,
                stderr=self._log_file,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            self.ready = False
            self._log_cursor = os.path.getsize(LOG_PATH) if os.path.exists(LOG_PATH) else 0
        return self._wait_ready(timeout=20)

    def _wait_ready(self, timeout=20):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.proc is None or self.proc.poll() is not None:
                raise RuntimeError("Soullink 侧服务启动失败，请查看日志")
            if self._health_ok():
                self.ready = True
                return True
            time.sleep(0.2)
        raise RuntimeError("Soullink 侧服务启动超时")

    def _health_ok(self):
        if not self.port:
            return False
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}/health", timeout=2
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    def wait_classifier_ready(self, on_ready=None, timeout=600):
        """等待 Embedding 语料初始化完成（首次约 1 分钟），回调在后台线程执行。"""
        def _wait():
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if not self.ready or self.proc is None or self.proc.poll() is not None:
                    return
                try:
                    with urllib.request.urlopen(
                        f"http://127.0.0.1:{self.port}/health", timeout=3
                    ) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    if data.get("classifierInitialized"):
                        if on_ready:
                            on_ready()
                        return
                except Exception:
                    pass
                time.sleep(2)

        threading.Thread(target=_wait, daemon=True).start()

    def classify(self, message, timeout=180):
        if not self.ready or not self.port:
            raise RuntimeError("Soullink 侧服务未就绪")
        body = json.dumps({"message": message}, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/classify",
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("intent") or {}

    def generate_profile(self, model_id, force=False):
        """为模型生成 soullink.profile.json（已存在且非 force 时跳过）。

        返回 (ok, message)。
        """
        node = self.node_path()
        if not node:
            return False, "未找到 Node.js"
        profile_path = os.path.join(
            BASE_DIR, "model", model_id, "soullink.profile.json"
        )
        if os.path.isfile(profile_path) and not force:
            return True, "profile 已存在"
        cmd = [
            node,
            os.path.join(SOULLINK_DIR, "generate-profile.mjs"),
            "--root",
            os.path.join(BASE_DIR, "model"),
            "--model",
            str(model_id),
        ]
        if force:
            cmd.append("--force")
        try:
            result = subprocess.run(
                cmd,
                cwd=SOULLINK_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception as exc:
            return False, str(exc)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "生成失败").strip()
            return False, detail[:200]
        return True, "profile 已生成"

    def stop(self):
        with self._lock:
            proc, self.proc = self.proc, None
            self.port = None
            self.ready = False
            log_file, self._log_file = self._log_file, None
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        if log_file is not None:
            try:
                log_file.close()
            except Exception:
                pass
