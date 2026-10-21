#!/usr/bin/env python3
"""Deterministic desktop controls, not Android execution or teardown evidence."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SCRIPT = Path(__file__).with_name("desktop-readiness.py")
spec = importlib.util.spec_from_file_location("readiness", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
BUILD = {"source": "a" * 40, "apk_sha256": "b" * 64, "variant": "release"}
NATIVE = {name: {"sha256": "d" * 64, "role": role, "needed": ["libc.so"]}
          for name, role in (("lib/arm64-v8a/libsubstrate.so", "JNI-shared"),
                             ("lib/x86_64/libsubstrate.so", "JNI-shared"),
                             ("lib/arm64-v8a/libpdva_launch.so", "dynamic-PIE"))}
RESULT = {"build": BUILD, "validation": {"manifest": "passed", "native": NATIVE},
          "artifacts": {k: {"path": "synthetic/" + k, "sha256": v["sha256"]} for k, v in NATIVE.items()},
          "validator_sha256": "c" * 64, "analyzer_sha256": "e" * 64, "source_tree": "f" * 40,
          "scope": "offline-inspection-only"}


class JournalTests(unittest.TestCase):
    def setUp(self):
        m.STORE.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=m.STORE)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.jsonl"
        m.initialize(self.path, BUILD)

    def prepare(self):
        m.mutate(self.path, BUILD, "check-1", "PREPARED")

    def run_check(self):
        return m.execute(self.path, BUILD, "check-1", None, None, {})

    def state(self):
        return m.status(self.path)["operations"]["check-1"]["state"]

    def append_for_control(self, kind, op="check-1", data=None):
        with self.path.open("r+b") as stream:
            records = m.read(self.path)
            m.append(stream, records, kind, op, data or {})

    def test_not_started_and_readonly_plan(self):
        before = self.path.read_bytes()
        self.assertEqual(m.status(self.path)["state"], "NOT_STARTED")
        self.assertEqual(before, self.path.read_bytes())

    def test_prepared_is_safe_offline_continuation(self):
        self.prepare()
        self.assertEqual(self.state(), "PREPARED")
        with patch.object(m, "inspect", return_value=RESULT) as inspect:
            self.run_check()
        inspect.assert_called_once()
        self.assertEqual(self.state(), "COMPLETED")

    def test_durable_intent_precedes_dispatch(self):
        self.prepare()
        calls = []
        original = m.sync
        def sync(stream):
            original(stream)
            calls.append("synced")
        def inspect(*args):
            self.assertEqual(calls, ["synced"])
            self.assertEqual(m.decode(self.path.read_bytes())[-1]["kind"], "IN_PROGRESS")
            return RESULT
        # Reading through another Windows handle while locked is forbidden. The
        # persisted event is checked after release there; flush ordering is universal.
        if os.name == "nt":
            def inspect(*args):
                self.assertEqual(calls, ["synced"])
                return RESULT
        with patch.object(m, "sync", side_effect=sync), patch.object(m, "inspect", side_effect=inspect):
            self.run_check()
        self.assertEqual(calls, ["synced", "synced"])
        self.assertEqual(m.read(self.path)[-2]["kind"], "IN_PROGRESS")

    def test_interrupt_before_dispatch_blocks_action(self):
        self.prepare()
        with patch.object(m, "sync", side_effect=KeyboardInterrupt), patch.object(m, "inspect") as inspect:
            with self.assertRaises(KeyboardInterrupt):
                self.run_check()
        inspect.assert_not_called()
        self.assertEqual(self.state(), "UNKNOWN")

    def test_interrupt_after_dispatch_before_result(self):
        self.prepare()
        with patch.object(m, "inspect", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_check()
        self.assertEqual(self.state(), "UNKNOWN")
        self.assertEqual(m.read(self.path)[-1]["kind"], "IN_PROGRESS")
        with self.assertRaises(m.Rejected):
            self.run_check()
        with self.assertRaises(m.Rejected):
            m.mutate(self.path, BUILD, "retry-with-new-id", "PREPARED")

    def test_real_process_exit_releases_lock_but_not_uncertainty(self):
        self.prepare()
        result = subprocess.run([sys.executable, __file__, "--crash", str(self.path)],
                                timeout=10, capture_output=True)
        self.assertEqual(result.returncode, 73, result.stderr)
        self.assertEqual(self.state(), "UNKNOWN")
        with self.assertRaises(m.Rejected):
            self.run_check()

    def test_partial_result_persistence_is_never_repaired(self):
        self.prepare()
        original = m.append
        def partial(stream, records, kind, op, data):
            if kind == "COMPLETED":
                stream.seek(0, os.SEEK_END)
                stream.write(b'{"kind":"COMPLE')
                m.sync(stream)
                raise KeyboardInterrupt
            original(stream, records, kind, op, data)
        with patch.object(m, "append", side_effect=partial), patch.object(m, "inspect", return_value=RESULT):
            with self.assertRaises(KeyboardInterrupt):
                self.run_check()
        before = self.path.read_bytes()
        with self.assertRaises(m.Rejected):
            m.status(self.path)
        with self.assertRaises(m.Rejected):
            self.run_check()
        self.assertEqual(before, self.path.read_bytes())

    def test_concurrent_process_writer_rejected(self):
        self.prepare()
        with self.path.open("r+b") as stream, m.locked(stream):
            result = subprocess.run([sys.executable, __file__, "--contend", str(self.path)],
                                    timeout=10, capture_output=True)
            self.assertEqual(result.returncode, 74, result.stderr)
        self.assertEqual(self.state(), "PREPARED")

    def test_failed_offline_validation_persisted(self):
        self.prepare()
        with patch.object(m, "inspect", side_effect=m.Rejected("wrong hash")):
            with self.assertRaises(m.Rejected):
                self.run_check()
        self.assertEqual(self.state(), "FAILED")
        with self.assertRaises(m.Rejected):
            self.run_check()
        # A separate explicit offline inspection is allowed after a known failure.
        m.mutate(self.path, BUILD, "check-2", "PREPARED")

    def test_duplicate_id(self):
        self.prepare()
        with self.assertRaises(m.Rejected):
            self.prepare()

    def test_mismatched_build_rejected_before_dispatch(self):
        self.prepare()
        for key, value in (("source", "d" * 40), ("apk_sha256", "e" * 64), ("variant", "debug")):
            with self.subTest(key=key), patch.object(m, "inspect") as inspect:
                with self.assertRaises(m.Rejected):
                    m.execute(self.path, dict(BUILD, **{key: value}), "check-1", None, None, {})
                inspect.assert_not_called()

    def test_cleanup_unknown_has_no_clear_or_retry(self):
        m.mutate(self.path, BUILD, "external", "CLEANUP_UNKNOWN")
        self.assertEqual(m.status(self.path)["operations"]["external"]["state"], "CLEANUP_UNKNOWN")
        for kind in ("PREPARED", "COMPLETED", "VERIFIED_CLEAN"):
            with self.subTest(kind=kind), self.assertRaises(m.Rejected):
                m.mutate(self.path, BUILD, "new-id", kind)
        self.append_for_control("COMPLETED", "external", RESULT)
        with self.assertRaises(m.Rejected):
            m.status(self.path)

    def test_forged_completion_without_dispatch(self):
        self.prepare()
        self.append_for_control("COMPLETED", data=RESULT)
        with self.assertRaises(m.Rejected):
            m.status(self.path)

    def test_forged_phone_success_is_not_offline_receipt(self):
        self.prepare()
        self.append_for_control("IN_PROGRESS")
        self.append_for_control("COMPLETED", data=dict(RESULT, scope="phone-cleanup-verified"))
        with self.assertRaises(m.Rejected):
            m.status(self.path)

    def test_replayed_completion(self):
        self.prepare()
        with patch.object(m, "inspect", return_value=RESULT):
            self.run_check()
        self.append_for_control("COMPLETED", data=RESULT)
        with self.assertRaises(m.Rejected):
            m.status(self.path)

    def test_corruption_truncation_stale_record_and_duplicate_keys(self):
        original = self.path.read_bytes()
        cases = [b"", original[:-1], original + original,
                 original.replace(b'"version":1', b'"version":2'),
                 original.replace(b'"version":1', b'"version":1,"version":1')]
        for raw in cases:
            with self.subTest(raw=raw[:30]):
                self.path.write_bytes(raw)
                with self.assertRaises(m.Rejected):
                    m.status(self.path)
                with self.assertRaises(m.Rejected):
                    self.prepare()

    def test_wrong_journal_name(self):
        other = self.path.with_name("other.jsonl")
        other.write_bytes(self.path.read_bytes())
        with self.assertRaises(m.Rejected):
            m.status(other)

    def test_reinitialize_refused(self):
        with self.assertRaises(FileExistsError):
            m.initialize(self.path, BUILD)

    def test_cli_has_no_manual_completion_clear_or_retry(self):
        before = self.path.read_bytes()
        for command in ("complete", "clear-cleanup", "retry", "dispatch-phone"):
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, str(SCRIPT), command, "--journal", "test"],
                                        timeout=10, capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn(b"invalid choice", result.stderr)
        self.assertEqual(before, self.path.read_bytes())

    def test_unsafe_names(self):
        for value in ("../elsewhere", "A", "x/y", "", "x" * 65, "con", "com1", "nul"):
            with self.subTest(value=value), self.assertRaises(m.Rejected):
                m.safe_path(value)


class InspectionTests(unittest.TestCase):
    def setUp(self):
        m.STORE.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=m.STORE)
        self.addCleanup(self.temp.cleanup)
        self.apk = Path(self.temp.name) / "fixture.apk"
        self.apk.write_bytes(b"synthetic invalid APK")

    def inspection_fixture(self):
        # Reuse the established ELF positive fixture; only the analyzer's text
        # transport is mocked. Actual manifest and native-byte validators run.
        spec = importlib.util.spec_from_file_location("regression", SCRIPT.with_name("test-repository-validation.py"))
        regression = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(regression)
        fixture = regression.LaunchElfTests().fixture
        entries = {"lib/arm64-v8a/libsubstrate.so": fixture(False),
                   "lib/x86_64/libsubstrate.so": fixture(False, 62),
                   "lib/arm64-v8a/libpdva_launch.so": fixture()}
        paths = {}
        with zipfile.ZipFile(self.apk, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for i, (name, data) in enumerate(entries.items()):
                z.writestr(name, data)
                local = Path(self.temp.name) / (str(i) + ".fixture")
                local.write_bytes(data)
                paths[name] = local
        text = regression.harness.SOURCE.read_text(encoding="utf-8")
        text = text.replace("<application", '<uses-sdk android:minSdkVersion="30" android:targetSdkVersion="37"/><application android:extractNativeLibs="true"')
        analyzer = Path(self.temp.name) / "analyzer.fixture"
        analyzer.write_bytes(b"synthetic transport identity; never executed")
        return dict(BUILD, apk_sha256=m.file_hash(self.apk)), analyzer, paths, text

    def test_actual_validators_and_local_correspondence(self):
        build, analyzer, paths, manifest = self.inspection_fixture()
        with patch.object(m, "check_source", return_value="f" * 40), patch.object(m.subprocess, "check_output", return_value=manifest):
            result = m.inspect(build, self.apk, analyzer, paths)
        m.receipt(result, build)
        self.assertEqual(set(result["validation"]["native"]), set(paths))

    def test_local_missing_extra_and_mismatched_native(self):
        build, analyzer, paths, manifest = self.inspection_fixture()
        cases = [{}, dict(list(paths.items())[1:]), dict(paths, extra=self.apk)]
        swapped = dict(paths)
        swapped[next(iter(paths))] = self.apk
        cases.append(swapped)
        with patch.object(m, "check_source", return_value="f" * 40), patch.object(m.subprocess, "check_output", return_value=manifest):
            for mapping in cases:
                with self.subTest(keys=list(mapping)), self.assertRaises(m.Rejected):
                    m.inspect(build, self.apk, analyzer, mapping)

    def test_manifest_permissions_and_wrong_variant_rejected(self):
        build, analyzer, paths, manifest = self.inspection_fixture()
        permission = manifest.replace("<application", '<uses-permission android:name="android.permission.INTERNET"/><application')
        for text, variant in ((permission, "release"), (manifest, "debug"),
                              (manifest.replace("<application", '<application android:debuggable="true"'), "release")):
            with self.subTest(variant=variant), patch.object(m, "check_source", return_value="f" * 40), patch.object(m.subprocess, "check_output", return_value=text):
                with self.assertRaises(ValueError):
                    m.inspect(dict(build, variant=variant), self.apk, analyzer, paths)

    def test_input_changed_during_inspection(self):
        build, analyzer, paths, manifest = self.inspection_fixture()
        def change(*args, **kwargs):
            analyzer.write_bytes(b"changed")
            return manifest
        with patch.object(m, "check_source", return_value="f" * 40), patch.object(m.subprocess, "check_output", side_effect=change):
            with self.assertRaisesRegex(m.Rejected, "Inputs changed"):
                m.inspect(build, self.apk, analyzer, paths)

    def test_apk_mismatch(self):
        with patch.object(m, "check_source"), self.assertRaisesRegex(m.Rejected, "APK identity"):
            m.inspect(BUILD, self.apk, None, {})

    def test_wrong_source_or_dirty_source(self):
        for replies in (["d" * 40], [BUILD["source"], "diff"], [BUILD["source"], "", "untracked"]):
            with self.subTest(replies=replies), patch.object(m, "git", side_effect=replies):
                with self.assertRaises(m.Rejected):
                    m.check_source(BUILD["source"])

    def test_real_existing_validator_rejects_absent_extra_and_ambiguous_assets(self):
        spec = importlib.util.spec_from_file_location("validator", SCRIPT.with_name("validate-harness.py"))
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        for entries in ([], [("lib/arm64-v8a/extra.so", b"bad")],
                        [("duplicate", b"a"), ("duplicate", b"b")]):
            with self.subTest(entries=entries):
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    with zipfile.ZipFile(self.apk, "w") as z:
                        for name, data in entries:
                            z.writestr(name, data)
                with self.assertRaises(ValueError):
                    validator.inventory(self.apk)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in {"--crash", "--contend"}:
        path = Path(sys.argv[2])
        if sys.argv[1] == "--crash":
            with patch.object(m, "inspect", side_effect=lambda *args: os._exit(73)):
                m.execute(path, BUILD, "check-1", None, None, {})
        else:
            try:
                m.mutate(path, BUILD, "contender", "PREPARED")
            except OSError:
                sys.exit(74)
        sys.exit(1)  # A negative control must actually reject/interrupt.
    unittest.main(verbosity=2)
