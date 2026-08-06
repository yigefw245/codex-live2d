import atexit
import base64
import ctypes
import json
import os
import re
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from PySide6.QtCore import QBuffer, QIODevice, QObject, QTimer, QUrl, Qt, Signal, Slot
from PySide6.QtGui import QAction, QColor, QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

import codex_monitor
import soullink_runner

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
    "model": "yumi",
    "actions": {},
}


MODEL_DIR = os.path.join(BASE_DIR, "model")


def list_models():
    models = []
    try:
        for entry in sorted(os.listdir(MODEL_DIR)):
            cfg_path = os.path.join(MODEL_DIR, entry, "model.json")
            if not os.path.isfile(cfg_path):
                continue
            try:
                with open(cfg_path, encoding="utf-8") as f:
                    cfg = json.load(f)
                models.append(
                    {
                        "id": cfg.get("id", entry),
                        "name": cfg.get("name", entry),
                    }
                )
            except Exception:
                pass
    except OSError:
        pass
    return models


def load_model_config(model_id):
    try:
        with open(
            os.path.join(MODEL_DIR, model_id, "model.json"),
            encoding="utf-8",
        ) as f:
            return json.load(f)
    except Exception:
        return None


def model_actions(settings, model_id):
    """当前模型的手动动作设置（用于同步到前端）。"""
    actions = settings.get("actions") or {}
    return actions.get(model_id) or {}


def sanitize_model_id(name):
    name = str(name or "").strip()
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "", name)
    return cleaned or "model"


def unique_model_id(base):
    model_id = sanitize_model_id(base)
    candidate = model_id
    n = 1
    while os.path.isdir(os.path.join(MODEL_DIR, candidate)):
        n += 1
        candidate = f"{model_id}_{n}"
    return candidate


def _fix_zip_name(name):
    """部分压缩包把中文文件名存成 GBK，Python 会按 cp437 解成乱码，
    这里尝试还原成正确的中文名；纯 ASCII 或已是正确 Unicode 的名字原样返回。"""
    try:
        fixed = name.encode("cp437").decode("gbk")
        if any("\u4e00" <= ch <= "\u9fff" for ch in fixed):
            return fixed
    except Exception:
        pass
    return name


def _expr_classify(name):
    """按文件名关键词把表情映射为 key / kind / 是否固定效果。"""
    name = str(name)
    if "水印" in name or "watermark" in name.lower():
        return "watermark", "effect", True
    if any(w in name for w in ("隐藏", "hide")):
        return "hide", "pose", False
    for key, words in (
        ("star", ("星星", "星光", "星眼", "star")),
        ("heart", ("爱心", "heart")),
        ("swirl", ("蚊香", "晕晕", "眩晕", "swirl", "dizzy")),
        ("black", ("黑脸", "黑面", "black")),
        ("tear", ("眼泪", "流泪", "tear")),
        ("cry", ("哭哭", "哭泣", "大哭", "cry")),
        ("teary", ("泪汪汪", "泪眼", "teary")),
        ("blush", ("脸红", "害羞", "blush")),
        ("hand", ("扶脸", "托腮", "思考", "hand")),
        ("notes", ("笔记", "写字", "书写", "notes")),
        ("phone", ("手机", "看手机", "phone")),
        ("lean", ("前倾", "俯身", "lean")),
        ("fly", ("飞头", "fly")),
        ("wry", ("歪嘴", "wry")),
        ("tongue", ("舌头", "吐舌", "tongue")),
        ("raiseL", ("抬手左", "举左手", "raiseL", "left")),
        ("raiseR", ("抬手右", "举右手", "raiseR", "right")),
        ("mic", ("话筒", "麦克风", "mic")),
        ("dog", ("小狗", "漂浮小狗", "dog")),
        ("hair", ("短发", "发型", "hair")),
    ):
        if any(w in name for w in words):
            return key, "face", False
    return None, "face", False


def _model3_expression_entries(expressions):
    """把扫描到的表情映射为 model3.json 的 Expressions 条目。

    pixi-live2d-display 与 Soullink profile 生成器都从 FileReferences.Expressions
    读取表情，所以导入模型时把 exp3 文件补注册进去，情绪引擎才能驱动原生表情。
    表情名尽量取生成器启发式认识的英文名（star/happy/surprised/angry/tear/blush），
    以便自动生成 expressionMap；星星眼额外注册一个 happy 别名。
    水印/隐藏类固定效果不注册为表情。
    """
    name_map = {
        "star": ["star", "happy"],
        "heart": ["heart"],
        "swirl": ["surprised"],
        "black": ["angry"],
        "tear": ["tear"],
        "cry": ["sob"],
        "teary": ["teary"],
        "blush": ["blush"],
        "fly": ["fly"],
        "hand": ["hand"],
        "notes": ["notes"],
        "phone": ["phone"],
        "lean": ["lean"],
        "wry": ["wry"],
        "tongue": ["tongue"],
        "raiseL": ["raiseL"],
        "raiseR": ["raiseR"],
        "mic": ["mic"],
        "dog": ["dog"],
    }
    entries = []
    for key, info in expressions.items():
        if key.startswith("hide") or key == "watermark":
            continue
        file = info.get("file") if isinstance(info, dict) else None
        if not file:
            continue
        for name in name_map.get(key, [key]):
            entries.append({"Name": name, "File": file})
    return entries


