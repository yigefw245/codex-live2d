"use strict";

const MODEL_ROOT = "/model/";
const STATUS_H = 0;
const PAD = 12;

const canvas = document.getElementById("stage");
const bubbleEl = document.getElementById("bubble");
const chatboxEl = document.getElementById("chatbox");
const chatInputEl = document.getElementById("chat-input");
let bubbleTimer = null;
let chatPanelH = 0;
let chatReactTimer = null;
let lastReactEmotion = null;
let lastReactAt = 0;
let motionIntensity = 1;
let headTiltGain = 1;
let userCropBottom = 0;
let userCropSide = 0;
let poseName = null;
let poseEndAt = 0;
let nextIdlePoseAt = 0;
let nextSpeakPoseAt = 0;
let baseModelY = null;
let speakEnv = 0;
let bodyPhase = 0;
let lookX = 0;
let lookTX = 0;
let lookPhase = "pause";
let lookPhaseEndAt = 0;
let lastXDir = 1;
let lookDownTarget = 0;
let lookDownY = 0;
let burst = null;
let nextBurstAt = 0;
let tiltCur = 0;
let tiltTarget = 0;
let nextTiltAt = 0;
let gravY = 0;
let gravV = 0;
let speakTiltZ = null;
let speakTiltY = null;
let recZ = 0;
let soullinkActions = null;
let speakQueue = Promise.resolve();
let speakPending = 0;
let soullink = { enabled: false, config: null, bridge: null, starting: null };

function soullinkEnabled() {
  return soullink.enabled;
}

let app = null;
let model = null;
let modelConfig = null;
let currentState = "idle";
let actionOverrides = {};
let EXPR_DATA = {};
let activeFace = null;
let activePose = null;
let exprFade = 0;
let manualExpression = null;
let motionActive = "idle";
let presetMotion = null;
let manualMotion = null;
let motionClock = 0;
let transitionT = 1;
let eyeTargetX = 0;
let eyeTargetY = 0;
let eyeX = 0;
let eyeY = 0;
let lastTs = 0;
let headX = 0;
let headY = 0;
let headTop = 0;
let headKnown = false;
let baseScale = 1;
let currentScale = 1;
let baseBounds = null;

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function easeInOut(t) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

// ---------- model config helpers ----------

function presetFor(state) {
  return (
    (modelConfig && modelConfig.presets && modelConfig.presets[state]) || {}
  );
}

function chatPresetFor(emotion) {
  return (
    (modelConfig && modelConfig.chat && modelConfig.chat[emotion]) || {}
  );
}

function exprKind(key) {
  const map = (modelConfig && modelConfig.expressions) || {};
  const info = map[key];
  if (info && typeof info === "object" && info.kind) return info.kind;
  return "face";
}

// 单模型底部裁切比例（0-1），用于隐藏角色脚下额外画的内容（如水印文字）。
function cropBottom() {
  return (
    Math.max(
      (modelConfig && modelConfig.crop && modelConfig.crop.bottom) || 0,
      userCropBottom
    )
  );
}

// 单模型两侧裁切比例（0-0.45），左右对称往中间裁。
function cropSide() {
  return Math.max(
    (modelConfig && modelConfig.crop && modelConfig.crop.side) || 0,
    userCropSide
  );
}

// 状态动作解析：手动指定优先；未指定 / 指定项不存在时回退默认配置。
function resolveStatusAction(name) {
  const ov = actionOverrides[name] || {};
  const pres = presetFor(name);
  const auto = {
    motion: pres.motion || null,
    pose: pres.pose || null,
    face: pres.face !== undefined ? pres.face : defaultFaceFor(name),
  };
  if (!ov.type || ov.type === "auto") return auto;
  if (ov.type === "none") return { motion: null, pose: null, face: null };
  if (ov.type === "motion") {
    const ok = ((modelConfig && modelConfig.motions) || []).some(
      (m) => m.group === ov.key
    );
    return ok
      ? { motion: ov.key, pose: auto.pose, face: auto.face }
      : auto;
  }
  if (ov.type === "expr") {
    if (!EXPR_DATA[ov.key]) return auto;
    if (exprKind(ov.key) === "pose") {
      return { motion: auto.motion, pose: ov.key, face: auto.face };
    }
    return { motion: auto.motion, pose: auto.pose, face: ov.key };
  }
  return auto;
}

function defaultFaceFor(state) {
  switch (state) {
    case "idle":
      return "heart";
    case "thinking":
      return "star";
    case "working":
      return "swirl";
    case "fault":
      return "black";
    case "interact":
      return "heart";
    default:
      return null;
  }
}

function statusStateName(name) {
  return (
    name === "idle" ||
    name === "thinking" ||
    name === "working" ||
    name === "completed" ||
    name === "fault"
  );
}

// ---------- rendering helpers ----------

function setParam(id, value) {
  if (!model || !model.internalModel || !model.internalModel.coreModel) return;
  try {
    model.internalModel.coreModel.setParameterValueById(id, value);
  } catch (e) {
    /* ignore unknown parameters */
  }
}

function getParam(id) {
  if (!model || !model.internalModel || !model.internalModel.coreModel) return 0;
  try {
    return model.internalModel.coreModel.getParameterValueById(id);
  } catch (e) {
    return 0;
  }
}

