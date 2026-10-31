# AER-1 and the EU AI Act: Articles 12, 19, and 26

A technical mapping between the AER-1 receipt format
(draft-zambo-aer1-26) and the record-keeping provisions of Regulation
(EU) 2024/1689 (the EU AI Act): Article 12 (record-keeping), Article 19
(automatically generated logs), and Article 26 (obligations of
deployers), as those provisions concern records of what an AI system
did.

This document is a technical mapping, not legal advice and not a
conformity assessment. A record kept in AER-1 form does not by itself
show that a system or an organisation complies with the Regulation.
The duties in these articles fall on providers and deployers of
high-risk AI systems. AER-1 is a record format. It can supply the
execution records those duties call for, where the system's relevant
events are tool calls recorded by an AER-1 producer. It cannot operate
a system, keep records on anyone's behalf, or make the judgements the
articles assign to providers and deployers.

Every row below names its gap. A mapping that only lists strengths
would not be worth reading.

## How to read the status column

- **Covered at the record layer:** AER-1 defines the record and the
  rule that produces it. Operating the producer and keeping the
  records remain the operator's duties in every row.
- **Partial:** AER-1 supplies part of what the paragraph calls for.
  The gap column says which part it does not supply.
- **Not covered:** AER-1 has no mechanism for this. The row is listed
  so the gap is on the record.

Article text is quoted from Regulation (EU) 2024/1689 as published in
the Official Journal (EUR-Lex). AER-1 references are to
draft-zambo-aer1-26 by section.

## Article 12: Record-keeping

| Provision | What it requires | AER-1 mechanism | Status | Gap |
|---|---|---|---|---|
| Art. 12(1) | "High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system." | Section 3: a producer MUST issue a receipt for every tool call it receives, including calls it rejects before execution. "A call that leaves no receipt is a conformance failure: the absence of a record MUST NOT be allowed to hide an attempted call." Recording is therefore automatic and exception-free at the tool-call layer. | Partial | Only events that reach a recording producer as tool calls are recorded. Events inside a model that never become tool calls leave no receipt, and whether recording spans the system's lifetime is a property of the deployment, not of the format. |
| Art. 12(2) | Logging capabilities shall enable the recording of events relevant for (a) identifying situations that may result in the system presenting a risk under Article 79(1) or in a substantial modification, (b) facilitating post-market monitoring under Article 72, and (c) monitoring the operation of the system under Article 26(5). | Each receipt binds an identifier, a creation time, the tool name, version and caller scope, a provenance class (Section 5), and a hash commitment over the exact output bytes (Sections 3 and 4). Optional members add an input commitment (Section 3.3), execution context (model, source system, framework, environment; Section 3.2), checks not performed and actions not taken (negative_record, Section 3.4), reversal state, and fresh-read mismatch outcomes. Sections 7 and 8 order a job's receipts into a hash-chained timeline and bind multi-step workflows under one root, so a reviewer can reconstruct what ran, in what order, with what recorded result. Records are checkable by any party without an account (Section 9). | Partial | AER-1 records events; it does not judge which events signal a risk, and it performs none of the monitoring itself. Identifying risk situations, running post-market monitoring, and monitoring operation remain the provider's and deployer's work. The receipts are evidence those processes can read. |
| Art. 12(3)(a) | For the systems in Annex III point 1(a) (remote biometric identification): recording of the period of each use (start date and time and end date and time of each use). | Every receipt carries created_at, the time the record was created. In a Section 7 timeline, the first and last entries bound the period over which a job's recorded calls occurred. | Partial | AER-1 defines no start-of-use and end-of-use members. A record creation time is not necessarily the start of a use, and bounding a period from a chain is an inference by the reader, not a recorded fact. |
| Art. 12(3)(b) | The reference database against which input data has been checked by the system. | execution_context.source names the source system the tool acted upon; the draft's own examples include a database name (Section 3.2). | Partial | The member is optional, specific to no kind of database, and producer-asserted. Section 3.2 places execution_context outside the hash-bound core: it is not part of the metadata_hash computation, and a verifier must surface it as asserted context, never as an attested fact. |
| Art. 12(3)(c) | The input data for which the search has led to a match. | The exact recorded input can be committed with input_hash (Section 3.3) under a published byte layout, and the reference payload shape carries the inputs themselves, so what the input was can be checked later. | Partial | AER-1 has no concept of a match. Nothing in the format designates which inputs produced one. The input can be recorded and committed; the match designation cannot. |
| Art. 12(3)(d) | The identification of the natural persons involved in the verification of the results, as referred to in Article 14(5). | None in the interoperable core. field_provenance (Section 3.4) names which party wrote each field, by role: actor, tool, or counterparty. | Not covered | AER-1 defines no member that identifies a natural person. Caller identity appears only in deployed records outside the interoperable core (Section 3), which verifiers must not require. A deployment that needs Article 12(3)(d) must record the persons' identities outside AER-1 or in deployment-specific members, and accept that verifiers will not check them. |

## Article 19: Automatically generated logs (providers)

| Provision | What it requires | AER-1 mechanism | Status | Gap |
|---|---|---|---|---|
| Art. 19(1) | Providers shall keep the logs referred to in Article 12(1), to the extent such logs are under their control, "for a period appropriate to the intended purpose of the high-risk AI system, of at least six months, unless provided otherwise in the applicable Union or national law, in particular in Union law on the protection of personal data." | Section 9: every receipt is retrievable at a stable public URL, and "the record at that URL MUST NOT be altered." Corrections are published as new receipts carrying the superseded id in the supersedes member; they never rewrite the original. Because each kept record carries its output commitment and metadata commitment, a later change to the committed bytes or to the bound metadata of a kept record is detectable by recomputation (Sections 4, 3.1, and 6). Section 10 anchors can additionally fix a record's digest at a point in time on infrastructure outside the keeper's store. | Partial | AER-1 sets no retention period. The six-month floor, and the judgement of what period is appropriate to the intended purpose, belong to the provider. The format also cannot keep anything by itself: storage, availability, and deletion policy are the deployment's. What the format contributes is that records kept under it can be shown, later, to be the records that were issued. |

