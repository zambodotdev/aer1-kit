#!/usr/bin/env python3
"""Run the complete served corpus. Python standard library only."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).digest()


def main():
    manifest = json.loads((HERE / "index.json").read_bytes())
    paths = sorted(p.relative_to(HERE).as_posix() for p in (HERE / "base").rglob("*.json"))
    paths.append("workflow-merkle-seq-output-v1.json")
    paths.sort()
    if paths != [f["path"] for f in manifest["files"]]:
        raise ValueError("Evaluated file inventory differs from index")
    entries = []
    vectors = checks = 0
    for name in paths:
        raw = (HERE / name).read_bytes()
        value = json.loads(raw)
        n = len(value["vectors"]) if "vectors" in value else 1
        c = n + (sum("expected_workflow_verdict" in v for v in value["vectors"])
                 if name == "base/merkle-vectors.json" else 0)
        entry = {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "vectors": n, "checks": c}
        entries.append(entry)
        vectors += n
        checks += c
    if entries != manifest["files"]:
        raise ValueError("Vector bytes or counts differ from index")
    digest = hashlib.sha256("".join(f'{e["path"]}\0{e["sha256"]}\n' for e in entries).encode()).hexdigest()
    if (vectors, checks, "sha256:" + digest) != (manifest["vector_count"], manifest["check_count"], manifest["evaluated_set_digest"]):
        raise ValueError("Evaluated-set record mismatch")
    base = subprocess.run([sys.executable, str(HERE / "base/conformance.py")], capture_output=True, text=True)
    if base.returncode or "CONFORMANCE OK" not in base.stdout:
        raise ValueError(base.stdout + base.stderr)
    base_checks = len(re.findall(r"^\[", base.stdout, re.M))
    print(base.stdout.replace("CONFORMANCE OK: all vectors behave as expected.", "Base expectations passed."), end="")
    workflows = json.loads((HERE / "workflow-merkle-seq-output-v1.json").read_bytes())["vectors"]
    for v in workflows:
        level = []
        for i, step in enumerate(v["steps"], 1):
            if step["seq"] != i:
                raise ValueError("Noncontiguous sequence")
            if v["merkle_version"] == "receipt-id-v0":
                leaf = step["receipt_id"]
            elif v["merkle_version"] == "seq-output-v1":
                output_hash = step["output_hash"].removeprefix("sha256:").lower()
                if not re.fullmatch(r"[0-9a-f]{64}", output_hash):
                    raise ValueError("Invalid output hash")
                leaf = f"{i}:{output_hash}"
            else:
                raise ValueError("Unsupported version")
            level.append(sha(leaf.encode("utf-8")))
        while len(level) > 1:
            if len(level) % 2:
                level.append(level[-1])
            level = [sha(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
        if not level or v["expected_verdict"] != "valid" or level[0].hex() != v["merkle_root"]:
            raise ValueError(v["name"] + ": root mismatch")
        print(f'[workflow-root] {v["name"]}: PASS')
    if base_checks + len(workflows) != checks:
        raise ValueError("Actual evaluated check count differs from manifest")
    print(f"CONFORMANCE OK: {vectors} vectors, {checks} checks, sha256:{digest}")


if __name__ == "__main__":
    main()
