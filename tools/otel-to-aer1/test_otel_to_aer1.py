#!/usr/bin/env python3
"""Tests for otel_to_aer1.py.

The oracle is the kit itself: every emitted receipt must pass the
kit's core check (base/conformance.py check()) with zero failures and
the reference-producer profile check, and its metadata commitment
must equal the kit's own _metadata_digest over _metadata_block.

Run from this directory:
    python3 -m unittest test_otel_to_aer1 -v
"""

import base64
import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


conv = _load("otel_to_aer1", HERE / "otel_to_aer1.py")
kit = _load("aer1_kit_conformance", REPO / "base" / "conformance.py")

UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def _sample(name):
    return json.loads((HERE / "samples" / name).read_text(encoding="utf-8"))


def _payload(receipt):
    return json.loads(base64.b64decode(receipt["canonical_bytes"]).decode())


class ConverterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.otel_receipts = conv.convert_otel(_sample("otel-span.json"))
        cls.langfuse_receipts = conv.convert_langfuse(
            _sample("langfuse-trace.json"))
        cls.all_receipts = cls.otel_receipts + cls.langfuse_receipts

    def test_counts(self):
        self.assertEqual(len(self.otel_receipts), 2)
        self.assertEqual(len(self.langfuse_receipts), 3)

    def test_kit_core_check_passes(self):
        for receipt in self.all_receipts:
            self.assertEqual(kit.check(receipt), [],
                             f"kit check failed for {receipt['id']}")

    def test_reference_profile_passes(self):
        for receipt in self.all_receipts:
            self.assertEqual(kit.check_reference_profile(receipt), [])

    def test_metadata_commitment_matches_kit(self):
        for receipt in self.all_receipts:
            block = kit._metadata_block(receipt)
            self.assertIsNotNone(block)
            self.assertEqual(receipt["metadata_hash"],
                             kit._metadata_digest(block))

    def test_output_commitment_recomputes(self):
        for receipt in self.all_receipts:
            raw = base64.b64decode(receipt["canonical_bytes"])
            self.assertEqual(receipt["output_hash"],
                             "sha256:" + hashlib.sha256(raw).hexdigest())

    def test_input_commitment_matches_documented_layout(self):
        # Layout (converter README): the canonical serialization of
        # the payload's "inputs" value alone.
        for receipt in self.all_receipts:
            inputs = _payload(receipt)["inputs"]
            want = "sha256:" + hashlib.sha256(
                conv.canonical_bytes(inputs)).hexdigest()
            self.assertEqual(receipt["input_hash"], want)

    def test_provenance_and_status(self):
        for receipt in self.all_receipts:
            self.assertEqual(receipt["provenance_class"], "LOGGED BY AGENT")
            self.assertEqual(receipt["verification_status"], "verified")
            self.assertEqual(receipt["receipt_schema_version"], "0.4")

    def test_id_shape(self):
        for receipt in self.all_receipts:
            self.assertRegex(receipt["id"], UUID4_RE)
            self.assertNotEqual(
                receipt["id"], "00000000-0000-0000-0000-000000000000")

    def test_error_spans_are_recorded_not_dropped(self):
        otel_errors = [r for r in self.otel_receipts
                       if "error" in _payload(r)["outputs"]]
        self.assertEqual(len(otel_errors), 1)
        self.assertEqual(_payload(otel_errors[0])["outputs"]["error"],
                         "card declined")
        lf_errors = [r for r in self.langfuse_receipts
                     if "error" in _payload(r)["outputs"]]
        self.assertEqual(len(lf_errors), 1)
        self.assertEqual(_payload(lf_errors[0])["outputs"]["error"],
                         "card declined")

    def test_tool_identity_from_trace(self):
        weather = [r for r in self.otel_receipts
                   if r["tool"]["name"] == "get_weather"]
        self.assertEqual(len(weather), 1)
        self.assertEqual(weather[0]["tool"]["scope"], "checkout-agent")
        self.assertEqual(weather[0]["tool"]["version"], "0.1.30")
        self.assertEqual(weather[0]["created_at"], "2026-10-31T10:00:00.000Z")
        ctx = weather[0]["execution_context"]
        self.assertEqual(ctx["model"]["name"], "grok-4")
        self.assertEqual(ctx["framework"]["name"],
                         "openinference.instrumentation.langchain")

    def test_tampered_output_is_detected(self):
        receipt = json.loads(json.dumps(self.otel_receipts[0]))
        payload = _payload(receipt)
        payload["outputs"] = "rainy, 40F"
        receipt["canonical_bytes"] = base64.b64encode(
            conv.canonical_bytes(payload)).decode("ascii")
        failures = kit.check(receipt)
        self.assertTrue(any("output_hash" in f for f in failures),
                        f"expected output_hash failure, got {failures}")

    def test_tampered_metadata_is_detected(self):
        receipt = json.loads(json.dumps(self.otel_receipts[0]))
        receipt["tool"]["name"] = "get_forecast"
        failures = kit.check(receipt)
        self.assertTrue(any("metadata_hash" in f for f in failures),
                        f"expected metadata_hash failure, got {failures}")

    def test_format_detection(self):
        self.assertEqual(conv.detect_format(_sample("otel-span.json")),
                         "otel")
        self.assertEqual(conv.detect_format(_sample("langfuse-trace.json")),
                         "langfuse")


if __name__ == "__main__":
    unittest.main()
