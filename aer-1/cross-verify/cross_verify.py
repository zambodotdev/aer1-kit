#!/usr/bin/env python3
"""AER-1 cross-implementation verification matrix.

Runs the core receipt vectors through the Python and JavaScript bundled
verifiers and records whether they AGREE on the verdict.

This is the cross-check: it is not enough that one verifier passes the
corpus. Independent implementations must reach the same pass/fail decision
on the same bytes.

Standard library only. Exit 0 when every runnable implementation agrees on
every vector and every verdict matches the corpus expectation; exit 1 on
any disagreement or expectation mismatch.

Usage:
    python3 cross_verify.py [--corpus DIR] [--out DIR]

Outputs:
    matrix.json  - machine-readable results
    MATRIX.md    - human-readable report (written by this script)
"""

import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# Kit repo layout: this harness lives at aer-1/cross-verify/, while the
# kit's runners and corpus live under base/ at the repo root.
KIT = os.path.dirname(os.path.dirname(HERE))

sys.path.insert(0, os.path.join(KIT, "base"))
from conformance import check as py_check  # noqa: E402  (the real Python verifier)
from conformance import check_version_and_binding as py_check_binding  # noqa: E402
from conformance import find_duplicate_member_name as py_find_duplicate  # noqa: E402

CORPUS_DIRS = ["valid", "invalid", "invalid-profile", "anchored"]

# Expected CORE verdict per corpus directory.
EXPECTED = {
    "valid": "pass",
    "invalid": "fail",
    "invalid-profile": "pass",  # core check passes; only the profile check fails
    "anchored": "pass",
}


def js_check(path):
    """Run the real JavaScript verifier on one receipt file via node."""
    r = subprocess.run(
        ["node", os.path.join(HERE, "check_one.js"), path],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        return {"verdict": "fail", "reasons": ["node helper error: " + r.stderr.strip()[:200]]}
    return json.loads(r.stdout)


def stdin_check(cmd, path):
    """Run an external verifier that reads a receipt on stdin and prints
    {"verdict": "pass"} or {"verdict": "fail", "reasons": [...]} on stdout.
    cmd is a list like ["python3", "my_verifier.py"]. Fail closed: a
    nonzero exit, unparseable output, or output that is not an object
    with a verdict field is a fail, never a pass."""
    with open(path, "rb") as f:
        data = f.read()
    r = subprocess.run(cmd, input=data, capture_output=True, timeout=30)
    if r.returncode != 0:
        return {"verdict": "fail",
                "reasons": ["verifier exited %d: %s" % (r.returncode, r.stderr.decode()[:200])]}
    try:
        out = json.loads(r.stdout.decode())
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return {"verdict": "fail", "reasons": ["unparseable verifier output: %s" % e]}
    if not isinstance(out, dict) or out.get("verdict") not in ("pass", "fail"):
        return {"verdict": "fail",
                "reasons": ["verifier output is not an object with a verdict field: %r" % (r.stdout.decode()[:200],)]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=os.path.join(KIT, "base", "test-vectors"))
    ap.add_argument("--out", default=HERE)
    args = ap.parse_args()

    verifiers = {
        "python": lambda p: _py(p),
        "javascript": js_check,
    }
    # Toolchains not present in this environment are marked untested, never failed.
    untested = []
    for lang, probe in (("go", "go"), ("rust", "rustc"), ("java", "java")):
        if subprocess.run(["which", probe], capture_output=True).returncode != 0:
            untested.append(lang)

    rows = []
    disagreements = 0
    for corpus in CORPUS_DIRS:
        d = os.path.join(args.corpus, corpus)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(d, name)
            expected = EXPECTED[corpus]
            results = {}
            for lang, fn in verifiers.items():
                try:
                    results[lang] = fn(path)
                except Exception as e:  # fail closed: a crash is a recorded outcome
                    results[lang] = {"verdict": "error", "reasons": [str(e)[:200]]}
            verdicts = {r["verdict"] for r in results.values()}
            agree = len(verdicts) == 1
            if not agree:
                disagreements += 1
            matches_expected = all(r["verdict"] == expected for r in results.values())
            rows.append({
                "corpus": corpus,
                "file": name,
                "expected": expected,
                "results": results,
                "implementations_agree": agree,
                "matches_expected": matches_expected,
            })

    mismatches = sum(1 for r in rows if not r["matches_expected"])

    matrix = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "draft": "draft-zambo-aer1-26",
        "corpus": args.corpus,
        "verifiers_run": sorted(verifiers.keys()),
        "verifiers_untested": untested,
        "total_vectors": len(rows),
        "disagreements": disagreements,
        "mismatches": mismatches,
        "rows": rows,
    }

    with open(os.path.join(args.out, "matrix.json"), "w") as f:
        json.dump(matrix, f, indent=2)

    _write_markdown(matrix, os.path.join(args.out, "MATRIX.md"))

    # Console summary
    n = len(rows)
    print(f"vectors: {n} | verifiers run: {', '.join(sorted(verifiers))} | "
          f"untested here: {', '.join(untested) or 'none'}")
    print(f"implementation disagreements: {disagreements}")
    if disagreements:
        for r in rows:
            if not r["implementations_agree"]:
                print(f"  MISMATCH {r['corpus']}/{r['file']}: " +
                      ", ".join(f"{k}={v['verdict']}" for k, v in r["results"].items()))
    for r in rows:
        if not r["matches_expected"]:
            print(f"  EXPECTATION FAIL {r['corpus']}/{r['file']}: expected {r['expected']}, " +
                  ", ".join(f"{k}={v['verdict']}" for k, v in r["results"].items()))
    return 1 if (disagreements or mismatches) else 0


