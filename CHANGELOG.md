# 更新日志

## v2.0.3（2026-08-06）

### ✨ 优化

- **右键菜单美化**：从系统原生样式改为暗色玻璃质感——圆角、半透明深色背景、紫罗兰渐变高亮、柔和分隔线，顶部显示当前模型名；主菜单与所有子菜单统一风格

## v2.0.2（2026-08-06）

### ✨ 新功能

- **Soullink 情绪引擎现在能驱动原生表情了**：此前 pixi-live2d-display 只从 `model3.json` 的 `FileReferences.Expressions` 读取表情，而标准模型文件把它们放在顶层，导致 SDK 的原生表情从未加载成功
  - 悠小喵：注册了 星星眼 / 晕晕眼 / 黑脸 / 流泪 / 哭哭 / 脸红 / 飞头 等 12 个表情，情绪识别到 happy / sad / angry / surprised / shy / confused 等会直接切换对应脸
  - yumi：同样补上 `FileReferences.Expressions`，爱心眼 / 星星眼 / 眼泪 / 黑脸 / 蚊香眼 等原生表情生效
- **导入模型自动注册 Expressions**：导入新模型时，如果模型目录里有 `.exp3.json` 表情文件但 `model3.json` 未声明，会自动补注册（含星星眼的 happy 别名），情绪引擎开箱即用
- **profile 生成器自动补全情绪别名**：teary / anxiety / tired / concerned 归入 tear，anger 归入 angry，affectionate 归入 happy，curious 归入 star，confused 归入 surprised

## v2.0.1（2026-08-06）

### 🔧 修复

- **Soullink 模式下恢复鼠标追踪**：开启情绪引擎后角色不再跟随鼠标，现在眼神/头部/身体会继续跟随光标（幅度减半，避免完全盖掉 SDK 的情绪姿态）
- **修复回复时"只动嘴、身体没反应"**：SDK 在说话（SPEAKING）状态下会主动压低情绪层权重并关闭空闲手势，导致回复时身体几乎不动。通过提高参数/身体增益（parameterGain 2.2 / bodyMotionGain 2.8），情绪驱动的头部偏转、微笑、眼神等姿态在说话时也能清晰可见

## v2.0.0（2026-08-06）

### ✨ 新功能

- **读屏幕**：右键菜单「读屏幕」可开关定时观察屏幕，设置读取频率（默认 10 分钟一次），调用视觉大模型识别画面内容，再交给聊天模型按人设生成一句回应
- **Soullink 情绪引擎（可选开关）**：接入 [Soullink Emotion SDK](https://github.com/nanlingyin/soullink-emotion-sdk)
  - 情绪识别改用 **Embedding 分类**（不经过 LLM 生成文本）：内置 1,400 条中文语料、Top-K 投票、精确命中、LRU 查询缓存与规则降级，输出连续 VAD 情绪
  - 动作与表情改由 Soullink 引擎驱动（连续 VAD + FACS 表情 + 待机动作 + 说话口型），支持 natural / lively / calm / shy 动作风格
  - 聊天回复自动用 TTS 朗读（默认百炼 Qwen-TTS / Cherry 音色，可配置）
  - 该功能作为开关使用：**关闭时完全恢复原有关键词情绪识别和动作系统**
- **Soullink 与 Codex 联动互斥**：开启 Soullink 期间自动禁用 Codex 状态动作匹配（思考/执行/完成/故障不再抢动作），关闭后立即恢复
- **任意模型自动生成 profile**：开启 Soullink 时若当前模型没有 `soullink.profile.json`，自动扫描模型生成参数映射；导入新模型后也会自动补生成；菜单可手动「生成/更新当前模型 profile…」

### 🔧 修复

- 修复 `codex_monitor.py` 中时间戳解析函数实现错位导致的死代码问题（`_iso_to_epoch` 之前永远返回 `None`）
- 移除调试遗留的 `pet_diag.log` / `pet_state_ack.log` 写入逻辑与日志文件
- 移除废弃的 `pets/yumi/manifest.json` 读取路径（旧架构遗留，实际从未命中）

### 🧹 整理

- 清理 `_expr_classify` 中重复的关键词
- 补充 Soullink 集成所需文件：`soullink_runner.py`、`tools/soullink/`（Node 侧服务 + profile 生成 + 浏览器桥接）、`tools/web/lib/soullink-emotion.esm.js`（构建产物）
