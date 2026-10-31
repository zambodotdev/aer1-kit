# AER-1 and SCITT: a bridge note

How the AER-1 receipt format (draft-zambo-aer1-26) relates to the
SCITT architecture (RFC 9943), concept by concept: what corresponds,
what does not, and what an implementation that connects the two would
need to build.

This note is descriptive. It does not claim that AER-1 is part of
SCITT, that any SCITT Transparency Service has registered an AER-1
record, or that either specification endorses the other. Where the two
do not correspond, this note says so.

## First, a naming hazard

The word "receipt" names different objects in the two specifications,
and confusing them is the most likely bridge error.

- An **AER-1 receipt** is the execution record itself: a JSON object
  that records one tool call, carries hash commitments over the exact
  output bytes, and resolves at a stable public URL.
- A **SCITT Receipt** (RFC 9943, Section 3, defined by RFC 9942) is a
  COSE proof object: a Transparency Service's attestation that a
  Signed Statement was included in its Verifiable Data Structure. It
  records nothing about any execution.

In this note, "receipt" alone means the AER-1 object. The SCITT
object is always "SCITT Receipt".

## The composition point that already exists

AER-1 does not compete with the transparency-service layer; it
already names it. Section 15 of draft-zambo-aer1-26 states that "AER-1
composes with the transparency-service slot rather than competing
with it", and Section 10 defines an anchor of type "scitt": the
record's anchored_digest is registered with a SCITT Transparency
Service as the payload digest of a Signed Statement, and the
resulting inclusion proof is carried in the anchor's proof object as
`service` (the Transparency Service URL) and `cose_receipt` (the
base64-encoded COSE Receipt the service returned).

RFC 9943 provides the other half of that pattern. Its Section 6.2
covers statements made over the hash of a payload rather than the
payload bytes, for payloads too large or too sensitive to send to a
remote service. Registering a digest is a use the SCITT architecture
anticipates.

So the bridge has a defined shape: the AER-1 record stays where it
is, publicly resolvable and checkable on its own terms, and a digest
of it gains a second, independent inclusion proof in a Transparency
Service's append-only log. Section 10.2's rule governs the whole
arrangement: binding does not transfer claims. AER-1 core
verification neither requires nor is changed by a SCITT registration,
and a SCITT Receipt over a digest does not upgrade anything the
AER-1 record itself attests.

## Concept mapping

| AER-1 concept | SCITT concept | Correspondence |
|---|---|---|
| Receipt (JSON execution record, Section 3) | Statement (the payload of a Signed Statement) | Partial. An AER-1 receipt is serializable information about an artifact (here, an execution), which is what a Statement is. As a payload it is opaque to the Transparency Service and would travel under a content type in the COSE protected header. AER-1 has no registered media type: its IANA section records no actions. A bridge must choose and document a content type (plain JSON is the honest interim choice) and accept that no registry entry backs it yet. |
| anchored_digest: the output_hash hex for a receipt, the merkle_root for a workflow, the chain commitment's final_entry_digest for a timeline (Section 10) | A Statement made over the hash of a payload (RFC 9943, Section 6.2) | Direct. This is the value AER-1 Section 10 specifies for registration, and the digest-statement pattern is the one RFC 9943 Section 6.2 describes. |
| Recording system (the producer that issues receipts) | Issuer | Partial, and the gap matters. A SCITT Issuer signs: a Signed Statement is a COSE_Sign1 envelope whose protected header carries the Issuer's identity as CWT claims, and the signature is what makes the statement attributable and non-repudiable. An AER-1 producer does not sign. Section 13 is explicit: issuer authentication is not part of the specification, no signature scheme is defined, and anyone can mint a well-formed receipt. A bridge therefore has to add a signing layer that AER-1 deliberately leaves out, using what Section 13 itself prescribes: a signature scheme documented alongside the receipt. Until it does, there is no Issuer, and nothing to register. |
| Anchor of type "scitt", with `service` and `cose_receipt` in its proof object (Section 10) | SCITT Receipt (inclusion proof, RFC 9942), normally carried in the unprotected header of the Signed Statement, which is what makes it a Transparent Statement (RFC 9943, Section 3) | Direct in substance, different in carrier. The same proof object is produced by registration in both designs. SCITT stores it in the envelope's unprotected header; AER-1 stores a base64 copy in the anchor published alongside the receipt at its public URL (Section 10, anchor discovery), because the AER-1 record's own bytes are frozen at issuance and anchors are additive. |
| Public resolution and verification (Sections 6 and 9): resolve the record at its URL, recompute the commitments | Relying Party validation (RFC 9943, Section 7.1): verify the Issuer's signature and the SCITT Receipt's inclusion proof | Different mechanics, same role. An AER-1 check is recomputation over JSON and needs the live record. A SCITT check is signature and proof verification and works offline, "universally verifiable without online access to the TS" (RFC 9943, Section 4). A bridge verifier performs both, independently, and reports both outcomes without merging them. |
| Hash-chained job timeline (Section 7) and workflow Merkle root (Section 8) | Append-only Log and Verifiable Data Structure (RFC 9943, Section 3; RFC 9942) | No direct correspondence; the two compose instead. Both are append-only structures whose contents can be checked for gaps and reordering. They commit different things: an AER-1 chain binds the steps of one job under one recording system, and even then Section 7.3 is explicit that end truncation is not detectable from the chain alone. A Transparency Service log binds the registration order of statements from many Issuers, under the service's key, with Auditors checking its consistency. Neither substitutes for the other; anchoring a chain commitment digest in a Transparency Service is exactly the external commitment Section 7.3 calls for. |
| Provenance classes: executed by the recording system, observed via gateway, logged by agent (Section 5) | No counterpart | None. SCITT envelopes carry metadata a Registration Policy can inspect, but the architecture defines no provenance semantics and no rule against upgrading a report into an observation. A bridge must not let a SCITT registration blur an AER-1 provenance class: a logged-by-agent record registered in a Transparency Service is still a logged-by-agent record. |
| No counterpart | Registration Policy (RFC 9943, Sections 3 and 5.1.1): the preconditions a Transparency Service enforces before registering a Signed Statement | None on the AER-1 side, by design. AER-1 publication is the producer's act, at a public URL, with no gatekeeper. A Transparency Service may impose policies on AER-1 digest statements (for example, accepting only statements from one Issuer identity), and those policies are the service's, not AER-1's. |
| Corrections by supersession: a correcting receipt carries the superseded id in its supersedes member; the original record is never rewritten (Sections 3 and 9) | Registering a new Signed Statement about the same Subject, with the same iss and sub claims (RFC 9943, Section 6.3) | Parallel pattern, different mechanics. Both systems refuse in-place edits and express correction as a new, linked record. The link is a receipt member in one design and shared claims in the other. |