def build_model_config(model_dir, model3_rel, display_name, model_id):
    """扫描模型目录，自动生成 model.json 配置。"""
    expressions = {}
    effects = {}
    poses = []
    hide_count = 0
    expr_count = 0
    motion_files = []
    for root, _dirs, files in os.walk(model_dir):
        for fname in files:
            rel = os.path.relpath(os.path.join(root, fname), model_dir)
            rel = rel.replace("\\", "/")
            if fname.lower().endswith(".exp3.json"):
                base = os.path.splitext(fname)[0]
                key, kind, is_effect = _expr_classify(base)
                if is_effect:
                    effects["watermark"] = {"file": rel}
                    continue
                if key == "hide":
                    hide_count += 1
                    key = f"hide{hide_count}"
                    kind = "pose"
                if not key:
                    expr_count += 1
                    key = f"expr{expr_count}"
                entry = {"file": rel, "label": base}
                if kind == "pose":
                    entry["kind"] = "pose"
                    poses.append(key)
                expressions[key] = entry
            elif fname.lower().endswith(".motion3.json"):
                motion_files.append(rel)

    # 读取 model3.json 已声明的动作组
    motions = []
    patched = False
    try:
        m3_path = os.path.join(model_dir, model3_rel)
        with open(m3_path, encoding="utf-8") as f:
            m3 = json.load(f)
        declared = (m3.get("Motions") or {}).items()
        for group, items in declared:
            if items:
                label = group
                motions.append(
                    {"key": group.lower(), "group": group, "label": label}
                )
        if not motions and motion_files:
            m3["Motions"] = {
                "Idle": [
                    {"File": motion_files[0], "Loop": True}
                ]
            }
            for extra in motion_files[1:]:
                m3["Motions"][os.path.splitext(os.path.basename(extra))[0]] = [
                    {"File": extra, "Loop": True}
                ]
            motions.append(
                {
                    "key": "idle",
                    "group": "Idle",
                    "label": os.path.splitext(
                        os.path.basename(motion_files[0])
                    )[0],
                }
            )
            patched = True
        expr_entries = _model3_expression_entries(expressions)
        existing_fr_exprs = (
            m3.get("FileReferences", {}).get("Expressions") or []
        )
        if not existing_fr_exprs:
            entries = expr_entries or [
                {"Name": e.get("Name", ""), "File": e.get("File", "")}
                for e in (m3.get("Expressions") or [])
            ]
            entries = [e for e in entries if e.get("File")]
            if entries:
                m3.setdefault("FileReferences", {})["Expressions"] = entries
                if not m3.get("Expressions"):
                    m3["Expressions"] = entries
            patched = True
        if patched:
            with open(m3_path, "w", encoding="utf-8") as f:
                json.dump(m3, f, ensure_ascii=False, indent=1)
    except Exception:
        pass

    presets = {}
    if "star" in expressions:
        presets["thinking"] = {"face": "star"}
    if "hand" in expressions:
        presets.setdefault("thinking", {})["pose"] = "hand"
    if "swirl" in expressions:
        presets["working"] = {"face": "swirl"}
    if "notes" in expressions:
        presets.setdefault("working", {})["pose"] = "notes"
    if "black" in expressions:
        presets["fault"] = {"face": "black"}
    if "heart" in expressions:
        presets["idle"] = {"face": "heart"}
    if "star" in expressions:
        presets["completed"] = {"face": "star"}

    chat = {}
    for emotion, key in (
        ("happy", "heart"),
        ("sad", "tear"),
        ("angry", "black"),
        ("thinking", "star"),
        ("surprised", "swirl"),
        ("neutral", "heart"),
    ):
        if key in expressions:
            chat[emotion] = {"face": key}

    config = {
        "id": model_id,
        "name": display_name,
        "model3": model3_rel,
        "motions": motions,
        "expressions": expressions,
        "effects": effects,
        "presets": presets,
        "chat": chat,
    }
    return config, patched


# 初始窗口基准尺寸（页面加载后由前端上报真实模型包围盒，这里只用于首帧）。
BASE_W, BASE_H = 462, 858


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


VISION_DEFAULTS = {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "",
    "model": "qwen-vl-max",
    "prompt": (
        "请仔细看这张屏幕截图，用中文简要描述屏幕上正在显示的内容："
        "主要窗口、标题或文字、应用类型、画面重点。客观描述即可，不要推测。"
    ),
}

SCREEN_READ_DEFAULTS = {
    "enabled": False,
    "interval_minutes": 10,
    "vision": dict(VISION_DEFAULTS),
}


SOULLINK_DEFAULTS = {
    "enabled": False,
    "motion_style": "natural",
    "embedding": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": "",
        "model": "text-embedding-v3",
    },
    "tts": {
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "api_key": "",
        "model": "qwen-tts",
        "voice": "Cherry",
        "language_type": "Chinese",
    },
}

SOULLINK_MOTION_STYLES = ["natural", "lively", "calm", "shy"]

MENU_QSS = """
QMenu {
    background-color: rgba(26, 28, 36, 242);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 14px;
    padding: 6px;
    font-family: "Microsoft YaHei";
    font-size: 13px;
}
QMenu::item {
    background: transparent;
    color: #e7e9f2;
    padding: 7px 32px 7px 14px;
    border-radius: 8px;
    margin: 1px 5px;
}
QMenu::item:selected {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #6d5cf0, stop: 1 #a855f7
    );
    color: #ffffff;
}
QMenu::item:disabled {
    color: rgba(255, 255, 255, 96);
}
QMenu::item:checked {
    color: #c4b5fd;
}
QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 24);
    margin: 6px 14px;
}
QMenu::right-arrow {
    width: 14px;
    height: 14px;
    margin-right: 10px;
}
QMenu::indicator {
    width: 14px;
    height: 14px;
    margin-left: 4px;
}
"""


def _new_menu(title="", parent=None):
    """创建应用了暗色玻璃样式的 QMenu（含子菜单，统一圆角透明背景）。"""
    menu = QMenu(title, parent)
    menu.setStyleSheet(MENU_QSS)
    menu.setAttribute(Qt.WA_TranslucentBackground)
    return menu


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


