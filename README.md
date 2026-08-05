# Codex Live2D 桌宠（yumi）

一个基于 Live2D 模型 **yumi** 的透明桌面宠物：实时渲染、眼神跟随鼠标，并且能感知 Codex 的运行状态自动切换动作和表情；还内置了角色聊天模式，可以像朋友一样和 yumi 对话。

![桌宠示意图](docs/preview.png)

> 截图占位：可自行放置预览图到 `docs/preview.png`。

## ✨ 功能

- **实时 Live2D 渲染**：QtWebEngine + pixi-live2d-display，无预渲染帧，角色一直在呼吸、摇摆
- **眼神/头部跟随鼠标**：光标在屏幕任意位置，角色都会看向它
- **Codex 状态联动**：读取 Codex 实时日志，自动切换状态
  - 待机 → 爱心眼 + 待机摇摆
  - 思考中 → 星星眼 + 托腮思考
  - 执行命令 → 蚊香眼 + 俯身忙碌
  - 完成 → 一次挥手
  - 故障 → 黑脸
  - 状态切换带柔和过渡动画，头顶气泡提示（思考中…/执行命令…/完成！/故障！）
- **聊天模式**：底部输入框和 yumi 对话
  - 回复以气泡漂浮在角色头顶
  - 根据回复情绪自动摆出动作和表情（开心→挥手爱心眼、难过→垂泪、生气→黑脸颤抖、思考→托腮、惊讶→后仰、中性→轻点头）
- **右键菜单**：表情切换、放松、聊天模式、聊天设置、锁定拖动、放大缩小、退出
- **透明置顶无边框窗口**，不挡工作区，窗口大小自适应角色，拖不丢

## 📦 环境要求

- Windows 10/11
- Python 3.10+（建议 3.12）
- 网络（首次安装依赖需要；聊天功能需要可用的 OpenAI 兼容接口）

## 🚀 快速开始

### 1. 安装依赖（项目本地虚拟环境）

```powershell
cd codex-live2d
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install PySide6
```

### 2. 配置聊天接口（可选，不配置也能用 Codex 状态模式）

复制 `config.example.json` 为 `config.json`，填入你的接口信息：

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

`config.json` 已被 `.gitignore` 忽略，不会提交到仓库（防止 Key 泄露）。也可以在桌宠右键菜单 →「聊天设置…」里直接填写，效果相同。

### 3. 启动

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
| 右键 | 打开菜单 |
| 右键 → 表情 | 切换 17 个模型自带表情 |
| 右键 → 聊天模式 | 打开底部输入框，开始和 yumi 对话 |
| 右键 → 聊天设置 | 配置聊天 API 地址 / Key / 模型 / 人设 |
| 右键 → 放大 / 缩小 | 调整角色大小 |
| 右键 → 退出 | 关闭桌宠 |

聊天模式下输入框左侧的「←」按钮可返回 Codex 模式。

## ⚙️ 配置文件

- `config.json`：聊天接口配置（`base_url`、`api_key`、`model`、`persona`），本地生成、不入库
- `settings.json`：窗口位置、大小、锁定状态，运行时会自动保存
- 模型文件位于 `model/yumi/`，程序只读不修改

## 📁 项目结构

```
├── main.py                  # 桌宠主程序（PySide6 + QtWebEngine）
├── codex_monitor.py         # 读取 Codex 实时日志，识别思考/执行/完成/故障
├── codex_pet_launcher.pyw   # 可选：随 Codex/桌面版启动的守护脚本
├── 启动桌宠.bat / 调试运行.bat
├── config.example.json      # 聊天配置模板（复制为 config.json 填写）
├── settings.example.json    # 窗口配置模板
├── model/yumi/              # Live2D 模型源文件
├── tools/web/
│   ├── live.html / live.js  # 实时渲染页面（动作、表情、眼神追踪、聊天 UI）
│   └── lib/                 # PixiJS / Live2D 运行时库
└── docs/                    # 文档与截图
```

## ❓ 常见问题

**启动后看不见小人？**

- 确认只启动了一个实例（重复启动可能互相遮挡）；右键多余的实例选择「退出」
- 桌宠不会掉出屏幕（已做边界限制），但可能被全屏应用盖住，可先最小化其他窗口
- 查看 `pet_error.log`（有报错时自动生成），把内容反馈给开发者

**聊天没反应 / 提示连接失败？**

- 在「聊天设置」里确认 `api_key` 已填写、`base_url` 和 `model` 与你使用的服务商一致
- 模型名按服务商实际提供填写（例如 DeepSeek 官方是 `deepseek-chat`）

**为什么有时候表情/动作不明显？**

- 情绪识别只对「强烈的情绪词」生效，普通回复会做轻点头的小反应
- 状态动作幅度可在 `tools/web/live.js` 的 `applyMotion()` 中调整数值

## ⚠️ 声明

- 本项目仅用于学习交流；Live2D 模型文件版权归原作者所有
- 依赖的 PixiJS、pixi-live2d-display 均为开源库，Live2D Cubism Core 遵循官方 SDK 许可
