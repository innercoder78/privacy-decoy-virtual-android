#!/usr/bin/env python3
"""Disposable unsigned ZIP controls, NEVER the independent-build positive result."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
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

    def signing_fixture(self, cert=b"fixture-cert", sig=b"fixture-signature", key=b"fixture-key",
                        algorithm=0x0103, signature_algorithm=None, extra=(), v2=None):
        # Structural transport only: these bytes are NOT cryptographic signatures.
        import struct
        lp = lambda data: struct.pack("<I", len(data)) + data
        digests = lp(struct.pack("<I", algorithm) + lp(b"fixture-digest"))
        signatures = lp(struct.pack("<I", algorithm if signature_algorithm is None else signature_algorithm) + lp(sig))
        data = lp(digests) + lp(lp(cert)) + lp(lp(struct.pack("<I", 7) + b"fixture-attribute"))
        signer = lp(data) + lp(signatures) + lp(key)
        value = lp(lp(signer)) if v2 is None else v2
        pairs = [(0x7109871a, value), (0x42726577, bytes(12)), *extra]
        payload = b"".join(struct.pack("<QI", len(value) + 4, identifier) + value for identifier, value in pairs)
        size = struct.pack("<Q", len(payload) + 24)
        return size + payload + size + b"APK Sig Block 42"

    def insert_signing_fixture(self, path, block):
        import struct
        raw = path.read_bytes()
        end = raw.rfind(b"PK\x05\x06")
        offset = struct.unpack_from("<I", raw, end + 16)[0]
        changed = bytearray(raw[:offset] + block + raw[offset:])
        struct.pack_into("<I", changed, end + len(block) + 16, offset + len(block))
        path.write_bytes(changed)

    def test_signing_parser_identifies_fields_and_preserves_unknown_blocks(self):
        block = self.signing_fixture(extra=[(0x12345678, b"opaque-private-fixture")])
        result = repro.signing_block_snapshot(block)
        signer = result["blocks"][0]["signers"][0]
        self.assertEqual(signer["signatures"][0]["id"], 0x0103)
        self.assertEqual(signer["signatures"][0]["algorithm"], "RSA-PKCS1-v1_5-SHA256")
        self.assertEqual(signer["certificates"][0]["sha256"], repro.digest(b"fixture-cert"))
        self.assertEqual(signer["public_key"]["sha256"], repro.digest(b"fixture-key"))
        self.assertTrue(result["blocks"][1]["all_zero"])
        self.assertEqual(result["blocks"][2]["kind"], "Unknown")
        self.assertNotIn("opaque-private-fixture", repro.canonical(result))
        for algorithm in (0x0101, 0x0201, 0x0301, 0x9999):
            value = repro.signing_block_snapshot(self.signing_fixture(algorithm=algorithm))
            self.assertEqual(value["blocks"][0]["signers"][0]["signatures"][0]["id"], algorithm)
        self.assertEqual(value["blocks"][0]["signers"][0]["signatures"][0]["algorithm"], "Unknown")

    def test_signing_parser_rejects_bounds_duplicates_and_incomplete_records(self):
        import struct
        block = self.signing_fixture()
        for size in range(len(block)):
            with self.assertRaises(ValueError):
                repro.signing_block_snapshot(block[:size])
        invalid = [self.signing_fixture(cert=b""), self.signing_fixture(sig=b""),
                   self.signing_fixture(key=b""), self.signing_fixture(signature_algorithm=0x0101),
                   self.signing_fixture(extra=[(0x7109871a, b"duplicate")]),
                   self.signing_fixture(v2=struct.pack("<I", 0)),
                   self.signing_fixture(v2=struct.pack("<I", 0xffffffff)),
                   self.signing_fixture(v2=struct.pack("<I", 0) + b"trailing")]
        for index, value in ((0, 1), (8, 3), (8, 0xffffffffffffffff)):
            bad = bytearray(block)
            struct.pack_into("<Q", bad, index, value)
            invalid.append(bad)
        bad = bytearray(block)
        struct.pack_into("<I", bad, 16, 0x9999)  # No v2 block remains.
        invalid.append(bad)
        signer = repro.signing_block_snapshot(block)["blocks"][0]["signers"][0]
        for field in (signer["signed_data"], signer["public_key"], signer["certificates"][0],
                      signer["signatures"][0]["value"], signer["digests"][0]["value"]):
            bad = bytearray(block)
            struct.pack_into("<I", bad, field["offset"] - 4, 0xffffffff)
            invalid.append(bad)
        invalid.append(self.signing_fixture(extra=[(0x10000 + i, b"x") for i in range(63)]))
        invalid.append(block + bytes(4 * 1024 * 1024))
        for bad in invalid:
            with self.assertRaises(ValueError):
                repro.signing_block_snapshot(bad)

    def test_signing_snapshot_binds_verified_identity_and_reports_mutations(self):
        self.insert_signing_fixture(self.a, self.signing_fixture())
        verified = dict(self.sign, certificate_sha256=repro.digest(b"fixture-cert"))
        original = repro.verified_signing_snapshot(self.a, verified)
        for bad in (self.sign, dict(verified, schemes={"v2": "false"})):
            with self.assertRaisesRegex(ValueError, "verified signer"):
                repro.verified_signing_snapshot(self.a, bad)
        for kwargs, field in (({"sig": b"changed-signature"}, "signatures"),
                              ({"key": b"changed-key"}, "public_key"),
                              ({"cert": b"changed-cert"}, "certificates")):
            changed = repro.signing_block_snapshot(self.signing_fixture(**kwargs))
            baseline = repro.signing_block_snapshot(self.signing_fixture())
            differences = repro.signing_differences(baseline, changed)
            self.assertTrue(any(field in path for path in differences))
        self.assertEqual(repro.signing_differences(original, copy.deepcopy(original)), [])

    def test_every_signing_block_difference_still_fails_whole_apk(self):
        for block in (self.signing_fixture(sig=b"changed-signature"),
                      self.signing_fixture(extra=[(0x12345678, b"unknown")]),
                      self.signing_fixture(extra=[(0x504b4453, b"metadata")])):
            self.write(self.a)
            self.write(self.b)
            self.insert_signing_fixture(self.a, self.signing_fixture())
            self.insert_signing_fixture(self.b, block)
            result = self.rejected()
            self.assertEqual(result["changed_entries"], [])
            self.assertIn("signing_block", result["changed_regions"])

    def test_signature_mutation_control_requires_real_verifier_rejection(self):
        self.insert_signing_fixture(self.a, self.signing_fixture())
        verified = dict(self.sign, certificate_sha256=repro.digest(b"fixture-cert"))
        report = repro.verified_signing_snapshot(self.a, verified)
        original = self.a.read_bytes()
        verifier = Path(self.tmp.name) / "verifier-fixture"
        verifier.write_bytes(b"not executable")
        with patch.object(repro.sys, "platform", "linux"), patch.dict(repro.os.environ, GITHUB_ACTIONS="true"):
            for i, (status, text) in enumerate(((1, "DOES NOT VERIFY"), (0, "Verifies"), (2, "failure"), (1, ""))):
                output = Path(self.tmp.name) / (str(i) + ".apk")
                completed = repro.subprocess.CompletedProcess([], status, text, "")
                with patch.object(repro.subprocess, "run", return_value=completed) as run:
                    if i == 0:
                        self.assertTrue(repro.signing_mutation_control(self.a, report, verifier, output)["altered_signature_rejected"])
                    else:
                        with self.assertRaises(ValueError):
                            repro.signing_mutation_control(self.a, report, verifier, output)
                    self.assertEqual(run.call_count, 1)
                self.assertEqual(self.a.read_bytes(), original)
                self.assertEqual(repro.byte_differences(original, output.read_bytes())["different_bytes"], 1)

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

    def test_byte_ranges_include_appended_bytes_and_bound_reporting(self):
        result = repro.byte_differences(b"abcd", b"xbcd!")
        self.assertEqual(result["ranges"], [[0, 1], [4, 5]])
        self.assertEqual(result["different_bytes"], 2)
        self.assertTrue(result["ranges_complete"])
        result = repro.byte_differences(b"ab" * 5000, b"ac" * 5000)
        self.assertEqual(result["range_count"], 5000)
        self.assertEqual(result["different_bytes"], 5000)
        self.assertFalse(result["ranges_complete"])

    def test_diagnostic_elf_section_hashes_detect_note_only_change(self):
        import struct
        raw = bytearray(512)
        raw[:6] = b"\x7fELF\x02\x01"
        struct.pack_into("<Q", raw, 40, 64)
        struct.pack_into("<HHH", raw, 58, 64, 3, 1)
        names = b"\0.shstrtab\0.note.gnu.build-id\0"
        raw[256:256 + len(names)] = names
        struct.pack_into("<IIQQQQIIQQ", raw, 128, 1, 3, 0, 0, 256, len(names), 0, 0, 1, 0)
        struct.pack_into("<IIQQQQIIQQ", raw, 192, 11, 7, 0, 0, 320, 20, 0, 0, 4, 0)
        before = repro.elf_sections(raw)
        snapshot = repro.diagnostic_elf(raw, Path("/private/checkout"), Path("/private/build"))
        self.assertFalse(snapshot["contains_checkout_path"])
        self.assertFalse(snapshot["contains_build_path"])
        self.assertEqual(repro.build_note(snapshot)["sha256"], before[1]["sha256"])
        raw[325] = 1
        after = repro.elf_sections(raw)
        changed = repro.diagnostic_elf(raw, Path("/private/checkout"), Path("/private/build"))
        self.assertNotEqual(repro.build_note(snapshot), repro.build_note(changed))
        self.assertEqual(before[0], after[0])
        self.assertNotEqual(before[1]["sha256"], after[1]["sha256"])
        self.assertEqual(before[1]["name"], ".note.gnu.build-id")
        with self.assertRaises(ValueError):
            repro.elf_sections(raw[:100])

    def test_diagnostic_command_facts_do_not_publish_private_paths(self):
        command = '/private/sdk/clang -g -O2 -fstack-protector-strong -o /private/out.o /private/input.c'
        facts = repro.command_facts(command)
        self.assertEqual(facts["flags"], ["-g", "-O2", "-fstack-protector-strong"])
        self.assertNotIn("private", repro.canonical(facts))
        self.assertNotEqual(facts["sha256"], repro.command_facts(command.replace("input.c", "other.c"))["sha256"])
        self.assertEqual(repro.command_facts(command + ' -fdebug-prefix-map=/private=/source')["prefix_map_options"], 1)

    def test_diagnostic_note_requires_exactly_one_section(self):
        for sections in ([], [{"name": ".debug_info"}],
                         [{"name": ".note.gnu.build-id"}] * 2):
            with self.assertRaises(ValueError):
                repro.build_note({"sections": sections})

    def test_diagnostic_path_presence_is_not_normalization(self):
        # Reuse a valid fixture, keeping path bytes outside its section payloads.
        import struct
        raw = bytearray(256)
        raw[:6] = b"\x7fELF\x02\x01"
        struct.pack_into("<Q", raw, 40, 64)
        struct.pack_into("<HHH", raw, 58, 64, 1, 0)
        raw[160:174] = b"/private/build"
        result = repro.diagnostic_elf(raw, Path("/private"), Path("/private/build"))
        # Path spelling is platform-specific; use exactly the encoded Path text.
        expected = str(Path("/private/build")).encode() in raw
        self.assertEqual(result["contains_build_path"], expected)
        self.assertEqual(result["sha256"], repro.digest(raw))

    def test_native_diagnostics_correspondence_and_missing_inputs(self):
        import struct
        raw = bytearray(512)
        raw[:6] = b"\x7fELF\x02\x01"
        struct.pack_into("<Q", raw, 40, 64)
        struct.pack_into("<HHH", raw, 58, 64, 3, 1)
        names = b"\0.shstrtab\0.note.gnu.build-id\0"
        raw[256:256 + len(names)] = names
        struct.pack_into("<IIQQQQIIQQ", raw, 128, 1, 3, 0, 0, 256, len(names), 0, 0, 1, 0)
        struct.pack_into("<IIQQQQIIQQ", raw, 192, 11, 7, 0, 0, 320, 20, 0, 0, 4, 0)
        checkout = Path(self.tmp.name) / "checkout"
        module = checkout / "android/gate0-harness"
        native = Path(self.tmp.name) / "stripped"
        entries = {}
        for abi in ("arm64-v8a", "x86_64"):
            build = module / ".cxx/RelWithDebInfo/fixture" / abi
            (build / "CMakeFiles").mkdir(parents=True)
            database = []
            for source in ("probe.c", "launch.c"):
                (build / (source + ".o")).write_bytes(raw)
                database.append({"directory": str(build), "file": source,
                                 "command": "clang -g -o " + source + ".o -c " + source})
            (build / "compile_commands.json").write_text(repro.canonical(database))
            for name in ("CMakeCache.txt", "build.ninja", "CMakeFiles/rules.ninja"):
                (build / name).write_text("fixture")
            unstripped = module / "build/intermediates/cxx/RelWithDebInfo/fixture/obj" / abi / "libsubstrate.so"
            unstripped.parent.mkdir(parents=True)
            unstripped.write_bytes(raw)
            name = "lib/" + abi + "/libsubstrate.so"
            (native / name).parent.mkdir(parents=True)
            (native / name).write_bytes(raw)
            entries[name] = raw
        self.write(self.a, entries)
        args = (checkout, {"cmake": checkout, "ndk": checkout / "sdk/ndk/version"},
                self.a, native, Path(self.tmp.name), "fixture")
        with patch.object(repro, "command", return_value="clang -g -Wl,--build-id=sha1"), \
                patch.object(repro, "mapping_control", return_value={"fixture_only": True}), patch("builtins.print"):
            repro.native_diagnostics(*args)
            changed = bytearray(raw)
            changed[325] = 1
            unstripped.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, "Build-ID changed"):
                repro.native_diagnostics(*args[:-1], "note-mutation")
            unstripped.write_bytes(raw)
            (native / name).write_bytes(changed)
            with self.assertRaisesRegex(ValueError, "packaged bytes"):
                repro.native_diagnostics(*args[:-1], "package-mutation")
            (native / name).write_bytes(raw)
            (build / "compile_commands.json").unlink()
            with self.assertRaisesRegex(ValueError, "compile database"):
                repro.native_diagnostics(*args[:-1], "missing-input")

    def test_public_commands_label_known_roots_and_hide_unknown_paths(self):
        result = repro.public_commands('/sdk/clang -g /checkout/source.c /secret/input.o',
                                      '/checkout', '/sdk')
        self.assertEqual(result[0][:3], ['<sdk>/clang', '-g', '<checkout>/source.c'])
        self.assertNotIn('secret', repro.canonical(result))
        self.assertIn('path_token_sha256', result[0][3])

    def test_mapping_flags_missing_changed_or_security_disabled_rejected(self):
        source, build = Path("source"), Path("build")
        flags = ["-fdebug-prefix-map=source=/pdva/jni/src", "-fdebug-prefix-map=build=/pdva/jni/build"]
        tokens = ["clang", "-g", "-fstack-protector-strong", *flags]
        self.assertEqual(repro.require_debug_mapping(tokens, source, build), flags)
        for bad in (tokens[:-1], tokens + ["-g0"], tokens[2:],
                    [x.replace("/pdva/jni/src", "/different") for x in tokens],
                    [x.replace("-fdebug-prefix-map=", "-ffile-prefix-map=") for x in tokens],
                    [x for x in tokens if x != "-fstack-protector-strong"]):
            with self.assertRaises(ValueError):
                repro.require_debug_mapping(bad, source, build)

    def mapping_elf(self, paths, code=b"code", debug=b"full debug fixture", extra=()):
        import struct
        names = b"\0.shstrtab\0.text\0.debug_info\0.debug_str\0.debug_line\0" + b"".join(
            name.encode() + b"\0" for name, _ in extra)
        payloads = [(".shstrtab", names), (".text", code), (".debug_info", debug),
                    (".debug_str", paths), (".debug_line", paths), *extra]
        raw = bytearray(64 + 64 * (len(payloads) + 1))
        raw[:6] = b"\x7fELF\x02\x01"
        struct.pack_into("<Q", raw, 40, 64)
        struct.pack_into("<HHH", raw, 58, 64, len(payloads) + 1, 1)
        for i, (name, data) in enumerate(payloads, 1):
            offset = len(raw)
            raw.extend(data)
            struct.pack_into("<IIQQQQIIQQ", raw, 64 + 64 * i, names.index(name.encode()),
                             3 if i == 1 else 1, 0, 0, offset, len(data), 0, 0, 1, 0)
        return bytes(raw)

    def test_mapping_control_positive_and_real_section_negative_controls(self):
        checkout, build = Path("private-checkout"), Path("private-checkout/build")
        mapped = self.mapping_elf(b"/pdva/jni/src\0/pdva/jni/build\0")
        paths = str(checkout).encode() + b"\0" + str(build).encode() + b"\0"
        unmapped = self.mapping_elf(paths)
        result = repro.verify_mapping_control(mapped, mapped, unmapped, checkout, build)
        self.assertTrue(result["non_debug_sections_equal"])
        for a, replay, b in ((mapped, unmapped, unmapped), (mapped, mapped, mapped),
                             (unmapped, unmapped, unmapped),
                             (mapped, mapped, self.mapping_elf(paths, code=b"mutant")),
                             (self.mapping_elf(b"/pdva/jni/src\0/pdva/jni/build\0", debug=b""),) * 2 + (unmapped,)):
            with self.assertRaises(ValueError):
                repro.verify_mapping_control(a, replay, b, checkout, build)
        for section in (".rela.debug_info", ".rela.text"):
            a = self.mapping_elf(b"/pdva/jni/build\0", extra=[(section, b"offset-a")])
            b = self.mapping_elf(paths, extra=[(section, b"offset-b")])
            if section == ".rela.debug_info":
                repro.verify_mapping_control(a, a, b, checkout, build)
            else:
                with self.assertRaisesRegex(ValueError, "non-debug"):
                    repro.verify_mapping_control(a, a, b, checkout, build)

    def test_mapping_control_runs_actual_arguments_only_with_fresh_outputs(self):
        checkout = Path(self.tmp.name) / "checkout"
        build = checkout / "build"
        source = checkout / "android/gate0-harness/src/main/cpp"
        packages = {"ndk": checkout / "ndk"}
        compiler = packages["ndk"] / "toolchains/llvm/prebuilt/linux-x86_64/bin/clang"
        maps = ["-fdebug-prefix-map=" + str(source) + "=/pdva/jni/src",
                "-fdebug-prefix-map=" + str(build) + "=/pdva/jni/build"]
        tokens = [str(compiler), "-g", "-fstack-protector-strong", *maps, "-o", "original.o", "-c", str(source / "probe.c")]
        entry = {"command": repro.shlex.join(tokens), "file": str(source / "probe.c")}
        output = Path(self.tmp.name) / "control"
        output.mkdir()
        calls = []
        def compile_fixture(args, cwd):
            calls.append((args, cwd))
            Path(args[args.index("-o") + 1]).write_bytes(b"fixture")
            return ""
        with patch.object(repro.sys, "platform", "linux"), patch.dict(repro.os.environ, GITHUB_ACTIONS="true"), \
                patch.object(repro, "command", side_effect=compile_fixture), \
                patch.object(repro, "verify_mapping_control", return_value={"fixture_only": True}):
            repro.mapping_control(entry, b"fixture", checkout, build, packages, output)
            self.assertEqual(len(calls), 2)
            for i, (args, cwd) in enumerate(calls):
                expected = list(tokens)
                expected[expected.index("-o") + 1] = str(output / ("probe.c." + ("mapped" if i == 0 else "unmapped") + ".o"))
                if i:
                    expected = [x for x in expected if x not in maps]
                self.assertEqual(args, expected)
                self.assertEqual(cwd, build)
            with self.assertRaisesRegex(ValueError, "already exists"):
                repro.mapping_control(entry, b"fixture", checkout, build, packages, output)
            with patch.object(repro, "command", side_effect=RuntimeError("compile failed")):
                entry["file"] = str(source / "launch.c")
                entry["command"] = repro.shlex.join(tokens[:-1] + [entry["file"]])
                with self.assertRaisesRegex(RuntimeError, "compile failed"):
                    repro.mapping_control(entry, b"fixture", checkout, build, packages, output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
