#!/usr/bin/env python3
"""Convert agent trace JSON into AER-1 receipt records.

Reads OpenTelemetry OTLP-JSON spans (as exported by agent frameworks
and collectors) or a Langfuse-style trace export, and emits one AER-1
receipt record (draft-zambo-aer1-26, Section 3) per span or
observation. The conversion is a recording act, not an execution:
every emitted receipt carries the provenance class LOGGED BY AGENT,
which is what Section 5 defines for an action an external system
reported to the recording system. The receipt attests that the trace
record was received and committed, not that the converter ran or
observed the underlying tool call.

Design rules, all from the draft:

- The committed payload follows the reference producer shape: a JSON
  object carrying "inputs", "outputs", and "tool" (the kit's
  check_reference_profile convention). The canonical bytes are that
  object serialized with member names sorted by Unicode code point,
  no whitespace outside strings, and the string escaping of
  Section 7.1 (Python json.dumps with ensure_ascii=True). That
  serialization is the published byte layout for both the output
  commitment (Section 4) and the input commitment (Section 3.3).
- input_hash is computed over the canonical serialization of the
  payload's "inputs" value alone, under the same layout.
- Receipts are emitted at schema version "0.4", so metadata_hash is
  REQUIRED (Table 1) and is computed exactly as Section 3.1 defines.
- An errored span still produces a receipt, with the error recorded
  in the payload's "outputs". The every-call rule of Section 3 is
  about producers, but the converter follows the same principle: a
  failed call is a recorded call, never a dropped one.
- verification_status is set to "verified" only after the finished
  record passes the kit's own core check (base/conformance.py
  check(), the Section 6 commitment steps that can be evaluated
  offline: shape, output commitment recomputation, metadata
  commitment recomputation). If the kit is not importable, the
  converter recomputes both commitments locally under the same rules
  before setting the status. A record that fails either path is
  never emitted; the converter raises instead.

Nothing here publishes a receipt. Publication (assigning the public
URL of Section 9, keeping the record, anchoring it) is a producer's
job and is deliberately out of scope.

Standard library only.

Usage:
    python3 otel_to_aer1.py INPUT.json [-o OUT.json]
                            [--format otel|langfuse|auto]
"""

import argparse
import base64
import hashlib
import importlib.util
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "0.4"
PROVENANCE_CLASS = "LOGGED BY AGENT"


# ---------------------------------------------------------------- kit

