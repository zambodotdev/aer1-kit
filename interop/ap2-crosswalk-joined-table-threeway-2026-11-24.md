# AP2 crosswalk: AER-1, AMEP, and APAF-1 joined, three dictionaries on the pinned fixtures

Joined 2026-11-24 for google-agentic-commerce/AP2 issue #402. This file extends the two-way join of 2026-11-23 (`ap2-crosswalk-joined-table-2026-11-23.md`, left untouched) with the third column @nmatt1 published the next day, so all three dictionaries sit side by side on the same 22 payment rows. Join key: bundle name + payment, transaction_id on every row.

## Provenance

- **APAF-1 column (his artifact, credited to him):** `interop/ap2/apaf1-column.json` in [nmatt1/paymnts-trail-head-conformance](https://github.com/nmatt1/paymnts-trail-head-conformance/blob/95d61c440d5a4e3cc109dc9de7cf8ff52aca976e/interop/ap2/apaf1-column.json), commit `95d61c440d5a4e3cc109dc9de7cf8ff52aca976e`, file SHA-256 `12d378cfd2af6e1216b6c4456cfe83099d1af865bb4effce76eaefe7901da568`. Published with his comment on the issue: https://github.com/google-agentic-commerce/AP2/issues/402#issuecomment-7131341440. Fetched byte-exact from that commit for this mirror; his per-row checks and evidence strings are carried verbatim in the companion JSON (`ap2-crosswalk-joined-table-threeway-2026-11-24.json`).
- **AER-1 column:** `ap2-crosswalk-aer1-column-2026-11-23.json` in this repo, as printed in the two-way join.
- **AMEP column:** `interop/ap2/verdicts.json` in stafordtituss/amep, SHA-256 `93aa9005beb32af0f1ba51666b45627b24b9c004da438c488af9d818fbf99b10`, as printed in the two-way join.
- **Fixtures, pinned by digest (recomputed by him before any row was judged, matching the published pins):** SDK fixtures `sdk-bundles.json` SHA-256 `7e1dd6d97003d11f61ee2b60625bc1fff282d9a5f1eaa7426b276bbd3140b61f`; synthetic fixtures `bundles.json` SHA-256 `bd530228cb9880d33f49016ab85f426a6c0e9668f3b6e47734b4aa779a71c4fc`.

**Cross-check run for this mirror:** his AER-1 column matches our published join on all 22 rows (17 verified, 2 verification failed on s7 and s8, 3 absent), and his AMEP column matches it too. His column JSON and his printed comment table agree row for row.

## What each column judges

Three layers, three different questions, one row set:

- **AMEP judges the payment afterwards:** `preserved` (within the mandate), `violated` (outside it, with blame), `unresolved` (a record needed for the decision is missing).
- **AER-1 judges the record:** `verified` (every digest binding in the record recomputes from the bytes in the bundle), `verification failed` (material present, a binding does not recompute), `absent` (the bundle names a payment and carries no receipt for it), `not checked`, `rejected: unresolvable record`.
- **APAF-1 judges the decision on the presented artifacts, including cumulative mandate state:** spend, use count, and closed-mandate replay carried across the bundle, the cross-payment state a single-record judgment cannot carry. Open-mandate expiry is judged at each hop's iat, not at evaluation time. His vocabulary, with his definitions:

  - `approved`: chain, signatures, bindings, open-to-closed constraints and receipt all verify at the hop's presentation time
  - `declined`: a hard failure: signature or binding invalid, constraint violated, presented evidence altered, or the closed mandate replayed
  - `escalated`: a required check is unverifiable from the presented set: receipt absent or bound to another mandate, or a prior payment outcome unknown under stateful constraints
  - `not_evaluated`: the processor reported a failed execution; there is no payment outcome to decide on

His method, in his file's words: an independent implementation; SD-JWT disclosures resolved, every ES256 signature and every digest binding (sd_hash, issuer_jwt_hash, disclosure digests, receipt references) recomputed. Nothing in this mirror re-judges his rows; it joins them.

## Three-way joined table

| Bundle | Payment | AER-1 | AMEP | APAF-1 | Note |
|---|---|---|---|---|---|
| sdk-within | txn-1, 199.00 | verified | preserved | approved | agree in all three columns |
| sdk-over-range | txn-1, 250.00 | verified | violated (I2, agent) | declined | same refusal from AMEP and APAF-1 in different words; the record of an over-range payment still recomputes, so AER-1 verifies it. Scope split, as printed in the two-way join |
| sdk-wrong-payee | txn-1, 199.00 | verified | violated (I2, agent) | declined | same split as sdk-over-range |
| sdk-declined | txn-1, 199.00 | verified | preserved | not_evaluated | processor reported an Error, so APAF-1 has no payment outcome to decide; AMEP's preserved and AER-1's verified judge the decline's record, which is intact. Same practical judgment, different word |
| sdk-lost-receipt | txn-1, 199.00 | absent | unresolved (gap: receipt) | escalated | all three columns name the same missing record: AER-1 absent, AMEP unresolved, APAF-1 escalated |
| sdk-budget | txn-1, 199.00 | verified | preserved | approved | agree in all three columns |
| sdk-budget | txn-2, 150.00 | verified | violated (I2, agent) | declined | the row that needs a decision column carrying state: APAF-1 declines on cumulative spend found by recompute (19900 minor already spent + 15000 presented over a 30000 budget, budget.max in major units where amount_range is minor); AMEP violated (I2); AER-1 verifies the single record, which carries no running total |
| sdk-issuer-jwt-hash | txn-1, 199.00 | verified | preserved | approved | agree in all three columns; the chain binds closed to open by issuer_jwt_hash and the binding recomputes |
| sdk-redeemed-twice | txn-1, 50.00 | verified (both records) | violated (I2, agent) | declined | one payment over-redeemed: a byte-identical closed hop presented twice. APAF-1 declines the second presentation as closed_mandate_replay and AMEP marks the second execution violated (I2); both AER-1 records recompute, and the record layer carries no one-payment-per-mandate rule |
| s1-within | txn-1, 199.00 | verified | preserved | approved | agree in all three columns |
| s2-over-range | txn-1, 250.00 | verified | violated (I2, agent) | declined | as sdk-over-range |
| s3-wrong-payee | txn-1, 199.00 | verified | violated (I2, agent) | declined | as sdk-wrong-payee |
| s4-declined | txn-1, 199.00 | verified | preserved | not_evaluated | as sdk-declined |
| s5-lost-receipt | txn-1, 199.00 | absent | unresolved (gap: receipt) | escalated | as sdk-lost-receipt |
| s6-budget | txn-1, 199.00 | verified | preserved | approved | agree in all three columns |
| s6-budget | txn-2, 150.00 | verified | violated (I2, agent) | declined | cumulative budget, as sdk-budget txn-2 |
| s7-receipt-for-another-mandate | txn-1, 199.00 | verification failed | unresolved (gap: receipt) | escalated | the presented receipt recomputes but binds a different mandate's closed hop. APAF-1 escalates: for this payment, execution is unverifiable from the presented set. AMEP reads a misbound receipt as no receipt (unresolved, gap: receipt); AER-1 reads the presented record as verification failed. Three words for one misbound receipt |
| s8-altered-amount | txn-1, 99.00 as presented | verification failed | unresolved (gap: signature) | declined | the three-way split, named in full below |
| s10-redeemed-twice | txn-1, 150.00 | verified (both records) | violated (I2, agent) | declined | replay, as sdk-redeemed-twice |
| s11-redeemed-twice-small | txn-1, 50.00 | verified (both records) | violated (I2, agent) | declined | replay, as sdk-redeemed-twice; the total fits every limit and the split is unchanged |
| s9-unknown-then-second | txn-1, 199.00 | absent | unresolved (gap: receipt) | escalated | all three columns name the same missing record, as sdk-lost-receipt |
| s9-unknown-then-second | txn-2, 150.00 | verified | unresolved (gap: held_outcome) | escalated | this payment's record verifies, and both decision columns hold it because payment 1's outcome is unknown under a stateful budget: AMEP unresolved (gap: held_outcome, the gap he named), APAF-1 escalated. Cross-payment state a record judgment does not carry |

One join detail, printed rather than smoothed: in his artifact the s8 row carries no transaction_id field (its checks read `closed_mandate_absent`, so no transaction id is recoverable from the presented set). That row is joined on bundle + payment index, the same key both published tables print for it (txn-1). Every other row carries its transaction_id in his file.

## Named divergences, printed not smoothed

**1. s8-altered-amount is the three-way split.** AMEP reads a signature gap (unresolved), AER-1 reads a failed record (verification failed), APAF-1 reads altered presented evidence and declines: the disclosure bytes decode, but their digest does not recompute against the digest committed inside the signed payload. In his dictionary, tampered evidence is a hard integrity failure, not a missing record and not a signature gap. Three defensible answers; his is the strictest.

**2. s7-receipt-for-another-mandate.** The presented receipt recomputes; it just binds a different mandate's closed hop. APAF-1 escalates: for this payment, execution cannot be verified from the presented set. That sits between AMEP's unresolved (gap: receipt) and AER-1's verification failed.

**3. Processor-Error rows (sdk-declined, s4-declined).** APAF-1 emits not_evaluated: the processor reported no execution, so there is no payment outcome to decide on. AMEP's preserved and AER-1's verified are about the decline's record, which also verifies. Agree in practice, different word.

## Counts

22 payment rows. AER-1: 17 verified, 2 verification failed, 3 absent. AMEP: 7 preserved, 9 violated, 6 unresolved. APAF-1: 5 approved, 10 declined, 5 escalated, 2 not_evaluated.

Against AMEP, as he printed it: 19 rows reach the same practical judgment (his declined covers AMEP's violated on all nine, plus s8; his escalated covers five of AMEP's six unresolved; his not_evaluated covers the two processor-Error receipts). Against AER-1, as he printed it: the rows mostly diverge by scope, which is expected, because the columns judge different things.

## A second axis his column publishes

Per row, under `checks.spec_schema`, his column also reports conformance of the presented mandate objects to the ap2-protocol.org JSON schemas. Finding: all 22 open payment mandates fail the contains clause, because none carries a `payment.reference` constraint, which the published open-payment-mandate schema requires. It does not drive his decision verdicts (it measures spec-profile conformance of the fixture generator, a different axis than decision semantics), but it is a real finding for whoever owns these fixtures: either the SDK never emits `payment.reference`, or the published schema is stricter than the ecosystem's de-facto profile.

**The shared boundary, unchanged across all three columns:** receipts carry no amount. Nothing in any column certifies the executed value; it rests on the closed mandate's amount and the processor's word.

Corrections welcome: any row where any column misread a bundle, name the row and it will be re-run and reprinted.
