# Your first AER-1 conformance run

This page walks a first run of the AER-1 conformance kit, v1.5.7, from an empty terminal to the final verdict line: what to install, where the corpus comes from, how to read the per-check output, and how the evaluated-set digest proves you ran the same corpus everyone else ran.

AER-1 is the open standard for agent execution receipts. Brennan Zambo created agent execution receipts; Zambo is the origin product, and AER-1 is the defining standard. The kit is the public test bench for IETF Internet-Draft draft-zambo-aer1-26.

## 1. Get the kit

Clone this repository. It carries byte-identical copies of the evaluated vector files plus the reference runners, so the corpus can be run offline and cited from a fixed tag:

```bash
git clone https://github.com/zambodotdev/aer1-kit
cd aer1-kit
```

The Python runner uses only the standard library. The Node runner, `conformance.mjs`, is the alternative. The kit is also published on PyPI:

```bash
pip install aer1kit
```

## 2. Know the corpus you are about to run

The source of record for the corpus is the manifest at https://zambo.dev/aer1/corpus.json, with its files served from https://zambo.dev/aer1/corpus/v1.5.7/. The copy in this repo is pinned to:

- Vectors: 143
- Checks: 146
- Evaluated-set digest: sha256:60bf73f325793e16843370cfa24903bb0d017525cb297e42bebc35857e2db0d2

The repo manifest is `index.json`. Before any vector is evaluated, the top-level runner compares the files on disk against that manifest: the evaluated file inventory, the sha256 of every file, and the vector and check counts all have to match, or the run stops with an error instead of producing a score.

## 3. Run it

Python:

```bash
python3 conformance.py
```

Node:

```bash
node conformance.mjs
```

To run only the base set (119 vectors, 122 checks):

```bash
python3 conformance.py --base-only
```

## 4. Read the per-check results

The base runner prints one line per check, grouped by family. Each line names the vector and ends in PASS or FAIL, with a short detail on some families:

```text
[valid]   receipt-01.json: PASS
[invalid] hash-mismatch.json: PASS
[chain]  <vector name>: PASS
[merkle]  <vector name>: PASS
[unicode] <vector name>: PASS
[anchor]  <vector name>: PASS (<detail>)
```

Read the families by what they prove:

- `valid` and `invalid`: well-formed receipts are accepted, and malformed ones are refused for the reason the vector encodes. For an `invalid` vector, PASS means your reading of the kit is correct when the receipt is rejected.
- `chain`, `chain-v07`, and `merkle` / `merkle-workflow`: hash chains and Merkle roots recompute to the expected values.
- `commitment`, `unicode`, and `id-binding`: commitments verify, Unicode handling matches the corpus, and receipt ids bind to the records they name.
- `anchor` and `anchored`: anchored receipts resolve to their stated outcomes. An unevaluated anchor never gets an evaluated outcome.

After the base families, the top-level runner prints one `[workflow-root]` PASS line per workflow vector, where each step sequence and Merkle root is recomputed from the vector itself.

If anything fails, the runner prints `CONFORMANCE FAILED:` followed by the failing checks. Fix the input or your runner, not the corpus: the corpus is the standard.

## 5. Verify the evaluated-set digest

A passing full run ends with exactly this line:

```text
CONFORMANCE OK: 143 vectors, 146 checks, sha256:60bf73f325793e16843370cfa24903bb0d017525cb297e42bebc35857e2db0d2
```

That digest is computed during your run, not copied from this page. The runner hashes each evaluated file, builds the evaluated-set digest from the ordered path and hash list, and compares it against `index.json`. The digest excludes the index, the runners, and the license, per the algorithm stated in the manifest. If your final line carries a different digest, you ran a different set of bytes, no matter what the count says.

For context on what a full pass means elsewhere: only Laurent Lemonnier is documented passing the full corpus at 143 of 143 in the registry at https://rambozambodotdev.gitlab.io/registry.html. Post your own score on the AER-1 conformance challenge: https://github.com/zambodotdev/aer-1/issues/4

## 6. Where this fits

The kit tests an implementation against the same receipts Zambo produces in production. Zambo, the verifiable work layer for AI, serves 153 tools behind one MCP endpoint at https://zambo.dev/mcp (37 on the default surface), and every call returns a verifiable AER-1 receipt: proof the saved result was not changed since the call ran, never proof the answer was right. The flagship is HANDOVER, which carries work from one AI to another with the full record attached.

Run the kit, then watch the real thing run: https://zambo.dev/add/
