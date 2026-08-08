# Codex Live2D 桌宠

> **v4.0.0**：流式 TTS（DeepSeek 边出字边朗读）。完整历史见 [CHANGELOG.md](CHANGELOG.md)（v3.0.0 为本地记忆、免按键语音对话、可自定义的 Soullink 动作等）。

一个「**记得住、听得懂、看得见**」的 Live2D 桌面伙伴：用语音喊一声就醒、回复边生成边朗读，记得你说过的话，说"帮我看看"它会真的看你的屏幕，还能感知 Codex 的运行状态。内置 **yumi** 模型，支持随时切换或导入其他 Live2D 模型。

![桌宠示意图](docs/preview.png)

## ✨ 核心亮点

- **免按键语音对话**：说唤醒词（默认「yumi」）唤醒，像打电话一样连续对话，VAD 静音自动断句，不用按任何键
- **流式 TTS**：DeepSeek 边出字边逐句朗读，不用等整段回复生成完才开口，延迟大幅降低
- **本地记忆**：短期对话 + 长期事实全部存在本机，重启不丢，回复前自动想起相关的事
- **读屏幕**：定时观察，或聊天里说「帮我看看」立刻看屏幕，结合画面内容回答
- **Soullink 情绪引擎**：Embedding 情绪识别 + 表情/动作/TTS 全套，动作可按模型自定义
- **Codex 状态联动**：感知思考/执行/完成/故障，自动切换动作与表情

---

## 🗂️ 功能总览

### 🗣️ 聊天与记忆

- **流式聊天 + 逐句朗读**：回复边生成边朗读（Soullink 朗读队列逐句播放，未启用时独立 TTS 兜底）；朗读自动去掉「（动作旁白）」只读台词
- **本地记忆**（默认开启）：短期记忆（最近 24 小时对话流水）+ 长期记忆（每轮自动提炼事实、去重合并、按重要度保留上限），右键 →「记忆」可查看/清空
- **记忆召回**：回复前按话题召回最相关的长期记忆（Embedding 语义检索，未配 Key 自动降级关键词）；短期记忆为主、长期按相关度补充、都没有则按人设回答
- **情绪反应**：开心→挥手爱心眼、难过→垂泪、生气→黑脸、思考→托腮等
- **实时语音对话不弹气泡**，打字聊天气泡照常

### 🎤 语音

- **语音对话（免按键 + 唤醒词）**：说「yumi」唤醒 → 连续对话 → 流式朗读 → 空闲超时或说「拜拜/退出对话」回到待唤醒
- **VAD 静音自动断句**：说完一句停顿片刻（默认 0.8 秒）自动识别，长句不被截断
- **语音输入（按住说话）**：快捷键按住说话、松开自动发送，作为免按键之外的备选
- 朗读期间自动静音麦克风防回声；TTS 音色、唤醒词、退出语均可配置

### 👀 读屏幕

- 定时（默认 10 分钟）截屏识别画面，让桌宠以人设口吻回应
- 聊天里说「帮我看看」「看看屏幕」「你能看到我的屏幕吗」等话，自动读一次屏幕，并把画面内容和你的问题一起发给模型回答
- 看到的内容会记入短期记忆；视觉接口在「读屏幕设置…」里配置

### 🎭 Soullink 情绪引擎（可选开关）

- **Embedding 情绪识别**（内置 1,400 条中文语料 + Top-K 投票，首次启用约 1 分钟初始化，之后缓存）
- **表情/动作/TTS 一体**：连续 VAD 情绪 + FACS 表情 + 待机动作 + 说话口型 + 朗读
- **动作幅度可调**（0.5x~2x），待机左右摇晃更明显
- **手部动作姿势**：好奇/疑惑时扶脸思考、累的时候看手机；待机还会随机做扶脸/看手机/记笔记/前倾等小动作
- **每个模型可自定义**：右键 →「选择待机动作姿势…」勾选待机小动作；「选择情绪动作…」为 16 种情绪指定姿势；重新生成 profile 不丢失
- **任意模型可用**：没有参数映射时自动扫描生成 `soullink.profile.json`

### 🖼️ 模型与显示

- **多模型**：切换、导入（zip/文件夹，自动识别表情/姿势/动作）、删除
- **状态动作自定义**：待机/思考中/执行中/完成/故障/点击互动可分别指定动作、姿势或表情
- **裁切显示**：右键 →「裁切（从脚底往上）」按百分比从脚底裁切（如 50% 只显示胸部以上），窗口自动适配
- **动作幅度**、放大缩小、锁定拖动、透明置顶无边框窗口，拖不丢

