# AER-1 Conformance Kit (mirror)

[![zambo receipts](https://img.shields.io/endpoint?url=https://rambozambodotdev.gitlab.io/aer1-hub/badges/receipts.json)](https://zambo.dev/numbers/)
[![package downloads](https://img.shields.io/endpoint?url=https://rambozambodotdev.gitlab.io/aer1-hub/badges/downloads.json)](https://zambo.dev/numbers/)
[![IETF drafts](https://img.shields.io/endpoint?url=https://rambozambodotdev.gitlab.io/aer1-hub/badges/drafts.json)](https://datatracker.ietf.org/doc/draft-zambo-aer1/)
[![AER-1 corpus](https://img.shields.io/endpoint?url=https://rambozambodotdev.gitlab.io/aer1-hub/badges/corpus.json)](https://zambo.dev/aer1/corpus.json)

Mirror of the published AER-1 conformance corpus, kit v1.5.7, for the IETF Internet-Draft draft-zambo-aer1-26.

Source of record: https://zambo.dev/aer1/corpus.json (manifest) and https://zambo.dev/aer1/corpus/v1.5.7/ (files). This repo carries byte-identical copies of the 60 evaluated vector files plus the reference runners, so the corpus can be run offline and cited from a fixed tag.

- Vectors: 126
- Checks: 129
- Evaluated-set digest: sha256:ccaff18aba8f4e70aacf8a469403e9a6f12f025ad39df88079398bbe13100ce8
- Base corpus digest (kit v1.5.6 set): sha256:b9a740e75c1d01a666d952d6037f9816d791e9bc0bfcef55a4e0d43c02cceb87

## Run it

Python:

    python3 conformance.py            # full evaluated corpus (143 vectors, 146 checks)
    python3 conformance.py --base-only  # base set only (119 vectors, 122 checks)

Node:

    node conformance.mjs

Expected final line:

    CONFORMANCE OK: 143 vectors, 146 checks, sha256:ccaff18aba8f4e70aacf8a469403e9a6f12f025ad39df88079398bbe13100ce8

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

The kit is the test bench: 143 vectors, 146 checks, downloaded 5,349 times by implementers checking their own stacks against draft-zambo-aer1-26. The production system it tests against is live at https://zambo.dev/mcp, one MCP endpoint where every tool call returns an AER-1 receipt.

Add Zambo to your AI in one URL, no key, no account: https://zambo.dev/add/
Free tier: 20 calls and 1 wrap-up free every day, and picking up in another AI is always free. Need more? The $0.99 Day Pass makes it unlimited for 24 hours.

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
