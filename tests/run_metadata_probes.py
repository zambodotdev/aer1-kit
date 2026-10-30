#!/usr/bin/env python3
"""Pin the Section 6 step 4 metadata recomputation (kit -24).

Every mutated fixture in tests/metadata-probes/ MUST fail check()
with the metadata mismatch reason; the two controls (the corpus
vector valid/real-04.json itself and Laurent Lemonnier's unmodified
composition receipt) MUST pass. Exit 0 when all expectations hold.
Standard library only.
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / "metadata-probes"
REASON = "metadata_hash does not match the recomputed metadata block"

spec = importlib.util.spec_from_file_location(
    "aer1_conformance", ROOT / "base" / "conformance.py")
conf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conf)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    problems = []
    controls = [ROOT / "base" / "test-vectors" / "valid" / "real-04.json",
                FIXTURES / "laurent-receipt.json"]
    for path in controls:
        fails = conf.check(load(path))
        status = "PASS" if not fails else "FAIL"
        print(f"[control] {path.name}: {status}")
        if fails:
            problems.append(f"{path.name}: control must pass, got {fails}")
    probes = sorted(p for p in FIXTURES.glob("*.json")
                    if p.name != "laurent-receipt.json")
    if len(probes) != 8:
        problems.append(f"expected 8 probe fixtures, found {len(probes)}")
    for path in probes:
        fails = conf.check(load(path))
        ok = REASON in fails
        print(f"[probe] {path.name}: {'FAIL (metadata)' if ok else 'PROBLEM'}"
              f" -> {fails}")
        if not ok:
            problems.append(
                f"{path.name}: must fail with {REASON!r}, got {fails}")
    if problems:
        print("METADATA PROBES FAILED:")
        for p in problems:
            print(" -", p)
        return 1
    print("METADATA PROBES OK: 2 controls pass, 8 probes fail on the "
          "metadata recomputation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
