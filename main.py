import atexit
import base64
import ctypes
import json
import os
import queue
import random
import re
import shutil
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from PySide6.QtCore import QBuffer, QIODevice, QObject, QTimer, QUrl, Qt, Signal, Slot
from PySide6.QtGui import QAction, QColor, QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

import codex_monitor
import pet_memory
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
    "crop_bottom": 0.0,
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

# 聊天里说“帮我看看”之类的话时，自动读屏幕并把画面内容一起交给模型
SCREEN_LOOK_KEYWORDS = (
    "屏幕",
    "看屏幕",
    "看看屏幕",
    "看一下屏幕",
    "看桌面",
    "看看桌面",
    "帮我看看",
    "帮我看",
    "帮我瞅瞅",
    "帮我瞧瞧",
    "看看我",
    "看看我在",
    "你能看到",
    "你在看什么",
    "瞅一眼",
    "瞄一眼",
)


SOULLINK_DEFAULTS = {
    "enabled": False,
    "motion_style": "natural",
    "motion_intensity": 1.0,
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

PROACTIVE_DEFAULTS = {
    "enabled": False,
    "interval_minutes": 15,
    "probability": 70,
    "min_interval_minutes": 3,
}

VOICE_INPUT_DEFAULTS = {
    "enabled": False,
    "model": "small",
    "language": "zh",
    "hf_endpoint": "",
    "hotkey_enabled": True,
    "hotkey_key": "F8",
    "hotkey_modifiers": "",
}

VOICE_CHAT_DEFAULTS = {
    "enabled": False,
    "wake_words": ["yumi", "尤米"],
    "silence_seconds": 0.8,
    "idle_timeout_seconds": 60,
    "max_turns": 50,
    "exit_phrases": ["退出对话", "拜拜", "再见", "不聊了", "去忙吧"],
    "tts_enabled": True,
    "tts": {
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "api_key": "",
        "model": "qwen-tts",
        "voice": "Cherry",
        "language_type": "Chinese",
    },
}

# 这类“（…）”开头的回复属于错误提示，不朗读
VOICE_ERROR_PREFIXES = ("（连接失败", "（读屏幕", "（Soullink", "（还没")

# Soullink 情绪集合（用于“情绪→动作姿势”自定义）
SOULLINK_EMOTIONS = [
    ("happy", "开心"),
    ("excited", "兴奋"),
    ("shy", "害羞"),
    ("affectionate", "亲昵"),
    ("neutral", "中性"),
    ("calm", "冷静"),
    ("curious", "好奇"),
    ("confused", "疑惑"),
    ("surprised", "惊讶"),
    ("sad", "难过"),
    ("teary", "想哭"),
    ("anxiety", "焦虑"),
    ("tired", "累"),
    ("concerned", "担心"),
    ("anger", "生气"),
    ("angry", "生气"),
]


def _voice_chat_diag(text):
    """语音对话诊断日志（排障用，不参与功能逻辑）。"""
    try:
        with open(
            os.path.join(BASE_DIR, "voice_chat_diag.log"),
            "a",
            encoding="utf-8",
        ) as f:
            f.write(f"{time.ctime()} {text}\n")
    except Exception:
        pass

MEMORY_DEFAULTS = {
    "enabled": True,
    "short_term_max_messages": 40,
    "short_term_max_hours": 24,
    "long_term_extract": True,
    "long_term_max_entries": 200,
    "recall_top_k": 5,
    "use_embedding": True,
    "embedding": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": "",
        "model": "text-embedding-v3",
    },
}

STT_CACHE_ROOT = os.path.join(BASE_DIR, ".cache", "stt")

STT_MODEL_REPOS = {
    "tiny": "Systran/faster-whisper-tiny",
    "base": "Systran/faster-whisper-base",
    "small": "Systran/faster-whisper-small",
    "medium": "Systran/faster-whisper-medium",
    "large": "Systran/faster-whisper-large-v3",
}

STT_MODELSCOPE_REPOS = {
    "tiny": "pengzhendong/faster-whisper-tiny",
    "base": "pengzhendong/faster-whisper-base",
    "small": "pengzhendong/faster-whisper-small",
    "medium": "pengzhendong/faster-whisper-medium",
    "large": "pengzhendong/faster-whisper-large-v3",
}

STT_REQUIRED_FILES = ("model.bin", "config.json", "tokenizer.json", "vocabulary.txt")

STT_HOTKEY_KEYS = {
    "F1": 0x70,
    "F2": 0x71,
    "F3": 0x72,
    "F4": 0x73,
    "F5": 0x74,
    "F6": 0x75,
    "F7": 0x76,
    "F8": 0x77,
    "F9": 0x78,
    "F10": 0x79,
    "F11": 0x7A,
    "F12": 0x7B,
    "CapsLock": 0x14,
    "ScrollLock": 0x91,
    "Pause": 0x13,
}

STT_HOTKEY_MODIFIER_VKS = {
    "ctrl": 0x11,
    "shift": 0x10,
    "alt": 0x12,
    "win": 0x5B,
}

# 未配置聊天接口时主动发言的兜底台词
PROACTIVE_FALLBACK_LINES = [
    "嗯……在忙什么呀？",
    "我刚刚发了一会儿呆，想你了。",
    "要不要休息一下，喝口水？",
    "窗外的风好像挺舒服的。",
    "嘿嘿，我在这里陪着你哦。",
    "今天也要加油鸭！",
]

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
        "motion_intensity": SOULLINK_DEFAULTS["motion_intensity"],
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
        try:
            cfg["motion_intensity"] = max(
                0.5, min(2.0, float(saved.get("motion_intensity", 1.0)))
            )
        except (TypeError, ValueError):
            pass
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


def load_proactive_config():
    """读取主动发言配置：开关、平均间隔、概率、最短间隔。"""
    cfg = dict(PROACTIVE_DEFAULTS)
    try:
        with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
            saved = (json.load(f).get("proactive_speech") or {})
        if isinstance(saved.get("enabled"), bool):
            cfg["enabled"] = saved["enabled"]
        for key in ("interval_minutes", "probability", "min_interval_minutes"):
            try:
                cfg[key] = max(1, int(saved.get(key, cfg[key])))
            except (TypeError, ValueError):
                pass
        cfg["probability"] = min(100, cfg["probability"])
    except Exception:
        pass
    return cfg


def save_proactive_config(cfg):
    config_path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(config_path, encoding="utf-8") as f:
            root = json.load(f)
    except Exception:
        root = {}
    root["proactive_speech"] = cfg
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=2)


def load_voice_input_config():
    """读取语音输入配置：开关 + 本地识别模型（RealtimeSTT / faster-whisper）。"""
    cfg = dict(VOICE_INPUT_DEFAULTS)
    try:
        with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
            saved = (json.load(f).get("voice_input") or {})
        if isinstance(saved.get("enabled"), bool):
            cfg["enabled"] = saved["enabled"]
        if isinstance(saved.get("hotkey_enabled"), bool):
            cfg["hotkey_enabled"] = saved["hotkey_enabled"]
        for key in ("model", "language", "hf_endpoint", "hotkey_key", "hotkey_modifiers"):
            if isinstance(saved.get(key), str) and saved[key].strip():
                cfg[key] = saved[key].strip()
    except Exception:
        pass
    return cfg


def save_voice_input_config(cfg):
    config_path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(config_path, encoding="utf-8") as f:
            root = json.load(f)
    except Exception:
        root = {}
    root["voice_input"] = cfg
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=2)


def load_voice_chat_config():
    """读取语音对话配置：唤醒词、监听时长、退出语与 TTS 接口。"""
    cfg = {
        "enabled": VOICE_CHAT_DEFAULTS["enabled"],
        "wake_words": list(VOICE_CHAT_DEFAULTS["wake_words"]),
        "silence_seconds": VOICE_CHAT_DEFAULTS["silence_seconds"],
        "idle_timeout_seconds": VOICE_CHAT_DEFAULTS["idle_timeout_seconds"],
        "max_turns": VOICE_CHAT_DEFAULTS["max_turns"],
        "exit_phrases": list(VOICE_CHAT_DEFAULTS["exit_phrases"]),
        "tts_enabled": VOICE_CHAT_DEFAULTS["tts_enabled"],
        "tts": dict(VOICE_CHAT_DEFAULTS["tts"]),
    }
    try:
        with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
            root = json.load(f)
            saved = (root.get("voice_chat") or {})
        if isinstance(saved.get("enabled"), bool):
            cfg["enabled"] = saved["enabled"]
        if isinstance(saved.get("tts_enabled"), bool):
            cfg["tts_enabled"] = saved["tts_enabled"]
        try:
            cfg["silence_seconds"] = max(
                0.3, float(saved.get("silence_seconds", cfg["silence_seconds"]))
            )
        except (TypeError, ValueError):
            pass
        for key in ("idle_timeout_seconds", "max_turns"):
            try:
                cfg[key] = max(1, int(saved.get(key, cfg[key])))
            except (TypeError, ValueError):
                pass
        for key in ("wake_words", "exit_phrases"):
            value = saved.get(key)
            if isinstance(value, str) and value.strip():
                cfg[key] = [
                    part.strip()
                    for part in re.split(r"[、,，/|]", value)
                    if part.strip()
                ]
            elif isinstance(value, list):
                cfg[key] = [
                    str(part).strip()
                    for part in value
                    if str(part).strip()
                ]
        tts = saved.get("tts") or {}
        for key in ("base_url", "api_key", "model", "voice", "language_type"):
            if isinstance(tts.get(key), str) and tts[key].strip():
                cfg["tts"][key] = tts[key].strip()
        # 复用已有百炼 TTS Key（Soullink TTS），省去重复填写
        soullink_tts = (root.get("soullink") or {}).get("tts") or {}
        if not cfg["tts"].get("api_key"):
            key = soullink_tts.get("api_key")
            if isinstance(key, str) and key.strip():
                cfg["tts"]["api_key"] = key.strip()
    except Exception:
        pass
    env_data = _dashscope_env()
    dashscope_key = os.environ.get("DASHSCOPE_API_KEY", "") or env_data.get(
        "DASHSCOPE_API_KEY", ""
    )
    if not cfg["tts"].get("api_key") and dashscope_key:
        cfg["tts"]["api_key"] = dashscope_key
    return cfg


def save_voice_chat_config(cfg):
    config_path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(config_path, encoding="utf-8") as f:
            root = json.load(f)
    except Exception:
        root = {}
    root["voice_chat"] = cfg
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=2)