def load_screen_read_config():
    """读取读屏幕配置：开关、频率和视觉模型接口。"""
    cfg = {
        "enabled": SCREEN_READ_DEFAULTS["enabled"],
        "interval_minutes": SCREEN_READ_DEFAULTS["interval_minutes"],
        "vision": dict(VISION_DEFAULTS),
    }
    try:
        with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
            saved = (json.load(f).get("screen_read") or {})
        if isinstance(saved.get("enabled"), bool):
            cfg["enabled"] = saved["enabled"]
        try:
            cfg["interval_minutes"] = max(1, int(saved.get("interval_minutes", 10)))
        except (TypeError, ValueError):
            pass
        vision = saved.get("vision") or {}
        for key in ("base_url", "api_key", "model", "prompt"):
            if isinstance(vision.get(key), str) and vision[key].strip():
                cfg["vision"][key] = vision[key].strip()
    except Exception:
        pass
    # 本机已有 DashScope（阿里云百炼）视觉配置时直接复用
    env_path = os.path.join(
        os.path.expanduser("~"),
        ".codex",
        "skills",
        "claude-vision-skill",
        ".env",
    )
    env_data = _read_env_file(env_path)
    if not cfg["vision"].get("api_key"):
        key = (
            os.environ.get("DASHSCOPE_API_KEY", "")
            or env_data.get("DASHSCOPE_API_KEY", "")
        )
        if key:
            cfg["vision"]["api_key"] = key
    if not cfg["vision"].get("model"):
        model = os.environ.get("VISION_MODEL", "") or env_data.get("VISION_MODEL", "")
        if model:
            cfg["vision"]["model"] = model
    return cfg


def save_screen_read_config(cfg):
    config_path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(config_path, encoding="utf-8") as f:
            root = json.load(f)
    except Exception:
        root = {}
    root["screen_read"] = cfg
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=2)


def _dashscope_env():
    env_path = os.path.join(
        os.path.expanduser("~"),
        ".codex",
        "skills",
        "claude-vision-skill",
        ".env",
    )
    return _read_env_file(env_path)


def load_soullink_config():
    """读取 Soullink 情绪引擎配置（Embedding 分类 + TTS）。"""
    cfg = {
        "enabled": SOULLINK_DEFAULTS["enabled"],
        "motion_style": SOULLINK_DEFAULTS["motion_style"],
        "embedding": dict(SOULLINK_DEFAULTS["embedding"]),
        "tts": dict(SOULLINK_DEFAULTS["tts"]),
    }
    try:
        with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
            saved = (json.load(f).get("soullink") or {})
        if isinstance(saved.get("enabled"), bool):
            cfg["enabled"] = saved["enabled"]
        if saved.get("motion_style") in SOULLINK_MOTION_STYLES:
            cfg["motion_style"] = saved["motion_style"]
        for section in ("embedding", "tts"):
            saved_section = saved.get(section) or {}
            for key in ("base_url", "api_key", "model", "voice", "language_type"):
                if isinstance(saved_section.get(key), str) and saved_section[key].strip():
                    cfg[section][key] = saved_section[key].strip()
    except Exception:
        pass
    env_data = _dashscope_env()
    dashscope_key = os.environ.get("DASHSCOPE_API_KEY", "") or env_data.get(
        "DASHSCOPE_API_KEY", ""
    )
    for section in ("embedding", "tts"):
        if not cfg[section].get("api_key") and dashscope_key:
            cfg[section]["api_key"] = dashscope_key
    return cfg


def save_soullink_config(cfg):
    config_path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(config_path, encoding="utf-8") as f:
            root = json.load(f)
    except Exception:
        root = {}
    root["soullink"] = cfg
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=2)


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


class VisionClient:
    """OpenAI 兼容的视觉模型客户端，用于读屏幕识图。"""

    def __init__(self, cfg):
        cfg = cfg or {}
        self.base = str(
            cfg.get("base_url", VISION_DEFAULTS["base_url"])
        ).rstrip("/")
        self.key = str(cfg.get("api_key", ""))
        self.model = str(cfg.get("model", VISION_DEFAULTS["model"]))
        self.prompt = str(cfg.get("prompt", VISION_DEFAULTS["prompt"]))

    def ready(self):
        return bool(self.key and self.base and self.model)

    def describe(self, image_b64, mime="image/jpeg", timeout=90):
        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{image_b64}"
                            },
                        },
                        {"type": "text", "text": self.prompt},
                    ],
                }
            ],
            "max_tokens": 1024,
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