// 手势姿势共用同一个槽位（待机/说话），通过直接参数开关，避免两个手势重叠。
function applyPose(name, on) {
  if (!name) return;
  const params = EXPR_DATA[name];
  if (!params) return;
  for (const p of params) setParam(p.id, on ? p.value : 0);
}

function clearPose() {
  if (poseName) applyPose(poseName, false);
  poseName = null;
}

function stopAllMotions() {
  try {
    if (model.motionManager) model.motionManager.stopAllMotions();
  } catch (e) {}
  try {
    if (model.internalModel && model.internalModel.motionManager) {
      model.internalModel.motionManager.stopAllMotions();
    }
  } catch (e) {}
}

function startNativeMotion(group) {
  if (!group || !model || !model.motion) return;
  try {
    model.motion(group);
  } catch (e) {
    /* group missing -> ignore */
  }
}

function applyEffects() {
  const effects = (modelConfig && modelConfig.effects) || {};
  for (const key of Object.keys(effects)) {
    const params = EXPR_DATA[key];
    if (!params) continue;
    for (const p of params) setParam(p.id, p.value);
  }
}

function applyExpressionTarget(face, pose) {
  face = face && EXPR_DATA[face] ? face : null;
  pose = pose && EXPR_DATA[pose] ? pose : null;
  if (face === activeFace && pose === activePose && exprFade > 0.01) return;
  // 先把所有非固定表情参数归零，避免残留（尤其是黑脸）。
  const effects = (modelConfig && modelConfig.effects) || {};
  for (const [key, params] of Object.entries(EXPR_DATA)) {
    if (effects[key]) continue;
    for (const p of params) setParam(p.id, 0);
  }
  applyEffects();
  activeFace = face;
  activePose = pose;
  exprFade = 0;
}

// ---------- motion: preset (native) or custom engine ----------

// 应用某个状态的外观（动作 + 姿势 + 表情），不弹气泡。
function applyStateVisuals(name) {
  if (soullinkEnabled()) return;
  const act = resolveStatusAction(name);
  let face = manualExpression || act.face;
  let pose = act.pose;
  // 故障在未手动覆盖时强制黑脸。
  if (name === "fault" && !(actionOverrides[name] || {}).type) {
    face = "black";
    pose = null;
  }
  applyExpressionTarget(face, pose);
  const group = act.motion;
  manualMotion = null;
  motionClock = 0;
  if ((actionOverrides[name] || {}).type === "none") {
    motionActive = "none";
    presetMotion = null;
  } else if (group) {
    presetMotion = group;
    motionActive = "preset";
    startNativeMotion(group);
  } else {
    presetMotion = null;
    motionActive =
      name === "completed" || name === "interact"
        ? "wave"
        : name === "thinking"
        ? "thinking"
        : name === "working"
        ? "working"
        : "idle";
  }
  transitionT = 0;
}

function applyCurrentMotion() {
  applyStateVisuals(currentState);
}

// Custom motion engine: drives parameters directly, so actions work even
// when a model has no preset motion files for that state.
function applyMotion(dt) {
  if (motionActive === "preset" || motionActive === "none") return;
  motionClock += dt;
  const t = motionClock;
  const mi = motionIntensity;
  if (motionActive === "wave") {
    setParam("ParamarmupR", 0);
    setParam("ParamBodyAngleY", 0);
    setParam("ParamAngleZ", 0);
    setParam("Paramdown1", 0);
    const WAVE_DURATION = 1.7;
    if (t >= WAVE_DURATION) {
      // One-shot wave finished: settle back to the idle pose.
      motionActive = "idle";
      motionClock = 0;
      setParam("ParamarmupL", 0);
      setParam("Paramanime", 0);
      setParam("ParamAngleX", 0);
      return;
    }
    let arm;
    if (t < 0.25) {
      arm = easeInOut(t / 0.25);
    } else if (t > 1.3) {
      arm = 1 - easeInOut((t - 1.3) / 0.4);
    } else {
      arm = 1;
    }
    setParam("ParamarmupL", arm);
    const waving = t >= 0.25 && t <= 1.3;
    setParam(
      "Paramanime",
      waving ? Math.sin(((t - 0.25) / 1.05) * Math.PI * 4) : 0
    );
  } else if (motionActive === "thinking") {
    // Thinking pose: head tilted, right hand near the face, eyes looking up.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0.95 + 0.08 * Math.sin((t * Math.PI * 2) / 2.2));
    setParam("Paramanime", 0);
    setParam("ParamAngleZ", 11 + 2.5 * mi * Math.sin((t * Math.PI * 2) / 3.5));
    setParam("ParamBodyAngleY", 3.2 * mi * Math.sin((t * Math.PI * 2) / 4));
    setParam("ParamEyeBallY", 0.6 + 0.2 * Math.sin((t * Math.PI * 2) / 2.4));
    setParam("Paramdown1", 0);
  } else if (motionActive === "working") {
    // Busy typing pose: bent forward with a quick bobbing rhythm.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0.8 + 0.1 * Math.sin((t * Math.PI * 2) / 1.1));
    setParam("ParamAngleZ", 3.5 * mi * Math.sin((t * Math.PI * 2) / 3.2));
    setParam("ParamBodyAngleY", 2.6 * mi * Math.sin((t * Math.PI * 2) / 0.9));
    setParam("ParamAngleX", 2.5 * mi * Math.sin((t * Math.PI * 2) / 1.3));
  } else if (motionActive === "sad") {
    // Drooping shoulders, looking down a little.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0.72 + 0.08 * Math.sin((t * Math.PI * 2) / 3));
    setParam("ParamAngleZ", 3.5 * mi * Math.sin((t * Math.PI * 2) / 4));
    setParam("ParamBodyAngleY", 1.6 * mi * Math.sin((t * Math.PI * 2) / 3));
  } else if (motionActive === "angry") {
    // Slight trembling, one hand clenched near the chest.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0.65 + 0.08 * Math.sin((t * Math.PI * 2) / 0.8));
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0);
    setParam("ParamAngleZ", 3.2 * mi * Math.sin((t * Math.PI * 2) / 0.45));
    setParam("ParamBodyAngleY", 4.2 * mi * Math.sin((t * Math.PI * 2) / 0.6));
  } else if (motionActive === "surprised") {
    // Leaning back, head slightly tilted.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0);
    setParam(
      "ParamAngleZ",
      -6.5 + 1.5 * mi * Math.sin((t * Math.PI * 2) / 1.2)
    );
    setParam("ParamAngleX", -7);
    setParam("ParamBodyAngleY", 0);
  } else if (motionActive === "nod") {
    // Gentle friendly nod for neutral replies.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0.22 + 0.06 * Math.sin((t * Math.PI * 2) / 3.2));
    setParam("ParamAngleZ", 1.5 * mi * Math.sin((t * Math.PI * 2) / 4));
    setParam("ParamBodyAngleY", 0.8 * mi * Math.sin((t * Math.PI * 2) / 3.2));
  } else {
    // 待机：明显的左右摇晃（身体 + 头部），幅度随动作强度设置放大。
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam(
      "ParamAngleZ",
      6.0 * mi * headTiltGain * Math.sin((t * Math.PI * 2) / 5)
    );
    setParam("ParamAngleX", 4.0 * mi * Math.sin((t * Math.PI * 2) / 7 + 1));
    setParam("ParamBodyAngleY", 3.5 * mi * Math.sin((t * Math.PI * 2) / 4.5));
    setParam("Paramdown1", 0);
  }
}

