# AP2 evidence-pack crosswalk: mirror notes (2026-11-24)

Mirror of `interop/ap2-evidence-pack/CROSSWALK.md` and `crosswalk.json` from
[eltociear/pqam](https://github.com/eltociear/pqam/tree/main/interop/ap2-evidence-pack)
at commit `d41f78a`, copied 2026-11-24. Mirrored file SHA-256:

- CROSSWALK.md: `4425b7a49d0284c3a418d96ba10df06063481c7d69c311b5950c1526d154717c`
- crosswalk.json: `138cc006f6456cae323aa0d5574430892be93dfcd54a87754b5d73053e3eb654`

Context: the crosswalk maps 62 cases (26 verify, 10 admission, 26 policy)
between the AP2 evidence pack (SPEC_AP2_EVIDENCE 1.10.0) and AER-1 outcomes.
Discussion: [AP2 issue #338](https://github.com/google-agentic-commerce/AP2/issues/338).
Our row-by-row read: comment
[7129148640](https://github.com/google-agentic-commerce/AP2/issues/338#issuecomment-7129148640).

## Run-verified corrections (Roberto Locatelli, 2026-11-24)

Roberto Locatelli, the pack spec's author, ran the crosswalk rows against
ap2-evidence-pack 1.10.0 from PyPI (wheel SHA-256
`36a176df58f3d35698a572647cc3399382dbd526aa2356213051ce4f1288accc`) on the
vectors in `spec/vectors/ap2/` at tag `v1.10.0`. His run:
comment [7130575583](https://github.com/google-agentic-commerce/AP2/issues/338#issuecomment-7130575583).
Our answer: comment
[7130965831](https://github.com/google-agentic-commerce/AP2/issues/338#issuecomment-7130965831).

Agreed as written: Verify 5/6 and Admission 7.

**Verify 26 is correct, and wider than the row says.** With the `ml-dsa-65`
entry removed and `scheme` set to `classical-only`, the pack reads
`valid: true` not only with no policy option but also with both producer keys
pinned (`producer_signature: verified`), with `--trust-set-complete`, and
with `--require-producer`. The downgrade shows only in `pq_protected: false`
and `scheme: classical-only`; `valid` and `producer_signature` do not show
it. It is refused under `--require-pq`, or when the pinned set holds the
`ml-dsa-65` key alone. Control: leaving `scheme: hybrid` after the strip
reads `contradicted`, because section 5 reconciles `scheme` with the
entries; it is the relabel that passes.

**Six rows where the 1.10.0 run gives a different output from the crosswalk:**

- V13: an amount given as a JSON integer inside the mandate is admitted and
  reads `valid: true`; a number with a fraction inside the mandate reads
  `sealed_content: contradicted` / `artifact_invalid`. The row's
  `admission: refused`, `malformed` is what a fraction written in the pack
  file itself gets.
- V10: a mandate with `typ: "kb+jwt"` reads `valid: true`; `verify` checks
  `typ` on the KB-JWT and on the hops after the first of a delegation chain,
  not on a mandate outside a chain.
- Admission 10: reads `sealed_content: verified`, `valid: true`, not
  `contradicted`.
- Admission 5, 6 and 9, column "today": a classical-only mandate with a
  pinned hybrid producer block and `--require-pq` reads `require_pq` met,
  `valid: true`; the column describes the proposed behaviour.
- Admission 7 and 8: `require_anchor` is unmet only when the flag is given
  and no anchor is counted.
- V14: an unknown member of a format object is `unknown_member`, but an
  unknown claim inside the mandate is admitted.

V1-V9, V11, V12, V17, V25, V26 and Admission 1-4 read as the crosswalk says.

## Committed fix and open items

Roberto committed to a spec-first fix in 1.11.0: sections 5 and 10 will name
the downgrade, and a pinned key set that contains an `ml-dsa-65` key will
require a valid `ml-dsa-65` signature under a pinned key, so the stripped
pack is not `valid` whenever that key is pinned. Until then, his advice is
to pass `--require-pq` together with the pins.

Our commitments on the record: re-run the stripped pack against 1.11.0 when
it lands and post the result on issue #338. Roberto will return with a
proposal, written as spec text first, on the two open questions: an issuer
PQ signature on the mandate, and refusal after a transition date.
