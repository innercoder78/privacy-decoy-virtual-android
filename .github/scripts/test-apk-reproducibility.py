#!/usr/bin/env python3
"""Disposable unsigned ZIP controls, NEVER the independent-build positive result."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

SPEC = importlib.util.spec_from_file_location("repro", Path(__file__).with_name("apk-reproducibility.py"))
repro = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repro)


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.a = Path(self.tmp.name) / "a.zip"
        self.b = Path(self.tmp.name) / "b.zip"
        self.entries = {"AndroidManifest.xml": b"compiled manifest fixture",
                        "resources.arsc": b"compiled table fixture", "res/4j.xml": b"policy fixture",
                        "classes.dex": b"dex fixture", **{x: b"native fixture" for x in repro.NATIVE}}
        row = {"files": 1, "sha256": "c" * 64}
        self.inputs = {"source": repro.SOURCE, "tree": repro.TREE,
                       "tools": dict({k: dict(row) for k in repro.TOOL_NAMES}, java_version="fixture-only"),
                       "dependencies": dict(row), "verification": "d" * 64,
                       "configuration": {k: "e" * 64 for k in repro.CONFIG_NAMES}}
        self.sign = {"certificate_sha256": "a" * 64, "schemes": {"v2": "true"}}
        self.write(self.a)
        self.write(self.b)

    def write(self, path, entries=None, timestamp=(2020, 1, 1, 0, 0, 0), method=zipfile.ZIP_DEFLATED):
        with zipfile.ZipFile(path, "w") as archive:
            for name, data in (self.entries if entries is None else entries).items():
                item = zipfile.ZipInfo(name, timestamp)
                item.compress_type = method
                archive.writestr(item, data)

    def args(self):
        return (self.a, self.b, self.inputs, copy.deepcopy(self.inputs), self.sign, copy.deepcopy(self.sign))

    def rejected(self, args=None):
        args = self.args() if args is None else args
        result = repro.compare(*args)
        self.assertFalse(result["signed_bytes_equal"])
        with self.assertRaisesRegex(ValueError, "differ"):
            repro.verify_result(result, *args)
        return result

    def test_identical_disposable_unsigned_fixture(self):
        result = repro.compare(*self.args())
        repro.verify_result(result, *self.args())
        self.assertTrue(result["entry_content_equal"])
        self.assertEqual(len(result["a"]["entries"]), 7)

    def test_every_content_entry_mutation_rejected(self):
        for name in self.entries:
            with self.subTest(entry=name):
                entries = dict(self.entries)
                entries[name] += b"mutation"
                self.write(self.b, entries)
                result = self.rejected()
                self.assertEqual(result["changed_content"], [name])

    def test_missing_extra_and_missing_native_entries(self):
        for name in self.entries:
            with self.subTest(missing=name):
                self.write(self.b, {k: v for k, v in self.entries.items() if k != name})
                self.assertIn(name, self.rejected()["changed_content"])
        self.write(self.b, dict(self.entries, extra=b"extra"))
        self.assertEqual(self.rejected()["changed_content"], ["extra"])

    def test_zip_metadata_order_and_compression_are_not_normalized(self):
        variants = ({"timestamp": (2021, 1, 1, 0, 0, 0)}, {"method": zipfile.ZIP_STORED},
                    {"entries": dict(reversed(list(self.entries.items())))})
        for variant in variants:
            with self.subTest(variant=variant):
                self.write(self.b, **variant)
                self.assertTrue(self.rejected()["entry_content_equal"])

    def test_source_tool_dependency_configuration_and_missing_inputs_rejected(self):
        for key in self.inputs:
            for remove in (False, True):
                with self.subTest(key=key, remove=remove):
                    args = list(self.args())
                    if remove:
                        del args[3][key]
                    else:
                        args[3][key] = "0" * 40
                    with self.assertRaises(ValueError):
                        repro.compare(*args)

    def test_different_certificate_and_scheme_rejected(self):
        args = list(self.args())
        args[5]["certificate_sha256"] = "b" * 64
        self.assertFalse(self.rejected(args)["same_signing_identity_and_schemes"])
        args = list(self.args())
        args[5]["schemes"]["v3"] = "true"
        self.rejected(args)

    def test_incomplete_or_unverified_signing_rejected(self):
        for text in ("", "Verifies\n", "DOES NOT VERIFY\n", "Signer #1 certificate SHA-256 digest: " + "a" * 64):
            with self.assertRaises(ValueError):
                repro.signature(text)
        valid = "Verifies\nVerified using v2 scheme (APK Signature Scheme v2): true\nSigner #1 certificate SHA-256 digest: " + "a" * 64
        self.assertEqual(repro.signature(valid), self.sign)
        for text in (valid.replace("true", "false"), valid + "\nSigner #2 certificate SHA-256 digest: " + "b" * 64):
            with self.assertRaises(ValueError):
                repro.signature(text)

    def test_partial_malformed_and_substituted_result_rejected(self):
        valid = repro.compare(*self.args())
        for bad in (None, {}, {"signed_bytes_equal": True}, dict(valid, unknown=True), dict(valid, version=2)):
            with self.assertRaises(ValueError):
                repro.verify_result(bad, *self.args())
        self.write(self.b, dict(self.entries, extra=b"extra"))
        with self.assertRaises(ValueError):
            repro.verify_result(valid, *self.args())

    def test_missing_empty_truncated_and_duplicate_artifact_rejected(self):
        self.b.unlink()
        with self.assertRaises(ValueError):
            repro.compare(*self.args())
        for raw in (b"", b"PK", self.a.read_bytes()[:-1]):
            self.b.write_bytes(raw)
            with self.assertRaises((ValueError, zipfile.BadZipFile)):
                repro.compare(*self.args())
        self.write(self.b)
        with zipfile.ZipFile(self.b, "a") as archive:
            archive.writestr("classes.dex", b"duplicate")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            repro.compare(*self.args())

    def test_signing_region_bytes_are_preserved(self):
        raw = self.a.read_bytes()
        end = raw.rfind(b"PK\x05\x06")
        import struct
        offset = struct.unpack_from("<I", raw, end + 16)[0]
        # Structural fake block only; deliberately not a signature or signed APK.
        block = struct.pack("<Q", 32) + b"fixture!" + struct.pack("<Q", 32) + b"APK Sig Block 42"
        changed = bytearray(raw[:offset] + block + raw[offset:])
        struct.pack_into("<I", changed, end + len(block) + 16, offset + len(block))
        self.b.write_bytes(changed)
        result = self.rejected()
        self.assertEqual(result["changed_entries"], [])
        self.assertIn("signing_block", result["changed_regions"])

    def test_build_failure_is_not_success(self):
        import subprocess
        import sys
        with self.assertRaises(subprocess.CalledProcessError):
            repro.command([sys.executable, "-c", "raise SystemExit(7)"])

    def test_same_artifact_and_incomplete_shared_inputs_rejected(self):
        args = list(self.args())
        args[1] = args[0]
        with self.assertRaises(ValueError):
            repro.compare(*args)
        for key in ("tools", "dependencies", "configuration"):
            args = list(self.args())
            args[2] = copy.deepcopy(args[2])
            args[2][key] = args[3][key] = {"partial": True}
            with self.assertRaises(ValueError):
                repro.compare(*args)


if __name__ == "__main__":
    unittest.main(verbosity=2)