class ScreenReadSettingsDialog(QDialog):
    """读屏幕设置：读取频率 + 视觉模型接口。"""

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("读屏幕设置")
        self.setModal(True)
        self.setMinimumWidth(440)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 180)
        self.interval_spin.setValue(int(cfg.get("interval_minutes", 10)))
        self.interval_spin.setSuffix(" 分钟")

        vision = cfg.get("vision") or {}
        self.base_url_edit = QLineEdit(str(vision.get("base_url", "")))
        self.api_key_edit = QLineEdit(str(vision.get("api_key", "")))
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.model_edit = QLineEdit(str(vision.get("model", "")))
        self.prompt_edit = QPlainTextEdit(str(vision.get("prompt", "")))
        self.prompt_edit.setFixedHeight(90)

        form.addRow("读取频率", self.interval_spin)
        form.addRow("视觉 API 地址", self.base_url_edit)
        form.addRow("视觉 API Key", self.api_key_edit)
        form.addRow("视觉模型", self.model_edit)
        form.addRow("识别提示词", self.prompt_edit)
        layout.addLayout(form)

        hint = QLabel(
            "开启后桌宠会按频率截取屏幕并发送给视觉模型识别，"
            "再把识别结果交给聊天模型生成符合人设的回应。\n"
            "截图会发送到你配置的视觉 API，请确认接口可信。"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #888;")
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return {
            "interval_minutes": self.interval_spin.value(),
            "vision": {
                "base_url": self.base_url_edit.text().strip().rstrip("/"),
                "api_key": self.api_key_edit.text().strip(),
                "model": self.model_edit.text().strip(),
                "prompt": self.prompt_edit.toPlainText().strip(),
            },
        }


class SoullinkSettingsDialog(QDialog):
    """Soullink 情绪引擎设置：Embedding 分类接口 + TTS + 动作风格。"""

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Soullink 情绪引擎设置")
        self.setModal(True)
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        embedding = cfg.get("embedding") or {}
        self.embed_base_edit = QLineEdit(str(embedding.get("base_url", "")))
        self.embed_key_edit = QLineEdit(str(embedding.get("api_key", "")))
        self.embed_key_edit.setEchoMode(QLineEdit.Password)
        self.embed_model_edit = QLineEdit(str(embedding.get("model", "")))

        tts = cfg.get("tts") or {}
        self.tts_base_edit = QLineEdit(str(tts.get("base_url", "")))
        self.tts_key_edit = QLineEdit(str(tts.get("api_key", "")))
        self.tts_key_edit.setEchoMode(QLineEdit.Password)
        self.tts_model_edit = QLineEdit(str(tts.get("model", "")))
        self.voice_combo = QComboBox()
        self.voice_combo.setEditable(True)
        voices = ["Cherry", "Serena", "Ethan", "Chelsie"]
        current_voice = str(tts.get("voice", "Cherry"))
        if current_voice not in voices:
            voices.insert(0, current_voice)
        self.voice_combo.addItems(voices)
        self.voice_combo.setCurrentText(current_voice)

        self.style_combo = QComboBox()
        self.style_combo.addItems(SOULLINK_MOTION_STYLES)
        self.style_combo.setCurrentText(str(cfg.get("motion_style", "natural")))

        form.addRow("Embedding API 地址", self.embed_base_edit)
        form.addRow("Embedding API Key", self.embed_key_edit)
        form.addRow("Embedding 模型", self.embed_model_edit)
        form.addRow("TTS API 地址", self.tts_base_edit)
        form.addRow("TTS API Key", self.tts_key_edit)
        form.addRow("TTS 模型", self.tts_model_edit)
        form.addRow("TTS 音色", self.voice_combo)
        form.addRow("动作风格", self.style_combo)
        layout.addLayout(form)

        hint = QLabel(
            "开启后，聊天气氛将改用 SDK 的 Embedding 情绪分类（首次启用需约 1 分钟"
            "初始化中文语料向量，之后自动缓存），动作系统由 Soullink 引擎驱动，"
            "回复会通过 TTS 朗读出来。若本机已配置 DASHSCOPE_API_KEY，"
            "Embedding 和 TTS 的 Key 会自动复用。"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #888;")
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return {
            "motion_style": self.style_combo.currentText(),
            "embedding": {
                "base_url": self.embed_base_edit.text().strip().rstrip("/"),
                "api_key": self.embed_key_edit.text().strip(),
                "model": self.embed_model_edit.text().strip(),
            },
            "tts": {
                "base_url": self.tts_base_edit.text().strip().rstrip("/"),
                "api_key": self.tts_key_edit.text().strip(),
                "model": self.tts_model_edit.text().strip(),
                "voice": self.voice_combo.currentText().strip(),
                "language_type": "Chinese",
            },
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

class PetWindow(QWidget):
    chat_reply = Signal(str)
    soullink_event = Signal(str)
    soullink_js = Signal(str)
    soullink_status = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)

        self.settings = load_settings()
        self.models = list_models()
        self.model_id = str(self.settings.get("model", "yumi"))
        if not any(m["id"] == self.model_id for m in self.models):
            self.model_id = "yumi"
        self.model_cfg = load_model_config(self.model_id) or {}
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
        self.screen_cfg = load_screen_read_config()
        self.vision_client = VisionClient(self.screen_cfg.get("vision") or {})
        self.screen_timer = QTimer(self)
        self.screen_timer.timeout.connect(self.read_screen_now)
        self.screen_read_busy = False
        if self.screen_cfg.get("enabled"):
            self._start_screen_timer()
        self.soullink_cfg = load_soullink_config()
        self.soullink_runner = soullink_runner.SoullinkRunner()
        self.soullink_ready = False
        self.soullink_event.connect(self._send_soullink_event)
        self.soullink_js.connect(self._run_js)
        self.soullink_status.connect(self._notify)
        if self.soullink_cfg.get("enabled"):
            QTimer.singleShot(0, self._start_soullink_async)
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
        self._run_js(
            f"window.setModelConfig({json.dumps(self.model_cfg, ensure_ascii=False)})"
        )
        self._run_js(
            f"window.setActionOverrides("
            f"{json.dumps(model_actions(self.settings, self.model_id), ensure_ascii=False)})"
        )
        self._run_js(f"window.setPetState({json.dumps(self.state)})")
        self._run_js(f"window.setScale({self.scale})")
        self._push_soullink_config()

    def set_state(self, name):
        self.state = name
        self._run_js(f"window.setPetState({json.dumps(name)})")

    def switch_model(self, model_id):
        if model_id == self.model_id:
            return
        cfg = load_model_config(model_id)
        if not cfg:
            return
        self.model_id = model_id
        self.model_cfg = cfg
        self.settings["model"] = model_id
        save_settings(self.settings)
        self.current_expression = None
        self._run_js(
            f"window.setActionOverrides("
            f"{json.dumps(model_actions(self.settings, self.model_id), ensure_ascii=False)})"
        )
        # 整页重载，让 QtWebEngine 以全新上下文加载新模型，避免原地换模型卡死。
        self.view.reload()

    def delete_model(self, model_id):
        if model_id == "yumi":
            self._notify("默认模型 yumi 不可删除")
            return
        target = os.path.join(MODEL_DIR, model_id)
        if not os.path.isdir(target):
            self._notify("模型不存在")
            return
        ret = QMessageBox.question(
            self,
            "删除模型",
            f"确定要删除模型「{model_id}」吗？\n"
            "模型文件将被永久删除，此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if ret != QMessageBox.StandardButton.Yes:
            return
        try:
            shutil.rmtree(target)
        except Exception:
            self._notify("删除失败：模型文件可能被占用")
            return
        actions = self.settings.setdefault("actions", {})
        actions.pop(model_id, None)
        save_settings(self.settings)
        self.models = list_models()
        if self.model_id == model_id:
            self.model_id = "yumi"
            self.model_cfg = load_model_config("yumi") or {}
            self.settings["model"] = "yumi"
            save_settings(self.settings)
            self.current_expression = None
            self.view.reload()
            QTimer.singleShot(
                1600,
                lambda mid=model_id: self._notify(
                    f"模型「{mid}」已删除，已切换到 yumi"
                ),
            )
        else:
            self._notify(f"模型「{model_id}」已删除")

    def set_status_action(self, status, choice):
        actions = self.settings.setdefault("actions", {})
        per_model = actions.setdefault(self.model_id, {})
        if choice is None or choice.get("type") == "auto":
            per_model.pop(status, None)
        else:
            per_model[status] = choice
        if not per_model:
            actions.pop(self.model_id, None)
        save_settings(self.settings)
        self._run_js(
            f"window.setActionOverrides("
            f"{json.dumps(per_model, ensure_ascii=False)})"
        )

    def _default_action_label(self, status):
        pres = (self.model_cfg.get("presets") or {}).get(status) or {}
        parts = []
        motion_labels = {
            m.get("group"): (m.get("label") or m.get("group"))
            for m in (self.model_cfg.get("motions") or [])
        }
        if pres.get("motion"):
            parts.append(
                motion_labels.get(pres["motion"], pres["motion"])
            )
        expressions = self.model_cfg.get("expressions") or {}
        for k in ("pose", "face"):
            key = pres.get(k)
            if not key:
                continue
            info = expressions.get(key)
            parts.append(
                info.get("label", key)
                if isinstance(info, dict)
                else key
            )
        return " + ".join(parts) if parts else "内置默认动作"

    def import_model_zip(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 Live2D 模型压缩包",
            "",
            "ZIP 压缩包 (*.zip)",
        )
        if not path:
            return
        base_name = os.path.splitext(os.path.basename(path))[0]
        model_id = unique_model_id(base_name)
        dest = os.path.join(MODEL_DIR, model_id)
        try:
            with zipfile.ZipFile(path) as zf:
                names = zf.namelist()
                dirs = [
                    _fix_zip_name(n).split("/")[0]
                    for n in names
                    if "/" in n and not n.endswith("/")
                ]
                strip = dirs[0] + "/" if len(set(dirs)) == 1 else ""
                os.makedirs(dest, exist_ok=True)
                for raw in names:
                    if raw.endswith("/"):
                        continue
                    n = _fix_zip_name(raw)
                    rel = n[len(strip):] if strip else n
                    target = os.path.normpath(os.path.join(dest, rel))
                    if not target.startswith(dest):
                        continue
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with open(target, "wb") as f:
                        f.write(zf.read(raw))
        except Exception:
            shutil.rmtree(dest, ignore_errors=True)
            self._notify("导入失败：压缩包无法解析")
            return
        self._finish_import(dest, model_id, base_name)

    def import_model_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, "选择包含 Live2D 模型的文件夹", ""
        )
        if not path:
            return
        base_name = os.path.basename(os.path.normpath(path))
        model_id = unique_model_id(base_name)
        dest = os.path.join(MODEL_DIR, model_id)
        try:
            shutil.copytree(path, dest)
        except Exception:
            shutil.rmtree(dest, ignore_errors=True)
            self._notify("导入失败：无法复制文件夹")
            return
        self._finish_import(dest, model_id, base_name)

    def _find_model3(self, model_dir):
        best = None
        for root, _dirs, files in os.walk(model_dir):
            for fname in files:
                if fname.lower().endswith(".model3.json"):
                    rel = os.path.relpath(os.path.join(root, fname), model_dir)
                    rel = rel.replace("\\", "/")
                    if best is None or len(rel.split("/")) < len(
                        best.split("/")
                    ):
                        best = rel
        return best

    def _finish_import(self, dest, model_id, display_name):
        model3_rel = self._find_model3(dest)
        if not model3_rel:
            shutil.rmtree(dest, ignore_errors=True)
            self._notify("导入失败：未找到 model3.json")
            return
        try:
            cfg, _patched = build_model_config(
                dest, model3_rel, display_name, model_id
            )
            with open(
                os.path.join(dest, "model.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            shutil.rmtree(dest, ignore_errors=True)
            self._notify("导入失败：配置生成出错")
            return
        self.models = list_models()
        self.switch_model(model_id)
        self._ensure_soullink_profile_async(model_id)
        self._notify(f"模型导入完成：{display_name}")

    def _notify(self, text):
        self._run_js(f"window.notify({json.dumps(text)}, 4000)")

    def play_motion(self, group):
        self._run_js(f"window.playMotion({json.dumps(group)})")

    def stop_motion(self):
        self._run_js("window.stopMotion()")

    def restore_defaults(self):
        self.settings = dict(DEFAULT_SETTINGS)
        save_settings(self.settings)
        self.model_id = "yumi"
        self.model_cfg = load_model_config("yumi") or {}
        self.scale = 1.0
        self.locked = True
        self.current_expression = None
        self.chat_mode = False
        self._run_js("window.setChatMode(false)")
        self.screen_cfg["enabled"] = False
        save_screen_read_config(self.screen_cfg)
        self.screen_timer.stop()
        self.soullink_cfg["enabled"] = False
        save_soullink_config(self.soullink_cfg)
        self.soullink_runner.stop()
        self.soullink_ready = False
        self._run_js("window.setSoullinkEnabled(false)")
        self.apply_geometry()
        self.move_to_saved_position()
        self.view.resize(self.width(), self.height())
        self._run_js(f"window.setScale({self.scale})")
        self.set_state("idle")
        self.view.reload()

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
        if self._soullink_usable():
            try:
                intent = self.soullink_runner.classify(text)
            except Exception:
                intent = None
            if intent:
                self.soullink_event.emit(
                    json.dumps(
                        {"reply": reply, "intent": intent},
                        ensure_ascii=False,
                    )
                )
                return
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

    # ---------- 读屏幕 ----------

    def _start_screen_timer(self):
        minutes = max(1, int(self.screen_cfg.get("interval_minutes", 10)))
        self.screen_timer.start(minutes * 60 * 1000)

    def set_screen_read_enabled(self, enabled):
        enabled = bool(enabled)
        self.screen_cfg["enabled"] = enabled
        save_screen_read_config(self.screen_cfg)
        if enabled:
            self._start_screen_timer()
            self._notify(
                f"读屏幕已开启，每 {self.screen_cfg.get('interval_minutes', 10)} 分钟看一次"
            )
            QTimer.singleShot(2000, self.read_screen_now)
        else:
            self.screen_timer.stop()
            self._notify("读屏幕已关闭")

    def read_screen_now(self):
        if self.screen_read_busy:
            return
        self.screen_read_busy = True
        try:
            shot = self._capture_screen_base64()
        except Exception as exc:
            self.screen_read_busy = False
            self._notify(f"读屏幕失败：{exc}")
            return
        if shot is None:
            self.screen_read_busy = False
            self._notify("读屏幕失败：无法截取屏幕")
            return
        threading.Thread(
            target=self._screen_read_worker,
            args=(shot[0], shot[1]),
            daemon=True,
        ).start()

    def _capture_screen_base64(self):
        """截取主屏幕并压缩为 base64 JPEG（截屏前先隐藏自己）。"""
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return None
        self.hide()
        QApplication.processEvents()
        try:
            pixmap = screen.grabWindow(0)
        finally:
            self.show()
            QApplication.processEvents()
        if pixmap.isNull():
            return None
        img = pixmap.toImage()
        max_side = 1280
        if max(img.width(), img.height()) > max_side:
            img = img.scaled(
                max_side,
                max_side,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        buf = QBuffer()
        buf.open(QIODevice.WriteOnly)
        img.save(buf, "JPG", 85)
        image_b64 = base64.b64encode(bytes(buf.data())).decode("ascii")
        return image_b64, "image/jpeg"

    def _screen_read_worker(self, image_b64, mime):
        reply = None
        desc = None
        try:
            if not self.vision_client or not self.vision_client.ready():
                reply = (
                    "（读屏幕：还没有配置视觉模型接口，"
                    "请在菜单的 读屏幕设置 里填写 API 信息）"
                )
            else:
                desc = self.vision_client.describe(image_b64, mime)
                prompt = (
                    "（读屏幕）我刚才悄悄看了一眼使用者的屏幕，看到的内容是："
                    f"{desc}\n"
                    "请以你的人物设定，用简短自然的一两句话回应这个画面，"
                    "像微信聊天一样，不要使用 Markdown，不要提及识图或你是 AI。"
                )
                if not self.chat_client or not self.chat_client.ready():
                    reply = f"我看到屏幕上好像有：{desc}"
                else:
                    reply = self.chat_client.chat([], prompt)
        except Exception as exc:
            reply = f"（读屏幕失败：{exc}）"
        finally:
            self.screen_read_busy = False
        if reply:
            if self._soullink_usable() and desc:
                try:
                    intent = self.soullink_runner.classify(desc)
                except Exception:
                    intent = None
                if intent:
                    self.soullink_event.emit(
                        json.dumps(
                            {"reply": reply, "intent": intent},
                            ensure_ascii=False,
                        )
                    )
                    return
            self.chat_reply.emit(reply)

    def open_screen_read_settings(self):
        cfg = load_screen_read_config()
        dialog = ScreenReadSettingsDialog(cfg, self)
        if dialog.exec() != QDialog.Accepted:
            return
        data = dialog.values()
        self.screen_cfg["interval_minutes"] = data["interval_minutes"]
        self.screen_cfg["vision"] = data["vision"]
        save_screen_read_config(self.screen_cfg)
        self.vision_client = VisionClient(self.screen_cfg.get("vision") or {})
        if self.screen_cfg.get("enabled"):
            self._start_screen_timer()

    # ---------- Soullink 情绪引擎 ----------

    def _soullink_usable(self):
        return bool(
            self.soullink_cfg.get("enabled")
            and self.soullink_runner
            and self.soullink_runner.ready
        )

    def _soullink_profile_url(self):
        return f"/model/{self.model_id}/soullink.profile.json"

    def _soullink_has_profile(self):
        return os.path.isfile(
            os.path.join(MODEL_DIR, self.model_id, "soullink.profile.json")
        )

    def _push_soullink_config(self):
        if not self.soullink_cfg.get("enabled") or not self.soullink_runner:
            self.soullink_js.emit("window.setSoullinkEnabled(false)")
            return
        if not self.soullink_runner.ready or not self.soullink_runner.port:
            self.soullink_js.emit("window.setSoullinkEnabled(false)")
            return
        if not self._soullink_has_profile():
            self.soullink_js.emit("window.setSoullinkEnabled(false)")
            return
        payload = {
            "enabled": True,
            "ttsUrl": f"http://127.0.0.1:{self.soullink_runner.port}/tts",
            "profileUrl": self._soullink_profile_url(),
            "motionStyle": self.soullink_cfg.get("motion_style", "natural"),
        }
        self.soullink_js.emit(
            f"window.setSoullinkConfig({json.dumps(payload, ensure_ascii=False)})"
        )

    def _start_soullink_async(self):
        def _start():
            try:
                self.soullink_runner.start(self.soullink_cfg)
                self.soullink_ready = True
            except Exception as exc:
                self.soullink_ready = False
                self.soullink_cfg["enabled"] = False
                save_soullink_config(self.soullink_cfg)
                self.chat_reply.emit(f"（Soullink 启动失败：{exc}）")
                return
            # 当前模型没有 profile 时自动生成（yumi 已带，其他模型自动扫描生成）
            if not self._soullink_has_profile():
                ok, msg = self.soullink_runner.generate_profile(self.model_id)
                if not ok:
                    self.soullink_ready = False
                    self.soullink_cfg["enabled"] = False
                    save_soullink_config(self.soullink_cfg)
                    self.soullink_runner.stop()
                    self.chat_reply.emit(
                        f"（Soullink 模型配置生成失败：{msg}）"
                    )
                    return
                self.soullink_status.emit(
                    f"已为「{self.model_id}」自动生成 Soullink 配置"
                )
            self.soullink_js.emit("window.setSoullinkEnabled(true)")
            self._push_soullink_config()
            self.soullink_status.emit(
                "Soullink 情绪引擎已启动，正在初始化情绪语料（首次约 1 分钟）"
            )
            self.soullink_runner.wait_classifier_ready(
                on_ready=lambda: self.soullink_status.emit(
                    "Soullink 情绪识别已就绪"
                )
            )

        threading.Thread(target=_start, daemon=True).start()

    def set_soullink_enabled(self, enabled):
        enabled = bool(enabled)
        self.soullink_cfg["enabled"] = enabled
        save_soullink_config(self.soullink_cfg)
        if enabled:
            if not self.soullink_runner.node_path():
                self.soullink_cfg["enabled"] = False
                save_soullink_config(self.soullink_cfg)
                self._notify("Soullink 需要 Node.js（18+），请先安装 Node")
                return
            self._start_soullink_async()
        else:
            self.soullink_ready = False
            self.soullink_runner.stop()
            self._run_js("window.setSoullinkEnabled(false)")
            # 关闭 Soullink 后立即恢复 Codex 状态动作匹配
            self.refresh_status()
            self._notify("Soullink 情绪引擎已关闭，恢复原有关键词识别")

    def open_soullink_settings(self):
        cfg = load_soullink_config()
        dialog = SoullinkSettingsDialog(cfg, self)
        if dialog.exec() != QDialog.Accepted:
            return
        data = dialog.values()
        data["enabled"] = bool(self.soullink_cfg.get("enabled"))
        self.soullink_cfg.update(data)
        save_soullink_config(self.soullink_cfg)
        if self.soullink_ready and self.soullink_runner and self.soullink_runner.ready:
            # 配置变更后重启侧服务使新模型/Key 生效
            self.soullink_runner.stop()
            self.soullink_ready = False
            if self.soullink_cfg.get("enabled"):
                self._start_soullink_async()
            else:
                self._run_js("window.setSoullinkEnabled(false)")

    def regenerate_soullink_profile(self):
        """手动重新生成当前模型的 Soullink profile（强制覆盖）。"""

        def _work():
            ok, msg = self.soullink_runner.generate_profile(
                self.model_id, force=True
            )
            if not ok:
                self.soullink_status.emit(
                    f"「{self.model_id}」配置生成失败：{msg}"
                )
                return
            self.soullink_status.emit(
                f"「{self.model_id}」的 Soullink 配置已重新生成"
            )
            if self.soullink_cfg.get("enabled"):
                # 让前端用新 profile 重启 SDK 会话
                self.soullink_js.emit("window.soullinkRestart()")

        threading.Thread(target=_work, daemon=True).start()

    def _ensure_soullink_profile_async(self, model_id):
        """模型导入后后台补生成 profile（已存在则跳过）。"""

        def _work():
            ok, msg = self.soullink_runner.generate_profile(model_id)
            if not ok:
                self.soullink_status.emit(
                    f"「{model_id}」Soullink 配置生成失败：{msg}"
                )
                return
            if self.soullink_cfg.get("enabled") and model_id == self.model_id:
                self._push_soullink_config()

        threading.Thread(target=_work, daemon=True).start()

    def _send_soullink_event(self, payload_json):
        self._run_js(f"window.soullinkChat({payload_json})")

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
            menu = _new_menu(parent=self)
            header = QLabel(f"✦  {self.model_cfg.get('name', self.model_id)}")
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet(
                "color: #a9b2c8;"
                "font-size: 11px;"
                "font-weight: bold;"
                "padding: 5px 10px 3px 10px;"
                "background: transparent;"
            )
            header_action = QWidgetAction(menu)
            header_action.setDefaultWidget(header)
            menu.addAction(header_action)
            menu.addSeparator()
            model_menu = _new_menu("模型", menu)
            menu.addMenu(model_menu)
            for m in self.models:
                action = QAction(m["name"], self, checkable=True)
                action.setChecked(m["id"] == self.model_id)
                action.triggered.connect(
                    lambda checked=False, mid=m["id"]: self.switch_model(mid)
                )
                model_menu.addAction(action)
            delete_menu = _new_menu("删除模型", model_menu)
            model_menu.addMenu(delete_menu)
            deletable = [m for m in self.models if m["id"] != "yumi"]
            if deletable:
                for m in deletable:
                    action = QAction(m["name"], self)
                    action.triggered.connect(
                        lambda checked=False, mid=m["id"]: self.delete_model(
                            mid
                        )
                    )
                    delete_menu.addAction(action)
            else:
                delete_menu.addAction(
                    QAction("（没有可删除的模型）", self, enabled=False)
                )
            model_menu.addSeparator()
            model_menu.addAction(
                QAction(
                    "导入模型（zip）…",
                    self,
                    triggered=self.import_model_zip,
                )
            )
            model_menu.addAction(
                QAction(
                    "导入模型（文件夹）…",
                    self,
                    triggered=self.import_model_folder,
                )
            )

            status_menu = _new_menu("状态动作", menu)
            menu.addMenu(status_menu)
            per_model_actions = model_actions(self.settings, self.model_id)
            status_list = [
                ("待机", "idle"),
                ("思考中", "thinking"),
                ("执行中", "working"),
                ("完成", "completed"),
                ("故障", "fault"),
                ("点击互动", "interact"),
            ]
            expressions = self.model_cfg.get("expressions") or {}
            for label, status in status_list:
                sub = _new_menu(label, status_menu)
                status_menu.addMenu(sub)
                cur = per_model_actions.get(status) or {}
                auto_item = QAction(
                    f"自动（{self._default_action_label(status)}）",
                    self,
                    checkable=True,
                )
                auto_item.setChecked(not cur.get("type"))
                auto_item.triggered.connect(
                    lambda checked=False, s=status: self.set_status_action(
                        s, None
                    )
                )
                sub.addAction(auto_item)
                none_item = QAction("无动作", self, checkable=True)
                none_item.setChecked(cur.get("type") == "none")
                none_item.triggered.connect(
                    lambda checked=False, s=status: self.set_status_action(
                        s, {"type": "none"}
                    )
                )
                sub.addAction(none_item)
                sub.addSeparator()
                for m in self.model_cfg.get("motions") or []:
                    group = m["group"]
                    item = QAction(
                        m.get("label") or group, self, checkable=True
                    )
                    item.setChecked(
                        cur.get("type") == "motion" and cur.get("key") == group
                    )
                    item.triggered.connect(
                        lambda checked=False, s=status, g=group: self.set_status_action(
                            s, {"type": "motion", "key": g}
                        )
                    )
                    sub.addAction(item)
                for key, info in expressions.items():
                    if isinstance(info, dict):
                        kind = info.get("kind", "face")
                        expr_label = info.get("label", key)
                    else:
                        kind = "face"
                        expr_label = key
                    item = QAction(expr_label, self, checkable=True)
                    item.setChecked(
                        cur.get("type") == "expr" and cur.get("key") == key
                    )
                    item.triggered.connect(
                        lambda checked=False, s=status, k=key: self.set_status_action(
                            s, {"type": "expr", "key": k}
                        )
                    )
                    sub.addAction(item)

            motion_menu = _new_menu("动作", menu)
            menu.addMenu(motion_menu)
            motions = self.model_cfg.get("motions") or []
            if motions:
                for m in motions:
                    label = m.get("label") or m.get("group")
                    action = QAction(label, self)
                    action.triggered.connect(
                        lambda checked=False, g=m["group"]: self.play_motion(g)
                    )
                    motion_menu.addAction(action)
            motion_menu.addAction(
                QAction("停止动作", self, triggered=self.stop_motion)
            )

            exp_menu = _new_menu("表情", menu)
            menu.addMenu(exp_menu)
            expressions = self.model_cfg.get("expressions") or {}
            for key, info in expressions.items():
                if isinstance(info, dict):
                    label = info.get("label", key)
                else:
                    label = key
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
                    "放松",
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
            screen_menu = _new_menu("读屏幕", menu)
            menu.addMenu(screen_menu)
            screen_toggle = QAction("开启读屏幕", self, checkable=True)
            screen_toggle.setChecked(bool(self.screen_cfg.get("enabled")))
            screen_toggle.triggered.connect(self.set_screen_read_enabled)
            screen_menu.addAction(screen_toggle)
            screen_menu.addAction(
                QAction(
                    "读屏幕设置…",
                    self,
                    triggered=self.open_screen_read_settings,
                )
            )
            screen_menu.addAction(
                QAction(
                    "立即读一次屏幕",
                    self,
                    triggered=self.read_screen_now,
                )
            )
            soullink_menu = _new_menu("Soullink 情绪引擎", menu)
            menu.addMenu(soullink_menu)
            soullink_toggle = QAction(
                "开启（Embedding 识别 + 动作 + TTS）",
                self,
                checkable=True,
            )
            soullink_toggle.setChecked(bool(self.soullink_cfg.get("enabled")))
            soullink_toggle.triggered.connect(self.set_soullink_enabled)
            soullink_menu.addAction(soullink_toggle)
            soullink_menu.addAction(
                QAction(
                    "Soullink 设置…",
                    self,
                    triggered=self.open_soullink_settings,
                )
            )
            soullink_menu.addAction(
                QAction(
                    "生成/更新当前模型 profile…",
                    self,
                    triggered=self.regenerate_soullink_profile,
                )
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
            menu.addAction(
                QAction(
                    "恢复默认设置和模型",
                    self,
                    triggered=self.restore_defaults,
                )
            )
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
        try:
            self.soullink_runner.stop()
        except Exception:
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
        if self.soullink_cfg.get("enabled"):
            # Soullink 模式：禁用 Codex 状态动作匹配
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
    # Fusion + QSS：让右键菜单支持圆角与渐变高亮（原生 Windows 样式会忽略这些）
    app.setStyle("Fusion")
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
