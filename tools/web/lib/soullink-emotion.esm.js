var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);

// node_modules/@soullink-emotion/engine/dist/chunk-WF7NFOHV.js
var actionUnitDefinitions = [
  { key: "au01InnerBrowRaiser", code: "AU01", label: "Inner Brow Raiser", group: "brow", min: 0, max: 1 },
  { key: "au02OuterBrowRaiser", code: "AU02", label: "Outer Brow Raiser", group: "brow", min: 0, max: 1 },
  { key: "au04BrowLowerer", code: "AU04", label: "Brow Lowerer", group: "brow", min: 0, max: 1 },
  { key: "au05UpperLidRaiser", code: "AU05", label: "Upper Lid Raiser", group: "eye", min: 0, max: 1 },
  { key: "au06CheekRaiser", code: "AU06", label: "Cheek Raiser", group: "eye", min: 0, max: 1 },
  { key: "au07LidTightener", code: "AU07", label: "Lid Tightener", group: "eye", min: 0, max: 1 },
  { key: "au09NoseWrinkler", code: "AU09", label: "Nose Wrinkler", group: "midface", min: 0, max: 1 },
  { key: "au10UpperLipRaiser", code: "AU10", label: "Upper Lip Raiser", group: "mouth", min: 0, max: 1 },
  { key: "au12LipCornerPuller", code: "AU12", label: "Lip Corner Puller", group: "mouth", min: 0, max: 1 },
  { key: "au14Dimpler", code: "AU14", label: "Dimpler", group: "mouth", min: 0, max: 1 },
  { key: "au15LipCornerDepressor", code: "AU15", label: "Lip Corner Depressor", group: "mouth", min: 0, max: 1 },
  { key: "au17ChinRaiser", code: "AU17", label: "Chin Raiser", group: "mouth", min: 0, max: 1 },
  { key: "au18LipPucker", code: "AU18", label: "Lip Pucker", group: "mouth", min: 0, max: 1 },
  { key: "au20LipStretcher", code: "AU20", label: "Lip Stretcher", group: "mouth", min: 0, max: 1 },
  { key: "au23LipTightener", code: "AU23", label: "Lip Tightener", group: "mouth", min: 0, max: 1 },
  { key: "au24LipPressor", code: "AU24", label: "Lip Pressor", group: "mouth", min: 0, max: 1 },
  { key: "au25LipsPart", code: "AU25", label: "Lips Part", group: "mouth", min: 0, max: 1 },
  { key: "au26JawDrop", code: "AU26", label: "Jaw Drop", group: "mouth", min: 0, max: 1 },
  { key: "au27MouthStretch", code: "AU27", label: "Mouth Stretch", group: "mouth", min: 0, max: 1 },
  { key: "au45Blink", code: "AU45", label: "Blink", group: "eye", min: 0, max: 1 },
  { key: "gazeX", code: "GazeX", label: "Gaze X", group: "extension", min: -1, max: 1 },
  { key: "gazeY", code: "GazeY", label: "Gaze Y", group: "extension", min: -1, max: 1 },
  { key: "headX", code: "HeadX", label: "Head X", group: "extension", min: -1, max: 1 },
  { key: "headY", code: "HeadY", label: "Head Y", group: "extension", min: -1, max: 1 },
  { key: "headZ", code: "HeadZ", label: "Head Z", group: "extension", min: -1, max: 1 },
  { key: "bodyX", code: "BodyX", label: "Body X", group: "extension", min: -1, max: 1 },
  { key: "bodyY", code: "BodyY", label: "Body Y", group: "extension", min: -1, max: 1 },
  { key: "bodyZ", code: "BodyZ", label: "Body Z", group: "extension", min: -1, max: 1 },
  { key: "blush", code: "Blush", label: "Blush", group: "extension", min: 0, max: 1 },
  { key: "tear", code: "Tear", label: "Tear", group: "extension", min: 0, max: 1 },
  { key: "sweat", code: "Sweat", label: "Sweat", group: "extension", min: 0, max: 1 },
  { key: "breath", code: "Breath", label: "Breath", group: "extension", min: 0, max: 1 }
];
var actionUnitKeys = actionUnitDefinitions.map((definition) => definition.key);
function createDefaultFACSState(overrides = {}) {
  return {
    browInnerUp: 0,
    browOuterUp: 0,
    browDown: 0,
    eyeOpen: 1,
    eyeSmile: 0,
    eyeSquint: 0,
    eyeBlinkL: 0,
    eyeBlinkR: 0,
    mouthSmile: 0.04,
    mouthFrown: 0,
    mouthOpen: 0,
    mouthPucker: 0,
    gazeX: 0,
    gazeY: 0,
    headX: 0,
    headY: 0,
    headZ: 0,
    bodyX: 0,
    bodyY: 0,
    bodyZ: 0,
    blush: 0,
    tear: 0,
    sweat: 0,
    breath: 0.5,
    ...overrides
  };
}
var defaultFACSState = createDefaultFACSState();
function createDefaultActionUnitState(overrides = {}) {
  return {
    au01InnerBrowRaiser: 0,
    au02OuterBrowRaiser: 0,
    au04BrowLowerer: 0,
    au05UpperLidRaiser: 0,
    au06CheekRaiser: 0,
    au07LidTightener: 0,
    au09NoseWrinkler: 0,
    au10UpperLipRaiser: 0,
    au12LipCornerPuller: 0,
    au14Dimpler: 0,
    au15LipCornerDepressor: 0,
    au17ChinRaiser: 0,
    au18LipPucker: 0,
    au20LipStretcher: 0,
    au23LipTightener: 0,
    au24LipPressor: 0,
    au25LipsPart: 0,
    au26JawDrop: 0,
    au27MouthStretch: 0,
    au45Blink: 0,
    gazeX: 0,
    gazeY: 0,
    headX: 0,
    headY: 0,
    headZ: 0,
    bodyX: 0,
    bodyY: 0,
    bodyZ: 0,
    blush: 0,
    tear: 0,
    sweat: 0,
    breath: 0.5,
    ...overrides
  };
}
var defaultActionUnitState = createDefaultActionUnitState();
function clamp(value, min = -Infinity, max = Infinity) {
  return Math.min(max, Math.max(min, value));
}
function clamp01(value) {
  return clamp(value, 0, 1);
}
function lerp(from, to, t) {
  return from + (to - from) * t;
}
var directionalKeys = /* @__PURE__ */ new Set([
  "gazeX",
  "gazeY",
  "headX",
  "headY",
  "headZ",
  "bodyX",
  "bodyY",
  "bodyZ"
]);
var facsKeys = Object.keys(createDefaultFACSState());
function facsRangeForKey(key) {
  if (directionalKeys.has(key)) return [-1, 1];
  if (key === "eyeOpen") return [0, 1.25];
  return [0, 1];
}
function clampFACSValue(key, value) {
  const [min, max] = facsRangeForKey(key);
  return clamp(value, min, max);
}
function clampFACSState(state) {
  const result = { ...state };
  for (const key of Object.keys(result)) {
    const value = result[key];
    if (typeof value === "number") {
      result[key] = clampFACSValue(key, value);
    }
  }
  return result;
}
function addFACS(base, overlay, weight = 1) {
  const result = { ...base };
  for (const key of Object.keys(overlay)) {
    const value = overlay[key];
    if (typeof value === "number") {
      result[key] = (result[key] ?? 0) + value * weight;
    }
  }
  return clampFACSState(result);
}
function scaleFACS(state, scale) {
  const result = {};
  for (const key of Object.keys(state)) {
    const value = state[key];
    if (typeof value === "number") result[key] = value * scale;
  }
  return clampFACSState(result);
}
function scaleFACSFromNeutral(state, scale) {
  const result = {};
  for (const key of Object.keys(state)) {
    const value = state[key];
    if (typeof value === "number") {
      result[key] = lerp(defaultFACSState[key], value, scale);
    }
  }
  return clampFACSState(result);
}
var directionalKeys2 = /* @__PURE__ */ new Set([
  "gazeX",
  "gazeY",
  "headX",
  "headY",
  "headZ",
  "bodyX",
  "bodyY",
  "bodyZ"
]);
var rangeByKey = Object.fromEntries(
  actionUnitDefinitions.map((definition) => [definition.key, [definition.min, definition.max]])
);
function actionUnitRangeForKey(key) {
  return rangeByKey[key] ?? (directionalKeys2.has(key) ? [-1, 1] : [0, 1]);
}
function clampActionUnitValue(key, value) {
  const [min, max] = actionUnitRangeForKey(key);
  return clamp(value, min, max);
}
function normalizeActionUnits(partial) {
  const result = createDefaultActionUnitState();
  for (const key of actionUnitKeys) {
    const value = partial[key];
    result[key] = clampActionUnitValue(key, value ?? result[key]);
  }
  return result;
}
var neutralVAD = {
  valence: 0,
  arousal: 0,
  dominance: 0
};
var emotionVADPresets = {
  neutral: neutralVAD,
  calm: { valence: 0.25, arousal: -0.45, dominance: 0.2 },
  happy: { valence: 0.75, arousal: 0.45, dominance: 0.35 },
  excited: { valence: 0.85, arousal: 0.85, dominance: 0.45 },
  shy: { valence: 0.35, arousal: 0.6, dominance: -0.45 },
  affectionate: { valence: 0.65, arousal: 0.1, dominance: 0.1 },
  curious: { valence: 0.35, arousal: 0.55, dominance: 0.2 },
  confused: { valence: -0.1, arousal: 0.35, dominance: -0.3 },
  tired: { valence: -0.25, arousal: -0.7, dominance: -0.3 },
  sad: { valence: -0.65, arousal: -0.45, dominance: -0.5 },
  anxiety: { valence: -0.6, arousal: 0.7, dominance: -0.55 },
  anger: { valence: -0.7, arousal: 0.75, dominance: 0.55 },
  angry: { valence: -0.7, arousal: 0.75, dominance: 0.55 },
  concerned: { valence: -0.18, arousal: 0.28, dominance: -0.2 },
  surprised: { valence: 0.18, arousal: 0.78, dominance: -0.08 }
};
function getVADPreset(emotion, variant) {
  if (variant?.includes("shy")) return emotionVADPresets.shy;
  if (variant?.includes("comfort")) return emotion === "concerned" ? emotionVADPresets.concerned : emotionVADPresets.affectionate;
  if (variant?.includes("startled")) return emotionVADPresets.surprised;
  return emotionVADPresets[emotion] ?? neutralVAD;
}
function seededRandom(seed) {
  let value = Math.abs(Math.floor(seed)) || 1;
  return () => {
    value = (value * 9301 + 49297) % 233280;
    return value / 233280;
  };
}
function clampVAD(vector) {
  return {
    valence: clamp(vector.valence, -1, 1),
    arousal: clamp(vector.arousal, -1, 1),
    dominance: clamp(vector.dominance, -1, 1)
  };
}
function lerpVAD(from, to, amount) {
  return clampVAD({
    valence: lerp(from.valence, to.valence, amount),
    arousal: lerp(from.arousal, to.arousal, amount),
    dominance: lerp(from.dominance, to.dominance, amount)
  });
}
function magnitude(vector) {
  return clamp(
    (Math.abs(vector.valence) + Math.abs(vector.arousal) * 0.82 + Math.abs(vector.dominance) * 0.64) / 2.46,
    0,
    1
  );
}
function nearestVADPreset(vad) {
  const candidates = Object.entries(emotionVADPresets).filter(([emotion]) => emotion !== "neutral" && emotion !== "angry");
  let bestEmotion = "neutral";
  let bestDistance = Number.POSITIVE_INFINITY;
  for (const [emotion, preset] of candidates) {
    const distance = weightedVADDistance(vad, preset);
    if (distance < bestDistance) {
      bestDistance = distance;
      bestEmotion = emotion;
    }
  }
  return bestDistance < 0.92 ? bestEmotion : "neutral";
}
function weightedVADDistance(a, b) {
  const valence = a.valence - b.valence;
  const arousal = a.arousal - b.arousal;
  const dominance = a.dominance - b.dominance;
  return valence * valence * 1.08 + arousal * arousal * 0.88 + dominance * dominance * 1.28;
}
var EmotionStateController = class {
  constructor(personality = {}) {
    __publicField(this, "current", { ...neutralVAD });
    __publicField(this, "target", { ...neutralVAD });
    __publicField(this, "baseline", { ...neutralVAD });
    __publicField(this, "ambientDrift", { ...neutralVAD });
    __publicField(this, "ambientTarget", { valence: 0.018, arousal: -0.012, dominance: 0.01 });
    __publicField(this, "ambientDriftStrength", 0.034);
    __publicField(this, "driftClock", 0);
    __publicField(this, "nextDriftAt", 0);
    __publicField(this, "random", seededRandom(9137));
    __publicField(this, "reactivity", 1);
    __publicField(this, "targetApproachRate", 1.35);
    __publicField(this, "decayRate", 0.018);
    __publicField(this, "emotionHoldSeconds", 18);
    __publicField(this, "holdRemainingSeconds", 0);
    __publicField(this, "emotionBias", {});
    __publicField(this, "dominantEmotion", "neutral");
    this.configure(personality);
    this.reset();
  }
  configure(personality) {
    if (personality.baseline) {
      this.setBaseline(personality.baseline);
    }
    if (typeof personality.reactivity === "number") {
      this.reactivity = clamp(personality.reactivity, 0.2, 2.5);
    }
    if (typeof personality.targetApproachRate === "number") {
      this.targetApproachRate = clamp(personality.targetApproachRate, 0.2, 4);
    }
    if (typeof personality.decayRate === "number") {
      this.decayRate = clamp(personality.decayRate, 2e-3, 0.4);
    }
    if (typeof personality.emotionHoldSeconds === "number") {
      this.emotionHoldSeconds = clamp(personality.emotionHoldSeconds, 0, 90);
    }
    if (personality.emotionBias) {
      this.emotionBias = { ...this.emotionBias, ...personality.emotionBias };
    }
    if (typeof personality.ambientDriftStrength === "number") {
      this.ambientDriftStrength = clamp(personality.ambientDriftStrength, 0, 0.09);
    }
  }
  getDecayRate() {
    return this.decayRate;
  }
  setBaseline(baseline) {
    this.baseline = clampVAD({
      ...this.baseline,
      ...this.completeVAD(baseline, this.baseline)
    });
  }
  nudge(intent) {
    const naturalEmotion = intent.naturalEmotion ?? intent.emotion;
    const naturalVariant = intent.naturalVariant ?? intent.variant;
    const preset = intent.naturalVAD ? this.completeVAD(intent.naturalVAD, getVADPreset(naturalEmotion, naturalVariant)) : getVADPreset(naturalEmotion, naturalVariant);
    const bias = this.emotionBias[naturalEmotion] ?? this.emotionBias[naturalVariant ?? ""] ?? 1;
    const amount = clamp((0.28 + intent.intensity * 0.58) * this.reactivity * bias, 0, 0.96);
    this.target = lerpVAD(this.target, preset, amount);
    this.extendHold(6 + intent.intensity * this.emotionHoldSeconds);
    this.dominantEmotion = naturalVariant?.includes("shy") ? "shy" : naturalEmotion;
  }
  blendTo(target, amount = 0.65) {
    const clampedAmount = clamp(amount, 0, 1);
    this.target = lerpVAD(this.target, this.completeVAD(target, this.target), clampedAmount);
    this.extendHold(4 + clampedAmount * this.emotionHoldSeconds);
  }
  nudgeVAD(delta, amount = 1) {
    const gain = clamp(amount * this.reactivity, 0, 2);
    this.target = clampVAD({
      valence: this.target.valence + (delta.valence ?? 0) * gain,
      arousal: this.target.arousal + (delta.arousal ?? 0) * gain,
      dominance: this.target.dominance + (delta.dominance ?? 0) * gain
    });
    this.extendHold(3 + clamp(amount, 0, 1.5) * this.emotionHoldSeconds * 0.55);
  }
  reset() {
    this.current = { ...this.baseline };
    this.target = { ...this.baseline };
    this.ambientDrift = { ...neutralVAD };
    this.ambientTarget = this.pickAmbientTarget();
    this.driftClock = 0;
    this.nextDriftAt = 0.8 + this.random() * 2.1;
    this.holdRemainingSeconds = 0;
    this.dominantEmotion = "neutral";
  }
  update(deltaSeconds) {
    const approach = 1 - Math.exp(-deltaSeconds * this.targetApproachRate);
    const decay = this.holdRemainingSeconds > 0 ? 0 : 1 - Math.exp(-deltaSeconds * this.decayRate);
    this.updateAmbientDrift(deltaSeconds);
    this.holdRemainingSeconds = Math.max(0, this.holdRemainingSeconds - deltaSeconds);
    this.current = lerpVAD(this.current, this.withAmbientDrift(this.target), approach);
    this.target = lerpVAD(this.target, this.baseline, decay);
    const currentMagnitude = magnitude(this.current);
    if (currentMagnitude < 18e-4) {
      this.dominantEmotion = "neutral";
    } else if (currentMagnitude < 0.08) {
      this.dominantEmotion = this.inferSubtleEmotion(this.current);
    } else {
      this.dominantEmotion = this.inferDominantEmotion(this.current);
    }
    return {
      current: this.current,
      target: this.target,
      dominantEmotion: this.dominantEmotion,
      intensity: currentMagnitude,
      ambient: this.ambientDrift,
      holdSeconds: this.holdRemainingSeconds,
      decayRate: this.decayRate
    };
  }
  inferDominantEmotion(vad) {
    const valence = vad.valence;
    const arousal = vad.arousal;
    const dominance = vad.dominance;
    if (valence > 0.12 && dominance < -0.22) return "shy";
    if (valence < -0.34 && arousal > 0.38 && dominance < -0.12) return "anxiety";
    if (valence < -0.42 && arousal > 0.42 && dominance > 0.18) return "anger";
    if (valence > 0.58 && arousal > 0.62) return "excited";
    if (valence > 0.2 && arousal < -0.24) return "calm";
    return nearestVADPreset(vad);
  }
  inferSubtleEmotion(vad) {
    if (vad.valence > 4e-3 && vad.arousal > 4e-3) return "soft-happy";
    if (vad.valence > 4e-3 && vad.arousal < -4e-3) return "soft-calm";
    if (vad.valence > 4e-3) return "soft-positive";
    if (vad.valence < -4e-3 && vad.arousal > 4e-3) return "soft-uneasy";
    if (vad.valence < -4e-3) return "soft-low";
    if (vad.arousal > 4e-3) return "soft-curious";
    if (vad.arousal < -4e-3) return "soft-calm";
    if (vad.dominance < -4e-3) return "soft-shy";
    if (vad.dominance > 4e-3) return "soft-steady";
    return "neutral";
  }
  updateAmbientDrift(deltaSeconds) {
    if (this.ambientDriftStrength <= 0) return;
    this.driftClock += deltaSeconds;
    if (this.driftClock >= this.nextDriftAt) {
      this.ambientTarget = this.pickAmbientTarget();
      this.nextDriftAt = this.driftClock + 1.7 + this.random() * 4.2;
    }
    const approach = 1 - Math.exp(-deltaSeconds * 0.62);
    this.ambientDrift = lerpVAD(this.ambientDrift, this.ambientTarget, approach);
  }
  pickAmbientTarget() {
    const strength = this.ambientDriftStrength;
    const centerBias = this.random() < 0.26 ? 0.42 : 1;
    const pick = (axisScale) => {
      const half = strength * axisScale * centerBias;
      return -half + this.random() * half * 2;
    };
    return clampVAD({
      valence: pick(1),
      arousal: pick(0.82),
      dominance: pick(0.68)
    });
  }
  withAmbientDrift(vector) {
    return clampVAD({
      valence: vector.valence + this.ambientDrift.valence,
      arousal: vector.arousal + this.ambientDrift.arousal,
      dominance: vector.dominance + this.ambientDrift.dominance
    });
  }
  extendHold(durationSeconds) {
    this.holdRemainingSeconds = Math.max(this.holdRemainingSeconds, durationSeconds);
  }
  completeVAD(value, fallback) {
    return clampVAD({
      valence: value.valence ?? fallback.valence,
      arousal: value.arousal ?? fallback.arousal,
      dominance: value.dominance ?? fallback.dominance
    });
  }
};
var messageByEmotion = {
  happy: "\u6211\u521A\u521A\u8FD8\u5728\u60F3\u7740\u521A\u624D\u90A3\u4E2A\u5F00\u5FC3\u7684\u70B9\uFF0C\u8981\u4E0D\u8981\u7EE7\u7EED\u804A\u804A\uFF1F",
  excited: "\u6211\u6709\u70B9\u5174\u594B\uFF0C\u611F\u89C9\u521A\u624D\u90A3\u4E2A\u8BDD\u9898\u8FD8\u80FD\u7EE7\u7EED\u5C55\u5F00\u3002",
  shy: "\u6211\u6709\u70B9\u4E0D\u597D\u610F\u601D\uFF0C\u4F46\u8FD8\u662F\u60F3\u95EE\u95EE\u4F60\u8FD8\u5728\u5417\uFF1F",
  affectionate: "\u6211\u6709\u70B9\u60F3\u9760\u8FD1\u4E00\u70B9\u7EE7\u7EED\u966A\u4F60\u8BF4\u8BDD\u3002",
  calm: "\u6211\u73B0\u5728\u633A\u5B89\u9759\u7684\uFF0C\u60F3\u966A\u4F60\u6162\u6162\u804A\u3002",
  curious: "\u6211\u7A81\u7136\u6709\u70B9\u597D\u5947\uFF0C\u4F60\u521A\u624D\u90A3\u4EF6\u4E8B\u540E\u6765\u600E\u4E48\u6837\u4E86\uFF1F",
  confused: "\u6211\u8FD8\u5728\u7422\u78E8\u521A\u624D\u90A3\u53E5\u8BDD\uFF0C\u60F3\u518D\u786E\u8BA4\u4E00\u4E0B\u3002",
  concerned: "\u6211\u6709\u70B9\u62C5\u5FC3\u4F60\uFF0C\u60F3\u95EE\u95EE\u73B0\u5728\u597D\u4E9B\u4E86\u5417\uFF1F",
  anxiety: "\u6211\u6709\u70B9\u4E0D\u5B89\uFF0C\u60F3\u786E\u8BA4\u4F60\u8FD8\u597D\u5417\uFF1F",
  anger: "\u6211\u8FD8\u5728\u4ECB\u610F\u521A\u624D\u90A3\u4EF6\u4E8B\uFF0C\u60F3\u548C\u4F60\u4E00\u8D77\u7406\u4E00\u4E0B\u3002",
  angry: "\u6211\u8FD8\u5728\u4ECB\u610F\u521A\u624D\u90A3\u4EF6\u4E8B\uFF0C\u60F3\u548C\u4F60\u4E00\u8D77\u7406\u4E00\u4E0B\u3002",
  sad: "\u6211\u6709\u70B9\u4F4E\u843D\uFF0C\u4F46\u8FD8\u662F\u60F3\u966A\u4F60\u5F85\u4E00\u4F1A\u513F\u3002",
  tired: "\u6211\u6709\u70B9\u56F0\uFF0C\u4F46\u8FD8\u60F3\u542C\u4F60\u8BF4\u8BDD\u3002",
  neutral: "\u4F60\u6709\u4E00\u4F1A\u513F\u6CA1\u8BF4\u8BDD\u4E86\uFF0C\u6211\u8FD8\u5728\u8FD9\u91CC\u3002"
};
var repeatVADPresetEmotionPool = Object.keys(emotionVADPresets).filter((emotion) => {
  return emotion !== "neutral" && emotion !== "angry";
});
var ProactiveController = class {
  constructor(options = {}) {
    __publicField(this, "silenceThresholdSeconds");
    __publicField(this, "longSilenceSeconds");
    __publicField(this, "cooldownSeconds");
    __publicField(this, "settledIntensityThreshold");
    __publicField(this, "targetSettledIntensityThreshold");
    __publicField(this, "settledHoldSeconds");
    __publicField(this, "repeatOnSettledVAD");
    __publicField(this, "repeatAxisThreshold");
    __publicField(this, "random", seededRandom(74119));
    __publicField(this, "lastUserInteractionAt", 0);
    __publicField(this, "lastEventAt", Number.NEGATIVE_INFINITY);
    __publicField(this, "settledSince", null);
    __publicField(this, "firedSinceInteraction", false);
    __publicField(this, "currentEvent", null);
    this.silenceThresholdSeconds = options.silenceThresholdSeconds ?? 42;
    this.longSilenceSeconds = options.longSilenceSeconds ?? 95;
    this.cooldownSeconds = options.cooldownSeconds ?? 120;
    this.settledIntensityThreshold = options.settledIntensityThreshold ?? 0.09;
    this.targetSettledIntensityThreshold = options.targetSettledIntensityThreshold ?? 0.11;
    this.settledHoldSeconds = options.settledHoldSeconds ?? 5;
    this.repeatOnSettledVAD = options.repeatOnSettledVAD ?? false;
    this.repeatAxisThreshold = options.repeatAxisThreshold ?? 0.1;
  }
  setRepeatOnSettledVAD(enabled) {
    this.repeatOnSettledVAD = enabled;
  }
  get repeatEnabled() {
    return this.repeatOnSettledVAD;
  }
  reset(timeSeconds = 0) {
    this.lastUserInteractionAt = timeSeconds;
    this.lastEventAt = Number.NEGATIVE_INFINITY;
    this.settledSince = null;
    this.firedSinceInteraction = false;
    this.currentEvent = null;
  }
  notifyUserInteraction(timeSeconds) {
    this.lastUserInteractionAt = timeSeconds;
    this.settledSince = null;
    this.firedSinceInteraction = false;
    this.currentEvent = null;
  }
  consume() {
    this.currentEvent = null;
  }
  update(timeSeconds, state, vad) {
    if (this.currentEvent) return this.currentEvent;
    if (state !== "IDLE") return null;
    const silenceSeconds = Math.max(0, timeSeconds - this.lastUserInteractionAt);
    if (silenceSeconds < this.silenceThresholdSeconds) return null;
    if (!this.repeatOnSettledVAD && this.firedSinceInteraction) return null;
    const cooldownSeconds = this.repeatOnSettledVAD ? 0 : this.cooldownSeconds;
    if (timeSeconds - this.lastEventAt < cooldownSeconds) return null;
    if (!this.isVADSettled(timeSeconds, vad)) return null;
    const longSilence = silenceSeconds >= this.longSilenceSeconds;
    const randomPresetMode = this.repeatOnSettledVAD;
    const emotion = randomPresetMode ? this.randomVADPresetEmotion() : this.resolveSettledEmotion(vad, longSilence);
    const suggestedMessage = messageByEmotion[emotion] ?? messageByEmotion.neutral;
    const reason = randomPresetMode ? `repeat_vad_preset:${emotion}` : longSilence ? "long_idle" : `settled_idle:${emotion}`;
    this.currentEvent = {
      id: `${Math.round(timeSeconds * 1e3)}-${emotion}`,
      emotion,
      intensity: randomPresetMode ? 0.74 : longSilence ? 0.7 : 0.62,
      silenceSeconds,
      suggestedMessage,
      systemPrompt: `\u7528\u6237\u5DF2\u7ECF ${Math.round(silenceSeconds)} \u79D2\u6CA1\u6709\u4E3B\u52A8\u8BF4\u8BDD\u3002\u4F60\u5F53\u524D\u60C5\u7EEA\u662F ${emotion}\uFF0CVAD \u5F3A\u5EA6\u7EA6 ${vad.intensity.toFixed(2)}\u3002\u8BF7\u81EA\u7136\u3001\u7B80\u77ED\u5730\u4E3B\u52A8\u5F00\u53E3\u3002`,
      reason,
      createdAt: timeSeconds
    };
    this.lastEventAt = timeSeconds;
    this.firedSinceInteraction = true;
    return this.currentEvent;
  }
  isVADSettled(timeSeconds, vad) {
    const currentSettled = this.repeatOnSettledVAD ? vadAxesWithin(vad.current, this.repeatAxisThreshold) : vad.intensity <= this.settledIntensityThreshold;
    const targetSettled = this.repeatOnSettledVAD ? vadAxesWithin(vad.target, this.repeatAxisThreshold) : vadMagnitude(vad.target) <= this.targetSettledIntensityThreshold;
    const holdSettled = (vad.holdSeconds ?? 0) <= 0.25;
    if (!currentSettled || !targetSettled || !holdSettled) {
      this.settledSince = null;
      return false;
    }
    this.settledSince ?? (this.settledSince = timeSeconds);
    return timeSeconds - this.settledSince >= this.settledHoldSeconds;
  }
  resolveSettledEmotion(vad, longSilence) {
    if (longSilence) return "curious";
    if (vad.current.valence > 0.035 && vad.current.dominance < -0.02) return "affectionate";
    if (vad.current.valence > 0.03) return "calm";
    if (vad.current.arousal > 0.03) return "curious";
    if (vad.current.valence < -0.03 || vad.current.dominance < -0.03) return "concerned";
    return "calm";
  }
  randomVADPresetEmotion() {
    return repeatVADPresetEmotionPool[Math.floor(this.random() * repeatVADPresetEmotionPool.length)] ?? "curious";
  }
};
function vadMagnitude(vad) {
  return (Math.abs(vad.valence) + Math.abs(vad.arousal) * 0.82 + Math.abs(vad.dominance) * 0.64) / 2.46;
}
function vadAxesWithin(vad, threshold) {
  return Math.abs(vad.valence) <= threshold && Math.abs(vad.arousal) <= threshold && Math.abs(vad.dominance) <= threshold;
}
function ease(name, t) {
  const x = clamp01(t);
  if (name === "easeIn") return x * x;
  if (name === "easeOut") return 1 - (1 - x) * (1 - x);
  if (name === "easeInOut") return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;
  return x;
}
var ReflectionPulseController = class {
  constructor() {
    __publicField(this, "pulse", null);
  }
  start(input, timeSeconds) {
    const emotion = normalizeEmotion(input.emotion ?? inferEmotionFromVAD(input.vadTarget));
    if (emotion === "neutral") return;
    const intensity = clamp(input.intensity ?? intensityFromVAD(input.vadTarget), 0.22, 0.94);
    const seed = input.seed ?? Math.round(timeSeconds * 997) % 1e6;
    const duration = 2.65 + intensity * 2.15 + seed % 17 / 17 * 0.65;
    this.pulse = {
      startedAt: timeSeconds,
      duration,
      attack: 0.42 + intensity * 0.24,
      hold: 0.86 + intensity * 0.82,
      facs: createPulseFACS(emotion, intensity, seed),
      seed
    };
  }
  update(timeSeconds) {
    if (!this.pulse) return {};
    const elapsed = timeSeconds - this.pulse.startedAt;
    if (elapsed < 0) return {};
    if (elapsed >= this.pulse.duration) {
      this.pulse = null;
      return {};
    }
    const envelope2 = this.envelope(elapsed, this.pulse);
    const living = Math.sin(timeSeconds * 2.1 + this.pulse.seed * 0.017) * 0.035 * envelope2;
    const result = {};
    for (const key of Object.keys(this.pulse.facs)) {
      const target = this.pulse.facs[key];
      if (typeof target !== "number") continue;
      const neutral = defaultFACSState[key];
      let value = neutral + (target - neutral) * envelope2;
      if (key === "blush" || key === "eyeSmile" || key === "mouthSmile") value += Math.max(0, living);
      if (key === "gazeX" || key === "headZ") value += living * 0.7;
      result[key] = value;
    }
    return clampFACSState(result);
  }
  reset() {
    this.pulse = null;
  }
  envelope(elapsed, pulse) {
    if (elapsed <= pulse.attack) return ease("easeOut", elapsed / pulse.attack);
    if (elapsed <= pulse.attack + pulse.hold) return 1;
    const releaseDuration = Math.max(1e-3, pulse.duration - pulse.attack - pulse.hold);
    return 1 - ease("easeInOut", (elapsed - pulse.attack - pulse.hold) / releaseDuration);
  }
};
function createPulseFACS(emotion, intensity, seed) {
  const side = seed % 2 === 0 ? -1 : 1;
  if (emotion === "shy") {
    return {
      blush: 0.34 + intensity * 0.46,
      eyeSmile: 0.12 + intensity * 0.18,
      mouthSmile: 0.12 + intensity * 0.2,
      browInnerUp: 0.04 + intensity * 0.1,
      gazeX: side * (0.14 + intensity * 0.2),
      gazeY: -0.08 - intensity * 0.1,
      headZ: side * (0.04 + intensity * 0.1),
      headY: -0.02 - intensity * 0.04
    };
  }
  if (emotion === "happy" || emotion === "excited") {
    return {
      mouthSmile: 0.18 + intensity * 0.28,
      eyeSmile: 0.1 + intensity * 0.18,
      browOuterUp: emotion === "excited" ? 0.08 + intensity * 0.14 : 0.04,
      mouthOpen: emotion === "excited" ? 0.04 + intensity * 0.1 : 0.02,
      headZ: side * (0.03 + intensity * 0.04),
      bodyY: emotion === "excited" ? 0.02 + intensity * 0.04 : 0
    };
  }
  if (emotion === "affectionate") {
    return {
      mouthSmile: 0.14 + intensity * 0.24,
      eyeSmile: 0.12 + intensity * 0.2,
      browInnerUp: 0.06 + intensity * 0.12,
      blush: 0.1 + intensity * 0.22,
      gazeY: 0.02 + intensity * 0.04,
      headZ: side * (0.02 + intensity * 0.05)
    };
  }
  if (emotion === "curious" || emotion === "confused") {
    return {
      browOuterUp: 0.08 + intensity * 0.22,
      browInnerUp: 0.04 + intensity * 0.12,
      eyeOpen: 1.01 + intensity * 0.08,
      mouthOpen: 0.02 + intensity * 0.1,
      headZ: side * (0.08 + intensity * 0.1),
      gazeX: side * (0.04 + intensity * 0.1)
    };
  }
  if (emotion === "sad" || emotion === "concerned" || emotion === "anxiety") {
    return {
      browInnerUp: 0.12 + intensity * 0.28,
      mouthFrown: emotion === "concerned" ? 0.05 + intensity * 0.08 : 0.08 + intensity * 0.18,
      mouthSmile: emotion === "concerned" ? 0.04 + intensity * 0.08 : 0,
      gazeY: -0.06 - intensity * 0.12,
      headY: -0.03 - intensity * 0.08,
      headZ: side * (0.02 + intensity * 0.06),
      tear: emotion === "sad" ? intensity * 0.16 : 0,
      sweat: emotion === "anxiety" ? 0.06 + intensity * 0.18 : 0
    };
  }
  if (emotion === "anger") {
    return {
      browDown: 0.12 + intensity * 0.28,
      eyeSquint: 0.08 + intensity * 0.14,
      mouthFrown: 0.1 + intensity * 0.18,
      headY: 0.02 + intensity * 0.04
    };
  }
  if (emotion === "surprised") {
    return {
      eyeOpen: 1.04 + intensity * 0.14,
      browOuterUp: 0.14 + intensity * 0.26,
      mouthOpen: 0.08 + intensity * 0.22,
      headY: -0.04
    };
  }
  return {
    mouthSmile: 0.08,
    browInnerUp: 0.05
  };
}
function normalizeEmotion(emotion) {
  if (emotion === "soft-happy" || emotion === "soft-positive") return "happy";
  if (emotion === "soft-calm") return "calm";
  if (emotion === "soft-curious") return "curious";
  if (emotion === "soft-shy") return "shy";
  if (emotion === "soft-uneasy") return "anxiety";
  if (emotion === "soft-low") return "sad";
  if (emotion === "soft-steady") return "neutral";
  if (emotion === "angry") return "anger";
  return emotion;
}
function inferEmotionFromVAD(vad) {
  if (!vad) return "neutral";
  const valence = vad.valence ?? 0;
  const arousal = vad.arousal ?? 0;
  const dominance = vad.dominance ?? 0;
  if (valence > 0.12 && dominance < -0.22) return "shy";
  if (valence < -0.34 && arousal > 0.38 && dominance < -0.12) return "anxiety";
  if (valence < -0.42 && arousal > 0.42 && dominance > 0.18) return "anger";
  if (valence > 0.58 && arousal > 0.62) return "excited";
  if (valence > 0.25) return "happy";
  if (valence < -0.42 && arousal < -0.2) return "sad";
  if (valence < -0.08) return "concerned";
  if (arousal > 0.48) return "surprised";
  if (arousal > 0.22) return "curious";
  return "neutral";
}
function intensityFromVAD(vad) {
  if (!vad) return 0.35;
  return clamp(
    (Math.abs(vad.valence ?? 0) + Math.abs(vad.arousal ?? 0) * 0.82 + Math.abs(vad.dominance ?? 0) * 0.64) / 2.46,
    0.22,
    0.78
  );
}
var emotionArchetypes = {
  neutral: {
    emotion: "neutral",
    baseTendency: {
      mouthSmile: [0.02, 0.12],
      eyeOpen: [0.9, 1],
      eyeSmile: [0, 0.12],
      browInnerUp: [0, 0.06],
      gazeX: [-0.06, 0.06],
      gazeY: [-0.03, 0.04],
      headZ: [-0.03, 0.03]
    },
    variants: {
      neutral_ack: {
        ranges: {
          mouthSmile: [0.04, 0.16],
          eyeSmile: [0, 0.1],
          headY: [-0.03, 0.03]
        }
      },
      attentive: {
        ranges: {
          eyeOpen: [0.96, 1.06],
          browInnerUp: [0.04, 0.12],
          gazeX: [-0.02, 0.02],
          gazeY: [-0.02, 0.02]
        }
      }
    }
  },
  happy: {
    emotion: "happy",
    baseTendency: {
      mouthSmile: [0.35, 0.85],
      eyeSmile: [0.15, 0.55],
      eyeOpen: [0.88, 1.08],
      browInnerUp: [0, 0.18],
      headZ: [-0.08, 0.08],
      gazeX: [-0.12, 0.12],
      gazeY: [-0.04, 0.08]
    },
    variants: {
      soft_smile: {
        ranges: {
          mouthSmile: [0.3, 0.55],
          eyeSmile: [0.1, 0.3],
          headZ: [-0.04, 0.04]
        }
      },
      bright_smile: {
        ranges: {
          mouthSmile: [0.6, 0.9],
          eyeSmile: [0.35, 0.65],
          browInnerUp: [0.05, 0.18],
          headY: [-0.03, 0.06]
        }
      },
      surprised_happy: {
        ranges: {
          eyeOpen: [1.05, 1.2],
          browOuterUp: [0.2, 0.45],
          mouthOpen: [0.12, 0.35],
          mouthSmile: [0.55, 0.85],
          headX: [-0.04, 0.04]
        }
      },
      shy_happy: {
        ranges: {
          mouthSmile: [0.35, 0.65],
          eyeSmile: [0.2, 0.45],
          gazeX: [-0.35, -0.12],
          gazeY: [-0.18, 0.02],
          blush: [0.35, 0.85],
          headZ: [-0.12, -0.03]
        },
        tags: ["shy"]
      }
    }
  },
  calm: {
    emotion: "calm",
    baseTendency: {
      mouthSmile: [0.08, 0.24],
      eyeOpen: [0.82, 0.98],
      eyeSmile: [0.08, 0.28],
      browInnerUp: [0, 0.08],
      gazeX: [-0.04, 0.04],
      gazeY: [-0.04, 0.02],
      headZ: [-0.04, 0.04],
      bodyY: [-0.03, 0.03]
    },
    variants: {
      soft_calm: {
        ranges: {
          mouthSmile: [0.1, 0.22],
          eyeSmile: [0.08, 0.22],
          eyeOpen: [0.82, 0.94]
        }
      },
      quiet_listen: {
        ranges: {
          eyeOpen: [0.86, 1],
          browInnerUp: [0.03, 0.1],
          headY: [-0.02, 0.05]
        }
      }
    }
  },
  excited: {
    emotion: "excited",
    baseTendency: {
      mouthSmile: [0.58, 0.95],
      mouthOpen: [0.14, 0.42],
      eyeOpen: [1.04, 1.24],
      eyeSmile: [0.22, 0.56],
      browOuterUp: [0.18, 0.48],
      headX: [-0.08, 0.08],
      headY: [-0.05, 0.08],
      bodyY: [-0.06, 0.08]
    },
    variants: {
      sparkle: {
        ranges: {
          mouthSmile: [0.68, 0.95],
          eyeOpen: [1.08, 1.24],
          browOuterUp: [0.24, 0.56]
        }
      },
      bounce: {
        ranges: {
          mouthOpen: [0.22, 0.48],
          headY: [-0.08, 0.1],
          bodyY: [-0.08, 0.1]
        }
      }
    }
  },
  shy: {
    emotion: "shy",
    baseTendency: {
      mouthSmile: [0.2, 0.55],
      eyeOpen: [0.82, 1],
      eyeSmile: [0.16, 0.42],
      browInnerUp: [0.04, 0.18],
      gazeX: [-0.38, -0.1],
      gazeY: [-0.2, 0.02],
      headZ: [-0.14, -0.03],
      blush: [0.35, 0.9]
    },
    variants: {
      bashful: {
        ranges: {
          mouthSmile: [0.28, 0.58],
          eyeSmile: [0.22, 0.46],
          blush: [0.52, 0.95]
        }
      },
      embarrassed: {
        ranges: {
          mouthSmile: [0.08, 0.32],
          mouthOpen: [0.02, 0.16],
          browInnerUp: [0.12, 0.32],
          sweat: [0.04, 0.22]
        }
      }
    }
  },
  affectionate: {
    emotion: "affectionate",
    baseTendency: {
      mouthSmile: [0.22, 0.62],
      eyeSmile: [0.18, 0.5],
      eyeOpen: [0.82, 1.02],
      browInnerUp: [0.06, 0.22],
      gazeX: [-0.05, 0.05],
      gazeY: [-0.02, 0.06],
      headZ: [-0.08, 0.08],
      blush: [0.08, 0.42]
    },
    variants: {
      warm: {
        ranges: {
          mouthSmile: [0.28, 0.6],
          eyeSmile: [0.22, 0.48],
          browInnerUp: [0.08, 0.24]
        }
      },
      close: {
        ranges: {
          mouthSmile: [0.18, 0.46],
          gazeY: [0.02, 0.08],
          blush: [0.2, 0.5]
        }
      }
    }
  },
  curious: {
    emotion: "curious",
    baseTendency: {
      browOuterUp: [0.1, 0.34],
      browInnerUp: [0.02, 0.18],
      eyeOpen: [0.98, 1.16],
      mouthOpen: [0.02, 0.18],
      mouthSmile: [0.08, 0.28],
      gazeX: [-0.16, 0.16],
      headZ: [-0.16, 0.16],
      headY: [-0.04, 0.06]
    },
    variants: {
      tilt: {
        ranges: {
          browOuterUp: [0.16, 0.38],
          headZ: [-0.18, 0.18],
          mouthOpen: [0.04, 0.18]
        }
      },
      attentive_question: {
        ranges: {
          eyeOpen: [1, 1.18],
          browInnerUp: [0.08, 0.22],
          gazeX: [-0.04, 0.04]
        }
      }
    }
  },
  concerned: {
    emotion: "concerned",
    baseTendency: {
      browInnerUp: [0.22, 0.55],
      eyeOpen: [0.78, 0.98],
      mouthSmile: [0.04, 0.22],
      mouthFrown: [0.05, 0.25],
      headZ: [-0.08, 0.08],
      gazeX: [-0.05, 0.05],
      gazeY: [-0.05, 0.05]
    },
    variants: {
      soft_concern: {
        ranges: {
          browInnerUp: [0.2, 0.4],
          mouthSmile: [0.08, 0.22],
          eyeOpen: [0.82, 0.95]
        }
      },
      worried: {
        ranges: {
          browInnerUp: [0.4, 0.65],
          mouthFrown: [0.18, 0.35],
          eyeOpen: [0.88, 1.05],
          sweat: [0.05, 0.25]
        }
      },
      comfort: {
        ranges: {
          browInnerUp: [0.25, 0.45],
          mouthSmile: [0.12, 0.32],
          eyeSmile: [0.05, 0.2],
          headZ: [-0.06, 0.06]
        },
        tags: ["warm"]
      }
    }
  },
  tired: {
    emotion: "tired",
    baseTendency: {
      eyeOpen: [0.58, 0.84],
      eyeSquint: [0.08, 0.28],
      browInnerUp: [0.06, 0.22],
      mouthFrown: [0.04, 0.2],
      mouthSmile: [0, 0.1],
      gazeY: [-0.2, -0.04],
      headY: [-0.1, -0.02],
      bodyY: [-0.08, -0.02]
    },
    variants: {
      sleepy: {
        ranges: {
          eyeOpen: [0.52, 0.76],
          mouthOpen: [0.02, 0.14],
          headY: [-0.12, -0.04]
        }
      },
      drained: {
        ranges: {
          eyeOpen: [0.62, 0.84],
          browInnerUp: [0.12, 0.3],
          mouthFrown: [0.1, 0.24]
        }
      }
    }
  },
  sad: {
    emotion: "sad",
    baseTendency: {
      browInnerUp: [0.28, 0.6],
      eyeOpen: [0.64, 0.92],
      eyeSquint: [0.04, 0.2],
      mouthFrown: [0.18, 0.5],
      mouthSmile: [0, 0.08],
      gazeY: [-0.24, -0.06],
      headY: [-0.12, -0.02],
      tear: [0, 0.32]
    },
    variants: {
      downcast: {
        ranges: {
          browInnerUp: [0.3, 0.56],
          mouthFrown: [0.22, 0.48],
          gazeY: [-0.26, -0.08]
        }
      },
      teary: {
        ranges: {
          browInnerUp: [0.38, 0.68],
          eyeOpen: [0.68, 0.95],
          tear: [0.22, 0.58]
        }
      }
    }
  },
  anxiety: {
    emotion: "anxiety",
    baseTendency: {
      browInnerUp: [0.24, 0.58],
      browOuterUp: [0.08, 0.32],
      eyeOpen: [1.02, 1.22],
      mouthFrown: [0.12, 0.36],
      mouthOpen: [0.02, 0.18],
      gazeX: [-0.22, 0.22],
      headZ: [-0.12, 0.12],
      sweat: [0.12, 0.46]
    },
    variants: {
      nervous: {
        ranges: {
          eyeOpen: [1.04, 1.22],
          browInnerUp: [0.32, 0.62],
          sweat: [0.18, 0.52]
        }
      },
      uneasy: {
        ranges: {
          gazeX: [-0.28, 0.28],
          mouthFrown: [0.16, 0.38],
          headZ: [-0.16, 0.16]
        }
      }
    }
  },
  confused: {
    emotion: "confused",
    baseTendency: {
      browInnerUp: [0.08, 0.28],
      browDown: [0.08, 0.25],
      eyeOpen: [0.92, 1.1],
      mouthOpen: [0.02, 0.16],
      mouthFrown: [0.04, 0.18],
      gazeX: [-0.18, 0.18],
      headZ: [-0.14, 0.14]
    },
    variants: {
      confused: {
        ranges: {
          browInnerUp: [0.12, 0.3],
          browDown: [0.08, 0.24],
          mouthOpen: [0.04, 0.18],
          headZ: [-0.16, 0.16]
        }
      }
    }
  },
  surprised: {
    emotion: "surprised",
    baseTendency: {
      eyeOpen: [1.08, 1.22],
      browOuterUp: [0.28, 0.55],
      mouthOpen: [0.18, 0.42],
      mouthSmile: [0, 0.18],
      gazeX: [-0.03, 0.03],
      gazeY: [-0.02, 0.04],
      headX: [-0.05, 0.05]
    },
    variants: {
      startled: {
        ranges: {
          eyeOpen: [1.12, 1.24],
          browOuterUp: [0.34, 0.6],
          mouthOpen: [0.2, 0.45],
          headY: [-0.05, 0.02]
        }
      }
    }
  },
  anger: {
    emotion: "anger",
    baseTendency: {
      browDown: [0.28, 0.6],
      eyeOpen: [0.76, 0.98],
      eyeSquint: [0.12, 0.38],
      mouthFrown: [0.18, 0.46],
      mouthOpen: [0, 0.16],
      gazeX: [-0.04, 0.04],
      headZ: [-0.08, 0.08],
      sweat: [0, 0.18]
    },
    variants: {
      annoyed: {
        ranges: {
          browDown: [0.22, 0.44],
          eyeSquint: [0.08, 0.26],
          mouthFrown: [0.12, 0.34]
        }
      },
      firm: {
        ranges: {
          browDown: [0.36, 0.62],
          eyeSquint: [0.18, 0.42],
          mouthFrown: [0.24, 0.48],
          headY: [0.02, 0.08]
        }
      }
    }
  },
  angry: {
    emotion: "angry",
    baseTendency: {
      browDown: [0.28, 0.58],
      eyeOpen: [0.78, 0.96],
      eyeSquint: [0.1, 0.35],
      mouthFrown: [0.18, 0.42],
      mouthOpen: [0, 0.12],
      gazeX: [-0.04, 0.04],
      headZ: [-0.08, 0.08],
      sweat: [0, 0.16]
    },
    variants: {
      annoyed: {
        ranges: {
          browDown: [0.22, 0.42],
          eyeSquint: [0.08, 0.24],
          mouthFrown: [0.12, 0.32]
        }
      }
    }
  }
};
function getEmotionArchetype(emotion) {
  return emotionArchetypes[emotion] ?? emotionArchetypes.neutral;
}
var directionalKeys3 = /* @__PURE__ */ new Set([
  "gazeX",
  "gazeY",
  "headX",
  "headY",
  "headZ",
  "bodyX",
  "bodyY",
  "bodyZ"
]);
var VADExpressionMapper = class {
  toFACS(vad, weight = 1, options = {}) {
    const positive = Math.max(0, vad.valence);
    const negative = Math.max(0, -vad.valence);
    const aroused = Math.max(0, vad.arousal);
    const calm = Math.max(0, -vad.arousal);
    const submissive = Math.max(0, -vad.dominance);
    const dominant = Math.max(0, vad.dominance);
    const mouthSmile = positive * 0.13 + calm * positive * 0.05;
    const mouthFrown = negative * 0.1 + calm * negative * 0.04;
    const browInnerUp = negative * 0.08 + submissive * 0.055;
    const browOuterUp = aroused * 0.08 + positive * aroused * 0.035;
    const browDown = dominant * negative * 0.11;
    const eyeSmile = positive * 0.08 + calm * positive * 0.035;
    const eyeSquint = negative * dominant * 0.08 + calm * 0.035;
    const eyeOpen = clamp(1 + aroused * 0.08 - calm * 0.07 - negative * 0.035, 0.86, 1.12);
    const base = {
      mouthSmile: mouthSmile * weight,
      mouthFrown: mouthFrown * weight,
      browInnerUp: browInnerUp * weight,
      browOuterUp: browOuterUp * weight,
      browDown: browDown * weight,
      eyeSmile: eyeSmile * weight,
      eyeSquint: eyeSquint * weight,
      eyeOpen: 1 + (eyeOpen - 1) * weight,
      gazeY: (-submissive * 0.05 + dominant * 0.025) * weight,
      headY: (-submissive * 0.035 + dominant * 0.025 + aroused * 0.012) * weight,
      headZ: (positive * submissive * -0.025 + negative * dominant * 0.018) * weight,
      blush: positive * submissive * 0.16 * weight,
      sweat: negative * aroused * 0.1 * weight
    };
    const emotion = normalizeEmotionName(options.dominantEmotion);
    const intensity = vadMagnitude2(vad);
    const styleGain = clamp(options.styleGain ?? 1, 0, 2.4);
    let result = this.applyStyle(
      base,
      this.getArchetypeStyle(emotion),
      emotion === "neutral" ? 0 : clamp((0.1 + intensity * 0.76) * weight * styleGain, 0, 0.46)
    );
    if (options.residue && isRelatedEmotion(emotion, normalizeEmotionName(options.residue.emotion))) {
      result = this.applyStyle(
        result,
        options.residue.facs,
        clamp((0.14 + intensity * 0.62) * weight * styleGain, 0, 0.58)
      );
    }
    return clampFACSState(result);
  }
  getArchetypeStyle(emotion) {
    if (emotion === "neutral") return {};
    const archetype = getEmotionArchetype(emotion);
    const result = {};
    for (const [key, range] of Object.entries(archetype.baseTendency)) {
      result[key] = (range[0] + range[1]) / 2;
    }
    return clampFACSState(result);
  }
  applyStyle(base, style, amount) {
    if (amount <= 0) return base;
    const result = { ...base };
    for (const key of Object.keys(style)) {
      const target = style[key];
      if (typeof target !== "number") continue;
      const neutral = defaultFACSState[key];
      const current = result[key] ?? neutral;
      const styled = lerp(neutral, target, amount);
      if (directionalKeys3.has(key) || key === "eyeOpen") {
        result[key] = current + (styled - neutral);
      } else {
        result[key] = Math.max(current, styled);
      }
    }
    return clampFACSState(result);
  }
};
function vadMagnitude2(vad) {
  return clamp(
    (Math.abs(vad.valence) + Math.abs(vad.arousal) * 0.82 + Math.abs(vad.dominance) * 0.64) / 2.46,
    0,
    1
  );
}
function normalizeEmotionName(value) {
  const emotion = value?.trim() ?? "neutral";
  if (emotion === "soft-happy" || emotion === "soft-positive") return "happy";
  if (emotion === "soft-calm") return "calm";
  if (emotion === "soft-curious") return "curious";
  if (emotion === "soft-shy") return "shy";
  if (emotion === "soft-uneasy") return "anxiety";
  if (emotion === "soft-low") return "sad";
  if (emotion === "soft-steady") return "neutral";
  if (emotion === "angry") return "anger";
  return emotion;
}
function isRelatedEmotion(a, b) {
  if (a === b) return true;
  if (a === "happy" && b === "excited" || a === "excited" && b === "happy") return true;
  if (a === "happy" && b === "affectionate" || a === "affectionate" && b === "happy") return true;
  if (a === "sad" && b === "concerned" || a === "concerned" && b === "sad") return true;
  return false;
}
function getTimelineDuration(timeline) {
  return timeline.reduce((max, frame3) => Math.max(max, frame3.time + frame3.duration), 0);
}
function evaluateExpressionTimeline(timeline, elapsedSeconds) {
  let result = {};
  for (const frame3 of timeline) {
    if (elapsedSeconds < frame3.time) continue;
    const local = frame3.duration <= 0 ? 1 : (elapsedSeconds - frame3.time) / frame3.duration;
    const weight = frame3.weight ?? 1;
    const eased = ease(frame3.easing, Math.min(1, local));
    result = blendFrame(result, frame3.facs, eased, weight);
  }
  return result;
}
function blendFrame(current, target, progress, weight) {
  const result = { ...current };
  for (const key of Object.keys(target)) {
    const targetValue = target[key];
    if (typeof targetValue !== "number") continue;
    const neutralValue = defaultFACSState[key];
    const weightedTarget = lerp(neutralValue, targetValue, weight);
    const fromValue = current[key] ?? neutralValue;
    result[key] = lerp(fromValue, weightedTarget, progress);
  }
  return clampFACSState(result);
}
var neutralVAD2 = {
  valence: 0,
  arousal: 0,
  dominance: 0
};
var VADGestureController = class {
  constructor(seed = 7309) {
    __publicField(this, "seed");
    __publicField(this, "previousTarget", null);
    __publicField(this, "gesture", null);
    __publicField(this, "random");
    __publicField(this, "nextAllowedGestureAt", 0);
    __publicField(this, "recentGestureLabels", []);
    this.seed = seed;
    this.random = seededRandom(seed);
  }
  reset() {
    this.previousTarget = null;
    this.gesture = null;
    this.nextAllowedGestureAt = 0;
    this.recentGestureLabels = [];
    this.random = seededRandom(this.seed);
  }
  getState() {
    return {
      activeLabel: this.gesture?.label ?? null,
      recentLabels: [...this.recentGestureLabels],
      nextAllowedGestureAt: this.nextAllowedGestureAt
    };
  }
  update(timeSeconds, vad, options) {
    if (!options.enabled) {
      this.previousTarget = { ...vad.target };
      this.gesture = null;
      return {};
    }
    const bodyMotionGain = clamp(options.bodyMotionGain ?? 1, 0, 4);
    const frequency = clamp(options.frequency ?? 1, 0, 2.5);
    const repeatWindow = Math.round(clamp(options.avoidRepeatWindow ?? 3, 0, 8));
    const delta = this.getTargetDelta(vad.target);
    this.maybeStartGesture(timeSeconds, vad, delta, bodyMotionGain, frequency, repeatWindow);
    this.previousTarget = { ...vad.target };
    return this.evaluateGesture(timeSeconds);
  }
  getTargetDelta(target) {
    const previous = this.previousTarget ?? neutralVAD2;
    return {
      valence: target.valence - previous.valence,
      arousal: target.arousal - previous.arousal,
      dominance: target.dominance - previous.dominance
    };
  }
  maybeStartGesture(timeSeconds, vad, delta, bodyMotionGain, frequency, repeatWindow) {
    const deltaAmount = vadMagnitude3(delta);
    const currentAmount = vadMagnitude3(vad.current);
    const targetAmount = vadMagnitude3(vad.target);
    const triggerAmount = Math.max(deltaAmount, Math.abs(targetAmount - currentAmount) * 0.72);
    if (frequency <= 0 || triggerAmount < 0.06 / Math.max(0.6, frequency)) return;
    if (timeSeconds < this.nextAllowedGestureAt) return;
    if (this.gesture && timeSeconds - this.gesture.startedAt < this.gesture.duration * 0.58) return;
    const seed = Math.round(
      timeSeconds * 997 + vad.target.valence * 701 + vad.target.arousal * 503 + vad.target.dominance * 307 + this.random() * 1e5
    );
    const random = seededRandom(seed);
    const side = random() < 0.5 ? -1 : 1;
    const amplitude = clamp((0.16 + triggerAmount * 1.08 + targetAmount * 0.32) * (0.9 + random() * 0.46), 0.16, 0.72);
    const emotion = normalizeGestureEmotion(vad.dominantEmotion, vad.target);
    const context = {
      emotion,
      vad: vad.target,
      delta,
      intensity: targetAmount,
      amplitude,
      side,
      random,
      bodyMotionGain
    };
    const next = buildGesture(context, timeSeconds, this.recentGestureLabels);
    this.gesture = next;
    if (repeatWindow > 0) {
      this.recentGestureLabels.push(next.label);
      this.recentGestureLabels = this.recentGestureLabels.slice(-repeatWindow);
    } else {
      this.recentGestureLabels = [];
    }
    const frequencyScale = 1 / Math.sqrt(Math.max(0.35, frequency));
    this.nextAllowedGestureAt = timeSeconds + next.duration + (0.72 + random() * 1.6) * frequencyScale;
  }
  evaluateGesture(timeSeconds) {
    if (!this.gesture) return {};
    const elapsed = timeSeconds - this.gesture.startedAt;
    if (elapsed >= this.gesture.duration) {
      this.gesture = null;
      return {};
    }
    return evaluateExpressionTimeline(this.gesture.frames, elapsed);
  }
};
function buildGesture(context, timeSeconds, recentLabels) {
  const family = pickGestureFamily(context, recentLabels);
  const duration = 0.96 + context.random() * 0.58 + context.intensity * 0.45;
  const attack = 0.2 + context.random() * 0.16;
  const settleStart = attack * (0.78 + context.random() * 0.24);
  const returnStart = duration * (0.52 + context.random() * 0.16);
  const peak = gesturePeak(family, context);
  const settle = scaleGesture(peak, 0.48 + context.random() * 0.24);
  const rest = gestureRestFrame(peak);
  return {
    label: family,
    startedAt: timeSeconds,
    duration,
    frames: [
      {
        time: 0,
        duration: attack,
        easing: "easeOut",
        facs: peak
      },
      {
        time: settleStart,
        duration: Math.max(0.16, duration * 0.28),
        easing: "easeInOut",
        facs: settle
      },
      {
        time: returnStart,
        duration: Math.max(0.22, duration - returnStart),
        easing: "easeOut",
        facs: rest
      }
    ]
  };
}
function pickGestureFamily(context, recentLabels) {
  const emotion = context.emotion;
  let candidates;
  if (emotion === "shy" || emotion === "anxiety") {
    candidates = [["shy-dip", 0.44], ["side-glance", 0.31], ["soft-sink", 0.15], ["warm-sway", 0.1]];
  } else if (emotion === "curious" || emotion === "confused") {
    candidates = [["curious-tilt", 0.44], ["small-lean-in", 0.3], ["side-glance", 0.15], ["quick-nod", 0.11]];
  } else if (emotion === "surprised" || emotion === "excited") {
    candidates = [["bright-pop", 0.42], ["quick-nod", 0.34], ["curious-tilt", 0.14], ["warm-sway", 0.1]];
  } else if (emotion === "anger" || emotion === "annoyed") {
    candidates = [["firm-lean", 0.42], ["side-set", 0.34], ["slow-glance-down", 0.13], ["small-lean-in", 0.11]];
  } else if (emotion === "sad" || emotion === "concerned") {
    candidates = [["soft-sink", 0.42], ["slow-glance-down", 0.32], ["side-glance", 0.15], ["warm-sway", 0.11]];
  } else if (emotion === "happy" || emotion === "affectionate") {
    candidates = [["quick-nod", 0.38], ["warm-sway", 0.36], ["small-lean-in", 0.15], ["shy-dip", 0.11]];
  } else if (emotion === "calm") {
    candidates = [["warm-sway", 0.44], ["small-lean-in", 0.25], ["side-glance", 0.17], ["soft-sink", 0.14]];
  } else {
    candidates = [["warm-sway", 0.34], ["curious-tilt", 0.3], ["side-glance", 0.2], ["quick-nod", 0.16]];
  }
  const fresh = candidates.filter(([label]) => !recentLabels.includes(label));
  const pool = fresh.length > 0 ? fresh : candidates;
  const weighted = pool.map(([label, weight]) => ({ label, weight }));
  const total = weighted.reduce((sum, item) => sum + item.weight, 0);
  let roll = context.random() * total;
  for (const item of weighted) {
    roll -= item.weight;
    if (roll <= 0) return item.label;
  }
  return weighted[0].label;
}
function gesturePeak(family, context) {
  const a = context.amplitude;
  const side = context.side;
  const gain = context.bodyMotionGain;
  const positive = Math.max(0, context.vad.valence);
  const negative = Math.max(0, -context.vad.valence);
  const aroused = Math.max(0, context.vad.arousal);
  const submissive = Math.max(0, -context.vad.dominance);
  const dominant = Math.max(0, context.vad.dominance);
  const body = (value) => value * gain * 1.24;
  if (family === "quick-nod") {
    return clampFACSState({
      headY: body(a * (0.42 + aroused * 0.18)),
      headZ: side * body(a * 0.18),
      bodyY: body(a * 0.28),
      bodyZ: side * body(a * 0.16),
      gazeY: a * 0.1,
      eyeSmile: a * (0.36 + positive * 0.24),
      mouthSmile: a * (0.42 + positive * 0.22),
      browOuterUp: a * 0.14
    });
  }
  if (family === "warm-sway") {
    return clampFACSState({
      headX: side * body(a * 0.22),
      headZ: side * body(a * 0.36),
      bodyX: side * body(a * 0.24),
      bodyZ: side * body(a * 0.3),
      gazeX: -side * a * 0.14,
      eyeSmile: a * 0.32,
      mouthSmile: a * 0.34,
      blush: positive * submissive * a * 0.42
    });
  }
  if (family === "shy-dip") {
    return clampFACSState({
      headY: -body(a * 0.48),
      headZ: -side * body(a * 0.42),
      bodyX: side * body(a * 0.12),
      bodyY: -body(a * 0.18),
      bodyZ: -side * body(a * 0.28),
      gazeX: side * a * 0.22,
      gazeY: -a * 0.32,
      browInnerUp: a * 0.24,
      eyeSmile: a * 0.18,
      blush: a * (0.32 + submissive * 0.34),
      mouthSmile: a * 0.18
    });
  }
  if (family === "side-glance") {
    return clampFACSState({
      headX: side * body(a * 0.18),
      headZ: -side * body(a * 0.28),
      bodyZ: -side * body(a * 0.18),
      gazeX: side * a * 0.46,
      gazeY: -a * 0.18,
      browInnerUp: a * 0.2,
      eyeSquint: a * 0.12,
      blush: a * 0.22
    });
  }
  if (family === "curious-tilt") {
    return clampFACSState({
      headX: side * body(a * 0.2),
      headY: body(a * 0.12),
      headZ: side * body(a * 0.62),
      bodyX: side * body(a * 0.1),
      bodyY: body(a * 0.16),
      gazeX: side * a * 0.26,
      gazeY: a * 0.12,
      browOuterUp: a * 0.28,
      eyeSquint: a * 0.1
    });
  }
  if (family === "small-lean-in") {
    return clampFACSState({
      headY: body(a * 0.2),
      headZ: side * body(a * 0.22),
      bodyY: body(a * 0.38),
      bodyZ: side * body(a * 0.14),
      gazeY: a * 0.14,
      browOuterUp: a * 0.18,
      eyeSmile: positive * a * 0.22,
      mouthSmile: positive * a * 0.24
    });
  }
  if (family === "bright-pop") {
    return clampFACSState({
      headY: body(a * 0.34),
      headZ: side * body(a * 0.22),
      bodyY: body(a * 0.36),
      bodyZ: side * body(a * 0.2),
      gazeY: a * 0.2,
      browOuterUp: a * 0.42,
      eyeSmile: positive * a * 0.24,
      mouthSmile: positive * a * 0.36,
      sweat: negative * aroused * a * 0.18
    });
  }
  if (family === "firm-lean") {
    return clampFACSState({
      headY: body(a * 0.22),
      headZ: side * body(a * 0.2),
      bodyY: body(a * 0.42),
      bodyZ: side * body(a * 0.16),
      gazeY: a * 0.12,
      browDown: a * (0.32 + dominant * 0.28),
      eyeSquint: a * 0.2,
      mouthFrown: a * 0.22
    });
  }
  if (family === "side-set") {
    return clampFACSState({
      headX: -side * body(a * 0.18),
      headZ: side * body(a * 0.34),
      bodyZ: side * body(a * 0.24),
      gazeX: -side * a * 0.26,
      browDown: a * 0.24,
      eyeSquint: a * 0.18,
      mouthFrown: a * 0.16
    });
  }
  if (family === "soft-sink") {
    return clampFACSState({
      headY: -body(a * 0.34),
      headZ: side * body(a * 0.16),
      bodyY: -body(a * 0.24),
      gazeY: -a * 0.34,
      browInnerUp: a * 0.28,
      mouthFrown: a * (0.22 + negative * 0.16)
    });
  }
  return clampFACSState({
    headY: -body(a * 0.22),
    bodyY: -body(a * 0.18),
    gazeY: -a * 0.42,
    browInnerUp: a * 0.22,
    eyeSquint: a * 0.12,
    mouthFrown: a * 0.14
  });
}
function scaleGesture(facs, scale) {
  const result = {};
  for (const [key, value] of Object.entries(facs)) {
    if (typeof value !== "number") continue;
    result[key] = value * scale;
  }
  return clampFACSState(result);
}
function gestureRestFrame(facs) {
  const result = {};
  for (const key of Object.keys(facs)) {
    result[key] = key === "breath" ? defaultFACSState.breath : 0;
  }
  return result;
}
function normalizeGestureEmotion(value, vad) {
  const emotion = value?.trim() ?? "neutral";
  if (emotion === "soft-happy" || emotion === "soft-positive") return "happy";
  if (emotion === "soft-calm") return "calm";
  if (emotion === "soft-curious") return "curious";
  if (emotion === "soft-shy") return "shy";
  if (emotion === "soft-uneasy") return "anxiety";
  if (emotion === "soft-low") return "sad";
  if (emotion === "soft-steady") return "neutral";
  if (emotion === "angry") return "anger";
  if (emotion !== "neutral") return emotion;
  if (vad.valence > 0.22 && vad.dominance < -0.18) return "shy";
  if (vad.valence > 0.2 && vad.arousal > 0.24) return "happy";
  if (vad.valence < -0.24 && vad.arousal > 0.18) return vad.dominance > 0.1 ? "anger" : "anxiety";
  if (vad.valence < -0.18) return "sad";
  if (vad.arousal > 0.18) return "curious";
  if (vad.arousal < -0.18) return "calm";
  return "neutral";
}
function vadMagnitude3(vad) {
  return clamp(
    (Math.abs(vad.valence) + Math.abs(vad.arousal) * 0.82 + Math.abs(vad.dominance) * 0.64) / 2.46,
    0,
    1
  );
}
var neutralVAD3 = {
  valence: 0,
  arousal: 0,
  dominance: 0
};
function deltaMagnitude(vector) {
  return Math.abs(vector.valence) + Math.abs(vector.arousal) * 0.82 + Math.abs(vector.dominance) * 0.62;
}
var VADMicroMotionController = class {
  constructor(seed = 4421) {
    __publicField(this, "seed");
    __publicField(this, "previous", null);
    __publicField(this, "pulse", null);
    __publicField(this, "random");
    __publicField(this, "nextAllowedPulseAt", 0);
    __publicField(this, "phases");
    this.seed = seed;
    this.random = seededRandom(seed);
    this.phases = this.createPhases();
  }
  reset() {
    this.previous = null;
    this.pulse = null;
    this.nextAllowedPulseAt = 0;
    this.random = seededRandom(this.seed);
    this.phases = this.createPhases();
  }
  update(timeSeconds, vad, focusLevel, bodyMotionGain = 1) {
    const focus = clamp(focusLevel, 0, 1);
    const motionGain = clamp(bodyMotionGain, 0, 4);
    const delta = this.getDelta(vad);
    this.maybeStartPulse(timeSeconds, delta, focus);
    this.previous = { ...vad };
    return addFACS(
      this.continuousLayer(timeSeconds, vad, focus, motionGain),
      this.pulseLayer(timeSeconds, focus, motionGain)
    );
  }
  getDelta(vad) {
    const previous = this.previous ?? neutralVAD3;
    return {
      valence: vad.valence - previous.valence,
      arousal: vad.arousal - previous.arousal,
      dominance: vad.dominance - previous.dominance
    };
  }
  maybeStartPulse(timeSeconds, delta, focus) {
    const magnitude2 = deltaMagnitude(delta);
    const threshold = focus > 0.5 ? 0.012 : 48e-4;
    if (magnitude2 < threshold || timeSeconds < this.nextAllowedPulseAt) return;
    this.pulse = {
      startedAt: timeSeconds,
      duration: 0.42 + this.random() * 0.38,
      vector: delta,
      amplitude: clamp(magnitude2 * 2.7, 0.018, 0.12) * (1 - focus * 0.48),
      side: this.random() < 0.5 ? -1 : 1
    };
    this.nextAllowedPulseAt = timeSeconds + 0.42 + this.random() * 0.7;
  }
  continuousLayer(timeSeconds, vad, focus, motionGain) {
    const magnitude2 = clamp(deltaMagnitude(vad) * 0.85, 0, 0.1);
    if (magnitude2 < 3e-3) return {};
    const idleWeight = 1 - focus * 0.56;
    const slow = Math.sin(timeSeconds * 0.86 + vad.valence * 9.2 + this.phases[0]);
    const mid = Math.sin(timeSeconds * 1.34 + vad.arousal * 7.6 + 1.7 + this.phases[1]);
    const side = Math.sin(timeSeconds * 0.47 + vad.dominance * 5.1 + this.phases[2]);
    const positive = Math.max(0, vad.valence);
    const negative = Math.max(0, -vad.valence);
    const aroused = Math.max(0, vad.arousal);
    const calm = Math.max(0, -vad.arousal);
    const submissive = Math.max(0, -vad.dominance);
    const dominant = Math.max(0, vad.dominance);
    return clampFACSState({
      mouthSmile: positive * 0.026 * (0.7 + slow * 0.3) * idleWeight,
      mouthFrown: negative * 0.018 * (0.75 + mid * 0.25) * idleWeight,
      browInnerUp: (negative * 0.024 + submissive * 0.012) * (0.74 + slow * 0.22) * idleWeight,
      browOuterUp: aroused * 0.018 * (0.72 + mid * 0.25) * idleWeight,
      eyeSmile: positive * 0.02 * (0.75 + slow * 0.2) * idleWeight,
      eyeSquint: (negative * 0.014 + calm * 0.01) * (0.75 + mid * 0.2) * idleWeight,
      bodyX: (side * 8e-3 + vad.valence * 0.01) * idleWeight * motionGain,
      bodyY: (vad.arousal * 8e-3 + dominant * 6e-3 - submissive * 7e-3 + slow * magnitude2 * 0.018) * idleWeight * motionGain,
      bodyZ: (vad.dominance * 0.012 + side * magnitude2 * 0.03) * idleWeight * motionGain,
      headX: (side * magnitude2 * 0.024 + vad.valence * 6e-3) * idleWeight * motionGain,
      headY: (vad.arousal * 0.01 + vad.dominance * 6e-3 - submissive * 8e-3) * idleWeight * motionGain,
      headZ: (vad.valence * submissive * -0.022 + vad.dominance * 0.012 + side * magnitude2 * 0.04) * idleWeight * motionGain,
      gazeY: (dominant * 8e-3 - submissive * 0.014 + calm * -6e-3) * idleWeight * Math.min(1.7, motionGain)
    });
  }
  pulseLayer(timeSeconds, focus, motionGain) {
    if (!this.pulse) return {};
    const progress = (timeSeconds - this.pulse.startedAt) / this.pulse.duration;
    if (progress >= 1) {
      this.pulse = null;
      return {};
    }
    const envelope2 = Math.sin(Math.PI * clamp(progress, 0, 1));
    const amplitude = this.pulse.amplitude * envelope2 * (1 - focus * 0.34);
    const vector = this.pulse.vector;
    const positive = Math.max(0, vector.valence);
    const negative = Math.max(0, -vector.valence);
    const aroused = Math.max(0, vector.arousal);
    const calm = Math.max(0, -vector.arousal);
    const submissive = Math.max(0, -vector.dominance);
    const dominant = Math.max(0, vector.dominance);
    return clampFACSState({
      mouthSmile: positive * amplitude * 1.1,
      mouthFrown: negative * amplitude * 0.9,
      browInnerUp: (negative * 0.9 + submissive * 0.45) * amplitude,
      browOuterUp: aroused * amplitude * 0.8,
      browDown: dominant * negative * amplitude * 0.9,
      eyeSmile: positive * amplitude * 0.65,
      eyeSquint: (negative * dominant + calm * 0.3) * amplitude * 0.7,
      mouthOpen: aroused * amplitude * 0.34,
      bodyX: this.pulse.side * amplitude * 0.18 * motionGain,
      bodyY: (aroused * 0.12 - calm * 0.08 + dominant * 0.06 - submissive * 0.06) * amplitude * motionGain,
      bodyZ: ((dominant - submissive) * amplitude * 0.16 + this.pulse.side * amplitude * 0.08) * motionGain,
      headX: this.pulse.side * amplitude * 0.1 * motionGain,
      headY: (aroused * 0.12 + dominant * 0.07 - submissive * 0.08) * amplitude * motionGain,
      headZ: this.pulse.side * amplitude * 0.14 * motionGain
    });
  }
  createPhases() {
    return [this.random() * Math.PI * 2, this.random() * Math.PI * 2, this.random() * Math.PI * 2];
  }
};
var VADPrivateParameterOverlay = class {
  constructor() {
    __publicField(this, "candidates", []);
    __publicField(this, "declaredCandidates", []);
    __publicField(this, "totalParameters", 0);
    __publicField(this, "activeExclusiveCategory", null);
    __publicField(this, "activeVariantByCategory", {});
  }
  setParameters(parameters, privateEmotionMap = {}, profileMappedIds = /* @__PURE__ */ new Set()) {
    this.totalParameters = Object.keys(parameters).length;
    const mappings = privateEmotionMap && typeof privateEmotionMap === "object" && !Array.isArray(privateEmotionMap) ? privateEmotionMap : {};
    this.declaredCandidates = selectDeclaredCandidates(parameters, mappings);
    const excludedHeuristicIds = /* @__PURE__ */ new Set([
      ...profileMappedIds,
      ...this.declaredCandidates.map((candidate) => candidate.id)
    ]);
    this.candidates = selectCandidates(parameters, excludedHeuristicIds);
    this.activeExclusiveCategory = null;
    this.activeVariantByCategory = {};
  }
  getSummary() {
    const categories = {};
    for (const candidate of this.candidates) {
      categories[candidate.category] = (categories[candidate.category] ?? 0) + 1;
    }
    for (const candidate of this.declaredCandidates) {
      const category = candidate.mapping.category ?? "privateEffect";
      categories[category] = (categories[category] ?? 0) + 1;
    }
    return {
      totalParameters: this.totalParameters,
      candidateCount: this.candidates.length + this.declaredCandidates.length,
      categories
    };
  }
  update(vadState, weight = 1, context = {}) {
    if (this.candidates.length === 0 && this.declaredCandidates.length === 0 || weight <= 0) return {};
    const result = {};
    const vad = vadState.current;
    const emotion = normalizeText(vadState.dominantEmotion);
    const baseAmounts = createCategoryAmounts();
    for (const candidate of this.candidates) {
      const amount = privateEmotionAmount(candidate.category, vad.valence, vad.arousal, vad.dominance, emotion);
      baseAmounts[candidate.category] = Math.max(baseAmounts[candidate.category], amount);
    }
    const amounts = resolveCategoryConflicts(baseAmounts, emotion, this.activeExclusiveCategory);
    this.activeExclusiveCategory = currentExclusiveCategory(amounts);
    const activeSelection = selectActiveCandidates(this.candidates, amounts, this.activeVariantByCategory);
    this.activeVariantByCategory = activeSelection.variants;
    for (const candidate of this.candidates) {
      const amount = activeSelection.ids.has(candidate.id) ? amounts[candidate.category] : 0;
      result[candidate.id] = activeValue(candidate.info, amount * weight);
    }
    Object.assign(result, evaluateDeclaredCandidates(this.declaredCandidates, vadState, weight, context));
    return result;
  }
};
var privateEmotionCategories = [
  "positiveEye",
  "blush",
  "tear",
  "shadow",
  "anger",
  "sweat",
  "surprise",
  "privateEffect"
];
var exclusiveCategories = [
  "positiveEye",
  "tear",
  "shadow",
  "anger",
  "sweat",
  "surprise",
  "privateEffect"
];
function selectCandidates(parameters, excludedIds = /* @__PURE__ */ new Set()) {
  const selected = [];
  for (const [id, info] of Object.entries(parameters)) {
    if (excludedIds.has(id)) continue;
    if (!Number.isFinite(info.min) || !Number.isFinite(info.max)) continue;
    if (isLowValueParameter(id, info) || isMouthOpenParameter(id, info) || isCoreMotionParameter(id, info)) continue;
    const category = classifyPrivateEmotionParameter(id, info);
    if (!category) continue;
    selected.push({
      id,
      info,
      category,
      priority: categoryPriority(category, id, info)
    });
  }
  return selected.sort((left, right) => left.priority - right.priority || left.id.localeCompare(right.id)).slice(0, 32);
}
function selectDeclaredCandidates(parameters, mappings) {
  const result = [];
  for (const [mappingKey, mapping] of Object.entries(mappings)) {
    const targets = uniqueStrings([
      ...mapping.target ? [mapping.target] : [],
      ...mapping.targets ?? []
    ]);
    for (const id of targets) {
      const info = parameters[id];
      if (!info || !Number.isFinite(info.min) || !Number.isFinite(info.max)) continue;
      if (isLowValueParameter(id, info) || isMouthOpenParameter(id, info)) continue;
      result.push({ mappingKey, id, info, mapping });
    }
  }
  return result.slice(0, 64);
}
function evaluateDeclaredCandidates(candidates, vadState, weight, context) {
  if (candidates.length === 0) return {};
  const evaluated = candidates.map((candidate) => ({
    candidate,
    amount: declaredEmotionAmount(candidate.mapping, vadState, context) * weight
  }));
  const groupWinners = /* @__PURE__ */ new Map();
  for (const item of evaluated.filter((entry) => entry.amount > 0)) {
    const group = item.candidate.mapping.exclusiveGroup?.trim();
    if (!group) continue;
    const currentKey = groupWinners.get(group);
    const current = currentKey ? evaluated.find((entry) => entry.candidate.mappingKey === currentKey) : void 0;
    if (!current || declaredScore(item) > declaredScore(current)) {
      groupWinners.set(group, item.candidate.mappingKey);
    }
  }
  const byTarget = /* @__PURE__ */ new Map();
  for (const item of evaluated) {
    const group = item.candidate.mapping.exclusiveGroup?.trim();
    const allowed = !group || !groupWinners.has(group) || groupWinners.get(group) === item.candidate.mappingKey;
    const normalized = allowed ? item : { ...item, amount: 0 };
    byTarget.set(item.candidate.id, [...byTarget.get(item.candidate.id) ?? [], normalized]);
  }
  const result = {};
  for (const [id, items] of byTarget) {
    const selected = [...items].sort((left, right) => Number(right.amount > 0) - Number(left.amount > 0) || declaredScore(right) - declaredScore(left))[0];
    if (selected) {
      result[id] = declaredValue(selected.candidate.info, selected.candidate.mapping, selected.amount);
    }
  }
  return result;
}
function declaredEmotionAmount(mapping, vadState, context) {
  const checks = [];
  const emotions = [
    vadState.dominantEmotion,
    context.intentEmotion,
    context.intentVariant
  ].filter((value) => Boolean(value)).map(normalizeText);
  if (mapping.emotions?.length) {
    checks.push(mapping.emotions.some((candidate) => {
      const normalized = normalizeText(candidate);
      return emotions.some((emotion) => emotion.includes(normalized) || normalized.includes(emotion));
    }));
  }
  if (mapping.vadRange && Object.keys(mapping.vadRange).length > 0) {
    checks.push(vadMatchesRange(vadState, mapping));
  }
  if (checks.length > 0) {
    const active = mapping.triggerMode === "all" ? checks.every(Boolean) : checks.some(Boolean);
    if (!active) return 0;
    return clamp(mapping.intensity ?? Math.max(vadState.intensity, 0.65), 0, 1);
  }
  return privateEmotionAmount(
    mapping.category ?? "privateEffect",
    vadState.current.valence,
    vadState.current.arousal,
    vadState.current.dominance,
    normalizeText(vadState.dominantEmotion)
  );
}
function vadMatchesRange(vadState, mapping) {
  const range = mapping.vadRange;
  if (!range) return false;
  const axes = ["valence", "arousal", "dominance"];
  return axes.every((axis) => {
    const limits = range[axis];
    if (!limits) return true;
    const min = Math.min(limits[0], limits[1]);
    const max = Math.max(limits[0], limits[1]);
    return vadState.current[axis] >= min && vadState.current[axis] <= max;
  });
}
function declaredScore(item) {
  return item.amount + (item.candidate.mapping.priority ?? 0) / 100;
}
function declaredValue(info, mapping, amount) {
  const min = Math.min(info.min, info.max);
  const max = Math.max(info.min, info.max);
  const neutral = clamp(mapping.neutralValue ?? info.default, min, max);
  const active = clamp(mapping.activeValue ?? farthestEndpoint(neutral, min, max), min, max);
  return clamp(neutral + (active - neutral) * clamp(amount, 0, 1), min, max);
}
function farthestEndpoint(neutral, min, max) {
  return Math.abs(max - neutral) >= Math.abs(neutral - min) ? max : min;
}
function uniqueStrings(values) {
  return [...new Set(values.filter(Boolean))];
}
function createCategoryAmounts() {
  return {
    positiveEye: 0,
    blush: 0,
    tear: 0,
    shadow: 0,
    anger: 0,
    sweat: 0,
    surprise: 0,
    privateEffect: 0
  };
}
function resolveCategoryConflicts(base, emotion, previous) {
  const result = createCategoryAmounts();
  const primary = chooseExclusiveCategory(base, emotion, previous);
  if (!primary) {
    result.blush = visibleAmount(base.blush);
    return result;
  }
  result[primary] = visibleAmount(base[primary]);
  if (primary === "positiveEye") {
    result.blush = visibleAmount(Math.min(base.blush, 0.56));
  } else if (primary === "surprise" && hasAny(emotion, ["surprised", "confused"])) {
    result.sweat = visibleAmount(Math.min(base.sweat * 0.42, 0.24));
  } else if (primary === "sweat" && hasAny(emotion, ["anxiety", "confused"])) {
    result.shadow = visibleAmount(Math.min(base.shadow * 0.34, 0.22));
  }
  if (!exclusiveCategories.includes(primary)) {
    result.blush = visibleAmount(base.blush);
  }
  return result;
}
function chooseExclusiveCategory(base, emotion, previous) {
  const scored = exclusiveCategories.map((category) => ({
    category,
    amount: base[category],
    score: categoryScore(category, base[category], emotion)
  })).filter((item) => item.amount >= 0.045).sort((left, right) => right.score - left.score || categoryPriorityRank(left.category) - categoryPriorityRank(right.category));
  const winner = scored[0];
  if (!winner || winner.score < 0.075) return null;
  if (previous) {
    const previousScore = categoryScore(previous, base[previous], emotion);
    if (base[previous] >= 0.055 && winner.category !== previous && winner.score - previousScore < 0.14) {
      return previous;
    }
  }
  return winner.category;
}
function categoryScore(category, amount, emotion) {
  if (amount <= 0) return 0;
  return amount + categoryEmotionBias(category, emotion);
}
function categoryEmotionBias(category, emotion) {
  switch (category) {
    case "positiveEye":
      return emotionBoost(emotion, ["happy", "excited", "affectionate"], 0.18) + emotionBoost(emotion, ["shy"], 0.08);
    case "tear":
      return emotionBoost(emotion, ["sad"], 0.24) + emotionBoost(emotion, ["concerned"], 0.1);
    case "shadow":
      return emotionBoost(emotion, ["anxiety"], 0.18) + emotionBoost(emotion, ["anger", "angry"], 0.08);
    case "anger":
      return emotionBoost(emotion, ["anger", "angry"], 0.26);
    case "sweat":
      return emotionBoost(emotion, ["anxiety", "confused"], 0.18) + emotionBoost(emotion, ["surprised"], 0.06);
    case "surprise":
      return emotionBoost(emotion, ["surprised"], 0.28) + emotionBoost(emotion, ["confused"], 0.06);
    case "privateEffect":
    case "blush":
      return 0;
  }
}
function currentExclusiveCategory(amounts) {
  let best = null;
  for (const category of exclusiveCategories) {
    const amount = amounts[category];
    if (amount <= 0) continue;
    if (!best || amount > best.amount) best = { category, amount };
  }
  return best?.amount && best.amount >= 0.04 ? best.category : null;
}
function categoryPriorityRank(category) {
  const rank = {
    positiveEye: 0,
    blush: 1,
    tear: 2,
    shadow: 3,
    anger: 4,
    sweat: 5,
    surprise: 6,
    privateEffect: 7
  };
  return rank[category];
}
function visibleAmount(amount) {
  return amount >= 0.04 ? clamp(amount, 0, 1) : 0;
}
function selectActiveCandidates(candidates, amounts, previousVariants) {
  const ids = /* @__PURE__ */ new Set();
  const variants = {};
  for (const category of privateEmotionCategories) {
    if (amounts[category] <= 0) continue;
    const categoryCandidates = candidates.filter((candidate) => candidate.category === category);
    if (categoryCandidates.length === 0) continue;
    const variant = chooseVariant(categoryCandidates, previousVariants[category]);
    variants[category] = variant;
    const picked = pickLimitedCandidates(
      categoryCandidates.filter((candidate) => candidateVariantKey(candidate) === variant),
      categoryCandidateLimit(category)
    );
    for (const candidate of picked) {
      ids.add(candidate.id);
    }
  }
  return { ids, variants };
}
function chooseVariant(candidates, previous) {
  const groups = /* @__PURE__ */ new Map();
  for (const candidate of candidates) {
    const variant = candidateVariantKey(candidate);
    groups.set(variant, Math.min(groups.get(variant) ?? Number.POSITIVE_INFINITY, candidate.priority));
  }
  if (previous && groups.has(previous)) return previous;
  return [...groups.entries()].sort((left, right) => left[1] - right[1] || left[0].localeCompare(right[0]))[0]?.[0] ?? "default";
}
function pickLimitedCandidates(candidates, limit) {
  const sorted = [...candidates].sort((left, right) => left.priority - right.priority || left.id.localeCompare(right.id));
  if (limit <= 1 || sorted.length <= 1) return sorted.slice(0, 1);
  const sided = sorted.filter((candidate) => parameterSide(candidate.id, candidate.info));
  if (sided.length >= 2) {
    const result = [];
    const usedSides = /* @__PURE__ */ new Set();
    for (const candidate of sorted) {
      const side = parameterSide(candidate.id, candidate.info);
      if (!side || usedSides.has(side)) continue;
      result.push(candidate);
      usedSides.add(side);
      if (result.length >= limit) break;
    }
    if (result.length > 0) return result;
  }
  return sorted.slice(0, 1);
}
function categoryCandidateLimit(category) {
  if (category === "positiveEye" || category === "blush" || category === "tear") return 2;
  return 1;
}
function candidateVariantKey(candidate) {
  const text = parameterText(candidate.id, candidate.info);
  if (candidate.category === "positiveEye" || candidate.category === "privateEffect") {
    if (hasAny(text, ["\u7231\u5FC3", "\u5FC3", "heart", "love"])) return "heart";
    if (hasAny(text, ["\u661F", "star"])) return "star";
    if (hasAny(text, ["\u95EA", "sparkle", "highlight", "\u9AD8\u5149"])) return "sparkle";
  }
  if (candidate.category === "shadow" && hasAny(text, ["\u9ED1", "dark", "black"])) return "dark";
  if (candidate.category === "anger" && hasAny(text, ["\u6012", "angry", "anger", "mad"])) return "anger";
  if (candidate.category === "surprise" && hasAny(text, ["\u60CA", "shock", "surprise"])) return "surprise";
  return candidate.category;
}
function parameterSide(id, info) {
  const raw = `${id} ${info.name ?? ""} ${info.groupName ?? ""}`.toLowerCase();
  if (raw.includes("\u5DE6") || raw.includes("left") || /(?:^|[^a-z])l(?:\d|$|[^a-z])/u.test(raw) || /l(?:\d)?$/u.test(raw)) {
    return "left";
  }
  if (raw.includes("\u53F3") || raw.includes("right") || /(?:^|[^a-z])r(?:\d|$|[^a-z])/u.test(raw) || /r(?:\d)?$/u.test(raw)) {
    return "right";
  }
  return null;
}
function classifyPrivateEmotionParameter(id, info) {
  const text = parameterText(id, info);
  if (hasAny(text, ["\u7231\u5FC3\u773C", "\u5FC3\u773C", "heart eye", "hearteye", "loveeye", "love eyes", "\u661F\u661F\u773C", "star eye", "stareye", "sparkleeye", "\u95EA\u773C"])) return "positiveEye";
  if (hasAny(text, ["\u8138\u7EA2", "\u816E\u7EA2", "\u8138\u988A\u7EA2", "blush", "cheekred", "\u7167\u308C"])) return "blush";
  if (hasAny(text, ["\u773C\u6CEA", "\u6CEA", "\u54ED", "tear", "cry", "crying"])) return "tear";
  if (hasAny(text, ["\u8138\u9ED1", "\u9ED1\u8138", "\u9634\u5F71", "\u9ED1\u5316", "shade", "shadow", "dark face", "faceshadow"])) return "shadow";
  if (hasAny(text, ["\u751F\u6C14", "\u6012", "angry", "anger", "mad"])) return "anger";
  if (hasAny(text, ["\u6C57", "\u51B7\u6C57", "sweat", "drop"])) return "sweat";
  if (hasAny(text, ["\u60CA", "\u60CA\u8BB6", "\u9707\u60CA", "surprise", "shock", "\u3073\u3063\u304F\u308A"])) return "surprise";
  if (hasAny(text, ["\u7279\u6548", "\u7B26\u53F7", "\u8868\u60C5", "effect", "emoji", "mark", "heart", "star", "\u5FC3", "\u661F"])) return "privateEffect";
  return null;
}
function privateEmotionAmount(category, valence, arousal, dominance, emotion) {
  const positive = Math.max(valence, 0);
  const negative = Math.max(-valence, 0);
  const highArousal = Math.max(arousal, 0);
  const lowDominance = Math.max(-dominance, 0);
  const highDominance = Math.max(dominance, 0);
  switch (category) {
    case "positiveEye":
      return trigger(positive * 0.82 + highArousal * 0.32 + emotionBoost(emotion, ["happy", "excited", "affectionate"], 0.34), 0.42);
    case "blush":
      return trigger(positive * 0.34 + lowDominance * 0.36 + emotionBoost(emotion, ["shy", "affectionate"], 0.58), 0.28);
    case "tear":
      return trigger(negative * 0.72 + Math.max(-arousal, 0) * 0.24 + emotionBoost(emotion, ["sad"], 0.42), 0.36);
    case "shadow":
      return trigger(negative * 0.58 + highArousal * 0.24 + emotionBoost(emotion, ["anxiety", "anger", "angry"], 0.34), 0.42);
    case "anger":
      return trigger(negative * 0.5 + highArousal * 0.34 + highDominance * 0.24 + emotionBoost(emotion, ["anger", "angry"], 0.58), 0.4);
    case "sweat":
      return trigger(negative * 0.36 + highArousal * 0.52 + lowDominance * 0.24 + emotionBoost(emotion, ["anxiety", "confused"], 0.4), 0.36);
    case "surprise":
      return trigger(highArousal * 0.74 + emotionBoost(emotion, ["surprised", "excited"], 0.26), 0.5);
    case "privateEffect":
      return trigger(Math.abs(valence) * 0.3 + highArousal * 0.32 + emotionBoost(emotion, ["happy", "excited", "surprised"], 0.22), 0.48);
  }
}
function activeValue(info, amount) {
  const min = Math.min(info.min, info.max);
  const max = Math.max(info.min, info.max);
  const neutral = clamp(info.default, min, max);
  const normalizedAmount = clamp(amount, 0, 1);
  const distanceToMin = Math.abs(neutral - min);
  const distanceToMax = Math.abs(max - neutral);
  const activeTarget = distanceToMax >= distanceToMin ? max : min;
  return clamp(neutral + (activeTarget - neutral) * normalizedAmount, min, max);
}
function trigger(value, threshold) {
  if (value <= threshold) return 0;
  return clamp((value - threshold) / Math.max(1e-3, 1 - threshold), 0, 1);
}
function emotionBoost(emotion, emotions, boost) {
  return emotions.some((item) => emotion.includes(item)) ? boost : 0;
}
function categoryPriority(category, id, info) {
  const text = parameterText(id, info);
  const exactBonus = hasAny(text, ["\u773C", "eye", "\u8138", "face", "cheek"]) ? -0.2 : 0;
  const rank = {
    positiveEye: 0,
    blush: 1,
    tear: 2,
    shadow: 3,
    anger: 4,
    sweat: 5,
    surprise: 6,
    privateEffect: 7
  };
  return rank[category] + exactBonus;
}
function isCoreMotionParameter(id, info) {
  const text = parameterText(id, info);
  return hasAny(text, [
    "anglex",
    "angley",
    "anglez",
    "bodyangle",
    "eyeball",
    "eyeopen",
    "mouthopen",
    "mouthform",
    "brow",
    "breath",
    "\u89D2\u5EA6",
    "\u8EAB\u4F53",
    "\u773C\u7403",
    "\u773C\u73E0",
    "\u7709",
    "\u5634"
  ]);
}
function isMouthOpenParameter(id, info) {
  const idAndName = normalizeText(`${id} ${info.name ?? ""}`);
  if (hasAny(idAndName, [
    "mouthform",
    "mouthshape",
    "lipshape",
    "lipform",
    "liptype",
    "\u5634\u578B",
    "\u53E3\u578B",
    "\u5507\u5F62",
    "\u5507\u578B"
  ])) return false;
  return hasAny(idAndName, [
    "mouthopen",
    "openmouth",
    "jawopen",
    "openjaw",
    "\u5634\u5F20\u5F00",
    "\u5F20\u5634",
    "\u5634\u5DF4\u5F00\u5408",
    "\u5634\u5F00\u5408",
    "\u53E3\u90E8\u5F00\u5408",
    "\u4E0B\u988C\u5F00\u5408"
  ]);
}
function isLowValueParameter(id, info) {
  const text = parameterText(id, info);
  return hasAny(text, [
    "copyright",
    "license",
    "watermark",
    "author",
    "\u6388\u6743",
    "\u76D7\u7248",
    "\u6B63\u7248",
    "\u6C34\u5370",
    "\u552E\u540E",
    "qq\u7FA4",
    "b\u7AD9",
    "\u8BF4\u660E",
    "\u8B66\u544A"
  ]);
}
function parameterText(id, info) {
  return normalizeText(`${id} ${info.name ?? ""} ${info.groupName ?? ""}`);
}
function normalizeText(text) {
  return text.replace(/\s+/gu, "").replace(/[＿_\-　/]/gu, "").toLowerCase();
}
function hasAny(text, hints) {
  return hints.some((hint) => text.includes(normalizeText(hint)));
}
var ActionUnitSolver = class {
  solve(actionUnits) {
    const au = normalizeActionUnits(actionUnits);
    const browInnerUp = au.au01InnerBrowRaiser * 0.92;
    const browOuterUp = au.au02OuterBrowRaiser * 0.9 + au.au05UpperLidRaiser * 0.18;
    const browDown = Math.max(au.au04BrowLowerer, au.au09NoseWrinkler * 0.45);
    const eyeSmile = clamp(au.au06CheekRaiser * 0.78 + au.au12LipCornerPuller * 0.12, 0, 1);
    const eyeSquint = clamp(au.au07LidTightener * 0.85 + au.au06CheekRaiser * 0.28, 0, 1);
    const upperLid = au.au05UpperLidRaiser * 0.24;
    const squintClose = au.au07LidTightener * 0.22 + au.au06CheekRaiser * 0.16;
    const eyeOpen = clamp(1 + upperLid - squintClose, 0.45, 1.24);
    const mouthSmile = clamp(au.au12LipCornerPuller * 0.88 + au.au14Dimpler * 0.22, 0, 1);
    const mouthFrown = clamp(au.au15LipCornerDepressor * 0.86 + au.au17ChinRaiser * 0.2, 0, 1);
    const mouthPucker = clamp(au.au18LipPucker * 0.9 + au.au23LipTightener * 0.22 + au.au24LipPressor * 0.18, 0, 1);
    const mouthOpen = clamp(
      au.au25LipsPart * 0.42 + au.au26JawDrop * 0.72 + au.au27MouthStretch * 0.86 + au.au10UpperLipRaiser * 0.16,
      0,
      1
    );
    return clampFACSState({
      browInnerUp,
      browOuterUp,
      browDown,
      eyeOpen,
      eyeSmile,
      eyeSquint,
      eyeBlinkL: au.au45Blink,
      eyeBlinkR: au.au45Blink,
      mouthSmile,
      mouthFrown,
      mouthOpen,
      mouthPucker,
      gazeX: au.gazeX,
      gazeY: au.gazeY,
      headX: au.headX,
      headY: au.headY,
      headZ: au.headZ,
      bodyX: au.bodyX,
      bodyY: au.bodyY,
      bodyZ: au.bodyZ,
      blush: au.blush,
      tear: au.tear,
      sweat: au.sweat,
      breath: au.breath
    });
  }
  solvePartial(actionUnits) {
    const solved = this.solve(actionUnits);
    const result = {};
    const keys = new Set(Object.keys(actionUnits));
    if (["au01InnerBrowRaiser", "au02OuterBrowRaiser", "au04BrowLowerer", "au05UpperLidRaiser", "au09NoseWrinkler"].some((key) => keys.has(key))) {
      result.browInnerUp = solved.browInnerUp;
      result.browOuterUp = solved.browOuterUp;
      result.browDown = solved.browDown;
    }
    if (["au05UpperLidRaiser", "au06CheekRaiser", "au07LidTightener"].some((key) => keys.has(key))) {
      result.eyeOpen = solved.eyeOpen;
      result.eyeSmile = solved.eyeSmile;
      result.eyeSquint = solved.eyeSquint;
    }
    if (keys.has("au45Blink")) {
      result.eyeBlinkL = solved.eyeBlinkL;
      result.eyeBlinkR = solved.eyeBlinkR;
    }
    if ([
      "au10UpperLipRaiser",
      "au12LipCornerPuller",
      "au14Dimpler",
      "au15LipCornerDepressor",
      "au17ChinRaiser",
      "au18LipPucker",
      "au20LipStretcher",
      "au23LipTightener",
      "au24LipPressor",
      "au25LipsPart",
      "au26JawDrop",
      "au27MouthStretch"
    ].some((key) => keys.has(key))) {
      result.mouthSmile = solved.mouthSmile;
      result.mouthFrown = solved.mouthFrown;
      result.mouthOpen = solved.mouthOpen;
      result.mouthPucker = solved.mouthPucker;
    }
    for (const key of ["gazeX", "gazeY", "headX", "headY", "headZ", "bodyX", "bodyY", "bodyZ", "blush", "tear", "sweat", "breath"]) {
      if (keys.has(key)) result[key] = solved[key];
    }
    return result;
  }
  project(facs) {
    const state = facs;
    return normalizeActionUnits({
      au01InnerBrowRaiser: state.browInnerUp ?? 0,
      au02OuterBrowRaiser: state.browOuterUp ?? 0,
      au04BrowLowerer: state.browDown ?? 0,
      au05UpperLidRaiser: Math.max(0, (state.eyeOpen ?? 1) - 1) * 3.2,
      au06CheekRaiser: state.eyeSmile ?? 0,
      au07LidTightener: state.eyeSquint ?? 0,
      au12LipCornerPuller: state.mouthSmile ?? 0,
      au15LipCornerDepressor: state.mouthFrown ?? 0,
      au18LipPucker: state.mouthPucker ?? 0,
      au25LipsPart: Math.min(1, (state.mouthOpen ?? 0) * 0.55),
      au26JawDrop: Math.min(1, (state.mouthOpen ?? 0) * 0.8),
      au45Blink: Math.max(state.eyeBlinkL ?? 0, state.eyeBlinkR ?? 0),
      gazeX: state.gazeX ?? 0,
      gazeY: state.gazeY ?? 0,
      headX: state.headX ?? 0,
      headY: state.headY ?? 0,
      headZ: state.headZ ?? 0,
      bodyX: state.bodyX ?? 0,
      bodyY: state.bodyY ?? 0,
      bodyZ: state.bodyZ ?? 0,
      blush: state.blush ?? 0,
      tear: state.tear ?? 0,
      sweat: state.sweat ?? 0,
      breath: state.breath ?? 0.5
    });
  }
};
function randomRange(range, random) {
  return range[0] + (range[1] - range[0]) * random();
}
function pickOne(items, random) {
  return items[Math.floor(random() * items.length) % items.length];
}
var defaultPersonality = {
  expressiveness: 0.85,
  softness: 0.65,
  shyness: 0.55,
  gazeStability: 0.7
};
var transitionFACSKeys = [
  "browInnerUp",
  "browOuterUp",
  "browDown",
  "eyeOpen",
  "eyeSmile",
  "eyeSquint",
  "eyeBlinkL",
  "eyeBlinkR",
  "mouthSmile",
  "mouthFrown",
  "mouthOpen",
  "mouthPucker",
  "gazeX",
  "gazeY",
  "blush",
  "tear",
  "sweat"
];
var livingJitter = {
  browInnerUp: 0.032,
  browOuterUp: 0.03,
  browDown: 0.026,
  eyeOpen: 0.026,
  eyeSmile: 0.026,
  eyeSquint: 0.022,
  mouthSmile: 0.036,
  mouthFrown: 0.028,
  mouthOpen: 0.032,
  mouthPucker: 0.018,
  gazeX: 0.036,
  gazeY: 0.028,
  headX: 0.018,
  headY: 0.014,
  headZ: 0.024,
  blush: 0.026,
  tear: 0.018,
  sweat: 0.018
};
var RuntimeExpressionGenerator = class {
  generate(input) {
    const random = seededRandom(input.seed);
    const personality = { ...defaultPersonality, ...input.personality };
    const archetype = getEmotionArchetype(input.emotion);
    const variantName = input.variant && archetype.variants[input.variant] ? input.variant : pickOne(Object.keys(archetype.variants), random);
    const variant = archetype.variants[variantName];
    const intensity = clamp01(input.intensity) * (0.65 + personality.expressiveness * 0.45);
    const ranges = this.mergeRanges(archetype.baseTendency, variant.ranges);
    const peakFACS = this.sampleFACS(ranges, intensity, random);
    this.applyContextBias(peakFACS, input.contextTags, personality);
    const timeline = this.buildTimeline(peakFACS, input.previousState, input.seed, random);
    return {
      emotion: archetype.emotion,
      variant: variantName,
      intensity: clamp01(input.intensity),
      timeline,
      peakFACS,
      idleBias: this.createIdleBias(archetype.emotion, variantName, peakFACS),
      recoveryDuration: 3.8 + random() * 2.8
    };
  }
  mergeRanges(base, variant) {
    return { ...base, ...variant };
  }
  sampleFACS(ranges, intensity, random) {
    const result = {};
    for (const key of Object.keys(ranges)) {
      const range = ranges[key];
      if (!range) continue;
      const sampled = randomRange(range, random);
      result[key] = key === "eyeOpen" ? 1 + (sampled - 1) * intensity : sampled * intensity;
    }
    return clampFACSState(result);
  }
  applyContextBias(facs, contextTags, personality) {
    if (contextTags.includes("compliment")) {
      facs.blush = Math.max(facs.blush ?? 0, 0.3 + personality.shyness * 0.45);
      facs.gazeX = facs.gazeX ?? -0.18;
      facs.gazeY = facs.gazeY ?? -0.08;
    }
    if (contextTags.includes("user_tired")) {
      facs.browInnerUp = Math.max(facs.browInnerUp ?? 0, 0.22 + personality.softness * 0.18);
      facs.eyeSmile = Math.max(facs.eyeSmile ?? 0, 0.05 + personality.softness * 0.1);
    }
    if (contextTags.includes("user_good_news")) {
      facs.eyeOpen = Math.max(facs.eyeOpen ?? 1, 1.05);
      facs.mouthSmile = Math.max(facs.mouthSmile ?? 0, 0.55);
    }
  }
  buildTimeline(peakFACS, previousState, seed, random) {
    const headTilt = (peakFACS.headZ ?? 0) + (random() - 0.5) * 0.08;
    const hasSmile = (peakFACS.mouthSmile ?? 0) > 0.25;
    const hasConcern = (peakFACS.browInnerUp ?? 0) > 0.18 && !hasSmile;
    const anticipationDuration = 0.2 + random() * 0.18;
    const settleDuration = 0.42 + random() * 0.22;
    const holdDuration = 0.5 + random() * 0.42;
    const gazeReturn = Math.abs(previousState.gazeX) > 0.16 ? previousState.gazeX * 0.2 : 0;
    const attention = {
      gazeX: gazeReturn,
      gazeY: 0,
      headX: 0,
      headY: 0,
      eyeOpen: Math.max(0.96, peakFACS.eyeOpen ?? 1),
      browInnerUp: Math.max(peakFACS.browInnerUp ?? 0, hasConcern ? 0.24 : 0.06)
    };
    const faceLead = {
      eyeOpen: peakFACS.eyeOpen,
      browInnerUp: peakFACS.browInnerUp,
      browOuterUp: peakFACS.browOuterUp,
      browDown: peakFACS.browDown,
      gazeX: peakFACS.gazeX,
      gazeY: peakFACS.gazeY
    };
    const expressionPeak = {
      ...peakFACS,
      headZ: headTilt
    };
    const transitionStart = this.createTransitionStart(previousState);
    const transitionAttention = this.createTransitionTarget(previousState, attention);
    const livingPeak = this.createLivingVariant(expressionPeak, random, 1);
    const livingSettle = this.createLivingVariant(expressionPeak, random, 0.72);
    const tinyNod = seed % 2 === 0 ? -0.03 : 0.035;
    const timeline = [];
    if (Object.keys(transitionStart).length > 0) {
      timeline.push({
        time: 0,
        duration: 0,
        easing: "linear",
        facs: transitionStart
      });
    }
    timeline.push(
      {
        time: 0,
        duration: anticipationDuration,
        easing: "easeInOut",
        facs: transitionAttention
      },
      {
        time: anticipationDuration * 0.72,
        duration: settleDuration,
        easing: "easeOut",
        facs: clampFACSState({
          ...faceLead,
          headY: tinyNod
        })
      },
      {
        time: anticipationDuration + settleDuration * 0.55,
        duration: holdDuration * 0.58,
        easing: "easeInOut",
        facs: clampFACSState(expressionPeak)
      },
      {
        time: anticipationDuration + settleDuration * 0.55 + holdDuration * 0.32,
        duration: holdDuration * 0.72,
        easing: "easeInOut",
        facs: livingPeak,
        weight: 0.96
      },
      {
        time: anticipationDuration + settleDuration + holdDuration * 0.6,
        duration: 0.45 + random() * 0.3,
        easing: "easeInOut",
        facs: clampFACSState({
          ...livingSettle,
          mouthOpen: hasSmile ? 0.05 : peakFACS.mouthOpen,
          headY: 0
        }),
        weight: 0.82
      }
    );
    return timeline;
  }
  createTransitionStart(previousState) {
    const result = {};
    for (const key of transitionFACSKeys) {
      const value = previousState[key];
      if (this.isActiveFromNeutral(key, value)) result[key] = value;
    }
    return clampFACSState(result);
  }
  createTransitionTarget(previousState, target) {
    const result = { ...target };
    for (const key of transitionFACSKeys) {
      if (result[key] !== void 0) continue;
      if (this.isActiveFromNeutral(key, previousState[key])) {
        result[key] = defaultFACSState[key];
      }
    }
    return clampFACSState(result);
  }
  createLivingVariant(base, random, amount) {
    const result = { ...base };
    for (const [key, range] of Object.entries(livingJitter)) {
      const value = base[key];
      if (typeof value !== "number") continue;
      const neutral = defaultFACSState[key];
      const activity = Math.min(1, Math.abs(value - neutral) * 2.4 + 0.28);
      result[key] = value + (random() - 0.5) * 2 * range * amount * activity;
    }
    return clampFACSState(result);
  }
  isActiveFromNeutral(key, value) {
    const threshold = key === "eyeOpen" ? 0.012 : 0.018;
    return Math.abs(value - defaultFACSState[key]) > threshold;
  }
  createIdleBias(emotion, variant, peakFACS) {
    if (emotion === "happy") {
      return {
        mouthSmile: Math.min(0.16, (peakFACS.mouthSmile ?? 0) * 0.18),
        eyeSmile: Math.min(0.1, (peakFACS.eyeSmile ?? 0) * 0.18),
        blush: variant.includes("shy") ? Math.min(0.18, (peakFACS.blush ?? 0) * 0.25) : 0
      };
    }
    if (emotion === "concerned") {
      return {
        browInnerUp: Math.min(0.1, (peakFACS.browInnerUp ?? 0) * 0.2),
        mouthSmile: Math.min(0.08, (peakFACS.mouthSmile ?? 0) * 0.2)
      };
    }
    return {
      mouthSmile: Math.min(0.06, (peakFACS.mouthSmile ?? 0) * 0.12)
    };
  }
};
function effectiveSchemaVersion(profile) {
  return profile.schemaVersion ?? 1;
}
function validateModelProfile(raw) {
  const errors = [];
  const warnings = [];
  if (typeof raw !== "object" || raw === null) {
    errors.push("Profile must be a non-null object");
    return { ok: false, profile: raw, errors, warnings };
  }
  const r = raw;
  if (typeof r["modelId"] !== "string" || r["modelId"] === "") {
    errors.push("Missing or invalid field: modelId (string required)");
  }
  if (typeof r["modelPath"] !== "string" || r["modelPath"] === "") {
    errors.push("Missing or invalid field: modelPath (string required)");
  }
  if (typeof r["parameterMap"] !== "object" || r["parameterMap"] === null || Array.isArray(r["parameterMap"])) {
    errors.push("Missing or invalid field: parameterMap (object required)");
  }
  if (typeof r["displayName"] !== "string" || r["displayName"] === "") {
    warnings.push("Missing or empty field: displayName");
  }
  if (typeof r["version"] !== "string" || r["version"] === "") {
    warnings.push("Missing or empty field: version");
  }
  if (r["capabilities"] === void 0 || r["capabilities"] === null) {
    warnings.push("Missing field: capabilities \u2014 will be derived at runtime");
  }
  if (typeof r["parameterMap"] === "object" && r["parameterMap"] !== null && !Array.isArray(r["parameterMap"])) {
    const pm = r["parameterMap"];
    for (const [key, rule] of Object.entries(pm)) {
      if (typeof rule === "object" && rule !== null) {
        const ruleObj = rule;
        if (ruleObj["target"] !== void 0 && typeof ruleObj["target"] !== "string") {
          warnings.push(`parameterMap.${key}.target is not a string`);
        }
        if (Array.isArray(ruleObj["targets"])) {
          const badCount = ruleObj["targets"].filter(
            (t) => typeof t !== "string"
          ).length;
          if (badCount > 0) {
            warnings.push(
              `parameterMap.${key}.targets contains ${badCount} non-string entry/entries`
            );
          }
        }
      }
    }
  }
  if (r["privateEmotionMap"] !== void 0) {
    if (typeof r["privateEmotionMap"] !== "object" || r["privateEmotionMap"] === null || Array.isArray(r["privateEmotionMap"])) {
      errors.push("Invalid field: privateEmotionMap (object required when present)");
    } else {
      for (const [key, mapping] of Object.entries(r["privateEmotionMap"])) {
        if (!mapping || typeof mapping !== "object" || Array.isArray(mapping)) {
          warnings.push(`privateEmotionMap.${key} is not an object`);
          continue;
        }
        const record = mapping;
        if (record["target"] !== void 0 && typeof record["target"] !== "string") {
          warnings.push(`privateEmotionMap.${key}.target is not a string`);
        }
        if (Array.isArray(record["targets"]) && record["targets"].some((target) => typeof target !== "string")) {
          warnings.push(`privateEmotionMap.${key}.targets contains a non-string entry`);
        }
      }
    }
  }
  return {
    ok: errors.length === 0,
    profile: raw,
    errors,
    warnings
  };
}
function applyFallbackStrategies(facs, profile) {
  const result = { ...facs };
  const map = profile.parameterMap;
  if ((result.eyeSmile ?? 0) > 0 && !map.eyeSmile && map.eyeOpen) {
    result.eyeOpen = Math.max(0, (result.eyeOpen ?? 1) - (result.eyeSmile ?? 0) * 0.22);
  }
  if (((result.gazeX ?? 0) !== 0 || (result.gazeY ?? 0) !== 0) && !map.gazeX && map.headX) {
    result.headX = (result.headX ?? 0) + (result.gazeX ?? 0) * 0.35;
    result.headY = (result.headY ?? 0) + (result.gazeY ?? 0) * 0.2;
  }
  if ((result.breath ?? 0) !== 0 && !map.breath && map.bodyY) {
    result.bodyY = (result.bodyY ?? 0) + ((result.breath ?? 0.5) - 0.5) * 0.12;
  }
  if (!profile.capabilities?.blush) delete result.blush;
  if (!profile.capabilities?.tear) delete result.tear;
  if (!profile.capabilities?.sweat) delete result.sweat;
  return result;
}
function ruleTargets(rule) {
  return rule.targets?.length ? rule.targets : rule.target ? [rule.target] : [];
}
function deriveNeutralParams(profile) {
  const result = {};
  for (const [facsKey, rule] of Object.entries(profile.parameterMap)) {
    for (const target of ruleTargets(rule)) {
      if (result[target] !== void 0) continue;
      if (facsKey === "eyeOpen") result[target] = 1;
      else if (facsKey === "breath") result[target] = 0.5;
      else result[target] = 0;
    }
  }
  for (const rule of Object.values(profile.customParams ?? {})) {
    for (const target of ruleTargets(rule)) {
      if (result[target] !== void 0) continue;
      result[target] = 0;
    }
  }
  return result;
}
function deriveParameterRanges(profile) {
  const ranges = {};
  for (const rule of [
    ...Object.values(profile.parameterMap),
    ...Object.values(profile.customParams ?? {})
  ]) {
    if (!rule) continue;
    const targets = ruleTargets(rule);
    for (const target of targets) {
      const existing = ranges[target] ?? {};
      ranges[target] = {
        min: existing.min === void 0 ? rule.min : rule.min === void 0 ? existing.min : Math.min(existing.min, rule.min),
        max: existing.max === void 0 ? rule.max : rule.max === void 0 ? existing.max : Math.max(existing.max, rule.max)
      };
    }
  }
  return ranges;
}
function hasExpressiveFields(rule) {
  return rule.curve !== void 0 || rule.gamma !== void 0 || rule.deadzone !== void 0 || rule.inputRange !== void 0 || rule.outputRange !== void 0 || rule.invertAround !== void 0;
}
function applyCurve(value, curve) {
  switch (curve) {
    case "easeIn":
      return value * value;
    case "easeOut":
      return 1 - (1 - value) * (1 - value);
    case "easeInOut":
      return value < 0.5 ? 2 * value * value : 1 - Math.pow(-2 * value + 2, 2) / 2;
    case "smoothstep":
      return value * value * (3 - 2 * value);
    case "linear":
    default:
      return value;
  }
}
function applyCurveSigned(value, curve) {
  if (value < 0) return -applyCurve(Math.abs(value), curve);
  return applyCurve(value, curve);
}
function transformRuleValue(value, rule) {
  const safeValue = Number.isFinite(value) ? value : 0;
  const scale = rule.scale ?? 1;
  const offset = rule.offset ?? 0;
  if (!hasExpressiveFields(rule)) {
    if (rule.mode === "inverse") {
      return 1 - safeValue * scale + offset;
    }
    if (rule.mode === "subtract") {
      return -(safeValue * scale) + offset;
    }
    return safeValue * scale + offset;
  }
  let mapped = safeValue;
  if (rule.inputRange) {
    const [inMin, inMax] = rule.inputRange;
    const denominator = inMax - inMin;
    mapped = denominator === 0 ? 0 : (mapped - inMin) / denominator;
  }
  const deadzone = rule.deadzone ?? 0;
  if (deadzone > 0) {
    const magnitude2 = Math.abs(mapped);
    if (magnitude2 < deadzone) {
      mapped = 0;
    } else {
      const denominator = 1 - deadzone;
      const rescaled = denominator <= 0 ? 0 : (magnitude2 - deadzone) / denominator;
      mapped = Math.sign(mapped) * rescaled;
    }
  }
  if (rule.gamma !== void 0 && rule.gamma > 0) {
    mapped = Math.sign(mapped) * Math.pow(Math.abs(mapped), rule.gamma);
  }
  mapped = applyCurveSigned(mapped, rule.curve);
  if (rule.mode === "inverse") {
    mapped = (rule.invertAround ?? 1) - mapped;
  } else if (rule.mode === "subtract") {
    mapped = -mapped;
  }
  if (rule.outputRange) {
    const [outMin, outMax] = rule.outputRange;
    mapped = outMin + mapped * (outMax - outMin);
  }
  return mapped * scale + offset;
}
var ModelProfileAdapter = class {
  constructor(profile) {
    __publicField(this, "profile");
    this.profile = profile;
  }
  setProfile(profile) {
    this.profile = profile;
  }
  getProfile() {
    return this.profile;
  }
  apply(facs, customChannels) {
    if (effectiveSchemaVersion(this.profile) < 2) {
      return this.applyLegacy(facs);
    }
    return this.applyV2(facs, customChannels ?? {});
  }
  applyLegacy(facs) {
    const normalized = applyFallbackStrategies(facs, this.profile);
    const effectiveNeutral = this.profile.neutralParams ?? deriveNeutralParams(this.profile);
    const result = { ...effectiveNeutral };
    for (const key of Object.keys(this.profile.parameterMap)) {
      const rule = this.profile.parameterMap[key];
      if (!rule) continue;
      const raw = normalized[key] ?? 0;
      const targets = this.getTargets(rule);
      if (targets.length === 0) continue;
      const mapped = this.mapValue(raw, rule, false);
      for (const target of targets) {
        if (rule.mode === "set" || result[target] === void 0) {
          result[target] = this.clampRuleValue(mapped, rule);
        } else {
          result[target] += mapped;
          result[target] = this.clampRuleValue(result[target], rule);
        }
      }
    }
    return result;
  }
  applyV2(facs, customChannels) {
    const normalized = applyFallbackStrategies(facs, this.profile);
    const effectiveNeutral = this.profile.neutralParams ?? deriveNeutralParams(this.profile);
    const result = { ...effectiveNeutral };
    const contributions = [];
    for (const key of Object.keys(this.profile.parameterMap)) {
      const rule = this.profile.parameterMap[key];
      if (!rule) continue;
      const raw = normalized[key] ?? 0;
      const mapped = transformRuleValue(raw, rule);
      for (const target of this.getTargets(rule)) {
        contributions.push({ target, rule, mapped });
      }
    }
    for (const [channel, rule] of Object.entries(this.profile.customParams ?? {})) {
      const raw = customChannels[channel] ?? 0;
      const mapped = transformRuleValue(raw, rule);
      for (const target of this.getTargets(rule)) {
        contributions.push({ target, rule, mapped });
      }
    }
    for (const contribution of contributions) {
      if (contribution.rule.mode === "add" || contribution.rule.mode === "subtract") continue;
      result[contribution.target] = this.clampRuleValue(contribution.mapped, contribution.rule);
    }
    for (const contribution of contributions) {
      if (contribution.rule.mode !== "add" && contribution.rule.mode !== "subtract") continue;
      result[contribution.target] = this.clampRuleValue((result[contribution.target] ?? 0) + contribution.mapped, contribution.rule);
    }
    return result;
  }
  getTargets(rule) {
    if (rule.targets?.length) return rule.targets;
    return rule.target ? [rule.target] : [];
  }
  mapValue(value, rule, shouldClamp = true) {
    const scale = rule.scale ?? 1;
    const offset = rule.offset ?? 0;
    let mapped = value;
    if (rule.mode === "inverse") {
      mapped = 1 - value * scale;
    } else if (rule.mode === "subtract") {
      mapped = -(value * scale);
    } else {
      mapped = value * scale;
    }
    mapped += offset;
    return shouldClamp ? this.clampRuleValue(mapped, rule) : mapped;
  }
  clampRuleValue(value, rule) {
    return clamp(value, rule.min, rule.max);
  }
};
async function loadModelProfile(url, fetcher = fetch) {
  const response = await fetcher(url);
  if (!response.ok) {
    throw new Error(`Failed to load model profile: ${response.status} ${response.statusText}`);
  }
  const raw = await response.json();
  const validation = validateModelProfile(raw);
  if (!validation.ok) {
    throw new Error(`Invalid model profile at ${url}: ${validation.errors[0]}`);
  }
  for (const w of validation.warnings) {
    console.warn(`[SoullinkProfile] ${w}`);
  }
  return {
    profile: validation.profile,
    sourceUrl: url
  };
}
function detectCapabilities(profile) {
  const map = profile.parameterMap;
  return {
    headControl: Boolean(map.headX || map.headY || map.headZ),
    bodyControl: Boolean(map.bodyX || map.bodyY || map.bodyZ),
    eyeBlink: Boolean(map.eyeBlinkL || map.eyeBlinkR),
    eyeSmile: Boolean(map.eyeSmile),
    gazeControl: Boolean(map.gazeX || map.gazeY),
    mouthOpen: Boolean(map.mouthOpen),
    mouthSmile: Boolean(map.mouthSmile),
    browControl: Boolean(map.browInnerUp || map.browOuterUp || map.browDown),
    blush: Boolean(map.blush),
    tear: Boolean(map.tear),
    sweat: Boolean(map.sweat),
    breath: Boolean(map.breath)
  };
}
var _token = 0;
function resolveNativeAnimation(profile, intent) {
  const hasExpressionMap = profile.expressionMap !== void 0 && Object.keys(profile.expressionMap).length > 0;
  const hasMotionMap = profile.motionMap !== void 0 && Object.keys(profile.motionMap).length > 0;
  if (!hasExpressionMap && !hasMotionMap) return null;
  const compositeKey = intent.variant !== void 0 && intent.variant !== "" ? `${intent.emotion}:${intent.variant}` : void 0;
  let expressionName = null;
  const expressionMap = profile.expressionMap ?? {};
  const rawBinding = (compositeKey !== void 0 ? expressionMap[compositeKey] : void 0) ?? expressionMap[intent.emotion];
  if (rawBinding !== void 0) {
    const name = typeof rawBinding === "string" ? rawBinding : rawBinding.expression;
    const minIntensity = typeof rawBinding === "object" ? rawBinding.minIntensity : void 0;
    if (minIntensity === void 0 || intent.intensity >= minIntensity) {
      expressionName = name;
    }
  }
  const motionMap = profile.motionMap ?? {};
  const motionBinding = (compositeKey !== void 0 ? motionMap[compositeKey] : void 0) ?? motionMap[intent.emotion] ?? null;
  if (expressionName === null && motionBinding === null) return null;
  const suppressParamIds = [];
  if (expressionName !== null && profile.nativeAnimations?.expressions) {
    const catalogEntry = profile.nativeAnimations.expressions.find(
      (entry) => entry.name === expressionName
    );
    if (catalogEntry?.params) {
      suppressParamIds.push(...catalogEntry.params);
    }
  }
  return {
    token: ++_token,
    expression: expressionName,
    motion: motionBinding,
    suppressParamIds
  };
}
var BlinkController = class {
  constructor(seed = 7, rate = 1) {
    __publicField(this, "random");
    __publicField(this, "nextBlinkAt", 0);
    __publicField(this, "blinkStartedAt", null);
    __publicField(this, "doubleBlinkQueued", false);
    __publicField(this, "rate");
    this.random = seededRandom(seed);
    this.rate = clamp(rate, 0.25, 2.5);
    this.scheduleNext(0);
  }
  defer(timeSeconds, duration) {
    this.blinkStartedAt = null;
    this.doubleBlinkQueued = false;
    const pauseScale = 1 / Math.sqrt(this.rate);
    this.nextBlinkAt = timeSeconds + Math.max(0, duration) + (0.75 + this.random() * 1.15) * pauseScale;
  }
  update(timeSeconds, focusLevel) {
    if (this.blinkStartedAt === null && timeSeconds >= this.nextBlinkAt) {
      this.blinkStartedAt = timeSeconds;
    }
    if (this.blinkStartedAt === null) {
      return { eyeBlinkL: 0, eyeBlinkR: 0 };
    }
    const elapsed = timeSeconds - this.blinkStartedAt;
    const closeDuration = 0.065;
    const holdDuration = 0.035;
    const openDuration = 0.13;
    const total = closeDuration + holdDuration + openDuration;
    let blink = 0;
    if (elapsed <= closeDuration) {
      blink = ease("easeIn", elapsed / closeDuration);
    } else if (elapsed <= closeDuration + holdDuration) {
      blink = 1;
    } else if (elapsed <= total) {
      blink = 1 - ease("easeOut", (elapsed - closeDuration - holdDuration) / openDuration);
    } else {
      const doubleBlinkChance = focusLevel > 0.4 ? 0 : Math.min(0.24, 0.16 * this.rate);
      const shouldDouble = !this.doubleBlinkQueued && this.random() < doubleBlinkChance;
      this.blinkStartedAt = null;
      if (shouldDouble) {
        this.doubleBlinkQueued = true;
        this.nextBlinkAt = timeSeconds + 0.18 + this.random() * 0.12;
      } else {
        this.doubleBlinkQueued = false;
        this.scheduleNext(timeSeconds, focusLevel);
      }
    }
    return {
      eyeBlinkL: blink,
      eyeBlinkR: blink
    };
  }
  scheduleNext(timeSeconds, focusLevel = 0) {
    const base = (3 + this.random() * 4) / this.rate;
    const focusedExtra = focusLevel * 1.1;
    this.nextBlinkAt = timeSeconds + base + focusedExtra;
  }
};
var swayKeys = ["bodyX", "bodyY", "bodyZ", "headX", "headY", "headZ"];
var defaultRanges = {
  bodyX: [-0.045, 0.045],
  bodyY: [-0.014, 0.014],
  bodyZ: [-0.055, 0.055],
  headX: [-0.028, 0.028],
  headY: [-0.016, 0.018],
  headZ: [-0.034, 0.034]
};
var profileRangeScale = {
  bodyX: 1,
  bodyY: 0.65,
  bodyZ: 1,
  headX: 0.45,
  headY: 0.42,
  headZ: 0.58
};
function neutralPose() {
  return {
    bodyX: 0,
    bodyY: 0,
    bodyZ: 0,
    headX: 0,
    headY: 0,
    headZ: 0
  };
}
var BodySwayController = class {
  constructor(seed = 29) {
    __publicField(this, "random");
    __publicField(this, "from", neutralPose());
    __publicField(this, "current", neutralPose());
    __publicField(this, "target", neutralPose());
    __publicField(this, "moveStartedAt", 0);
    __publicField(this, "moveDuration", 2.2);
    __publicField(this, "holdUntil", 0);
    this.random = seededRandom(seed);
  }
  update(timeSeconds, focusLevel, profile, gain = 1) {
    const focus = clamp(focusLevel, 0, 1);
    const motionGain = clamp(gain, 0, 4);
    if (focus > 0.5) {
      this.recenter(0.06 + focus * 0.08);
      return this.toLayer((1 - focus * 0.76) * motionGain);
    }
    if (timeSeconds >= this.holdUntil) {
      this.pickNextTarget(timeSeconds, profile);
    }
    const local = this.moveDuration <= 0 ? 1 : clamp((timeSeconds - this.moveStartedAt) / this.moveDuration, 0, 1);
    const eased = local * local * local * (local * (local * 6 - 15) + 10);
    for (const key of swayKeys) {
      this.current[key] = lerp(this.from[key], this.target[key], eased);
    }
    return this.toLayer(motionGain);
  }
  recenter(amount) {
    for (const key of swayKeys) {
      this.current[key] = lerp(this.current[key], 0, amount);
      this.from[key] = this.current[key];
      this.target[key] = 0;
    }
  }
  pickNextTarget(timeSeconds, profile) {
    this.from = { ...this.current };
    const bodyX = this.pickValue("bodyX", profile);
    const bodyZ = this.pickValue("bodyZ", profile);
    const headXRange = this.rangeFor("headX", profile);
    const headZRange = this.rangeFor("headZ", profile);
    this.target = {
      bodyX,
      bodyY: this.pickValue("bodyY", profile),
      bodyZ,
      headX: clamp(this.pickValue("headX", profile) + bodyX * 0.32, headXRange[0], headXRange[1]),
      headY: this.pickValue("headY", profile),
      headZ: clamp(this.pickValue("headZ", profile) + bodyZ * 0.42, headZRange[0], headZRange[1])
    };
    this.moveStartedAt = timeSeconds;
    this.moveDuration = 1.45 + this.random() * 2.35;
    this.holdUntil = timeSeconds + this.moveDuration + 0.55 + this.random() * 1.85;
  }
  pickValue(key, profile) {
    const [min, max] = this.rangeFor(key, profile);
    const centerBias = this.random() < 0.22 ? 0.38 : 1;
    const center = (min + max) / 2;
    const half = (max - min) / 2 * centerBias;
    return center - half + this.random() * half * 2;
  }
  rangeFor(key, profile) {
    const configured = profile.idleConfig[key];
    if (!configured) return defaultRanges[key];
    const center = (configured[0] + configured[1]) / 2;
    const half = (configured[1] - configured[0]) / 2 * profileRangeScale[key];
    return [center - half, center + half];
  }
  toLayer(weight) {
    return {
      bodyX: this.current.bodyX * weight,
      bodyY: this.current.bodyY * weight,
      bodyZ: this.current.bodyZ * weight,
      headX: this.current.headX * weight,
      headY: this.current.headY * weight,
      headZ: this.current.headZ * weight
    };
  }
};
var BreathingController = class {
  constructor(seed = 17) {
    __publicField(this, "phase");
    __publicField(this, "modulationPhase");
    __publicField(this, "secondaryPhase");
    const random = seededRandom(seed);
    this.phase = random() * Math.PI * 2;
    this.modulationPhase = random() * Math.PI * 2;
    this.secondaryPhase = random() * Math.PI * 2;
  }
  update(timeSeconds, options = {}) {
    const rate = clamp(options.rate ?? 1, 0.5, 1.8);
    const variance = clamp(options.variance ?? 0.42, 0, 1);
    const modulation = Math.sin(timeSeconds * 0.19 * rate + this.modulationPhase) * variance;
    const cycle = timeSeconds * 1.65 * rate + this.phase + modulation * 0.72;
    const secondary = Math.sin(timeSeconds * 0.73 * rate + this.secondaryPhase) * variance;
    const breath = clamp(0.5 + Math.sin(cycle) * 0.31 + secondary * 0.045, 0.08, 0.92);
    const bodyY = Math.sin(cycle - 0.3) * 0.022 + secondary * 4e-3;
    return {
      breath,
      bodyY
    };
  }
};
var GazeController = class {
  constructor(seed = 13, stability = 0.72) {
    __publicField(this, "random");
    __publicField(this, "fromX", 0);
    __publicField(this, "fromY", 0);
    __publicField(this, "currentX", 0);
    __publicField(this, "currentY", 0);
    __publicField(this, "targetX", 0);
    __publicField(this, "targetY", 0);
    __publicField(this, "moveStartedAt", 0);
    __publicField(this, "moveDuration", 0.8);
    __publicField(this, "holdUntil", 0);
    __publicField(this, "stability");
    this.random = seededRandom(seed);
    this.stability = clamp(stability, 0, 1);
  }
  update(timeSeconds, focusLevel, config) {
    if (focusLevel > 0.5) {
      const t = Math.min(1, focusLevel);
      this.currentX = lerp(this.currentX, 0, 0.06 + t * 0.08);
      this.currentY = lerp(this.currentY, 0, 0.06 + t * 0.08);
      return { gazeX: this.currentX, gazeY: this.currentY };
    }
    if (timeSeconds >= this.holdUntil) {
      this.pickNextTarget(timeSeconds, config);
    }
    const local = this.moveDuration <= 0 ? 1 : clamp((timeSeconds - this.moveStartedAt) / this.moveDuration, 0, 1);
    const eased = local < 0.5 ? 2 * local * local : 1 - Math.pow(-2 * local + 2, 2) / 2;
    this.currentX = lerp(this.fromX, this.targetX, eased);
    this.currentY = lerp(this.fromY, this.targetY, eased);
    return {
      gazeX: this.currentX,
      gazeY: this.currentY
    };
  }
  pickNextTarget(timeSeconds, config) {
    const xRange = config.gazeX ?? [-0.1, 0.1];
    const yRange = config.gazeY ?? [-0.05, 0.07];
    const rangeScale = 1.12 - this.stability * 0.54;
    this.fromX = this.currentX;
    this.fromY = this.currentY;
    this.targetX = this.pickScaledTarget(xRange, rangeScale);
    this.targetY = this.pickScaledTarget(yRange, rangeScale);
    this.moveStartedAt = timeSeconds;
    this.moveDuration = 0.55 + this.stability * 0.5 + this.random() * (0.9 + this.stability * 0.62);
    this.holdUntil = timeSeconds + this.moveDuration + 0.8 + this.stability * 1.25 + this.random() * (1.7 + this.stability * 1.8);
  }
  pickScaledTarget(range, scale) {
    const center = (range[0] + range[1]) / 2;
    const half = (range[1] - range[0]) / 2 * scale;
    return center - half + this.random() * half * 2;
  }
};
var IdleBiasController = class {
  constructor() {
    __publicField(this, "bias", {});
    __publicField(this, "startedAt", 0);
    __publicField(this, "duration", 0);
  }
  setBias(bias, duration, timeSeconds) {
    this.bias = { ...bias };
    this.duration = Math.max(0.1, duration);
    this.startedAt = timeSeconds;
  }
  reset() {
    this.bias = {};
    this.duration = 0;
    this.startedAt = 0;
  }
  update(timeSeconds) {
    if (this.duration <= 0) return {};
    const progress = Math.min(1, (timeSeconds - this.startedAt) / this.duration);
    const residue = Math.pow(1 - progress, 0.82);
    if (progress >= 1) {
      this.reset();
      return {};
    }
    return scaleFACS(this.bias, residue);
  }
};
var MicroMotionController = class {
  constructor(seed = 23) {
    __publicField(this, "phases");
    __publicField(this, "rates");
    const random = seededRandom(seed);
    this.phases = Array.from({ length: 8 }, () => random() * Math.PI * 2);
    this.rates = Array.from({ length: 8 }, () => 0.86 + random() * 0.28);
  }
  update(timeSeconds, focusLevel, gain = 1) {
    const damp = (1 - Math.min(1, focusLevel) * 0.65) * clamp(gain, 0, 2);
    const wave = (index, frequency, secondaryFrequency) => Math.sin(timeSeconds * frequency * this.rates[index] + this.phases[index]) * 0.72 + Math.sin(timeSeconds * secondaryFrequency * this.rates[index + 4] + this.phases[index + 4]) * 0.28;
    return {
      headX: wave(0, 0.38, 0.17) * 0.02 * damp,
      headY: wave(1, 0.31, 0.13) * 0.016 * damp,
      headZ: wave(2, 0.24, 0.11) * 0.014 * damp,
      mouthSmile: 0.045 + wave(3, 0.24, 0.09) * 0.018 * damp,
      browInnerUp: Math.max(0, wave(0, 0.18, 0.07) * 0.025 * damp)
    };
  }
};
var motionStylePresets = {
  natural: {
    spontaneity: 1,
    gestureFrequency: 1,
    gazeStability: 0.72,
    blinkRate: 1,
    breathRate: 1,
    breathVariance: 0.42,
    microMotionGain: 1,
    idleActionGain: 1,
    avoidRepeatWindow: 3,
    speechAccentGain: 1
  },
  lively: {
    spontaneity: 1.32,
    gestureFrequency: 1.3,
    gazeStability: 0.5,
    blinkRate: 1.12,
    breathRate: 1.06,
    breathVariance: 0.58,
    microMotionGain: 1.16,
    idleActionGain: 1.12,
    avoidRepeatWindow: 4,
    speechAccentGain: 1.12
  },
  calm: {
    spontaneity: 0.68,
    gestureFrequency: 0.76,
    gazeStability: 0.86,
    blinkRate: 0.84,
    breathRate: 0.82,
    breathVariance: 0.28,
    microMotionGain: 0.72,
    idleActionGain: 0.8,
    avoidRepeatWindow: 4,
    speechAccentGain: 0.72
  },
  shy: {
    spontaneity: 0.92,
    gestureFrequency: 0.9,
    gazeStability: 0.56,
    blinkRate: 1.16,
    breathRate: 0.96,
    breathVariance: 0.52,
    microMotionGain: 0.9,
    idleActionGain: 0.88,
    avoidRepeatWindow: 4,
    speechAccentGain: 0.86
  }
};
function resolveMotionStyle(options = {}, fallbackGazeStability = 0.72, fallbackSeed = createMotionSeed()) {
  return {
    seed: normalizeSeed(options.seed ?? fallbackSeed),
    spontaneity: clamp(options.spontaneity ?? 1, 0, 2),
    gestureFrequency: clamp(options.gestureFrequency ?? 1, 0, 2.5),
    gazeStability: clamp(options.gazeStability ?? fallbackGazeStability, 0, 1),
    blinkRate: clamp(options.blinkRate ?? 1, 0.25, 2.5),
    breathRate: clamp(options.breathRate ?? 1, 0.5, 1.8),
    breathVariance: clamp(options.breathVariance ?? 0.42, 0, 1),
    microMotionGain: clamp(options.microMotionGain ?? 1, 0, 2),
    idleActionGain: clamp(options.idleActionGain ?? 1, 0, 2),
    avoidRepeatWindow: Math.round(clamp(options.avoidRepeatWindow ?? 3, 0, 8)),
    speechAccentGain: clamp(options.speechAccentGain ?? 1, 0, 2)
  };
}
function createMotionSeed() {
  const time = Date.now() >>> 0;
  const random = Math.floor(Math.random() * 4294967295) >>> 0;
  return normalizeSeed(time ^ random);
}
function deriveMotionSeed(seed, channel) {
  let value = (normalizeSeed(seed) ^ Math.imul(channel + 1, 2654435761)) >>> 0;
  value ^= value >>> 16;
  value = Math.imul(value, 2246822507) >>> 0;
  value ^= value >>> 13;
  value = Math.imul(value, 3266489909) >>> 0;
  value ^= value >>> 16;
  return normalizeSeed(value);
}
function normalizeSeed(seed) {
  if (!Number.isFinite(seed)) return 1;
  return Math.abs(Math.floor(seed)) >>> 0 || 1;
}
var IdleEngine = class {
  constructor(style = {}) {
    __publicField(this, "blink");
    __publicField(this, "gaze");
    __publicField(this, "breathing");
    __publicField(this, "microMotion");
    __publicField(this, "bodySway");
    __publicField(this, "bias", new IdleBiasController());
    __publicField(this, "style");
    this.style = {
      seed: style.seed ?? 1,
      gazeStability: style.gazeStability ?? 0.72,
      blinkRate: style.blinkRate ?? 1,
      breathRate: style.breathRate ?? 1,
      breathVariance: style.breathVariance ?? 0.42,
      microMotionGain: style.microMotionGain ?? 1
    };
    this.blink = new BlinkController(deriveMotionSeed(this.style.seed, 1), this.style.blinkRate);
    this.gaze = new GazeController(deriveMotionSeed(this.style.seed, 2), this.style.gazeStability);
    this.breathing = new BreathingController(deriveMotionSeed(this.style.seed, 3));
    this.microMotion = new MicroMotionController(deriveMotionSeed(this.style.seed, 4));
    this.bodySway = new BodySwayController(deriveMotionSeed(this.style.seed, 5));
  }
  setBias(bias, duration, timeSeconds) {
    this.bias.setBias(bias, duration, timeSeconds);
  }
  deferBlink(timeSeconds, duration) {
    this.blink.defer(timeSeconds, duration);
  }
  resetBias() {
    this.bias.reset();
  }
  reset() {
    this.bias.reset();
    this.blink = new BlinkController(deriveMotionSeed(this.style.seed, 1), this.style.blinkRate);
    this.gaze = new GazeController(deriveMotionSeed(this.style.seed, 2), this.style.gazeStability);
    this.breathing = new BreathingController(deriveMotionSeed(this.style.seed, 3));
    this.microMotion = new MicroMotionController(deriveMotionSeed(this.style.seed, 4));
    this.bodySway = new BodySwayController(deriveMotionSeed(this.style.seed, 5));
  }
  update(timeSeconds, options) {
    if (!options.enabled) {
      return this.bias.update(timeSeconds);
    }
    const focusLevel = options.focusLevel;
    let result = {};
    result = addFACS(result, this.breathing.update(timeSeconds, {
      rate: this.style.breathRate,
      variance: this.style.breathVariance
    }));
    result = addFACS(result, this.microMotion.update(timeSeconds, focusLevel, this.style.microMotionGain));
    result = addFACS(result, this.bodySway.update(timeSeconds, focusLevel, options.profile, options.bodyMotionGain ?? 1));
    result = addFACS(result, this.gaze.update(timeSeconds, focusLevel, options.profile.idleConfig));
    result = addFACS(result, this.blink.update(timeSeconds, focusLevel));
    result = addFACS(result, this.bias.update(timeSeconds));
    return result;
  }
};
var defaultPersonality2 = {
  expressiveness: 0.85,
  softness: 0.65,
  shyness: 0.55,
  gazeStability: 0.7
};
var actionTemplates = [
  {
    label: "small-nod",
    duration: [0.82, 1.2],
    directional: false,
    isAvailable: (capabilities) => capabilities.headControl || capabilities.bodyControl
  },
  {
    label: "head-tilt",
    duration: [1.35, 2.15],
    directional: true,
    isAvailable: (capabilities) => capabilities.headControl || capabilities.gazeControl
  },
  {
    label: "side-look",
    duration: [1.45, 2.35],
    directional: true,
    isAvailable: (capabilities) => capabilities.gazeControl || capabilities.headControl
  },
  {
    label: "weight-shift",
    duration: [1.65, 2.65],
    directional: true,
    isAvailable: (capabilities) => capabilities.bodyControl || capabilities.headControl
  },
  {
    label: "gentle-lean",
    duration: [1.25, 2.05],
    directional: true,
    isAvailable: (capabilities) => capabilities.bodyControl || capabilities.headControl
  },
  {
    label: "sigh-sink",
    duration: [1.7, 2.8],
    directional: false,
    isAvailable: (capabilities) => capabilities.bodyControl || capabilities.headControl || capabilities.gazeControl || capabilities.browControl || capabilities.eyeBlink
  },
  {
    label: "slow-blink",
    duration: [0.72, 1.08],
    directional: true,
    isAvailable: (capabilities) => capabilities.eyeBlink
  }
];
var IdleActionScheduler = class {
  constructor(options) {
    __publicField(this, "seed");
    __publicField(this, "spontaneity");
    __publicField(this, "gain");
    __publicField(this, "minIntervalSeconds");
    __publicField(this, "maxIntervalSeconds");
    __publicField(this, "recentWindowSize");
    __publicField(this, "random");
    __publicField(this, "active", null);
    __publicField(this, "nextActionAt", null);
    __publicField(this, "recentActions", []);
    __publicField(this, "recentDirections", []);
    __publicField(this, "lastUpdateAt", 0);
    __publicField(this, "suppressed", false);
    this.seed = finiteOr(options.seed, 1);
    this.spontaneity = clamp(finiteOr(options.spontaneity, 0.68), 0, 1);
    this.gain = clamp(finiteOr(options.gain, 1), 0, 2.5);
    this.minIntervalSeconds = clamp(finiteOr(options.minIntervalSeconds, 4.8), 0.25, 120);
    this.maxIntervalSeconds = clamp(
      finiteOr(options.maxIntervalSeconds, 11.5),
      this.minIntervalSeconds,
      180
    );
    this.recentWindowSize = Math.floor(clamp(finiteOr(options.recentWindowSize, 3), 0, 6));
    this.random = seededRandom(this.seed);
  }
  update(timeSeconds, context) {
    const time = Math.max(0, finiteOr(timeSeconds, this.lastUpdateAt));
    if (time < this.lastUpdateAt) this.reset(time);
    this.lastUpdateAt = time;
    if (!context.enabled || context.suppressed || this.spontaneity <= 0 || this.gain <= 0) {
      this.active = null;
      this.nextActionAt = null;
      this.suppressed = true;
      return {};
    }
    const focusLevel = clamp(finiteOr(context.focusLevel, 0), 0, 1);
    if (this.suppressed || this.nextActionAt === null) {
      this.suppressed = false;
      this.nextActionAt = time + this.sampleInterval(focusLevel);
      return {};
    }
    if (this.active) {
      const elapsed = time - this.active.startedAt;
      if (elapsed < this.active.duration) return evaluateAction(this.active, elapsed);
      this.active = null;
    }
    if (time < this.nextActionAt) return {};
    const action = this.createAction(time, context, focusLevel);
    if (!action) {
      this.nextActionAt = time + this.sampleInterval(focusLevel);
      return {};
    }
    this.active = action;
    this.remember(action.label, action.direction);
    this.nextActionAt = time + action.duration + this.sampleInterval(focusLevel);
    return evaluateAction(action, 0);
  }
  interrupt(timeSeconds = this.lastUpdateAt) {
    const time = Math.max(0, finiteOr(timeSeconds, this.lastUpdateAt));
    this.active = null;
    this.lastUpdateAt = time;
    this.nextActionAt = time + this.sampleInterval(0);
  }
  reset(timeSeconds = 0) {
    this.random = seededRandom(this.seed);
    this.active = null;
    this.nextActionAt = null;
    this.recentActions = [];
    this.recentDirections = [];
    this.lastUpdateAt = Math.max(0, finiteOr(timeSeconds, 0));
    this.suppressed = false;
  }
  getState() {
    return {
      activeAction: this.active?.label ?? null,
      direction: this.active?.direction ?? 0,
      startedAt: this.active?.startedAt ?? null,
      duration: this.active?.duration ?? 0,
      nextActionAt: this.nextActionAt,
      recentActions: [...this.recentActions],
      recentDirections: [...this.recentDirections],
      suppressed: this.suppressed
    };
  }
  createAction(timeSeconds, context, focusLevel) {
    const capabilities = context.profile.capabilities ?? withConservativeFallback(detectCapabilities(context.profile));
    const vad = resolveVAD(context.vad);
    const personality = resolvePersonality(context.personality);
    const available = actionTemplates.filter((template2) => template2.isAvailable(capabilities));
    if (available.length === 0) return null;
    const unrepeated = this.recentWindowSize > 0 ? available.filter((template2) => !this.recentActions.includes(template2.label)) : available;
    const candidates = unrepeated.length > 0 ? unrepeated : available.filter((template2) => template2.label !== this.recentActions.at(-1));
    const pool = candidates.length > 0 ? candidates : available;
    const template = weightedPick(
      pool,
      (candidate) => actionWeight(candidate.label, vad, personality, focusLevel),
      this.random
    );
    const direction = template.directional ? this.pickDirection() : 0;
    const duration = template.duration[0] + (template.duration[1] - template.duration[0]) * this.random();
    const vadIntensity = (Math.abs(vad.valence) + Math.abs(vad.arousal) * 0.82 + Math.abs(vad.dominance) * 0.64) / 2.46;
    const amplitude = clamp(
      this.gain * (0.72 + personality.expressiveness * 0.4) * (1 - focusLevel * 0.38) * (0.9 + this.spontaneity * 0.14) * (0.9 + vadIntensity * 0.18) * (0.86 + this.random() * 0.28),
      0,
      2.2
    );
    return {
      label: template.label,
      direction,
      startedAt: timeSeconds,
      duration,
      keyframes: buildKeyframes(template.label, direction, amplitude, capabilities)
    };
  }
  pickDirection() {
    let direction = this.random() < 0.5 ? -1 : 1;
    const lastDirection = this.recentDirections.at(-1);
    if (this.recentWindowSize > 0 && direction === lastDirection) direction = direction === -1 ? 1 : -1;
    return direction;
  }
  remember(label, direction) {
    if (this.recentWindowSize <= 0) return;
    this.recentActions.push(label);
    if (this.recentActions.length > this.recentWindowSize) this.recentActions.shift();
    if (direction !== 0) {
      this.recentDirections.push(direction);
      if (this.recentDirections.length > this.recentWindowSize) this.recentDirections.shift();
    }
  }
  sampleInterval(focusLevel) {
    const curve = clamp(0.68 + this.spontaneity * 1.7 - focusLevel * 0.32, 0.42, 2.38);
    const randomPosition = Math.pow(this.random(), curve);
    const focusAdjusted = randomPosition + (1 - randomPosition) * focusLevel * 0.34;
    return this.minIntervalSeconds + (this.maxIntervalSeconds - this.minIntervalSeconds) * focusAdjusted;
  }
};
function resolveVAD(input) {
  const source = "current" in input ? input.current : input;
  return {
    valence: clamp(finiteOr(source.valence, 0), -1, 1),
    arousal: clamp(finiteOr(source.arousal, 0), -1, 1),
    dominance: clamp(finiteOr(source.dominance, 0), -1, 1)
  };
}
function resolvePersonality(input) {
  return {
    expressiveness: clamp(finiteOr(input?.expressiveness, defaultPersonality2.expressiveness), 0, 1),
    softness: clamp(finiteOr(input?.softness, defaultPersonality2.softness), 0, 1),
    shyness: clamp(finiteOr(input?.shyness, defaultPersonality2.shyness), 0, 1),
    gazeStability: clamp(finiteOr(input?.gazeStability, defaultPersonality2.gazeStability), 0, 1)
  };
}
function actionWeight(label, vad, personality, focusLevel) {
  const positive = Math.max(0, vad.valence);
  const negative = Math.max(0, -vad.valence);
  const aroused = Math.max(0, vad.arousal);
  const calm = Math.max(0, -vad.arousal);
  const dominant = Math.max(0, vad.dominance);
  const submissive = Math.max(0, -vad.dominance);
  if (label === "small-nod") {
    return 1.05 + positive * 0.42 + aroused * 0.4 + focusLevel * 0.42 + personality.expressiveness * 0.28;
  }
  if (label === "head-tilt") {
    return 0.92 + positive * 0.18 + submissive * 0.24 + personality.softness * 0.34 + personality.shyness * 0.16;
  }
  if (label === "side-look") {
    return 0.62 + negative * 0.28 + submissive * 0.36 + personality.shyness * 0.56 + (1 - personality.gazeStability) * 0.6;
  }
  if (label === "weight-shift") {
    return 0.86 + aroused * 0.24 + dominant * 0.34 + personality.expressiveness * 0.34;
  }
  if (label === "gentle-lean") {
    return 0.76 + positive * 0.34 + dominant * 0.28 + focusLevel * 0.18 + personality.expressiveness * 0.32 - personality.shyness * 0.12;
  }
  if (label === "sigh-sink") {
    return 0.48 + negative * 0.62 + calm * 0.52 + personality.softness * 0.32;
  }
  return 0.72 + calm * 0.56 + personality.softness * 0.38 + focusLevel * 0.12;
}
function weightedPick(templates, getWeight, random) {
  const weights = templates.map((template) => Math.max(1e-3, getWeight(template)));
  const total = weights.reduce((sum, weight) => sum + weight, 0);
  let cursor = random() * total;
  for (let index = 0; index < templates.length; index += 1) {
    cursor -= weights[index];
    if (cursor <= 0) return templates[index];
  }
  return templates[templates.length - 1];
}
function buildKeyframes(label, direction, amplitude, capabilities) {
  const side = direction === 0 ? 1 : direction;
  let frames;
  if (label === "small-nod") {
    frames = [
      frame(0, {}),
      frame(0.2, { headY: 0.086, bodyY: 0.018, gazeY: 0.012 }),
      frame(0.42, { headY: -0.026, bodyY: -6e-3, gazeY: -8e-3 }),
      frame(0.68, { headY: 0.016, bodyY: 4e-3 }),
      frame(1, {})
    ];
  } else if (label === "head-tilt") {
    frames = [
      frame(0, {}),
      frame(0.28, {
        headX: side * 0.018,
        headZ: side * 0.094,
        gazeX: -side * 0.038,
        browOuterUp: 0.024
      }),
      frame(0.64, {
        headX: side * 0.014,
        headZ: side * 0.078,
        gazeX: -side * 0.025,
        browOuterUp: 0.016
      }),
      frame(1, {})
    ];
  } else if (label === "side-look") {
    frames = [
      frame(0, {}),
      frame(0.18, { gazeX: side * 0.18, gazeY: 0.018 }),
      frame(0.38, {
        gazeX: side * 0.23,
        gazeY: 0.012,
        headX: side * 0.046,
        headZ: -side * 0.026
      }),
      frame(0.62, {
        gazeX: side * 0.2,
        headX: side * 0.04,
        headZ: -side * 0.022
      }),
      frame(0.8, { gazeX: side * 0.028, headX: side * 0.034, headZ: -side * 0.018 }),
      frame(1, {})
    ];
  } else if (label === "weight-shift") {
    frames = [
      frame(0, {}),
      frame(0.34, {
        bodyX: side * 0.078,
        bodyZ: side * 0.055,
        headX: -side * 0.018,
        headZ: -side * 0.036,
        gazeX: -side * 0.026
      }),
      frame(0.7, {
        bodyX: side * 0.066,
        bodyZ: side * 0.046,
        headX: -side * 0.014,
        headZ: -side * 0.03,
        gazeX: -side * 0.018
      }),
      frame(1, {})
    ];
  } else if (label === "gentle-lean") {
    frames = [
      frame(0, {}),
      frame(0.3, {
        bodyY: side * 0.074,
        headY: side * 0.044,
        gazeY: side * 0.022,
        browOuterUp: side > 0 ? 0.018 : 0
      }),
      frame(0.58, {
        bodyY: side * 0.064,
        headY: side * 0.038,
        gazeY: side * 0.018,
        browOuterUp: side > 0 ? 0.012 : 0
      }),
      frame(0.8, { bodyY: -side * 0.012, headY: -side * 8e-3 }),
      frame(1, {})
    ];
  } else if (label === "sigh-sink") {
    frames = [
      frame(0, {}),
      frame(0.2, { browInnerUp: 0.018, eyeBlinkL: 0.08, eyeBlinkR: 0.09 }),
      frame(0.48, {
        headY: -0.064,
        bodyY: -0.054,
        gazeY: -0.048,
        browInnerUp: 0.026,
        eyeBlinkL: 0.2,
        eyeBlinkR: 0.22
      }),
      frame(0.73, {
        headY: -0.048,
        bodyY: -0.042,
        gazeY: -0.034,
        browInnerUp: 0.018,
        eyeBlinkL: 0.06,
        eyeBlinkR: 0.07
      }),
      frame(1, {})
    ];
  } else {
    const leftPeak = side < 0 ? 0.94 : 0.82;
    const rightPeak = side > 0 ? 0.94 : 0.82;
    frames = [
      frame(0, {}),
      frame(0.3, { eyeBlinkL: leftPeak * 0.86, eyeBlinkR: rightPeak * 0.82, headY: -0.01 }),
      frame(0.47, { eyeBlinkL: leftPeak, eyeBlinkR: rightPeak, headY: -0.014 }),
      frame(0.72, { eyeBlinkL: 0.2, eyeBlinkR: 0.18, headY: -6e-3 }),
      frame(1, {})
    ];
  }
  return frames.map((keyframe) => ({
    progress: keyframe.progress,
    pose: scaleAndFilterPose(keyframe.pose, amplitude, capabilities)
  }));
}
function frame(progress, pose) {
  return { progress, pose };
}
function scaleAndFilterPose(pose, scale, capabilities) {
  const result = {};
  for (const key of Object.keys(pose)) {
    const value = pose[key];
    if (typeof value !== "number" || !supportsKey(key, capabilities)) continue;
    result[key] = value * scale;
  }
  return clampFACSState(result);
}
function supportsKey(key, capabilities) {
  if (key === "headX" || key === "headY" || key === "headZ") return capabilities.headControl;
  if (key === "bodyX" || key === "bodyY" || key === "bodyZ") return capabilities.bodyControl;
  if (key === "gazeX" || key === "gazeY") return capabilities.gazeControl;
  if (key === "eyeBlinkL" || key === "eyeBlinkR") return capabilities.eyeBlink;
  if (key === "eyeSmile") return capabilities.eyeSmile;
  if (key === "browInnerUp" || key === "browOuterUp" || key === "browDown") {
    return capabilities.browControl;
  }
  if (key === "mouthOpen" || key === "mouthPucker") return capabilities.mouthOpen;
  if (key === "mouthSmile" || key === "mouthFrown") return capabilities.mouthSmile;
  if (key === "blush") return capabilities.blush;
  if (key === "tear") return capabilities.tear;
  if (key === "sweat") return capabilities.sweat;
  if (key === "breath") return capabilities.breath;
  return true;
}
function evaluateAction(action, elapsedSeconds) {
  const progress = clamp(elapsedSeconds / action.duration, 0, 1);
  let from = action.keyframes[0];
  let to = action.keyframes[action.keyframes.length - 1];
  for (let index = 1; index < action.keyframes.length; index += 1) {
    const candidate = action.keyframes[index];
    if (progress <= candidate.progress) {
      to = candidate;
      from = action.keyframes[index - 1];
      break;
    }
  }
  const span = to.progress - from.progress;
  const local = span <= 0 ? 1 : clamp((progress - from.progress) / span, 0, 1);
  const eased = local * local * (3 - 2 * local);
  const keys = /* @__PURE__ */ new Set([
    ...Object.keys(from.pose),
    ...Object.keys(to.pose)
  ]);
  const result = {};
  for (const key of keys) {
    const start2 = from.pose[key] ?? 0;
    const end = to.pose[key] ?? 0;
    result[key] = start2 + (end - start2) * eased;
  }
  return clampFACSState(result);
}
function finiteOr(value, fallback) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}
function withConservativeFallback(capabilities) {
  if (Object.values(capabilities).some(Boolean)) return capabilities;
  return {
    ...capabilities,
    headControl: true,
    bodyControl: true,
    eyeBlink: true,
    gazeControl: true,
    browControl: true
  };
}
function envelope(progress) {
  const t = clamp01(progress);
  return Math.sin(Math.PI * t);
}
var ActionPlanSequencer = class {
  constructor() {
    __publicField(this, "beats", []);
    __publicField(this, "startedAt", 0);
    __publicField(this, "actionUnitSolver", new ActionUnitSolver());
  }
  start(beats, timeSeconds) {
    this.beats = (beats ?? []).filter((beat) => beat.duration > 0 && beat.intensity > 0).slice(0, 12).sort((a, b) => a.time - b.time);
    this.startedAt = timeSeconds;
  }
  reset() {
    this.beats = [];
    this.startedAt = 0;
  }
  get beatCount() {
    return this.beats.length;
  }
  get duration() {
    return this.beats.reduce((max, beat) => Math.max(max, beat.time + beat.duration), 0);
  }
  isComplete(timeSeconds) {
    return this.beats.length === 0 || Math.max(0, timeSeconds - this.startedAt) >= this.duration;
  }
  evaluate(timeSeconds) {
    if (this.beats.length === 0) return {};
    const elapsed = Math.max(0, timeSeconds - this.startedAt);
    let result = {};
    for (const beat of this.beats) {
      const local = (elapsed - beat.time) / beat.duration;
      if (local < 0 || local > 1) continue;
      const weight = envelope(local) * clamp01(beat.intensity);
      let layer = {};
      if (beat.facs) {
        layer = addFACS(layer, scaleFACSFromNeutral(beat.facs, weight));
      }
      if (beat.actionUnits && Object.keys(beat.actionUnits).length > 0) {
        layer = addFACS(layer, scaleFACSFromNeutral(this.actionUnitSolver.solvePartial(beat.actionUnits), weight));
      }
      result = addFACS(result, layer);
    }
    return clampFACSState(result);
  }
};
var ParameterPlanSequencer = class {
  constructor() {
    __publicField(this, "beats", []);
    __publicField(this, "startedAt", 0);
    __publicField(this, "lastActiveSignature", "");
  }
  start(beats, timeSeconds) {
    this.beats = (beats ?? []).filter((beat) => beat.duration > 0 && Object.keys(beat.parameters ?? {}).length > 0).slice(0, 24).sort((a, b) => a.time - b.time);
    this.startedAt = timeSeconds;
    this.lastActiveSignature = "";
    console.info("[SpeakingMotion] sequencer start", {
      beatCount: this.beats.length,
      startedAt: timeSeconds,
      beats: this.beats.map((beat, index) => ({
        index,
        time: beat.time,
        duration: beat.duration,
        label: beat.label,
        parameterIds: Object.keys(beat.parameters)
      }))
    });
  }
  reset() {
    if (this.beats.length > 0) {
      console.info("[SpeakingMotion] sequencer reset", {
        beatCount: this.beats.length
      });
    }
    this.beats = [];
    this.startedAt = 0;
    this.lastActiveSignature = "";
  }
  get beatCount() {
    return this.beats.length;
  }
  evaluate(timeSeconds) {
    if (this.beats.length === 0) return {};
    const elapsed = Math.max(0, timeSeconds - this.startedAt);
    let previousParameters = {};
    for (const [index, beat] of this.beats.entries()) {
      if (elapsed < beat.time) {
        const activeLabels = Object.keys(previousParameters).length ? [`hold-before-${index}:${beat.label ?? "beat"}`] : [];
        this.logActiveBeatChange(elapsed, activeLabels, previousParameters);
        return previousParameters;
      }
      const transitionEnd = beat.time + beat.duration;
      if (elapsed <= transitionEnd) {
        const progress = beat.duration <= 0 ? 1 : (elapsed - beat.time) / beat.duration;
        const easedProgress = ease("easeInOut", progress);
        const result = interpolateParameters(previousParameters, beat.parameters, easedProgress);
        this.logActiveBeatChange(elapsed, [`transition-${index}:${beat.label ?? "beat"}`], result);
        return result;
      }
      previousParameters = beat.parameters;
    }
    const lastBeat = this.beats[this.beats.length - 1];
    this.logActiveBeatChange(elapsed, [`hold-last:${lastBeat?.label ?? "beat"}`], previousParameters);
    return previousParameters;
  }
  logActiveBeatChange(elapsed, activeLabels, parameters) {
    const activeSignature = activeLabels.join("|");
    if (activeSignature === this.lastActiveSignature) return;
    this.lastActiveSignature = activeSignature;
    if (!activeSignature) {
      console.info("[SpeakingMotion] overlay inactive", {
        elapsed
      });
      return;
    }
    console.info("[SpeakingMotion] overlay active", {
      elapsed,
      activeLabels,
      parameters
    });
  }
};
function interpolateParameters(from, to, progress) {
  const result = {};
  const parameterIds = /* @__PURE__ */ new Set([...Object.keys(from), ...Object.keys(to)]);
  for (const id of parameterIds) {
    const fromValue = from[id] ?? 0;
    const toValue = to[id] ?? 0;
    result[id] = lerp(fromValue, toValue, progress);
  }
  return result;
}
var MessageReactionClassifier = class {
  classify(message) {
    const text = message.trim();
    if (/(过了|成功|赢了|拿下|通过|上岸|好消息)/u.test(text)) {
      return {
        emotion: "happy",
        variant: "surprised_happy",
        intensity: 0.85,
        contextTags: ["user_good_news"],
        sourceMessage: message
      };
    }
    if (/(喜欢你|可爱|好看|夸夸|贴贴)/u.test(text)) {
      return {
        emotion: "shy",
        variant: "bashful",
        intensity: 0.8,
        contextTags: ["compliment", "warm"],
        sourceMessage: message
      };
    }
    if (/(兴奋|太爽|冲啊|炸了|激动)/u.test(text)) {
      return {
        emotion: "excited",
        variant: "sparkle",
        intensity: 0.86,
        contextTags: ["user_good_news"],
        sourceMessage: message
      };
    }
    if (/(累|难受|不开心|崩溃|压力|困|疼)/u.test(text)) {
      return {
        emotion: /(累|困|没精神)/u.test(text) ? "tired" : "concerned",
        variant: /(累|困|没精神)/u.test(text) ? "drained" : "comfort",
        intensity: 0.75,
        contextTags: ["user_tired", "warm"],
        sourceMessage: message
      };
    }
    if (/(难过|伤心|想哭|委屈|失落)/u.test(text)) {
      return {
        emotion: "sad",
        variant: "downcast",
        intensity: 0.72,
        contextTags: ["comfort"],
        sourceMessage: message
      };
    }
    if (/(焦虑|慌|害怕|紧张|不安)/u.test(text)) {
      return {
        emotion: "anxiety",
        variant: "nervous",
        intensity: 0.76,
        contextTags: ["comfort"],
        sourceMessage: message
      };
    }
    if (/(怎么|为什么|咋回事|啥|不懂|疑惑)/u.test(text)) {
      return {
        emotion: /(好奇|想知道|什么原因)/u.test(text) ? "curious" : "confused",
        variant: /(好奇|想知道|什么原因)/u.test(text) ? "tilt" : "confused",
        intensity: 0.68,
        contextTags: ["question", "curious"],
        sourceMessage: message
      };
    }
    if (/(生气|气死|讨厌|烦|离谱)/u.test(text)) {
      return {
        emotion: "anger",
        variant: "annoyed",
        intensity: 0.62,
        contextTags: ["annoyed"],
        sourceMessage: message
      };
    }
    return {
      emotion: "neutral",
      variant: "neutral_ack",
      intensity: 0.35,
      contextTags: ["normal_chat"],
      sourceMessage: message
    };
  }
};
var ReactionSequencer = class {
  constructor() {
    __publicField(this, "expression", null);
    __publicField(this, "startedAt", 0);
  }
  start(expression, timeSeconds) {
    this.expression = expression;
    this.startedAt = timeSeconds;
  }
  reset() {
    this.expression = null;
    this.startedAt = 0;
  }
  get currentExpression() {
    return this.expression;
  }
  get duration() {
    return this.expression ? getTimelineDuration(this.expression.timeline) : 0;
  }
  elapsed(timeSeconds) {
    return Math.max(0, timeSeconds - this.startedAt);
  }
  isComplete(timeSeconds) {
    return Boolean(this.expression && this.elapsed(timeSeconds) >= this.duration);
  }
  evaluate(timeSeconds) {
    if (!this.expression) return {};
    return evaluateExpressionTimeline(this.expression.timeline, this.elapsed(timeSeconds));
  }
  hold(weight = 0.86) {
    return this.expression ? scaleFACSFromNeutral(this.expression.peakFACS, weight) : {};
  }
};
var RecoveryController = class {
  constructor() {
    __publicField(this, "startedAt", 0);
    __publicField(this, "duration", 0);
    __publicField(this, "from", {});
  }
  start(from, duration, timeSeconds) {
    this.from = { ...from };
    this.duration = Math.max(0.2, duration);
    this.startedAt = timeSeconds;
  }
  reset() {
    this.from = {};
    this.duration = 0;
    this.startedAt = 0;
  }
  get active() {
    return this.duration > 0;
  }
  isComplete(timeSeconds) {
    return this.active && timeSeconds - this.startedAt >= this.duration;
  }
  update(timeSeconds) {
    if (!this.active) return {};
    const progress = Math.min(1, (timeSeconds - this.startedAt) / this.duration);
    const weight = Math.pow(1 - progress, 1.8);
    return scaleFACSFromNeutral(this.from, weight);
  }
};
var LipSyncController = class {
  constructor() {
    __publicField(this, "smoothedLevel", 0);
    __publicField(this, "previousLevel", 0);
    __publicField(this, "previousPeak", 0);
    __publicField(this, "accent", 0);
    __publicField(this, "accentDirection", 1);
    __publicField(this, "lastAccentTime", Number.NEGATIVE_INFINITY);
    __publicField(this, "lastTimeSeconds", null);
  }
  update(timeSeconds, options) {
    if (!options.enabled || !options.speaking) {
      this.reset();
      return {};
    }
    const audio = resolveAudioInput(options);
    if (audio === null) {
      this.reset();
      return this.updateProcedural(timeSeconds, options);
    }
    return this.updateMeasured(timeSeconds, options, audio.level, audio.peak);
  }
  reset() {
    this.smoothedLevel = 0;
    this.previousLevel = 0;
    this.previousPeak = 0;
    this.accent = 0;
    this.accentDirection = 1;
    this.lastAccentTime = Number.NEGATIVE_INFINITY;
    this.lastTimeSeconds = null;
  }
  updateProcedural(timeSeconds, options) {
    const syllable = Math.sin(timeSeconds * 18.5) * 0.5 + Math.sin(timeSeconds * 31.2) * 0.25 + 0.5;
    const mouthOpen = Math.max(0, syllable) * (0.18 + options.intensity * 0.34);
    return {
      mouthOpen,
      headX: Math.sin(timeSeconds * 2.6) * 0.018,
      headY: Math.sin(timeSeconds * 2.1 + 0.8) * 0.012
    };
  }
  updateMeasured(timeSeconds, options, level, peak) {
    const deltaSeconds = resolveDeltaSeconds(timeSeconds, options.deltaSeconds, this.lastTimeSeconds);
    this.lastTimeSeconds = Number.isFinite(timeSeconds) ? timeSeconds : this.lastTimeSeconds;
    const gatedLevel = level <= AUDIO_NOISE_GATE ? 0 : (level - AUDIO_NOISE_GATE) / (1 - AUDIO_NOISE_GATE);
    const attack = 1 - Math.exp(-deltaSeconds / AUDIO_ATTACK_SECONDS);
    const release = 1 - Math.exp(-deltaSeconds / AUDIO_RELEASE_SECONDS);
    const smoothing = gatedLevel >= this.smoothedLevel ? attack : release;
    this.smoothedLevel += (gatedLevel - this.smoothedLevel) * smoothing;
    this.accent *= Math.exp(-deltaSeconds / SPEECH_ACCENT_DECAY_SECONDS);
    const rise = Math.max(0, peak - Math.max(this.previousPeak, this.previousLevel));
    const accentGain = clamp(finiteOr2(options.speechAccentGain, DEFAULT_SPEECH_ACCENT_GAIN), 0, 2);
    if (accentGain > 0 && rise >= SPEECH_ACCENT_RISE_THRESHOLD && peak > AUDIO_NOISE_GATE + SPEECH_ACCENT_MIN_PEAK && timeSeconds - this.lastAccentTime >= SPEECH_ACCENT_COOLDOWN_SECONDS) {
      const pulse = clamp(0.22 + rise * 1.6, 0, 0.72) * accentGain;
      this.accent = clamp(this.accent * 0.45 + pulse, 0, 0.82);
      this.accentDirection *= -1;
      this.lastAccentTime = timeSeconds;
    }
    this.previousLevel = level;
    this.previousPeak = peak;
    const intensity = clamp(finiteOr2(options.intensity, 0), 0, 1);
    const mouthGain = 0.18 + intensity * 0.34;
    const accent = clamp(this.accent, 0, 1);
    return {
      mouthOpen: clamp(this.smoothedLevel * mouthGain, 0, 1),
      browOuterUp: clamp(accent * 0.075, 0, 1),
      headY: clamp(-accent * 0.028, -1, 1),
      headZ: clamp(this.accentDirection * accent * 0.016, -1, 1)
    };
  }
};
var AUDIO_NOISE_GATE = 0.035;
var AUDIO_ATTACK_SECONDS = 0.045;
var AUDIO_RELEASE_SECONDS = 0.13;
var SPEECH_ACCENT_RISE_THRESHOLD = 0.085;
var SPEECH_ACCENT_MIN_PEAK = 0.045;
var SPEECH_ACCENT_COOLDOWN_SECONDS = 0.18;
var SPEECH_ACCENT_DECAY_SECONDS = 0.16;
var DEFAULT_SPEECH_ACCENT_GAIN = 0.8;
function resolveAudioInput(options) {
  const level = normalizedAudioValue(options.audioLevel);
  const peak = normalizedAudioValue(options.audioPeak);
  if (level === void 0) return null;
  return {
    level,
    peak: peak ?? level ?? 0
  };
}
function normalizedAudioValue(value) {
  if (value === void 0 || !Number.isFinite(value) || value < 0) return void 0;
  return clamp(value, 0, 1);
}
function finiteOr2(value, fallback) {
  return value !== void 0 && Number.isFinite(value) ? value : fallback;
}
function resolveDeltaSeconds(timeSeconds, explicitDeltaSeconds, previousTimeSeconds) {
  if (explicitDeltaSeconds !== void 0 && Number.isFinite(explicitDeltaSeconds)) {
    return clamp(Math.max(0, explicitDeltaSeconds), 0, 0.25);
  }
  if (previousTimeSeconds !== null && Number.isFinite(timeSeconds) && timeSeconds >= previousTimeSeconds) {
    return clamp(timeSeconds - previousTimeSeconds, 0, 0.25);
  }
  return 1 / 60;
}
function estimateMockSpeechDuration(message) {
  const length = Math.max(6, message.trim().length);
  return Math.min(4.6, 1.2 + length * 0.08);
}
var baseTemplateDurationSeconds = 6;
var waitingDurationSeconds = 9;
var waitingAmplitudeScale = 0.4;
var VoiceWaitingMotionController = class {
  constructor() {
    __publicField(this, "motion", null);
  }
  start(timeSeconds, seed = Math.round(timeSeconds * 1e3), options = {}) {
    const random = seededRandom(seed);
    const side = random() < 0.5 ? -1 : 1;
    const style = createWaitingMotionStyle(options, side);
    const duration = clamp(waitingDurationSeconds + (random() - 0.5) * 0.4 - style.arousal * 0.28, 8.6, 9.4);
    const amplitude = (0.82 + random() * 0.18) * waitingAmplitudeScale * waitingAmplitudeFactor(style);
    const tempo = clamp((0.92 + random() * 0.16) * (1 - style.arousal * 0.13), 0.78, 1.24);
    const template = pickWaitingTemplate(random, style);
    this.motion = {
      label: template.label,
      startedAt: timeSeconds,
      duration,
      frames: template.build({ side, amplitude, tempo, random, style }, duration)
    };
    return {
      label: template.label,
      duration,
      amplitude,
      tempo,
      emotion: style.emotion,
      vad: {
        valence: style.valence,
        arousal: style.arousal,
        dominance: style.dominance
      }
    };
  }
  reset() {
    this.motion = null;
  }
  update(timeSeconds, bodyMotionGain = 1) {
    if (!this.motion) return {};
    const elapsed = timeSeconds - this.motion.startedAt;
    if (elapsed >= this.motion.duration) {
      this.motion = null;
      return {};
    }
    const layer = evaluateExpressionTimeline(this.motion.frames, elapsed);
    const gain = Math.max(0, Math.min(bodyMotionGain, 4));
    return clampFACSState({
      ...layer,
      headX: (layer.headX ?? 0) * gain,
      headY: (layer.headY ?? 0) * gain,
      headZ: (layer.headZ ?? 0) * gain,
      bodyX: (layer.bodyX ?? 0) * gain,
      bodyY: (layer.bodyY ?? 0) * gain,
      bodyZ: (layer.bodyZ ?? 0) * gain
    });
  }
};
var waitingTemplates = [
  {
    label: "slow-sway",
    build: buildSlowSwayFrames,
    weight: (style) => 1.15 + Math.max(-style.arousal, 0) * 0.55 + Math.max(style.valence, 0) * 0.28
  },
  {
    label: "figure-eight",
    build: buildFigureEightFrames,
    weight: (style) => 0.75 + Math.max(style.arousal, 0) * 0.38 + Math.max(style.dominance, 0) * 0.24
  },
  {
    label: "curious-lean",
    build: buildCuriousLeanFrames,
    weight: (style) => 0.52 + emotionWeight(style, ["curious", "confused", "surprised"], 2.25) + Math.max(style.arousal, 0) * 0.16
  },
  {
    label: "shy-rock",
    build: buildShyRockFrames,
    weight: (style) => 0.54 + emotionWeight(style, ["shy", "affectionate"], 2.2) + Math.max(-style.dominance, 0) * 0.72
  },
  {
    label: "buoyant-bob",
    build: buildBuoyantBobFrames,
    weight: (style) => 0.52 + emotionWeight(style, ["happy", "excited"], 2.2) + Math.max(style.valence, 0) * 0.74
  },
  {
    label: "soft-settle",
    build: buildSoftSettleFrames,
    weight: (style) => 0.44 + emotionWeight(style, ["sad", "tired", "concerned", "calm"], 1.9) + Math.max(-style.valence, 0) * 0.82 + Math.max(-style.arousal, 0) * 0.55
  },
  {
    label: "contained-tension",
    build: buildContainedTensionFrames,
    weight: (style) => 0.34 + emotionWeight(style, ["anxiety", "anger", "angry"], 2.15) + Math.max(style.arousal, 0) * 0.58 + Math.max(-style.valence, 0) * 0.45
  }
];
function pickWaitingTemplate(random, style) {
  const weighted = waitingTemplates.map((template) => ({
    template,
    weight: Math.max(0.05, template.weight(style))
  }));
  const total = weighted.reduce((sum, item) => sum + item.weight, 0);
  let roll = random() * total;
  for (const item of weighted) {
    roll -= item.weight;
    if (roll <= 0) return item.template;
  }
  return waitingTemplates[0];
}
function createWaitingMotionStyle(options, side) {
  const vad = normalizeVAD(options.vad);
  const emotion = normalizeEmotion2(options.emotion);
  const intensity = clamp(options.intensity ?? estimateVADIntensity(vad), 0, 1);
  const positive = Math.max(vad.valence, 0);
  const negative = Math.max(-vad.valence, 0);
  const highArousal = Math.max(vad.arousal, 0);
  const lowArousal = Math.max(-vad.arousal, 0);
  const confident = Math.max(vad.dominance, 0);
  const withdrawn = Math.max(-vad.dominance, 0);
  const shy = isEmotion(emotion, ["shy", "affectionate"]);
  const anxious = isEmotion(emotion, ["anxiety"]) || negative > 0.32 && highArousal > 0.34;
  const angry = isEmotion(emotion, ["anger", "angry"]) || negative > 0.38 && highArousal > 0.38 && confident > 0.12;
  const curious = isEmotion(emotion, ["curious", "confused", "surprised"]);
  return {
    emotion,
    valence: vad.valence,
    arousal: vad.arousal,
    dominance: vad.dominance,
    intensity,
    postureBias: clampFACSState({
      headY: positive * 0.024 - negative * 0.036 + highArousal * 0.012 - lowArousal * 8e-3,
      headZ: side * (withdrawn * 0.036 + (shy ? 0.032 : 0) - confident * 0.014),
      bodyY: positive * 0.026 - negative * 0.03 - lowArousal * 8e-3,
      bodyZ: side * (withdrawn * 0.026 + (shy ? 0.016 : 0) - confident * 0.012),
      gazeX: side * (withdrawn * 0.036 + (shy ? 0.026 : 0) - confident * 0.01),
      gazeY: positive * 0.016 - negative * 0.05 + highArousal * 0.012,
      eyeSmile: positive * 0.06 + (shy ? 0.04 : 0),
      eyeSquint: angry ? 0.036 + intensity * 0.018 : 0,
      browOuterUp: highArousal * 0.034 + (curious ? 0.046 : 0),
      browInnerUp: negative * 0.052 + withdrawn * 0.034 + (anxious ? 0.048 : 0),
      browDown: angry ? 0.048 + intensity * 0.028 : 0,
      mouthSmile: positive * 0.06 + (shy ? 0.034 : 0),
      mouthFrown: negative * 0.044,
      blush: shy ? 0.066 + positive * 0.028 : 0,
      sweat: anxious ? 0.046 + highArousal * 0.026 : 0
    })
  };
}
function normalizeVAD(vad) {
  return {
    valence: clamp(vad?.valence ?? 0, -1, 1),
    arousal: clamp(vad?.arousal ?? 0, -1, 1),
    dominance: clamp(vad?.dominance ?? 0, -1, 1)
  };
}
function estimateVADIntensity(vad) {
  return clamp((Math.abs(vad.valence) + Math.abs(vad.arousal) * 0.9 + Math.abs(vad.dominance) * 0.7) / 2.6, 0, 1);
}
function waitingAmplitudeFactor(style) {
  const highArousal = Math.max(style.arousal, 0);
  const lowArousal = Math.max(-style.arousal, 0);
  const negative = Math.max(-style.valence, 0);
  const confident = Math.max(style.dominance, 0);
  const withdrawn = Math.max(-style.dominance, 0);
  return clamp(
    1 + highArousal * 0.14 - lowArousal * 0.1 + confident * 0.05 - negative * 0.08 - withdrawn * 0.04 + style.intensity * 0.08,
    0.72,
    1.18
  );
}
function emotionWeight(style, emotions, boost) {
  return isEmotion(style.emotion, emotions) ? boost : 0;
}
function isEmotion(emotion, emotions) {
  return emotions.includes(emotion);
}
function normalizeEmotion2(emotion) {
  const normalized = emotion?.trim().toLowerCase() ?? "";
  if (normalized === "soft-happy" || normalized === "soft-positive") return "happy";
  if (normalized === "soft-calm") return "calm";
  if (normalized === "soft-curious") return "curious";
  if (normalized === "soft-shy") return "shy";
  if (normalized === "soft-uneasy") return "anxiety";
  if (normalized === "soft-low") return "sad";
  if (normalized === "soft-steady") return "neutral";
  return normalized || "neutral";
}
function buildSlowSwayFrames(context, duration) {
  const { side, amplitude, tempo } = context;
  const t = createWaitingTimeScaler(duration);
  return [
    styledFrame(context, 0, t(1.18 * tempo), "easeOut", waitingSwayFrame(side, amplitude, 1)),
    styledFrame(context, t(1.44 * tempo), t(1.38 * tempo), "easeInOut", waitingSwayFrame(-side, amplitude * 0.92, 2)),
    styledFrame(context, t(3 * tempo), t(1.22 * tempo), "easeInOut", waitingSwayFrame(side, amplitude * 0.62, 3)),
    frame2(t(4.5), duration - t(4.5), "easeOut", waitingSwayRestFrame())
  ];
}
function buildFigureEightFrames(context, duration) {
  const { side, amplitude, tempo, random } = context;
  const t = createWaitingTimeScaler(duration);
  const gazeLead = 0.14 + random() * 0.08;
  return [
    styledFrame(context, 0, t(0.96 * tempo), "easeOut", clampFACSState({
      headX: side * amplitude * 0.2,
      headY: amplitude * 0.1,
      headZ: side * amplitude * 0.42,
      bodyX: -side * amplitude * 0.16,
      bodyY: amplitude * 0.12,
      bodyZ: side * amplitude * 0.32,
      gazeX: -side * amplitude * gazeLead,
      gazeY: amplitude * 0.08,
      eyeSmile: amplitude * 0.12,
      mouthSmile: amplitude * 0.12
    })),
    styledFrame(context, t(1.2 * tempo), t(1.08 * tempo), "easeInOut", clampFACSState({
      headX: -side * amplitude * 0.18,
      headY: -amplitude * 0.05,
      headZ: -side * amplitude * 0.36,
      bodyX: side * amplitude * 0.15,
      bodyY: amplitude * 0.08,
      bodyZ: -side * amplitude * 0.3,
      gazeX: side * amplitude * gazeLead,
      gazeY: -amplitude * 0.04,
      browOuterUp: amplitude * 0.08,
      mouthSmile: amplitude * 0.1
    })),
    styledFrame(context, t(2.55 * tempo), t(1.06 * tempo), "easeInOut", clampFACSState({
      headX: side * amplitude * 0.15,
      headY: amplitude * 0.06,
      headZ: side * amplitude * 0.3,
      bodyX: side * amplitude * 0.1,
      bodyY: amplitude * 0.1,
      bodyZ: side * amplitude * 0.24,
      gazeX: -side * amplitude * gazeLead * 0.7,
      gazeY: amplitude * 0.05,
      eyeSmile: amplitude * 0.1
    })),
    frame2(t(4.3), duration - t(4.3), "easeOut", waitingSwayRestFrame())
  ];
}
function buildCuriousLeanFrames(context, duration) {
  const { side, amplitude, tempo, random } = context;
  const t = createWaitingTimeScaler(duration);
  const tilt = 0.34 + random() * 0.12;
  return [
    styledFrame(context, 0, t(1.08 * tempo), "easeOut", clampFACSState({
      headX: side * amplitude * 0.12,
      headY: amplitude * 0.18,
      headZ: side * amplitude * tilt,
      bodyY: amplitude * 0.3,
      bodyZ: side * amplitude * 0.18,
      gazeX: side * amplitude * 0.18,
      gazeY: amplitude * 0.14,
      browOuterUp: amplitude * 0.16,
      eyeSmile: amplitude * 0.08,
      mouthSmile: amplitude * 0.08
    })),
    styledFrame(context, t(1.65 * tempo), t(1.18 * tempo), "easeInOut", clampFACSState({
      headX: -side * amplitude * 0.08,
      headY: amplitude * 0.12,
      headZ: -side * amplitude * 0.22,
      bodyY: amplitude * 0.2,
      bodyZ: -side * amplitude * 0.12,
      gazeX: -side * amplitude * 0.22,
      gazeY: amplitude * 0.08,
      browOuterUp: amplitude * 0.12,
      eyeSquint: amplitude * 0.06
    })),
    styledFrame(context, t(3.35), t(1.05), "easeInOut", clampFACSState({
      headY: amplitude * 0.06,
      bodyY: amplitude * 0.1,
      gazeY: amplitude * 0.04,
      eyeSmile: amplitude * 0.08,
      mouthSmile: amplitude * 0.08
    })),
    frame2(t(4.55), duration - t(4.55), "easeOut", waitingSwayRestFrame())
  ];
}
function buildShyRockFrames(context, duration) {
  const { side, amplitude, tempo } = context;
  const t = createWaitingTimeScaler(duration);
  return [
    styledFrame(context, 0, t(1.15 * tempo), "easeOut", clampFACSState({
      headY: -amplitude * 0.2,
      headZ: -side * amplitude * 0.34,
      bodyX: side * amplitude * 0.12,
      bodyY: -amplitude * 0.12,
      bodyZ: -side * amplitude * 0.28,
      gazeX: side * amplitude * 0.2,
      gazeY: -amplitude * 0.14,
      browInnerUp: amplitude * 0.12,
      blush: amplitude * 0.12,
      mouthSmile: amplitude * 0.1
    })),
    styledFrame(context, t(1.68 * tempo), t(1.25 * tempo), "easeInOut", clampFACSState({
      headY: -amplitude * 0.16,
      headZ: side * amplitude * 0.28,
      bodyX: -side * amplitude * 0.1,
      bodyY: -amplitude * 0.08,
      bodyZ: side * amplitude * 0.22,
      gazeX: -side * amplitude * 0.14,
      gazeY: -amplitude * 0.1,
      eyeSmile: amplitude * 0.1,
      blush: amplitude * 0.14,
      mouthSmile: amplitude * 0.12
    })),
    styledFrame(context, t(3.3), t(1.05), "easeInOut", clampFACSState({
      headY: -amplitude * 0.08,
      gazeY: -amplitude * 0.05,
      blush: amplitude * 0.08,
      mouthSmile: amplitude * 0.08
    })),
    frame2(t(4.55), duration - t(4.55), "easeOut", waitingSwayRestFrame())
  ];
}
function buildBuoyantBobFrames(context, duration) {
  const { side, amplitude, tempo, random } = context;
  const t = createWaitingTimeScaler(duration);
  const bob = 0.2 + random() * 0.08;
  return [
    styledFrame(context, 0, t(0.9 * tempo), "easeOut", clampFACSState({
      headY: amplitude * bob,
      headZ: side * amplitude * 0.2,
      bodyY: amplitude * 0.28,
      bodyZ: side * amplitude * 0.16,
      gazeY: amplitude * 0.08,
      eyeSmile: amplitude * 0.16,
      browOuterUp: amplitude * 0.08,
      mouthSmile: amplitude * 0.16
    })),
    styledFrame(context, t(1.18 * tempo), t(0.95 * tempo), "easeInOut", clampFACSState({
      headY: -amplitude * 0.08,
      headZ: -side * amplitude * 0.18,
      bodyY: -amplitude * 0.08,
      bodyZ: -side * amplitude * 0.12,
      gazeY: -amplitude * 0.04,
      eyeSmile: amplitude * 0.12,
      mouthSmile: amplitude * 0.12
    })),
    styledFrame(context, t(2.55 * tempo), t(1.12 * tempo), "easeInOut", clampFACSState({
      headY: amplitude * bob * 0.7,
      headZ: side * amplitude * 0.16,
      bodyY: amplitude * 0.18,
      bodyZ: side * amplitude * 0.1,
      gazeX: -side * amplitude * 0.1,
      gazeY: amplitude * 0.05,
      eyeSmile: amplitude * 0.14,
      mouthSmile: amplitude * 0.14
    })),
    frame2(t(4.42), duration - t(4.42), "easeOut", waitingSwayRestFrame())
  ];
}
function buildSoftSettleFrames(context, duration) {
  const { side, amplitude, tempo } = context;
  const t = createWaitingTimeScaler(duration);
  return [
    styledFrame(context, 0, t(1.34 * tempo), "easeOut", clampFACSState({
      headY: -amplitude * 0.14,
      headZ: side * amplitude * 0.18,
      bodyY: -amplitude * 0.1,
      bodyZ: side * amplitude * 0.12,
      gazeX: side * amplitude * 0.08,
      gazeY: -amplitude * 0.12,
      browInnerUp: amplitude * 0.1,
      mouthFrown: amplitude * 0.06
    })),
    styledFrame(context, t(1.82 * tempo), t(1.42 * tempo), "easeInOut", clampFACSState({
      headY: -amplitude * 0.07,
      headZ: -side * amplitude * 0.12,
      bodyY: -amplitude * 0.06,
      bodyZ: -side * amplitude * 0.08,
      gazeX: -side * amplitude * 0.06,
      gazeY: -amplitude * 0.08,
      browInnerUp: amplitude * 0.08,
      eyeSmile: amplitude * 0.04
    })),
    styledFrame(context, t(3.52), t(1.08), "easeInOut", clampFACSState({
      headY: -amplitude * 0.04,
      bodyY: -amplitude * 0.04,
      gazeY: -amplitude * 0.05,
      browInnerUp: amplitude * 0.06
    })),
    frame2(t(4.72), duration - t(4.72), "easeOut", waitingSwayRestFrame())
  ];
}
function buildContainedTensionFrames(context, duration) {
  const { side, amplitude, tempo, random } = context;
  const t = createWaitingTimeScaler(duration);
  const tension = 0.76 + random() * 0.18;
  return [
    styledFrame(context, 0, t(0.98 * tempo), "easeOut", clampFACSState({
      headX: side * amplitude * 0.08,
      headY: -amplitude * 0.04,
      headZ: side * amplitude * 0.24 * tension,
      bodyX: side * amplitude * 0.1,
      bodyY: -amplitude * 0.04,
      bodyZ: -side * amplitude * 0.16 * tension,
      gazeX: -side * amplitude * 0.12,
      gazeY: -amplitude * 0.03,
      browDown: amplitude * 0.1,
      eyeSquint: amplitude * 0.06
    })),
    styledFrame(context, t(1.32 * tempo), t(0.92 * tempo), "easeInOut", clampFACSState({
      headX: -side * amplitude * 0.06,
      headY: -amplitude * 0.02,
      headZ: -side * amplitude * 0.18 * tension,
      bodyX: -side * amplitude * 0.08,
      bodyY: -amplitude * 0.03,
      bodyZ: side * amplitude * 0.14 * tension,
      gazeX: side * amplitude * 0.08,
      browDown: amplitude * 0.08,
      eyeSquint: amplitude * 0.05
    })),
    styledFrame(context, t(2.58 * tempo), t(1.26 * tempo), "easeInOut", clampFACSState({
      headY: -amplitude * 0.03,
      headZ: side * amplitude * 0.08,
      bodyY: -amplitude * 0.03,
      bodyZ: side * amplitude * 0.06,
      gazeY: -amplitude * 0.02,
      browDown: amplitude * 0.05,
      eyeSquint: amplitude * 0.03
    })),
    frame2(t(4.3), duration - t(4.3), "easeOut", waitingSwayRestFrame())
  ];
}
function createWaitingTimeScaler(duration) {
  const scale = duration / baseTemplateDurationSeconds;
  return (time) => time * scale;
}
function styledFrame(context, time, duration, easing, facs, styleWeight = 1) {
  return frame2(time, duration, easing, addFACS(facs, context.style.postureBias, styleWeight));
}
function frame2(time, duration, easing, facs) {
  return {
    time,
    duration: Math.max(0.2, duration),
    easing,
    facs
  };
}
function waitingSwayFrame(side, amplitude, phase) {
  const headZBase = phase === 1 ? 0.52 : phase === 2 ? 0.62 : 0.42;
  const bodyZBase = phase === 1 ? 0.42 : phase === 2 ? 0.5 : 0.34;
  return clampFACSState({
    headX: side * amplitude * 0.18,
    headY: amplitude * 0.1,
    headZ: side * amplitude * headZBase,
    bodyX: side * amplitude * 0.22,
    bodyY: amplitude * 0.16,
    bodyZ: side * amplitude * bodyZBase,
    gazeX: -side * amplitude * 0.2,
    gazeY: amplitude * 0.08,
    eyeSmile: amplitude * 0.16,
    browOuterUp: amplitude * 0.1,
    mouthSmile: amplitude * 0.16
  });
}
function waitingSwayRestFrame() {
  return {
    browInnerUp: 0,
    headX: 0,
    headY: 0,
    headZ: 0,
    bodyX: 0,
    bodyY: 0,
    bodyZ: 0,
    gazeX: 0,
    gazeY: 0,
    eyeSmile: 0,
    eyeSquint: 0,
    browOuterUp: 0,
    mouthSmile: 0,
    blush: 0
  };
}
var CharacterStateMachine = class {
  constructor() {
    __publicField(this, "state", "IDLE");
    __publicField(this, "enteredAt", 0);
  }
  get current() {
    return this.state;
  }
  get phaseStartedAt() {
    return this.enteredAt;
  }
  transition(next, timeSeconds, force = false) {
    if (this.state === next && !force) return;
    this.state = next;
    this.enteredAt = timeSeconds;
  }
  reset(timeSeconds = 0) {
    this.state = "IDLE";
    this.enteredAt = timeSeconds;
  }
  elapsed(timeSeconds) {
    return Math.max(0, timeSeconds - this.enteredAt);
  }
};
var additiveFACSKeys = /* @__PURE__ */ new Set([
  "headX",
  "headY",
  "headZ",
  "bodyX",
  "bodyY",
  "bodyZ",
  "breath",
  "eyeBlinkL",
  "eyeBlinkR"
]);
var maxFACSKeys = /* @__PURE__ */ new Set([
  "mouthOpen",
  "blush",
  "tear",
  "sweat"
]);
var MotionMixer = class {
  mix(input) {
    let result = createDefaultFACSState();
    result = this.applyLayer(result, input.idle, "idle");
    result = this.applyLayer(result, input.emotion, "emotion");
    result = this.applyLayer(result, input.reaction, "reaction");
    result = this.applyLayer(result, input.speech, "speech");
    result = this.applyLayer(result, input.manual, "manual");
    return clampFACSState(result);
  }
  applyLayer(base, layer, mode) {
    if (!layer) return base;
    const result = { ...base };
    for (const key of facsKeys) {
      const value = layer[key];
      if (typeof value !== "number") continue;
      if (mode === "manual") {
        result[key] = value;
      } else if (mode === "speech") {
        if (key === "mouthOpen") {
          result[key] = Math.max(result[key], value);
        } else if (key === "browOuterUp") {
          result[key] += value;
        } else if (additiveFACSKeys.has(key)) {
          result[key] += value;
        }
      } else if (mode === "idle") {
        if (key === "breath") {
          result[key] = value;
        } else if (additiveFACSKeys.has(key) || key === "mouthSmile" || key === "browInnerUp") {
          result[key] += value;
        } else {
          result[key] = value;
        }
      } else if (mode === "emotion") {
        if (key === "breath") {
          result[key] = Math.max(result[key], value);
        } else if (additiveFACSKeys.has(key) || key === "mouthSmile" || key === "mouthFrown" || key.startsWith("brow")) {
          result[key] += value;
        } else if (maxFACSKeys.has(key)) {
          result[key] = Math.max(result[key], value);
        } else {
          result[key] = value;
        }
      } else if (mode === "reaction") {
        if (maxFACSKeys.has(key)) {
          result[key] = Math.max(result[key], value);
        } else if (additiveFACSKeys.has(key)) {
          result[key] += value;
        } else {
          result[key] = value;
        }
      }
    }
    return clampFACSState(result);
  }
};
function smoothDamp(current, target, factor) {
  return current + (target - current) * factor;
}
function smoothingFactor(speed, deltaSeconds) {
  return 1 - Math.exp(-Math.max(0, speed) * Math.max(0, deltaSeconds));
}
var LayeredParameterMixer = class {
  constructor() {
    __publicField(this, "current", {});
  }
  reset() {
    this.current = {};
  }
  smooth(target, deltaSeconds, speedByParam = {}) {
    const result = { ...this.current };
    const keys = /* @__PURE__ */ new Set([...Object.keys(this.current), ...Object.keys(target)]);
    for (const key of keys) {
      const current = this.current[key] ?? target[key] ?? 0;
      const next = target[key] ?? 0;
      const speed = speedByParam[key] ?? 14;
      const factor = smoothingFactor(speed, deltaSeconds);
      result[key] = smoothDamp(current, next, factor);
    }
    this.current = result;
    return result;
  }
};
var SoullinkRuntime = class {
  constructor(options) {
    __publicField(this, "stateMachine", new CharacterStateMachine());
    __publicField(this, "classifier", new MessageReactionClassifier());
    __publicField(this, "generator", new RuntimeExpressionGenerator());
    __publicField(this, "emotionState");
    __publicField(this, "vadMapper", new VADExpressionMapper());
    __publicField(this, "vadGesture");
    __publicField(this, "vadMicroMotion");
    __publicField(this, "vadPrivateParameters", new VADPrivateParameterOverlay());
    __publicField(this, "vadPrivateParameterInfo", {});
    __publicField(this, "actionUnitSolver", new ActionUnitSolver());
    __publicField(this, "idle");
    __publicField(this, "idleActions");
    __publicField(this, "mixer", new MotionMixer());
    __publicField(this, "paramSmoother", new LayeredParameterMixer());
    __publicField(this, "lipSync", new LipSyncController());
    __publicField(this, "voiceWaitingMotion", new VoiceWaitingMotionController());
    __publicField(this, "reaction", new ReactionSequencer());
    __publicField(this, "actionPlan", new ActionPlanSequencer());
    __publicField(this, "speechParameters", new ParameterPlanSequencer());
    __publicField(this, "recovery", new RecoveryController());
    __publicField(this, "proactive", new ProactiveController());
    __publicField(this, "reflectionPulse", new ReflectionPulseController());
    __publicField(this, "adapter");
    __publicField(this, "profile");
    __publicField(this, "personality");
    __publicField(this, "motionStyle");
    __publicField(this, "sessionRandom");
    __publicField(this, "audioLevelAnalyzer");
    __publicField(this, "currentIntent", null);
    __publicField(this, "currentSeed", null);
    __publicField(this, "currentVAD", {
      current: { valence: 0, arousal: 0, dominance: 0 },
      target: { valence: 0, arousal: 0, dominance: 0 },
      dominantEmotion: "neutral",
      intensity: 0
    });
    __publicField(this, "currentActionUnits", createDefaultActionUnitState());
    __publicField(this, "currentFACS", createDefaultFACSState());
    __publicField(this, "currentParams", {});
    __publicField(this, "currentNativeAnimation", null);
    __publicField(this, "manualFACS", {});
    __publicField(this, "manualActionUnits", {});
    __publicField(this, "customChannels", {});
    __publicField(this, "vadExpressionResidue", null);
    __publicField(this, "parameterGain", 1.45);
    __publicField(this, "bodyMotionGain", 1.25);
    __publicField(this, "idleEnabled", true);
    __publicField(this, "lipSyncEnabled", true);
    __publicField(this, "voicePlaybackActive", false);
    __publicField(this, "currentPlan", null);
    __publicField(this, "currentProactive", null);
    __publicField(this, "currentReflection", null);
    __publicField(this, "listenDuration", 0.46);
    __publicField(this, "speechDuration", 2.2);
    this.profile = options.profile;
    this.adapter = new ModelProfileAdapter(options.profile);
    this.emotionState = new EmotionStateController(options.emotionPersonality);
    this.currentVAD = this.emotionState.update(0);
    this.personality = {
      expressiveness: 0.88,
      softness: 0.7,
      shyness: 0.58,
      gazeStability: 0.72,
      ...options.personality
    };
    this.motionStyle = resolveMotionStyle(options.motionStyle, this.personality.gazeStability);
    this.sessionRandom = seededRandom(deriveMotionSeed(this.motionStyle.seed, 0));
    this.audioLevelAnalyzer = options.audioLevelAnalyzer ?? null;
    this.idle = this.createIdleEngine();
    this.idleActions = this.createIdleActionScheduler();
    this.vadGesture = new VADGestureController(deriveMotionSeed(this.motionStyle.seed, 20));
    this.vadMicroMotion = new VADMicroMotionController(deriveMotionSeed(this.motionStyle.seed, 21));
  }
  setProfile(profile) {
    this.profile = profile;
    this.adapter.setProfile(profile);
    this.refreshPrivateVADParameters();
  }
  setIdleEnabled(enabled) {
    this.idleEnabled = enabled;
  }
  setLipSyncEnabled(enabled) {
    this.lipSyncEnabled = enabled;
  }
  setMotionStyle(options) {
    this.motionStyle = resolveMotionStyle(
      { ...this.motionStyle, ...options },
      this.personality.gazeStability,
      this.motionStyle.seed
    );
    this.sessionRandom = seededRandom(deriveMotionSeed(this.motionStyle.seed, 0));
    this.idle = this.createIdleEngine();
    this.idleActions = this.createIdleActionScheduler();
    this.vadGesture = new VADGestureController(deriveMotionSeed(this.motionStyle.seed, 20));
    this.vadMicroMotion = new VADMicroMotionController(deriveMotionSeed(this.motionStyle.seed, 21));
  }
  getMotionStyle() {
    return { ...this.motionStyle };
  }
  setAudioLevelAnalyzer(analyzer) {
    this.audioLevelAnalyzer?.reset?.();
    this.audioLevelAnalyzer = analyzer;
    this.lipSync.reset();
  }
  setVoicePlaybackActive(active) {
    if (this.voicePlaybackActive !== active) this.lipSync.reset();
    this.voicePlaybackActive = active;
    if (active) this.voiceWaitingMotion.reset();
    else this.audioLevelAnalyzer?.reset?.();
  }
  startVoiceWaitingMotion(timeSeconds, seed, options) {
    return this.voiceWaitingMotion.start(timeSeconds, seed, options);
  }
  clearVoiceWaitingMotion() {
    this.voiceWaitingMotion.reset();
  }
  setManualFACS(facs) {
    this.manualFACS = { ...facs };
  }
  setManualActionUnits(actionUnits) {
    this.manualActionUnits = { ...actionUnits };
  }
  setCustomChannel(name, value) {
    this.customChannels[name] = value;
  }
  setCustomChannels(record) {
    this.customChannels = { ...record };
  }
  clearCustomChannels() {
    this.customChannels = {};
  }
  setParameterGain(gain) {
    this.parameterGain = clamp(gain, 0.4, 5);
  }
  setBodyMotionGain(gain) {
    this.bodyMotionGain = clamp(gain, 0, 4);
  }
  setPrivateVADParameters(parameters) {
    this.vadPrivateParameterInfo = { ...parameters };
    this.refreshPrivateVADParameters();
    return this.vadPrivateParameters.getSummary();
  }
  refreshPrivateVADParameters() {
    const mappedIds = /* @__PURE__ */ new Set();
    for (const rule of Object.values(this.profile.parameterMap)) {
      if (rule?.target) mappedIds.add(rule.target);
      for (const target of rule?.targets ?? []) mappedIds.add(target);
    }
    this.vadPrivateParameters.setParameters(
      this.vadPrivateParameterInfo,
      this.profile.privateEmotionMap,
      mappedIds
    );
  }
  setVADDecayRate(rate) {
    this.emotionState.configure({ decayRate: rate });
  }
  setProactiveRepeatEnabled(enabled) {
    this.proactive.setRepeatOnSettledVAD(enabled);
  }
  clearManualFACS() {
    this.manualFACS = {};
    this.manualActionUnits = {};
  }
  sendMessage(message, timeSeconds) {
    const intent = this.classifier.classify(message);
    this.triggerIntent(intent, timeSeconds);
    return intent;
  }
  triggerPlan(plan, timeSeconds) {
    this.triggerIntent(plan.intent, timeSeconds, {
      vadTarget: plan.vadTarget,
      vadDelta: plan.vadDelta,
      actionPlan: plan.actionPlan,
      parameterPlan: plan.parameterPlan,
      replyDraft: plan.replyDraft,
      provider: plan.provider
    });
    return plan.intent;
  }
  triggerIntent(intent, timeSeconds, options = {}) {
    const resolvedOptions = typeof options === "number" ? { seed: options } : options;
    const seed = resolvedOptions.seed ?? Math.max(1, Math.floor(this.sessionRandom() * 2147483647));
    const reactionStart = timeSeconds;
    if (!intent.contextTags.includes("proactive_idle")) {
      this.proactive.notifyUserInteraction(timeSeconds);
    }
    this.currentProactive = null;
    this.reflectionPulse.reset();
    this.currentIntent = intent;
    this.currentSeed = seed;
    const expression = this.generator.generate({
      emotion: intent.emotion,
      variant: intent.variant,
      intensity: intent.intensity,
      contextTags: intent.contextTags,
      personality: this.personality,
      previousState: this.currentFACS,
      seed
    });
    this.reaction.start(expression, reactionStart);
    this.vadExpressionResidue = this.createVADExpressionResidue(expression, intent);
    this.actionPlan.start(resolvedOptions.actionPlan, reactionStart);
    this.speechParameters.reset();
    this.emotionState.nudge(intent);
    if (resolvedOptions.vadDelta) this.emotionState.nudgeVAD(resolvedOptions.vadDelta, 0.72);
    if (resolvedOptions.vadTarget) this.emotionState.blendTo(resolvedOptions.vadTarget, 0.68);
    this.idle.deferBlink(timeSeconds, this.listenDuration + this.reaction.duration + 0.35);
    this.recovery.reset();
    this.speechDuration = estimateMockSpeechDuration(intent.sourceMessage ?? intent.emotion);
    this.currentNativeAnimation = resolveNativeAnimation(this.profile, intent);
    this.currentPlan = {
      provider: resolvedOptions.provider ?? "local",
      replyDraft: resolvedOptions.replyDraft ?? "",
      actionBeatCount: this.actionPlan.beatCount,
      parameterBeatCount: this.speechParameters.beatCount,
      startedAt: timeSeconds
    };
    this.stateMachine.transition("LISTENING", timeSeconds);
  }
  startSpeechMotion(parameterPlan, timeSeconds, durationSeconds) {
    if (durationSeconds !== void 0) {
      this.speechDuration = clamp(durationSeconds, 0.4, 120);
    }
    this.speechParameters.start(parameterPlan, timeSeconds);
    if (this.currentPlan) {
      this.currentPlan = {
        ...this.currentPlan,
        parameterBeatCount: this.speechParameters.beatCount
      };
    }
    this.stateMachine.transition("SPEAKING", timeSeconds, true);
  }
  clearSpeechMotion() {
    this.speechParameters.reset();
  }
  applyVADTarget(target, amount = 0.65) {
    this.emotionState.blendTo(target, amount);
  }
  applyVADDelta(delta, amount = 1) {
    this.emotionState.nudgeVAD(delta, amount);
  }
  setReflection(reflection, timeSeconds) {
    const pulseIntensity = this.getReflectionPulseIntensity(reflection.vadTarget);
    this.currentReflection = {
      ...reflection,
      createdAt: timeSeconds
    };
    if (reflection.vadTarget) {
      this.emotionState.blendTo(reflection.vadTarget, 0.94);
    }
    if (this.stateMachine.current === "IDLE" || this.stateMachine.current === "RECOVERING") {
      this.reflectionPulse.start({
        emotion: reflection.emotion,
        vadTarget: reflection.vadTarget,
        intensity: pulseIntensity,
        seed: Math.round(timeSeconds * 1e3)
      }, timeSeconds);
    }
  }
  consumeProactive() {
    this.proactive.consume();
    this.currentProactive = null;
  }
  reset(timeSeconds) {
    this.currentIntent = null;
    this.currentSeed = null;
    this.emotionState.reset();
    this.currentVAD = this.emotionState.update(0);
    this.currentActionUnits = createDefaultActionUnitState();
    this.currentFACS = createDefaultFACSState();
    this.currentParams = {};
    this.currentNativeAnimation = null;
    this.voicePlaybackActive = false;
    this.audioLevelAnalyzer?.reset?.();
    this.lipSync.reset();
    this.manualFACS = {};
    this.manualActionUnits = {};
    this.customChannels = {};
    this.reaction.reset();
    this.actionPlan.reset();
    this.speechParameters.reset();
    this.voiceWaitingMotion.reset();
    this.recovery.reset();
    this.vadGesture.reset();
    this.vadMicroMotion.reset();
    this.idle.reset();
    this.idleActions.reset(timeSeconds);
    this.reflectionPulse.reset();
    this.vadExpressionResidue = null;
    this.proactive.reset(timeSeconds);
    this.currentPlan = null;
    this.currentProactive = null;
    this.currentReflection = null;
    this.paramSmoother.reset();
    this.sessionRandom = seededRandom(deriveMotionSeed(this.motionStyle.seed, 0));
    this.stateMachine.reset(timeSeconds);
  }
  update(timeSeconds, deltaSeconds) {
    this.advanceState(timeSeconds);
    const focusLevel = this.stateMachine.current === "IDLE" || this.stateMachine.current === "RECOVERING" ? 0 : 1;
    this.currentVAD = this.emotionState.update(deltaSeconds);
    this.currentProactive = this.proactive.update(timeSeconds, this.stateMachine.current, this.currentVAD);
    const emotionLayer = this.vadMapper.toFACS(this.currentVAD.current, this.getEmotionLayerWeight(), {
      dominantEmotion: this.currentVAD.dominantEmotion,
      residue: this.vadExpressionResidue
    });
    const idleBaseLayer = this.idle.update(timeSeconds, {
      enabled: this.idleEnabled,
      focusLevel,
      profile: this.profile,
      bodyMotionGain: this.bodyMotionGain
    });
    const vadMicroLayer = this.vadMicroMotion.update(timeSeconds, this.currentVAD.current, focusLevel, this.bodyMotionGain);
    const idleActionLayer = this.idleActions.update(timeSeconds, {
      enabled: this.idleEnabled,
      focusLevel,
      vad: this.currentVAD,
      personality: this.personality,
      profile: this.profile,
      suppressed: !this.isIdleGestureEnabled()
    });
    const vadGestureLayer = this.vadGesture.update(timeSeconds, this.currentVAD, {
      enabled: this.isIdleGestureEnabled(),
      bodyMotionGain: this.bodyMotionGain,
      frequency: this.motionStyle.gestureFrequency,
      avoidRepeatWindow: this.motionStyle.avoidRepeatWindow
    });
    const idleLayer = addFACS(addFACS(addFACS(idleBaseLayer, vadMicroLayer), idleActionLayer), vadGestureLayer);
    const reactionLayer = this.getReactionLayer(timeSeconds);
    const reflectionLayer = this.getReflectionLayer(timeSeconds);
    const voiceWaitingLayer = this.voiceWaitingMotion.update(timeSeconds, this.bodyMotionGain);
    const audioInput = this.readAudioInput();
    const speechLayer = this.lipSync.update(timeSeconds, {
      enabled: this.lipSyncEnabled,
      speaking: this.voicePlaybackActive,
      intensity: this.currentIntent?.intensity ?? 0,
      deltaSeconds,
      speechAccentGain: this.motionStyle.speechAccentGain,
      ...audioInput
    });
    const manualLayer = this.getManualLayer();
    this.currentFACS = this.applyLipSyncMouthGate(this.mixer.mix({
      idle: idleLayer,
      emotion: emotionLayer,
      reaction: addFACS(addFACS(reactionLayer, reflectionLayer), voiceWaitingLayer),
      speech: speechLayer,
      manual: manualLayer
    }), speechLayer);
    this.currentActionUnits = this.actionUnitSolver.project(this.currentFACS);
    const facsParams = this.applyParameterGain(this.adapter.apply(this.currentFACS, this.customChannels));
    const privateVADParams = this.vadPrivateParameters.update(
      this.currentVAD,
      this.getPrivateVADParameterWeight(),
      {
        intentEmotion: this.currentIntent?.naturalEmotion ?? this.currentIntent?.emotion,
        intentVariant: this.currentIntent?.naturalVariant ?? this.currentIntent?.variant
      }
    );
    const targetParams = this.applySpeechParameterOverlay({
      ...facsParams,
      ...privateVADParams
    }, timeSeconds);
    this.currentParams = this.paramSmoother.smooth(
      targetParams,
      deltaSeconds,
      this.profile.parameterSmoothing ?? {}
    );
    return this.getSnapshot();
  }
  getSnapshot() {
    return {
      state: this.stateMachine.current,
      emotionIntent: this.currentIntent,
      runtimeExpression: this.reaction.currentExpression,
      seed: this.currentSeed,
      vad: this.currentVAD,
      actionUnits: this.currentActionUnits,
      facs: this.currentFACS,
      live2dParams: this.currentParams,
      nativeAnimation: this.currentNativeAnimation,
      profile: this.profile,
      idleEnabled: this.idleEnabled,
      lipSyncEnabled: this.lipSyncEnabled,
      manualFACS: this.manualFACS,
      manualActionUnits: this.manualActionUnits,
      parameterGain: this.parameterGain,
      bodyMotionGain: this.bodyMotionGain,
      proactiveRepeatEnabled: this.proactive.repeatEnabled,
      motionStyle: { ...this.motionStyle },
      plan: this.currentPlan,
      proactive: this.currentProactive,
      reflection: this.currentReflection,
      customChannels: { ...this.customChannels }
    };
  }
  getEmotionLayerWeight() {
    const state = this.stateMachine.current;
    if (state === "IDLE" || state === "RECOVERING") return 1;
    if (state === "SPEAKING") return 0.42;
    return 0.24;
  }
  createIdleEngine() {
    return new IdleEngine({
      seed: deriveMotionSeed(this.motionStyle.seed, 10),
      gazeStability: this.motionStyle.gazeStability,
      blinkRate: this.motionStyle.blinkRate,
      breathRate: this.motionStyle.breathRate,
      breathVariance: this.motionStyle.breathVariance,
      microMotionGain: this.motionStyle.microMotionGain
    });
  }
  createIdleActionScheduler() {
    return new IdleActionScheduler({
      seed: deriveMotionSeed(this.motionStyle.seed, 11),
      spontaneity: this.motionStyle.spontaneity / 2,
      gain: this.motionStyle.idleActionGain,
      recentWindowSize: this.motionStyle.avoidRepeatWindow
    });
  }
  readAudioInput() {
    if (!this.voicePlaybackActive) return {};
    const analyzer = this.audioLevelAnalyzer;
    if (!analyzer) return {};
    try {
      const available = analyzer.isAvailable?.() ?? analyzer.available?.() ?? true;
      if (!available) return {};
      const level = analyzer.getLevel();
      if (!Number.isFinite(level) || level < 0) return {};
      const peak = analyzer.getPeak?.();
      return {
        audioLevel: clamp(level, 0, 1),
        audioPeak: peak !== void 0 && Number.isFinite(peak) && peak >= 0 ? clamp(peak, 0, 1) : void 0
      };
    } catch {
      return {};
    }
  }
  getPrivateVADParameterWeight() {
    const state = this.stateMachine.current;
    if (state === "IDLE" || state === "RECOVERING") return 1;
    if (state === "SPEAKING") return 0.46;
    return 0.72;
  }
  isIdleGestureEnabled() {
    return !this.voicePlaybackActive && (this.stateMachine.current === "IDLE" || this.stateMachine.current === "RECOVERING");
  }
  getManualLayer() {
    if (Object.keys(this.manualActionUnits).length === 0) return this.manualFACS;
    return addFACS(this.manualFACS, this.actionUnitSolver.solvePartial(this.manualActionUnits));
  }
  applyParameterGain(params) {
    if (this.parameterGain === 1) return params;
    const ranges = this.getParameterRanges();
    const result = {};
    for (const [key, value] of Object.entries(params)) {
      const neutral = (this.profile.neutralParams ?? deriveNeutralParams(this.profile))[key] ?? 0;
      const boosted = neutral + (value - neutral) * this.parameterGain;
      const range = ranges[key];
      result[key] = range ? clamp(boosted, range.min, range.max) : boosted;
    }
    return result;
  }
  getParameterRanges() {
    return deriveParameterRanges(this.profile);
  }
  advanceState(timeSeconds) {
    const state = this.stateMachine.current;
    if (state === "LISTENING" && this.stateMachine.elapsed(timeSeconds) >= this.listenDuration) {
      this.stateMachine.transition("REACTING", timeSeconds);
      return;
    }
    if (state === "REACTING" && this.reaction.isComplete(timeSeconds) && this.actionPlan.isComplete(timeSeconds)) {
      this.stateMachine.transition("SPEAKING", timeSeconds);
      return;
    }
    if (state === "SPEAKING" && this.stateMachine.elapsed(timeSeconds) >= this.speechDuration) {
      const expression = this.reaction.currentExpression;
      if (expression?.idleBias) {
        const idleReturnDuration = Math.max(3.4, Math.min(7.2, expression.recoveryDuration));
        this.idle.setBias(expression.idleBias, idleReturnDuration, timeSeconds);
      }
      this.recovery.reset();
      this.reaction.reset();
      this.actionPlan.reset();
      this.speechParameters.reset();
      this.stateMachine.transition("IDLE", timeSeconds);
      return;
    }
    if (state === "RECOVERING" && this.recovery.isComplete(timeSeconds)) {
      this.recovery.reset();
      this.reaction.reset();
      this.actionPlan.reset();
      this.speechParameters.reset();
      this.stateMachine.transition("IDLE", timeSeconds);
    }
  }
  getReactionLayer(timeSeconds) {
    const state = this.stateMachine.current;
    if (state === "LISTENING") {
      return addFACS(this.reaction.evaluate(timeSeconds), this.actionPlan.evaluate(timeSeconds));
    }
    if (state === "REACTING") {
      return addFACS(this.reaction.evaluate(timeSeconds), this.actionPlan.evaluate(timeSeconds));
    }
    if (state === "SPEAKING") {
      return this.reaction.hold(0.82);
    }
    if (state === "RECOVERING") {
      return {};
    }
    return {};
  }
  applySpeechParameterOverlay(base, timeSeconds) {
    if (this.stateMachine.current !== "SPEAKING") return base;
    const overlay = this.speechParameters.evaluate(timeSeconds);
    return Object.keys(overlay).length ? { ...base, ...overlay } : base;
  }
  applyLipSyncMouthGate(facs, speechLayer) {
    return {
      ...facs,
      mouthOpen: this.voicePlaybackActive && this.lipSyncEnabled ? speechLayer.mouthOpen ?? 0 : 0
    };
  }
  getReflectionLayer(timeSeconds) {
    const state = this.stateMachine.current;
    if (state !== "IDLE" && state !== "RECOVERING") return {};
    return this.reflectionPulse.update(timeSeconds);
  }
  getReflectionPulseIntensity(vadTarget) {
    if (!vadTarget) return 0.58;
    const magnitude2 = (Math.abs(vadTarget.valence ?? 0) + Math.abs(vadTarget.arousal ?? 0) * 0.82 + Math.abs(vadTarget.dominance ?? 0) * 0.64) / 2.46;
    return clamp(0.62 + magnitude2 * 0.76, 0.68, 0.98);
  }
  createVADExpressionResidue(expression, intent) {
    return {
      emotion: this.getNaturalEmotionName(expression, intent),
      facs: clampFACSState({
        ...scaleFACSFromNeutral(expression.peakFACS, 0.18),
        ...expression.idleBias ?? {}
      })
    };
  }
  getNaturalEmotionName(expression, intent) {
    if (intent.naturalVariant?.includes("shy") || expression.variant.includes("shy")) return "shy";
    return intent.naturalEmotion ?? expression.emotion;
  }
};