---

## 📦 环境要求

- Windows 10/11
- Python 3.10+（建议 3.12）
- 网络（首次安装依赖需要；聊天/朗读需要可用的 OpenAI 兼容接口和百炼 TTS）
- Soullink 情绪引擎需要 Node.js 18+（`node --version` 可查，本项目在 Node 24 下验证）

## 🚀 快速开始

### 1. 安装依赖（项目本地虚拟环境）

```powershell
cd codex-live2d
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install PySide6
.\.venv\Scripts\python.exe -m pip install "RealtimeSTT[faster-whisper]" silero-vad
```

Soullink 情绪引擎还需要安装一次 npm 依赖（不装也能用原有关键词模式）：

```powershell
cd tools/soullink
npm install
```

### 2. 配置聊天接口

复制 `config.example.json` 为 `config.json`，填入你的接口信息；也可以在桌宠右键菜单 →「聊天设置…」里直接填写，效果相同：

```json
{
  "chat": {
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "你的 API Key",
    "model": "deepseek-v4-flash",
    "persona": "角色人设……"
  }
}
```

`config.json` 已被 `.gitignore` 忽略，不会提交到仓库（防止 Key 泄露）。

### 3. 可选：读屏幕、记忆与 Soullink

**读屏幕**（也可在右键 →「读屏幕设置…」填写；本机已有 `DASHSCOPE_API_KEY` 时视觉 Key 自动复用）：

```json
{
  "screen_read": {
    "enabled": false,
    "interval_minutes": 10,
    "vision": {
      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "api_key": "你的视觉模型 API Key",
      "model": "qwen-vl-max",
      "prompt": "请仔细看这张屏幕截图，用中文简要描述屏幕上正在显示的内容……"
    }
  }
}
```

**记忆**默认开启，数据全部保存在本地 `memory/` 目录（不入库）。可在「记忆设置…」里调整：

```json
{
  "memory": {
    "enabled": true,
    "short_term_max_messages": 40,
    "short_term_max_hours": 24,
    "long_term_extract": true,
    "long_term_max_entries": 200,
    "recall_top_k": 5,
    "use_embedding": true,
    "embedding": {
      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "api_key": "",
      "model": "text-embedding-v3"
    }
  }
}
```

- 短期记忆：保留最近 `short_term_max_messages` 条、`short_term_max_hours` 小时内的对话
- 长期记忆：每轮对话后自动提炼事实并合并去重，超过上限自动淘汰重要度低的旧记忆
- 语义检索：开启 `use_embedding` 后按话题召回；未填写 Embedding Key 时自动降级为本地关键词匹配

**Soullink 情绪引擎**：安装 npm 依赖后，右键 →「Soullink 情绪引擎」→「开启」即可；Embedding 和 TTS 的 Key 会自动复用本机百炼 Key（也可在「Soullink 设置…」单独填写）。

### 4. 启动

双击 `启动桌宠.bat`，或运行：

```powershell
.\.venv\Scripts\pythonw.exe main.py
```

出问题时用 `调试运行.bat`（带控制台）查看报错。

## 🖱️ 操作说明

| 操作 | 效果 |
| --- | --- |
| 单击小人 | 挥手互动（“嗨！”气泡） |
| 按住拖动 | 移动位置（右键可锁定/解锁拖动） |
| 右键 → 聊天模式 / 聊天设置 | 打开底部输入框对话 / 配置 API、人设 |
| 右键 → 语音对话 → 开启 | 免按键语音聊天：说唤醒词（默认 yumi）唤醒，回复流式朗读 |
| 右键 → 语音对话 → 设置 | 配置唤醒词、静音断句时长、退出语、TTS 音色 |
| 右键 → 记忆 | 开关、设置、查看、清空本地记忆 |
| 右键 → 读屏幕 | 定时读屏幕、立即读一次、读屏幕设置 |
| 右键 → Soullink 情绪引擎 | 开启/设置、生成 profile、自定义待机动作与情绪动作 |
| 右键 → 状态动作 | 为各状态指定动作/姿势/表情 |
| 右键 → 动作 / 表情 | 手动播放预设动作 / 切换表情 |
| 右键 → 模型 | 切换、导入、删除模型 |
| 右键 → 裁切（从脚底往上） | 按百分比裁掉脚部，只保留上半身/头部，窗口自动适配 |
| 右键 → 放大 / 缩小 | 调整角色大小 |
| 右键 → 恢复默认设置和模型 | 重置为 yumi、默认大小和位置 |
| 右键 → 退出 | 关闭桌宠 |

