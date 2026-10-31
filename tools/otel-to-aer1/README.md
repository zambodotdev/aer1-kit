# otel-to-aer1: trace JSON in, AER-1 receipts out

A converter that takes agent trace exports and emits AER-1 receipt
records (draft-zambo-aer1-26). It exists so that work an agent did
inside an observability stack can be carried into the AER-1 record
layer, where each record is independently checkable: a reviewer can
recompute the commitments and confirm the saved record was not
changed after it was saved.

Two input shapes are supported:

- **OpenTelemetry OTLP JSON** (`resourceSpans`, as produced by OTel
  collectors and framework instrumentations), a bare span object, or
  a list of span objects.
- **Langfuse-style trace JSON**: a trace object with an
  `observations` array, or a single observation.

One receipt is emitted per span or observation. Standard library
only; Python 3.

## Run it

    python3 otel_to_aer1.py samples/otel-span.json
    python3 otel_to_aer1.py samples/langfuse-trace.json -o receipts.json
    python3 -m unittest test_otel_to_aer1 -v     # the test suite

## What the conversion records, and what it does not claim

The converter did not run the tool calls it converts. Every receipt
therefore carries the provenance class **LOGGED BY AGENT** (draft
Section 5): the recording system received a report of the action.
The receipt attests that the trace record was received and
committed, in that form, at conversion time. It does not attest
that the underlying call happened as the trace describes; that is
exactly the distinction the provenance classes exist to preserve.

`verification_status` is set to "verified" only after the finished
record passes the kit's own core check (`base/conformance.py`), or,
when the kit is not importable, a local recomputation of both
commitments under the same rules. A record that fails is never
emitted; the converter raises instead.

Errored spans and observations are converted, not dropped, with the
error recorded in the payload. A failed call is a recorded call.

## Field mapping

| AER-1 member | OTel source | Langfuse source |
|---|---|---|
| `created_at` | span `startTimeUnixNano` | observation `startTime` |
| `tool.name` | `gen_ai.tool.name` or `tool.name` attribute, else span name | observation `name` |
| `tool.version` | instrumentation scope version, else "unknown" | "unknown" (traces carry no tool version) |
| `tool.scope` | resource `service.name`, else "external" | trace `environment`, else "external" |
| payload `inputs` | first of `gen_ai.tool.call.arguments`, `tool.arguments`, `gen_ai.input.messages`, `input`, `prompt` (parsed as JSON when it parses); else the full span attribute map under `span_attributes` | observation `input` |
| payload `outputs` | first of `gen_ai.tool.call.result`, `tool.result`, `gen_ai.output.messages`, `output`, `response`; on span error, `{"error": status message}` plus any result | observation `output`; on `level: ERROR`, `{"error": statusMessage}` plus any output |
| `execution_context.model` | `gen_ai.response.model` / `gen_ai.request.model` / `llm.model_name` | observation `model` |
| `execution_context.framework` | instrumentation scope name and version | `{"name": "langfuse"}` |
| `execution_context.source` | first of `peer.service`, `db.system`, `url.full`, `http.url`, `server.address` | not set |

`execution_context` is producer-asserted context under draft
Section 3.2: it sits outside the hash-bound core and a verifier
surfaces it as recorded, never as an attested fact. The converter
follows that rule rather than upgrading trace metadata into the
commitment.

## Published byte layout (draft Section 3.3)

The input commitment is only checkable because its byte layout is
stated. It is:

- **Canonical payload**: the JSON object `{"inputs": ..., "outputs":
  ..., "tool": ...}` serialized with member names sorted by Unicode
  code point at every level, no whitespace outside strings, and the
  string escaping of draft Section 7.1 (Python `json.dumps` with
  `ensure_ascii=True`). `canonical_bytes` is the base64 of those
  bytes; `output_hash` is their SHA-256.
- **Input commitment**: `input_hash` is the SHA-256 of the canonical
  serialization, under the same layout, of the payload's `inputs`
  value alone.

## Out of scope, deliberately

- **Publication.** Assigning the public URL of draft Section 9,
  keeping records, and anchoring them (Section 10) belong to a
  producer. This tool emits records; it does not publish them.
- **Packaging.** This folder is source in the kit repository. No
  package is published from it; a PyPI release is a separate
  decision.
- **Span-to-chain assembly.** Receipts are emitted per span. Building
  a Section 7 timeline or a Section 8 workflow record over a whole
  trace is a natural next step and is not hidden inside this tool.
