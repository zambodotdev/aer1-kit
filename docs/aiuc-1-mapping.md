# AER-1 and AIUC-1: requirement E015

A technical mapping between the AER-1 receipt format
(draft-zambo-aer1-26) and AIUC-1 requirement E015, "Log AI system
activity", the requirement in the AIUC-1 standard that specifies what
an AI system's logs must capture and how they must be protected.

This document is a technical mapping, not an audit and not a
certification claim. AIUC-1 certifies organisations and deployments,
assessed by accredited auditors against the whole standard. A record
format can supply evidence toward one requirement. It cannot certify
anything, and nothing here suggests that using AER-1 makes a
deployment AIUC-1 compliant.

## Scope, and why only one requirement is mapped

AIUC-1 is organised in six domains. Domain E, Accountability, covers
failure plans, ownership, vendor due diligence, logging,
transparency, and quality management. Most of those are
organisational controls: named owners, documented approvals,
diligence processes. A record format has nothing to say about them,
and this document does not pretend otherwise.

E015 is different in kind. It specifies log content, log storage,
and log integrity: the properties a record format either has or does
not have. It is also the requirement whose own crosswalks point at
record-keeping law, including Articles 12 and 19 of the EU AI Act
and ISO/IEC 42001 control A.6.2.8 on recording of event logs. E015
is therefore the one requirement mapped here, in full, against its
four published evidence components (E015.1 to E015.4). The standard
text was read at aiuc-1.com on 31 October 2026; AIUC-1 is updated
quarterly, and this mapping should be re-read against the current
text before it is relied on.

E015 itself: "Maintain logs of AI system processes, actions, and
agent outputs where permitted to support incident investigation,
auditing, and explanation of AI system behavior." Application:
Mandatory. Type: Detective.

Status labels match the companion EU AI Act mapping in this
repository: **Covered at the record layer** means AER-1 defines the
record and the rule that produces it; **Partial** means AER-1
supplies part of what the component calls for, with the gap named;
**Not covered** means AER-1 has no mechanism for it.

## The mapping

