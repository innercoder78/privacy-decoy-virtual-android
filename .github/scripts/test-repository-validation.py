#!/usr/bin/env python3
"""Regression tests for narrow source admission and zero-permission manifests."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import tarfile
import unittest

SCRIPTS = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

foundation = load("validate-foundation")
harness = load("validate-harness")
research = load("qemu-android-research")

class RepositoryTests(unittest.TestCase):
    def check_tree(self, extra=None, mode="100644", stage="0"):
        with tempfile.TemporaryDirectory(prefix="pdva-validation-") as directory:
            root = Path(directory)
            files = {
                "docs/requirements.md": b"| PDVA-REQ-001 | test obligation |\n",
                "docs/decisions/ADR-0001-test.md": b"# Test ADR\n",
            }
            files.update(extra or {})
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            old_root, old_git = foundation.ROOT, foundation.git
            foundation.ROOT = root
            def git(*args):
                if "--stage" in args:
                    return f"{mode} {'0'*40} {stage}\tdocs/requirements.md\0".encode()
                return "\0".join(files).encode()
            foundation.git = git
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    return foundation.validate()
            finally:
                foundation.ROOT, foundation.git = old_root, old_git

    def test_minimal_valid_tree(self): self.assertEqual(0, self.check_tree())
    def test_unknown_source(self):
        self.assertEqual(1, self.check_tree({"android/unreviewed.java": b"class X {}"}))
    def test_exact_approved_source(self):
        self.assertEqual(0, self.check_tree({"android/build.gradle": b"// fixture\n"}))
    def test_research_exact_paths_only(self):
        for name in (".github/scripts/qemu-android-research.py",
                     ".github/workflows/qemu-android-research.yml"):
            with self.subTest(name=name):
                self.assertEqual(0, self.check_tree({name: b"# fixture\n"}))
                self.assertEqual(1, self.check_tree({name: b"\x00binary"}))
                self.assertEqual(1, self.check_tree({name.replace("research", "unreviewed"): b"# fixture\n"}))
    def test_binary_in_text_path(self):
        self.assertEqual(1, self.check_tree({"android/build.gradle": b"\x00bad"}))
    def test_unknown_root(self):
        self.assertEqual(1, self.check_tree({"surprise/README.md": b"# surprise"}))
    def test_artifact_suffixes(self):
        for extension in foundation.BLOCKED_SUFFIXES:
            with self.subTest(extension=extension):
                self.assertEqual(1, self.check_tree({"android/test" + extension: b"artifact"}))
    def test_sensitive_names(self):
        for name in foundation.SECRET_NAMES | {".env", ".env.local"}:
            with self.subTest(name=name):
                self.assertEqual(1, self.check_tree({"android/" + name: b"synthetic"}))
    def test_modes_and_conflict(self):
        for mode, stage in [("100755","0"), ("120000","0"), ("160000","0"), ("100644","1")]:
            self.assertEqual(1, self.check_tree(mode=mode, stage=stage))
    def test_history_notice_preserved(self):
        self.assertEqual(1, self.check_tree({"docs/reference/privacy-decoy-history/test.md": b"missing notices"}))
    def test_missing_link(self):
        self.assertEqual(1, self.check_tree({"docs/test.md": b"[bad](missing.md)"}))
    def test_requirement_id(self):
        self.assertEqual(1, self.check_tree({"docs/test.md": b"PDVA-REQ-999"}))
    def test_private_key_marker(self):
        marker = ("-----BEGIN " + "PRIVATE KEY-----").encode()
        self.assertEqual(1, self.check_tree({"docs/test.md": marker}))

class ResearchInputTests(unittest.TestCase):
    def test_corrupt_download_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input"
            path.write_bytes(b"corrupt archive")
            with self.assertRaisesRegex(RuntimeError, "Hash mismatch"):
                research.verify(path, "0" * 64)

    def test_source_archive_cannot_escape_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "bad.tar"
            with tarfile.open(archive, "w") as output:
                member = tarfile.TarInfo("../escaped")
                member.size = 1
                output.addfile(member, io.BytesIO(b"x"))
            with self.assertRaises(tarfile.FilterError):
                research.unpack(archive, root / "extracted")
            self.assertFalse((root / "escaped").exists())

class ManifestTests(unittest.TestCase):
    def setUp(self): self.source = harness.SOURCE.read_text(encoding="utf-8")
    def test_valid(self): harness.manifest(self.source, release=True)
    def test_any_permission_rejected(self):
        for tag in ("uses-permission", "uses-permission-sdk-23", "permission"):
            changed = self.source.replace("<application", '<' + tag +
                    ' android:name="android.permission.INTERNET" /><application', 1)
            with self.assertRaises(ValueError): harness.manifest(changed)
    def test_isolated_attributes(self):
        for old, new in [('isolatedProcess="true"', 'isolatedProcess="false"'),
                         ('useAppZygote="false"', 'useAppZygote="true"'),
                         ('android:process=":gate0_worker"', 'android:process=":shared"')]:
            with self.assertRaises(ValueError): harness.manifest(self.source.replace(old,new))
    def test_shared_and_exported(self):
        with self.assertRaises(ValueError):
            harness.manifest(self.source.replace('<service ', '<service android:allowSharedIsolatedProcess="true" '))
        with self.assertRaises(ValueError):
            harness.manifest(self.source.replace('android:exported="false"', 'android:exported="true"'))
    def test_debuggable_release(self):
        with self.assertRaises(ValueError):
            harness.manifest(self.source.replace('<application ', '<application android:debuggable="true" '), True)

if __name__ == "__main__":
    unittest.main()
