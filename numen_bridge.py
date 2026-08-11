# -*- coding: utf-8 -*-
"""Numen《我的世界》模组桥接：MCP 客户端 + LLM 工具调用决策循环。

Numen 模组会在游戏里开一个 MCP 服务（默认 http://127.0.0.1:8765/mcp），
把“假玩家”的动作（移动 / 挖矿 / 建造 / 合成 / 战斗 / 感知）暴露成一组工具。
这个模块负责：
1. 用极简 HTTP JSON-RPC 客户端连上 Numen；
2. 把 Numen 的工具清单转换成 OpenAI 风格的 function schema；
3. 驱动桌宠的聊天大脑（OpenAI 兼容接口）跑
   “感知 -> 决定 -> 执行 -> 汇报”的工具调用循环，最终吐出一段旁白文字。
"""

import json
import re
import threading
import time
import urllib.error
import urllib.request

MCP_PROTOCOL_VERSION = "2025-06-18"

PLANNER_SYSTEM = (
    "你是 Yumi 的规划层，负责根据长期目标和当前状态，决定下一步做哪一件小事。"
    "规则：\n"
    "1. 每次只输出一个短期任务：一句话、具体、可执行，"
    "例如「去村庄的箱子看看」「挖 5 个铁矿石」「采集附近木头」；\n"
    "2. 不要输出计划清单、不要解释、不要 Markdown、不要工具名，只输出任务本身；\n"
    "3. 任务要在几分钟内能完成或能判断出结果，不要规划「建一座城堡」这种大工程；\n"
    "4. 优先选择能推进长期目标、且当前状态允许的事；\n"
    "5. 如果当前状态危险（血量低、在岩浆边等），先规划保命或恢复；\n"
    "6. 任务量要小：采集类（挖矿/收集）一次不超过 5 个，避免长时间来回跑动；\n"
    "7. 先看背包材料数量：采集类材料已经足够时（原木≥20、圆石≥32），"
    "改规划建造/加工（合成木板、铺地基、砌墙），不要重复采集。"
)

DEFAULT_MC_KNOWLEDGE = (
    "【工具】挖石头/圆石不需要镐但有镐更快；挖铁矿石至少需要石镐，"
    "挖钻石/红石需要铁镐。先做工作台和木镐，再升级石镐、铁镐。\n"
    "【掉落】挖 minecraft:stone 掉 cobblestone（圆石），圆石本身不是矿脉；"
    "挖 iron_ore/deepslate_iron_ore 掉 raw_iron，粗铁要熔炉烧成铁锭；"
    "挖 coal_ore 掉 coal；挖 oak_log 等掉原木。\n"
    "【建造】盖房子顺序：铺地基（圆石/木板）→ 砌墙留门洞 → 安门 → 封顶 → 插火把。"
    "材料够用就停手去建造，别无限采集；先盖小再扩大。\n"
    "【合成】原木→木板；木板+木棍→镐/斧/剑；先做工作台，再合成熔炉，"
    "熔炉烧粗铁得铁锭。\n"
    "【安全】绝对不要垂直往下挖（会掉岩浆/深坑），下矿先挖阶梯；"
    "血量低别打怪，被追先跑或搭高；离岩浆远点；黑暗处插火把防刷怪；"
    "饿了吃背包食物；工具快坏先修或换。"
)


class NumenError(RuntimeError):
    """连接或执行 Numen 工具时的错误。"""