def load_memory_config():
    """读取本地记忆配置：短期/长期记忆参数 + Embedding 语义检索接口。"""
    cfg = {
        "enabled": MEMORY_DEFAULTS["enabled"],
        "short_term_max_messages": MEMORY_DEFAULTS["short_term_max_messages"],
        "short_term_max_hours": MEMORY_DEFAULTS["short_term_max_hours"],
        "long_term_extract": MEMORY_DEFAULTS["long_term_extract"],
        "long_term_max_entries": MEMORY_DEFAULTS["long_term_max_entries"],
        "recall_top_k": MEMORY_DEFAULTS["recall_top_k"],
        "use_embedding": MEMORY_DEFAULTS["use_embedding"],
        "embedding": dict(MEMORY_DEFAULTS["embedding"]),
    }
    try:
        with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
            root = json.load(f)
            saved = (root.get("memory") or {})
        if isinstance(saved.get("enabled"), bool):
            cfg["enabled"] = saved["enabled"]
        if isinstance(saved.get("long_term_extract"), bool):
            cfg["long_term_extract"] = saved["long_term_extract"]
        if isinstance(saved.get("use_embedding"), bool):
            cfg["use_embedding"] = saved["use_embedding"]
        for key in (
            "short_term_max_messages",
            "long_term_max_entries",
            "recall_top_k",
        ):
            try:
                cfg[key] = max(1, int(saved.get(key, cfg[key])))
            except (TypeError, ValueError):
                pass
        try:
            cfg["short_term_max_hours"] = max(
                0.5,
                float(
                    saved.get(
                        "short_term_max_hours",
                        cfg["short_term_max_hours"],
                    )
                ),
            )
        except (TypeError, ValueError):
            pass
        embedding = saved.get("embedding") or {}
        for key in ("base_url", "api_key", "model"):
            if isinstance(embedding.get(key), str) and embedding[key].strip():
                cfg["embedding"][key] = embedding[key].strip()
        if not cfg["embedding"].get("api_key"):
            # 复用已有百炼 Key（Soullink Embedding / 读屏幕视觉），省去重复填写
            for section in ("soullink", "screen_read"):
                part = root.get(section) or {}
                if section == "soullink":
                    part = part.get("embedding") or {}
                elif section == "screen_read":
                    part = part.get("vision") or {}
                key = part.get("api_key") if isinstance(part, dict) else None
                if isinstance(key, str) and key.strip():
                    cfg["embedding"]["api_key"] = key.strip()
                    break
    except Exception:
        pass
    env_data = _dashscope_env()
    dashscope_key = os.environ.get("DASHSCOPE_API_KEY", "") or env_data.get(
        "DASHSCOPE_API_KEY", ""
    )
    if not cfg["embedding"].get("api_key") and dashscope_key:
        cfg["embedding"]["api_key"] = dashscope_key
    return cfg


def save_memory_config(cfg):
    config_path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(config_path, encoding="utf-8") as f:
            root = json.load(f)
    except Exception:
        root = {}
    root["memory"] = cfg
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
        "生气", "气死", "气人", "气呼呼", "可恶", "讨厌", "恼火",
        "愤怒", "发火", "烦死了", "烦人", "😠", "😡",
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


def _split_sentences(text):
    """把文本按句末标点（。！？!?…/换行）切成句子。"""
    parts = re.split(r"([。！？!?…]+|\n)", text)
    sentences = []
    i = 0
    while i < len(parts):
        seg = parts[i]
        if i + 1 < len(parts) and re.match(
            r"[。！？!?…]+|\n", parts[i + 1]
        ):
            sentences.append((seg + parts[i + 1]).strip())
            i += 2
        else:
            if seg.strip():
                sentences.append(seg.strip())
            i += 1
    return [s for s in sentences if s]


class _SpeechChunker:
    """流式文本 → 逐句 TTS 片段（未完成的句尾留在缓冲里）。"""

    def __init__(self, max_len=80):
        self.buf = ""
        self.max_len = max_len

    def feed(self, chunk):
        self.buf += chunk
        sentences = _split_sentences(self.buf)
        if not sentences:
            return []
        if self.buf and self.buf[-1] not in "。！？!?…\n":
            complete, pending = sentences[:-1], sentences[-1]
        else:
            complete, pending = sentences, ""
        self.buf = pending
        out = list(complete)
        # 超长兜底：缓冲过长时整段发出，避免一直等句号
        if len(self.buf) >= self.max_len:
            out.append(self.buf)
            self.buf = ""
        return out

    def flush(self):
        out = [self.buf] if self.buf.strip() else []
        self.buf = ""
        return out


class ChatClient:
    def __init__(self, cfg):
        self.base = str(cfg.get("base_url", CHAT_DEFAULTS["base_url"])).rstrip("/")
        self.key = str(cfg.get("api_key", ""))
        self.model = str(cfg.get("model", CHAT_DEFAULTS["model"]))
        self.persona = str(cfg.get("persona", CHAT_DEFAULTS["persona"]))

    def ready(self):
        return bool(self.key and self.base)

    def chat(self, history, text, memory_note=None, timeout=60):
        messages = [{"role": "system", "content": self.persona}]
        if memory_note:
            messages.append({"role": "system", "content": memory_note})
        messages.extend(history[-20:])
        messages.append({"role": "user", "content": text})
        return self.raw_complete(messages, max_tokens=300, timeout=timeout)

    def chat_stream(self, history, text, memory_note=None, on_chunk=None, timeout=120):
        """流式聊天（SSE）：逐字回调 on_chunk，返回完整回复。"""
        messages = [{"role": "system", "content": self.persona}]
        if memory_note:
            messages.append({"role": "system", "content": memory_note})
        messages.extend(history[-20:])
        messages.append({"role": "user", "content": text})
        body = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 300,
            "stream": True,
        }
        request = urllib.request.Request(
            self.base + "/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.key,
                "Content-Type": "application/json",
            },
        )
        full = []
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw in response:
                line = raw.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    obj = json.loads(payload)
                except Exception:
                    continue
                choices = obj.get("choices") or []
                if not choices:
                    continue
                delta = (choices[0].get("delta") or {}).get("content") or ""
                if delta:
                    full.append(delta)
                    if on_chunk:
                        try:
                            on_chunk(delta)
                        except Exception:
                            pass
        return "".join(full)

    def raw_complete(self, messages, max_tokens=300, timeout=60):
        """直接发送一组消息并返回模型文本（记忆提炼等内部调用使用）。"""
        body = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
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


