#!/usr/bin/env node
// Pin the Section 6 step 4 metadata recomputation (kit -24), JS side.
// base/conformance.cjs is a script whose last line runs main(); this
// driver loads a copy with that line swapped for an export of check()
// and applies the same expectations as run_metadata_probes.py. Exit 0
// when all expectations hold.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(here);
const fixtures = path.join(here, "metadata-probes");
const REASON = "metadata_hash does not match the recomputed metadata block";

let src = fs.readFileSync(path.join(root, "base", "conformance.cjs"), "utf8");
if (!/process\.exitCode = main\(\);?\s*$/.test(src)) {
  console.error("cannot locate the main() invocation in base/conformance.cjs");
  process.exit(1);
}
src = src.replace(/process\.exitCode = main\(\);?\s*$/,
                  "module.exports = { check };\n");
const tmp = path.join(os.tmpdir(), "aer1-conformance-probe.cjs");
fs.writeFileSync(tmp, src);
const { check } = createRequire(import.meta.url)(tmp);

const load = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const problems = [];
const controls = [path.join(root, "base", "test-vectors", "valid", "real-04.json"),
                  path.join(fixtures, "laurent-receipt.json")];
for (const p of controls) {
  const fails = check(load(p));
  console.log(`[control] ${path.basename(p)}: ${fails.length ? "FAIL" : "PASS"}`);
  if (fails.length) problems.push(`${path.basename(p)}: control must pass, got ${JSON.stringify(fails)}`);
}
const probes = fs.readdirSync(fixtures).filter((n) => n.endsWith(".json") && n !== "laurent-receipt.json").sort();
if (probes.length !== 8) problems.push(`expected 8 probe fixtures, found ${probes.length}`);
for (const name of probes) {
  const fails = check(load(path.join(fixtures, name)));
  const ok = fails.includes(REASON);
  console.log(`[probe] ${name}: ${ok ? "FAIL (metadata)" : "PROBLEM"} -> ${JSON.stringify(fails)}`);
  if (!ok) problems.push(`${name}: must fail with ${JSON.stringify(REASON)}, got ${JSON.stringify(fails)}`);
}
if (problems.length) {
  console.log("METADATA PROBES FAILED:");
  for (const p of problems) console.log(" -", p);
  process.exit(1);
}
console.log("METADATA PROBES OK: 2 controls pass, 8 probes fail on the metadata recomputation.");
