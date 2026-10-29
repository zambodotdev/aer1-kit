# Independent implementations and verifiers

Independent work built from the AER-1 draft text and the published conformance corpus, by people outside the Zambo project.

## Laurent Lemonnier: from-the-text verifier (Python)

Laurent Lemonnier (iSoluce) wrote a verifier from the text of draft-zambo-aer1-26 alone (Sections 3 to 8 and 10), without reading this kit's runners, and ran it against the kit at v1.5.7. Result: 119 of 119 checks agreed across the seven base vector files, with a per-vector report published alongside the code.

- Code and report: https://github.com/Laurent-Lemonnier/dps-scitt-decision-layer/tree/main/interop/aer1
- His related draft: draft-lemonnier-scitt-decision-provenance (a record of a human decision placed above execution evidence such as an AER-1 receipt)

He also reported three places where the draft text and the kit differ; in each case he followed the kit, which is the governing published record per draft -26.