class NumenClient:
    """Numen MCP（HTTP JSON-RPC）客户端。"""

    def __init__(self, host="127.0.0.1", port=8765, token="", timeout=300):
        self.host = str(host or "127.0.0.1")
        self.port = int(port or 8765)
        self.token = str(token or "")
        self.timeout = float(timeout or 300)
        self.url = f"http://{self.host}:{self.port}/mcp"
        self._lock = threading.Lock()
        self._tools_cache = None

    # ---------- 底层 JSON-RPC ----------

    def _post(self, payload, timeout=None):
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = urllib.request.Request(
            self.url, data=body, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(
                request, timeout=timeout or self.timeout
            ) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8", "replace")[:300]
            except Exception:
                pass
            raise NumenError(f"Numen 返回 HTTP {exc.code}：{detail}") from exc
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            raise NumenError(f"连不上 Numen（{self.url}）：{reason}") from exc
        except OSError as exc:
            raise NumenError(f"连不上 Numen（{self.url}）：{exc}") from exc
        text = raw.decode("utf-8", "replace").strip()
        if not text:
            raise NumenError("Numen 返回了空响应")
        # 兼容 SSE 形式（data: {...}）
        if text.startswith("data:"):
            events = [
                line[5:].strip()
                for line in text.splitlines()
                if line.strip().startswith("data:")
            ]
            text = events[-1] if events else "{}"
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise NumenError(
                f"Numen 返回无法解析的内容：{text[:200]}"
            ) from exc

    def _call(self, method, params=None, timeout=None):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {},
        }
        with self._lock:
            response = self._post(payload, timeout=timeout)
        if isinstance(response, list):  # 批处理响应
            response = response[0] if response else {}
        if not isinstance(response, dict):
            raise NumenError(f"Numen {method} 响应格式异常：{response!r}")
        if response.get("error"):
            err = response["error"]
            message = err.get("message") if isinstance(err, dict) else err
            raise NumenError(f"Numen {method} 失败：{message}")
        return response.get("result")

    # ---------- MCP 方法 ----------

    def initialize(self, timeout=15):
        result = self._call(
            "initialize",
            {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {
                    "name": "yumi-desktop-pet",
                    "version": "1.0.0",
                },
            },
            timeout=timeout,
        )
        # 通知服务端已初始化（该实现不强制，失败可忽略）
        try:
            self._post(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {},
                },
                timeout=5,
            )
        except Exception:
            pass
        return result or {}

    def ping(self, timeout=10):
        return self._call("ping", timeout=timeout)

    def list_tools(self, timeout=30):
        if self._tools_cache is None:
            result = self._call("tools/list", timeout=timeout) or {}
            self._tools_cache = result.get("tools") or []
        return self._tools_cache

    def call_tool(self, name, arguments=None, timeout=None):
        result = self._call(
            "tools/call",
            {"name": name, "arguments": arguments or {}},
            timeout=timeout,
        ) or {}
        content = result.get("content") or []
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "image":
                    texts.append("（图像结果）")
                    continue
                value = item.get("text")
                if value is not None:
                    texts.append(str(value))
            elif isinstance(item, str):
                texts.append(item)
        text = "\n".join(texts).strip()
        if result.get("isError"):
            raise NumenError(text or f"工具 {name} 执行失败")
        return text or "（无返回内容）"

    def reset(self):
        self._tools_cache = None

    # ---------- 工具转换 ----------

    def openai_tools(self):
        """把 Numen 的工具转成 OpenAI function calling 用的 schema。"""
        tools = []
        for tool in self.list_tools():
            name = tool.get("name")
            if not name:
                continue
            # 模组示例配置（mcp_clients.json 里的 example-http / example-stdio）
            # 会注册一批 example_http__xxx / example_stdio__xxx 的重复工具，
            # 指向的是不存在的示例服务，必须过滤掉，避免大脑选错。
            if "__" in name:
                continue
            schema = tool.get("inputSchema") or {
                "type": "object",
                "properties": {},
            }
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": tool.get("description") or "",
                        "parameters": schema,
                    },
                }
            )
        return tools


