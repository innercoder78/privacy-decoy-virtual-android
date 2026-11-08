#!/usr/bin/env python3
"""Synthetic byte/identity controls. No JDK, SDK, Gradle or Android invocation."""
import copy
from datetime import datetime, timezone, timedelta
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "android"))
import installed_tools as v

NOW = datetime(2026, 11, 8, 12, tzinfo=timezone.utc)
HOST = "windows" if os.name == "nt" else "linux"


def fixture(roots):
    suffix = ".exe" if HOST == "windows" else ""
    contents = {
        "jdk": {"release": ('IMPLEMENTOR="Eclipse Adoptium"\n'
                            'IMPLEMENTOR_VERSION="Temurin-17.0.21+9"\n'
                            'JAVA_VERSION="17.0.21"\nIMAGE_TYPE="JDK"\n'
                            f'OS_NAME="{"Windows" if HOST == "windows" else "Linux"}"\n'
                            'OS_ARCH="x86_64"\n').encode(),
                **{f"bin/{name}{suffix}": b"synthetic non-executable bytes"
                   for name in ("java", "javac", "jar")}, "lib/modules": b"modules"},
        "platform": {"android.jar": b"synthetic jar", "source.properties":
                     b"Pkg.Revision=2\nAndroidVersion.ApiLevel=37.0\n"
                     b"AndroidVersion.ExtensionLevel=22\nAndroidVersion.PreviewSdkInt=0\n"},
        "build_tools": {"source.properties": b"Pkg.Revision=36.0.0\n",
                        **{name + suffix: b"synthetic bytes" for name in
                           ("aapt2", "aidl", "zipalign")}, "lib/d8.jar": b"d8 jar",
                        "d8.bat" if HOST == "windows" else "d8": b"d8 launcher"}}
    for key, identity, major in (("platform", "platforms;android-37.0", 2),
                                  ("build_tools", "build-tools;36.0.0", 36)):
        contents[key]["package.xml"] = (
            f'<repository><localPackage path="{identity}"><revision><major>{major}'
            '</major></revision></localPackage></repository>').encode()
    for package, entries in contents.items():
        for name, data in entries.items():
            target = roots[package] / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)


class InstalledTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.roots = {key: self.root / key for key in v.PACKAGES}
        fixture(self.roots)
        self.manifest = {"schema": 1, "trust": "UNTRUSTED", "host": HOST,
                         "observed_utc": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "packages": v.scan(self.roots, HOST)}

    def compare(self):
        return v.compare(self.manifest, self.roots, HOST, NOW)

    def test_positive_remains_untrusted(self):
        self.assertEqual(self.compare(), "MATCH — UNTRUSTED; independent approval NOT ESTABLISHED")

    def test_changed_byte(self):
        target = self.roots["platform"] / "android.jar"
        original = target.read_bytes()
        target.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        with self.assertRaisesRegex(ValueError, "Installed inventory mismatch"):
            self.compare()

    def test_missing(self):
        (self.roots["jdk"] / "lib/modules").unlink()
        with self.assertRaisesRegex(ValueError, "Required tool identity absent"):
            self.compare()

    def test_unexpected_file_and_directory(self):
        for directory in (False, True):
            with self.subTest(directory=directory):
                target = self.roots["platform"] / "extra"
                target.mkdir() if directory else target.write_bytes(b"extra")
                with self.assertRaisesRegex(ValueError, "Installed inventory mismatch"):
                    self.compare()
                target.rmdir() if directory else target.unlink()

    def test_identity_even_with_regenerated_inventory(self):
        target = self.roots["platform"] / "source.properties"
        target.write_bytes(target.read_bytes().replace(b"37.0", b"38.0"))
        with self.assertRaisesRegex(ValueError, "Unexpected platform identity"):
            v.scan(self.roots, HOST)

    def test_xml_identity(self):
        target = self.roots["build_tools"] / "package.xml"
        target.write_bytes(target.read_bytes().replace(b"36.0.0", b"35.0.0"))
        with self.assertRaisesRegex(ValueError, "Unexpected XML package identity"):
            self.compare()

    def test_stale_and_future(self):
        for delta in (timedelta(days=31), -timedelta(seconds=1)):
            with self.subTest(delta=delta), self.assertRaisesRegex(ValueError, "Stale or future"):
                v.compare(self.manifest, self.roots, HOST, NOW + delta)

    def test_self_approval_refused(self):
        self.manifest["trust"] = "APPROVED"
        with self.assertRaisesRegex(ValueError, "Unsupported manifest or trust claim"):
            self.compare()

    def test_bad_schema_entries(self):
        for field, value in (("schema", True), ("host", "other"), ("packages", {})):
            altered = copy.deepcopy(self.manifest)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                v.validate(altered, NOW)
        for name in ("../outside", "/absolute", "a:stream", "a\\b", "NUL", "a."):
            altered = copy.deepcopy(self.manifest)
            altered["packages"]["platform"][name] = {"type": "directory"}
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Invalid relative path"):
                v.validate(altered, NOW)

    def test_malformed_json(self):
        target = self.root / "manifest.json"
        for raw in ('{', '{"schema":1,"schema":1}', '[]'):
            target.write_text(raw)
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                v.load(target, NOW)

    def test_hardlink(self):
        os.link(self.roots["platform"] / "android.jar", self.root / "alias")
        with self.assertRaisesRegex(RuntimeError, "Unsafe distribution filesystem type"):
            self.compare()

    def test_real_directory_redirection(self):
        link = self.roots["platform"] / "redirect"
        outside = self.root / "outside"
        outside.mkdir()
        if os.name == "nt":
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, "junction creation must actually succeed")
        else:
            link.symlink_to(outside, target_is_directory=True)
        try:
            with self.assertRaisesRegex(RuntimeError, "Unsafe distribution filesystem type"):
                self.compare()
        finally:
            link.rmdir() if os.name == "nt" else link.unlink()

    def test_host_mismatch(self):
        with self.assertRaisesRegex(ValueError, "Host identity mismatch"):
            v.compare(self.manifest, self.roots, "linux" if HOST == "windows" else "windows", NOW)

    def test_semantic_byte_mutant_is_caught(self):
        # Restoring cached/self-reported trust must defeat the SAME assertion,
        # not merely crash a subprocess or return an unrelated nonzero status.
        with patch.object(v, "scan", return_value=self.manifest["packages"]):
            with self.assertRaisesRegex(AssertionError, "ValueError not raised"):
                self.test_changed_byte()

    def test_semantic_trust_and_freshness_mutant_is_caught(self):
        altered = copy.deepcopy(self.manifest)
        altered["trust"] = "APPROVED"
        with patch.object(v, "validate", return_value=None):
            with self.assertRaisesRegex(AssertionError, "ValueError not raised"):
                with self.assertRaisesRegex(ValueError, "Unsupported manifest or trust claim"):
                    v.compare(altered, self.roots, HOST, NOW)
        with patch.object(v, "MAX_AGE", timedelta(days=365)):
            with self.assertRaisesRegex(AssertionError, "ValueError not raised"):
                with self.assertRaisesRegex(ValueError, "Stale or future"):
                    v.compare(self.manifest, self.roots, HOST, NOW + timedelta(days=31))

    def test_cli_exclusive_output_and_sanitized_failure(self):
        output = self.root / "private-manifest.json"
        args = [sys.executable, str(ROOT / "android/installed_tools.py"), "inventory",
                "--jdk", str(self.roots["jdk"]), "--platform", str(self.roots["platform"]),
                "--build-tools", str(self.roots["build_tools"]), "--manifest", str(output)]
        def run():
            return subprocess.run(args, capture_output=True, timeout=15)
        result = run()
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"UNTRUSTED", result.stdout)
        saved = output.read_bytes()
        result = run()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(output.read_bytes(), saved)
        args[2] = "compare"
        self.assertEqual(run().returncode, 0)
        output.write_text('{"schema":1,"schema":1}')
        result = run()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr.strip(),
                         b"FAIL: installed-tool check refused; no approval established")


if __name__ == "__main__":
    unittest.main()
