// Generate soullink.profile.json for Live2D models in ../model.
// Usage:
//   node generate-profile.mjs --model yumi [--force]
//   node generate-profile.mjs [--force]          (all models)
//   node generate-profile.mjs --root <modelsRoot> [--model <id>] [--force]
import { readdirSync, existsSync } from "node:fs";
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
