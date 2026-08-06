// Generate soullink.profile.json for Live2D models in ../model.
// Usage:
//   node generate-profile.mjs --model yumi [--force]
//   node generate-profile.mjs [--force]          (all models)
//   node generate-profile.mjs --root <modelsRoot> [--model <id>] [--force]
import { readdirSync, existsSync } from "node:fs";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { Live2DProfileAutoGenerator } from "@soullink-emotion/profile-generator";

function parseArgs(argv) {
  const args = { model: null, force: false, root: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--model" && argv[i + 1]) {
      args.model = argv[i + 1];
      i += 1;
    } else if (argv[i] === "--force") {
      args.force = true;
    } else if (argv[i] === "--root" && argv[i + 1]) {
      args.root = argv[i + 1];
      i += 1;
    }
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
const modelsRoot = args.root
  ? resolve(args.root)
  : resolve(import.meta.dirname, "../model");

function modelDirs() {
  if (args.model) return [args.model];
  return readdirSync(modelsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => existsSync(resolve(modelsRoot, name, "model.json")));
}

const generator = new Live2DProfileAutoGenerator({
  modelsRoot,
  modelsBaseUrl: "/model",
  useConfiguredOpenAI: false
});

// 生成器只按表情文件名启发式映射少数情绪（happy/excited/surprised/angry/sad/shy），
// 这里把同一张脸的其他等价情绪别名也补进 expressionMap，让情绪反应覆盖更全。
// 只有 catalog 里真实存在的表情名才会被引用。
const EXPRESSION_ALIASES = [
  { name: "happy", emotions: ["affectionate"] },
  { name: "star", emotions: ["curious"] },
  { name: "tear", emotions: ["teary", "anxiety", "tired", "concerned"] },
  { name: "angry", emotions: ["anger"] },
  { name: "surprised", emotions: ["confused"] }
];

async function extendExpressionMap(profilePath) {
  let profile;
  try {
    profile = JSON.parse(await readFile(profilePath, "utf8"));
  } catch {
    return;
  }
  const catalogNames = new Set(
    (profile.nativeAnimations?.expressions ?? []).map((entry) => entry.name)
  );
  const expressionMap = profile.expressionMap ?? {};
  let changed = false;
  for (const alias of EXPRESSION_ALIASES) {
    if (!catalogNames.has(alias.name)) continue;
    for (const emotion of alias.emotions) {
      if (expressionMap[emotion] === undefined) {
        expressionMap[emotion] = alias.name;
        changed = true;
      }
    }
  }
  if (!changed) return;
  profile.expressionMap = expressionMap;
  await writeFile(profilePath, JSON.stringify(profile, null, 2) + "\n", "utf8");
}

const results = [];
for (const modelDir of modelDirs()) {
  const profilePath = resolve(modelsRoot, modelDir, "soullink.profile.json");
  if (existsSync(profilePath) && !args.force) {
    results.push({
      model: modelDir,
      status: "skipped",
      reason: "profile exists (use --force to regenerate)"
    });
    continue;
  }
  try {
    const result = await generator.ensure({
      modelDir,
      force: args.force
    });
    results.push({
      model: modelDir,
      status: "ok",
      generated: result.generated,
      reason: result.reason,
      provider: result.provider,
      profileUrl: result.profileUrl,
      notes: result.notes.slice(0, 5)
    });
    if (result.generated) {
      await extendExpressionMap(profilePath);
    }
  } catch (error) {
    results.push({
      model: modelDir,
      status: "error",
      error: String(error && error.message ? error.message : error)
    });
  }
}

console.log(JSON.stringify(results, null, 2));
if (results.some((r) => r.status === "error")) {
  process.exit(1);
}