// Gentle transition played when switching between states.
function applyTransition(dt) {
  if (transitionT >= 1 || motionActive === "preset") return;
  transitionT = Math.min(1, transitionT + dt / 0.7);
  const cm = model.internalModel.coreModel;
  const g = (id) => cm.getParameterValueById(id);
  const k = Math.sin(transitionT * Math.PI);
  const sway = Math.sin(transitionT * Math.PI * 2) * k;
  const amp =
    (currentState === "completed" || currentState === "chat-happy"
      ? 1.4
      : 0.8) * motionIntensity;
  setParam("ParamAngleZ", g("ParamAngleZ") + sway * 2.5 * amp);
  setParam("ParamBodyAngleY", g("ParamBodyAngleY") + k * 1.2 * amp);
  setParam("Paramdown1", g("Paramdown1") + k * 0.08 * amp);
}

// ---------- state / expression ----------

function setPetState(name) {
  const prevState = currentState;
  currentState = name;
  // 状态类表情永远优先：状态切换后手动表情自动让位并还原。
  if (statusStateName(name) && name !== prevState) {
    manualExpression = null;
  }
  applyStateVisuals(name);
  if (name === "thinking") showBubble("思考中…", 2600);
  else if (name === "working") showBubble("执行命令…", 2600);
  else if (name === "completed") showBubble("完成！", 2600);
  else if (name === "fault") showBubble("故障！", 2600);
  else if (name === "idle") showBubble("待机中", 1800);
  else if (name === "interact") showBubble("嗨！", 1600);
}

function setExpression(name) {
  manualExpression = name && name !== "none" ? name : null;
  applyStateVisuals(currentState);
}

function playMotion(group) {
  if (!group || !model) return;
  manualMotion = group;
  presetMotion = null;
  motionActive = "preset";
  motionClock = 0;
  startNativeMotion(group);
}

function stopMotion() {
  stopAllMotions();
  manualMotion = null;
  applyCurrentMotion();
}

// ---------- chat ----------

function chatReact(emotion) {
  if (soullinkEnabled()) return;
  const prevState = currentState;
  const generic = {
    happy: { face: "heart" },
    sad: { face: "tear" },
    angry: { face: "black" },
    thinking: { face: "star" },
    surprised: { face: "swirl" },
    neutral: { face: "heart" },
  };
  const m = chatPresetFor(emotion);
  const base = generic[emotion] || generic.neutral;
  const faceKey =
    m.face !== undefined ? m.face : base.face;
  const poseKey = m.pose || null;
  const motionMap = {
    happy: "wave",
    sad: "sad",
    angry: "angry",
    thinking: "thinking",
    surprised: "surprised",
    neutral: "nod",
  };
  currentState = "chat-" + emotion;
  applyExpressionTarget(faceKey, poseKey);
  motionActive = motionMap[emotion] || "nod";
  presetMotion = null;
  manualMotion = null;
  motionClock = 0;
  transitionT = 0;
  // 反应有硬上限：连续对话也不会一直不还原（尤其是黑脸）。
  // 计时器已在计时时不再重置，保证一轮连发后必定还原。
  if (!chatReactTimer) {
    const duration = emotion === "angry" ? 4000 : 8000;
    chatReactTimer = setTimeout(() => {
      chatReactTimer = null;
      currentState = prevState;
      applyStateVisuals(prevState);
    }, duration);
  }
}

