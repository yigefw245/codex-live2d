# 更新日志

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
