# AER-1 Conformance Kit (mirror)

Mirror of the published AER-1 conformance corpus, kit v1.5.7, for the IETF Internet-Draft draft-zambo-aer1-26.

Source of record: https://zambo.dev/aer1/corpus.json (manifest) and https://zambo.dev/aer1/corpus/v1.5.7/ (files). This repo carries byte-identical copies of the 60 evaluated vector files plus the reference runners, so the corpus can be run offline and cited from a fixed tag.

- Vectors: 126
- Checks: 129
- Evaluated-set digest: sha256:ccaff18aba8f4e70aacf8a469403e9a6f12f025ad39df88079398bbe13100ce8
- Base corpus digest (kit v1.5.6 set): sha256:b9a740e75c1d01a666d952d6037f9816d791e9bc0bfcef55a4e0d43c02cceb87

## Run it

Python:

    python3 conformance.py            # full evaluated corpus (126 vectors, 129 checks)
    python3 conformance.py --base-only  # base set only (119 vectors, 122 checks)

Node:

    node conformance.mjs

Expected final line:

    CONFORMANCE OK: 126 vectors, 129 checks, sha256:ccaff18aba8f4e70aacf8a469403e9a6f12f025ad39df88079398bbe13100ce8

## Layout

- `base/`: the v1.5.6 base corpus and its runners (`base/conformance.py`, `base/conformance.cjs`).
- Top-level vector files: the versioned workflow-root vectors and the cross-version must-fail workflow vectors added on top of the base set.
- `index.json`: the corpus manifest (format, digests, per-file hashes). The evaluated-set digest excludes the index, the runners, and the license, per the algorithm stated in the manifest.
- `LICENSE`: the kit license.

AER-1 is the receipt format behind Zambo, the verifiable work layer for AI: every tool call returns a verifiable receipt, proof the saved result was not changed since it was saved. Spec: https://datatracker.ietf.org/doc/draft-zambo-aer1/26/
