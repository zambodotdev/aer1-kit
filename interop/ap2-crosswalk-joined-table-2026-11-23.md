# AP2 crosswalk: AMEP column joined with the AER-1 column

Joined 2026-11-23 for google-agentic-commerce/AP2 issue #402, at @stafordtituss's invitation. Join key: bundle name, one row per payment, as he specified.

**Inputs, pinned by digest (all recomputed by us before any row was judged):**

- AMEP column: `interop/ap2/verdicts.json` in stafordtituss/amep, SHA-256 `93aa9005beb32af0f1ba51666b45627b24b9c004da438c488af9d818fbf99b10`
- SDK fixtures: `packages/conformance/test/fixtures/ap2/sdk-bundles.json`, SHA-256 `7e1dd6d97003d11f61ee2b60625bc1fff282d9a5f1eaa7426b276bbd3140b61f` (matches the prefix he published, `7e1dd6d97003…`)
- Synthetic fixtures: `packages/conformance/test/fixtures/ap2/bundles.json`, SHA-256 `bd530228cb9880d33f49016ab85f426a6c0e9668f3b6e47734b4aa779a71c4fc` (matches `bd530228cb98…`)

**Method:** the AER-1 column was hand-traced from the fixture JSON. Every digest was recomputed with SHA-256 over the exact bytes as they appear in the fixture files. No code from the AMEP repository was executed; files were read only. The AER-1 column in machine-readable form sits next to this table (`ap2-crosswalk-aer1-column-2026-11-23.json`).

**What each column judges.** AMEP judges the payment afterwards: `preserved` (within the mandate), `violated` (outside it, with blame), `unresolved` (a record needed for the decision is missing). The AER-1 column judges the record, in the AER-1 outcome dictionary only: `verified` (every digest binding in the record recomputes from the bytes in the bundle), `verification failed` (material present, a binding does not recompute), `absent` (the bundle names a payment and carries no receipt for it), `not checked` (the bytes a recompute needs are not in the bundle), `rejected: unresolvable record`. A row is marked **agree** when both columns reach the same practical judgment about the payment's evidence, **diverge (scope)** when the columns answer different questions (record vs decision) and both answers stand, and **diverge (kind)** when the same facts draw a different refusal from each dictionary.

## The three rows he asked for, as data

**1. The #405 reference rule.** The fixtures carry 22 receipt records. Recomputed from the closed mandate material in each bundle: **21 references match the SDK rule** (SHA-256 over the closed hop's JWT alone), **0 match the specification rule** (the sd_hash manner, over the closed SD-JWT presentation with its disclosures), and **1 matches neither** (s7's receipt, which belongs to another mandate). Every binding reference in both families follows the SDK; the rule the specification text describes matched nothing, anywhere. Per-row rule matches are printed in the AER-1 column file.

**2. The #346 replay (`sdk-redeemed-twice`, `s10-redeemed-twice`, `s11-redeemed-twice-small`).** In all three bundles the two chains are byte-identical: the same closed mandate, presented and processed twice, carrying two receipts with the same reference. Both receipt records recompute in full, so the AER-1 column prints **verified** for the records, including the second one. AER-1's dictionary judges records; it carries no one-payment-per-mandate rule, and this column does not silently adopt one. AMEP's **violated** is a decision about the second execution. The divergence is one of scope, printed as a divergence, not smoothed over: a record layer can show that the same reference verified twice; counting executions under one consent is a profile judgment, and his profile makes it.

**3. Preserved vs verified.** These are answers to different questions. AMEP's `preserved` means the processed payment stayed within the mandate, judged afterwards; it does not certify the processor's settlement. AER-1's `verified` means the saved record recomputes unchanged; it does not say the payment was within the mandate, or that the result was right. A row where both appear (for example `sdk-within`) is an agreement that nothing is wrong on either axis, not a claim that the two words mean the same thing. Rows like `sdk-over-range` show the split plainly: the record of an over-range payment verifies, and the payment still violated the mandate.

## Joined table

