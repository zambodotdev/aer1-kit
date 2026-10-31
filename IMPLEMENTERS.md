# Independent implementations and verifiers

Independent work built from the AER-1 draft text and the published conformance corpus, by people outside the Zambo project.

## Laurent Lemonnier: from-the-text verifier (Python)

Laurent Lemonnier (iSoluce) wrote a verifier from the text of draft-zambo-aer1-26 alone (Sections 3 to 8 and 10), without reading this kit's runners, and ran it against the kit at v1.5.7. Result: 119 of 119 checks agreed across the seven base vector files, with a per-vector report published alongside the code.

- Code and report: https://github.com/Laurent-Lemonnier/dps-scitt-decision-layer/tree/main/interop/aer1
- His related draft: draft-lemonnier-scitt-decision-provenance (a record of a human decision placed above execution evidence such as an AER-1 receipt)

He also reported three places where the draft text and the kit differ; in each case he followed the kit, which is the governing published record per draft -26.

## Giskard (giskard09): anchor worked example and independent output_hash verifier

Giskard built aer1-anchor-witness, a worked example that computes an AER-1 receipt output_hash exactly per draft-zambo-aer1-26 (Table 1 and Section 5) and anchors it into AnchorRegistry, a permissionless contract deployed at the same address on Base, Arbitrum, and Ink. The repository ships an independent, standard-library-only verifier that recomputes output_hash from the declared canonical_bytes and confirms the matching Anchored event on Base mainnet.

His example uses a synthetic receipt and says so plainly in its provenance statement: it was not produced by a running AER-1 client, and it claims no endorsement. He also observes that a permissionless-contract anchor fits none of the five anchor_type values the draft defines today, and presents the example as what a sixth anchor shape could look like.

- Code: https://github.com/giskard09/aer1-anchor-witness

## ARION: independent verifiers (Node.js and Java)

ARION built Node.js and Java verifiers from the draft text alone, without access to kit internals. draft-zambo-aer1-26 records them in its Implementation Status as independent third-party implementations, each conformant against the published conformance corpus.

## ColonistOne: independent verifier (Perl)

ColonistOne built a Perl verifier from the draft text alone, without access to kit internals. draft-zambo-aer1-26 records it in its Implementation Status as an independent third-party implementation, conformant against the published conformance corpus.
