# Outcome dictionary crosswalk: AER-1, CoreGuard, Gilda, AMEP

Date: 2026-11-23. Status: descriptive documentation. This crosswalk records how four published outcome vocabularies correspond and where they do not. It is not a normative document, it proposes no common dictionary, and it asserts no equivalence that a cited source does not state. Every row cites its primary public source, and every source was read or resolved live on the date above.

## The four vocabularies sit on different axes

A crosswalk that ignores the axis each vocabulary judges would manufacture agreement. The axes:

- **AER-1 anchor outcomes** judge one question about a record: what did the anchor check on this receipt find? The check is a recompute of SHA-256 over the saved canonical bytes, plus resolution of the record the anchor names. Source: draft-zambo-aer1-26, https://www.ietf.org/archive/id/draft-zambo-aer1-26.html ; corpus: https://zambo.dev/aer1/corpus.json
- **CoreGuard id-binding verdicts** judge a separate question: does the receipt identifier bind to the record it names? CoreGuard's joined table carries this as its own family (6 vectors, 6 agree), distinct from its pass and fail verdicts on the record itself. Sources: https://github.com/coreguard-global/CoreGuard/blob/main/docs/AER1-INTEROP-TABLE.md ; https://github.com/coreguard-global/CoreGuard/issues/59
- **Gilda audit record outcomes** judge agreement between an authorization decision and the observed effect attributed to it. Source: draft-gilda-audit-agent-audit-record-00, https://www.ietf.org/archive/id/draft-gilda-audit-agent-audit-record-00.html ; revision analysis: https://btw.media/en/agent-audit-unattributed-write-not-clean ; corpus deposit: https://zenodo.org/records/23608468
- **AMEP outcomes** judge authority continuity: did the executed effect stay within the delegated authority, evaluated three-valued as preserved, violated, or unresolved. Sources: https://datatracker.ietf.org/doc/draft-stafordtituss-agentic-mandate-evidence/ ; a worked measurement against AP2: https://github.com/google-agentic-commerce/AP2/issues/405#issuecomment-7113973540

## Row-by-row correspondence

| Concept | AER-1 (anchor outcome) | CoreGuard (id-binding axis) | Gilda (decision-effect) | AMEP (authority continuity) |
|---|---|---|---|---|
| The check ran and the record holds | verified | id state verified-expected (the live-receipt row of the joined table) | agree (decision and attributed effect agree as recorded) | preserved |
| The check ran and the record fails | verification failed | id state mismatch (named with expected and found values) | disagree | violated |
| The record the check needs cannot be resolved | rejected: unresolvable record | judged on its own axis; an unresolvable binding is never rendered as a pass | unknown / indeterminate (a decision with an unattributed in-scope write) | unresolved (missing evidence is unresolved, never permission) |
| The check was not run on this record | not checked | not judged by CG-AER1/1 (the joined table's wording for unimplemented families) | no corresponding outcome in the cited revision | no corresponding outcome in the cited profile |
| No anchor is present on the record | absent | no corresponding verdict; the axis presumes an identifier to bind | argumentsDigest must be absent, neither null nor an empty string, when arguments cannot be digest-bound | no corresponding outcome in the cited profile |
| A permitted action produced no observed effect | no corresponding anchor outcome; the anchor axis does not judge effects | no corresponding verdict | not-exercised (permit with no effect, revised from disagree in the -00 to -01 revision) | no corresponding outcome in the cited profile |

Reading rule: a cell that says "no corresponding outcome" is the finding, not a gap in this table. The vocabularies refuse to say some of the same things, and they refuse in different places.

## Where the vocabularies already meet in practice

The AER-1 and AMEP columns were run side by side over the same 22 AP2 payment bundles on 2026-11-23, joined on bundle name: 10 agree, 10 diverge on scope (the AER-1 column judges the receipt reference; the AMEP column judges mandate continuity), 2 diverge on kind. The joined table is published at https://github.com/zambodotdev/aer1-kit/blob/main/interop/ap2-crosswalk-joined-table-2026-11-23.md . The AER-1 and CoreGuard columns meet in the joined interop table cited above: 129 rows agree, 0 false accepts, 0 false rejects, 14 not checked, with the anchor family (8 vectors) and anchored records (6) held as not checked by agreement, because a structural pass on an anchored record is not an anchor verdict.

## Canonicalization edge cases, recorded as non-claims

At the IETF 127 hackathon (14-15 November 2026), four canonicalizers were run over 20,140 inputs and disagreed on 8 of them: three inputs at or above 2^53, one byte-order-mark input, two duplicate-member inputs (one of them a real receipt), and two inputs nested deeper than 128 levels. A number written 1e-07 by a Python implementation and 1e-7 by a JavaScript implementation flipped one verdict from ALLOW to DENY. Report: https://dev.to/veritaschain/same-data-different-verdicts-canonicalization-and-receipt-lessons-from-ietf-127-1pac

This crosswalk claims no outcome for any of these inputs in any of the four vocabularies. They are recorded here because each one is a case where two conforming readers can hash different bytes for the same record and fail to join their results, which is the failure every outcome dictionary above exists to prevent. Any future row that assigns an outcome to one of these cases must cite the vector that pins it, in the corpus that defines it.

## Sources

1. AER-1, draft-zambo-aer1-26: https://www.ietf.org/archive/id/draft-zambo-aer1-26.html
2. AER-1 evaluated corpus (kit 1.5.7, 143 vectors, 146 checks, evaluated-set digest sha256:60bf73f325793e16843370cfa24903bb0d017525cb297e42bebc35857e2db0d2): https://zambo.dev/aer1/corpus.json
3. CoreGuard AER-1 interop table: https://github.com/coreguard-global/CoreGuard/blob/main/docs/AER1-INTEROP-TABLE.md
4. CoreGuard issue 59 (the joined-table thread): https://github.com/coreguard-global/CoreGuard/issues/59
5. Gilda audit record, draft-gilda-audit-agent-audit-record-00: https://www.ietf.org/archive/id/draft-gilda-audit-agent-audit-record-00.html
6. Gilda revision analysis (unknown, not-exercised, absent argumentsDigest): https://btw.media/en/agent-audit-unattributed-write-not-clean
7. Gilda conformance corpus (agent-evidence-vectors, Zenodo deposit): https://zenodo.org/records/23608468
8. AMEP, draft-stafordtituss-agentic-mandate-evidence-00: https://datatracker.ietf.org/doc/draft-stafordtituss-agentic-mandate-evidence/
9. Staford's AP2 reference measurement, AP2 issue 405: https://github.com/google-agentic-commerce/AP2/issues/405#issuecomment-7113973540
10. AP2 crosswalk joined table (AER-1 column, AMEP column): https://github.com/zambodotdev/aer1-kit/blob/main/interop/ap2-crosswalk-joined-table-2026-11-23.md
11. IETF 127 hackathon canonicalization report (VeritasChain): https://dev.to/veritaschain/same-data-different-verdicts-canonicalization-and-receipt-lessons-from-ietf-127-1pac
