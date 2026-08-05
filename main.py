import atexit
import ctypes
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from PySide6.QtCore import QObject, QTimer, QUrl, Qt, Signal, Slot
from PySide6.QtGui import QAction, QColor, QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMenu,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

import codex_monitor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG = os.path.join(BASE_DIR, "pet_error.log")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
PID_FILE = os.path.join(BASE_DIR, "pet.pid")
SHUTDOWN_FLAG = os.path.join(BASE_DIR, "pet_shutdown.flag")
DISABLED_FLAG = os.path.join(BASE_DIR, "pet_disabled.flag")
LIVE_URL_PATH = "/tools/web/live.html"

STATUS_H = 0
CHAT_H = 50
PAD = 12
MIN_SCALE = 0.3
MAX_SCALE = 2.0

DEFAULT_SETTINGS = {
    "scale": 1.0,
    "pos_x": None,
    "pos_y": None,
    "locked": True,
}


def load_pet_size():
    """Base pixel size of the character, from the rendered manifest."""
    try:
        with open(
            os.path.join(BASE_DIR, "pets", "yumi", "manifest.json"),
            encoding="utf-8",
        ) as f:
            manifest = json.load(f)
        bx, by, bx2, by2 = manifest["states"]["idle"]["bbox"]
        return bx2 - bx + 1, by2 - by + 1
    except Exception:
        return 462, 858


BASE_W, BASE_H = load_pet_size()


def load_settings():
    data = dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data.update(json.load(f))
    except Exception:
        pass
    return data


def save_settings(data):
    tmp = SETTINGS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, SETTINGS_PATH)


def remove_pid_file():
    try:
        os.remove(PID_FILE)
    except OSError:
        pass


def remove_disabled_flag():
    try:
        os.remove(DISABLED_FLAG)
    except OSError:
        pass


def make_handler(base):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=base, **kwargs)

        def log_message(self, *args):
            pass

    return Handler


CHAT_DEFAULTS = {
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "",
    "model": "deepseek-v4-flash",
    "persona": (
        "你是 yumi，一只可爱的桌面宠物女孩。银白色长发、蓝色大眼睛、头顶黑色蝴蝶结，"
        "性格温柔、元气，偶尔会害羞或撒娇，还有点爱哭。你会关心地陪使用者聊天，"
        "语气亲切口语化。回答请简短自然（通常一两句话），像微信聊天一样，"
        "不要使用 Markdown 或列表，不要提及你是 AI 或模型。"
    ),
}


def _read_env_file(path):
    data = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    data[key.strip()] = value.strip()
    except OSError:
        pass
    return data


def load_chat_config():
    cfg = dict(CHAT_DEFAULTS)
    try:
        with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
            cfg.update((json.load(f).get("chat") or {}))
    except Exception:
        pass
    if not cfg.get("api_key") and os.environ.get("DEEPSEEK_API_KEY"):
        cfg["api_key"] = os.environ["DEEPSEEK_API_KEY"]
    if not cfg.get("api_key"):
        env_path = os.path.join(
            os.path.expanduser("~"),
            ".codex",
            "skills",
            "claude-vision-skill",
            ".env",
        )
        cfg["api_key"] = _read_env_file(env_path).get("DASHSCOPE_API_KEY", "")
    return cfg


EMOTION_KEYWORDS = {
    "happy": [
        "哈哈", "开心", "高兴", "太好了", "真棒", "爱你", "耶", "可爱",
        "嘻嘻哈哈", "😄", "😁", "😊", "🥰", "😍", "🎉",
    ],
    "sad": [
        "难过", "伤心", "哭", "泪", "呜呜", "唉", "委屈", "想哭",
        "不开心", "遗憾", "😢", "😭",
    ],
    "angry": [
        "生气", "讨厌", "气死", "烦", "怒", "可恶", "哼", "😠", "😡",
    ],
    "thinking": [
        "也许", "可能", "考虑", "思考", "应该", "疑惑", "好奇", "为什么",
        "嗯…", "嗯，", "🤔", "😅",
    ],
    "surprised": [
        "天哪", "竟然", "没想到", "惊讶", "吓一跳", "😮", "😲",
    ],
}


