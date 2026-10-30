# Metadata-binding probes (draft -26 Section 6 step 4)

Runner test fixtures for the metadata recomputation in
`base/conformance.py` / `base/conformance.cjs` (kit -24). These files
live OUTSIDE the published corpus: nothing under `base/` changed, and
the corpus still stands at 126 vectors / 129 checks with its
evaluated-set digest unchanged.

The rule (draft Section 6 step 4, block defined in Section 3.1):
whenever a receipt carries `metadata_hash`, a verifier recomputes the
canonical metadata block from the receipt's stored member values and
MUST fail on a mismatch. Before kit -24 no runner recomputed it, so
the four mutations below passed every kit check (finding by Laurent
Lemonnier, 2026-10-29).

Fixtures:

- `real-04-*.json`: the corpus vector `base/test-vectors/valid/
  real-04.json` (the one corpus receipt carrying a correct Section
  3.1 `metadata_hash`) with exactly one covered member changed.
- `laurent-receipt.json`: the unmodified receipt from Laurent
  Lemonnier's DPS x AER-1 composition,
  https://github.com/Laurent-Lemonnier/dps-scitt-decision-layer/tree/main/interop/aer1-decision
  (repo commit 96633ce825c1a407aade20b075d41a47b2f00ef4, file
  `out/aer1-receipt.json`). Control: it MUST pass.
- `laurent-*.json`: the same receipt with the four mutations of his
  `metadata_probes()` in that folder's `negatives.py` applied
  verbatim (created_at moved to 2026-10-28T14:00:00.000Z; id replaced
  by his deterministic `uuid4_from("another id")`; tool version set
  to 9.9.9; metadata_hash zeroed).

Expectations, both runners: the two unmodified controls pass with no
failures; every mutated fixture fails, and the failure list contains
"metadata_hash does not match the recomputed metadata block".

Run:

    python3 tests/run_metadata_probes.py
    node tests/run_metadata_probes.mjs