function showBubble(text, ms) {
  bubbleEl.textContent = text;
  bubbleEl.classList.add("show");
  positionBubble();
  if (bubbleTimer) clearTimeout(bubbleTimer);
  bubbleTimer = setTimeout(() => {
    bubbleEl.classList.remove("show");
  }, ms || 1800);
}

function setChatMode(on) {
  chatboxEl.classList.toggle("show", !!on);
  chatPanelH = on ? 50 : 0;
  reposition();
  if (on) chatInputEl.focus();
}

function showChatReply(text, ms) {
  showBubble(text, ms || 6000);
}

function sendChat() {
  const text = chatInputEl.value.trim();
  if (!text || !window.__bridge) return;
  chatInputEl.value = "";
  showBubble("…", 60000);
  window.__bridge.send_chat(text);
}

// ---------- Soullink Emotion SDK ----------

async function ensureSoullinkBridge() {
  if (soullink.bridge) return soullink.bridge;
  if (soullink.starting) return soullink.starting;
  soullink.starting = (async () => {
    await import("/tools/web/lib/soullink-emotion.esm.js");
    const bridge = window.__soullink;
    if (!bridge) throw new Error("Soullink SDK 未初始化");
    soullink.bridge = bridge;
    return bridge;
  })();
  try {
    return await soullink.starting;
  } finally {
    soullink.starting = null;
  }
}

async function stopSoullink() {
  soullink.enabled = false;
  if (soullink.bridge) {
    try {
      soullink.bridge.stop();
    } catch (err) {
      console.error("[soullink] stop failed", err);
    }
  }
}

window.setSoullinkConfig = async (cfg) => {
  soullink.config = cfg;
  if (cfg && typeof cfg.motionIntensity === "number") {
    window.setMotionIntensity(cfg.motionIntensity);
  }
  if (cfg && typeof cfg.headTiltGain === "number") {
    window.setHeadTiltGain(cfg.headTiltGain);
  }
  if (!cfg || !cfg.enabled) {
    await stopSoullink();
    return;
  }
  try {
    const bridge = await ensureSoullinkBridge();
    await bridge.start({
      profileUrl: cfg.profileUrl,
      ttsUrl: cfg.ttsUrl,
      motionStyle: cfg.motionStyle || "natural",
      bodyMotionGain: 2.8 * motionIntensity,
      lipSyncGain: typeof cfg.lipSyncGain === "number" ? cfg.lipSyncGain : 1,
      headTiltGain:
        typeof cfg.headTiltGain === "number" ? cfg.headTiltGain : 1,
      poseKeys:
        soullinkActions && soullinkActions.length
          ? soullinkActions
          : ["hand", "phone", "notes", "lean"]
    });
    soullink.enabled = true;
    if (model) bridge.setModel(model);
  } catch (err) {
    console.error("[soullink] start failed", err);
    soullink.enabled = false;
    showBubble("Soullink 启动失败：" + (err && err.message ? err.message : err), 6000);
  }
};

window.setSoullinkEnabled = (on) => {
  if (!on && soullink.enabled) void stopSoullink();
};

window.soullinkRestart = async () => {
  await stopSoullink();
  if (soullink.config && soullink.config.enabled) {
    await window.setSoullinkConfig(soullink.config);
  }
};

window.soullinkChat = (payload) => {
  if (!payload) return;
  if (!soullinkEnabled() || !soullink.bridge) {
    if (payload.reply) showChatReply(payload.reply, 6000);
    return;
  }
  const intent = payload.intent || null;
  // 实时语音对话（no_bubble）不显示文字气泡，其余照常显示
  if (payload.reply && !payload.no_bubble) showChatReply(payload.reply, 6000);
  if (intent) {
    // 有情绪反应/说话时，让 SDK 表情接管，取消手势姿势及其恢复计时
    clearPose();
    nextIdlePoseAt =
      (performance.now ? performance.now() / 1000 : Date.now() / 1000) + 30;
    // 同一情绪在短时间内重复触发时跳过表情反应（避免连续“生气”导致黑脸不还原），
    // TTS 朗读不受影响。
    const emotionKey =
      intent.naturalEmotion || intent.emotion || "neutral";
    const now = Date.now();
    const repeat = emotionKey === lastReactEmotion && now - lastReactAt < 2500;
    if (!repeat) {
      lastReactEmotion = emotionKey;
      lastReactAt = now;
      soullink.bridge.react(intent);
    }
    let speakPromise;
    try {
      speakPromise = soullink.bridge.speak({
        text: payload.speak_text || payload.reply || "",
        emotion: intent.naturalEmotion || intent.emotion,
        vad: intent.naturalVAD,
        intent
      });
    } catch (err) {
      speakPromise = Promise.resolve();
    }
    Promise.resolve(speakPromise).finally(() => {
      // 朗读结束（无论成败）通知 Python，用于语音对话期间恢复麦克风
      if (window.__bridge && window.__bridge.tts_played) {
        window.__bridge.tts_played();
      }
    });
  }
};

