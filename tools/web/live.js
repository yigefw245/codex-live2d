"use strict";

const MODEL_URL = "/model/yumi/yumi.model3.json";
const STATUS_H = 0;
const PAD = 12;

const EXPR_FILES = {
  heart: "爱心眼.exp3.json",
  star: "星星眼.exp3.json",
  tear: "眼泪.exp3.json",
  teary: "泪汪汪.exp3.json",
  wry: "歪嘴.exp3.json",
  catmouth: "猫猫嘴.exp3.json",
  eyepatch: "眼罩.exp3.json",
  black: "黑脸.exp3.json",
  swirl: "蚊香眼.exp3.json",
  tongue: "舌头伸出.exp3.json",
  mic: "拿话筒.exp3.json",
  bend: "俯身按键.exp3.json",
  raiseL: "抬手左.exp3.json",
  raiseR: "抬手右.exp3.json",
  dog: "漂浮小狗.exp3.json",
  hair1: "短发1.exp3.json",
  hair2: "短发2.exp3.json",
};

const canvas = document.getElementById("stage");
const bubbleEl = document.getElementById("bubble");
const chatboxEl = document.getElementById("chatbox");
const chatInputEl = document.getElementById("chat-input");
let bubbleTimer = null;
let chatPanelH = 0;
let chatReactTimer = null;

let app = null;
let model = null;
let currentState = "idle";
let EXPR_DATA = {};
let activeExpression = null;
let prevExpression = null;
let exprFade = 0;
let frameCount = 0;
let lastReportedFrame = -1;
let motionActive = "idle";
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

// Custom motion engine: drives parameters directly, so animations work
// even when the renderer library fails to load the model's motion files.
function applyMotion(dt) {
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
  if (transitionT >= 1) return;
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

function statusExpressionFor(state) {
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
    case "completed":
      return null;
    default:
      return null;
  }
}

let manualExpression = null;

function applyExpressionTarget(name) {
  name = name && name !== "none" ? name : null;
  if (name === activeExpression && exprFade > 0.01) return;
  prevExpression = activeExpression;
  activeExpression = name;
  exprFade = 0;
}

function setPetState(name) {
  currentState = name;
  motionActive =
    name === "completed" || name === "interact"
      ? "wave"
      : name === "thinking"
      ? "thinking"
      : name === "working"
      ? "working"
      : "idle";
  motionClock = 0;
  const target = manualExpression || statusExpressionFor(name);
  applyExpressionTarget(target);
  transitionT = 0;
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
  applyExpressionTarget(manualExpression || statusExpressionFor(currentState));
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

function chatReact(emotion) {
  if (chatReactTimer) clearTimeout(chatReactTimer);
  if (window.__bridge) window.__bridge.set_diag("chatReact:" + emotion);
  const map = {
    happy: { motion: "wave", expr: "heart" },
    sad: { motion: "sad", expr: "tear" },
    angry: { motion: "angry", expr: "black" },
    thinking: { motion: "thinking", expr: "star" },
    surprised: { motion: "surprised", expr: "swirl" },
    neutral: { motion: "nod", expr: "heart" },
  };
  const m = map[emotion] || map.neutral;
  currentState = "chat-" + emotion;
  motionActive = m.motion;
  motionClock = 0;
  applyExpressionTarget(m.expr);
  transitionT = 0;
  chatReactTimer = setTimeout(() => {
    motionActive = "idle";
    motionClock = 0;
    applyExpressionTarget("heart");
    transitionT = 0;
  }, 8000);
}

function sendChat() {
  const text = chatInputEl.value.trim();
  if (!text || !window.__bridge) return;
  chatInputEl.value = "";
  showBubble("…", 60000);
  window.__bridge.send_chat(text);
}

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
    window.__bridge.set_head(
      headX / cw,
      headY / ch
    );
  }
}

function reportDiag() {
  if (window.__bridge) {
    window.__bridge.set_diag(
      JSON.stringify({
        ready: window.__ready,
        error: window.__error || null,
        bridge: !!window.__bridge,
        model: !!model,
        expCount: Object.keys(EXPR_DATA).length,
        events: typeof canvas.addEventListener === "function",
        frameCount: frameCount,
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
  const motions = ["Idle", "Tap"];
  let union = null;
  for (const m of motions) {
    stopAllMotions();
    model.motion(m);
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
  model.motion("Idle");
  baseBounds = union
    ? { w: union.x2 - union.x, h: union.y2 - union.y }
    : { w: 440, h: 700 };
  reportBounds();
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
  if (prevExpression || activeExpression) {
    exprFade = Math.min(1, exprFade + dt / 0.4);
    const out = activeExpression ? 1 - exprFade : 0;
    const inp = activeExpression ? exprFade : 0;
    if (prevExpression && out > 0 && EXPR_DATA[prevExpression]) {
      for (const p of EXPR_DATA[prevExpression]) {
        setParam(p.id, p.value * out);
      }
    }
    if (activeExpression && inp > 0 && EXPR_DATA[activeExpression]) {
      for (const p of EXPR_DATA[activeExpression]) {
        setParam(p.id, p.value * inp);
      }
    }
    if (exprFade >= 1) prevExpression = null;
  }

  app.render();
}

async function loadExpressions() {
  const entries = await Promise.all(
    Object.entries(EXPR_FILES).map(async ([name, file]) => {
      const resp = await fetch(
        "/model/yumi/" + encodeURIComponent(file)
      );
      const obj = await resp.json();
      const params = (obj.Parameters || []).map((p) => ({
        id: p.Id,
        value: p.Value,
      }));
      return [name, params];
    })
  );
  EXPR_DATA = Object.fromEntries(entries);
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
window.setPetState = setPetState;
window.setExpression = setExpression;
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

  model = await PIXI.live2d.Live2DModel.from(MODEL_URL, {
    autoInteract: false,
    motionPreload: "NONE",
  });
  app.stage.addChild(model);
  await loadExpressions();
  fitModel();
  baseScale = model.scale.x;
  model.motion("Idle");
  setTimeout(() => measureBounds(), 150);
  requestAnimationFrame(onFrame);
  window.__ready = true;
  setTimeout(reportDiag, 400);
}

init().catch((err) => {
  window.__ready = true;
  window.__error = String(err && err.stack ? err.stack : err);
});