class TtsClient:
    """DashScope（百炼）TTS 客户端：合成文本并下载音频，供语音对话朗读。"""

    def __init__(self, cfg):
        cfg = cfg or {}
        self.base = str(
            cfg.get("base_url") or VOICE_CHAT_DEFAULTS["tts"]["base_url"]
        ).rstrip("/")
        self.key = str(cfg.get("api_key") or "")
        self.model = str(cfg.get("model") or "qwen-tts")
        self.voice = str(cfg.get("voice") or "Cherry")
        self.language_type = str(cfg.get("language_type") or "Chinese")

    def ready(self):
        return bool(self.key and self.base and self.model)

    def synthesize(self, text, timeout=120):
        """合成并下载音频，返回 (audio_bytes, mime)。"""
        body = {
            "model": self.model,
            "input": {
                "text": str(text),
                "voice": self.voice,
                "language_type": self.language_type,
            },
        }
        request = urllib.request.Request(
            self.base + "/services/aigc/multimodal-generation/generation",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.key,
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        audio_url = (data.get("output") or {}).get("audio", {}).get("url")
        if not audio_url:
            raise RuntimeError("TTS 响应中没有音频地址")
        with urllib.request.urlopen(audio_url, timeout=timeout) as response:
            audio = response.read()
        mime = (
            response.headers.get("content-type") or "audio/wav"
        ).split(";")[0].strip()
        return audio, mime


class LocalVoiceRecognizer:
    """本地语音识别：RealtimeSTT + faster-whisper，录音和识别都在本机完成。"""

    def __init__(self, cfg):
        cfg = cfg or {}
        self.model = str(cfg.get("model") or VOICE_INPUT_DEFAULTS["model"])
        self.language = str(cfg.get("language") or VOICE_INPUT_DEFAULTS["language"])
        self.hf_endpoint = str(cfg.get("hf_endpoint") or "").strip()
        self.silence_duration = 0.8
        self._recorder = None
        self._ready = False
        self._recording = False
        self._error = ""
        self._lock = threading.Lock()
        self._cancel = threading.Event()
        self._progress_cb = None
        self._continuous = False

    def ready(self):
        return self._ready

    def error(self):
        return self._error

    def cancel(self):
        self._cancel.set()

    def set_progress_callback(self, cb):
        self._progress_cb = cb

    def _model_dir(self):
        return os.path.join(STT_CACHE_ROOT, "whisper-" + self.model)

    def needs_model(self):
        return not os.path.isfile(
            os.path.join(self._model_dir(), "model.bin")
        )

    def _emit_progress(self, text):
        if self._progress_cb:
            try:
                self._progress_cb(text)
            except Exception:
                pass

    def _get_json(self, url):
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def _list_source_files(self, kind, base, repo):
        """返回 (文件名, 大小) 列表；kind: modelscope / huggingface。"""
        if kind == "modelscope":
            url = (
                f"{base}/api/v1/models/{repo}/repo/files"
                "?Revision=master&Recursive=true"
            )
            data = self._get_json(url)
            files = (
                (data.get("Data") or {}).get("Files")
                or data.get("Files")
                or []
            )
            return [
                (str(f.get("Path", "")), int(f.get("Size") or 0))
                for f in files
            ]
        url = f"{base}/api/models/{repo}"
        data = self._get_json(url)
        return [
            (str(s.get("rfilename", "")), int(s.get("size") or 0))
            for s in data.get("siblings", [])
        ]

    def _source_file_url(self, kind, base, repo, filename):
        if kind == "modelscope":
            quoted = urllib.parse.quote(filename)
            return (
                f"{base}/api/v1/models/{repo}/repo"
                f"?Revision=master&FilePath={quoted}"
            )
        quoted = urllib.parse.quote(filename)
        return f"{base}/{repo}/resolve/main/{quoted}"

    def _download_file(self, url, dest, label, expected_size=0):
        """流式下载单个文件到 dest，带进度回调与取消检查。"""
        tmp = dest + ".part"
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        request = urllib.request.Request(url)
        last_report = 0.0
        with urllib.request.urlopen(request, timeout=60) as response:
            got = 0
            with open(tmp, "wb") as f:
                while True:
                    if self._cancel.is_set():
                        raise RuntimeError("下载已取消")
                    chunk = response.read(262144)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    now = time.monotonic()
                    if now - last_report >= 2.0:
                        last_report = now
                        if expected_size > 0:
                            percent = got * 100 // expected_size
                            self._emit_progress(
                                f"正在下载{label}：{got // 1048576}MB / "
                                f"{expected_size // 1048576}MB（{percent}%）"
                            )
                        else:
                            self._emit_progress(
                                f"正在下载{label}：{got // 1048576}MB…"
                            )
        if os.path.getsize(tmp) <= 0:
            os.remove(tmp)
            raise RuntimeError(f"{label} 下载内容为空")
        os.replace(tmp, dest)

    def _ensure_model(self):
        """下载/确认本地 Whisper 模型，按多来源自动回退。"""
        target = self._model_dir()
        if os.path.isfile(os.path.join(target, "model.bin")):
            return target
        self._cancel.clear()
        os.makedirs(target, exist_ok=True)
        hf_repo = STT_MODEL_REPOS.get(self.model) or (
            f"Systran/faster-whisper-{self.model}"
        )
        ms_repo = STT_MODELSCOPE_REPOS.get(self.model, "")
        sources = []
        if self.hf_endpoint:
            sources.append(("huggingface", self.hf_endpoint, hf_repo))
        sources.append(("modelscope", "https://modelscope.cn", ms_repo))
        sources.append(("huggingface", "https://hf-mirror.com", hf_repo))
        sources.append(("huggingface", "https://huggingface.co", hf_repo))
        errors = []
        for kind, base, repo in sources:
            if not repo or self._cancel.is_set():
                continue
            self._emit_progress(
                f"正在从 {base} 下载语音识别模型（首次需要，可能几分钟）…"
            )
            try:
                listing = self._list_source_files(kind, base, repo)
                by_name = dict(listing)
                missing = [
                    name
                    for name in STT_REQUIRED_FILES
                    if name in by_name
                    and not os.path.isfile(os.path.join(target, name))
                ]
                for name in sorted(missing):
                    if self._cancel.is_set():
                        raise RuntimeError("下载已取消")
                    self._download_file(
                        self._source_file_url(kind, base, repo, name),
                        os.path.join(target, name),
                        name,
                        expected_size=by_name.get(name, 0),
                    )
                if os.path.isfile(os.path.join(target, "model.bin")):
                    return target
                errors.append(f"{base}：缺少 model.bin")
            except Exception as exc:
                errors.append(f"{base}：{exc}")
                continue
        if self._cancel.is_set():
            raise RuntimeError("模型下载已取消")
        detail = "；".join(errors[-2:]) if errors else "未知错误"
        raise RuntimeError(
            f"语音模型下载失败，已尝试 {len(errors)} 个来源：{detail}。"
            "请检查网络后重试。"
        )

    def _create(self):
        """创建 RealtimeSTT 录音器（应在工作线程中调用）。"""
        from RealtimeSTT import AudioToTextRecorder

        model_path = self._ensure_model()
        return AudioToTextRecorder(
            model=model_path,
            language=self.language or "",
            device="cpu",
            compute_type="int8",
            spinner=False,
            no_log_file=True,
            ensure_sentence_starting_uppercase=False,
            ensure_sentence_ends_with_period=False,
            use_microphone=True,
            post_speech_silence_duration=max(
                0.3, float(self.silence_duration)
            ),
        )

    def start(self):
        """开始录音（首次会自动加载本地模型，可能较慢）。"""
        with self._lock:
            if self._recording:
                return True
            need_create = self._recorder is None
        if need_create:
            try:
                recorder = self._create()
            except Exception as exc:
                self._error = f"语音模型加载失败：{exc}"
                return False
            with self._lock:
                if self._recorder is not None:
                    # 创建期间被关闭/重建，释放新实例
                    try:
                        recorder.shutdown()
                    except Exception:
                        pass
                    return False
                self._recorder = recorder
                self._ready = True
                self._error = ""
        with self._lock:
            if self._recorder is None:
                return False
            recorder = self._recorder
            try:
                recorder.start()
                recorder.set_microphone(True)
            except Exception as exc:
                self._error = f"麦克风启动失败：{exc}"
                return False
            self._recording = True
            return True

    def stop_and_transcribe(self):
        """停止录音并返回识别文本（阻塞直到识别完成）。"""
        with self._lock:
            recorder = self._recorder
            if recorder is None or not self._recording:
                self._error = "还没有开始录音"
                return ""
            self._recording = False
        try:
            recorder.stop()
            return str(recorder.text() or "").strip()
        except Exception as exc:
            self._error = f"语音识别失败：{exc}"
            return ""

    def abort(self):
        """放弃当前录音（例如按住说话时提前松键取消）。"""
        with self._lock:
            recorder = self._recorder
            self._recording = False
        if recorder is not None:
            try:
                recorder.abort()
            except Exception:
                pass

    def shutdown(self):
        with self._lock:
            recorder = self._recorder
            self._recorder = None
            self._ready = False
            self._recording = False
            self._continuous = False
        if recorder is not None:
            try:
                recorder.shutdown()
            except Exception:
                pass

    # ---------- 连续监听（VAD 静音自动断句） ----------

    def start_continuous(self):
        """确保录音器就绪并进入连续监听状态。

        不手动开始录音：首次调用 recognize_utterance() 时库会自动武装
        VAD 循环，之后每说完一句（静音断句）就返回一句识别文本。
        """
        with self._lock:
            need_create = self._recorder is None
        if need_create:
            try:
                recorder = self._create()
            except Exception as exc:
                self._error = f"语音模型加载失败：{exc}"
                return False
            with self._lock:
                if self._recorder is not None:
                    try:
                        recorder.shutdown()
                    except Exception:
                        pass
                    return False
                self._recorder = recorder
                self._ready = True
                self._error = ""
        with self._lock:
            recorder = self._recorder
        if recorder is not None:
            try:
                recorder.set_microphone(True)
            except Exception:
                pass
        self._continuous = True
        return True

    def recognize_utterance(self, timeout=None, cancel=None):
        """等待下一句（VAD 静音断句）并返回识别文本。

        等待期间不打断录音（说话不会被切片切碎）。
        - timeout：最多等多少秒，超时中断并返回 None（通常表示空闲超时）；
        - cancel：可选的停止事件，置位时立即中断并返回 None；
        - 识别出错返回空字符串。
        """
        with self._lock:
            recorder = self._recorder
        if recorder is None:
            return ""

        # 等待上一个等待线程完全退出，避免并发调用 text()
        prev = getattr(self, "_utterance_worker", None)
        if prev is not None and prev.is_alive():
            prev.join(timeout=3.0)

        result = {}
        done = threading.Event()

        def _work():
            try:
                result["text"] = str(recorder.text() or "").strip()
            except Exception as exc:
                result["error"] = str(exc)
            finally:
                done.set()

        def _abort():
            try:
                recorder.abort()
            except Exception:
                pass

        worker = threading.Thread(target=_work, daemon=True)
        self._utterance_worker = worker
        worker.start()
        started = time.monotonic()
        while True:
            if cancel is not None and cancel.is_set():
                threading.Thread(target=_abort, daemon=True).start()
                worker.join(timeout=1.0)
                return None
            if timeout is not None and time.monotonic() - started >= timeout:
                threading.Thread(target=_abort, daemon=True).start()
                worker.join(timeout=1.0)
                return None
            if done.wait(0.2):
                break
        if result.get("error"):
            self._error = f"语音识别失败：{result['error']}"
            return ""
        return result.get("text", "")

    def set_microphone(self, enabled):
        """暂停/恢复收音（TTS 朗读期间静音，避免自听自说）。"""
        with self._lock:
            recorder = self._recorder
        if recorder is not None:
            try:
                recorder.set_microphone(bool(enabled))
            except Exception:
                pass

    def stop_continuous(self):
        with self._lock:
            recorder = self._recorder
            self._continuous = False
            self._recording = False
        if recorder is not None:
            try:
                recorder.set_microphone(False)
            except Exception:
                pass


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


class MemorySettingsDialog(QDialog):
    """记忆设置：开关 + 短期/长期记忆参数 + 语义检索接口。"""

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("记忆设置")
        self.setModal(True)
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.enabled_check = QCheckBox("开启记忆（重启后保留）")
        self.enabled_check.setChecked(bool(cfg.get("enabled", True)))
        self.short_max_spin = QSpinBox()
        self.short_max_spin.setRange(5, 500)
        self.short_max_spin.setValue(int(cfg.get("short_term_max_messages", 40)))
        self.short_hours_spin = QSpinBox()
        self.short_hours_spin.setRange(1, 720)
        self.short_hours_spin.setValue(int(cfg.get("short_term_max_hours", 24)))
        self.extract_check = QCheckBox("对话后自动提炼长期记忆")
        self.extract_check.setChecked(bool(cfg.get("long_term_extract", True)))
        self.long_max_spin = QSpinBox()
        self.long_max_spin.setRange(20, 2000)
        self.long_max_spin.setValue(int(cfg.get("long_term_max_entries", 200)))
        self.use_emb_check = QCheckBox("用 Embedding 语义检索记忆（推荐）")
        self.use_emb_check.setChecked(bool(cfg.get("use_embedding", True)))

        form.addRow("记忆开关", self.enabled_check)
        form.addRow("短期记忆保留条数", self.short_max_spin)
        form.addRow("短期记忆保留时长（小时）", self.short_hours_spin)
        form.addRow("长期记忆提炼", self.extract_check)
        form.addRow("长期记忆上限（条）", self.long_max_spin)
        form.addRow("语义检索", self.use_emb_check)

        embedding = cfg.get("embedding") or {}
        self.embed_base_edit = QLineEdit(str(embedding.get("base_url", "")))
        self.embed_key_edit = QLineEdit(str(embedding.get("api_key", "")))
        self.embed_key_edit.setEchoMode(QLineEdit.Password)
        self.embed_model_edit = QLineEdit(str(embedding.get("model", "")))
        form.addRow("Embedding API 地址", self.embed_base_edit)
        form.addRow("Embedding API Key", self.embed_key_edit)
        form.addRow("Embedding 模型", self.embed_model_edit)
        layout.addLayout(form)

        hint = QLabel(
            "短期记忆：保存最近几小时内的对话，重启后自动恢复。\n"
            "长期记忆：每轮对话后自动提炼重要事实（如你的名字、喜好、约定），"
            "回复前按相关度召回。未配置 Embedding Key 时自动改用关键词匹配。"
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
            "enabled": self.enabled_check.isChecked(),
            "short_term_max_messages": self.short_max_spin.value(),
            "short_term_max_hours": self.short_hours_spin.value(),
            "long_term_extract": self.extract_check.isChecked(),
            "long_term_max_entries": self.long_max_spin.value(),
            "use_embedding": self.use_emb_check.isChecked(),
            "embedding": {
                "base_url": self.embed_base_edit.text().strip().rstrip("/"),
                "api_key": self.embed_key_edit.text().strip(),
                "model": self.embed_model_edit.text().strip(),
            },
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
        self.intensity_spin = QDoubleSpinBox()
        self.intensity_spin.setRange(0.5, 2.0)
        self.intensity_spin.setSingleStep(0.1)
        self.intensity_spin.setDecimals(1)
        self.intensity_spin.setValue(float(cfg.get("motion_intensity", 1.0)))
        self.intensity_spin.setSuffix(" 倍")

        form.addRow("Embedding API 地址", self.embed_base_edit)
        form.addRow("Embedding API Key", self.embed_key_edit)
        form.addRow("Embedding 模型", self.embed_model_edit)
        form.addRow("TTS API 地址", self.tts_base_edit)
        form.addRow("TTS API Key", self.tts_key_edit)
        form.addRow("TTS 模型", self.tts_model_edit)
        form.addRow("TTS 音色", self.voice_combo)
        form.addRow("动作风格", self.style_combo)
        form.addRow("动作幅度（摇晃更明显）", self.intensity_spin)
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
            "motion_intensity": round(self.intensity_spin.value(), 1),
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


class SoullinkActionsDialog(QDialog):
    """选择当前模型的 Soullink 待机动作姿势（扶脸/看手机/记笔记等，按模型自定义）。"""

    def __init__(self, expressions, current, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择待机动作姿势")
        self.setModal(True)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        hint = QLabel(
            "勾选想让桌宠待机时随机做的动作姿势（如扶脸、看手机、记笔记等）。\n"
            "只有模型自带的表情会显示在这里；不勾选则用默认姿势。"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #888;")
        layout.addWidget(hint)

        self.list_widget = QListWidget()
        current = set(current or [])
        for key, info in expressions.items():
            label = (
                info.get("label", key)
                if isinstance(info, dict)
                else key
            )
            item = QListWidgetItem(f"{label}（{key}）")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(
                Qt.Checked if key in current else Qt.Unchecked
            )
            item.setData(Qt.UserRole, key)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        keys = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                key = item.data(Qt.UserRole)
                if key:
                    keys.append(str(key))
        return keys


class SoullinkEmotionActionsDialog(QDialog):
    """按模型自定义“情绪 → 动作姿势”映射（如 累 → 看手机）。"""

    def __init__(self, expressions, current, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择情绪动作")
        self.setModal(True)
        self.setMinimumWidth(420)

        outer = QVBoxLayout(self)
        hint = QLabel(
            "为每个情绪选择对应的动作姿势（如 累 → 看手机、好奇 → 扶脸）。\n"
            "选“默认”则使用生成器自带映射；不选默认姿势时该情绪不触发额外动作。"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #888;")
        outer.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        form = QFormLayout(body)
        self.combos = {}
        options = [("", "默认")] + [
            (
                key,
                (
                    info.get("label", key)
                    if isinstance(info, dict)
                    else key
                ),
            )
            for key, info in expressions.items()
        ]
        for emotion, label in SOULLINK_EMOTIONS:
            combo = QComboBox()
            for key, opt_label in options:
                combo.addItem(opt_label, key)
            idx = combo.findData(str(current.get(emotion) or ""))
            combo.setCurrentIndex(max(0, idx))
            self.combos[emotion] = combo
            form.addRow(label, combo)
        scroll.setWidget(body)
        outer.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

    def values(self):
        return {
            emotion: str(combo.currentData() or "")
            for emotion, combo in self.combos.items()
            if combo.currentData()
        }


class ProactiveSettingsDialog(QDialog):
    """主动发言设置：平均间隔 + 开口概率 + 最短间隔。"""

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("主动发言设置")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 240)
        self.interval_spin.setValue(int(cfg.get("interval_minutes", 15)))
        self.interval_spin.setSuffix(" 分钟")

        self.probability_spin = QSpinBox()
        self.probability_spin.setRange(1, 100)
        self.probability_spin.setValue(int(cfg.get("probability", 70)))
        self.probability_spin.setSuffix(" %")

        self.min_interval_spin = QSpinBox()
        self.min_interval_spin.setRange(1, 60)
        self.min_interval_spin.setValue(int(cfg.get("min_interval_minutes", 3)))
        self.min_interval_spin.setSuffix(" 分钟")

        form.addRow("平均间隔", self.interval_spin)
        form.addRow("开口概率", self.probability_spin)
        form.addRow("最短间隔", self.min_interval_spin)
        layout.addLayout(form)

        hint = QLabel(
            "不是定时说话，而是每过一分钟按概率“掷一次骰子”：间隔越短、概率越高，"
            "说得越勤；间隔越长，时间点越随机。\n"
            "最短间隔用于防止连续说个没完。已配置聊天接口时会用角色人设生成内容，"
            "未配置则使用内置台词。"
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
            "probability": self.probability_spin.value(),
            "min_interval_minutes": self.min_interval_spin.value(),
        }


class VoiceInputSettingsDialog(QDialog):
    """语音输入设置：本地识别模型（RealtimeSTT / faster-whisper）。"""

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("语音输入设置")
        self.setModal(True)
        self.setMinimumWidth(440)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.model_combo = QComboBox()
        model_options = [
            ("tiny（最快，精度一般）", "tiny"),
            ("base（较快）", "base"),
            ("small（推荐，中文效果较好）", "small"),
            ("medium（较慢，更准）", "medium"),
            ("large（最准，最慢）", "large"),
        ]
        current_model = str(cfg.get("model") or "small")
        for label, value in model_options:
            self.model_combo.addItem(label, value)
        idx = self.model_combo.findData(current_model)
        self.model_combo.setCurrentIndex(idx if idx >= 0 else 2)

        self.language_combo = QComboBox()
        language_options = [
            ("中文", "zh"),
            ("English", "en"),
            ("日本語", "ja"),
            ("自动检测", ""),
        ]
        current_lang = str(cfg.get("language") or "zh")
        for label, value in language_options:
            self.language_combo.addItem(label, value)
        idx = self.language_combo.findData(current_lang)
        self.language_combo.setCurrentIndex(idx if idx >= 0 else 0)

        form.addRow("识别模型", self.model_combo)
        form.addRow("识别语言", self.language_combo)
        self.endpoint_edit = QLineEdit(str(cfg.get("hf_endpoint", "")).strip())
        self.endpoint_edit.setPlaceholderText("例如 https://hf-mirror.com（默认留空）")
        form.addRow("模型下载镜像", self.endpoint_edit)

        self.hotkey_check = QCheckBox("启用「按住说话」快捷键")
        self.hotkey_check.setChecked(bool(cfg.get("hotkey_enabled", True)))
        form.addRow("快捷键", self.hotkey_check)

        self.hotkey_combo = QComboBox()
        current_key = str(cfg.get("hotkey_key") or "F8")
        key_options = [
            ("F1", "F1"),
            ("F2", "F2"),
            ("F3", "F3"),
            ("F4", "F4"),
            ("F5", "F5"),
            ("F6", "F6"),
            ("F7", "F7"),
            ("F8（推荐）", "F8"),
            ("F9", "F9"),
            ("F10", "F10"),
            ("F11", "F11"),
            ("F12", "F12"),
            ("Caps Lock", "CapsLock"),
            ("Scroll Lock", "ScrollLock"),
            ("Pause", "Pause"),
        ]
        for label, value in key_options:
            self.hotkey_combo.addItem(label, value)
        idx = self.hotkey_combo.findData(current_key)
        self.hotkey_combo.setCurrentIndex(idx if idx >= 0 else 7)

        self.hotkey_mods_combo = QComboBox()
        current_mods = str(cfg.get("hotkey_modifiers") or "").strip()
        mod_options = [
            ("无", ""),
            ("Ctrl +", "ctrl"),
            ("Shift +", "shift"),
            ("Alt +", "alt"),
            ("Ctrl + Shift +", "ctrl+shift"),
            ("Ctrl + Alt +", "ctrl+alt"),
        ]
        for label, value in mod_options:
            self.hotkey_mods_combo.addItem(label, value)
        idx = self.hotkey_mods_combo.findData(current_mods)
        self.hotkey_mods_combo.setCurrentIndex(idx if idx >= 0 else 0)
        form.addRow("按键", self.hotkey_combo)
        form.addRow("组合键", self.hotkey_mods_combo)
        layout.addLayout(form)

        hint = QLabel(
            "在聊天模式输入框左侧点 🎤 开始录音，再点一次结束并识别成文字填入输入框。\n"
            "开启快捷键后，按住设定按键说话、松开自动识别并发送，不需要再点发送。\n"
            "识别在本机完成（RealtimeSTT + faster-whisper），不经过任何云端 API；\n"
            "首次使用会自动下载所选模型（small 约 460MB），之后离线可用；\n"
            "下载会自动尝试 ModelScope（国内）→ 配置镜像 → hf-mirror.com → "
            "huggingface.co；\n"
            "仍失败时可在“模型下载镜像”手动指定可用地址，或手动把模型放进项目 .cache/stt 目录。"
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
            "model": str(self.model_combo.currentData() or "small"),
            "language": str(self.language_combo.currentData() or ""),
            "hf_endpoint": self.endpoint_edit.text().strip(),
            "hotkey_enabled": self.hotkey_check.isChecked(),
            "hotkey_key": str(self.hotkey_combo.currentData() or "F8"),
            "hotkey_modifiers": str(self.hotkey_mods_combo.currentData() or ""),
        }


class VoiceChatSettingsDialog(QDialog):
    """语音对话设置：唤醒词、监听时长、退出语与 TTS 接口。"""

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("语音对话设置")
        self.setModal(True)
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.enabled_check = QCheckBox("开启语音对话（免按键）")
        self.enabled_check.setChecked(bool(cfg.get("enabled", False)))
        self.wake_edit = QLineEdit(
            "、".join(str(w) for w in (cfg.get("wake_words") or ["yumi"]))
        )
        self.exit_edit = QLineEdit(
            "、".join(str(p) for p in (cfg.get("exit_phrases") or []))
        )
        self.silence_spin = QDoubleSpinBox()
        self.silence_spin.setRange(0.3, 2.0)
        self.silence_spin.setSingleStep(0.1)
        self.silence_spin.setDecimals(1)
        self.silence_spin.setValue(float(cfg.get("silence_seconds", 0.8)))
        self.silence_spin.setSuffix(" 秒")
        self.idle_spin = QSpinBox()
        self.idle_spin.setRange(10, 600)
        self.idle_spin.setValue(int(cfg.get("idle_timeout_seconds", 60)))
        self.idle_spin.setSuffix(" 秒")
        self.turns_spin = QSpinBox()
        self.turns_spin.setRange(5, 200)
        self.turns_spin.setValue(int(cfg.get("max_turns", 50)))
        self.turns_spin.setSuffix(" 轮")

        form.addRow("开启语音对话", self.enabled_check)
        form.addRow("唤醒词（多个用顿号隔开）", self.wake_edit)
        form.addRow("静音多久算说完一句", self.silence_spin)
        form.addRow("空闲多久回到待唤醒", self.idle_spin)
        form.addRow("单次对话最多轮数", self.turns_spin)
        form.addRow("退出语（多个用顿号隔开）", self.exit_edit)
        layout.addLayout(form)

        self.tts_check = QCheckBox("用 TTS 朗读回复")
        self.tts_check.setChecked(bool(cfg.get("tts_enabled", True)))
        form.addRow("语音回复", self.tts_check)

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
        form.addRow("TTS API 地址", self.tts_base_edit)
        form.addRow("TTS API Key", self.tts_key_edit)
        form.addRow("TTS 模型", self.tts_model_edit)
        form.addRow("TTS 音色", self.voice_combo)
        layout.addLayout(form)

        hint = QLabel(
            "开启后无需按键：先对着麦克风说唤醒词（默认 yumi）唤醒，"
            "然后像打电话一样直接对话，每句话说完稍作停顿即可。\n"
            "TTS Key 会自动复用已有百炼 Key；未配置时只显示文字回复。"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #888;")
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _split(self, text):
        return [
            part.strip()
            for part in re.split(r"[、,，/|]", text)
            if part.strip()
        ]

    def values(self):
        return {
            "enabled": self.enabled_check.isChecked(),
            "wake_words": self._split(self.wake_edit.text()),
            "silence_seconds": round(self.silence_spin.value(), 1),
            "idle_timeout_seconds": self.idle_spin.value(),
            "max_turns": self.turns_spin.value(),
            "exit_phrases": self._split(self.exit_edit.text()),
            "tts_enabled": self.tts_check.isChecked(),
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

    @Slot()
    def tts_played(self):
        """Soullink 朗读结束回调（语音对话期间用于恢复麦克风）。"""
        self.window._on_tts_played()

    @Slot()
    def voice_toggle(self):
        self.window.toggle_voice_recording()


class PetWindow(QWidget):
    chat_reply = Signal(str)
    chat_reply_quiet = Signal(str)
    soullink_event = Signal(str)
    soullink_speech = Signal(str)
    soullink_react = Signal(str)
    soullink_js = Signal(str)
    soullink_status = Signal(str)
    voice_text = Signal(str)
    voice_ui = Signal(str)
    voice_status = Signal(str)
    voice_send = Signal(str)
    voice_ptt_down = Signal()
    voice_ptt_up = Signal()
    voice_play = Signal(str)
    voice_shot_requested = Signal()

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
        self.memory_cfg = load_memory_config()
        self.memory = pet_memory.PetMemory(self.memory_cfg, BASE_DIR)
        self.chat_mode = False
        self.chat_reply.connect(self._show_chat_reply)
        self.chat_reply_quiet.connect(self._show_chat_reply_quiet)
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
        self.soullink_classifier_ready = False
        self.soullink_event.connect(self._send_soullink_event)
        self.soullink_speech.connect(self._send_soullink_speech)
        self.soullink_react.connect(self._send_soullink_react)
        self.soullink_js.connect(self._run_js)
        self.soullink_status.connect(self._notify)
        if self.soullink_cfg.get("enabled"):
            QTimer.singleShot(0, self._start_soullink_async)
        self.proactive_cfg = load_proactive_config()
        self.proactive_timer = QTimer(self)
        self.proactive_timer.setInterval(60 * 1000)
        self.proactive_timer.timeout.connect(self._proactive_tick)
        self.last_proactive_ts = 0.0
        self.proactive_busy = False
        if self.proactive_cfg.get("enabled"):
            self.last_proactive_ts = time.monotonic()
            self.proactive_timer.start()
        self.voice_cfg = load_voice_input_config()
        self.voice_recognizer = LocalVoiceRecognizer(self.voice_cfg)
        self.voice_recording = False
        self.voice_busy = False
        self.voice_token = 0
        self.voice_pending_abort = False
        self._ptt_stop_event = threading.Event()
        self._ptt_thread = None
        self._ptt_down = False
        self.voice_recognizer.set_progress_callback(
            lambda text: self.voice_status.emit(text)
        )
        self.voice_text.connect(
            lambda text: self._run_js(
                f"window.setVoiceText({json.dumps(text)})"
            )
        )
        self.voice_ui.connect(self._run_js)
        self.voice_status.connect(self._notify)
        self.voice_send.connect(self._voice_send_text)
        self.voice_ptt_down.connect(self._on_ptt_down)
        self.voice_ptt_up.connect(self._on_ptt_up)
        if self.voice_cfg.get("enabled") and self.voice_cfg.get(
            "hotkey_enabled"
        ):
            self._start_ptt()
        self.voice_chat_cfg = load_voice_chat_config()
        self.voice_recognizer.silence_duration = float(
            self.voice_chat_cfg.get("silence_seconds", 0.8)
        )
        self._tts_client = TtsClient(self.voice_chat_cfg.get("tts") or {})
        self.voice_chat_stop = threading.Event()
        self.voice_chat_thread = None
        self.voice_chat_active = False
        self._play_done = threading.Event()
        self._player = None
        self._audio_output = None
        self.voice_tts_done = threading.Event()
        self._tts_queue = queue.Queue()
        threading.Thread(target=self._tts_queue_worker, daemon=True).start()
        self._shot_result = None
        self._shot_event = threading.Event()
        self.voice_play.connect(self._play_voice_file)
        self.voice_shot_requested.connect(self._on_voice_shot_requested)
        if self.voice_chat_cfg.get("enabled"):
            QTimer.singleShot(
                0, lambda: self.set_voice_chat_enabled(True)
            )
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
        actions = self.model_cfg.get("soullink_actions")
        self._run_js(
            f"window.setSoullinkActions("
            f"{json.dumps(actions or None, ensure_ascii=False)})"
        )
        self._run_js(
            f"window.setActionOverrides("
            f"{json.dumps(model_actions(self.settings, self.model_id), ensure_ascii=False)})"
        )
        self._run_js(f"window.setPetState({json.dumps(self.state)})")
        self._run_js(f"window.setScale({self.scale})")
        self._run_js(
            "window.setVoiceInputEnabled("
            f"{str(bool(self.voice_cfg.get('enabled'))).lower()},"
            f"{json.dumps(self._ptt_label(), ensure_ascii=False)})"
        )
        self._run_js(
            f"window.setMotionIntensity("
            f"{float(self.soullink_cfg.get('motion_intensity', 1.0))})"
        )
        self._run_js(
            f"window.setCropBottom("
            f"{float(self.settings.get('crop_bottom', 0.0))})"
        )
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
        self._run_js("window.setCropBottom(0)")
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
        self.proactive_cfg["enabled"] = False
        save_proactive_config(self.proactive_cfg)
        self.proactive_timer.stop()
        self.voice_cfg["enabled"] = False
        save_voice_input_config(self.voice_cfg)
        self.voice_recording = False
        self._stop_ptt()
        self.voice_token += 1
        self.voice_busy = False
        self.voice_pending_abort = False
        self.voice_recognizer.cancel()
        self.voice_recognizer.shutdown()
        self._run_js("window.setVoiceInputEnabled(false)")
        if self.voice_chat_active:
            self.set_voice_chat_enabled(False)
        self.voice_chat_cfg["enabled"] = False
        save_voice_chat_config(self.voice_chat_cfg)
        self.apply_geometry()
        self.move_to_saved_position()
        self.view.resize(self.width(), self.height())
        self._run_js(f"window.setScale({self.scale})")
        self.set_state("idle")
        self.view.reload()

    def _is_screen_look_request(self, text):
        """判断一句话是否在请求看屏幕（“帮我看看”之类）。"""
        t = str(text or "")
        return any(keyword in t for keyword in SCREEN_LOOK_KEYWORDS)

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
        shot = None
        if self._is_screen_look_request(text):
            if not self.vision_client or not self.vision_client.ready():
                self._run_js(
                    "window.showChatReply("
                    "'（我还没配置视觉接口，暂时看不了屏幕，"
                    "请在菜单的 读屏幕设置 里填写 API 信息）', 6000)"
                )
                return
            try:
                # 截屏必须在界面线程完成（截屏前会先隐藏窗口）
                shot = self._capture_screen_base64()
            except Exception:
                shot = None
        threading.Thread(
            target=self._chat_worker,
            args=(text, shot[0] if shot else None, shot[1] if shot else None),
            daemon=True,
        ).start()

    def _chat_worker(self, text, image_b64=None, mime=None):
        success = False
        screen_desc = None
        try:
            if image_b64:
                try:
                    screen_desc = self.vision_client.describe(
                        image_b64, mime or "image/jpeg"
                    )
                except Exception:
                    screen_desc = None
            try:
                # 短期记忆为主，长期记忆按相关度补充；都没有则按人设回答
                history, memory_note = self.memory.dialogue_context(text)
            except Exception:
                history, memory_note = [], None
            user_content = text
            if screen_desc:
                user_content = (
                    f"{text}\n"
                    f"（补充信息：我刚刚看了你的屏幕，看到的内容是：{screen_desc}。"
                    "请参考屏幕内容自然回答我的问题，不要提及“看了屏幕”或识图。）"
                )
            # 流式生成 + 逐句朗读（出字就开始 TTS）
            reply, speech_sent = self._stream_chat(
                history, user_content, memory_note, text
            )
            success = True
        except Exception as exc:
            reply = f"（连接失败：{exc}）"
        # 先展示回复
        soullink_handled = False
        if self._soullink_usable() and success and not self._is_error_reply(reply):
            try:
                intent = self.soullink_runner.classify(text)
            except Exception:
                intent = None
            if intent:
                # 朗读已由流式逐句完成，这里只做情绪反应
                self.soullink_react.emit(
                    json.dumps(
                        {
                            "reply": reply,
                            "intent": intent,
                        },
                        ensure_ascii=False,
                    )
                )
                soullink_handled = True
        if not soullink_handled:
            self.chat_reply.emit(reply)
        # 等独立 TTS 队列播完；再落盘记忆（提炼放最后不阻塞展示）
        try:
            self._tts_queue.join()
        except Exception:
            pass
        try:
            if success:
                if screen_desc:
                    self.memory.record_line(
                        "user",
                        f"（我看到的屏幕内容：{screen_desc}）",
                        source="screen",
                    )
                self.memory.record_turn(
                    text,
                    reply,
                    source="chat",
                    extract=True,
                    chat_client=self.chat_client,
                )
        except Exception:
            pass

    def _show_chat_reply(self, reply):
        emotion = classify_emotion(reply)
        self._run_js(f"window.chatReact({json.dumps(emotion)})")
        self._run_js(
            f"window.showChatReply({json.dumps(reply)}, 6000)"
        )

    def _show_chat_reply_quiet(self, reply):
        """实时语音对话用：只做情绪表情反应，不显示文字气泡。"""
        emotion = classify_emotion(reply)
        self._run_js(f"window.chatReact({json.dumps(emotion)})")

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

    # ---------- 记忆 ----------

    def set_memory_enabled(self, enabled):
        enabled = bool(enabled)
        self.memory_cfg["enabled"] = enabled
        save_memory_config(self.memory_cfg)
        self.memory.enabled = enabled
        self._notify("记忆功能已开启" if enabled else "记忆功能已关闭")

    def open_memory_settings(self):
        cfg = load_memory_config()
        dialog = MemorySettingsDialog(cfg, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.memory_cfg = dialog.values()
        save_memory_config(self.memory_cfg)
        self.memory = pet_memory.PetMemory(self.memory_cfg, BASE_DIR)
        self._notify("记忆设置已保存")

    def view_memory(self):
        short = self.memory.short_term_entries()
        long_entries = self.memory.long_term_entries()
        lines = [f"【短期记忆】（最近 {len(short)} 条，保留最近 "
                 f"{self.memory_cfg.get('short_term_max_messages', 40)} 条 / "
                 f"{self.memory_cfg.get('short_term_max_hours', 24)} 小时内）"]
        source_label = {
            "chat": "",
            "proactive": "（主动）",
            "screen": "（读屏）",
        }
        for item in short[-30:]:
            ts = item.get("ts", 0)
            stamp = (
                time.strftime("%m-%d %H:%M", time.localtime(ts))
                if ts
                else "--:--"
            )
            speaker = item.get("speaker") or item.get("role")
            label = "你" if speaker == "user" else "yumi"
            tag = source_label.get(item.get("source"), "")
            lines.append(f"{stamp} {label}{tag}：{item.get('content', '')}")
        lines.append("")
        lines.append(f"【长期记忆】（共 {len(long_entries)} 条）")
        for entry in sorted(
            long_entries,
            key=lambda e: (e.get("importance", 1), e.get("updated_at", 0)),
            reverse=True,
        ):
            ts = entry.get("updated_at", 0)
            stamp = time.strftime("%m-%d", time.localtime(ts)) if ts else ""
            imp = entry.get("importance", 3)
            lines.append(
                f"- [重要度{imp}/5] {entry.get('content', '')}（{stamp} 更新）"
            )
        dialog = QDialog(self)
        dialog.setWindowTitle("记忆")
        dialog.setMinimumSize(560, 460)
        dialog_layout = QVBoxLayout(dialog)
        editor = QPlainTextEdit("\n".join(lines))
        editor.setReadOnly(True)
        dialog_layout.addWidget(editor)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)
        dialog.exec()

    def clear_memory(self):
        answer = QMessageBox.question(
            self,
            "清空记忆",
            "确定要清空所有短期记忆和长期记忆吗？\n此操作无法恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        self.memory.clear()
        self._notify("记忆已清空")

    # ---------- 主动发言 ----------

    def set_proactive_enabled(self, enabled):
        enabled = bool(enabled)
        self.proactive_cfg["enabled"] = enabled
        save_proactive_config(self.proactive_cfg)
        if enabled:
            self.last_proactive_ts = time.monotonic()
            self.proactive_timer.start()
            self._notify(
                f"主动发言已开启（平均约 {self.proactive_cfg.get('interval_minutes', 15)} 分钟一次）"
            )
        else:
            self.proactive_timer.stop()
            self._notify("主动发言已关闭")

    def open_proactive_settings(self):
        cfg = load_proactive_config()
        dialog = ProactiveSettingsDialog(cfg, self)
        if dialog.exec() != QDialog.Accepted:
            return
        data = dialog.values()
        self.proactive_cfg.update(data)
        self.proactive_cfg["enabled"] = bool(self.proactive_cfg.get("enabled"))
        save_proactive_config(self.proactive_cfg)
        if self.proactive_cfg.get("enabled"):
            self.last_proactive_ts = time.monotonic()
            if not self.proactive_timer.isActive():
                self.proactive_timer.start()
            self._notify(
                f"主动发言设置已更新（平均约 {self.proactive_cfg.get('interval_minutes')} 分钟一次）"
            )
        else:
            self.proactive_timer.stop()
            self._notify("主动发言已关闭")

    def _proactive_tick(self):
        if not self.proactive_cfg.get("enabled"):
            return
        # 不再受聊天模式限制：聊天框开着也照常主动发言
        if self.proactive_busy or self.screen_read_busy:
            return
        now = time.monotonic()
        elapsed = now - self.last_proactive_ts
        interval = max(1, int(self.proactive_cfg.get("interval_minutes", 15))) * 60
        min_interval = (
            max(1, int(self.proactive_cfg.get("min_interval_minutes", 3))) * 60
        )
        if elapsed < min_interval:
            return
        # 每分钟“掷一次骰子”：概率随经过时间线性增长，时间越久越可能开口，
        # 但具体时机是随机的，不是固定节奏。
        base_p = int(self.proactive_cfg.get("probability", 70)) / 100.0
        p = base_p * min(1.0, elapsed / interval) * (60.0 / interval)
        if random.random() >= p:
            return
        self.last_proactive_ts = now
        self.proactive_busy = True
        threading.Thread(target=self._proactive_worker, daemon=True).start()

    def _proactive_worker(self):
        try:
            reply = None
            if self.chat_client and self.chat_client.ready():
                prompt = (
                    "（主动发言）使用者现在没有在和你说话，也许在忙别的。"
                    "请以你的人物设定，主动说一句简短自然的话（一两句话），"
                    "可以是关心、碎碎念、自言自语或分享此刻的心情。"
                    "不要使用 Markdown，不要提及你是 AI 或模型，不要加引号。"
                )
                try:
                    # 短期记忆为主，长期记忆按相关度补充；都没有则按人设回答
                    history, memory_note = self.memory.dialogue_context(
                        prompt, history_limit=8
                    )
                except Exception:
                    history, memory_note = [], None
                reply = self.chat_client.chat(
                    history,
                    prompt,
                    memory_note=memory_note,
                )
                try:
                    self.memory.record_line(
                        "assistant", reply, source="proactive"
                    )
                except Exception:
                    pass
            if not reply:
                reply = random.choice(PROACTIVE_FALLBACK_LINES)
        except Exception:
            reply = random.choice(PROACTIVE_FALLBACK_LINES)
        finally:
            self.proactive_busy = False
        self._emit_speech(reply)

    def _emit_speech(self, reply):
        """主动发言出口：TTS 朗读时不出气泡、不读括号；仅文本模式时显示气泡。"""
        reply = str(reply or "").strip()
        if not reply:
            return
        tts_ok = bool(
            self.voice_chat_cfg.get("tts_enabled")
            and self._tts_client.ready()
        )
        if self._soullink_usable():
            try:
                intent = self.soullink_runner.classify(reply)
            except Exception:
                intent = None
            if intent:
                # Soullink 朗读：不出气泡，括号内容不读
                self.soullink_event.emit(
                    json.dumps(
                        {
                            "reply": reply,
                            "speak_text": self._tts_text(reply),
                            "intent": intent,
                            "no_bubble": True,
                        },
                        ensure_ascii=False,
                    )
                )
                return
        if tts_ok:
            # 独立 TTS 朗读：不出气泡，括号内容不读
            try:
                self._speak_voice(self._tts_text(reply))
            except Exception:
                # 朗读失败退回文本模式
                self.chat_reply.emit(reply)
            return
        # 纯文本模式：显示气泡（保留原文）
        self.chat_reply.emit(reply)

    # ---------- 语音输入 ----------

    def set_voice_input_enabled(self, enabled):
        enabled = bool(enabled)
        if enabled and self.voice_chat_active:
            # 语音输入与语音对话互斥：开启语音输入时自动关闭语音对话
            self.set_voice_chat_enabled(False)
        self.voice_cfg["enabled"] = enabled
        save_voice_input_config(self.voice_cfg)
        if enabled:
            if self.voice_cfg.get("hotkey_enabled"):
                self._start_ptt()
            self._run_js(
                "window.setVoiceInputEnabled(true,"
                f"{json.dumps(self._ptt_label(), ensure_ascii=False)})"
            )
            self._notify(
                "语音输入已开启：按住 "
                f"{self._ptt_label()} 说话，松开自动发送"
            )
            return
        if not enabled and self.voice_recording:
            self.voice_recording = False
            self._run_js("window.setVoiceRecording(false)")
        self._stop_ptt()
        self.voice_token += 1
        self.voice_busy = False
        self.voice_pending_abort = False
        self.voice_recognizer.cancel()
        self.voice_recognizer.shutdown()
        self._run_js(f"window.setVoiceInputEnabled({str(enabled).lower()})")
        self._notify("语音输入已关闭")

    def _ptt_label(self):
        mods = str(self.voice_cfg.get("hotkey_modifiers") or "").strip()
        key = str(self.voice_cfg.get("hotkey_key") or "F8")
        parts = [p.strip() for p in mods.replace("+", " ").split() if p.strip()]
        if not parts:
            return key
        return " + ".join(p.upper() for p in parts) + " + " + key

    def open_voice_input_settings(self):
        if self.voice_chat_active:
            # 要配置语音输入就先把语音对话关掉，避免两个流程抢麦克风
            self.set_voice_chat_enabled(False)
        cfg = load_voice_input_config()
        dialog = VoiceInputSettingsDialog(cfg, self)
        if dialog.exec() != QDialog.Accepted:
            return
        data = dialog.values()
        if self.voice_recording:
            self.voice_recording = False
            self._run_js("window.setVoiceRecording(false)")
        self._stop_ptt()
        self.voice_token += 1
        self.voice_busy = False
        self.voice_pending_abort = False
        self.voice_recognizer.cancel()
        self.voice_recognizer.shutdown()
        self.voice_cfg.update(data)
        self.voice_cfg["enabled"] = bool(self.voice_cfg.get("enabled"))
        save_voice_input_config(self.voice_cfg)
        self.voice_recognizer = LocalVoiceRecognizer(self.voice_cfg)
        self.voice_recognizer.set_progress_callback(
            lambda text: self.voice_status.emit(text)
        )
        if self.voice_cfg.get("enabled") and self.voice_cfg.get(
            "hotkey_enabled"
        ):
            self._start_ptt()
        self._notify("语音输入设置已更新")

    def toggle_voice_recording(self):
        if self.voice_chat_active:
            self._notify(
                "语音对话正在运行：右键菜单 语音对话 → 关闭，"
                "或直接说「退出对话」"
            )
            return
        if not self.voice_cfg.get("enabled"):
            self._notify("语音输入未开启，请在菜单中开启")
            return
        if self.voice_busy:
            return
        if self.voice_recording:
            self._voice_stop_and_send()
            return
        self._voice_start()

    def _voice_start(self):
        if self.voice_busy or self.voice_recording:
            return
        self.voice_pending_abort = False

        def _begin():
            token = self.voice_token
            if self.voice_recognizer.needs_model():
                self.voice_status.emit(
                    "正在下载语音识别模型（首次需要，可能几分钟）…"
                )
            if not self.voice_recognizer.start():
                self.voice_busy = False
                if token == self.voice_token:
                    self.voice_status.emit(
                        self.voice_recognizer.error() or "语音识别启动失败"
                    )
                return
            if token != self.voice_token:
                self.voice_busy = False
                return
            if self.voice_pending_abort:
                # 按键已松开（或录音被取消），不进入录音状态
                self.voice_pending_abort = False
                self.voice_busy = False
                self.voice_recognizer.abort()
                return
            self.voice_recording = True
            self.voice_busy = False
            self.voice_ui.emit("window.setVoiceRecording(true)")
            if self._ptt_down:
                self.voice_status.emit("🎤 正在录音，松开按键发送")
            else:
                self.voice_status.emit("🎤 正在录音，再点一次结束并发送")

        self.voice_busy = True
        self._notify("正在启动本地语音识别…")
        threading.Thread(target=_begin, daemon=True).start()

    def _voice_stop_and_send(self):
        if self.voice_busy:
            return
        self.voice_recording = False
        self.voice_busy = True
        self._run_js("window.setVoiceRecording(false)")
        self._notify("录音结束，正在识别…")

        def _finish():
            token = self.voice_token
            try:
                text = self.voice_recognizer.stop_and_transcribe()
            finally:
                self.voice_busy = False
            if token != self.voice_token:
                return
            if not text:
                self.voice_status.emit(
                    self.voice_recognizer.error() or "没听清，再说一次？"
                )
                return
            # 填进输入框并直接发送，不需要再点发送按钮
            self.voice_text.emit(text)
            self.voice_send.emit(text)

        threading.Thread(target=_finish, daemon=True).start()

    def _voice_send_text(self, text):
        self._run_js("window.showChatReply('…', 60000)")
        self.handle_chat(text)

    # ---------- 按住说话快捷键 ----------

    def _ptt_key_down(self):
        cfg = self.voice_cfg
        vk = STT_HOTKEY_KEYS.get(str(cfg.get("hotkey_key", "F8")))
        if not vk:
            return False
        get_key = ctypes.windll.user32.GetAsyncKeyState
        if not (get_key(vk) & 0x8000):
            return False
        mods = str(cfg.get("hotkey_modifiers") or "").lower()
        for part in mods.replace("+", " ").split():
            mod_vk = STT_HOTKEY_MODIFIER_VKS.get(part.strip())
            if mod_vk and not (get_key(mod_vk) & 0x8000):
                return False
        return True

    def _start_ptt(self):
        self._stop_ptt()
        self._ptt_stop_event = threading.Event()
        self._ptt_down = False
        self._ptt_thread = threading.Thread(
            target=self._ptt_loop, daemon=True
        )
        self._ptt_thread.start()

    def _stop_ptt(self):
        self._ptt_stop_event.set()
        self._ptt_down = False
        thread = self._ptt_thread
        self._ptt_thread = None
        if thread is not None and thread.is_alive():
            thread.join(timeout=1.0)

    def _ptt_loop(self):
        while not self._ptt_stop_event.is_set():
            pressed = self._ptt_key_down()
            if pressed and not self._ptt_down:
                self._ptt_down = True
                self.voice_ptt_down.emit()
            elif not pressed and self._ptt_down:
                self._ptt_down = False
                self.voice_ptt_up.emit()
            self._ptt_stop_event.wait(0.06)

    def _on_ptt_down(self):
        if self.voice_chat_active:
            return
        if not self.voice_cfg.get("enabled"):
            return
        if not self.chat_mode:
            self._notify("语音输入要在聊天模式下使用，先打开聊天模式吧")
            return
        if self.voice_busy:
            return
        if self.voice_recording:
            return
        self._voice_start()

    def _on_ptt_up(self):
        if not self.voice_cfg.get("enabled"):
            return
        if self.voice_busy:
            # 录音还没真正开始（例如首次加载模型），标记为取消，避免松手后空录
            self.voice_pending_abort = True
            return
        if self.voice_recording:
            self._voice_stop_and_send()

    # ---------- 语音对话（免按键 + 唤醒词） ----------

    def set_voice_chat_enabled(self, enabled):
        enabled = bool(enabled)
        if enabled:
            if self.voice_chat_active:
                return
            old_thread = self.voice_chat_thread
            if old_thread is not None and old_thread.is_alive():
                old_thread.join(timeout=2.0)
            if not self.chat_client or not self.chat_client.ready():
                self.voice_chat_cfg["enabled"] = False
                save_voice_chat_config(self.voice_chat_cfg)
                self._notify("语音对话需要先配置聊天接口")
                return
            # 语音对话自动拉起 Soullink（表情驱动 + TTS 朗读）。
            # 关闭语音对话时不再连带关闭 Soullink：它是打字聊天的朗读底座，
            # 自动关闭会导致 TTS 一起消失。
            if not self.soullink_cfg.get("enabled"):
                self.set_soullink_enabled(True)
            elif not self.soullink_ready:
                # 配置开着但侧车没起来，补一次启动
                self._start_soullink_async()
            self.voice_chat_cfg["enabled"] = True
            save_voice_chat_config(self.voice_chat_cfg)
            self.voice_chat_stop = threading.Event()
            self.voice_chat_thread = threading.Thread(
                target=self._voice_chat_loop, daemon=True
            )
            self.voice_chat_thread.start()
            self.voice_chat_active = True
            wake_words = self.voice_chat_cfg.get("wake_words") or ["yumi"]
            wake = str(wake_words[0]) if wake_words else "yumi"
            self._notify(f"语音对话已开启：说「{wake}」唤醒")
            return
        self.voice_chat_cfg["enabled"] = False
        save_voice_chat_config(self.voice_chat_cfg)
        self.voice_chat_stop.set()
        self.voice_chat_active = False
        try:
            # 中断可能正阻塞在“等下一句”里的监听线程
            self.voice_recognizer.stop_continuous()
        except Exception:
            pass
        thread = self.voice_chat_thread
        self.voice_chat_thread = None
        if thread is not None and thread.is_alive():
            thread.join(timeout=2.0)
        self._notify("语音对话已关闭")

    def open_voice_chat_settings(self):
        cfg = load_voice_chat_config()
        dialog = VoiceChatSettingsDialog(cfg, self)
        if dialog.exec() != QDialog.Accepted:
            return
        was_active = self.voice_chat_active
        if was_active:
            self.set_voice_chat_enabled(False)
        self.voice_chat_cfg = dialog.values()
        self._tts_client = TtsClient(self.voice_chat_cfg.get("tts") or {})
        save_voice_chat_config(self.voice_chat_cfg)
        self.voice_recognizer.silence_duration = float(
            self.voice_chat_cfg.get("silence_seconds", 0.8)
        )
        # 断句时长变更需要重建录音器才生效
        self.voice_recognizer.shutdown()
        if was_active or self.voice_chat_cfg.get("enabled"):
            self.set_voice_chat_enabled(True)
        self._notify("语音对话设置已保存")

    @staticmethod
    def _text_after_wake(text, wake):
        """取唤醒词之后的内容作为第一句话（例如“yumi 帮我看看”里的后半句）。"""
        idx = str(text).lower().find(str(wake).lower())
        if idx < 0:
            return ""
        rest = str(text)[idx + len(str(wake)) :].strip()
        return rest.strip("，。,.！!？?、 ")

    @staticmethod
    def _is_error_reply(reply):
        """判断回复是否是错误提示（这类内容不朗读）。"""
        return str(reply or "").startswith(VOICE_ERROR_PREFIXES)

    @staticmethod
    def _tts_text(reply):
        """朗读文本：去掉所有括号里的内容（动作旁白、语气说明等），只读台词。"""
        text = str(reply or "")
        text = re.sub(r"[（(【\[][^（）()【】\[\]]*[）)】\]]", "", text)
        return re.sub(r"\s+", " ", text).strip()

    def _voice_chat_loop(self):
        recognizer = self.voice_recognizer
        stop = self.voice_chat_stop
        cfg = self.voice_chat_cfg
        wake_words = [
            str(w).strip().lower()
            for w in (cfg.get("wake_words") or ["yumi"])
            if str(w).strip()
        ]
        exit_phrases = [
            str(p).strip()
            for p in (cfg.get("exit_phrases") or ["退出对话"])
            if str(p).strip()
        ]
        idle_timeout = max(5, int(cfg.get("idle_timeout_seconds", 60)))
        max_turns = max(1, int(cfg.get("max_turns", 50)))
        wake_label = wake_words[0] if wake_words else "yumi"

        if recognizer.needs_model():
            self.voice_status.emit(
                "正在下载语音识别模型（首次需要，可能几分钟）…"
            )
        if not recognizer.start_continuous():
            self.voice_status.emit(
                recognizer.error() or "语音识别启动失败，请检查麦克风"
            )
            # 启动失败也要复位状态，避免“关不掉”的假象
            self.voice_chat_active = False
            if self.voice_chat_cfg.get("enabled"):
                self.voice_chat_cfg["enabled"] = False
                try:
                    save_voice_chat_config(self.voice_chat_cfg)
                except Exception:
                    pass
            return

        try:
            while not stop.is_set():
                # ---- 唤醒阶段：等待唤醒词 ----
                self.voice_status.emit(
                    f"👂 待唤醒：说「{wake_label}」开始对话"
                )
                first_turn = None
                hit = None
                while not stop.is_set():
                    # 一直等下一句，说唤醒词即可（关闭时自动中断）
                    text = recognizer.recognize_utterance(cancel=stop)
                    if stop.is_set():
                        break
                    if not text:
                        continue
                    low = text.lower()
                    hit = next(
                        (w for w in wake_words if w in low), None
                    )
                    if hit:
                        remainder = self._text_after_wake(text, hit)
                        if remainder:
                            first_turn = remainder
                        break
                if stop.is_set() or hit is None:
                    break

                # ---- 对话阶段：连续语音聊天 ----
                self.voice_status.emit("🔔 在呢！我在听，直接说～")
                turn = 0
                if first_turn:
                    self.voice_status.emit("💭 正在思考…")
                    try:
                        self._voice_turn(first_turn)
                    except Exception:
                        self.voice_status.emit(
                            "处理这句话时出了点问题，再说一次？"
                        )
                    turn = 1
                while not stop.is_set() and turn < max_turns:
                    text = recognizer.recognize_utterance(
                        timeout=idle_timeout, cancel=stop
                    )
                    if stop.is_set():
                        break
                    if text is None:
                        self.voice_status.emit(
                            "😴 聊得差不多了，有事再叫我～"
                        )
                        break
                    if not text:
                        continue
                    if any(phrase in text for phrase in exit_phrases):
                        self.voice_status.emit("👋 好的，随时叫我～")
                        break
                    self.voice_status.emit("💭 正在思考…")
                    try:
                        self._voice_turn(text)
                    except Exception:
                        self.voice_status.emit(
                            "处理这句话时出了点问题，再说一次？"
                        )
                    turn += 1
        finally:
            try:
                recognizer.stop_continuous()
            except Exception:
                pass
            self.voice_chat_active = False
            if self.voice_chat_cfg.get("enabled"):
                self.voice_chat_cfg["enabled"] = False
                try:
                    save_voice_chat_config(self.voice_chat_cfg)
                except Exception:
                    pass

    def _stream_chat(self, history, user_content, memory_note, text):
        """流式聊天 + 逐句朗读；返回 (完整回复, 是否发出了朗读)。"""
        chunker = _SpeechChunker()
        sent_speech = [0]
        soullink_mode = self._soullink_usable()
        standalone_ok = bool(
            self.voice_chat_cfg.get("tts_enabled")
            and self._tts_client.ready()
        )

        def _push(sentence):
            clean = self._tts_text(sentence)
            if not clean:
                return
            if soullink_mode:
                self.soullink_speech.emit(clean)
            elif standalone_ok:
                self._tts_queue.put(clean)
            sent_speech[0] += 1

        def _on_chunk(chunk):
            for sentence in chunker.feed(chunk):
                _push(sentence)

        stream_ok = True
        try:
            reply = self.chat_client.chat_stream(
                history,
                user_content,
                memory_note=memory_note,
                on_chunk=_on_chunk,
            )
        except Exception:
            stream_ok = False
            # 流式不可用/中途失败：退回一次性请求
            reply = self.chat_client.chat(
                history, user_content, memory_note=memory_note
            )
        if stream_ok or sent_speech[0] == 0:
            for sentence in chunker.flush():
                _push(sentence)
        return reply, sent_speech[0] > 0

    def _voice_turn(self, text):
        """处理一句语音：可选读屏 + 聊天 + 记忆 + 气泡 + TTS 朗读。"""
        _voice_chat_diag(f"turn text={text[:40]!r}")
        screen_desc = None
        user_content = text
        if (
            self._is_screen_look_request(text)
            and self.vision_client
            and self.vision_client.ready()
        ):
            shot = self._request_screen_shot()
            if shot:
                try:
                    screen_desc = self.vision_client.describe(shot[0], shot[1])
                except Exception:
                    screen_desc = None
        if screen_desc:
            user_content = (
                f"{text}\n"
                f"（补充信息：我刚刚看了你的屏幕，看到的内容是：{screen_desc}。"
                "请参考屏幕内容自然回答我的问题，不要提及“看了屏幕”或识图。）"
            )
        try:
            history, memory_note = self.memory.dialogue_context(
                text, history_limit=8
            )
        except Exception:
            history, memory_note = [], None
        success = False
        speech_sent = False
        # 流式朗读期间静音麦克风（防自听自说），读完恢复
        self.voice_recognizer.set_microphone(False)
        self.voice_tts_done.clear()
        try:
            reply, speech_sent = self._stream_chat(
                history, user_content, memory_note, text
            )
            success = True
        except Exception as exc:
            reply = f"（连接失败：{exc}）"
        try:
            if speech_sent:
                if self._soullink_usable():
                    self.voice_tts_done.wait(timeout=90)
                else:
                    self._tts_queue.join()
        finally:
            self.voice_recognizer.set_microphone(True)
        # 结尾情绪反应：朗读已由流式逐句完成，这里只做表情不重复朗读
        if (
            self._soullink_usable()
            and success
            and not self._is_error_reply(reply)
        ):
            try:
                intent = self.soullink_runner.classify(text)
            except Exception:
                intent = None
            if intent:
                self.soullink_react.emit(
                    json.dumps(
                        {
                            "reply": reply,
                            "intent": intent,
                            "no_bubble": True,
                        },
                        ensure_ascii=False,
                    )
                )
            else:
                self.chat_reply_quiet.emit(reply)
        else:
            self.chat_reply_quiet.emit(reply)
        # 记忆落盘（提炼放最后，不阻塞朗读）
        try:
            if success:
                if screen_desc:
                    self.memory.record_line(
                        "user",
                        f"（我看到的屏幕内容：{screen_desc}）",
                        source="screen",
                    )
                self.memory.record_turn(
                    text,
                    reply,
                    source="voice",
                    extract=True,
                    chat_client=self.chat_client,
                )
        except Exception:
            pass

    def _request_screen_shot(self):
        """请求界面线程截屏并等待结果（语音对话线程不能直接操作界面）。"""
        self._shot_result = None
        self._shot_event.clear()
        self.voice_shot_requested.emit()
        self._shot_event.wait(timeout=15)
        return self._shot_result

    def _tts_queue_worker(self):
        """独立 TTS 队列：逐句顺序朗读（Soullink 不可用时兜底）。"""
        while True:
            item = self._tts_queue.get()
            if item is None:
                break
            try:
                self._speak_voice(item)
            except Exception:
                pass
            self._tts_queue.task_done()

    def _on_voice_shot_requested(self):
        try:
            self._shot_result = self._capture_screen_base64()
        except Exception:
            self._shot_result = None
        finally:
            self._shot_event.set()

    def _speak_voice(self, text):
        audio, mime = self._tts_client.synthesize(text)
        if "wav" in mime:
            ext = ".wav"
        elif "mp3" in mime or "mpeg" in mime:
            ext = ".mp3"
        else:
            ext = ".mp3"
        path = os.path.join(
            tempfile.gettempdir(), f"pet_tts_{int(time.time() * 1000)}{ext}"
        )
        try:
            with open(path, "wb") as f:
                f.write(audio)
            self._play_done.clear()
            self.voice_play.emit(path)
            # 等待播放结束，但随时响应关闭语音对话
            stop = self.voice_chat_stop
            while not self._play_done.is_set():
                if stop.is_set():
                    break
                self._play_done.wait(0.3)
        finally:
            try:
                os.remove(path)
            except Exception:
                pass

    def _play_voice_file(self, path):
        from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

        if self._player is None:
            self._audio_output = QAudioOutput(self)
            self._player = QMediaPlayer(self)
            self._player.setAudioOutput(self._audio_output)
            self._player.mediaStatusChanged.connect(self._on_media_status)
        self._player.stop()
        self._player.setSource(QUrl.fromLocalFile(path))
        if self._audio_output is not None:
            self._audio_output.setVolume(85)
        self._player.play()

    def _on_media_status(self, status):
        from PySide6.QtMultimedia import QMediaPlayer

        if status in (
            QMediaPlayer.MediaStatus.EndOfMedia,
            QMediaPlayer.MediaStatus.InvalidMedia,
        ):
            self._play_done.set()

    def _on_tts_played(self):
        """Soullink 朗读结束（由 JS 回调），恢复语音对话的麦克风。"""
        self.voice_tts_done.set()

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
                    try:
                        history, memory_note = self.memory.dialogue_context(
                            prompt, history_limit=8
                        )
                    except Exception:
                        history, memory_note = [], None
                    reply = self.chat_client.chat(
                        history,
                        prompt,
                        memory_note=memory_note,
                    )
                try:
                    self.memory.record_turn(
                        f"（我看到的屏幕内容：{desc}）",
                        reply,
                        source="screen",
                        extract=False,
                    )
                except Exception:
                    pass
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
            "motionIntensity": float(
                self.soullink_cfg.get("motion_intensity", 1.0)
            ),
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
                self.soullink_classifier_ready = False
                self.soullink_cfg["enabled"] = False
                save_soullink_config(self.soullink_cfg)
                self.chat_reply.emit(f"（Soullink 启动失败：{exc}）")
                return
            # 当前模型没有 profile 时自动生成（yumi 已带，其他模型自动扫描生成）
            if not self._soullink_has_profile():
                ok, msg = self.soullink_runner.generate_profile(self.model_id)
                if not ok:
                    self.soullink_ready = False
                    self.soullink_classifier_ready = False
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
                on_ready=self._on_soullink_classifier_ready
            )

        threading.Thread(target=_start, daemon=True).start()

    def _on_soullink_classifier_ready(self):
        self.soullink_classifier_ready = True
        self.soullink_status.emit("Soullink 情绪识别已就绪")

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
            self.soullink_classifier_ready = False
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
        # 动作幅度即时生效（内置引擎与 Soullink 共用）
        self._run_js(
            f"window.setMotionIntensity("
            f"{float(self.soullink_cfg.get('motion_intensity', 1.0))})"
        )
        if self.soullink_ready and self.soullink_runner and self.soullink_runner.ready:
            # 配置变更后重启侧服务使新模型/Key 生效
            self.soullink_runner.stop()
            self.soullink_ready = False
            if self.soullink_cfg.get("enabled"):
                self._start_soullink_async()
            else:
                self._run_js("window.setSoullinkEnabled(false)")

    def open_soullink_actions(self):
        """选择当前模型的 Soullink 待机动作姿势（每个模型可自定义）。"""
        expressions = self.model_cfg.get("expressions") or {}
        if not expressions:
            self._notify("当前模型没有可用的表情/姿势")
            return
        current = self.model_cfg.get("soullink_actions") or []
        dialog = SoullinkActionsDialog(expressions, current, self)
        if dialog.exec() != QDialog.Accepted:
            return
        keys = dialog.values()
        model_path = os.path.join(MODEL_DIR, self.model_id, "model.json")
        try:
            with open(model_path, encoding="utf-8") as f:
                cfg = json.load(f)
            cfg["soullink_actions"] = keys
            with open(model_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            self.model_cfg = load_model_config(self.model_id) or {}
        except Exception:
            pass
        self._run_js(
            f"window.setSoullinkActions("
            f"{json.dumps(keys, ensure_ascii=False)})"
        )
        self._notify(
            f"待机动作已更新：{len(keys)} 个"
            if keys
            else "待机动作已清空（使用默认姿势）"
        )

    def open_soullink_emotion_actions(self):
        """按模型自定义“情绪 → 动作姿势”映射（如 累 → 看手机）。"""
        expressions = self.model_cfg.get("expressions") or {}
        if not expressions:
            self._notify("当前模型没有可用的表情/姿势")
            return
        current = self.model_cfg.get("soullink_emotion_actions") or {}
        dialog = SoullinkEmotionActionsDialog(expressions, current, self)
        if dialog.exec() != QDialog.Accepted:
            return
        actions = dialog.values()
        model_path = os.path.join(MODEL_DIR, self.model_id, "model.json")
        try:
            with open(model_path, encoding="utf-8") as f:
                cfg = json.load(f)
            cfg["soullink_emotion_actions"] = actions
            with open(model_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            self.model_cfg = load_model_config(self.model_id) or {}
        except Exception:
            pass
        # 同步写入 profile 的 expressionMap，并让 SDK 重新加载
        profile_path = os.path.join(
            MODEL_DIR, self.model_id, "soullink.profile.json"
        )
        try:
            with open(profile_path, encoding="utf-8") as f:
                profile = json.load(f)
            expr_map = profile.get("expressionMap") or {}
            for emotion, key in actions.items():
                expr_map[emotion] = key
            profile["expressionMap"] = expr_map
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            if self.soullink_cfg.get("enabled"):
                self.soullink_js.emit("window.soullinkRestart()")
        except Exception:
            pass
        self._notify("情绪动作已更新")

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

    def _send_soullink_speech(self, text):
        """流式朗读片段：交给前端朗读队列逐句播放。"""
        self._run_js(
            f"window.soullinkSpeak({json.dumps(text, ensure_ascii=False)})"
        )

    def _send_soullink_react(self, payload_json):
        """流式结束后的情绪反应（只做表情，不再重复朗读）。"""
        self._run_js(f"window.soullinkReactOnly({payload_json})")

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
                        expr_label = info.get("label", key)
                    else:
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
            memory_menu = _new_menu("记忆", menu)
            menu.addMenu(memory_menu)
            memory_toggle = QAction("开启记忆", self, checkable=True)
            memory_toggle.setChecked(bool(self.memory_cfg.get("enabled")))
            memory_toggle.triggered.connect(self.set_memory_enabled)
            memory_menu.addAction(memory_toggle)
            memory_menu.addAction(
                QAction(
                    "记忆设置…",
                    self,
                    triggered=self.open_memory_settings,
                )
            )
            memory_menu.addAction(
                QAction("查看记忆…", self, triggered=self.view_memory)
            )
            memory_menu.addAction(
                QAction("清空记忆", self, triggered=self.clear_memory)
            )
            proactive_menu = _new_menu("主动发言", menu)
            menu.addMenu(proactive_menu)
            proactive_toggle = QAction(
                "开启主动发言", self, checkable=True
            )
            proactive_toggle.setChecked(
                bool(self.proactive_cfg.get("enabled"))
            )
            proactive_toggle.triggered.connect(self.set_proactive_enabled)
            proactive_menu.addAction(proactive_toggle)
            proactive_menu.addAction(
                QAction(
                    "主动发言设置…",
                    self,
                    triggered=self.open_proactive_settings,
                )
            )
            voice_menu = _new_menu("语音输入", menu)
            menu.addMenu(voice_menu)
            voice_toggle_action = QAction(
                "开启语音输入", self, checkable=True
            )
            voice_toggle_action.setChecked(bool(self.voice_cfg.get("enabled")))
            voice_toggle_action.triggered.connect(self.set_voice_input_enabled)
            voice_menu.addAction(voice_toggle_action)
            voice_menu.addAction(
                QAction(
                    "语音输入设置…",
                    self,
                    triggered=self.open_voice_input_settings,
                )
            )
            voice_chat_menu = _new_menu("语音对话", menu)
            menu.addMenu(voice_chat_menu)
            voice_chat_toggle = QAction(
                "开启语音对话（免按键）", self, checkable=True
            )
            voice_chat_toggle.setChecked(
                bool(self.voice_chat_cfg.get("enabled"))
            )
            voice_chat_toggle.triggered.connect(self.set_voice_chat_enabled)
            voice_chat_menu.addAction(voice_chat_toggle)
            voice_chat_menu.addAction(
                QAction(
                    "语音对话设置…",
                    self,
                    triggered=self.open_voice_chat_settings,
                )
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
            soullink_menu.addAction(
                QAction(
                    "选择待机动作姿势…",
                    self,
                    triggered=self.open_soullink_actions,
                )
            )
            soullink_menu.addAction(
                QAction(
                    "选择情绪动作…",
                    self,
                    triggered=self.open_soullink_emotion_actions,
                )
            )
            menu.addSeparator()
            lock_action = QAction(
                "解锁拖动" if self.locked else "锁定拖动", self
            )
            lock_action.triggered.connect(self.toggle_lock)
            menu.addAction(lock_action)
            menu.addSeparator()
            crop_menu = _new_menu("裁切（从脚底往上）", menu)
            menu.addMenu(crop_menu)
            crop_action = QWidgetAction(crop_menu)
            crop_widget = QWidget()
            crop_layout = QVBoxLayout(crop_widget)
            crop_layout.setContentsMargins(12, 6, 16, 6)
            crop_label = QLabel()
            crop_slider = QSlider(Qt.Horizontal)
            crop_slider.setRange(0, 90)
            crop_slider.setValue(
                int(round(float(self.settings.get("crop_bottom", 0.0)) * 100))
            )
            crop_label.setText(f"裁切底部 {crop_slider.value()}%")
            crop_label.setStyleSheet("color: #c4b5fd; font-size: 12px;")
            crop_widget.setStyleSheet("background: transparent;")
            crop_layout.addWidget(crop_label)
            crop_layout.addWidget(crop_slider)
            crop_action.setDefaultWidget(crop_widget)
            crop_menu.addAction(crop_action)

            def _apply_crop(_value):
                pct = crop_slider.value()
                crop_label.setText(f"裁切底部 {pct}%")
                self.settings["crop_bottom"] = round(pct / 100.0, 2)
                save_settings(self.settings)
                self._run_js(f"window.setCropBottom({pct / 100.0})")

            crop_slider.valueChanged.connect(_apply_crop)
            crop_menu.addAction(
                QAction(
                    "重置裁切（0%）",
                    self,
                    triggered=lambda: crop_slider.setValue(0),
                )
            )
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
        try:
            self.voice_token += 1
            self._stop_ptt()
            self.voice_recognizer.cancel()
            self.voice_recognizer.shutdown()
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