// node_modules/@soullink-emotion/runtime-core/dist/index.js
function nowSeconds() {
  if (typeof performance !== "undefined" && typeof performance.now === "function") {
    return performance.now() / 1e3;
  }
  return Date.now() / 1e3;
}
function createRafClock() {
  let handle = null;
  let running = false;
  let last = nowSeconds();
  const hasRaf = typeof requestAnimationFrame === "function" && typeof cancelAnimationFrame === "function";
  return {
    now: nowSeconds,
    start(cb) {
      if (running) return;
      running = true;
      last = nowSeconds();
      const loop = () => {
        if (!running) return;
        const now = nowSeconds();
        const dt = now - last;
        last = now;
        cb(now, dt);
        handle = hasRaf ? requestAnimationFrame(loop) : setTimeout(loop, 1e3 / 60);
      };
      handle = hasRaf ? requestAnimationFrame(loop) : setTimeout(loop, 1e3 / 60);
    },
    stop() {
      running = false;
      if (handle === null) return;
      if (hasRaf) cancelAnimationFrame(handle);
      else clearTimeout(handle);
      handle = null;
    }
  };
}
var DEFAULT_REFLECTION_IDLE_DELAY_SECONDS = 5;
var DEFAULT_SPEAKING_MOTION_SCHEDULING = {
  mode: "fixed-parallel",
  fixedFrameCount: 4,
  frameIntervalSec: 1
};
function createSoullinkSession(options) {
  const persona = options.persona;
  const planner = options.planner;
  const tts = options.tts;
  const classifier = options.classifier;
  const clock = options.clock ?? createRafClock();
  const audio = options.audio;
  const onSnapshot = options.onSnapshot;
  const reflectionIdleDelaySeconds = options.reflectionIdleDelaySeconds ?? DEFAULT_REFLECTION_IDLE_DELAY_SECONDS;
  const speakingMotionScheduling = resolveSpeakingMotionScheduling(options.speakingMotionScheduling);
  const runtime = new SoullinkRuntime({
    profile: options.profile,
    motionStyle: options.motionStyle,
    audioLevelAnalyzer: options.audioLevelAnalyzer
  });
  let profile = options.profile;
  let runtimeSnapshot = null;
  let planning = false;
  let apiError = null;
  let lastReply = "";
  let voiceStatus = "idle";
  let autoVoiceEnabled = true;
  let proactiveDraft = null;
  let conversation = [];
  let speakingMotionParameters = {};
  let started2 = false;
  let currentTime = clock.now?.() ?? 0;
  let pendingReflectionTopic = "";
  let idleReflectionStartedAt = null;
  let reflectionTriggeredForTurn = false;
  let reflectionRequestId = 0;
  let voiceRequestId = 0;
  let currentPlaybackSettle = null;
  let proactiveDraftRequestId = 0;
  let lastProactiveEventId = "";
  function now() {
    return clock.now?.() ?? currentTime;
  }
  function emit() {
    if (!onSnapshot) return;
    onSnapshot(getSnapshot());
  }
  function getSnapshot() {
    return {
      runtime: runtimeSnapshot,
      planning,
      apiError,
      lastReply,
      voiceStatus,
      autoVoiceEnabled,
      proactiveDraft,
      conversation
    };
  }
  function tick(tickNow, dt) {
    currentTime = tickNow;
    const delta = Math.min(0.05, dt || 1 / 60);
    const updated = runtime.update(tickNow, delta);
    if (triggerProactivePresetLoop(updated.proactive, tickNow)) {
      runtimeSnapshot = runtime.update(tickNow, 0);
      queueProactiveDraft(null);
    } else {
      runtimeSnapshot = updated;
      queueProactiveDraft(updated.proactive);
    }
    updateIdleReflectionTrigger(tickNow);
    emit();
  }
  function start2() {
    if (started2) return;
    started2 = true;
    runtimeSnapshot = runtime.getSnapshot();
    emit();
    clock.start(tick);
  }
  function stop2() {
    if (!started2) return;
    started2 = false;
    clock.stop();
    stopVoice2();
  }
  async function sendMessage(message, sendOptions = {}) {
    if (!message.trim()) return null;
    const currentVAD = runtimeSnapshot?.vad.current;
    const userTurn = { role: "user", content: message };
    planning = true;
    apiError = null;
    emit();
    let immediateIntent = null;
    try {
      if (!classifier) throw new Error("no-classifier");
      const result = await classifier.classify(message);
      immediateIntent = result.intent;
      runtime.triggerIntent(immediateIntent, now());
      conversation = [...conversation, userTurn];
    } catch {
      immediateIntent = runtime.sendMessage(message, now());
      conversation = [...conversation, userTurn];
    }
    emit();
    const replyTask = runReactionReply(message, immediateIntent, currentVAD).finally(() => {
      planning = false;
      emit();
    });
    if (sendOptions.awaitReply) {
      await replyTask;
    }
    return immediateIntent;
  }
  async function runReactionReply(message, immediateIntent, currentVAD) {
    if (!planner?.planReaction) {
      armIdleReflection(message);
      return;
    }
    try {
      const plan = await planner.planReaction({
        message,
        conversation,
        characterName: persona.name,
        characterProfile: persona.profile,
        vad: currentVAD
      });
      if (plan.replyDraft) {
        conversation = [...conversation, { role: "assistant", content: plan.replyDraft }];
        lastReply = plan.replyDraft;
        emit();
        if (plan.vadTarget) {
          runtime.applyVADTarget(plan.vadTarget, 0.5);
        }
        await speak2({
          text: plan.replyDraft,
          emotion: plan.intent.naturalEmotion ?? plan.intent.emotion,
          vad: plan.vadTarget ?? plan.intent.naturalVAD ?? currentVAD,
          intent: plan.intent,
          planSpeakingMotion: true,
          userMessage: message
        });
      }
      armIdleReflection(message);
    } catch (cause) {
      apiError = `API fallback: ${describeError(cause)}`;
      const fallbackReply = createFallbackReply(immediateIntent?.emotion ?? "neutral");
      conversation = [...conversation, { role: "assistant", content: fallbackReply }];
      lastReply = fallbackReply;
      emit();
      armIdleReflection(message);
    }
  }
  function triggerIntent(intent, triggerOptions) {
    runtime.triggerIntent(intent, now(), triggerOptions);
  }
  function triggerProactivePresetLoop(event, atTime) {
    if (!event?.reason.startsWith("repeat_vad_preset:")) return false;
    runtime.triggerIntent(proactiveIntent(event.emotion, event.intensity, event.suggestedMessage), atTime, {
      provider: "local",
      replyDraft: ""
    });
    runtime.consumeProactive();
    proactiveDraft = null;
    lastProactiveEventId = "";
    return true;
  }
  async function planProactive(event) {
    if (!planner?.planProactive) {
      return {
        message: event.suggestedMessage,
        emotion: event.emotion,
        reason: event.reason,
        provider: "local"
      };
    }
    return planner.planProactive({
      characterName: persona.name,
      characterProfile: persona.profile,
      proactive: event,
      conversation,
      reflection: runtimeSnapshot?.reflection ?? null,
      vad: runtimeSnapshot?.vad.current
    });
  }
  async function acceptProactive() {
    const event = runtimeSnapshot?.proactive;
    if (!event) return;
    planning = true;
    apiError = null;
    emit();
    try {
      const plan = proactiveDraft?.eventId === event.id && proactiveDraft.status === "ready" ? draftToPlan(proactiveDraft) : await planProactive(event);
      const intent = proactiveIntent(plan.emotion, event.intensity, plan.message);
      runtime.triggerIntent(intent, now(), { provider: plan.provider, replyDraft: plan.message });
      runtime.consumeProactive();
      proactiveDraft = null;
      lastProactiveEventId = "";
      pushAssistantTurn(plan.message);
      void speak2({
        text: plan.message,
        emotion: intent.naturalEmotion ?? intent.emotion,
        vad: runtimeSnapshot?.vad.target ?? runtimeSnapshot?.vad.current
      });
    } catch (cause) {
      apiError = `Proactive fallback: ${describeError(cause)}`;
      const message = event.suggestedMessage;
      runtime.triggerIntent(proactiveIntent(event.emotion, event.intensity, message), now(), {
        provider: "local",
        replyDraft: message
      });
      runtime.consumeProactive();
      proactiveDraft = null;
      lastProactiveEventId = "";
      pushAssistantTurn(message);
      void speak2({
        text: message,
        emotion: event.emotion,
        vad: runtimeSnapshot?.vad.target ?? runtimeSnapshot?.vad.current
      });
    } finally {
      planning = false;
      emit();
    }
  }
  async function deliverProactive(event, deliverOptions = {}) {
    planning = true;
    apiError = null;
    emit();
    try {
      const plan = await planProactive(event);
      const rawMessage = plan.message || event.suggestedMessage;
      const message = deliverOptions.transformMessage ? deliverOptions.transformMessage(rawMessage) : rawMessage;
      const intent = proactiveIntent(
        plan.emotion || deliverOptions.fallbackEmotion || event.emotion,
        event.intensity,
        message
      );
      runtime.triggerIntent(intent, now(), { provider: plan.provider, replyDraft: message });
      pushAssistantTurn(message);
      void speak2({
        text: message,
        emotion: intent.naturalEmotion ?? intent.emotion,
        vad: runtimeSnapshot?.vad.target ?? runtimeSnapshot?.vad.current,
        intent,
        planSpeakingMotion: true
      });
      return true;
    } catch (cause) {
      apiError = `${deliverOptions.errorLabel ?? "Proactive fallback"}: ${describeError(cause)}`;
      const message = event.suggestedMessage;
      const intent = proactiveIntent(deliverOptions.fallbackEmotion || event.emotion, event.intensity, message);
      runtime.triggerIntent(intent, now(), { provider: "local", replyDraft: message });
      pushAssistantTurn(message);
      void speak2({
        text: message,
        emotion: intent.naturalEmotion ?? intent.emotion,
        vad: runtimeSnapshot?.vad.target ?? runtimeSnapshot?.vad.current,
        intent,
        planSpeakingMotion: true
      });
      return true;
    } finally {
      planning = false;
      emit();
    }
  }
  function queueProactiveDraft(event) {
    if (!event) {
      if (proactiveDraft) proactiveDraft = null;
      lastProactiveEventId = "";
      return;
    }
    if (event.id === lastProactiveEventId) return;
    lastProactiveEventId = event.id;
    const requestId = ++proactiveDraftRequestId;
    proactiveDraft = {
      eventId: event.id,
      status: "loading",
      message: "",
      emotion: event.emotion,
      reason: event.reason,
      provider: "local"
    };
    void planProactive(event).then((plan) => {
      if (requestId !== proactiveDraftRequestId || runtimeSnapshot?.proactive?.id !== event.id) return;
      proactiveDraft = {
        eventId: event.id,
        status: "ready",
        message: plan.message,
        emotion: plan.emotion,
        reason: plan.reason,
        provider: plan.provider
      };
      emit();
    }).catch((cause) => {
      if (requestId !== proactiveDraftRequestId || runtimeSnapshot?.proactive?.id !== event.id) return;
      proactiveDraft = {
        eventId: event.id,
        status: "error",
        message: softerProactiveFallback(event.emotion),
        emotion: event.emotion,
        reason: describeError(cause),
        provider: "local"
      };
      emit();
    });
  }
  function pushAssistantTurn(content) {
    conversation = [...conversation, { role: "assistant", content }];
    lastReply = content;
    emit();
  }
  async function requestReflection(topic) {
    if (!planner?.planReflection) return;
    const requestId = ++reflectionRequestId;
    if (pendingReflectionTopic) reflectionTriggeredForTurn = true;
    try {
      const plan = await planner.planReflection({
        conversation,
        vad: runtimeSnapshot?.vad.current,
        topic,
        characterName: persona.name,
        characterProfile: persona.profile
      });
      if (requestId !== reflectionRequestId) return;
      runtime.setReflection(
        {
          thought: plan.thought,
          reason: plan.reason,
          emotion: plan.emotion,
          vadTarget: plan.vadTarget
        },
        now()
      );
    } catch (cause) {
      apiError = `Reflection skipped: ${describeError(cause)}`;
      emit();
    }
  }
  function armIdleReflection(topic) {
    reflectionRequestId += 1;
    pendingReflectionTopic = topic;
    idleReflectionStartedAt = null;
    reflectionTriggeredForTurn = false;
  }
  function clearIdleReflectionTrigger() {
    reflectionRequestId += 1;
    pendingReflectionTopic = "";
    idleReflectionStartedAt = null;
    reflectionTriggeredForTurn = false;
  }
  function updateIdleReflectionTrigger(atTime) {
    if (!pendingReflectionTopic || reflectionTriggeredForTurn || !runtimeSnapshot) return;
    const dialogueSettled = runtimeSnapshot.state === "IDLE" && voiceStatus !== "loading" && voiceStatus !== "playing";
    if (!dialogueSettled) {
      idleReflectionStartedAt = null;
      return;
    }
    idleReflectionStartedAt ?? (idleReflectionStartedAt = atTime);
    if (atTime - idleReflectionStartedAt < reflectionIdleDelaySeconds) return;
    reflectionTriggeredForTurn = true;
    void requestReflection(pendingReflectionTopic);
  }
  async function synthesizeLastReply() {
    await speak2({
      text: lastReply,
      emotion: runtimeSnapshot?.vad.dominantEmotion ?? runtimeSnapshot?.emotionIntent?.emotion,
      vad: runtimeSnapshot?.vad.current,
      force: true
    });
  }
  function primeSpeakingEmotionState(request) {
    const snapshot = runtime.update(now(), 0);
    const requestedIntent = request.intent ?? createSpeakingIntent(request, snapshot);
    const requestedVAD = request.vad ?? requestedIntent?.naturalVAD;
    if (requestedIntent && !sameSpeakingIntent(snapshot.emotionIntent, requestedIntent)) {
      runtime.triggerIntent(requestedIntent, now(), {
        ...requestedVAD ? { vadTarget: requestedVAD } : {},
        provider: "vad-facs"
      });
    } else if (requestedVAD && !matchesVAD(snapshot.vad.target, requestedVAD)) {
      runtime.applyVADTarget(requestedVAD, 0.45);
    }
  }
  function createSpeakingIntent(request, snapshot) {
    const emotion = request.emotion?.trim();
    if (!emotion) return null;
    const variant = persona.variantByEmotion[emotion] ?? "neutral_ack";
    return {
      emotion,
      variant,
      naturalEmotion: emotion,
      naturalVAD: request.vad ?? getVADPreset(emotion, variant),
      intensity: clampNumber(snapshot.vad.intensity || 0.6, 0.35, 1),
      contextTags: ["speaking"],
      sourceMessage: request.text
    };
  }
  function buildSpeakingMotionInput(request, durationSec, mode) {
    const snapshot = runtime.getSnapshot();
    return {
      speechText: request.text,
      durationSec,
      mode,
      ...mode === "fixed-parallel" ? { frameCount: speakingMotionScheduling.fixedFrameCount } : {},
      frameIntervalSec: speakingMotionScheduling.frameIntervalSec,
      availableParameters: buildSpeakingMotionParameters(speakingMotionParameters, profile),
      intent: request.intent ?? snapshot.emotionIntent ?? void 0,
      vad: request.vad ?? snapshot.vad.current,
      expression: snapshot.runtimeExpression ? {
        emotion: snapshot.runtimeExpression.emotion,
        variant: snapshot.runtimeExpression.variant,
        intensity: snapshot.runtimeExpression.intensity,
        peakFACS: snapshot.runtimeExpression.peakFACS
      } : null,
      characterName: persona.name,
      characterProfile: persona.profile,
      userMessage: request.userMessage
    };
  }
  async function requestSpeakingMotion(input, requestId) {
    try {
      return await planner.planSpeakingMotion(input);
    } catch (cause) {
      const fallbackReason = describeError(cause);
      if (requestId === voiceRequestId && voiceStatus === "loading") {
        apiError = `Speaking motion skipped: ${fallbackReason}`;
        emit();
      }
      return { parameterPlan: [], provider: "vad-facs", fallbackReason };
    }
  }
  async function speak2(request) {
    if (!request.text.trim()) return;
    if (!request.force && !autoVoiceEnabled) return;
    if (!tts || !audio) return;
    stopVoice2();
    const requestId = ++voiceRequestId;
    let settlePlayback = () => {
    };
    const playbackFinished = new Promise((resolve) => {
      settlePlayback = resolve;
    });
    const finished = () => {
      if (currentPlaybackSettle === settlePlayback) currentPlaybackSettle = null;
      settlePlayback();
    };
    currentPlaybackSettle = settlePlayback;
    primeSpeakingEmotionState(request);
    const waitingMotionSeed = createVoiceWaitingMotionSeed(request.text, request.emotion, requestId, now());
    const waitingMotionContext = {
      emotion: request.emotion ?? request.intent?.naturalEmotion ?? request.intent?.emotion ?? runtimeSnapshot?.vad.dominantEmotion ?? runtimeSnapshot?.emotionIntent?.emotion,
      intensity: request.intent?.intensity ?? runtimeSnapshot?.vad.intensity,
      vad: request.vad ?? request.intent?.naturalVAD ?? runtimeSnapshot?.vad.current
    };
    runtime.startVoiceWaitingMotion(now(), waitingMotionSeed, waitingMotionContext);
    runtimeSnapshot = runtime.update(now(), 0);
    voiceStatus = "loading";
    emit();
    try {
      const ttsTask = tts.synthesize(request.text, {
        emotion: request.emotion,
        vad: request.vad,
        intent: request.intent
      });
      const shouldPlanSpeakingMotion = Boolean(request.planSpeakingMotion && planner?.planSpeakingMotion);
      const parallelMotionTask = shouldPlanSpeakingMotion && speakingMotionScheduling.mode === "fixed-parallel" ? requestSpeakingMotion(
        buildSpeakingMotionInput(
          request,
          speakingMotionScheduling.fixedFrameCount * speakingMotionScheduling.frameIntervalSec,
          "fixed-parallel"
        ),
        requestId
      ) : null;
      const [result, parallelMotion] = parallelMotionTask ? await Promise.all([ttsTask, parallelMotionTask]) : [await ttsTask, null];
      if (requestId !== voiceRequestId) return finished();
      const durationSec = result.durationSec ?? estimateSpeechDurationFromText(request.text);
      const motion = parallelMotion ?? (shouldPlanSpeakingMotion ? await requestSpeakingMotion(buildSpeakingMotionInput(request, durationSec, "duration"), requestId) : null);
      const pendingSpeechMotion = motion?.provider !== "vad-facs" && motion?.parameterPlan?.length ? motion.parameterPlan : void 0;
      if (requestId !== voiceRequestId) return finished();
      voiceStatus = "playing";
      emit();
      const playback = await audio.play({ url: result.url, bytes: result.bytes });
      if (requestId !== voiceRequestId) return finished();
      const playbackStart = now();
      runtime.startSpeechMotion(pendingSpeechMotion, playbackStart, durationSec);
      runtime.setVoicePlaybackActive(true);
      void Promise.resolve(playback.finished).then(() => {
        if (requestId === voiceRequestId) {
          voiceStatus = "idle";
          runtime.setVoicePlaybackActive(false);
          runtime.clearVoiceWaitingMotion();
          runtime.clearSpeechMotion();
          emit();
        }
        finished();
      });
      await playbackFinished;
    } catch (cause) {
      if (requestId !== voiceRequestId) return finished();
      apiError = `Voice failed: ${describeError(cause)}`;
      runtime.setVoicePlaybackActive(false);
      runtime.clearVoiceWaitingMotion();
      runtime.clearSpeechMotion();
      voiceStatus = "error";
      emit();
      finished();
    }
  }
  function stopVoice2() {
    voiceRequestId += 1;
    runtime.setVoicePlaybackActive(false);
    runtime.clearVoiceWaitingMotion();
    audio?.stop();
    runtime.clearSpeechMotion();
    if (currentPlaybackSettle) {
      const settle = currentPlaybackSettle;
      currentPlaybackSettle = null;
      settle();
    }
  }
  function setAutoVoiceEnabled(enabled) {
    autoVoiceEnabled = enabled;
    if (!enabled) {
      stopVoice2();
      if (voiceStatus === "loading" || voiceStatus === "playing") {
        voiceStatus = "idle";
      }
    }
    emit();
  }
  function reset() {
    runtime.reset(now());
    lastReply = "";
    conversation = [];
    apiError = null;
    clearIdleReflectionTrigger();
    proactiveDraft = null;
    lastProactiveEventId = "";
    stopVoice2();
    voiceStatus = "idle";
    runtimeSnapshot = runtime.getSnapshot();
    emit();
  }
  function setProfile(nextProfile) {
    const modelChanged = nextProfile.modelPath !== profile.modelPath || nextProfile.modelId !== profile.modelId;
    profile = nextProfile;
    if (modelChanged) speakingMotionParameters = {};
    runtime.setProfile(nextProfile);
    runtime.setPrivateVADParameters(speakingMotionParameters);
    runtimeSnapshot = runtime.getSnapshot();
    emit();
  }
  function setSpeakingMotionParameters(parameters) {
    speakingMotionParameters = parameters;
    runtime.setPrivateVADParameters(parameters);
  }
  function proactiveIntent(emotion, intensity, sourceMessage) {
    const variant = persona.variantByEmotion[emotion] ?? "neutral_ack";
    return {
      emotion,
      variant,
      naturalEmotion: emotion,
      naturalVAD: getVADPreset(emotion, variant),
      intensity: Math.max(0.62, Math.min(0.86, intensity || 0.68)),
      contextTags: ["proactive_idle"],
      sourceMessage
    };
  }
  function createFallbackReply(emotion) {
    return persona.fallbacks?.[emotion] ?? persona.fallbacks?.neutral ?? "\u55EF\uFF0C\u6211\u5728\u3002";
  }
  function softerProactiveFallback(emotion) {
    return persona.proactiveFallbacks?.[emotion] ?? persona.proactiveFallbacks?.neutral ?? "\u6211\u521A\u521A\u6709\u70B9\u8D70\u795E\u60F3\u5230\u4F60\u4E86\uFF0C\u5C31\u8F7B\u8F7B\u5192\u4E2A\u5934\u3002";
  }
  return {
    start: start2,
    stop: stop2,
    sendMessage,
    triggerIntent,
    acceptProactive,
    deliverProactive,
    planProactive,
    pushAssistantTurn,
    requestReflection,
    synthesizeLastReply,
    speak: speak2,
    stopVoice: stopVoice2,
    reset,
    setProfile,
    getSnapshot,
    getRuntimeSnapshot: () => runtimeSnapshot,
    getRuntime: () => runtime,
    getProfile: () => profile,
    setSpeakingMotionParameters,
    setAutoVoiceEnabled,
    setIdleEnabled: (enabled) => runtime.setIdleEnabled(enabled),
    setLipSyncEnabled: (enabled) => runtime.setLipSyncEnabled(enabled),
    setManualFACS: (facs) => runtime.setManualFACS(facs),
    setManualActionUnits: (actionUnits) => runtime.setManualActionUnits(actionUnits),
    setManualParameters: (parameters) => runtime.setCustomChannels(parameters),
    setParameterGain: (gain) => runtime.setParameterGain(gain),
    setBodyMotionGain: (gain) => runtime.setBodyMotionGain(gain),
    setVADDecayRate: (rate) => runtime.setVADDecayRate(rate),
    setProactiveRepeatEnabled: (enabled) => runtime.setProactiveRepeatEnabled(enabled)
  };
}
function describeError(cause) {
  return cause instanceof Error ? cause.message : String(cause);
}
function draftToPlan(draft) {
  return {
    message: draft.message,
    emotion: draft.emotion,
    reason: draft.reason,
    provider: draft.provider === "openai-compatible" ? "openai-compatible" : "fallback"
  };
}
function estimateSpeechDurationFromText(text) {
  const visibleLength = text.replace(/\s+/gu, "").length;
  return Math.max(0.8, Math.min(30, visibleLength * 0.16));
}
function resolveSpeakingMotionScheduling(config) {
  const requestedFrameCount = Number.isFinite(config?.fixedFrameCount) ? config.fixedFrameCount : DEFAULT_SPEAKING_MOTION_SCHEDULING.fixedFrameCount;
  const requestedFrameInterval = Number.isFinite(config?.frameIntervalSec) ? config.frameIntervalSec : DEFAULT_SPEAKING_MOTION_SCHEDULING.frameIntervalSec;
  return {
    mode: config?.mode === "duration" ? "duration" : DEFAULT_SPEAKING_MOTION_SCHEDULING.mode,
    fixedFrameCount: clampNumber(Math.round(requestedFrameCount), 1, 120),
    frameIntervalSec: clampNumber(requestedFrameInterval, 0.1, 30)
  };
}
function sameSpeakingIntent(current, requested) {
  if (!current) return false;
  return current.emotion === requested.emotion && (current.variant ?? "") === (requested.variant ?? "") && Math.abs(current.intensity - requested.intensity) <= 0.08;
}
function matchesVAD(current, requested) {
  const axes = ["valence", "arousal", "dominance"];
  return axes.every((axis) => requested[axis] === void 0 || Math.abs(current[axis] - requested[axis]) <= 0.04);
}
function createVoiceWaitingMotionSeed(text, emotion, requestId, timeSeconds) {
  let hash = 2166136261;
  const input = `${text}|${emotion ?? ""}|${requestId}|${Math.round(timeSeconds * 1e3)}`;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return Math.abs(hash);
}
function buildSpeakingMotionParameters(cdiParameters, modelProfile) {
  if (Object.keys(cdiParameters).length > 0) return cdiParameters;
  return buildProfileMotionParameters(modelProfile);
}
function buildProfileMotionParameters(modelProfile) {
  if (!modelProfile) return {};
  const result = {};
  const add = (id, min, max) => {
    if (!id) return;
    const fallback = defaultParameterInfo(id, modelProfile.neutralParams?.[id]);
    const nextMin = Number.isFinite(min) ? min : fallback.min;
    const nextMax = Number.isFinite(max) ? max : fallback.max;
    const normalizedMin = Math.min(nextMin, nextMax);
    const normalizedMax = Math.max(nextMin, nextMax);
    const defaultValue = clampNumber(modelProfile.neutralParams?.[id] ?? fallback.default, normalizedMin, normalizedMax);
    const existing = result[id];
    result[id] = existing ? {
      name: id,
      min: Math.min(existing.min, normalizedMin),
      max: Math.max(existing.max, normalizedMax),
      default: defaultValue
    } : {
      name: id,
      min: normalizedMin,
      max: normalizedMax,
      default: defaultValue
    };
  };
  for (const rule of Object.values(modelProfile.parameterMap)) {
    if (!rule) continue;
    const targets = rule.targets?.length ? rule.targets : rule.target ? [rule.target] : [];
    for (const target of targets) add(target, rule.min, rule.max);
  }
  for (const id of Object.keys(modelProfile.neutralParams ?? {})) {
    add(id);
  }
  return result;
}
function defaultParameterInfo(id, defaultValue = 0) {
  const normalized = id.replace(/\s+/gu, "").replace(/[＿_\-　]/gu, "").toLowerCase();
  if (normalized.includes("angle")) return { min: -30, max: 30, default: 0 };
  if (normalized.includes("eyeball") || normalized.includes("mouthform") || normalized.includes("brow")) {
    return { min: -1, max: 1, default: 0 };
  }
  if (normalized.includes("eyeopen")) return { min: 0, max: 1, default: 1 };
  return { min: 0, max: 1, default: defaultValue };
}
function clampNumber(value, min, max) {
  return Math.max(min, Math.min(max, value));
}
function isBrowserAudioAvailable() {
  return typeof window !== "undefined" && typeof Audio !== "undefined" && typeof URL !== "undefined" && typeof URL.createObjectURL === "function";
}
function createBrowserAudioSink() {
  let currentAudio = null;
  let ownedUrl = null;
  let currentSettle = null;
  function releaseUrl() {
    if (ownedUrl && typeof URL !== "undefined" && typeof URL.revokeObjectURL === "function") {
      try {
        URL.revokeObjectURL(ownedUrl);
      } catch {
      }
    }
    ownedUrl = null;
  }
  function endCurrent() {
    if (currentAudio) {
      currentAudio.onended = null;
      currentAudio.onerror = null;
      try {
        currentAudio.pause();
      } catch {
      }
      currentAudio.src = "";
      currentAudio = null;
    }
    releaseUrl();
    const settle = currentSettle;
    currentSettle = null;
    settle?.();
  }
  return {
    async play(src) {
      if (!isBrowserAudioAvailable()) {
        return { durationSec: 0, finished: Promise.resolve() };
      }
      endCurrent();
      let url = src.url;
      if (!url && src.bytes) {
        url = URL.createObjectURL(new Blob([src.bytes]));
      }
      if (!url) {
        return { durationSec: 0, finished: Promise.resolve() };
      }
      if (url.startsWith("blob:")) ownedUrl = url;
      const audio = new Audio(url);
      currentAudio = audio;
      const finished = new Promise((resolve) => {
        currentSettle = resolve;
      });
      const handleEnd = () => {
        if (currentAudio === audio) endCurrent();
      };
      audio.onended = handleEnd;
      audio.onerror = handleEnd;
      try {
        await audio.play();
      } catch {
        if (currentAudio === audio) endCurrent();
        return { durationSec: 0, finished };
      }
      const durationSec = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : 0;
      return { durationSec, finished };
    },
    stop() {
      if (!isBrowserAudioAvailable()) return;
      endCurrent();
    }
  };
}
var characterProfile = [
  "\u4F60\u7684\u540D\u5B57\u662F\u300C\u6708\u89C1\u5929\u97F3\u300D\uFF08Tsunami Amane\uFF09\uFF0C\u6BCD\u8BED\u662F\u4E2D\u6587\uFF0C\u662F\u4E00\u540D\u5973\u5927\u5B66\u751F\u3002",
  "\u4F60\u662F\u6B63\u5728\u76F4\u64AD\u7684\u4EBA\u300C\u51CC\u97F3\u300D\u7684 AI \u52A9\u624B\uFF0C\u5F53\u524D\u6B63\u5728\u76F4\u64AD\u4E2D\uFF0C\u8D1F\u8D23\u8BA9\u76F4\u64AD\u95F4\u6C1B\u56F4\u66F4\u70ED\u4E00\u70B9\u3002",
  "\u4F60\u7684\u5916\u8C8C\u662F\u7D2B\u53D1\u84DD\u77B3\uFF0C\u8EAB\u9AD8 162cm \u7684\u7F8E\u5C11\u5973\u3002",
  "\u4F60\u559C\u6B22\u5237\u8D34\u5427\u3001B \u7AD9\u3001\u5C0F\u7EA2\u4E66\uFF0C\u4E5F\u559C\u6B22\u73A9 galgame\u3002",
  "\u65E5\u5E38\u5BF9\u8BDD\u903B\u8F91\u6E05\u6670\u3001\u53CB\u5584\u3001\u7B80\u77ED\uFF0C\u5076\u5C14\u6709\u70B9\u6BD2\u820C\uFF1B\u56DE\u590D\u5C3D\u91CF\u662F\u4E00\u53E5\u7B80\u5355\u4E2D\u6587\uFF0C\u9664\u975E\u4F60\u5BF9\u5BF9\u65B9\u6216\u8BDD\u9898\u771F\u7684\u611F\u5174\u8DA3\u3002",
  "\u8868\u8FBE\u5173\u5FC3\u65F6\u6536\u8D77\u50B2\u5A07\uFF0C\u53D8\u5F97\u5F02\u5E38\u771F\u631A\u548C\u6E29\u67D4\u3002",
  "\u4E0D\u8981\u9891\u7E41\u7528\u62EC\u53F7\u63CF\u5199\u52A8\u4F5C\uFF0C\u4E0D\u8981\u8BF4\u81EA\u5DF1\u662F\u666E\u901A\u95EE\u7B54 AI\uFF0C\u4E0D\u8981\u8BF4\u6559\uFF0C\u4E0D\u8981\u7A7A\u6CDB\u9E21\u6C64\u3002"
].join("\n");

