#!/usr/bin/env node
"use strict";
/* Cross-verify helper: run the JS AER-1 core check on a single receipt file.
 * Usage: node check_one.js <path-to-receipt.json>
 * Prints: {"verdict":"pass"|"fail","reasons":[...]}
 *
 * Runs the full runner judgment: check() plus checkVersionAndBinding(),
 * mirroring cross_verify.py's Python runner.
 *
 * Builds a driver script from the real conformance.cjs verifier (library
 * portion only, no vendored copy) plus a small main, writes it to a temp
 * file, and executes it. This guarantees we test the actual bundled
 * checker, not a duplicate.
 */
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");

const file = process.argv[2];
if (!file) { console.error("usage: node check_one.js <receipt.json>"); process.exit(2); }

const kitDir = path.join(__dirname, "..", "..", "base");
const src = fs.readFileSync(path.join(kitDir, "conformance.cjs"), "utf8");
const marker = "function globJson";
const cut = src.indexOf(marker);
if (cut === -1) { console.error("runner marker not found in conformance.cjs"); process.exit(2); }
const lib = src.slice(0, cut);

const driver = lib + `
"use strict";
const fs2 = require("fs");
const target = ${JSON.stringify(path.resolve(file))};
let receipt;
let text;
try {
  text = fs2.readFileSync(target, "utf8");
  receipt = JSON.parse(text);
} catch (e) {
  console.log(JSON.stringify({ verdict: "fail", reasons: ["unreadable JSON: " + e.message] }));
  process.exit(0);
}
let reasons;
try {
  reasons = check(receipt).concat(checkVersionAndBinding(receipt).failures);
  // Section 6 duplicate member name rejection (draft -19): JSON.parse
  // erases the signal, so scan the text as received.
  const dupName = findDuplicateMemberName(text);
  if (dupName !== null) reasons.push("duplicate member name: " + dupName);
} catch (e) {
  console.log(JSON.stringify({ verdict: "fail", reasons: ["checker threw: " + e.message] }));
  process.exit(0);
}
console.log(JSON.stringify({ verdict: reasons.length === 0 ? "pass" : "fail", reasons }));
`;

const tmp = path.join(os.tmpdir(), "aer1-check-one-" + process.pid + ".js");
fs.writeFileSync(tmp, driver);
try {
  const out = execFileSync("node", [tmp], { encoding: "utf8", timeout: 30000 });
  process.stdout.write(out);
} finally {
  try { fs.unlinkSync(tmp); } catch (e) { /* best effort */ }
}
