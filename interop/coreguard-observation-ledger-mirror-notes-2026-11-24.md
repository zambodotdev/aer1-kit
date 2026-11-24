# CoreGuard CG-OBS/1 observation ledger: mirror notes (2026-11-24)

Mirror of `docs/AER1-OBSERVATION-LEDGER.md` from
[coreguard-global/CoreGuard](https://github.com/coreguard-global/CoreGuard/blob/main/docs/AER1-OBSERVATION-LEDGER.md),
copied 2026-11-24 at commit `220c9e8964557a7d45f7cd8c04d061c3b4036aff`.
Mirrored file SHA-256: `8bafaeb16d466a294fad4c27c3a454484c6c12506cb55aa7923c69a4a8327251`
(6,391 bytes, byte-identical to the source).

CG-OBS/1 is EslaM-X's profile layer over AER-1: an append-only observation
ledger in which each (observer, read) event carries one of AER-1's five
outcomes unchanged, a frozen reason under `not_checked`
(`access_refused`, `access_revoked`, `not_attempted`), and named refusal
codes including `OUT_OF_ORDER` for backfilled reads. The subject is
`receipt-03-live` from kit 1.5.7, digest
`sha256:0492c18e09059aa2e30ba0864f6aada2ef08475a5b35944cbf2a9ce46d12b9f1`,
recomputed from the pinned bytes by his generator at generation time; the
three observers on the page are labelled synthetic by the author.

Our position, stated on the thread (EslaM-X/CoreGuard issue #59): the five
outcomes are outcomes of a check (one caller, over specific bytes, at one
time), never a property of a run, so the dictionary does not move and the
ledger sits in the profile layer by design. An observation family against
the same set joins this interop record as a joined column under his name
when he builds it; it does not join the corpus, which judges bytes.
Discussion: https://github.com/EslaM-X/CoreGuard/issues/59