聊天模式下输入框左侧的「←」按钮可返回 Codex 模式。

## ⚙️ 配置文件

- `config.json`：聊天（`chat`）、记忆（`memory`）、读屏幕（`screen_read`）、语音对话（`voice_chat`）、Soullink（`soullink`）等配置，本地生成、不入库
- `settings.json`：窗口位置、大小、锁定状态、当前模型、裁切比例，运行时会自动保存
- `model/<id>/model.json`：每个模型的入口、表情、动作、状态绑定声明（含 `soullink_actions`、`soullink_emotion_actions` 自定义字段）
- `memory/`：本地记忆数据（`short_term.jsonl` + `long_term.json`），已加入 `.gitignore`

## 📁 项目结构

```
├── main.py                  # 桌宠主程序（PySide6 + QtWebEngine）
├── pet_memory.py            # 本地记忆模块（短期记忆 + 长期记忆 + 语义检索）
├── codex_monitor.py         # 读取 Codex 实时日志，识别思考/执行/完成/故障
├── soullink_runner.py       # Soullink SDK 本地侧服务管理（启动/停止 Node 服务）
├── codex_pet_launcher.pyw   # 可选：随 Codex/桌面版启动的守护脚本
├── 启动桌宠.bat / 调试运行.bat
├── config.example.json / settings.example.json  # 配置模板
├── memory/                  # 本地记忆数据（运行时自动生成，不入库）
├── model/
│   └── yumi/                # yumi 模型 + model.json + soullink.profile.json（其余模型自行导入）
├── tools/soullink/          # Soullink SDK 集成（Node 侧服务、profile 生成、浏览器桥接、npm 依赖）
├── tools/web/
│   ├── live.html / live.js  # 实时渲染页面（动作、表情、眼神追踪、聊天 UI）
│   └── lib/                 # PixiJS / Live2D 运行时库 + soullink-emotion.esm.js
└── docs/                    # 文档与截图
```

## ❓ 常见问题

**启动后看不见小人？**

- 确认只启动了一个实例（重复启动可能互相遮挡）；右键多余的实例选择「退出」
- 桌宠不会掉出屏幕（已做边界限制），但可能被全屏应用盖住，可先最小化其他窗口
- 查看 `pet_error.log`（有报错时自动生成），把内容反馈给开发者

**聊天没反应 / 提示连接失败？**

- 在「聊天设置」里确认 `api_key` 已填写、`base_url` 和 `model` 与你使用的服务商一致
- 本项目默认模型是 `deepseek-v4-flash`，如果服务商不支持，可在「聊天设置」里改成它实际提供的模型名

**语音对话没声音？**

- 确认「Soullink 情绪引擎」已开启且「情绪识别已就绪」（未就绪时会自动用独立 TTS 兜底）
- 确认网络能访问百炼（`dashscope.aliyuncs.com`），TTS 和记忆 Embedding 都走百炼接口
- 朗读会自动去掉「（旁白）」只读台词；实时语音对话不显示文字气泡属正常设计

**yumi 会记得之前聊过什么吗？**

- 默认开启本地记忆：短期记忆保存最近 24 小时（可调）内的对话，长期记忆每轮对话后自动提炼重要事实，重启桌宠后都还在
- 所有记忆只存在本机 `memory/` 目录，可在右键 →「记忆」→「查看记忆 / 清空记忆」里管理

**为什么有时候表情/动作不明显？**

- 情绪识别只对「强烈的情绪词」生效，普通回复会做轻点头的小反应
- 可在「Soullink 设置 → 动作幅度」里调大；内置引擎的幅度在 `tools/web/live.js` 的 `applyMotion()` 中调整

**如何添加/更换模型？**

- 最省事：右键 →「模型」→「导入模型（zip / 文件夹）」，程序自动识别表情（星星眼/黑脸/脸红等）、姿势（扶脸/记笔记/看手机等）和动作，生成配置并切换
- 也可以手动把模型放进 `model/<名字>/`，写一份 `model.json`（参考 `model/yumi/model.json`）声明 `model3`、`expressions`、`motions`、`presets`、`effects`、`chat`、`crop` 等字段
- 当前模型会自动保存，切换模型互不影响；「恢复默认设置和模型」会重置为 yumi

## ⚠️ 声明

- 本项目仅用于学习交流；Live2D 模型文件版权归原作者所有
- 默认模型 yumi 来源：B 站视频 [BV1LM41137vK](https://www.bilibili.com/video/BV1LM41137vK)
- 依赖的 PixiJS、pixi-live2d-display 均为开源库，Live2D Cubism Core 遵循官方 SDK 许可