| Component | What it calls for | AER-1 mechanism | Status | Gap |
|---|---|---|---|---|
| E015.1, Logging implementation | Capturing system activity details to support incident investigation and behaviour explanation: logging inputs, processing steps, outputs, and metadata. Example evidence: example log entries showing captured information (timestamps, inputs, outputs, user actions). | Every tool call a producer receives produces a receipt, executed or rejected (Section 3). The record carries the time of creation, the tool name, version and caller scope, and a commitment over the exact output bytes; the reference payload shape carries the inputs and outputs themselves, and an optional input_hash commits to the exact recorded input under a published byte layout (Section 3.3). A rejected call records the requested tool, the arguments as received, and the error returned. | Covered at the record layer | The record covers tool calls. Activity that never reaches a producer as a tool call is not in it, and which systems route their activity through a producer is a deployment decision. |
| E015.2, AI agent logging implementation | Capturing full execution chains of agentic workflows: agent provenance metadata per execution (agent type identifier, creator or deployment origin); structured entries capturing tool call parameters and results; delegation chain records showing sub-agent handoffs with identity, task context, and outcome at each step; approval and authorisation records linked to execution (approver identity, timestamp, decision outcome); reasoning traces where available. | Provenance is a first-class, hash-bound part of the record: provenance_class states whether the recording system executed the call, observed it through a gateway, or received it as an agent's report (Section 5), field_provenance states per field which party wrote the value (Section 3.4), and execution_context can record the model, framework, source system, and environment (Section 3.2). Parameters and results are the payload and its commitments. Full chains exist at two levels: the Section 7 hash-chained timeline binds every step of one job, in order, each step carrying its receipt id, sequence position, tool, provenance class, and output commitment; Section 8 workflow receipts bind a multi-step workflow under one root. | Partial | Three named gaps. First, delegation across independent systems is not a defined AER-1 structure: a chain is one job's timeline under one recording system, and a handoff between separate systems is represented only as far as each side records its own receipts. Second, approval and authorisation records are not a core member; a deployment may add them as extra members, and verifiers will not check them. Third, reasoning traces are not recorded: AER-1 commits to outputs, defines no reasoning member, and output bytes should not be presented as a reasoning record. One further honesty note: execution_context is producer-asserted and sits outside the hash-bound core (Section 3.2), while the provenance class itself is bound. |
| E015.3, Log storage | Implementing log storage with appropriate retention periods, access controls, and data sanitation to support auditing and incident response. Example evidence: retention policy settings, access control configuration, PII masking, automatic deletion rules. | Records are stable: a receipt resolves at a public URL whose record must not be altered, and corrections arrive as new receipts linked by the supersedes member rather than as rewrites (Section 9). What is published can be limited before commitment: the logged-by-agent provenance class attests that the report was "received, redacted, timestamped, and chained" (Section 5), so redaction happens on the way in, before the commitment is computed. Anchors publish digests only: an anchor must not contain step content, tool inputs, or tool outputs (Section 10, privacy bound), so an integrity reference can be made public without making content public. | Partial | AER-1 sets no retention period and no deletion rules; both are storage policy. Access control runs the other way by design: resolution is public and needs no account, which suits transparency evidence and does not suit deployments whose logs must stay access-controlled. Sanitation beyond producer-side redaction is deployment policy, not format. |
| E015.4, Log integrity protection | Technical controls so that captured records cannot be modified or deleted after creation, and sequence integrity so that gaps, omissions, and reordering are detectable during incident investigation or audit. Example evidence given by the standard: write-once storage configuration, hashing of log entries, append-only database settings, third-party log management features. (Paraphrased: the standard's own adjective for this property is one AER-1 documents avoid; the functional description above is the standard's.) | Modification is detectable by recomputation: the output commitment binds the exact output bytes (Sections 3 and 4), the metadata commitment binds the identifier, creation time, tool, and provenance class (Section 3.1), and Section 6 verification recomputes both. Inside a Section 7 timeline, the chain rules make gaps, duplicate or out-of-order sequence numbers, and spliced entries from other jobs detectable, and require every link to be recomputed rather than trusted (Section 7.2). Section 10 anchors can fix a digest on infrastructure the record keeper does not control. | Covered at the record layer, with one stated condition | The condition is AER-1's own published limit, not a reading of it: end truncation of a chain is not detectable from the chain alone, because an attacker who can rebuild the links can present a shorter, internally valid chain (Section 7.3). It becomes detectable when the deployment publishes the chain commitment Section 7.3 defines (the final entry's digest and the entry count, published outside the chain) or anchors the final digest under Section 10. Deletion of an entire record is likewise detectable against those external references, not from the format alone. A deployment claiming E015.4 evidence from AER-1 should publish chain commitments as a matter of routine. |

## Reading this mapping honestly

Two of the four components are covered at the record layer, and
both carry conditions a reader should not skip: the record covers
tool calls rather than all system activity, and chain integrity
against truncation depends on an external commitment the deployment
must actually publish. The other two components are partial, with
the gaps named in the table: cross-system delegation, approvals,
reasoning traces, retention duration, and access control are either
deployment matters or things AER-1 does not do.

That is the shape of the honest claim. AER-1 is a strong answer to
"what exactly was recorded, and can anyone check it was not changed
afterwards". AIUC-1 asks that question as one requirement among
many, inside an organisational certification. This mapping covers
the one requirement, and no more.

## Sources

- AIUC-1 Standard, requirement E015 "Log AI system activity",
  including evidence components E015.1 to E015.4 and crosswalks,
  AIUC-1 Accountability domain, read 31 October 2026:
  https://www.aiuc-1.com/accountability/log-model-activity
- AIUC-1 Standard, overview and domain structure:
  https://standard.aiuc-1.com
- draft-zambo-aer1-26, Sections 3 to 10:
  https://datatracker.ietf.org/doc/draft-zambo-aer1/26/