def _load_kit():
    """Import the kit's base conformance module, if it is present.

    The kit lives at <repo>/base/conformance.py and this tool at
    <repo>/tools/otel-to-aer1/. Returns the module or None.
    """
    kit_path = Path(__file__).resolve().parents[2] / "base" / "conformance.py"
    if not kit_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("aer1_kit_conformance",
                                                  kit_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


KIT = _load_kit()


# ------------------------------------------------------- canonical form

def canonical_bytes(obj):
    """The published byte layout: sorted member names, no whitespace
    outside strings, Section 7.1 string escaping."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


def _digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def metadata_digest(receipt_core):
    """Section 3.1 metadata_hash over the canonical metadata block."""
    tool = receipt_core["tool"]
    block = {
        "created_at": receipt_core["created_at"],
        "id": receipt_core["id"],
        "output_hash": receipt_core["output_hash"],
        "provenance_class": receipt_core["provenance_class"],
        "receipt_schema_version": receipt_core["receipt_schema_version"],
        "tool": {
            "name": tool["name"],
            "scope": tool["scope"],
            "version": tool["version"],
        },
    }
    return _digest(canonical_bytes(block))


# ------------------------------------------------------------- building

def build_receipt(*, tool_name, tool_version, tool_scope, created_at,
                  inputs, outputs, execution_context=None):
    """Assemble one AER-1 receipt record and self-verify it."""
    payload = {"inputs": inputs, "outputs": outputs, "tool": tool_name}
    raw = canonical_bytes(payload)
    receipt = {
        "id": str(uuid.uuid4()),
        "receipt_schema_version": SCHEMA_VERSION,
        "created_at": created_at,
        "tool": {
            "name": tool_name,
            "version": tool_version,
            "scope": tool_scope,
        },
        "provenance_class": PROVENANCE_CLASS,
        "canonical_bytes": base64.b64encode(raw).decode("ascii"),
        "output_hash": _digest(raw),
        "input_hash": _digest(canonical_bytes(inputs)),
    }
    receipt["metadata_hash"] = metadata_digest(receipt)
    if execution_context:
        receipt["execution_context"] = execution_context
    # The status member is part of the record, so it is set before
    # the self-check runs; the check then decides whether the record
    # may be emitted at all. A record that fails raises here and is
    # never returned, so no emitted record carries an unearned
    # "verified".
    receipt["verification_status"] = "verified"
    _self_verify(receipt)
    return receipt


def _self_verify(receipt):
    """Run the Section 6 commitment checks that work offline.

    Uses the kit's check() when the kit is importable; otherwise
    recomputes both commitments locally. Raises ValueError on any
    failure: a record that does not pass is not emitted.
    """
    if KIT is not None:
        failures = KIT.check(receipt)
        if failures:
            raise ValueError("kit check failed: " + "; ".join(failures))
        return
    raw = base64.b64decode(receipt["canonical_bytes"], validate=True)
    if _digest(raw) != receipt["output_hash"]:
        raise ValueError("output_hash does not recompute")
    if metadata_digest(receipt) != receipt["metadata_hash"]:
        raise ValueError("metadata_hash does not recompute")


# ------------------------------------------------------------ timestamps

def rfc3339_from_unix_nano(nano):
    """OTLP startTimeUnixNano (string or int) to RFC 3339, UTC, ms."""
    ns = int(nano)
    seconds, rem_ns = divmod(ns, 1_000_000_000)
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    ms = rem_ns // 1_000_000
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{ms:03d}Z"


def rfc3339_from_iso(text):
    """ISO 8601 timestamp (Langfuse startTime) to RFC 3339, UTC, ms."""
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{dt.microsecond // 1000:03d}Z"


# ---------------------------------------------------------------- OTel

def _otlp_value(value):
    """Unwrap one OTLP AnyValue into a plain Python value."""
    if not isinstance(value, dict):
        return value
    if "stringValue" in value:
        return value["stringValue"]
    if "intValue" in value:
        return int(value["intValue"])
    if "doubleValue" in value:
        return value["doubleValue"]
    if "boolValue" in value:
        return value["boolValue"]
    if "arrayValue" in value:
        return [_otlp_value(v) for v in value["arrayValue"].get("values", [])]
    if "kvlistValue" in value:
        return {kv["key"]: _otlp_value(kv.get("value", {}))
                for kv in value["kvlistValue"].get("values", [])}
    return value


def _attr_map(attributes):
    out = {}
    for attr in attributes or []:
        out[attr.get("key")] = _otlp_value(attr.get("value", {}))
    return out


def _maybe_json(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return value
    return value


def _first(attrs, *keys):
    for key in keys:
        if key in attrs and attrs[key] not in (None, ""):
            return attrs[key]
    return None


INPUT_KEYS = ("gen_ai.tool.call.arguments", "tool.arguments",
              "gen_ai.input.messages", "input", "prompt")
OUTPUT_KEYS = ("gen_ai.tool.call.result", "tool.result",
               "gen_ai.output.messages", "output", "response")


def convert_otel_span(span, *, service_name, scope_name, scope_version):
    attrs = _attr_map(span.get("attributes"))
    tool_name = (_first(attrs, "gen_ai.tool.name", "tool.name")
                 or span.get("name") or "unknown")
    raw_inputs = _first(attrs, *INPUT_KEYS)
    inputs = (_maybe_json(raw_inputs) if raw_inputs is not None
              else {"span_attributes": attrs})
    status = span.get("status") or {}
    status_code = status.get("code", 0)
    raw_output = _first(attrs, *OUTPUT_KEYS)
    output = _maybe_json(raw_output) if raw_output is not None else None
    if status_code == 2:  # OTLP StatusCode.Error
        outputs = {"error": status.get("message") or "span error"}
        if output is not None:
            outputs["result"] = output
    elif output is not None:
        outputs = output
    else:
        outputs = {"status_code": status_code}
    context = {}
    model = _first(attrs, "gen_ai.response.model", "gen_ai.request.model",
                   "llm.model_name")
    if model:
        context["model"] = {"name": str(model)}
    if scope_name:
        framework = {"name": str(scope_name)}
        if scope_version:
            framework["version"] = str(scope_version)
        context["framework"] = framework
    source = _first(attrs, "peer.service", "db.system", "url.full",
                    "http.url", "server.address")
    if source:
        context["source"] = str(source)
    return build_receipt(
        tool_name=str(tool_name),
        tool_version=str(scope_version) if scope_version else "unknown",
        tool_scope=service_name or "external",
        created_at=rfc3339_from_unix_nano(span["startTimeUnixNano"]),
        inputs=inputs,
        outputs=outputs,
        execution_context=context or None,
    )


def convert_otel(doc):
    """OTLP JSON (resourceSpans) or a bare span / list of spans."""
    receipts = []
    if isinstance(doc, dict) and "resourceSpans" in doc:
        for resource_span in doc["resourceSpans"]:
            resource_attrs = _attr_map(
                (resource_span.get("resource") or {}).get("attributes"))
            service = resource_attrs.get("service.name") or "external"
            for scope_span in resource_span.get("scopeSpans", []):
                scope = scope_span.get("scope") or {}
                for span in scope_span.get("spans", []):
                    receipts.append(convert_otel_span(
                        span,
                        service_name=service,
                        scope_name=scope.get("name"),
                        scope_version=scope.get("version")))
        return receipts
    spans = doc if isinstance(doc, list) else [doc]
    for span in spans:
        receipts.append(convert_otel_span(
            span, service_name="external", scope_name=None,
            scope_version=None))
    return receipts


# ------------------------------------------------------------- Langfuse

def convert_langfuse_observation(obs, *, environment):
    name = obs.get("name") or "unknown"
    inputs = obs.get("input") if obs.get("input") is not None else {}
    output = obs.get("output")
    if obs.get("level") == "ERROR":
        outputs = {"error": obs.get("statusMessage") or "observation error"}
        if output is not None:
            outputs["result"] = output
    elif output is not None:
        outputs = output
    else:
        outputs = {"status": obs.get("statusMessage") or "no output recorded"}
    context = {"framework": {"name": "langfuse"}}
    if obs.get("model"):
        context["model"] = {"name": str(obs["model"])}
    return build_receipt(
        tool_name=str(name),
        tool_version="unknown",
        tool_scope=environment or "external",
        created_at=rfc3339_from_iso(obs["startTime"]),
        inputs=inputs,
        outputs=outputs,
        execution_context=context,
    )


def convert_langfuse(doc):
    """A Langfuse trace export (with observations) or one observation."""
    if isinstance(doc, dict) and isinstance(doc.get("observations"), list):
        environment = doc.get("environment")
        return [convert_langfuse_observation(obs, environment=environment)
                for obs in doc["observations"]]
    return [convert_langfuse_observation(doc, environment=None)]


# ------------------------------------------------------------------ CLI

def detect_format(doc):
    if isinstance(doc, dict) and "resourceSpans" in doc:
        return "otel"
    if isinstance(doc, dict) and "observations" in doc:
        return "langfuse"
    if isinstance(doc, dict) and "startTimeUnixNano" in doc:
        return "otel"
    if isinstance(doc, dict) and "startTime" in doc:
        return "langfuse"
    if isinstance(doc, list) and doc and "startTimeUnixNano" in doc[0]:
        return "otel"
    raise ValueError("cannot detect input format; pass --format")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert OTel / Langfuse trace JSON to AER-1 receipts.")
    parser.add_argument("input", help="trace JSON file")
    parser.add_argument("-o", "--output", help="write receipts here "
                        "(default: stdout)")
    parser.add_argument("--format", choices=("otel", "langfuse", "auto"),
                        default="auto")
    args = parser.parse_args(argv)
    doc = json.loads(Path(args.input).read_text(encoding="utf-8"))
    fmt = detect_format(doc) if args.format == "auto" else args.format
    receipts = convert_otel(doc) if fmt == "otel" else convert_langfuse(doc)
    text = json.dumps(receipts, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