// 流式朗读：逐句排队播放（上一句播完才播下一句），全部播完通知 Python。
window.soullinkSpeak = (text) => {
  if (!soullinkEnabled() || !soullink.bridge) return;
  const t = String(text || "");
  if (!t.trim()) return;
  speakPending += 1;
  speakQueue = speakQueue
    .then(() =>
      soullink.bridge.speak({
        text: t,
        emotion: "neutral",
        vad: null,
        intent: null
      })
    )
    .catch(() => {})
    .finally(() => {
      speakPending -= 1;
      if (
        speakPending === 0 &&
        window.__bridge &&
        window.__bridge.tts_played
      ) {
        window.__bridge.tts_played();
      }
    });
};

// 流式结束后的情绪反应：只做表情/气泡，不再重复朗读。
window.soullinkReactOnly = (payload) => {
  if (!payload) return;
  if (payload.reply && !payload.no_bubble) {
    showChatReply(payload.reply, 6000);
  }
  if (payload.intent && soullinkEnabled() && soullink.bridge) {
    soullink.bridge.react(payload.intent);
  }
};

// ---------- layout ----------

function computeHeadRef() {
  if (!model) return;
  const b = model.getBounds();
  headX = b.x + b.width / 2;
  headY = b.y + b.height * 0.22;
  headTop = b.y + b.height * 0.04;
  headKnown = true;
  positionBubble();
  reportHead();
}

function positionBubble() {
  const bubbleH = bubbleEl.offsetHeight;
  if (headTop - 6 - bubbleH < 2) {
    bubbleEl.style.left = headX + "px";
    bubbleEl.style.top = headY + 8 + "px";
    bubbleEl.style.transform = "translate(-50%, 0)";
  } else {
    bubbleEl.style.left = headX + "px";
    bubbleEl.style.top = headTop - 6 + "px";
    bubbleEl.style.transform = "translate(-50%, -100%)";
  }
}

function reportHead() {
  const cw = window.innerWidth;
  const ch = window.innerHeight;
  if (window.__bridge && cw > 0 && ch > 0) {
    window.__bridge.set_head(headX / cw, headY / ch);
  }
}

function reposition() {
  const cw = window.innerWidth;
  const ch = window.innerHeight;
  if (!cw || !ch || !model) return;
  app.renderer.resize(cw, ch);
  model.update(0.001);
  const b = model.getBounds();
  model.x += cw / 2 - (b.x + b.width / 2);
  // 以“裁切后的角色底部”对齐窗口底部，把裁掉的部分（文字）留在窗口外。
  model.y +=
    (ch - STATUS_H - PAD - chatPanelH) -
    (b.y + b.height * (1 - cropBottom()));
  baseModelY = model.y;
  computeHeadRef();
}

function fitModel() {
  const cw = window.innerWidth;
  const ch = window.innerHeight;
  if (!cw || !ch || !model) return;
  app.renderer.resize(cw, ch);
  const regionH = ch - STATUS_H - PAD * 2;
  const s0 = baseScale || 1;
  model.scale.set(s0, s0);
  model.update(0.001);
  const b = model.getBounds();
  const fit = Math.min(
    (cw - PAD * 2) / Math.max(1, b.width * (1 - cropSide())),
    regionH / Math.max(1, b.height * (1 - cropBottom()))
  );
  const s1 = s0 * fit;
  baseScale = s1;
  model.scale.set(s1 * (currentScale || 1), s1 * (currentScale || 1));
  reposition();
}

function measureBounds() {
  const motions = ((modelConfig && modelConfig.motions) || []).map(
    (m) => m.group
  );
  const groups = motions.length ? motions : ["Idle"];
  let union = null;
  for (const m of groups) {
    stopAllMotions();
    try {
      model.motion(m);
    } catch (e) {
      continue;
    }
    for (let i = 0; i < 45; i++) {
      model.update(1 / 20);
      const b = model.getBounds();
      const x2 = b.x + b.width;
      const y2 = b.y + b.height;
      if (!union) {
        union = { x: b.x, y: b.y, x2: x2, y2: y2 };
      } else {
        union.x = Math.min(union.x, b.x);
        union.y = Math.min(union.y, b.y);
        union.x2 = Math.max(union.x2, x2);
        union.y2 = Math.max(union.y2, y2);
      }
    }
  }
  stopAllMotions();
  baseBounds = union
    ? { w: union.x2 - union.x, h: union.y2 - union.y }
    : { w: 440, h: 700 };
  reportBounds();
  // 窗口按裁切后的尺寸重排后，重新适配一次，避免缩放错位。
  setTimeout(() => fitModel(), 250);
  applyCurrentMotion();
  reposition();
}

function reportBounds() {
  if (window.__bridge && baseBounds) {
    window.__bridge.set_bounds(
      baseBounds.w * (1 - cropSide()),
      baseBounds.h * (1 - cropBottom())
    );
  }
}

function setScale(s) {
  currentScale = s;
  if (model && baseScale) {
    model.scale.set(baseScale * s, baseScale * s);
  }
  reposition();
}

// ---------- main loop ----------

