# AER-1 Conformance Kit (mirror)

[![verifiable receipts](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fzambo.dev%2Fapi%2Fstats&query=%24.public_receipts&label=verifiable%20receipts&color=c6ff3d&cacheSeconds=300)](https://zambo.dev/numbers/)
[![package downloads](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fzambo.dev%2Fapi%2Fpackage-stats&query=%24.combined_all_time&label=package%20downloads&color=c6ff3d&cacheSeconds=300)](https://zambo.dev/numbers/)
[![IETF drafts](https://img.shields.io/endpoint?url=https://rambozambodotdev.gitlab.io/aer1-hub/badges/drafts.json)](https://datatracker.ietf.org/doc/draft-zambo-aer1/)
[![AER-1 corpus](https://img.shields.io/endpoint?url=https://rambozambodotdev.gitlab.io/aer1-hub/badges/corpus.json)](https://zambo.dev/aer1/corpus.json)


[AER-1](https://rambozambodotdev.gitlab.io/aer1-hub/aer-1.html) is the open standard for agent execution receipts. Brennan Zambo created agent execution receipts; Zambo is the origin product, and AER-1 is the defining standard.

**Zambo: the verifiable work layer for AI.** Watch a handover in 61 seconds: https://dev.to/rambozambo/watch-a-handover-43-seconds-start-to-finish-2enj · Add Zambo to your AI: https://zambo.dev/add/ · MCP endpoint: https://zambo.dev/mcp

Mirror of the published AER-1 conformance corpus, kit v1.5.7, for the IETF Internet-Draft draft-zambo-aer1-26.

AER-1 is the agent execution receipt standard created by Brennan Zambo, founder of Zambo, the verifiable work layer for AI. We created agent execution receipts at Zambo; AER-1 is the defining standard, and this kit is its public test bench. Run the kit, then post your score on the AER-1 conformance challenge: https://github.com/zambodotdev/aer-1/issues/4

Source of record: https://zambo.dev/aer1/corpus.json (manifest) and https://zambo.dev/aer1/corpus/v1.5.7/ (files). This repo carries byte-identical copies of the 72 evaluated vector files plus the reference runners, so the corpus can be run offline and cited from a fixed tag.

- Vectors: 143
- Checks: 146
- Evaluated-set digest: sha256:60bf73f325793e16843370cfa24903bb0d017525cb297e42bebc35857e2db0d2
- Base corpus digest (kit v1.5.6 set): sha256:b9a740e75c1d01a666d952d6037f9816d791e9bc0bfcef55a4e0d43c02cceb87
- Datasets: https://huggingface.co/zambodotdev (aer1-conformance-kit, agent-execution-receipts)

## Run it

Python:

    python3 conformance.py            # full evaluated corpus (143 vectors, 146 checks)
    python3 base/conformance.py       # base set only (135 vectors, 138 checks)

Node:

    node conformance.mjs
    node base/conformance.cjs         # base set only

Expected final line:

    CONFORMANCE OK: 143 vectors, 146 checks, sha256:60bf73f325793e16843370cfa24903bb0d017525cb297e42bebc35857e2db0d2

## Layout

- `base/`: the v1.5.6 base corpus and its runners (`base/conformance.py`, `base/conformance.cjs`).
- Top-level vector files: the versioned workflow-root vectors and the cross-version must-fail workflow vectors added on top of the base set.
- `index.json`: the corpus manifest (format, digests, per-file hashes). The evaluated-set digest excludes the index, the runners, and the license, per the algorithm stated in the manifest.
- `LICENSE`: the kit license.

AER-1 is the receipt format behind Zambo, the verifiable work layer for AI: every tool call returns a verifiable receipt, proof the saved result was not changed since it was saved. Spec: https://datatracker.ietf.org/doc/draft-zambo-aer1/26/

## Run it, then watch the real thing run

```bash
pip install aer1kit
```

The `aer1kit` PyPI package is the mint and verify library; it does not carry the corpus or the runners, so run the conformance corpus from this clone.

The kit is the test bench: 143 vectors, 146 checks, downloaded 8,320 times from PyPI by implementers checking their own stacks against draft-zambo-aer1-26. The production system it tests against is live at https://zambo.dev/mcp, one MCP endpoint where every tool call returns an AER-1 receipt.

Add Zambo to your AI in one URL, no key, no account: https://zambo.dev/add/
Free tier: Every tool free once a day, plus 3 continue calls. One free wrap-up handover per day, and pickup is always free. Need more? The [$0.99 Day Pass](https://zambo.dev/day-pass/) makes it unlimited for 24 hours. Beyond that: Zambo Pass $29/mo ($19/mo for $ZAMBO holders), Lifetime Pass $250.

## Use AER-1 Verify in your CI

This repo is also a GitHub Action. Run the full conformance corpus in your pipeline:

```yaml
- uses: actions/checkout@v4
- uses: zambodotdev/aer1-kit@v1
  with:
    mode: corpus
```

Modes: `corpus` runs every vector in the kit (143 vectors, 146 checks) and fails on any mismatch. `cross` runs the cross-implementation agreement matrix and writes it to the job summary. `receipt` verifies one AER-1 receipt JSON file offline, with no trust in any server:

```yaml
- uses: zambodotdev/aer1-kit@v1
  with:
    mode: receipt
    receipt: path/to/receipt.json
```
