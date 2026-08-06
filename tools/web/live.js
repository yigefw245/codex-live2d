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
let frameCount = 0;
let lastReportedFrame = -1;

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function easeInOut(t) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

// ---------- model config helpers ----------

function exprFile(key) {
  const map = (modelConfig && modelConfig.expressions) || {};
  const info = map[key];
  if (!info) return null;
  return typeof info === "string" ? info : info.file;
}

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
    setParam("ParamAngleZ", 11 + 2.5 * Math.sin((t * Math.PI * 2) / 3.5));
    setParam("ParamBodyAngleY", 3.2 * Math.sin((t * Math.PI * 2) / 4));
    setParam("ParamEyeBallY", 0.6 + 0.2 * Math.sin((t * Math.PI * 2) / 2.4));
    setParam("Paramdown1", 0);
  } else if (motionActive === "working") {
    // Busy typing pose: bent forward with a quick bobbing rhythm.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0.8 + 0.1 * Math.sin((t * Math.PI * 2) / 1.1));
    setParam("ParamAngleZ", 3.5 * Math.sin((t * Math.PI * 2) / 3.2));
    setParam("ParamBodyAngleY", 2.6 * Math.sin((t * Math.PI * 2) / 0.9));
    setParam("ParamAngleX", 2.5 * Math.sin((t * Math.PI * 2) / 1.3));
  } else if (motionActive === "sad") {
    // Drooping shoulders, looking down a little.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0.72 + 0.08 * Math.sin((t * Math.PI * 2) / 3));
    setParam("ParamAngleZ", 3.5 * Math.sin((t * Math.PI * 2) / 4));
    setParam("ParamBodyAngleY", 1.6 * Math.sin((t * Math.PI * 2) / 3));
  } else if (motionActive === "angry") {
    // Slight trembling, one hand clenched near the chest.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0.65 + 0.08 * Math.sin((t * Math.PI * 2) / 0.8));
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0);
    setParam("ParamAngleZ", 3.2 * Math.sin((t * Math.PI * 2) / 0.45));
    setParam("ParamBodyAngleY", 4.2 * Math.sin((t * Math.PI * 2) / 0.6));
  } else if (motionActive === "surprised") {
    // Leaning back, head slightly tilted.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0);
    setParam("ParamAngleZ", -6.5 + 1.5 * Math.sin((t * Math.PI * 2) / 1.2));
    setParam("ParamAngleX", -7);
    setParam("ParamBodyAngleY", 0);
  } else if (motionActive === "nod") {
    // Gentle friendly nod for neutral replies.
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam("Paramdown1", 0.22 + 0.06 * Math.sin((t * Math.PI * 2) / 3.2));
    setParam("ParamAngleZ", 1.5 * Math.sin((t * Math.PI * 2) / 4));
    setParam("ParamBodyAngleY", 0.8 * Math.sin((t * Math.PI * 2) / 3.2));
  } else {
    setParam("ParamarmupL", 0);
    setParam("ParamarmupR", 0);
    setParam("Paramanime", 0);
    setParam("ParamAngleZ", 4.5 * Math.sin((t * Math.PI * 2) / 7));
    setParam("ParamAngleX", 3.5 * Math.sin((t * Math.PI * 2) / 9 + 1));
    setParam("ParamBodyAngleY", 0);
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
    currentState === "completed" || currentState === "chat-happy" ? 1.4 : 0.8;
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
  if (window.__bridge) window.__bridge.set_state_ack(name);
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
  if (chatReactTimer) clearTimeout(chatReactTimer);
  if (window.__bridge) window.__bridge.set_diag("chatReact:" + emotion);
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
  chatReactTimer = setTimeout(() => {
    currentState = prevState;
    applyStateVisuals(prevState);
  }, 8000);
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

function reportDiag() {
  if (window.__bridge) {
    let wm = null;
    try {
      if (model && model.internalModel && model.internalModel.coreModel) {
        wm = +model.internalModel.coreModel
          .getParameterValueById("Param85")
          .toFixed(3);
      }
    } catch (e) {}
    window.__bridge.set_diag(
      JSON.stringify({
        ready: window.__ready,
        error: window.__error || null,
        bridge: !!window.__bridge,
        model: !!model,
        modelId: modelConfig ? modelConfig.id : null,
        expCount: Object.keys(EXPR_DATA).length,
        frameCount: frameCount,
        expr: {
          state: currentState,
          face: activeFace,
          pose: activePose,
          manual: manualExpression,
          fade: +exprFade.toFixed(3),
        },
        motion: { active: motionActive, preset: presetMotion, manual: manualMotion },
        wm: wm,
      })
    );
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
  model.y += (ch - STATUS_H - PAD - chatPanelH) - (b.y + b.height);
  computeHeadRef();
}

function fitModel() {
  const cw = window.innerWidth;
  const ch = window.innerHeight;
  if (!cw || !ch || !model) return;
  app.renderer.resize(cw, ch);
  const regionH = ch - STATUS_H - PAD * 2;
  model.update(0.001);
  const b = model.getBounds();
  const fit = Math.min(
    (cw - PAD * 2) / Math.max(1, b.width),
    regionH / Math.max(1, b.height)
  );
  model.scale.set(model.scale.x * fit, model.scale.y * fit);
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
  applyCurrentMotion();
  reposition();
}

function reportBounds() {
  if (window.__bridge && baseBounds) {
    window.__bridge.set_bounds(baseBounds.w, baseBounds.h);
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
  frameCount++;
  if (frameCount - lastReportedFrame >= 300) {
    lastReportedFrame = frameCount;
    reportDiag();
  }
  const dt = lastTs ? Math.min(0.1, (ts - lastTs) / 1000) : 0.016;
  lastTs = ts;
  const t = ts / 1000;

  // Eye / head follow the mouse (target comes from Python, screen-space).
  const nx = clamp(eyeTargetX, -1, 1);
  const ny = clamp(eyeTargetY, -1, 1);
  eyeX += (nx - eyeX) * Math.min(1, dt * 6);
  eyeY += (ny - eyeY) * Math.min(1, dt * 6);
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
  setTimeout(() => measureBounds(), 150);
  reportDiag();
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
window.switchModel = async (id) => {
  if (!id) return;
  try {
    const resp = await fetch(modelUrl({ id: id }, "model.json"));
    const cfg = await resp.json();
    if (!cfg || !cfg.model3) return;
    await loadModel(cfg);
  } catch (err) {
    window.__error = String(err && err.stack ? err.stack : err);
  }
};
window.playMotion = playMotion;
window.stopMotion = stopMotion;
window.setPetState = setPetState;
window.setExpression = setExpression;
window.notify = showBubble;
window.setChatMode = setChatMode;
window.showChatReply = showChatReply;
window.chatReact = chatReact;
window.refit = reposition;
window.setScale = setScale;

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
    reportDiag();
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
    reportDiag();
    return;
  }

  await loadModel(modelConfig);
  requestAnimationFrame(onFrame);
  window.__ready = true;
  setTimeout(reportDiag, 400);
}

init().catch((err) => {
  window.__ready = true;
  window.__error = String(err && err.stack ? err.stack : err);
});