function onFrame(ts) {
  requestAnimationFrame(onFrame);
  if (!model) return;
  const dt = lastTs ? Math.min(0.1, (ts - lastTs) / 1000) : 0.016;
  lastTs = ts;
  const t = ts / 1000;

  // Eye / head follow the mouse (target comes from Python, screen-space).
  const nx = clamp(eyeTargetX, -1, 1);
  const ny = clamp(eyeTargetY, -1, 1);
  eyeX += (nx - eyeX) * Math.min(1, dt * 6);
  eyeY += (ny - eyeY) * Math.min(1, dt * 6);

  if (!soullinkEnabled()) {
    setParam("ParamEyeBallX", eyeX);
    setParam("ParamEyeBallY", -eyeY * 0.9);
    setParam("ParamAngleX", eyeX * 22);
    setParam("ParamAngleY", -eyeY * 18);
    setParam("ParamBodyAngleX", eyeX * 5);

    // Gentle breathing so the character stays alive.
    setParam("ParamBreath", 0.5 + 0.5 * Math.sin((t * Math.PI * 2) / 4.5));

    model.update(dt);
    applyMotion(dt);
    applyTransition(dt);

    // Expressions: fade in/out the parameter values ourselves.
    if (activeFace || activePose) {
      exprFade = Math.min(1, exprFade + dt / 0.4);
      const inp = exprFade;
      for (const key of [activeFace, activePose]) {
        const params = key && EXPR_DATA[key];
        if (!params) continue;
        for (const p of params) setParam(p.id, p.value * inp);
      }
    }
  } else {
    model.update(dt);
    // Soullink 模式：身体/表情由 SDK 情绪引擎驱动，这里只补回鼠标追踪
    // （眼神全量跟随，头部/身体减半幅度，避免完全盖掉情绪姿态）。
    const speakingNow =
      soullink.bridge && typeof soullink.bridge.isSpeaking === "function"
        ? soullink.bridge.isSpeaking()
        : false;
    // 手势（待机/说话共用一套）：随机做扶脸/看手机/记笔记/前倾等姿势，
    // 引擎不再触发手势表情，全部由这里统一调度，保证归正且不重叠。
    const posePool = soullinkActions || ["hand", "phone", "notes", "lean"];
    const poseOptions = posePool.filter((name) => EXPR_DATA[name]);
    if (!poseName && poseOptions.length) {
      if (!speakingNow && t >= nextIdlePoseAt && Math.random() < 0.7) {
        poseName = poseOptions[Math.floor(Math.random() * poseOptions.length)];
        poseEndAt = t + 4 + Math.random() * 3;
        applyPose(poseName, true);
        nextIdlePoseAt = t + 25 + Math.random() * 20;
      } else if (speakingNow && t >= nextSpeakPoseAt && Math.random() < 0.7) {
        poseName = poseOptions[Math.floor(Math.random() * poseOptions.length)];
        poseEndAt = t + 3 + Math.random() * 2.5;
        applyPose(poseName, true);
        nextSpeakPoseAt = t + 4.5 + Math.random() * 3.5;
      }
    }
    if (poseName && t >= poseEndAt) {
      clearPose();
      nextIdlePoseAt = t + 25 + Math.random() * 20;
      nextSpeakPoseAt = t + 4.5 + Math.random() * 3.5;
    }
    // 手势看门狗：每帧把“非当前手势”的参数强制归零；
    // 没有手势时全部归零，确保引擎残留或旧手势一定归正。
    const poseKeys = soullinkActions || ["hand", "phone", "notes", "lean"];
    for (const key of poseKeys) {
      if (poseName && key === poseName) continue;
      const pp = EXPR_DATA[key];
      if (!pp) continue;
      for (const p of pp) setParam(p.id, 0);
    }
    // 说话时自然动作组合：
    // - 身体持续轻微摇晃（慢周期），头部滞后跟随身体；
    // - 偶尔一次“重点点头”（随机间隔、随机朝向、平滑包络）；
    // - 歪头每几秒随机微调一个角度；
    // - 重力下沉只在说话开始时发生，说完平滑回弹回正。
    if (speakingNow) {
      speakEnv = Math.min(1, speakEnv + dt * 2.5);
      bodyPhase += dt * ((Math.PI * 2) / 4.6);
      if (speakTiltZ === null) {
        // 说话开始时记录基准角度，之后用“基准 + 偏移”写入，避免叠加残留。
        speakTiltZ = getParam("ParamAngleZ");
        speakTiltY = getParam("ParamBodyAngleY");
        nextBurstAt = t + 1.2 + Math.random() * 1.5;
        tiltTarget = (Math.random() * 2 - 1) * 5;
        nextTiltAt = t + 3 + Math.random() * 2;
        lookPhase = "pause";
        lookPhaseEndAt = t + 0.4 + Math.random() * 0.6;
        lastXDir = Math.random() < 0.5 ? 1 : -1;
      }
      // 转头三段式：转向一侧 -> 回正 -> 短暂停留（随机时长）-> 换方向再来。
      if (lookPhase === "turn" && t >= lookPhaseEndAt) {
        lookTX = 0;
        lookDownTarget = 0;
        lookPhase = "return";
        lookPhaseEndAt = t + 0.7 + Math.random() * 0.5;
      } else if (lookPhase === "return" && t >= lookPhaseEndAt) {
        lookPhase = "pause";
        lookPhaseEndAt = t + 0.3 + Math.random() * 0.9;
      } else if (lookPhase === "pause" && t >= lookPhaseEndAt) {
        const dir = lastXDir >= 0 ? -1 : 1;
        lookTX = dir * (18 + Math.random() * 12);
        // 1/3 概率向下看（-15），2/3 不低头。
        lookDownTarget = Math.random() < 1 / 3 ? -15 : 0;
        lastXDir = dir;
        lookPhase = "turn";
        lookPhaseEndAt = t + 1.0 + Math.random() * 0.8;
      }
      if (!burst && t >= nextBurstAt) {
        burst = {
          start: t,
          dur: 1.3 + Math.random() * 0.7,
          sign: lookX >= 0 ? -1 : 1,
          amp: 0.7 + Math.random() * 0.4
        };
        nextBurstAt = t + 3.5 + Math.random() * 4.5;
      }
      if (t >= nextTiltAt) {
        tiltTarget = (Math.random() * 2 - 1) * 6;
        nextTiltAt = t + 4 + Math.random() * 3;
      }
      recZ = 0;
    } else {
      speakEnv = Math.max(0, speakEnv - dt * 2.5);
      burst = null;
      tiltTarget = 0;
      lookTX = 0;
      lookDownTarget = 0;
      lookPhase = "pause";
      if (speakEnv <= 0.001) {
        speakTiltZ = null;
        speakTiltY = null;
      }
    }
    // 身体微晃（幅度比待机大）+ 随机左右转头（不连续同向）。
    const bodySway = 8 * speakEnv * Math.sin(bodyPhase);
    const lookK = Math.min(1, dt * 3.2);
    lookX += (lookTX - lookX) * lookK;
    lookDownY += (lookDownTarget - lookDownY) * lookK;
    // 重点点头：平滑包络，点头时同时低头，朝向随机。
    let burstEnv = 0;
    if (burst) {
      const p = (t - burst.start) / burst.dur;
      if (p >= 1) {
        burst = null;
      } else {
        burstEnv = Math.sin(Math.PI * Math.min(1, p));
      }
    }
    const burstTurn = burst ? burst.sign * 9 * burst.amp * burstEnv : 0;
    // 歪头姿势微调：缓慢过渡。
    tiltCur += (tiltTarget - tiltCur) * Math.min(1, dt * 2);
    // 重力弹簧：说话时身体稍微下沉（带轻微回弹），说完平滑弹回。
    const gravTarget = 5 * (model.scale.x || 1) * speakEnv;
    const gk = 22;
    const gd = speakingNow ? 3.2 : 5.5;
    gravV += (gravTarget - gravY) * gk * dt - gravV * gd * dt;
    gravY += gravV * dt;
    if (baseModelY !== null) model.y = baseModelY + gravY;
    if (speakTiltZ !== null) {
      setParam(
        "ParamAngleZ",
        speakTiltZ +
          tiltCur * speakEnv +
          3 * speakEnv * Math.sin(bodyPhase + 1.2)
      );
      setParam(
        "ParamBodyAngleY",
        speakTiltY + bodySway + burstTurn * 0.5
      );
    }
    // 说完话回正：把说话时残留的歪头快速拉回 0。
    if (!speakingNow && recZ < 1) {
      recZ = Math.min(1, recZ + dt * 2.2);
      setParam("ParamAngleZ", getParam("ParamAngleZ") * (1 - recZ * 0.9));
    }
    setParam("ParamEyeBallX", eyeX);
    setParam("ParamEyeBallY", -eyeY * 0.9);
    setParam("ParamAngleX", eyeX * 11 + lookX + burstTurn);
    setParam("ParamAngleY", -eyeY * 9 + lookDownY);
    setParam(
      "ParamBodyAngleX",
      eyeX * 2.5 + 4 * speakEnv * Math.cos(bodyPhase)
    );
  }

  app.render();
}