| Bundle | Payment | AMEP | AER-1 | Join | Note |
|---|---|---|---|---|---|
| sdk-within | txn-1, 199.00 | preserved | verified | agree | reference: SDK rule |
| sdk-over-range | txn-1, 250.00 | violated (I2, agent) | verified | diverge (scope) | the record of an over-range payment recomputes; the decision is his column's |
| sdk-wrong-payee | txn-1, 199.00 | violated (I2, agent) | verified | diverge (scope) | same split as over-range |
| sdk-declined | txn-1, 199.00 | preserved | verified | agree | the record judged is the Error receipt; verified says the decline's record is intact, not that a payment occurred |
| sdk-lost-receipt | txn-1, 199.00 | unresolved (gap: receipt) | absent | agree | both columns name the same missing record |
| sdk-budget | txn-1, 199.00 | preserved | verified | agree | |
| sdk-budget | txn-2, 150.00 | violated (I2, agent) | verified | diverge (scope) | the violation is cumulative (349.00 over a 300.00 budget); a single record carries no running total |
| sdk-issuer-jwt-hash | txn-1, 199.00 | preserved | verified | agree | this chain binds closed to open by `issuer_jwt_hash`, not `sd_hash`; the binding recomputes |
| sdk-redeemed-twice | txn-1, 50.00 | violated (I2, agent) | verified (both records) | diverge (scope) | row 2 above; two receipts, one reference, identical chains |
| s1-within | txn-1, 199.00 | preserved | verified | agree | reference: SDK rule |
| s2-over-range | txn-1, 250.00 | violated (I2, agent) | verified | diverge (scope) | |
| s3-wrong-payee | txn-1, 199.00 | violated (I2, agent) | verified | diverge (scope) | |
| s4-declined | txn-1, 199.00 | preserved | verified | agree | Error receipt record, as sdk-declined |
| s5-lost-receipt | txn-1, 199.00 | unresolved (gap: receipt) | absent | agree | both name the missing receipt |
| s6-budget | txn-1, 199.00 | preserved | verified | agree | |
| s6-budget | txn-2, 150.00 | violated (I2, agent) | verified | diverge (scope) | cumulative budget, as sdk-budget |
| s7-receipt-for-another-mandate | txn-1, 199.00 | unresolved (gap: receipt) | verification failed | diverge (kind) | the bundle's only receipt carries a reference that recomputes under neither rule from this mandate; AMEP reads a misbound receipt as no receipt, the record layer reads the presented record as failed |
| s8-altered-amount | txn-1, 99.00 as presented | unresolved (gap: signature) | verification failed | diverge (kind) | the payment disclosure's digest does not recompute against the digest committed in the signed payload; the receipt reference itself still matches the SDK rule, because the JWT bytes were never touched. A reference match alone does not verify a record |
| s10-redeemed-twice | txn-1, 150.00 | violated (I2, agent) | verified (both records) | diverge (scope) | row 2 above |
| s11-redeemed-twice-small | txn-1, 50.00 | violated (I2, agent) | verified (both records) | diverge (scope) | row 2 above; the total fits every limit and the scope split is unchanged |
| s9-unknown-then-second | txn-1, 199.00 | unresolved (gap: receipt) | absent | agree | no receipt for this payment in the bundle |
| s9-unknown-then-second | txn-2, 150.00 | unresolved (gap: held_outcome) | verified | diverge (scope) | this payment's record is complete and recomputes; his column holds it because the first payment's outcome is unknown, which is cross-payment state a record judgment does not carry |

**Counts:** 22 payment rows. 10 agree, 12 diverge (10 of scope, 2 of kind), 0 not comparable. AER-1 column outcomes: 17 verified, 2 verification failed, 3 absent, 0 not checked, 0 rejected. Chain bindings: 25 chains; 24 bind closed to open by `sd_hash` and 1 by `issuer_jwt_hash`; every binding recomputes. Every disclosure in every chain matches the digest committed to it, except the one altered disclosure in s8.

**The shared boundary, unchanged:** the receipts carry no amount. Nothing in either column certifies what the processor actually charged; the executed value rests on the closed mandate's amount and the processor's word, in his column and in ours.

Corrections welcome: any row where we misread a bundle, he is invited to name it and the row will be re-run and reprinted.
