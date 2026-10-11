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


class ElfInspectionTests(unittest.TestCase):
    def fixture(self, mode='static'):
        # Structured synthetic ELF for inspection only, never executable evidence.
        data = bytearray(0x5000)
        pack = lambda fmt, offset, *values: research.struct.pack_into(fmt, data, offset, *values)
        names = ['.text', '.dynstr', '.dynsym', '.rela.dyn', '.note.android.ident',
                 '.dynamic', '.data', '.strtab', '.symtab', '.shstrtab']
        shstrings = b'\0' + b''.join(n.encode() + b'\0' for n in names)
        strtab = b'\0_start\0__libc_init\0'
        dynstr = b'\0libc.so\0__libc_init\0'
        note = research.struct.pack('<III', 8, 132, 1) + b'Android\0'
        note += research.struct.pack('<I', 30) + b'r28c'.ljust(64, b'\0') + b'13676358'.ljust(64, b'\0')
        for offset, content in ((0x400, note), (0x600, dynstr), (0x3500, shstrings), (0x3600, strtab)):
            data[offset:offset+len(content)] = content
        pack('<QQq', 0x900, 0xa300, 1027, 0x5000)
        pack('<IBBHQQ', 0x3718, 1, 0x12, 0, 1, 0x5000, 4)
        pack('<IBBHQQ', 0x3730, 8, 0x12, 0, 1, 0x5004, 4)
        tags = [(30, 8), (0x6ffffffb, 0x08000001), (5, 0x600), (10, len(dynstr)), (6, 0x800), (11, 24)]
        tags += [(7, 0x900), (8, 24), (9, 24), (0x6ffffff9, 1)]
        if mode == 'dynamic':
            tags += [(1, 1)]
            pack('<IBBHQQ', 0x818, 9, 0x12, 0, 0, 0, 0)
        tags += [(0, 0)]
        for i, (tag, value) in enumerate(tags): pack('<qQ', 0x2100 + i*16, tag, value)
        ph = [(1,4,0,0,0,0x1000,0x1000,0x4000),
              (1,5,0x1000,0x5000,0x5000,0x100,0x100,0x4000),
              (1,6,0x2000,0xa000,0xa000,0x1000,0x1000,0x4000),
              (2,6,0x2100,0xa100,0xa100,len(tags)*16,len(tags)*16,8),
              (0x6474e551,6,0,0,0,0,0,0),
              (0x6474e552,4,0x2000,0xa000,0xa000,0x1000,0x1000,1)]
        if mode == 'dynamic':
            interp = b'/system/bin/linker64\0'; data[0x500:0x500+len(interp)] = interp
            ph.append((3,4,0x500,0x500,0x500,len(interp),len(interp),1))
        for i,p in enumerate(ph): pack('<IIQQQQQQ',64+i*56,*p)
        specs = [(1,6,0x5000,0x1000,0x100,0,0), (3,2,0x600,0x600,len(dynstr),0,0),
                 (11,2,0x800,0x800,48 if mode == 'dynamic' else 24,2,24), (4,2,0x900,0x900,24,3,24),
                 (7,2,0x400,0x400,len(note),0,0), (6,3,0xa100,0x2100,len(tags)*16,2,16),
                 (1,3,0xa000,0x2000,0x1000,0,0), (3,0,0,0x3600,len(strtab),0,0),
                 (2,0,0,0x3700,72,8,24), (3,0,0,0x3500,len(shstrings),0,0)]
        for i,(name,s) in enumerate(zip(names,specs),1):
            kind,flags,addr,offset,size,link,entsize=s
            pack('<IIQQQQIIQQ',0x4000+i*64,shstrings.index(name.encode()+b'\0'),kind,flags,addr,offset,size,link,0,8,entsize)
        pack('<16sHHIQQQIHHHHHH',0,b'\x7fELF\x02\x01\x01'+bytes(9),3,183,1,0x5000,64,0x4000,0,64,56,len(ph),64,11,10)
        return data

    def inspect(self, data, mode='static'):
        return research.inspect_android_elf(bytes(data), mode)

    def test_valid_dynamic_structure_and_static_candidate_are_distinct(self):
        self.assertEqual(self.inspect(self.fixture('dynamic'),'dynamic')['needed'], ['libc.so'])
        report = self.inspect(self.fixture())
        self.assertEqual(report['relocations'], {'R_AARCH64_RELATIVE': 1})
        self.assertFalse(report['static_startup_accepted'])

    def test_static_candidate_cannot_be_promoted_by_boolean_or_elf_shape(self):
        report = self.inspect(self.fixture())
        evidence = {'binary_sha256': report['sha256'], 'mode': 'static',
                    'crtbegin': {'crtbegin_dynamic.o': 'fixture'}, 'libc_static_init': True,
                    'static_startup_accepted': True}
        with self.assertRaisesRegex(RuntimeError, 'Unsupported Android static PIE startup'):
            research.require_static_startup(report,evidence)

    def test_missing_and_substituted_startup_evidence_rejected(self):
        report = self.inspect(self.fixture())
        for evidence in ({}, {'binary_sha256':'wrong','mode':'static','crtbegin':True,'libc_static_init':True},
                         {'binary_sha256':report['sha256'],'mode':'dynamic','crtbegin':True,'libc_static_init':True}):
            with self.assertRaisesRegex(RuntimeError, 'evidence missing'):
                research.require_static_startup(report,evidence)

    def test_modes_cannot_bypass_interpreter_or_dependency_checks(self):
        for actual,requested in (('static','dynamic'),('dynamic','static')):
            with self.assertRaises(RuntimeError): self.inspect(self.fixture(actual),requested)
        data=self.fixture('dynamic'); research.struct.pack_into('<I',data,64+6*56,0)
        with self.assertRaisesRegex(RuntimeError,'interpreter'): self.inspect(data,'dynamic')

    def test_foreign_dependency_and_glibc_version_rejected(self):
        data=self.fixture('dynamic'); data[0x601:0x608]=b'evil.so'
        with self.assertRaisesRegex(RuntimeError,'dependencies'): self.inspect(data,'dynamic')
        data=self.fixture(); data[0x601:0x607]=b'GLIBC_'
        with self.assertRaisesRegex(RuntimeError,'glibc'): self.inspect(data)

    def test_wrong_architecture_class_byte_order_and_ndk_rejected(self):
        for offset,value in ((4,1),(5,2),(18,62),(0x414,29),(0x418,ord('x'))):
            data=self.fixture(); data[offset]=value
            with self.subTest(offset=offset),self.assertRaises(RuntimeError): self.inspect(data)

    def test_invalid_entrypoint_or_shared_library_without_pie_flag_rejected(self):
        for entry in (0,0xa100,0x6000):
            data=self.fixture(); research.struct.pack_into('<Q',data,24,entry)
            with self.assertRaisesRegex(RuntimeError,'entrypoint'): self.inspect(data)
        data=self.fixture(); research.struct.pack_into('<Q',data,0x2118,1)
        with self.assertRaisesRegex(RuntimeError,'PIE'): self.inspect(data)

    def test_wx_load_executable_stack_and_bad_alignment_rejected(self):
        for offset,value in ((64+56+4,7),(64+4*56+4,7),(64+48,4096)):
            data=self.fixture(); research.struct.pack_into('<I',data,offset,value)
            with self.assertRaises(RuntimeError): self.inspect(data)

    def test_invalid_segment_size_overlap_and_relro_rejected(self):
        for offset,value in ((64+40,1),(64+56+16,0),(64+5*56+16,0xb000)):
            data=self.fixture(); research.struct.pack_into('<Q',data,offset,value)
            with self.assertRaises(RuntimeError): self.inspect(data)

    def test_forbidden_paths_textrel_and_missing_now_rejected(self):
        for tag in (14,15,22,29):
            data=self.fixture(); research.struct.pack_into('<q',data,0x2100,tag)
            with self.assertRaisesRegex(RuntimeError,'forbidden'): self.inspect(data)
        data=self.fixture(); research.struct.pack_into('<Q',data,0x2108,0)
        research.struct.pack_into('<Q',data,0x2118,0x08000000)
        with self.assertRaisesRegex(RuntimeError,'bind-now'): self.inspect(data)

    def test_unsupported_relocations_and_invalid_targets_rejected(self):
        for offset,value in ((0x908,1032),(0x908,1027+(1<<32)),(0x900,0x5000),(0x910,0xffff)):
            data=self.fixture(); research.struct.pack_into('<Q',data,offset,value)
            with self.assertRaisesRegex(RuntimeError,'relocation'): self.inspect(data)

    def test_start_symbol_and_static_libc_definition_required(self):
        for offset in (0x3718+6,0x3730+6):
            data=self.fixture(); research.struct.pack_into('<H',data,offset,0)
            with self.assertRaises(RuntimeError): self.inspect(data)

    def test_substituted_truncated_and_malformed_tables_rejected(self):
        for data in (b'MZ'+bytes(500),bytes(self.fixture()[:60]),bytes(self.fixture()[:0x4100])):
            with self.assertRaises(RuntimeError): self.inspect(data)
        for offset,value in ((32,2**64-1),(40,2**64-1),(0x4000+3*64+56,8)):
            data=self.fixture(); research.struct.pack_into('<Q',data,offset,value)
            with self.assertRaises(RuntimeError): self.inspect(data)

    def link_fixture(self, root):
        build = root / 'qemu-build'; build.mkdir()
        toolbin = root / 'ndk/bin'; toolbin.mkdir(parents=True)
        for name in ('aarch64-linux-android30-clang', 'ld.lld'):
            (toolbin / name).write_bytes(b'fixture never executed')
        lib = root / 'ndk/sysroot/usr/lib/aarch64-linux-android'
        (lib / '30').mkdir(parents=True)
        for name in ('crtbegin_dynamic.o', 'crtend_android.o'):
            (lib / '30' / name).write_bytes(b'inspection fixture only')
        (lib / 'libc.a').write_bytes(b'synthetic archive, never executed')
        binary = build / 'qemu-system-aarch64'; binary.write_bytes(self.fixture())
        commands = root / 'commands.log'; compile_log = root / 'compile.log'
        commands.write_text(research.shlex.join([str(toolbin / 'aarch64-linux-android30-clang'),
                            '-static-pie', '-o', 'qemu-system-aarch64'])+'\n')
        compile_log.write_text('[1/1] '+commands.read_text()+research.shlex.join([str(toolbin / 'ld.lld'), '-static', '-pie', '-m', 'aarch64linux',
            '--no-dynamic-linker', '-Map', str(build / 'qemu.map'), '-o', 'qemu-system-aarch64', str(lib / '30/crtbegin_dynamic.o'),
            str(lib / '30/crtend_android.o')])+'\n')
        (build / 'qemu.map').write_text('  5000 5000 40 4 '+str(lib / 'libc.a')+'(libc_init_static.o):(.text)\n' +
            ''.join('  5000 5000 40 4 '+str(lib / '30' / n)+':(.text)\n' for n in ('crtbegin_dynamic.o', 'crtend_android.o')))
        return binary, build, toolbin, commands, compile_log

    def test_link_evidence_is_bound_to_output_and_actual_input_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.link_fixture(Path(directory))
            evidence = research.qemu_link_evidence(*args, lambda _: None)
            self.assertEqual(evidence['binary_sha256'], research.digest(args[0]))
            self.assertEqual(evidence['mode'], 'static')
            self.assertTrue(evidence['libc_static_init'])
            with self.assertRaisesRegex(RuntimeError,'Unsupported'):
                research.require_static_startup(self.inspect(args[0].read_bytes()), evidence)

    def test_generated_link_mode_and_actual_driver_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.link_fixture(Path(directory))
            for path,old,new in ((args[3],'-static-pie','-shared'),
                                 (args[4],'--no-dynamic-linker','--dynamic-linker=foreign'),
                                 (args[4],'crtbegin_dynamic.o','crtbegin_so.o')):
                original=path.read_text(); path.write_text(original.replace(old,new))
                with self.assertRaises(RuntimeError): research.qemu_link_evidence(*args, lambda _: None)
                path.write_text(original)

    def test_missing_map_startup_and_ambiguous_final_command_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.link_fixture(Path(directory))
            path=args[3]; original=path.read_text(); path.write_text(original*2)
            with self.assertRaisesRegex(RuntimeError,'ambiguous'): research.qemu_link_evidence(*args, lambda _: None)
            path.write_text(original)
            (args[1]/'qemu.map').write_text('libc_init_static.o is mentioned but is not a map input\n')
            with self.assertRaisesRegex(RuntimeError,'startup input'): research.qemu_link_evidence(*args, lambda _: None)


class LinkProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.args = ElfInspectionTests().link_fixture(Path(self.temp.name))
        self.messages = []

    def inspect(self, mode='static', dependencies=None):
        return research.qemu_link_evidence(*self.args, self.messages.append, mode, dependencies)

    def command(self, text):
        old = self.args[3].read_text()
        self.args[3].write_text(text)
        self.args[4].write_text(self.args[4].read_text().replace(old, text))

    def response(self):
        tokens = research.shlex.split(self.args[3].read_text())
        path = self.args[1] / 'qemu-system-aarch64.rsp'
        path.write_text(research.shlex.join(tokens[1:]))
        self.command(research.shlex.join([tokens[0], '@' + path.name]) + '\n')
        return path

    def dynamic(self):
        self.command(self.args[3].read_text().replace('-static-pie', '-pie'))
        lib = self.args[2].parent / 'sysroot/usr/lib/aarch64-linux-android'
        (lib / '30/libc.so').write_bytes(b'fixture stub, never executed')
        text = self.args[4].read_text().replace(' -static ', ' ').replace('--no-dynamic-linker',
                    '-dynamic-linker /system/bin/linker64')
        text = text.rstrip() + ' ' + research.shlex.join(['-L' + str(lib / '30'), '-lc']) + '\n'
        self.args[4].write_text(text)
        (self.args[1] / 'qemu.map').write_text(''.join('  5000 5000 40 4 ' + str(lib / '30' / name) + ':(.text)\n'
            for name in ('crtbegin_dynamic.o', 'crtend_android.o')))

    def test_retained_response_resolves_output_and_preserves_identity(self):
        response = self.response()
        evidence = self.inspect()
        self.assertEqual(evidence['response']['sha256'], research.digest(response))
        self.assertTrue(any('"candidate_count": 1' in m for m in self.messages))
        self.assertTrue(any('"input_truncated": false' in m for m in self.messages))

    def test_response_missing_nested_oversized_and_malformed_fail(self):
        path = self.response()
        for content in ('@nested.rsp', '"unterminated', '', 'x' * (1024 * 1024 + 1)):
            path.write_text(content)
            with self.subTest(content=content[:24]), self.assertRaises(RuntimeError): self.inspect()
        path.unlink()
        with self.assertRaisesRegex(RuntimeError, 'retained response'): self.inspect()

    def test_response_traversal_absolute_and_mixed_arguments_fail(self):
        original = self.args[3].read_text()
        compiler = research.shlex.split(original)[0]
        for ref in ('@../qemu-system-aarch64.rsp', '@/tmp/qemu-system-aarch64.rsp',
                    '@qemu-system-aarch64.rsp -o qemu-system-aarch64'):
            self.command(research.shlex.quote(compiler) + ' ' + ref + '\n')
            with self.assertRaises(RuntimeError): self.inspect()

    def test_response_symlink_and_ancestor_fail(self):
        path = self.response()
        original = Path.is_symlink
        for bad in (path, path.parent):
            with mock.patch.object(Path, 'is_symlink', lambda p: p == bad or original(p)):
                with self.assertRaisesRegex(RuntimeError, 'unsafe'): self.inspect()

    def test_wrappers_shell_composition_and_substituted_compiler_fail(self):
        original = self.args[3].read_text()
        for text in ('env ' + original, 'sh -c ' + research.shlex.quote(original),
                     original.rstrip() + ' && true\n', original.replace('android30-clang', 'android29-clang'),
                     original.rstrip() + ' $(touch sentinel)\n'):
            self.command(text)
            with self.subTest(text=text[:40]), self.assertRaises(RuntimeError): self.inspect()
        self.assertFalse((self.args[1] / 'sentinel').exists())

    def test_output_ambiguity_wrong_output_and_missing_actual_execution_fail(self):
        original = self.args[3].read_text()
        for text in (original * 2, original.rstrip() + ' -o other\n',
                     original.replace('qemu-system-aarch64', 'different'), original.rstrip() + ' -o\n'):
            self.command(text)
            with self.assertRaises(RuntimeError): self.inspect()
        self.command(original)
        self.args[4].write_text(self.args[4].read_text().replace('[1/1] ' + original, ''))
        with self.assertRaisesRegex(RuntimeError, 'actual verbose'): self.inspect()

    def test_dynamic_link_evidence_and_static_mode_mismatch(self):
        self.dynamic()
        evidence = self.inspect('dynamic')
        self.assertFalse(evidence['libc_static_init'])
        self.assertIn('libc.so', evidence['shared_inputs'])
        with self.assertRaises(RuntimeError): self.inspect('static')
        self.response()
        self.assertEqual(self.inspect('dynamic')['mode'], 'dynamic')

    def test_dynamic_foreign_search_missing_library_and_wrong_crt_fail(self):
        self.dynamic()
        original = self.args[4].read_text()
        for text in (original.rstrip() + ' -L/host/lib\n', original.replace('-lc', '-lforeign'),
                     original.replace('crtbegin_dynamic.o', 'crtbegin_static.o'),
                     original.replace('aarch64linux', 'elf_x86_64'), original.replace('qemu.map', 'other.map'),
                     original.rstrip() + ' -m\n'):
            self.args[4].write_text(text)
            with self.assertRaises(RuntimeError): self.inspect('dynamic')

    def test_map_missing_input_and_dependency_substitution_fail(self):
        lib = self.args[2].parent / 'sysroot/usr/lib/aarch64-linux-android/libc.a'
        lib.unlink()
        with self.assertRaisesRegex(RuntimeError, 'Link input'): self.inspect()
        lib.write_bytes(b'fixture')
        with self.assertRaisesRegex(RuntimeError, 'changed after verification'):
            self.inspect(dependencies={str(lib): '0' * 64})
        with self.assertRaisesRegex(RuntimeError, 'Missing source-built'):
            self.inspect(dependencies={})

    def test_dynamic_relocations_reject_bad_kind_symbol_and_target(self):
        for offset, value in ((0x908, 1031), (0x908, (999 << 32) | 1025),
                              (0x900, 0x5000), (0x910, 0xffffffffff)):
            data = ElfInspectionTests().fixture('dynamic')
            research.struct.pack_into('<Q', data, offset, value)
            with self.assertRaisesRegex(RuntimeError, 'relocation'):
                research.inspect_android_elf(bytes(data), 'dynamic')

    def test_dynamic_startup_import_and_relocation_metadata_required(self):
        data = ElfInspectionTests().fixture('dynamic')
        research.struct.pack_into('<H', data, 0x818 + 6, 1)
        with self.assertRaisesRegex(RuntimeError, 'Bionic startup'):
            research.inspect_android_elf(bytes(data), 'dynamic')
        data = ElfInspectionTests().fixture('dynamic')
        research.struct.pack_into('<Q', data, 0x2100 + 7 * 16 + 8, 48)
        with self.assertRaisesRegex(RuntimeError, 'RELA'):
            research.inspect_android_elf(bytes(data), 'dynamic')

    def test_ndk_stub_exports_require_real_structure_and_defined_symbol(self):
        path = self.args[1] / 'fixture.so'
        data = ElfInspectionTests().fixture('dynamic')
        path.write_bytes(data)
        self.assertNotIn('__libc_init', research.ndk_dynamic_exports(path))
        research.struct.pack_into('<H', data, 0x818 + 6, 1)
        path.write_bytes(data)
        self.assertIn('__libc_init', research.ndk_dynamic_exports(path))
        for invalid in (bytes(data[:20]), b'MZ' + bytes(100), bytes(data[:0x4050])):
            path.write_bytes(invalid)
            with self.assertRaises(RuntimeError): research.ndk_dynamic_exports(path)

    def test_dynamic_source_built_closure_is_bound_before_acceptance(self):
        self.dynamic()
        prefix = Path(self.temp.name) / 'target/lib'
        prefix.mkdir(parents=True)
        hashes = {}
        for name in ('libfdt.a', 'libglib-2.0.a', 'libpcre2-8.a'):
            path = prefix / name
            path.write_bytes(b'source-build fixture never executed')
            hashes[str(path.resolve())] = research.digest(path)
            with (self.args[1] / 'qemu.map').open('a') as stream:
                stream.write('  5000 5000 40 4 ' + str(path) + '(unit.o):(.text)\n')
            self.args[4].write_text(self.args[4].read_text().rstrip() + ' ' + research.shlex.quote(str(path)) + '\n')
        self.assertEqual(self.inspect('dynamic', hashes)['mode'], 'dynamic')
        (prefix / 'libglib-2.0.a').write_bytes(b'substituted')
        with self.assertRaisesRegex(RuntimeError, 'changed after verification'):
            self.inspect('dynamic', hashes)

    def test_actual_crt_must_also_be_present_in_map(self):
        path = self.args[1] / 'qemu.map'
        path.write_text('\n'.join(line for line in path.read_text().splitlines() if 'crtend_android.o' not in line))
        with self.assertRaisesRegex(RuntimeError, 'CRT missing'): self.inspect()

    def test_response_quoting_is_preserved_and_not_display_truncated(self):
        path = self.response()
        tokens = research.link_tokens(path.read_text()) + ['a path with spaces.o', 'quoted"name.o'] + ['padding.o'] * 8000
        path.write_text(research.shlex.join(tokens))
        self.assertGreater(path.stat().st_size, 60000)
        expanded, record = research.expand_link_response(['compiler', '@' + path.name], self.args[1], self.args[0])
        self.assertEqual(expanded[1:], tokens)
        self.assertEqual(record['sha256'], research.digest(path))


class NinjaSelectionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.path = self.root / 'ninja'
        self.path.write_bytes(self.elf())
        self.env = {'PATH': str(self.root)}
        self.run = mock.Mock(return_value='1.13.2\n')
        self.access = mock.patch.object(research.os, 'access', return_value=True)
        self.access.start(); self.addCleanup(self.access.stop)
        self.which = mock.patch.object(research.shutil, 'which', return_value=str(self.path))
        self.which.start(); self.addCleanup(self.which.stop)

    @staticmethod
    def elf(machine=62, interpreter=b'/lib64/ld-linux-x86-64.so.2\0'):
        # Synthetic bytes for inspection only; never executed as a tool.
        header = bytearray(64)
        header[:7] = b'\x7fELF\x02\x01\x01'
        research.struct.pack_into('<HHI', header, 16, 3, machine, 1)
        research.struct.pack_into('<Q', header, 32, 64)
        research.struct.pack_into('<HH', header, 54, 56, 1)
        entry = bytearray(56)
        research.struct.pack_into('<I', entry, 0, 3)
        research.struct.pack_into('<Q', entry, 8, 120)
        research.struct.pack_into('<Q', entry, 32, len(interpreter))
        return bytes(header + entry) + interpreter

    def select(self):
        return research.select_host_ninja(self.env, self.run, lambda _: None)

    def test_host_discovery_and_minimum_version(self):
        for version in ('1.8.2', '1.13.2', '2.0.0'):
            self.run.return_value = version + '\n'
            path, sha = self.select()
            self.assertEqual(path, self.path.resolve())
            self.assertEqual(sha, research.digest(path))
            self.assertEqual(self.run.call_args.args, (path, '--version'))
            self.assertEqual(self.run.call_args.kwargs['env'], self.env)

    def test_missing_discovery_and_explicit_path_never_fall_back(self):
        with mock.patch.object(research.shutil, 'which', return_value=None):
            with self.assertRaisesRegex(RuntimeError, 'not found'): self.select()
        self.env['NINJA'] = str(self.root / 'missing')
        with self.assertRaises(FileNotFoundError): self.select()
        self.run.assert_not_called()

    def test_explicit_absolute_tool_is_the_only_candidate(self):
        self.env['NINJA'] = str(self.path)
        with mock.patch.object(research.shutil, 'which', side_effect=AssertionError('fallback')):
            self.assertEqual(self.select()[0], self.path.resolve())

    def test_relative_or_empty_environment_paths_rejected(self):
        for path in ('', '.', str(self.root) + os.pathsep, str(self.root) + os.pathsep + 'relative'):
            self.env = {'PATH': path}
            with self.assertRaisesRegex(RuntimeError, 'host PATH'): self.select()
        for override in ('', 'ninja', './ninja'):
            self.env = {'PATH': str(self.root), 'NINJA': override}
            with self.assertRaisesRegex(RuntimeError, 'override'): self.select()
        self.run.assert_not_called()

    def test_non_executable_and_directory_rejected_before_execution(self):
        with mock.patch.object(research.os, 'access', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'host executable'): self.select()
        self.env['NINJA'] = str(self.root)
        with self.assertRaisesRegex(RuntimeError, 'host executable'): self.select()
        self.run.assert_not_called()

    def test_old_malformed_and_failed_version_commands_rejected(self):
        for output in ('1.8.1', '0.99.99', '', 'ninja 1.13.2', '1.13.2\n1.13.2', '1.13.2.git'):
            self.run.return_value = output
            with self.subTest(output=output), self.assertRaisesRegex(RuntimeError, 'version'):
                self.select()
        self.run.side_effect = RuntimeError('Command exit 1')
        with self.assertRaisesRegex(RuntimeError, 'Command exit 1'): self.select()

    def test_android_foreign_and_script_files_never_executed(self):
        for data in (self.elf(machine=183), self.elf(interpreter=b'/system/bin/linker64\0'),
                     b'MZ' + bytes(128), b'#!/bin/sh\necho 1.13.2\n', b'\x7fELF'):
            self.path.write_bytes(data)
            with self.assertRaises(RuntimeError): self.select()
        self.run.assert_not_called()

    def test_corrupt_program_headers_and_interpreter_rejected(self):
        for position, replacement in ((54, b'\x00\x00'), (56, b'\xff\xff'),
                                      (32, b'\xff' * 8), (96, b'\xff' * 8)):
            data = bytearray(self.elf()); data[position:position+len(replacement)] = replacement
            self.path.write_bytes(data)
            with self.assertRaises((RuntimeError, OverflowError, OSError)): self.select()
        self.run.assert_not_called()

    def test_substitution_during_version_probe_rejected(self):
        def substitute(*args, **kwargs):
            self.path.write_bytes(self.elf() + b'changed')
            return '1.13.2'
        self.run.side_effect = substitute
        with self.assertRaisesRegex(RuntimeError, 'executable changed'): self.select()

    def test_later_environment_and_file_substitution_rejected_before_spawn(self):
        path, sha = self.select()
        runner = object.__new__(research.Research)
        runner.host_ninja, runner.ninja_sha = path, sha
        runner.env = {'NINJA': str(path)}
        with mock.patch.object(research.subprocess, 'Popen') as spawn:
            with self.assertRaisesRegex(RuntimeError, 'environment changed'):
                runner.run(path, '--version', env={'NINJA': str(self.root / 'other')})
            self.path.write_bytes(self.elf() + b'changed')
            with self.assertRaisesRegex(RuntimeError, 'executable changed'):
                runner.run(path, '--version')
            spawn.assert_not_called()

    def test_configure_and_build_use_selected_identity(self):
        import ast
        import inspect
        tree = ast.parse(inspect.getsource(research))
        build = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'build')
        calls = [n for n in ast.walk(build) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == 'run']
        ninja_calls = [n for n in calls if n.args and isinstance(n.args[0], ast.Attribute)
                       and n.args[0].attr == 'host_ninja']
        self.assertEqual(len(ninja_calls), 3)  # GLib build, QEMU build, command inventory.
        config = next(n for n in calls if any(isinstance(a, ast.Constant)
                                             and a.value == '--target-list=aarch64-softmmu' for a in n.args))
        option = next(a for a in config.args if isinstance(a, ast.JoinedStr)
                      and isinstance(a.values[0], ast.Constant) and a.values[0].value == '--ninja=')
        self.assertEqual(ast.unparse(option.values[1].value), 'self.host_ninja')


class FdtDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.source = research.QEMU_FDT_ANCHOR.encode()
        self.patch_pin = mock.patch.object(research, 'QEMU_FDT_PATCH_INPUT',
                                           research.hashlib.sha256(self.source).hexdigest())
        self.patch_pin.start()
        self.addCleanup(self.patch_pin.stop)
        self.members = '\n'.join(name + '.o' for name in research.FDT_OBJECTS) + '\n'
        self.headers = ("Class: ELF64\nData: 2's complement, little endian\n"
                        "Type: REL (Relocatable file)\nMachine: AArch64\n") * len(research.FDT_OBJECTS)
        self.symbols = '0000000000000110 T fdt_find_max_phandle\n'

    def render(self, source=None, directory='/review/target/lib', target='aarch64-linux-android30'):
        return research.render_android_fdt_patch(self.source if source is None else source,
                                                directory, target)

    def test_android_static_directory_and_original_other_platform_branch(self):
        text = self.render().decode()
        self.assertIn("if cc.get_define('__ANDROID__') != ''", text)
        self.assertIn("dirs: ['/review/target/lib'], static: true", text)
        self.assertIn("required: fdt_opt == 'system'", text)
        self.assertIn('  else\n' + research.QEMU_FDT_ANCHOR + '  endif\n', text)

    def test_substituted_source_and_duplicate_application_rejected(self):
        for source in (self.source + b'changed', self.render()):
            with self.subTest(source=source), self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
                self.render(source)

    def test_missing_or_duplicate_anchor_rejected_even_with_matching_digest(self):
        for source in (b'wrong anchor\n', self.source * 2):
            with mock.patch.object(research, 'QEMU_FDT_PATCH_INPUT',
                                   research.hashlib.sha256(source).hexdigest()):
                with self.assertRaisesRegex(RuntimeError, 'anchor mismatch'):
                    self.render(source)

    def test_wrong_target_rejected(self):
        for target in ('aarch64-linux-android29', 'x86_64-linux-android30', 'aarch64-linux-gnu'):
            with self.subTest(target=target), self.assertRaisesRegex(RuntimeError, 'patch target'):
                self.render(target=target)

    def test_unsafe_or_host_search_directories_rejected(self):
        for directory in ('/usr/lib', '/review/lib', 'target/lib', '/review/../target/lib',
                          '/review/./target/lib', '/review//target/lib', '/review space/target/lib',
                          "/review'path/target/lib", '/review\\target/lib', '/review/target/lib\n'):
            with self.subTest(directory=directory), self.assertRaisesRegex(RuntimeError, 'search path'):
                self.render(directory=directory)

    def test_every_archive_member_and_required_symbol_accepted(self):
        research.validate_fdt_inspection(self.members, self.headers, self.symbols)

    def test_missing_extra_or_substituted_archive_members_rejected(self):
        for members in ('fdt.o\n', self.members + 'host.o\n',
                        self.members.replace('fdt_ro.o', 'host.o'), self.members.replace('fdt_ro.o\n', '')):
            with self.subTest(members=members), self.assertRaisesRegex(RuntimeError, 'archive members'):
                research.validate_fdt_inspection(members, self.headers, self.symbols)

    def test_one_wrong_member_abi_is_rejected(self):
        for old, new in [('AArch64', 'Advanced Micro Devices X86-64'), ('ELF64', 'ELF32'),
                         ("little endian", "big endian"), ('REL (Relocatable file)', 'DYN')]:
            with self.subTest(old=old), self.assertRaisesRegex(RuntimeError, 'target ABI'):
                research.validate_fdt_inspection(self.members, self.headers.replace(old, new, 1), self.symbols)

    def test_truncated_or_extra_member_inspection_is_rejected(self):
        for headers in (self.headers.split('Machine:')[0], self.headers + self.headers):
            with self.assertRaisesRegex(RuntimeError, 'target ABI'):
                research.validate_fdt_inspection(self.members, headers, self.symbols)

    def test_missing_undefined_or_ambiguous_required_symbol_rejected(self):
        for symbols in ('', '                 U fdt_find_max_phandle\n',
                        self.symbols * 2, self.symbols.replace(' T ', ' W ')):
            with self.subTest(symbols=symbols), self.assertRaisesRegex(RuntimeError, 'required symbol'):
                research.validate_fdt_inspection(self.members, self.headers, symbols)

    def identity_fixture(self, root):
        (root / 'lib').mkdir(); (root / 'include').mkdir()
        (root / 'lib/libfdt.a').write_bytes(b'synthetic source-built archive')
        hashes = {}
        for name in research.FDT_HEADERS:
            (root / 'include' / name).write_bytes(name.encode())
            hashes[name] = research.digest(root / 'include' / name)
        return research.digest(root / 'lib/libfdt.a'), hashes

    def test_archive_and_header_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); archive_sha, hashes = self.identity_fixture(root)
            with contextlib.redirect_stdout(io.StringIO()):
                research.verify_fdt_identity(root, archive_sha, hashes)
                for relative in ('lib/libfdt.a', 'include/libfdt.h', 'include/libfdt_env.h', 'include/fdt.h'):
                    path = root / relative; original = path.read_bytes(); path.write_bytes(b'host substitution')
                    with self.subTest(relative=relative), self.assertRaisesRegex(RuntimeError, 'Hash mismatch'):
                        research.verify_fdt_identity(root, archive_sha, hashes)
                    path.write_bytes(original)
                with self.assertRaisesRegex(RuntimeError, 'headers'):
                    research.verify_fdt_identity(root, archive_sha, {'libfdt.h': hashes['libfdt.h']})

    def test_foreign_target_prefix_rejected_before_source_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); qemu = root / 'qemu-source/pinned'; qemu.mkdir(parents=True)
            path = qemu / 'meson.build'; path.write_bytes(self.source)
            with self.assertRaisesRegex(RuntimeError, 'target prefix'):
                research.apply_android_fdt_patch(qemu, root / 'host/target', lambda _: None)
            self.assertEqual(self.source, path.read_bytes())

    def test_invalid_source_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); qemu = root / 'qemu-source/pinned'; qemu.mkdir(parents=True)
            path = qemu / 'meson.build'; path.write_bytes(b'substituted source')
            with self.assertRaises(RuntimeError):
                research.apply_android_fdt_patch(qemu, root / 'target', lambda _: None)
            self.assertEqual(b'substituted source', path.read_bytes())

    def test_link_control_checks_android_bionic_aarch64_and_api30(self):
        for token in ('__ANDROID__', '__BIONIC__', '__aarch64__', '__ANDROID_API__ != 30',
                      '#include <libfdt.h>', '#include <libfdt_env.h>', 'fdt_find_max_phandle(NULL, NULL)'):
            self.assertIn(token, research.ANDROID_FDT_PROBE)


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