// ---------- model loading ----------

function modelUrl(cfg, relPath) {
  const base = MODEL_ROOT + encodeURIComponent(cfg.id) + "/";
  return (
    base +
    String(relPath)
      .split("/")
      .map((seg) => encodeURIComponent(seg))
      .join("/")
  );
}

async function loadExpressions() {
  const map = Object.assign(
    {},
    (modelConfig && modelConfig.expressions) || {},
    (modelConfig && modelConfig.effects) || {}
  );
  const entries = await Promise.all(
    Object.entries(map).map(async ([key, info]) => {
      const file = typeof info === "string" ? info : info.file;
      const resp = await fetch(modelUrl(modelConfig, file));
      const obj = await resp.json();
      const valueOverride =
        typeof info === "object" && info.value !== undefined
          ? info.value
          : null;
      const params = (obj.Parameters || []).map((p) => ({
        id: p.Id,
        value: valueOverride !== null ? valueOverride : p.Value,
      }));
      return [key, params];
    })
  );
  EXPR_DATA = Object.fromEntries(entries);
  applyEffects();
}

async function loadModel(cfg) {
  modelConfig = cfg;
  if (model) {
    try {
      model.destroy();
    } catch (e) {}
    model = null;
  }
  EXPR_DATA = {};
  activeFace = null;
  activePose = null;
  manualExpression = null;
  manualMotion = null;
  presetMotion = null;
  motionActive = "idle";
  model = await PIXI.live2d.Live2DModel.from(modelUrl(cfg, cfg.model3), {
    autoInteract: false,
    motionPreload: "NONE",
  });
  app.stage.addChild(model);
  await loadExpressions();
  fitModel();
  baseScale = model.scale.x;
  setPetState(currentState);
  if (soullinkEnabled() && soullink.bridge) {
    soullink.bridge.setModel(model);
  }
  setTimeout(() => measureBounds(), 150);
}