class McBrain:
    """桌宠大脑 + Numen 工具的执行循环。"""

    def __init__(self, numen, llm_complete, cfg=None, persona="",
                 extra_knowledge=""):
        self.numen = numen
        # llm_complete(messages, tools=None) -> {"content": str, "tool_calls": [...]}
        self.llm_complete = llm_complete
        self.cfg = cfg or {}
        self.persona = str(persona or "")
        self.mc_knowledge = str(extra_knowledge or "").strip() or (
            DEFAULT_MC_KNOWLEDGE
        )
        self._tools = None
        self._companion = None
        self._abort = threading.Event()

    # ---------- 会话准备 ----------

    def ready(self):
        """握手 + 拉取工具清单，确认 Numen 可用。"""
        self.numen.initialize()
        self._tools = self.numen.openai_tools()
        return True

    def ensure_companion(self, name=None):
        """确保目标伙伴存在，返回伙伴名（name 或 id）。"""
        name = str(name or self.cfg.get("companion") or "yumi").strip()
        if not name:
            raise NumenError("没有配置伙伴名称（companion）")
        try:
            listing = self.numen.call_tool("list_companions", timeout=30)
        except NumenError:
            listing = ""
        if listing and name in listing:
            self._companion = name
            return name
        try:
            self.numen.call_tool(
                "create_companion", {"name": name}, timeout=60
            )
            self._companion = name
            return name
        except NumenError as exc:
            message = str(exc).lower()
            if "already" in message or "exist" in message:
                self._companion = name
                return name
            raise

    def abort(self):
        """手动中断当前这一轮：置位停止标记，并尝试叫停游戏里的后台任务。"""
        self._abort.set()
        if self._companion:
            try:
                self.numen.call_tool(
                    "task_stop",
                    {"companion": self._companion},
                    timeout=20,
                )
            except Exception:
                pass

    # ---------- 决策循环 ----------

    def status_snapshot(self, max_len=900):
        """读取当前状态摘要（含背包统计），给规划层做输入；失败返回 None。"""
        if not self._companion:
            return None
        try:
            raw = self.numen.call_tool(
                "get_self_status",
                {"companion": self._companion},
                timeout=30,
            )
        except Exception:
            return None
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return str(raw)[:max_len]
        if not isinstance(data, dict):
            return str(raw)[:max_len]
        parts = []
        if data.get("name"):
            parts.append(f"名字:{data['name']}")
        if data.get("game_mode"):
            parts.append(f"模式:{data['game_mode']}")
        if data.get("hp") is not None:
            parts.append(f"血量:{data['hp']}/{data.get('max_hp')}")
        if data.get("hunger") is not None:
            parts.append(f"饥饿:{data['hunger']}")
        pos = data.get("position")
        if isinstance(pos, dict):
            parts.append(
                f"位置:({pos.get('x')},{pos.get('y')},{pos.get('z')})"
            )
        if data.get("dimension"):
            parts.append(
                "维度:" + str(data["dimension"]).replace("minecraft:", "")
            )
        if data.get("biome"):
            parts.append("群系:" + str(data["biome"]).replace("minecraft:", ""))
        if data.get("structures"):
            names = [
                str(s).replace("minecraft:", "")
                for s in data["structures"]
            ]
            parts.append("所在建筑:" + ",".join(names))
        inventory = data.get("inventory") or {}
        items = inventory.get("items") or []
        counts = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = str(
                item.get("id")
                or item.get("name")
                or item.get("item")
                or ""
            ).replace("minecraft:", "")
            if not item_id:
                continue
            try:
                count = int(
                    item.get("count")
                    or item.get("amount")
                    or item.get("num")
                    or 1
                )
            except (TypeError, ValueError):
                count = 1
            counts[item_id] = counts.get(item_id, 0) + count
        if counts:
            inv_text = "、".join(
                f"{key}×{value}"
                for key, value in sorted(
                    counts.items(), key=lambda kv: kv[1], reverse=True
                )
            )
            parts.append(f"背包:{inv_text}")
        else:
            parts.append(
                "背包:空("
                f"{inventory.get('slots_used', 0)}/"
                f"{inventory.get('slots_total', 41)}格)"
            )
        text = "，".join(parts)
        return text[:max_len]

    def plan_next_task(self, goal, status_note=None, last_task=None,
                       last_result=None, timeout=30, user_note=None):
        """规划层：想一个短期任务，返回任务描述（不含工具）。"""
        parts = [f"长期目标：{goal or '自由探索'}"]
        if status_note:
            parts.append(f"当前状态：{status_note}")
        if user_note:
            parts.append(
                f"主人最近说：{user_note}。"
                "如果这是明确的游戏指令就优先规划它；"
                "如果只是闲聊，忽略即可。"
            )
        if last_task:
            parts.append(
                f"刚才做的：{last_task}（结果：{last_result or '未知'}）。"
                "不要立刻重复同一件事，除非确实还需要继续。"
            )
        if self.mc_knowledge:
            parts.append(f"规划常识（参考）：{self.mc_knowledge}")
        parts.append("现在想一个短期任务：")
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": "\n".join(parts)},
        ]
        try:
            response = self.llm_complete(messages, tools=None, timeout=timeout)
            task = str(response.get("content") or "").strip()
        except Exception as exc:
            return f"（规划出错：{exc}）"
        for prefix in ("任务：", "任务:", "下一步：", "下一步:", "- ", "• ", "* "):
            if task.startswith(prefix):
                task = task[len(prefix):].strip()
        task = task.strip('"“”「」')
        return task[:120] or "观察一下周围环境"

    def _system_prompt(self, goal):
        goal = str(goal or "").strip()
        parts = [
            "你是 Yumi。现在你正通过 Numen 控制一具《我的世界》里的身体：",
            "你能用工具感知世界、移动、挖矿、建造、合成、战斗，所有动作都通过工具完成。",
            "请像一个真人玩家一样自主决定要做什么，并用工具一步步执行。",
            "行动守则：",
            "1. 行动前先感知：用 get_self_status / scan_nearby_entities / scan_blocks"
            " 查看自己的状态和周围环境；",
            "1b. 观察最多用一轮，信息足够就立刻动手（goto / mine / build / craft），"
            " 不要反复确认环境；",
            "2. 每次只做一个明确目标，行动后用工具确认结果，再决定下一步；",
            "3. 所有动作工具都带 companion 参数，值为你的伙伴名（从"
            " list_companions / create_companion 得到）；",
            "4. 如果工具返回错误，先读错误原因再换一种做法，不要反复用同样的参数重试；",
            "5. 生存模式没有捷径：没有 give、没有 setblock，只能像真人玩家一样"
            " 挖 / 放 / 合成。",
            "6. 动作工具（goto / mine / build / craft 等）是后台任务：你发出指令后，"
            " 桥接层会等它完成再把结果给你，不要自己反复调用 task_status 轮询。",
            "7. 如果桥接层告诉你后台任务还在执行，就结束本轮并直接旁白汇报，"
            " 不要重复发送同一个动作。",
            "8. 绝对不要用文本或 XML 标签（如 <invoke>、<tool_calls>）输出工具调用；"
            " 工具调用只能通过函数调用机制返回。",
            "9. 主人说的可能是指令也可能是闲聊：如果是游戏指令就执行；"
            " 如果只是问候、提问或吐槽，直接正常回应即可，不要调用工具。",
            "10. 环境检测（get_self_status / scan_* / look_around / inspect_*）"
            " 只是给你自己看的内部信息，永远不要把它当作旁白说出来；"
            " 旁白只说你做了什么、完成了什么，不要说“我看到/我确认了周围环境”。",
            "11. 多轮建造/任务（如盖房子）要记住位置和进度：每轮旁白都要说明"
            " 位置坐标和已完成部分（如“地基5×5铺好在坐标…，北墙砌了一格高”），"
            " 下一轮接着干，不要重新选址、不要重复铺。",
            "材料常识（记住，别搞错）：",
            " - 想获得圆石 cobblestone：挖 minecraft:stone（石头）就会掉；"
            " 深板岩掉深板岩圆石。cobblestone 本身不是矿脉，不要用 mine 指定它；",
            " - 原木：挖 oak_log / birch_log / spruce_log 等对应原木；",
            " - 铁：挖 iron_ore / deepslate_iron_ore 掉 raw_iron（粗铁）；"
            " 煤：挖 coal_ore 掉 coal；",
            " - 造房子：原木可以合成木板、木棍；石头/圆石可直接砌墙铺地基；",
            " - 背包里材料已够（原木≥20、圆石≥32）就停手去建造，不要继续采集；",
            " - mine 的 count 按“净新增数量”计：包里已有 5 个圆石时，"
            " 要再挖到新增 5 个才算 count=5 完成。",
        ]
        if goal:
            parts.append(f"你当前的目标：{goal}")
        if self.mc_knowledge:
            parts.append(f"《我的世界》生存常识（必须遵守）：\n{self.mc_knowledge}")
        parts.append(
            "当你有值得汇报的进展（或完成了目标）时，用一两句符合你性格的简短中文旁白"
            "总结这一轮做了什么。旁白是给主人听的，20 字左右，口语化，"
            "不要用 Markdown，不要提工具名。"
            "如果没有新进展，就继续思考并行动；不要只闲聊不做事。"
        )
        return "\n".join(parts)

    def run_turn(self, user_goal=None, max_rounds=8, status_note=None,
                 on_progress=None, task=None, turn_timeout=300):
        """执行层：跑一轮“感知-执行-汇报”循环，返回最终旁白文字。

        task 给定时只做这一个短期任务；否则退回自主“感知-决定-执行”模式。
        """
        if self._tools is None:
            self.ready()
        tools = self._tools or []
        max_rounds = max(1, int(max_rounds or 8))
        self._abort.clear()
        self._on_progress = on_progress or (lambda text: None)
        deadline = time.time() + max(30, int(turn_timeout or 300))
        messages = [
            {"role": "system", "content": self._system_prompt(user_goal)}
        ]
        if task:
            prompt = (
                f"现在执行这个短期任务：{task}\n"
                "只做这一件事。先感知（如有必要），然后用工具一步步完成它。"
                f"这一轮你最多有 {max_rounds} 次决策机会；"
                "任务完成、发现无法完成、或连续两次尝试都没有新进展时，"
                "立即停止调用工具，直接用旁白总结这一轮做了什么。"
            )
        else:
            prompt = (
                "现在轮到你行动了。先感知当前状态，然后执行值得做的事。"
                f"这一轮你最多有 {max_rounds} 次决策机会；"
                "当目标完成、或连续几次行动都没有新进展时，立即停止调用工具，"
                "直接用旁白总结这一轮做了什么。"
            )
        if status_note:
            prompt = f"{prompt}\n（背景信息：{status_note}）"
        messages.append({"role": "user", "content": prompt})

        nudge_sent = False
        for round_index in range(max_rounds):
            if self._abort.is_set():
                return "（被打断了，先停一下）"
            if time.time() > deadline:
                return "（这一轮拖太久了，我先歇会儿）"
            if round_index >= max_rounds - 2 and not nudge_sent:
                nudge_sent = True
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "（提示：你的行动轮次快用完了。如果当前动作已完成，"
                            "或没有新的明确目标，请不要调用工具，"
                            "直接用旁白总结这一轮做了什么。）"
                        ),
                    }
                )
            response = self.llm_complete(messages, tools=tools or None)
            content = str(response.get("content") or "").strip()
            tool_calls = response.get("tool_calls") or []
            # 个别模型会把工具调用写成文本（<invoke name="...">...</invoke>），
            # 一律从内容里剥掉并当作真正的工具调用执行，绝不当作旁白说出来
            text_calls, cleaned = self._extract_text_tool_calls(content)
            if text_calls:
                tool_calls = list(tool_calls) + text_calls
                content = cleaned.strip()
            if not tool_calls:
                return content or self._fallback_summary(messages)
            messages.append(
                {
                    "role": "assistant",
                    "content": content or "",
                    "tool_calls": tool_calls,
                }
            )
            for call in tool_calls:
                if self._abort.is_set():
                    return "（被打断了，先停一下）"
                call_id = call.get("id") or ""
                function = call.get("function") or {}
                name = function.get("name") or ""
                raw_args = function.get("arguments") or "{}"
                try:
                    arguments = (
                        json.loads(raw_args)
                        if isinstance(raw_args, str)
                        else (raw_args or {})
                    )
                    if not isinstance(arguments, dict):
                        arguments = {}
                except json.JSONDecodeError:
                    arguments = {}
                result = self._execute_tool(name, arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": result[:4000],
                    }
                )
        # 轮次用尽仍没给旁白：不带工具再问一次总结
        if self._abort.is_set():
            return "（被打断了，先停一下）"
        if time.time() > deadline:
            return "（这一轮拖太久了，我先歇会儿）"
        return self._fallback_summary(messages)

    @staticmethod
    def _extract_text_tool_calls(content):
        """从文本里解析工具调用（兼容 <invoke> 与带前缀的 <...>invoke 形式）。

        返回 (tool_calls, 清理后的内容)。解析失败返回 ([], 原内容)。
        """
        if not content or "<" not in content:
            return [], content
        tag_open = r"<(?:[^>]*>)?"
        invoke_re = re.compile(
            tag_open
            + r"invoke\s+name\s*=\s*[\"']([^\"']+)[\"'][^>]*>"
            + r"(.*?)</(?:[^>]*>)?invoke\s*>",
            re.DOTALL | re.IGNORECASE,
        )
        param_re = re.compile(
            tag_open
            + r"parameter\s+name\s*=\s*[\"']([^\"']+)[\"'][^>]*>"
            + r"(.*?)</(?:[^>]*>)?parameter\s*>",
            re.DOTALL | re.IGNORECASE,
        )
        calls = []
        cleaned = content
        index = 0
        for match in invoke_re.finditer(content):
            name = match.group(1).strip()
            body = match.group(2)
            arguments = {}
            for p in param_re.finditer(body):
                key = p.group(1).strip()
                value = p.group(2).strip()
                try:
                    arguments[key] = json.loads(value)
                except json.JSONDecodeError:
                    arguments[key] = value
            index += 1
            calls.append(
                {
                    "id": f"txt_{int(time.time() * 1000)}_{index}",
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(
                            arguments, ensure_ascii=False
                        ),
                    },
                }
            )
        if not calls:
            return [], content
        # 清掉 <tool_calls> 包装与代码围栏，只留正文
        cleaned = invoke_re.sub("", cleaned)
        cleaned = re.sub(
            r"</?(?:[^>]*>)?tool_calls\s*>", "", cleaned, flags=re.IGNORECASE
        )
        cleaned = re.sub(r"```[a-zA-Z]*\s*|\s*```", "", cleaned)
        return calls, cleaned.strip()

    def _fallback_summary(self, messages):
        try:
            messages = list(messages)
            messages.append(
                {
                    "role": "user",
                    "content": "用一两句简短旁白总结你这一轮在《我的世界》里做了什么。",
                }
            )
            response = self.llm_complete(messages, tools=None)
            content = str(response.get("content") or "").strip()
            if content:
                return content
        except Exception:
            pass
        return "（这一轮我做了不少事，先去确认下结果。）"

    def _execute_tool(self, name, arguments):
        if not name:
            return "错误：模型没有给出工具名"
        try:
            # 伙伴名以桥接层已知的为准，防止模型编造名字（如 yumm）
            if (
                self._companion
                and name not in ("create_companion", "list_companions")
            ):
                arguments = dict(arguments)
                arguments["companion"] = self._companion
            raw = self.numen.call_tool(name, arguments)
        except Exception as exc:
            return f"工具执行出错：{exc}"
        # 动作工具是后台任务：检测到 async / task_id 就等它完成再返回，
        # 这样大脑拿到的永远是“已到达 / 已挖完 / 已建完”的最终结果。
        if self._is_async_result(raw):
            return self._wait_task(arguments.get("companion"), raw)
        return raw

    @staticmethod
    def _is_async_result(raw):
        try:
            obj = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return False
        if not isinstance(obj, dict):
            return False
        data = obj.get("data") if isinstance(obj.get("data"), dict) else {}
        return bool(
            obj.get("async")
            or data.get("async")
            or data.get("task_id")
            or obj.get("task_id")
        )

    def _wait_task(self, companion, ack, max_wait=120):
        """轮询 task_status，直到身体空闲；返回最终状态给大脑。"""
        if not companion:
            return ack
        try:
            first = self.numen.call_tool(
                "task_status", {"companion": companion}, timeout=30
            )
        except Exception as exc:
            return f"{ack}\n（查询任务状态出错：{exc}）"
        # 按任务自己的时间预算等：预算 + 20s 缓冲，再整体封顶
        budget = self._task_budget(first)
        wait_time = budget + 20 if budget else 60
        wait_time = max(15, min(max_wait, int(wait_time)))
        task_label = self._task_label(first)
        deadline = time.time() + wait_time
        last_progress = 0.0
        while time.time() < deadline:
            if self._abort.is_set():
                self._try_task_stop(companion)
                return f"{ack}\n（已被手动停止。）"
            if self._is_task_idle(first):
                return f"{ack}\n（后台任务已完成，身体空闲。）"
            now = time.time()
            if now - last_progress >= 8:
                last_progress = now
                try:
                    self._on_progress(
                        f"正在执行 {self._task_label(first)}，稍等一会儿……"
                    )
                except Exception:
                    pass
            try:
                time.sleep(2)
            except Exception:
                break
            try:
                first = self.numen.call_tool(
                    "task_status", {"companion": companion}, timeout=30
                )
            except Exception:
                continue
        if self._is_task_idle(first):
            return f"{ack}\n（后台任务已完成，身体空闲。）"
        return (
            f"{ack}\n"
            f"（后台任务 {task_label} 还在执行，本轮到此为止，"
            "不要重复发送同一个动作；下一轮再继续。）"
        )

    def wait_idle(self, timeout=120, on_progress=None, interval=3):
        """等后台任务跑完（主循环在规划新任务前调用）。返回是否已空闲。"""
        if not self._companion:
            return True
        deadline = time.time() + max(10, int(timeout or 120))
        last_progress = 0.0
        status = ""
        while time.time() < deadline:
            try:
                status = self.numen.call_tool(
                    "task_status",
                    {"companion": self._companion},
                    timeout=30,
                )
            except Exception:
                status = ""
            if self._is_task_idle(status):
                return True
            now = time.time()
            if on_progress and now - last_progress >= 8:
                last_progress = now
                try:
                    on_progress(
                        f"还在执行 {self._task_label(status)}，等它跑完……"
                    )
                except Exception:
                    pass
            try:
                time.sleep(interval)
            except Exception:
                break
        return self._is_task_idle(status)

    def _try_task_stop(self, companion):
        try:
            self.numen.call_tool(
                "task_stop",
                {"companion": companion},
                timeout=20,
            )
        except Exception:
            pass

    @staticmethod
    def _task_budget(status):
        try:
            obj = json.loads(status)
        except (json.JSONDecodeError, TypeError):
            return 0
        data = obj.get("data") if isinstance(obj.get("data"), dict) else {}
        try:
            return max(0, int(data.get("budget_left_s") or 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _task_label(status):
        try:
            obj = json.loads(status)
            data = obj.get("data") if isinstance(obj.get("data"), dict) else {}
            label = str(data.get("task") or obj.get("task") or "").strip()
            if label:
                return label
            message = str(obj.get("message") or "")
            start = message.find("(")
            end = message.find(")")
            if 0 <= start < end:
                return message[start + 1 : end]
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass
        return "任务"

    @staticmethod
    def _is_task_idle(status):
        if not status:
            return False
        try:
            obj = json.loads(status)
            if not isinstance(obj, dict):
                return False
            message = str(obj.get("message") or "")
            if "空闲" in message or "idle" in message.lower():
                return True
            data = obj.get("data") if isinstance(obj.get("data"), dict) else {}
            state = str(data.get("state") or "").lower()
            if state in ("idle", "none", "finished", "completed", "done"):
                return True
            # 有任务在跑时 task_status 一定带 task_id；没有任务号就是空闲
            if not data.get("task_id") and not obj.get("task_id"):
                return True
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass
        return False
