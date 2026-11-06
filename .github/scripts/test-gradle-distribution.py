#!/usr/bin/env python3
"""Offline synthetic distributions; every Gradle invocation is mocked."""
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import traceback
import unittest
from unittest.mock import patch
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("bootstrap", ROOT / "android/build.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
PREFIX = "gradle-" + b.VERSION


class DistributionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        # Never inspect the real user's Gradle home or inherit injected JVM options.
        for fixture_patch in (
                patch.dict(os.environ, {"GRADLE_USER_HOME": str(self.root / "user-home")}, clear=True),
                patch.object(b.sys, "argv", ["build.py", "help"])):
            fixture_patch.start()
            self.addCleanup(fixture_patch.stop)
        self.store = self.root / "build/gradle-distribution"
        self.store.mkdir(parents=True)
        self.archive = self.store / (PREFIX + "-bin.zip")
        self.home = self.store / PREFIX
        self.payloads = {"bin/gradle": b"synthetic shell\n", "bin/gradle.bat": b"synthetic batch\r\n",
                         "lib/test.jar": b"synthetic library; not executable"}
        root_patch = patch.object(b, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.make_archive()

    def pin(self):
        b.SHA256 = hashlib.sha256(self.archive.read_bytes()).hexdigest()

    def make_archive(self, extra=()):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.archive, "w") as z:
                z.writestr(PREFIX + "/", b"")
                for name, data in self.payloads.items():
                    z.writestr(PREFIX + "/" + name, data)
                for name, data in extra:
                    z.writestr(name, data)
        self.pin()

    def accepted(self):
        with patch.object(b.subprocess, "call", return_value=17) as execute:
            self.assertEqual(b.main(), 17)
            execute.assert_called_once()
            self.assertEqual(Path(execute.call_args.args[0][0]), self.home / "bin" /
                             ("gradle.bat" if os.name == "nt" else "gradle"))

    def rejected(self, reason):
        before = self.archive.read_bytes()
        with patch.object(b.subprocess, "call") as execute:
            with self.assertRaisesRegex(RuntimeError, reason):
                b.main()
            execute.assert_not_called()
        self.assertEqual(self.archive.read_bytes(), before)

    def test_fresh_and_reuse(self):
        self.accepted()
        before = {p.relative_to(self.home): p.stat().st_mtime_ns for p in self.home.rglob("*")}
        self.accepted()
        self.assertEqual(before, {p.relative_to(self.home): p.stat().st_mtime_ns
                                  for p in self.home.rglob("*")})
        if os.name != "nt":
            self.assertTrue((self.home / "bin/gradle").stat().st_mode & stat.S_IXUSR)

    def test_modified_scripts_and_library(self):
        self.accepted()
        for name, original in self.payloads.items():
            with self.subTest(name=name):
                path = self.home / name
                changed = bytes([original[0] ^ 1]) + original[1:]
                path.write_bytes(changed)
                self.rejected("Installed distribution content mismatch")
                self.assertEqual(path.read_bytes(), changed)
                path.write_bytes(original)

    def test_truncated_file(self):
        self.accepted()
        (self.home / "lib/test.jar").write_bytes(b"")
        self.rejected("Installed distribution content mismatch")

    def test_missing_file(self):
        self.accepted()
        (self.home / "lib/test.jar").unlink()
        self.rejected("Missing installed distribution entry")
        self.assertFalse((self.home / "lib/test.jar").exists())

    def test_unexpected_file_and_directory(self):
        self.accepted()
        extra = self.home / "unexpected"
        extra.write_bytes(b"evidence")
        self.rejected("Unexpected installed distribution entry")
        self.assertEqual(extra.read_bytes(), b"evidence")
        extra.unlink()
        extra.mkdir()
        self.rejected("Unexpected installed distribution entry")

    def test_type_substitution(self):
        self.accepted()
        path = self.home / "lib/test.jar"
        path.unlink()
        path.mkdir()
        self.rejected("Unsafe distribution filesystem type")

    def test_home_file_preserved(self):
        self.home.write_bytes(b"evidence")
        self.rejected("Unsafe distribution filesystem type")
        self.assertEqual(self.home.read_bytes(), b"evidence")

    def test_hardlink_rejected(self):
        self.accepted()
        os.link(self.home / "lib/test.jar", self.root / "alias")
        self.rejected("Unsafe distribution filesystem type")

    def test_directory_link_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        if os.name == "nt":
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(self.home), str(outside)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.home.symlink_to(outside, target_is_directory=True)
        try:
            self.rejected("Unsafe distribution filesystem type")
            self.assertEqual(list(outside.iterdir()), [])
        finally:
            if os.name == "nt":
                self.home.rmdir()
            else:
                self.home.unlink()

    def test_archive_symlink_type(self):
        entry = zipfile.ZipInfo(PREFIX + "/lib/link")
        entry.create_system = 3
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.make_archive([(entry, b"../../outside")])
        self.rejected("Unsafe distribution archive type")
        self.assertFalse(self.home.exists())

    def test_unsafe_paths(self):
        for name in ["../escape", "/absolute", PREFIX + "/../escape", PREFIX + "/bin\\escape",
                     PREFIX + "/C:escape", PREFIX + "//empty", PREFIX + "/NUL.txt",
                     PREFIX + "/tail.", "other/file"]:
            with self.subTest(name=name):
                # Windows ZipInfo normalizes backslashes when writing. Patch both
                # raw headers so the fixture actually contains the unsafe bytes.
                self.make_archive([(name.replace("\\", "~"), b"bad")])
                if "\\" in name:
                    self.archive.write_bytes(self.archive.read_bytes().replace(b"~", b"\\"))
                    self.pin()
                self.rejected("Unsafe distribution path")
                self.assertFalse(self.home.exists())
        self.make_archive([(PREFIX + "/x_hidden", b"bad")])
        self.archive.write_bytes(self.archive.read_bytes().replace(b"x_hidden", b"x\x00hidden"))
        self.pin()
        self.rejected("Unsafe distribution path")

    def test_conflicting_entries(self):
        for extra in [[(PREFIX + "/bin/gradle", b"duplicate")],
                      [(PREFIX + "/LIB/extra", b"case alias")],
                      [(PREFIX + "/lib", b"file directory conflict")]]:
            with self.subTest(extra=extra):
                self.make_archive(extra)
                self.rejected("Conflicting distribution entries")
                self.assertFalse(self.home.exists())

    def test_mismatched_hash(self):
        b.SHA256 = "0" * 64
        self.rejected("Gradle distribution checksum mismatch")
        self.pin()
        self.accepted()
        b.SHA256 = "0" * 64
        self.rejected("Gradle distribution checksum mismatch")

    def test_bad_zip(self):
        self.archive.write_bytes(b"not a zip")
        self.pin()
        with patch.object(b.subprocess, "call") as execute:
            with self.assertRaises(zipfile.BadZipFile):
                b.main()
            execute.assert_not_called()
        self.assertFalse(self.home.exists())

    def test_mock_download_and_preserve_partial(self):
        data = self.archive.read_bytes()
        self.archive.unlink()
        with patch.object(b.urllib.request, "urlopen", return_value=io.BytesIO(data)) as download:
            self.accepted()
            download.assert_called_once()
        self.assertEqual(self.archive.read_bytes(), data)
        self.assertEqual(self.archive.with_suffix(".download").read_bytes(), data)
        self.archive.unlink()
        with patch.object(b.subprocess, "call") as execute:
            with patch.object(b.urllib.request, "urlopen") as download:
                with self.assertRaises(FileExistsError):
                    b.main()
                download.assert_not_called()
            execute.assert_not_called()

    def test_mock_download_bad_hash(self):
        self.archive.unlink()
        with patch.object(b.urllib.request, "urlopen", return_value=io.BytesIO(b"bad download")):
            with patch.object(b.subprocess, "call") as execute:
                with self.assertRaisesRegex(RuntimeError, "Gradle distribution checksum mismatch"):
                    b.main()
                execute.assert_not_called()
        self.assertFalse(self.archive.exists())
        self.assertEqual(self.archive.with_suffix(".download").read_bytes(), b"bad download")

    def test_file_identity_race_rejected(self):
        original = b.os.fstat
        def substituted(fd):
            value = list(original(fd))
            value[1] += 1  # A different opened inode must not reach read/launch.
            return os.stat_result(value)
        with patch.object(b.os, "fstat", side_effect=substituted):
            self.rejected("Distribution file changed during validation")

    def test_corrupt_member_crc(self):
        original = self.archive.read_bytes()
        self.archive.write_bytes(original.replace(b"synthetic library", b"Synthetic library"))
        self.pin()  # Separately test ZIP structure/content validation after SHA admission.
        with patch.object(b.subprocess, "call") as execute:
            with self.assertRaisesRegex(zipfile.BadZipFile, "Bad CRC-32"):
                b.main()
            execute.assert_not_called()
        self.assertFalse(self.home.exists())

    def test_initial_extraction_validation(self):
        original = b.shutil.copyfileobj
        def corrupt(source, target):
            original(source, target)
            target.write(b"injected corruption")
        with patch.object(b.shutil, "copyfileobj", side_effect=corrupt):
            self.rejected("Installed distribution content mismatch")
        self.assertTrue(self.home.exists())
        self.rejected("Installed distribution content mismatch")

    def test_original_weakness_mutation(self):
        self.accepted()
        (self.home / "bin/gradle").write_bytes(b"modified launcher")
        self.rejected("Installed distribution content mismatch")
        # Remove ONLY installed-tree validation, restoring original cached trust.
        # Require the precise failed assertion AND an observed mocked invocation.
        with patch.object(b, "validate_installation", return_value=None):
            with patch.object(b.subprocess, "call", return_value=17) as execute:
                with self.assertRaisesRegex(AssertionError, "RuntimeError not raised"):
                    with self.assertRaisesRegex(RuntimeError, "Installed distribution content mismatch"):
                        b.main()
                execute.assert_called_once()
        self.assertEqual((self.home / "bin/gradle").read_bytes(), b"modified launcher")

    def test_startup_supported_tasks_and_selectors(self):
        tasks = [":gate0-harness:assembleDebug", ":gate0-harness:assembleRelease",
                 ":gate0-harness:assembleDebugAndroidTest", ":gate0-harness:protocolTest",
                 ":gate0-harness:lintDebug", "--offline", "--stacktrace", "-i",
                 "-Pfixture=true", "-Dfile.encoding=UTF-8", "--no-daemon",
                 "-help", "-profile", "-xcompileIgnored", "-project-cache-dir=fixture",
                 "-Dorg.gradle.java.home=fixture-jdk"]
        env = {"JAVA_HOME": str(self.root / "jdk"), "ANDROID_HOME": str(self.root / "sdk"),
               "ANDROID_SDK_ROOT": str(self.root / "sdk"), "JAVA_OPTS": "",
               "ORG_GRADLE_PROJECT_fixture": "true"}
        with patch.dict(os.environ, env), patch.object(b.sys, "argv", ["build.py", *tasks]), \
                patch.object(b.subprocess, "call", return_value=17) as launch:
            self.assertEqual(b.main(), 17)
            self.assertEqual(launch.call_args.args[0][-len(tasks):], tasks)
            self.assertEqual(launch.call_args.kwargs["env"], dict(os.environ))
            self.assertEqual(launch.call_args.args[0][4:6],
                             ["-g", str(self.root / "user-home")])

    def test_startup_default_home_is_bound(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(Path, "home", return_value=self.root), \
                patch.object(b.subprocess, "call", return_value=17) as launch:
            self.assertEqual(b.main(), 17)
            self.assertEqual(launch.call_args.args[0][4:6], ["-g", str(self.root / ".gradle")])
            self.assertFalse((self.root / ".gradle").exists())

    def test_startup_argument_forms(self):
        cases = [["--init-script", "fixture"], ["-I", "fixture"], ["-Ifixture"],
                 ["-I=fixture"], ["--I=fixture"], ["-init-script", "fixture"],
                 ["--init-script=fixture"], ["--init-s"], ["-qI"],
                 ["--", "--init-script=fixture"], ["-I"], ["--init-script="],
                 ["--gradle-user-home", "fixture"], ["-gfixture"], ["--g=fixture"],
                 ["-gradle-user-home", "fixture"], ["-pfixture"], ["--project-dir=fixture"],
                 ["--include-build=fixture"], ["-include-build", "fixture"],
                 ["--system-prop"], ["--system-prop", "-I"], ['"-I"', "fixture"]]
        for key in ("gradle.user.home", "user.home", "user.dir", "gradle.home", "org.gradle.jvmargs"):
            for option in ("-D", "--system-prop", "-system-prop", "--D", "-P", "--project-prop"):
                cases.extend([[option, key + "=fixture"], [option + "=" + key + "=fixture"]])
            cases.append(["-D" + key + "=fixture"])
        for args in cases:
            with self.subTest(args=args), patch.object(b.sys, "argv", ["build.py", "help", *args]):
                self.rejected("Gradle startup configuration")
        self.assertFalse(self.home.exists())

    def test_startup_environment_forms(self):
        for name in ("JAVA_OPTS", "GRADLE_OPTS", "JAVA_TOOL_OPTIONS", "JDK_JAVA_OPTIONS",
                     "_JAVA_OPTIONS", "ORG_GRADLE_PROJECT_org.gradle.jvmargs",
                     "ORG_GRADLE_PROJECT_systemProp.gradle.user.home"):
            for value in ("-Dpdva.fixture=true", " ", "@fixture", '"'):
                with self.subTest(name=name, value=value), patch.dict(os.environ, {name: value}):
                    self.rejected("Gradle startup configuration")

    def test_startup_home_ambiguity_and_errors(self):
        for value in ("", ".", "relative", str(self.root / ".." / "other")):
            with self.subTest(value=value), patch.dict(os.environ, {"GRADLE_USER_HOME": value}):
                self.rejected("Gradle startup configuration")
        with patch.object(Path, "lstat", side_effect=PermissionError("PRIVATE FIXTURE")):
            self.rejected("^Unreviewed or ambiguous Gradle startup configuration$")
            try:
                b.main()
            except RuntimeError as error:
                self.assertNotIn("PRIVATE FIXTURE", "".join(traceback.format_exception(error)))

    def test_startup_automatic_entries_preserved(self):
        user = self.root / "user-home"
        user.mkdir()
        (user / "gradle.properties").write_bytes(b"synthetic private properties")
        (user / "caches").mkdir()
        (user / "caches/fixture").write_bytes(b"synthetic cache")
        for name in ("init.gradle", "init.gradle.kts", "init.gradle.dcl", "init.d"):
            for directory in (False, True):
                entry = user / name
                entry.mkdir() if directory else entry.write_bytes(b"synthetic init; never executed")
                before = {p.relative_to(user): (p.stat().st_mtime_ns,
                          p.read_bytes() if p.is_file() else None) for p in user.rglob("*")}
                with patch.object(Path, "iterdir", side_effect=AssertionError("No home enumeration")):
                    self.rejected("Gradle startup configuration")
                self.assertEqual(before, {p.relative_to(user): (p.stat().st_mtime_ns,
                                 p.read_bytes() if p.is_file() else None) for p in user.rglob("*")})
                entry.rmdir() if directory else entry.unlink()
        self.accepted()

    def test_startup_home_link_rejected(self):
        user = self.root / "user-home"
        outside = self.root / "outside"
        outside.mkdir()
        if os.name == "nt":
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(user), str(outside)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            user.symlink_to(outside, target_is_directory=True)
        try:
            self.rejected("Gradle startup configuration")
            self.assertEqual(list(outside.iterdir()), [])
        finally:
            user.rmdir() if os.name == "nt" else user.unlink()

    def test_pr60_startup_regression_and_guard_removal(self):
        external = self.root / "external-home"
        external.mkdir()
        init = external / "init.gradle"
        init.write_text("println 'PDVA_SYNTHETIC_INIT'\n", encoding="utf-8")
        (external / "gradle.properties").write_text(
            "org.gradle.jvmargs=-Dpdva.fixture=true\n", encoding="utf-8")
        env = {"GRADLE_USER_HOME": str(external), "ORG_GRADLE_PROJECT_pdvaFixture": "true"}
        for name in ("GRADLE_OPTS", "JAVA_OPTS", "JAVA_TOOL_OPTIONS", "JDK_JAVA_OPTIONS", "_JAVA_OPTIONS"):
            env[name] = "-Dpdva.fixture=true"
        before = {p.name: p.read_bytes() for p in external.iterdir()}
        with patch.dict(os.environ, env, clear=True), patch.object(
                b.sys, "argv", ["build.py", "help", "--init-script", str(init)]):
            self.rejected("Gradle startup configuration")
            # Remove only the guard: the exact rejection assertion must fail,
            # with a mocked launch observed, not an unrelated test exception.
            with patch.object(b, "admit_startup", return_value=None), \
                    patch.object(b.subprocess, "call", return_value=17) as launch:
                with self.assertRaisesRegex(AssertionError, "RuntimeError not raised"):
                    with self.assertRaisesRegex(RuntimeError, "Gradle startup configuration"):
                        b.main()
                launch.assert_called_once()
                self.assertEqual(launch.call_args.args[0][-2:], ["--init-script", str(init)])
                self.assertEqual(launch.call_args.kwargs["env"], dict(os.environ))
        self.assertEqual(before, {p.name: p.read_bytes() for p in external.iterdir()})


if __name__ == "__main__":
    unittest.main(verbosity=2)