function setupEvents() {
  canvas.addEventListener("mousedown", (e) => {
    e.preventDefault();
    if (window.__bridge) window.__bridge.drag_start();
  });
  canvas.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    if (window.__bridge) window.__bridge.context_menu(0, 0);
  });
  if (!window.__bridge) {
    window.addEventListener("mousemove", (e) => {
      window.setEye(
        (e.clientX / canvas.clientWidth - 0.5) * 2,
        (e.clientY / canvas.clientHeight - 0.5) * 2
      );
    });
  }
  window.addEventListener("resize", reposition);
}

// Python -> JS API (called with page.runJavaScript).
window.setEye = (x, y) => {
  eyeTargetX = clamp(x, -1, 1);
  eyeTargetY = clamp(y, -1, 1);
};
window.setModelConfig = (cfg) => {
  if (!modelConfig && cfg && cfg.model3) {
    modelConfig = cfg;
  }
};
window.setActionOverrides = (obj) => {
  actionOverrides = obj || {};
  if (model && modelConfig) applyStateVisuals(currentState);
};
window.playMotion = playMotion;
window.stopMotion = stopMotion;
window.setPetState = setPetState;
window.setExpression = setExpression;
window.notify = showBubble;
window.setChatMode = setChatMode;
window.showChatReply = showChatReply;
window.chatReact = chatReact;

// 动作幅度（0.5x - 2x）：内置动作引擎的摇晃/姿态统一按此放大。
window.setMotionIntensity = (v) => {
  const n = Number(v);
  motionIntensity = Number.isFinite(n) ? Math.min(2, Math.max(0.5, n)) : 1;
};

// 歪头幅度（0.25x - 3x）：待机歪头与说话时额外歪头统一按此放大。
window.setHeadTiltGain = (v) => {
  const n = Number(v);
  headTiltGain = Number.isFinite(n) ? Math.min(3, Math.max(0.25, n)) : 1;
};

// 从脚底往上裁切（百分比 0-95），裁掉的底部留在窗口外。
window.setCropBottom = (v) => {
  const n = Number(v);
  userCropBottom = Number.isFinite(n) ? Math.min(0.95, Math.max(0, n)) : 0;
  if (model) {
    fitModel();
    reportBounds();
  }
};

// 从两侧往中间裁切（百分比 0-45，每侧），裁掉的部分留在窗口外。
window.setCropSide = (v) => {
  const n = Number(v);
  userCropSide = Number.isFinite(n) ? Math.min(0.45, Math.max(0, n)) : 0;
  if (model) {
    reportBounds();
    reposition();
  }
};

// 当前模型的 Soullink 待机动作姿势列表（每个模型可自定义）。
window.setSoullinkActions = (keys) => {
  soullinkActions = Array.isArray(keys) && keys.length ? keys : null;
};
window.setScale = setScale;

const chatMicEl = document.getElementById("chat-mic");

window.setVoiceInputEnabled = (on, keyLabel) => {
  chatMicEl.classList.toggle("show", !!on);
  if (!on) chatMicEl.classList.remove("recording");
  chatMicEl.title = keyLabel
    ? `按住 ${keyLabel} 说话，松开发送（或点击录音）`
    : "语音输入";
};

window.setVoiceRecording = (on) => {
  chatMicEl.classList.toggle("recording", !!on);
};

window.setVoiceText = (text) => {
  if (typeof text !== "string") return;
  chatInputEl.value = text;
  chatInputEl.focus();
  chatInputEl.setSelectionRange(text.length, text.length);
};

chatMicEl.addEventListener("click", () => {
  if (window.__bridge) window.__bridge.voice_toggle();
});

document.getElementById("chat-send").addEventListener("click", sendChat);
chatInputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendChat();
});
document.getElementById("chat-back").addEventListener("click", () => {
  if (window.__bridge) window.__bridge.back_to_codex();
});

function connectBridge() {
  if (typeof qt === "undefined" || !qt.webChannelTransport) {
    return false;
  }
  new QWebChannel(qt.webChannelTransport, (channel) => {
    const pet = channel.objects.pet;
    if (!pet) return;
    window.__bridge = pet;
    if (baseBounds) reportBounds();
    window.__ready = true;
  });
  return true;
}

async function init() {
  app = new PIXI.Application({
    view: canvas,
    width: 520,
    height: 760,
    transparent: true,
    antialias: true,
    autoStart: false,
  });

  setupEvents();
  connectBridge();

  // Wait for the model config pushed from Python (may take a moment).
  const deadline = Date.now() + 12000;
  while (!modelConfig) {
    if (Date.now() > deadline) break;
    await new Promise((r) => setTimeout(r, 100));
  }
  if (!modelConfig) {
    window.__ready = true;
    window.__error = "no model config";
    return;
  }

  await loadModel(modelConfig);
  requestAnimationFrame(onFrame);
  window.__ready = true;
}

init().catch((err) => {
  window.__ready = true;
  window.__error = String(err && err.stack ? err.stack : err);
});