def classify_emotion(text):
    text = str(text or "")
    scores = {}
    for emotion, words in EMOTION_KEYWORDS.items():
        scores[emotion] = sum(text.count(word) for word in words)
    best = max(scores, key=scores.get)
    best_score = scores[best]
    if best_score <= 0:
        return "neutral"
    tied = [e for e, s in scores.items() if s == best_score]
    if len(tied) > 1:
        return "neutral"
    return best


class ChatClient:
    def __init__(self, cfg):
        self.base = str(cfg.get("base_url", CHAT_DEFAULTS["base_url"])).rstrip("/")
        self.key = str(cfg.get("api_key", ""))
        self.model = str(cfg.get("model", CHAT_DEFAULTS["model"]))
        self.persona = str(cfg.get("persona", CHAT_DEFAULTS["persona"]))

    def ready(self):
        return bool(self.key and self.base)

    def chat(self, history, text, timeout=60):
        messages = [{"role": "system", "content": self.persona}]
        messages.extend(history[-20:])
        messages.append({"role": "user", "content": text})
        body = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 300,
        }
        request = urllib.request.Request(
            self.base + "/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.key,
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return str(data["choices"][0]["message"]["content"]).strip()


class ChatSettingsDialog(QDialog):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("聊天设置")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.base_url_edit = QLineEdit(str(cfg.get("base_url", "")))
        self.api_key_edit = QLineEdit(str(cfg.get("api_key", "")))
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.model_edit = QLineEdit(str(cfg.get("model", "")))
        self.persona_edit = QPlainTextEdit(str(cfg.get("persona", "")))
        self.persona_edit.setFixedHeight(120)

        form.addRow("API 地址", self.base_url_edit)
        form.addRow("API Key", self.api_key_edit)
        form.addRow("模型", self.model_edit)
        form.addRow("人物设定", self.persona_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return {
            "base_url": self.base_url_edit.text().strip().rstrip("/"),
            "api_key": self.api_key_edit.text().strip(),
            "model": self.model_edit.text().strip(),
            "persona": self.persona_edit.toPlainText().strip(),
        }


class PetBridge(QObject):
    """JS -> Python calls (menu, drag, chat)."""

    def __init__(self, window):
        super().__init__()
        self.window = window

    @Slot()
    def drag_start(self):
        self.window.begin_drag()

    @Slot(float, float)
    def context_menu(self, x, y):
        self.window.show_menu()

    @Slot(float, float)
    def set_head(self, fx, fy):
        self.window.head_frac_x = fx
        self.window.head_frac_y = fy

    @Slot(float, float)
    def set_bounds(self, w, h):
        self.window.base_bw = max(100, float(w))
        self.window.base_bh = max(100, float(h))
        self.window.apply_geometry()
        self.window._run_js(f"window.setScale({self.window.scale})")

    @Slot(str)
    def send_chat(self, text):
        self.window.handle_chat(text)

    @Slot()
    def back_to_codex(self):
        self.window.set_chat_mode(False)

    @Slot(str)
    def set_diag(self, text):
        try:
            with open(
                os.path.join(BASE_DIR, "pet_diag.log"),
                "a",
                encoding="utf-8",
            ) as f:
                f.write(f"{time.ctime()} {text}\n")
        except OSError:
            pass

    @Slot(str)
    def set_state_ack(self, name):
        try:
            with open(
                os.path.join(BASE_DIR, "pet_state_ack.log"),
                "a",
                encoding="utf-8",
            ) as f:
                f.write(f"{time.ctime()} {name}\n")
        except OSError:
            pass


class PetWindow(QWidget):
    EXPRESSIONS = [
        ("爱心眼", "heart"),
        ("星星眼", "star"),
        ("眼泪", "tear"),
        ("泪汪汪", "teary"),
        ("歪嘴", "wry"),
        ("猫猫嘴", "catmouth"),
        ("眼罩", "eyepatch"),
        ("黑脸", "black"),
        ("蚊香眼", "swirl"),
        ("舌头伸出", "tongue"),
        ("拿话筒", "mic"),
        ("俯身按键", "bend"),
        ("抬手左", "raiseL"),
        ("抬手右", "raiseR"),
        ("漂浮小狗", "dog"),
        ("短发1", "hair1"),
        ("短发2", "hair2"),
    ]

    chat_reply = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)

        self.settings = load_settings()
        self.scale = max(
            MIN_SCALE,
            min(MAX_SCALE, float(self.settings.get("scale", 1.0))),
        )
        self.locked = bool(self.settings.get("locked", True))
        self.state = "idle"
        self.pet_state = "idle"
        self.current_expression = None
        self.page_loaded = False
        self.head_frac_x = 0.5
        self.head_frac_y = 0.26
        self.base_bw = float(BASE_W)
        self.base_bh = float(BASE_H)
        chat_cfg = load_chat_config()
        self.chat_client = ChatClient(chat_cfg)
        self.chat_history = []
        self.chat_mode = False
        self.chat_reply.connect(self._show_chat_reply)
        self.dragging = False
        self.drag_start_pos = None
        self.drag_start_window = None
        self.drag_start_time = 0

        self._start_server()
        self.bridge = PetBridge(self)

        self.view = QWebEngineView(self)
        self.view.setAttribute(Qt.WA_TranslucentBackground)
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.page().setBackgroundColor(QColor(0, 0, 0, 0))
        settings = self.view.settings()
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(
            QWebEngineSettings.LocalContentCanAccessRemoteUrls, True
        )

        self.channel = QWebChannel(self.view.page())
        self.channel.registerObject("pet", self.bridge)
        self.view.page().setWebChannel(self.channel)

        self.drag_timer = QTimer(self)
        self.drag_timer.setInterval(15)
        self.drag_timer.timeout.connect(self.drag_poll)

        self.interact_timer = QTimer(self)
        self.interact_timer.setSingleShot(True)
        self.interact_timer.timeout.connect(self.end_interact)

        self.status_timer = QTimer(self)
        self.status_timer.setInterval(2000)
        self.status_timer.timeout.connect(self.refresh_status)
        self.status_timer.start()

        self.mouse_timer = QTimer(self)
        self.mouse_timer.setInterval(33)
        self.mouse_timer.timeout.connect(self.mouse_poll)
        self.mouse_timer.start()

        self.apply_geometry()
        self.move_to_saved_position()
        self.view.resize(self.width(), self.height())
        self.view.load(
            QUrl(f"http://127.0.0.1:{self.server_port}{LIVE_URL_PATH}")
        )
        self.view.loadFinished.connect(self.on_page_loaded)

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.save_position)

        self.refresh_status()
        self.show()

    def _start_server(self):
        handler = make_handler(BASE_DIR)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.server_port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def _run_js(self, code):
        self.view.page().runJavaScript(code)

    def content_size(self):
        width = int(round(self.base_bw * self.scale)) + PAD * 2
        chat_extra = CHAT_H if self.chat_mode else 0
        height = (
            int(round(self.base_bh * self.scale))
            + PAD * 2
            + STATUS_H
            + chat_extra
        )
        return width, height

    def apply_geometry(self):
        old_x, old_y = self.x(), self.y()
        old_w, old_h = self.width(), self.height()
        width, height = self.content_size()
        self.resize(width, height)
        bottom_center_x = old_x + old_w / 2
        bottom_y = old_y + old_h
        self.move(int(bottom_center_x - width / 2), int(bottom_y - height))

    def move_to_saved_position(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        pos_x = self.settings.get("pos_x")
        pos_y = self.settings.get("pos_y")
        if pos_x is not None and pos_y is not None:
            pos_x = int(pos_x)
            pos_y = int(pos_y)
            pos_x = max(
                screen.x(),
                min(pos_x, screen.x() + screen.width() - self.width()),
            )
            pos_y = max(
                screen.y(),
                min(pos_y, screen.y() + screen.height() - self.height()),
            )
            self.move(pos_x, pos_y)
        else:
            self.move(
                screen.x() + (screen.width() - self.width()) // 2,
                screen.y() + screen.height() - self.height(),
            )

    def resizeEvent(self, event):
        self.view.resize(self.width(), self.height())
        super().resizeEvent(event)

    def on_page_loaded(self, ok):
        self.page_loaded = ok
        if ok:
            self.sync_page_state()
            QTimer.singleShot(1500, self.sync_page_state)
        else:
            with open(ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(f"{time.ctime()} live page failed to load\n")

    def sync_page_state(self):
        self._run_js(f"window.setPetState({json.dumps(self.state)})")
        self._run_js(f"window.setScale({self.scale})")

    def set_state(self, name):
        self.state = name
        self._run_js(f"window.setPetState({json.dumps(name)})")

    def handle_chat(self, text):
        text = " ".join(str(text).split())
        if not text:
            return
        if not self.chat_client or not self.chat_client.ready():
            self._run_js(
                "window.showChatReply("
                "'（还没有配置聊天接口，请在菜单的 聊天设置 里填写 api_key）', 5000)"
            )
            return
        threading.Thread(
            target=self._chat_worker,
            args=(text,),
            daemon=True,
        ).start()

    def _chat_worker(self, text):
        try:
            reply = self.chat_client.chat(self.chat_history, text)
        except Exception as exc:
            reply = f"（连接失败：{exc}）"
        self.chat_history.append({"role": "user", "content": text})
        self.chat_history.append({"role": "assistant", "content": reply})
        self.chat_reply.emit(reply)

    def _show_chat_reply(self, reply):
        emotion = classify_emotion(reply)
        self._run_js(f"window.chatReact({json.dumps(emotion)})")
        self._run_js(
            f"window.showChatReply({json.dumps(reply)}, 6000)"
        )

    def set_chat_mode(self, enabled):
        self.chat_mode = bool(enabled)
        self.apply_geometry()
        self.view.resize(self.width(), self.height())
        self._run_js(f"window.setChatMode({str(self.chat_mode).lower()})")
        if self.chat_mode:
            self.set_state("idle")
        else:
            self.set_state(self.pet_state)

    def toggle_chat_mode(self):
        self.set_chat_mode(not self.chat_mode)

    def open_chat_settings(self):
        cfg = load_chat_config()
        dialog = ChatSettingsDialog(cfg, self)
        if dialog.exec() != QDialog.Accepted:
            return
        data = dialog.values()
        config_path = os.path.join(BASE_DIR, "config.json")
        try:
            with open(config_path, encoding="utf-8") as f:
                root = json.load(f)
        except Exception:
            root = {}
        root["chat"] = data
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(root, f, ensure_ascii=False, indent=2)
        self.chat_client = ChatClient(load_chat_config())

    def set_pet_state(self, name):
        self.pet_state = name
        if self.state != "interact":
            self.set_state(name)

    def trigger_interact(self):
        self.set_state("interact")
        self.interact_timer.start(4600)

    def end_interact(self):
        if self.state == "interact":
            self.set_state(self.pet_state)

    def apply_expression(self, name):
        self.current_expression = name
        self._run_js(
            f"window.setExpression({json.dumps(name or 'none')})"
        )

    def begin_drag(self):
        self.drag_start_pos = QCursor.pos()
        self.drag_start_window = self.pos()
        self.drag_start_time = time.monotonic()
        self.dragging = False
        self.drag_timer.start()

    def drag_poll(self):
        cur = QCursor.pos()
        held = bool(ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000)
        dx = cur.x() - self.drag_start_pos.x()
        dy = cur.y() - self.drag_start_pos.y()
        if not held:
            self.drag_timer.stop()
            elapsed = time.monotonic() - self.drag_start_time
            if not self.dragging and elapsed < 0.5 and dx * dx + dy * dy <= 36:
                self.trigger_interact()
            self.dragging = False
            return
        if self.locked:
            return
        if not self.dragging and dx * dx + dy * dy > 36:
            self.dragging = True
        if self.dragging and self.drag_start_window is not None:
            screen = QGuiApplication.primaryScreen().availableGeometry()
            new_x = self.drag_start_window.x() + dx
            new_y = self.drag_start_window.y() + dy
            new_x = max(
                screen.x(),
                min(new_x, screen.x() + screen.width() - self.width()),
            )
            new_y = max(
                screen.y(),
                min(new_y, screen.y() + screen.height() - self.height()),
            )
            self.move(new_x, new_y)

    def mouse_poll(self):
        cur = QCursor.pos()
        geo = self.frameGeometry()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        head_x = geo.x() + geo.width() * self.head_frac_x
        head_y = geo.y() + geo.height() * self.head_frac_y
        nx = (cur.x() - head_x) / max(1, screen.width() / 2)
        ny = (cur.y() - head_y) / max(1, screen.height() / 2)
        self._run_js(f"window.setEye({nx:.4f},{ny:.4f})")

    def show_menu(self):
        try:
            menu = QMenu(self)
            exp_menu = menu.addMenu("表情")
            for label, key in self.EXPRESSIONS:
                action = QAction(label, self, checkable=True)
                action.setChecked(self.current_expression == key)
                action.triggered.connect(
                    lambda checked=False, k=key: self.apply_expression(k)
                )
                exp_menu.addAction(action)
            clear_action = QAction("清除表情", self)
            clear_action.triggered.connect(
                lambda: self.apply_expression(None)
            )
            exp_menu.addAction(clear_action)
            menu.addSeparator()
            menu.addAction(
                QAction(
                    "放松（爱心眼）",
                    self,
                    triggered=lambda: self.set_pet_state("idle"),
                )
            )
            chat_action = QAction(
                "聊天模式（角色对话）", self, checkable=True
            )
            chat_action.setChecked(self.chat_mode)
            chat_action.triggered.connect(self.toggle_chat_mode)
            menu.addAction(chat_action)
            menu.addAction(
                QAction("聊天设置…", self, triggered=self.open_chat_settings)
            )
            menu.addSeparator()
            lock_action = QAction(
                "解锁拖动" if self.locked else "锁定拖动", self
            )
            lock_action.triggered.connect(self.toggle_lock)
            menu.addAction(lock_action)
            menu.addSeparator()
            menu.addAction(QAction("放大", self, triggered=self.scale_up))
            menu.addAction(QAction("缩小", self, triggered=self.scale_down))
            menu.addSeparator()
            menu.addAction(QAction("退出", self, triggered=self.quit_pet))
            menu.exec(QCursor.pos())
        except Exception:
            with open(ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(f"{time.ctime()} menu error\n")
                import traceback

                traceback.print_exc(file=f)

    def scale_up(self):
        self.set_scale(self.scale + 0.1)

    def scale_down(self):
        self.set_scale(self.scale - 0.1)

    def set_scale(self, value):
        self.scale = max(MIN_SCALE, min(MAX_SCALE, round(value, 1)))
        self.settings["scale"] = self.scale
        save_settings(self.settings)
        self.apply_geometry()
        self.view.resize(self.width(), self.height())
        self._run_js(f"window.setScale({self.scale})")

    def toggle_lock(self):
        self.locked = not self.locked
        self.settings["locked"] = self.locked
        save_settings(self.settings)
        self.dragging = False
        self.drag_timer.stop()

    def quit_pet(self):
        try:
            with open(DISABLED_FLAG, "w", encoding="utf-8") as f:
                f.write("1")
        except OSError:
            pass
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def save_position(self):
        self.settings["pos_x"] = self.x()
        self.settings["pos_y"] = self.y()
        save_settings(self.settings)

    def refresh_status(self):
        if os.path.exists(SHUTDOWN_FLAG):
            try:
                os.remove(SHUTDOWN_FLAG)
            except OSError:
                pass
            app = QApplication.instance()
            if app is not None:
                app.quit()
            return
        status = codex_monitor.get_codex_status()
        new_state = status.get("state") or "idle"
        if new_state != self.pet_state:
            self.pet_state = new_state
            if self.state != "interact" and not self.chat_mode:
                self.set_state(new_state)


def main():
    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    atexit.register(remove_pid_file)
    remove_disabled_flag()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    PetWindow()
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.ctime()}\n")
            import traceback

            traceback.print_exc(file=f)
        raise