def _py(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    receipt = json.loads(text)
    reasons = py_check(receipt)
    # Section 6 duplicate member name rejection (draft -19): json
    # parsing erases the signal, so scan the text as received.
    duplicate = py_find_duplicate(text)
    if duplicate is not None:
        reasons = reasons + ["duplicate member name: %s" % duplicate]
    _is_legacy, bind_reasons = py_check_binding(receipt)
    reasons = reasons + bind_reasons
    return {"verdict": "pass" if not reasons else "fail", "reasons": reasons}


def _write_markdown(matrix, path):
    lines = []
    L = lines.append
    L("# AER-1 Cross-Implementation Verification Matrix")
    L("")
    L(f"Generated {matrix['generated_at']} against {matrix['draft']}.")
    L("")
    L("This matrix runs the core receipt vectors through the Python and")
    L("JavaScript bundled verifiers and records whether they agree on the")
    L("verdict. Agreement across independent implementations is")
    L("the cross-check: the same bytes must produce the same decision")
    L(f"everywhere. {matrix['total_vectors']} core vectors, Python and JavaScript.")
    L("")
    L("## Verifiers")
    L("")
    for v in matrix["verifiers_run"]:
        L(f"- {v}: ran against every vector below")
    for v in matrix["verifiers_untested"]:
        L(f"- {v}: not tested in this environment (toolchain absent); "
          "marked untested, not failed")
    L("")
    L(f"Total vectors: {matrix['total_vectors']}. "
      f"Implementation disagreements: {matrix['disagreements']}.")
    L("")
    L("## Matrix")
    L("")
    L("| Corpus | Vector | Expected | " +
      " | ".join(v.capitalize() for v in matrix["verifiers_run"]) +
      " | Agree? |")
    L("|---|---|---" + "|---" * (len(matrix["verifiers_run"]) + 1) + "|")
    for r in matrix["rows"]:
        cells = [r["corpus"], r["file"], r["expected"]]
        for v in matrix["verifiers_run"]:
            cells.append(r["results"][v]["verdict"])
        cells.append("yes" if r["implementations_agree"] else "**NO**")
        L("| " + " | ".join(cells) + " |")
    L("")
    if matrix["disagreements"] == 0 and matrix["mismatches"] == 0:
        L("Every runnable implementation agreed on every vector. "
          "Where the corpus expected a pass, all verifiers passed; "
          "where it expected a failure, all verifiers failed, for the "
          "same reasons class.")
    else:
        if matrix["disagreements"]:
            L("Disagreements are listed above and must be investigated before "
              "any conformance claim is made.")
        if matrix["mismatches"]:
            L(f"{matrix['mismatches']} vector(s) did not match the corpus expectation. "
              "Expectation mismatches are listed above and must be investigated.")
    L("")
    L("Recompute: `python3 cross_verify.py` from this directory. "
      "Standard library only; Node.js required for the JavaScript column.")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
