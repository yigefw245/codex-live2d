// Browser-side Soullink Emotion SDK bridge.
// Bundled with esbuild into tools/web/lib/soullink-emotion.esm.js and loaded
// from live.js via dynamic import(). It owns a Soullink session (engine +
// runtime-core), applies the engine's parameter/action output to the existing
// pixi-live2d-display model, and plays TTS through the local Node sidecar.
import {
  loadModelProfile,
  motionStylePresets
} from "@soullink-emotion/engine";
import {
  createBrowserAudioSink,
  createRafClock,
  createSoullinkSession
} from "@soullink-emotion/runtime-core";

let session = null;
let modelRef = null;
let lastNativeToken = -1;
let started = false;
let paramsHookAttached = false;
let headTiltGain = 1;

function applyParamsHook() {
  const core = modelRef?.internalModel?.coreModel;
  if (!core || typeof core.setParameterValueById !== "function") return;
  const snapshot = session?.getRuntimeSnapshot?.();
  if (!snapshot) return;
  const suppressed = new Set(snapshot.nativeAnimation?.suppressParamIds ?? []);
  for (const [id, value] of Object.entries(snapshot.live2dParams || {})) {
    if (suppressed.has(id)) continue;
    if (typeof core.getParameterIndex === "function" && core.getParameterIndex(id) < 0) {
      continue;
    }
    try {
      core.setParameterValueById(id, value, 1);
    } catch {
      // ignore unknown parameters
    }
  }
  // 歪头幅度：ParamAngleZ 整体放大；说话（SPEAKING）时再叠一个明显的歪头角度。
  if (
    !suppressed.has("ParamAngleZ") &&
    typeof core.getParameterIndex === "function" &&
    core.getParameterIndex("ParamAngleZ") >= 0
  ) {
    let z = core.getParameterValueById("ParamAngleZ");
    if (headTiltGain !== 1) {
      z = Math.max(-30, Math.min(30, z * headTiltGain));
    }
    if (snapshot.state === "SPEAKING") {
      z = Math.max(-30, Math.min(30, z + 7 * headTiltGain));
    }
    try {
      core.setParameterValueById("ParamAngleZ", z, 1);
    } catch {
      // ignore
    }
  }
}

function applyNativeAnimation(snapshot) {
  const directive = snapshot?.nativeAnimation;
  if (!directive) return;
  if (directive.token === lastNativeToken) return;
  lastNativeToken = directive.token;

  if (directive.expression && typeof modelRef.expression === "function") {
    try {
      void Promise.resolve(modelRef.expression(directive.expression)).catch(() => {});
    } catch {
      // ignore
    }
  }
  if (directive.motion && typeof modelRef.motion === "function") {
    const priority =
      directive.motion.priority === "force"
        ? 3
        : directive.motion.priority === "idle"
          ? 1
          : 2;
    try {
      void Promise.resolve(
        modelRef.motion(directive.motion.group, directive.motion.index ?? 0, priority)
      ).catch(() => {});
    } catch {
      // ignore
    }
  } else if (directive.motion === null) {
    // 原生动作（如循环挥手）在指令结束后要停掉，避免一直播放。
    try {
      if (modelRef.motionManager && typeof modelRef.motionManager.stopAllMotions === "function") {
        modelRef.motionManager.stopAllMotions();
      } else if (
        modelRef.internalModel?.motionManager &&
        typeof modelRef.internalModel.motionManager.stopAllMotions === "function"
      ) {
        modelRef.internalModel.motionManager.stopAllMotions();
      }
    } catch {
      // ignore
    }
  }
}

function attachParamsHook(model) {
  if (paramsHookAttached && model === modelRef) return;
  detachParamsHook();
  modelRef = model;
  const internal = model?.internalModel;
  if (internal && typeof internal.on === "function") {
    internal.on("beforeModelUpdate", applyParamsHook);
    paramsHookAttached = true;
  }
  lastNativeToken = -1;
}

function detachParamsHook() {
  if (modelRef?.internalModel && paramsHookAttached && typeof modelRef.internalModel.off === "function") {
    try {
      modelRef.internalModel.off("beforeModelUpdate", applyParamsHook);
    } catch {
      // ignore
    }
  }
  paramsHookAttached = false;
}

async function start(config) {
  if (started) return true;
  if (!config || !config.profileUrl || !config.ttsUrl) {
    throw new Error("soullink bridge: missing profileUrl or ttsUrl");
  }
  headTiltGain =
    typeof config.headTiltGain === "number" ? config.headTiltGain : 1;

  const { profile } = await loadModelProfile(config.profileUrl);
  const style = motionStylePresets[config.motionStyle] || motionStylePresets.natural;

  session = createSoullinkSession({
    profile,
    persona: {
      name: "yumi",
      profile: config.personaProfile || "",
      variantByEmotion: {}
    },
    clock: createRafClock(),
    audio: createBrowserAudioSink(),
    tts: {
      async synthesize(text, ctx) {
        const response = await fetch(config.ttsUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text,
            emotion: ctx?.emotion || ""
          })
        });
        if (!response.ok) {
          throw new Error("TTS HTTP " + response.status);
        }
        const data = await response.json();
        if (!data.audio_b64) {
          throw new Error("TTS returned no audio");
        }
        const binary = atob(data.audio_b64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i += 1) {
          bytes[i] = binary.charCodeAt(i);
        }
        return {
          bytes: bytes.buffer,
          durationSec: Number(data.duration_sec) || 0
        };
      }
    },
    motionStyle: style,
    onSnapshot(snapshot) {
      if (snapshot?.runtime) applyNativeAnimation(snapshot.runtime);
    }
  });

  session.setAutoVoiceEnabled(true);
  // 说话（SPEAKING）状态下 SDK 会主动压低情绪层权重并关闭空闲手势，
  // 导致回复时身体几乎不动。提高参数/身体增益，让情绪姿态与表情清晰可见。
  session.setParameterGain(2.2);
  session.setBodyMotionGain(2.8);
  if (typeof options.lipSyncGain === "number") {
    session.setLipSyncGain(options.lipSyncGain);
  }
  session.start();
  started = true;
  if (modelRef) attachParamsHook(modelRef);
  return true;
}

function stop() {
  if (!session) return;
  try {
    session.stop();
  } catch {
    // ignore
  }
  session = null;
  started = false;
  lastNativeToken = -1;
  detachParamsHook();
}

function react(intent) {
  if (!session || !intent) return;
  session.triggerIntent(intent);
}

function speak(payload) {
  if (!session || !payload || !payload.text) return Promise.resolve();
  return session
    .speak({
      text: payload.text,
      emotion: payload.emotion,
      vad: payload.vad,
      intent: payload.intent || null,
      planSpeakingMotion: false
    })
    .catch(() => {});
}

function stopVoice() {
  session?.stopVoice();
}

window.__soullink = {
  start,
  stop,
  setModel(model) {
    if (started) attachParamsHook(model);
    else modelRef = model;
  },
  react,
  speak,
  stopVoice,
  isActive: () => started
};

export {};
