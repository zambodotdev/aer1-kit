#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";

const here = path.dirname(fileURLToPath(import.meta.url));
const hash = bytes => createHash("sha256").update(bytes).digest();
const read = file => fs.readFileSync(path.join(here, file));
const manifest = JSON.parse(read("index.json"));
function walk(dir) {
  return fs.readdirSync(path.join(here, dir), { withFileTypes: true }).flatMap(e =>
    e.isDirectory() ? walk(`${dir}/${e.name}`) : e.name.endsWith(".json") ? [`${dir}/${e.name}`] : []);
}
const paths = [...walk("base"), "workflow-merkle-seq-output-v1.json"].sort();
const entries = paths.map(file => {
  const raw = read(file), value = JSON.parse(raw);
  const vectors = Array.isArray(value.vectors) ? value.vectors.length : 1;
  const checks = vectors + (file === "base/merkle-vectors.json"
    ? value.vectors.filter(v => Object.hasOwn(v, "expected_workflow_verdict")).length : 0);
  return { path: file, sha256: hash(raw).toString("hex"), vectors, checks };
});
if (JSON.stringify(entries) !== JSON.stringify(manifest.files)) throw new Error("Evaluated file inventory, bytes or counts differ from index");
const vectors = entries.reduce((n, e) => n + e.vectors, 0);
const checks = entries.reduce((n, e) => n + e.checks, 0);
const digest = hash(Buffer.from(entries.map(e => `${e.path}\0${e.sha256}\n`).join(""), "utf8")).toString("hex");
if (manifest.vector_count !== vectors || manifest.check_count !== checks || manifest.evaluated_set_digest !== `sha256:${digest}`) throw new Error("Evaluated-set record mismatch");
const base = spawnSync(process.execPath, [path.join(here, "base/conformance.cjs")], { encoding: "utf8" });
if (base.status !== 0 || !base.stdout.includes("CONFORMANCE OK")) throw new Error(base.stdout + base.stderr);
const baseChecks = (base.stdout.match(/^\[/gm) ?? []).length;
process.stdout.write(base.stdout.replace("CONFORMANCE OK: all vectors behave as expected.", "Base expectations passed."));
const workflows = JSON.parse(read("workflow-merkle-seq-output-v1.json")).vectors;
for (const v of workflows) {
  let level = v.steps.map((step, index) => {
    if (step.seq !== index + 1) throw new Error("Noncontiguous sequence");
    let leaf;
    if (v.merkle_version === "receipt-id-v0") leaf = step.receipt_id;
    else if (v.merkle_version === "seq-output-v1") {
      const hex = step.output_hash.replace(/^sha256:/, "").toLowerCase();
      if (!/^[0-9a-f]{64}$/.test(hex)) throw new Error("Invalid output hash");
      leaf = `${index + 1}:${hex}`;
    } else throw new Error("Unsupported version");
    return hash(Buffer.from(leaf, "utf8"));
  });
  while (level.length > 1) {
    if (level.length % 2) level.push(level.at(-1));
    level = Array.from({ length: level.length / 2 }, (_, i) => hash(Buffer.concat([level[i * 2], level[i * 2 + 1]])));
  }
  if (!level.length || v.expected_verdict !== "valid" || level[0].toString("hex") !== v.merkle_root) throw new Error(`${v.name}: root mismatch`);
  console.log(`[workflow-root] ${v.name}: PASS`);
}
if (baseChecks + workflows.length !== checks) throw new Error("Actual evaluated check count differs from manifest");
console.log(`CONFORMANCE OK: ${vectors} vectors, ${checks} checks, sha256:${digest}`);
