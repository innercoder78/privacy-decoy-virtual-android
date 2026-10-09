#!/usr/bin/env python3
"""Regression tests for narrow source admission and zero-permission manifests."""
import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import zlib
from pathlib import Path
import tempfile
import tarfile
import unittest
from unittest import mock

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


class AndroidPatchTests(unittest.TestCase):
    def setUp(self):
        # Synthetic patch fixtures, never substituted into the research build.
        self.sources = {
            'meson.build': research.QEMU_RT_ANCHOR.encode(),
            'util/oslib-posix.c': (research.QEMU_SHM_ANCHOR +
                                  '\n    int fd = -73;\n    return fd;\n}\n').encode(),
        }
        pins = {name: research.hashlib.sha256(data).hexdigest() for name, data in self.sources.items()}
        patcher = mock.patch.dict(research.QEMU_PATCH_INPUTS, pins, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def render(self, sources=None, target='aarch64-linux-android30'):
        return research.render_android_patch(self.sources if sources is None else sources, target)

    def test_verified_inputs_and_platform_scope(self):
        patched = self.render()
        self.assertEqual(set(self.sources), set(patched))
        c = patched['util/oslib-posix.c'].decode()
        self.assertEqual(research.ANDROID_SHM_IMPL + self.sources['util/oslib-posix.c'].decode()
                         + '#endif /* __ANDROID__ */\n', c)
        meson = patched['meson.build'].decode()
        self.assertIn("if cc.get_define('__ANDROID__') != ''", meson)
        self.assertIn('if not cc.links', meson)
        self.assertIn("error('PDVA Android shared memfd functionality unavailable')", meson)
        self.assertIn(research.QEMU_RT_ANCHOR.removeprefix('rt = not_found\nif'), meson)
        for forbidden in ('mkstemp', 'shm_open', 'shm_unlink', 'syscall', 'MFD_HUGETLB', 'MFD_ALLOW_SEALING'):
            self.assertNotIn(forbidden, research.ANDROID_SHM_IMPL)

    def test_modified_or_substituted_source_is_rejected(self):
        for name in self.sources:
            with self.subTest(name=name), self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
                self.render(self.sources | {name: self.sources[name] + b'\n'})

    def test_missing_and_duplicate_anchors_are_rejected(self):
        for data in (b'no anchor', self.sources['meson.build'] * 2):
            # Reach the independent anchor check with a synthetic fixture pin.
            with mock.patch.dict(research.QEMU_PATCH_INPUTS, {
                'meson.build': research.hashlib.sha256(data).hexdigest()
            }), self.assertRaisesRegex(RuntimeError, 'anchors mismatch'):
                self.render(self.sources | {'meson.build': data})

    def test_duplicate_application_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
            self.render(self.render())

    def test_unexpected_files_and_wrong_targets_are_rejected(self):
        for sources in (self.sources | {'extra.c': b'extra'}, {'meson.build': b'only one'}):
            with self.assertRaisesRegex(RuntimeError, 'target or file set'):
                self.render(sources)
        for target in ('aarch64-linux-gnu', 'x86_64-linux-android30', 'aarch64-linux-android29'):
            with self.subTest(target=target), self.assertRaisesRegex(RuntimeError, 'target or file set'):
                self.render(target=target)

    def test_all_files_are_verified_before_any_write(self):
        with tempfile.TemporaryDirectory(prefix='pdva-patch-test-') as directory:
            root = Path(directory)
            (root / 'util').mkdir()
            for name, data in self.sources.items():
                (root / name).write_bytes(data)
            (root / 'util/oslib-posix.c').write_bytes(b'substitution')
            with self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
                research.apply_android_patch(root, lambda text: None)
            self.assertEqual(self.sources['meson.build'], (root / 'meson.build').read_bytes())

    def test_pcre2_targets_exclude_programs(self):
        self.assertEqual(('libpcre2-8.la', 'libpcre2-posix.la'), research.PCRE2_BUILD_TARGETS)
        self.assertEqual({'install-libLTLIBRARIES', 'install-includeHEADERS',
                          'install-nodist_includeHEADERS', 'install-pkgconfigDATA'},
                         set(research.PCRE2_INSTALL_TARGETS))

    @unittest.skipUnless(os.name == 'posix' and shutil.which('cc'), 'Host C controls run on Linux CI')
    def test_native_failure_cleanup_platform_and_missing_api_controls(self):
        # Only these modeled host unit tests execute. No Android code is run.
        prelude = '''#include <assert.h>
#include <errno.h>
#include <stddef.h>
#include <string.h>
#define __ANDROID__ 1
#define __BIONIC__ 1
#define __aarch64__ 1
#define __ANDROID_API__ 30
#define MFD_CLOEXEC 1
typedef struct Error { int code; } Error;
static Error recorded;
static int result, chmod_result, resize_result, creates, chmods, resizes, closes;
static size_t requested_size;
static int test_create(const char *name, unsigned flags) {
    assert(strcmp(name, "qemu-shm") == 0 && flags == MFD_CLOEXEC);
    creates++; errno = EPERM; return result;
}
static int test_resize(int fd, size_t size) {
    assert(fd == result); resizes++; requested_size = size;
    errno = ENOSPC; return resize_result;
}
static int test_chmod(int fd, unsigned mode) {
    assert(fd == result && mode == 0); chmods++;
    errno = EACCES; return chmod_result;
}
static int test_close(int fd) { assert(fd == result); closes++; return 0; }
static void error_setg_errno(Error **errp, int code, const char *format, ...) {
    (void)format; recorded.code = code; *errp = &recorded;
}
#define memfd_create test_create
#define ftruncate test_resize
#define fchmod test_chmod
#define close test_close
'''
        driver = '''#error Wrong Android branch
#endif
int main(void) {
    Error *error = NULL;
    result = -1;
    assert(qemu_shm_alloc(4096, &error) == -1);
    assert(creates == 1 && !chmods && !resizes && !closes && error->code == EPERM);
    error = NULL; result = 7; chmod_result = -1;
    assert(qemu_shm_alloc(4096, &error) == -1);
    assert(chmods == 1 && !resizes && closes == 1 && error->code == EACCES);
    error = NULL; chmod_result = 0; resize_result = -1;
    assert(qemu_shm_alloc(4096, &error) == -1);
    assert(resizes == 1 && closes == 2 && error->code == ENOSPC);
    error = NULL; result = 0; resize_result = 0;
    assert(qemu_shm_alloc(0, &error) == 0 && !error);
    assert(resizes == 2 && closes == 2 && requested_size == 0);
    return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='pdva-patch-c-test-') as directory:
            root = Path(directory)
            source, binary = root / 'control.c', root / 'control'
            source.write_text(prelude + research.ANDROID_SHM_IMPL + driver)
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', str(source),
                            '-o', str(binary)], check=True, capture_output=True)
            subprocess.run([str(binary)], check=True, timeout=10)
            for data in (self.sources['util/oslib-posix.c'], self.render()['util/oslib-posix.c']):
                source.write_bytes(data)
                text = subprocess.check_output(['cc', '-E', '-P', str(source)])
                if data == self.sources['util/oslib-posix.c']:
                    original = text
                else:
                    self.assertEqual(original, text)
            source.write_text(research.ANDROID_SHM_PROBE)
            flags = ['-D__ANDROID__=1', '-D__BIONIC__=1', '-D__aarch64__=1', '-D__ANDROID_API__=30']
            result = subprocess.run(['cc', '-Werror', *flags,
                '-Dmemfd_create=pdva_missing_memfd', str(source), '-o', str(binary)],
                capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn('pdva_missing_memfd', result.stderr)
            for missing in range(len(flags)):
                result = subprocess.run(['cc', '-Werror', *flags[:missing], *flags[missing + 1:],
                    '-c', str(source), '-o', str(root / 'bad.o')], capture_output=True, text=True)
                self.assertNotEqual(0, result.returncode)
                self.assertIn('PDVA research requires', result.stderr)


class GlibSubprojectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pdva-glib-source-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.glib = self.root / 'glib'
        self.parent = self.glib / 'subprojects'
        self.parent.mkdir(parents=True)
        (self.parent / 'gvdb').mkdir()
        self.archive = self.root / 'source.tar'
        self.write_archive()
        self.pin = research.digest(self.archive)
        self.pins = mock.patch.dict(research.ARCHIVES, {
            name: ('https://example.invalid/fixture', self.pin, 'fixture')
            for name in ('gvdb', 'proxy')
        })
        self.pins.start()
        self.addCleanup(self.pins.stop)
        research.unpack(self.archive, self.root / 'extracted')
        self.source = self.root / 'extracted/fixture'

    def write_archive(self, extra=None):
        with tarfile.open(self.archive, 'w') as output:
            directory = tarfile.TarInfo('fixture')
            directory.type = tarfile.DIRTYPE
            directory.mode = 0o775
            output.addfile(directory)
            member = tarfile.TarInfo('fixture/source.c')
            member.mode = 0o664
            member.size = 8
            output.addfile(member, io.BytesIO(b'reviewed'))
            if extra:
                output.addfile(extra, io.BytesIO(b'x' * extra.size))

    def install(self, name='gvdb'):
        with contextlib.redirect_stdout(io.StringIO()):
            research.materialize_glib_subproject(name, self.archive, self.source, self.glib)

    def test_expected_empty_and_absent_destinations(self):
        self.install('gvdb')
        self.install('proxy')
        for name in ('gvdb', 'proxy-libintl-0.5'):
            self.assertEqual(b'reviewed', (self.parent / name / 'source.c').read_bytes())
        self.assertEqual({'gvdb', 'proxy-libintl-0.5'}, {p.name for p in self.parent.iterdir()})

    def test_absent_gvdb_is_not_the_expected_placeholder(self):
        (self.parent / 'gvdb').rmdir()
        with self.assertRaises(FileNotFoundError):
            self.install()

    def test_existing_empty_proxy_is_rejected(self):
        (self.parent / 'proxy-libintl-0.5').mkdir()
        with self.assertRaisesRegex(RuntimeError, 'Expected absent'):
            self.install('proxy')

    def test_existing_correct_content_is_not_merged(self):
        self.install()
        with self.assertRaisesRegex(RuntimeError, 'Expected empty'):
            self.install()
        self.assertEqual(b'reviewed', (self.parent / 'gvdb/source.c').read_bytes())

    def test_unexpected_populated_directory_or_file_is_preserved(self):
        dest = self.parent / 'gvdb'
        marker = dest / 'unexpected'
        marker.mkdir()
        with self.assertRaisesRegex(RuntimeError, 'Expected empty'):
            self.install()
        self.assertTrue(marker.is_dir())
        marker.rmdir()
        dest.rmdir()
        dest.write_bytes(b'conflict')
        with self.assertRaisesRegex(RuntimeError, 'Expected empty'):
            self.install()
        self.assertEqual(b'conflict', dest.read_bytes())

    @unittest.skipIf(os.name == 'nt', 'Real destination/ancestor symlinks are checked on Linux')
    def test_destination_and_ancestor_symlinks_are_rejected(self):
        dest = self.parent / 'gvdb'
        dest.rmdir()
        outside = self.root / 'outside'
        outside.mkdir()
        dest.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, 'Expected empty'):
            self.install()
        dest.unlink()
        proxy = self.parent / 'proxy-libintl-0.5'
        proxy.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, 'Expected absent'):
            self.install('proxy')
        proxy.unlink()
        dest.mkdir()
        payload = self.source / 'source.c'
        payload.unlink()
        payload.symlink_to(outside / 'missing')
        with self.assertRaisesRegex(RuntimeError, 'Source file type mismatch'):
            self.install()
        payload.unlink()
        payload.write_bytes(b'reviewed')
        dest.rmdir()
        self.parent.rmdir()
        self.parent.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, 'not a real directory'):
            self.install()
        self.assertEqual([], list(outside.iterdir()))

    def test_source_substitution_missing_and_extra_are_rejected(self):
        path = self.source / 'source.c'
        path.write_bytes(b'substituted')
        with self.assertRaisesRegex(RuntimeError, 'blob mismatch'):
            self.install()
        path.unlink()
        with self.assertRaisesRegex(RuntimeError, 'Missing source'):
            self.install()
        path.write_bytes(b'reviewed')
        (self.source / 'extra').write_bytes(b'extra')
        with self.assertRaisesRegex(RuntimeError, 'Extra source'):
            self.install()
        self.assertEqual([], list((self.parent / 'gvdb').iterdir()))

    def test_staged_substitution_is_rejected_before_placeholder_removal(self):
        original = research.shutil.copytree
        def tamper(source, destination, **kwargs):
            result = original(source, destination, **kwargs)
            (destination / 'source.c').write_bytes(b'changed in staging')
            return result
        with mock.patch.object(research.shutil, 'copytree', side_effect=tamper):
            with self.assertRaisesRegex(RuntimeError, 'blob mismatch'):
                self.install()
        self.assertEqual([], list((self.parent / 'gvdb').iterdir()))

    def test_corrupt_archive_and_wrong_root_are_rejected(self):
        self.archive.write_bytes(b'corrupt')
        with self.assertRaisesRegex(RuntimeError, 'Hash mismatch'):
            self.install()
        self.write_archive()
        with self.assertRaisesRegex(RuntimeError, 'Unexpected or duplicate archive path'):
            research.regular_archive_manifest(self.archive, self.pin, 'wrong-root')

    def test_archive_escaping_paths_links_and_duplicates_are_rejected(self):
        for name, kind, link in (
            ('../escape', tarfile.REGTYPE, ''),
            ('/absolute', tarfile.REGTYPE, ''),
            ('fixture/link', tarfile.SYMTYPE, '../../escape'),
            ('fixture/link', tarfile.LNKTYPE, 'fixture/source.c'),
            ('fixture/source.c', tarfile.REGTYPE, ''),
        ):
            member = tarfile.TarInfo(name)
            member.type, member.linkname = kind, link
            member.mode = 0o644
            self.write_archive(member)
            with self.subTest(name=name, kind=kind), self.assertRaises(RuntimeError):
                research.regular_archive_manifest(self.archive, research.digest(self.archive), 'fixture')
        self.assertFalse((self.root / 'escape').exists())


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