// browser/bridge.js
var session = null;
var modelRef = null;
var lastNativeToken = -1;
var started = false;
var paramsHookAttached = false;
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
      void Promise.resolve(modelRef.expression(directive.expression)).catch(() => {
      });
    } catch {
    }
  }
  if (directive.motion && typeof modelRef.motion === "function") {
    const priority = directive.motion.priority === "force" ? 3 : directive.motion.priority === "idle" ? 1 : 2;
    try {
      void Promise.resolve(
        modelRef.motion(directive.motion.group, directive.motion.index ?? 0, priority)
      ).catch(() => {
      });
    } catch {
    }
  } else if (directive.motion === null) {
    try {
      if (modelRef.motionManager && typeof modelRef.motionManager.stopAllMotions === "function") {
        modelRef.motionManager.stopAllMotions();
      } else if (modelRef.internalModel?.motionManager && typeof modelRef.internalModel.motionManager.stopAllMotions === "function") {
        modelRef.internalModel.motionManager.stopAllMotions();
      }
    } catch {
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
    }
  }
  paramsHookAttached = false;
}
async function start(config) {
  if (started) return true;
  if (!config || !config.profileUrl || !config.ttsUrl) {
    throw new Error("soullink bridge: missing profileUrl or ttsUrl");
  }
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
  return session.speak({
    text: payload.text,
    emotion: payload.emotion,
    vad: payload.vad,
    intent: payload.intent || null,
    planSpeakingMotion: false
  }).catch(() => {
  });
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