## Article 26: Obligations of deployers

Only the paragraphs that concern execution records are mapped.
Paragraphs on worker information, registration, and data protection
impact assessments do not turn on record format and are out of scope
here.

| Provision | What it requires | AER-1 mechanism | Status | Gap |
|---|---|---|---|---|
| Art. 26(1) | Deployers shall take appropriate technical and organisational measures to ensure they use the systems in accordance with the instructions for use. | None. | Not covered | This is an organisational duty. Receipts can afterwards evidence how a system was in fact used, which is evidence about the measure, not the measure. |
| Art. 26(2) | Deployers shall assign human oversight to natural persons who have the necessary competence, training and authority, as well as the necessary support. | None in the core record. | Not covered | AER-1 records executions, not oversight assignments, and approval events are not a core member. A deployment may record approvals in deployment-specific members; verifiers will not check them. |
| Art. 26(4) | To the extent the deployer exercises control over the input data, the deployer shall ensure that input data is relevant and sufficiently representative in view of the intended purpose. | input_hash (Section 3.3) commits to the exact input bytes the producer recorded, under a published byte layout, so the input a decision rested on can be produced and checked later. | Partial | Relevance and representativeness are judgements about data. A commitment proves what the recorded input was; it says nothing about whether the input was representative. |
| Art. 26(5) | Deployers shall monitor the operation of the system on the basis of the instructions for use; where use may result in a risk under Article 79(1), inform the provider or distributor and the relevant market surveillance authority without undue delay and suspend use; where a serious incident is identified, inform the provider, then the importer or distributor and the authorities immediately. | The deployer's operation record exists in checkable form: receipts for executed and rejected calls alike, hash-chained job timelines whose breaks are detectable by recomputation (Section 7.2), workflow records, and verification outcomes under Section 6. A monitoring function, human or automated, can read the same records an auditor will later read, because resolution is public and needs no account (Section 9). | Partial | Monitoring is supported; the duties are not discharged by records. Informing providers and authorities, suspending use, and reporting incidents are acts of the deployer that no record format performs. |
| Art. 26(6) | Deployers shall keep the logs automatically generated by the system, to the extent under their control, for a period appropriate to the intended purpose, of at least six months, unless provided otherwise in applicable Union or national law, in particular on the protection of personal data. | The same mechanics as Article 19(1): stable public URLs, no alteration in place, corrections by supersession, commitments that make later alteration of kept records detectable, optional external anchors over digests only (Section 10, privacy bound: an anchor MUST NOT contain step content, tool inputs, or tool outputs). | Partial | The duration and the control judgement are the deployer's, exactly as in Article 19(1). One further tension to plan around: this paragraph is expressly subject to Union data-protection law, and AER-1's default is public resolution. A deployment whose logs contain personal data must decide what may resolve publicly before it issues receipts, because the format will not make that decision for it. |

## What AER-1 provides that these articles do not ask for

Three properties go beyond the articles' floor. They are listed
because deployers evaluating evidence formats will ask, and because
none of them should be mistaken for compliance.

- **Independent checkability.** Article 12 requires logs to exist.
  AER-1 additionally lets a party who did not produce a record check
  that the record was not changed after it was saved, by recomputing
  its commitments, without trusting the keeper's storage and without
  an account (Sections 6 and 9). The check covers the saved result.
  It does not show the result was correct.
- **Provenance as a recorded field.** Every receipt states whether the
  recording system executed the call, observed it through a gateway,
  or received it as an agent's report, and verification must not
  upgrade one class into another (Section 5). The articles require
  traceability appropriate to the purpose; they do not prescribe a
  provenance vocabulary.
- **A conformance corpus.** AER-1 ships with a public test corpus
  (126 vectors, 129 checks) and independent implementations, so the
  claim "this producer emits AER-1 records" is itself testable
  against fixed vectors rather than asserted.

## Scope notes

- These articles govern high-risk AI systems. Whether a given system
  is high-risk, and which of its events are tool calls, are
  classification and deployment questions this mapping does not
  answer.
- Under the Regulation's application dates as amended by Regulation
  (EU) 2026/1744, the Chapter III obligations that include Articles
  12, 19, and 26 apply from 2 December 2027 for systems under Article
  6(2) (Annex III) and from 2 August 2028 for systems under Article
  6(1) (Annex I). Preparation time is the point of publishing a
  mapping now; nothing in this document suggests the duties are
  already in force for a given reader.
- Article 12(3) applies only to the remote biometric identification
  systems of Annex III point 1(a). Its rows are mapped because they
  are the Act's most specific statement of log content, not because
  most agent systems fall under them.

## Sources

- Regulation (EU) 2024/1689 of 13 June 2024, Articles 12, 19, and 26,
  Official Journal text, EUR-Lex:
  https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
- draft-zambo-aer1-26, "AER-1: Agent Execution Receipts", Sections 3
  to 10, IETF Datatracker:
  https://datatracker.ietf.org/doc/draft-zambo-aer1/26/
- AER-1 conformance corpus and kit (126 vectors, 129 checks, kit
  v1.5.7): https://zambo.dev/aer1/corpus.json