## What a bridge implementation needs

1. **An Issuer identity and key for the producer.** Key generation,
   storage, rotation, and compromise handling (RFC 9943, Section 9.4)
   are all outside AER-1. The bridge owns them entirely.
2. **A signature scheme documented alongside the receipt**, as
   AER-1 Section 13 requires of any deployment that needs to bind
   records to their issuer. In practice: COSE_Sign1, with the payload
   detached or set to the digest per RFC 9943 Section 6.2, protected
   headers carrying the algorithm, a key identifier, a content type,
   and CWT claims with iss (the producer) and sub (the receipt id or
   its public URL are the natural subjects).
3. **A Transparency Service client**: submit the Signed Statement,
   satisfy the service's Registration Policy and client
   authentication (RFC 9943, Section 6.3), and retrieve the SCITT
   Receipt when the service issues it, which may be asynchronous.
4. **The anchor write-back**: publish the returned proof as an
   AER-1 anchor of type "scitt" next to the record, with `service`
   and `cose_receipt` as Section 10 specifies. The record's bytes do
   not change; anchors are discovered alongside the record, never
   inside it.
5. **A two-layer verifier**: run AER-1 Section 6 verification and
   SCITT validation as separate procedures with separate outcomes.
   A failure in either layer is reported as that layer's failure.
   Section 10's limits apply in full: a verified anchor proves the
   digest existed no later than the anchor's publication time, and
   nothing about whether the recorded content was correct,
   authorized, or truthful.
6. **A content-type decision**, documented with the bridge, since
   AER-1 has no registered media type (see the mapping table).

## What does not correspond, stated plainly

- AER-1 has no signatures and no issuer authentication. SCITT is
  built on both. The bridge adds them; the format does not grow them.
- AER-1 has no Registration Policy and no gatekeeper. Publication is
  unilateral and resolution is public and account-free.
- AER-1 has no cross-issuer append-only log, and its chains prove
  order within one job, not global registration order.
- SCITT has no execution semantics: no tool calls, no per-call
  issuance rule (AER-1 requires a receipt even for a rejected call),
  no provenance classes, and no requirement that a statement resolve
  at a public URL.
- Neither system's proof says the underlying work was done well, or
  done at all beyond what the record attests. AER-1 verification
  shows a saved result was not changed after it was saved. A SCITT
  Receipt shows a statement was included in a log. A bridged record
  shows both of those things, and nothing more.

## Sources

- RFC 9943, "An Architecture for Trustworthy and Transparent Digital
  Supply Chains", Sections 3 to 7 and 9.4:
  https://www.rfc-editor.org/rfc/rfc9943
- RFC 9942 (SCITT Verifiable Data Structures and Receipt formats),
  referenced by RFC 9943 for the Receipt definition.
- draft-zambo-aer1-26, Sections 3, 5, 6, 7, 9, 10, 13, and 15:
  https://datatracker.ietf.org/doc/draft-zambo-aer1/26/
