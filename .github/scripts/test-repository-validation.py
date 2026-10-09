#!/usr/bin/env python3
"""Regression tests for narrow source admission and zero-permission manifests."""
import contextlib
import importlib.util
import io
import os
import subprocess
import zlib
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


class GitSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pdva-git-source-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'objects'
        self.env = os.environ | {
            'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
            'GIT_NO_REPLACE_OBJECTS': '1',
            'GIT_AUTHOR_NAME': 'Source integrity fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
            'GIT_COMMITTER_NAME': 'Source integrity fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
        }
        subprocess.run(['git', 'init', '--quiet', str(self.repo)], env=self.env, check=True)
        self.payloads = {
            '.gitattributes': b'ignored.txt export-ignore\nsubst.txt export-subst\n* text eol=crlf\n',
            'ignored.txt': b'keep this file\n',
            'subst.txt': b'$Format:%H$\n',
            'run.sh': b'#!/bin/sh\nexit 0\n',
        }
        entries = []
        self.ids = {}
        for name, data in self.payloads.items():
            oid = self.git('hash-object', '-w', '--stdin', data=data).decode().strip()
            self.ids[name] = oid
            mode = '100755' if name == 'run.sh' else '100644'
            entries.append(f'{mode} blob {oid}\t{name}\0')
        self.tree = self.git('mktree', '-z', data=''.join(entries).encode()).decode().strip()
        self.commit = self.git('commit-tree', self.tree, data=b'synthetic fixture\n').decode().strip()
        self.destination = self.root / 'source'

    def git(self, *args, data=None):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], input=data,
                                       env=self.env, stderr=subprocess.PIPE)

    def materialize(self):
        with contextlib.redirect_stdout(io.StringIO()):
            research.materialize_git_source(self.repo, self.commit, self.tree,
                                            self.destination, self.env)
        return research.git_source_manifest(self.repo, self.commit, self.tree, self.env)

    def test_exact_source_ignores_crlf_and_export_transformations(self):
        self.git('config', 'core.autocrlf', 'true')
        manifest = self.materialize()
        self.assertEqual(set(self.payloads), set(manifest))
        self.assertEqual('100755', manifest['run.sh'][0])
        for name, data in self.payloads.items():
            self.assertEqual(data, (self.destination / name).read_bytes())

    def test_wrong_tree_pin_is_rejected(self):
        empty_tree = self.git('mktree', data=b'').decode().strip()
        with self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
            research.git_source_manifest(self.repo, self.commit, empty_tree, self.env)

    def test_corrupt_git_object_is_rejected(self):
        oid = self.ids['ignored.txt']
        path = self.repo / '.git/objects' / oid[:2] / oid[2:]
        path.chmod(0o644)
        path.write_bytes(zlib.compress(b'blob 7\0changed'))
        with self.assertRaises(subprocess.CalledProcessError):
            research.git_source_manifest(self.repo, self.commit, self.tree, self.env)

    def test_modified_file_is_rejected(self):
        manifest = self.materialize()
        (self.destination / 'ignored.txt').write_bytes(b'substituted\n')
        with self.assertRaisesRegex(RuntimeError, 'blob mismatch'):
            research.verify_source_tree(self.destination, manifest)

    def test_missing_file_is_rejected(self):
        manifest = self.materialize()
        (self.destination / 'ignored.txt').unlink()
        with self.assertRaisesRegex(RuntimeError, 'Missing source'):
            research.verify_source_tree(self.destination, manifest)

    def test_extra_file_and_directory_are_rejected(self):
        manifest = self.materialize()
        extra = self.destination / 'extra'
        extra.write_text('unreviewed')
        with self.assertRaisesRegex(RuntimeError, 'Extra source'):
            research.verify_source_tree(self.destination, manifest)
        extra.unlink()
        extra.mkdir()
        with self.assertRaisesRegex(RuntimeError, 'unexpected directory'):
            research.verify_source_tree(self.destination, manifest)

    def test_unsafe_paths_and_symlink_targets_are_rejected(self):
        for name in ('../escape', '/absolute', 'a//b', 'a/./b', 'C:/drive', 'a\\b', '.git/config'):
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                research.source_path(name)
        for target in (b'../../escape', b'/absolute', b'C:/drive', b'a\\b', b'../.git/config'):
            with self.subTest(target=target), self.assertRaises(RuntimeError):
                research.source_link('dir/link', target)
        self.assertEqual('../run.sh', research.source_link('dir/link', b'../run.sh'))

    @unittest.skipIf(os.name == 'nt', 'POSIX executable modes are enforced on Linux')
    def test_materialized_executable_mode_is_checked(self):
        manifest = self.materialize()
        (self.destination / 'run.sh').chmod(0o644)
        with self.assertRaisesRegex(RuntimeError, 'mode mismatch'):
            research.verify_source_tree(self.destination, manifest)

    @unittest.skipIf(os.name == 'nt', 'Real POSIX symlink types are enforced on Linux')
    def test_real_symlink_and_type_substitution(self):
        oid = self.git('hash-object', '-w', '--stdin', data=b'run.sh').decode().strip()
        rows = [f'{"100755" if name == "run.sh" else "100644"} blob {value}\t{name}\0'
                for name, value in self.ids.items()]
        rows.append(f'120000 blob {oid}\tlink\0')
        self.tree = self.git('mktree', '-z', data=''.join(rows).encode()).decode().strip()
        self.commit = self.git('commit-tree', self.tree, data=b'symlink fixture\n').decode().strip()
        manifest = self.materialize()
        link = self.destination / 'link'
        self.assertTrue(link.is_symlink())
        research.verify_source_tree(self.destination, manifest)
        link.unlink()
        link.write_bytes(b'run.sh')
        with self.assertRaisesRegex(RuntimeError, 'symlink type mismatch'):
            research.verify_source_tree(self.destination, manifest)


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
