// Soullink Emotion SDK local sidecar.
// Runs the SDK's Embedding emotion classifier and a DashScope TTS provider so
// the QtWebEngine front-end never has to hold API keys.
import { createServer } from "node:http";
import { readFile, writeFile } from "node:fs/promises";
import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import {
  EmbeddingMessageClassifier
} from "@soullink-emotion/classifier-embedding";
import { FileEmbeddingVectorCache } from "@soullink-emotion/classifier-embedding/node";

function parseArgs(argv) {
  const args = { port: 0, config: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--port" && argv[i + 1]) {
      args.port = Number.parseInt(argv[i + 1], 10);
      i += 1;
    } else if (argv[i] === "--config" && argv[i + 1]) {
      args.config = argv[i + 1];
      i += 1;
    }
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
const configPath = resolve(args.config || "soullink-config.json");
let config = {};
try {
  const raw = await readFile(configPath, "utf8");
  config = JSON.parse(raw.replace(/^\uFEFF/, ""));
} catch (error) {
  console.error("[soullink] cannot read config:", error.message);
  process.exit(1);
}

const embeddingCfg = config.embedding || {};
const ttsCfg = config.tts || {};
const cacheDir = resolve(config.cache_dir || "cache/embeddings");
await mkdir(cacheDir, { recursive: true });

// ---- Embedding provider (DashScope) ----
// The SDK's classifier keeps the Top-K voting / caching / fallback logic;
// only the wire calls are ours so the configured embedding model is used.
class DashScopeEmbeddingProvider {
  constructor(options) {
    this.baseURL = (options.baseURL || "https://dashscope.aliyuncs.com/compatible-mode/v1").replace(/\/+$/, "");
    this.apiKey = options.apiKey || "";
    this.model = options.model || "text-embedding-v3";
    this.timeoutMs = options.timeoutMs || 120_000;
  }

  get config() {
    return {
      configured: Boolean(this.apiKey),
      baseURL: this.baseURL,
      model: this.model,
      timeoutMs: this.timeoutMs
    };
  }

  isConfigured() {
    return Boolean(this.apiKey);
  }

  getCacheKey() {
    return `dashscope:${this.baseURL}:${this.model}:v1`;
  }

  async _call(input) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      const response = await fetch(this.baseURL + "/embeddings", {
        method: "POST",
        headers: {
          Authorization: "Bearer " + this.apiKey,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          model: this.model,
          input,
          encoding_format: "float"
        }),
        signal: controller.signal
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Embedding API failed with ${response.status}: ${text}`);
      }
      const data = await response.json();
      return [...data.data]
        .sort((a, b) => a.index - b.index)
        .map((item) => item.embedding);
    } finally {
      clearTimeout(timer);
    }
  }

  async embed(text) {
    const results = await this._call(text);
    return results[0] ?? [];
  }

  batchEmbed(texts) {
    return this._call(texts);
  }
}

const embeddingProvider = new DashScopeEmbeddingProvider({
  baseURL: embeddingCfg.base_url,
  apiKey: embeddingCfg.api_key || "",
  model: embeddingCfg.model || "text-embedding-v3",
  timeoutMs: 120_000
});

const classifier = new EmbeddingMessageClassifier(embeddingProvider, {
  similarityThreshold: 0.61,
  topK: 5,
  queryCacheSize: 256,
  // DashScope embeddings cap batch size at 10 per request.
  initializationBatchSize: Math.min(10, Number(embeddingCfg.init_batch_size) || 10),
  embeddingCache: new FileEmbeddingVectorCache({ directory: cacheDir }),
  logger: {
    debug: (msg) => console.log("[soullink]", msg),
    warn: (msg) => console.warn("[soullink]", msg),
    error: (msg, err) => console.error("[soullink]", msg, err)
  }
});

let initializationPromise = null;
function ensureClassifierReady() {
  if (!initializationPromise) {
    initializationPromise = classifier.initialize().catch((error) => {
      initializationPromise = null;
      throw error;
    });
  }
  return initializationPromise;
}

// Warm the classifier in the background so the first chat reaction is fast.
ensureClassifierReady().catch((error) => {
  console.error("[soullink] background classifier init failed:", error.message);
});

// ---- DashScope non-streaming TTS ----
async function synthesizeTts(text, voice) {
  const apiKey = ttsCfg.api_key || "";
  if (!apiKey) throw new Error("TTS api_key is not configured");
  const baseUrl = (ttsCfg.base_url || "https://dashscope.aliyuncs.com/api/v1").replace(/\/+$/, "");
  const model = ttsCfg.model || "qwen-tts";
  const body = {
    model,
    input: {
      text,
      voice: voice || ttsCfg.voice || "Cherry",
      language_type: ttsCfg.language_type || "Chinese"
    }
  };
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 120_000);
  try {
    const response = await fetch(baseUrl + "/services/aigc/multimodal-generation/generation", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + apiKey,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body),
      signal: controller.signal
    });
    if (!response.ok) {
      const detail = await response.text().catch(() => "");
      throw new Error(`TTS HTTP ${response.status}: ${detail.slice(0, 300)}`);
    }
    const data = await response.json();
    const audioUrl = data?.output?.audio?.url;
    if (!audioUrl) {
      throw new Error("TTS response has no output.audio.url");
    }
    const audioResponse = await fetch(audioUrl, { signal: controller.signal });
    if (!audioResponse.ok) {
      throw new Error(`TTS download HTTP ${audioResponse.status}`);
    }
    const buffer = await audioResponse.arrayBuffer();
    const mime =
      audioResponse.headers.get("content-type")?.split(";")[0].trim() || "audio/wav";
    const base64 = Buffer.from(buffer).toString("base64");
    return { audio_b64: base64, mime };
  } finally {
    clearTimeout(timer);
  }
}

function sendJson(res, status, payload, extraHeaders = {}) {
  const body = JSON.stringify(payload);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    ...extraHeaders
  });
  res.end(body);
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString("utf8");
  try {
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

const server = createServer(async (req, res) => {
  if (req.method === "OPTIONS") {
    sendJson(res, 204, {});
    return;
  }
  const url = new URL(req.url || "/", "http://127.0.0.1");
  try {
    if (req.method === "GET" && (url.pathname === "/" || url.pathname === "/health")) {
      sendJson(res, 200, {
        ok: true,
        service: "soullink-local",
        classifierInitialized: classifier.isInitialized,
        embeddingModel: embeddingProvider.config.model,
        ttsModel: ttsCfg.model || "qwen3-tts-flash"
      });
      return;
    }

    if (req.method === "POST" && url.pathname === "/classify") {
      const body = await readBody(req);
      const message = typeof body.message === "string" ? body.message.trim() : "";
      if (!message) {
        sendJson(res, 400, { error: "message is required" });
        return;
      }
      await ensureClassifierReady();
      const detail = await classifier.classifyDetailed(message);
      sendJson(res, 200, {
        intent: detail.intent,
        source: detail.source,
        confidence: detail.confidence,
        emotionScores: detail.emotionScores,
        naturalVAD: detail.naturalVAD,
        cacheHit: detail.cacheHit
      });
      return;
    }

    if (req.method === "POST" && url.pathname === "/tts") {
      const body = await readBody(req);
      const text = typeof body.text === "string" ? body.text.trim() : "";
      if (!text) {
        sendJson(res, 400, { error: "text is required" });
        return;
      }
      const result = await synthesizeTts(text, typeof body.voice === "string" ? body.voice : "");
      sendJson(res, 200, result);
      return;
    }

    sendJson(res, 404, { error: "not found" });
  } catch (error) {
    console.error("[soullink] request failed:", error);
    sendJson(res, 500, { error: String(error && error.message ? error.message : error) });
  }
});

server.listen(args.port, "127.0.0.1", () => {
  const port = server.address().port;
  console.log(`SOULLINK_READY ${port}`);
});

function shutdown() {
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(0), 500).unref();
}
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
