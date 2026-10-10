#!/usr/bin/env python3
"""Bounded, non-executing Android cross-build research; see the evidence ledger.

Python standard library only. Linux x86-64, Python >=3.12. Outputs live in a new
runner temporary directory, never in the checkout. Every failed stage is fatal.
No target program is run, installed into Android, uploaded or published.
"""
import hashlib
import json
import difflib
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat
import struct
import shlex
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
import zipfile

# Independently retrieved/reviewed before publication; not hashes learned in CI.
# name: (URL, SHA-256, archive top-level directory)
ARCHIVES = {
    'qemu': ('https://codeload.github.com/qemu/qemu/tar.gz/4fc49f46dc95d4a27de2509e7fceb2931e91faeb',
             'a5a78e7d395ed096a7b2d98375978d0e2cf73f62c49a081ca48fa665d479b09f',
             'qemu-4fc49f46dc95d4a27de2509e7fceb2931e91faeb'),
    'glib': ('https://codeload.github.com/GNOME/glib/tar.gz/e05063ccc6c8f222465a1080927f4c14349f3de6',
             '9c74d8dc96a547a544f3f479bc6f2fe8a333524ff44c997998ebe9963a63ad52',
             'glib-e05063ccc6c8f222465a1080927f4c14349f3de6'),
    'pcre2': ('https://github.com/PCRE2Project/pcre2/releases/download/pcre2-10.46/pcre2-10.46.tar.bz2',
              '15fbc5aba6beee0b17aecb04602ae39432393aba1ebd8e39b7cabf7db883299f', 'pcre2-10.46'),
    'libffi': ('https://github.com/libffi/libffi/releases/download/v3.5.2/libffi-3.5.2.tar.gz',
               'f3a3082a23b37c293a4fcd1053147b371f2ff91fa7ea1b2a52e335676bac82dc', 'libffi-3.5.2'),
    'proxy': ('https://github.com/frida/proxy-libintl/archive/refs/tags/0.5.tar.gz',
              'f7a1cbd7579baaf575c66f9d99fb6295e9b0684a28b095967cfda17857595303', 'proxy-libintl-0.5'),
    'gvdb': ('https://codeload.github.com/GNOME/gvdb/tar.gz/2b42fc75f09dbe1cd1057580b5782b08f2dcb400',
             '069a00aa1fc893f18423602f4e095583be5a220429f6e8a58d70511490b4b019',
             'gvdb-2b42fc75f09dbe1cd1057580b5782b08f2dcb400'),
}
# Upstream GitLab archives are bot-blocked. Fetch only these exact Git objects,
# then verify pinned commit/tree objects and every raw blob, type and mode.
# No git archive/checkout: attributes, CRLF filters and export rules cannot edit source.
GIT_INPUTS = {
    'dtc': ('b6910bec11614980a21e46fbccc35934b671bd81',
            '5de1e174f53a6ea499a49ac7b5eb7fe816dd9902'),
    'keycodemapdb': ('f5772a62ec52591ff6870b7e8ef32482371f22c6',
                     'eaa3f9fb1e2c7687b334f57cb605140cb5450f16'),
    'berkeley-softfloat-3': ('b64af41c3276f97f0e181920400ee056b9c88037',
                            '5f46f374bcf9aef50442ba5fd25f3b5bcdf963c4'),
    'berkeley-testfloat-3': ('e7af9751d9f9fd3b47911f51a5cfd08af256a9ab',
                            '9e166ce5ee90e0cb45f975a89c877bc4114de601'),
}
NDK_URL = 'https://dl.google.com/android/repository/android-ndk-r28c-linux.zip'
NDK_SHA256 = 'dfb20d396df28ca02a8c708314b814a4d961dc9074f9a161932746f815aa552f'
WHEELS = {
    'meson-1.11.1-py3-none-any.whl': '9b3a023657e393dbc5335b95c561337d49b7a458f5541e47ec44f2cc566e0d80',
    'pycotap-1.3.1-py3-none-any.whl': '1c3a25b3ff89e48f4e00f1f71dbbc1642b4f65c65d416524d07e73492fff25ea',
    'qemu_qmp-0.0.6-py3-none-any.whl': '5d7c5af0e9de427696e3bf72e333965c3a697929f77f6b7ddc30c989fc7b539b',
}
GIB = 1024 ** 3

# Local research adaptation of QEMU 4fc49f46..., not an upstream change.
# Whole-file hashes are from the independently verified, unmodified archive.
QEMU_PATCH_INPUTS = {
    'meson.build': '7d45b715ca8e740d787eee6d4a1e8ae4a7456aecfe16dda2a7d32a0f2cc10591',
    'util/oslib-posix.c': 'ad7bc820a4ab61fa0b00502a0a04540228a7cc60da5cb8908fcbc2af2419b869',
}
ANDROID_SHM_PROBE = '''#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#if !defined(__ANDROID__) || !defined(__BIONIC__) || !defined(__aarch64__) || __ANDROID_API__ != 30
#error PDVA research requires Android Bionic AArch64 API 30
#endif
int main(void)
{
    int fd = memfd_create("pdva-shm-control", MFD_CLOEXEC);
    void *p;
    if (fd < 0) { return 1; }
    if (fchmod(fd, 0) || ftruncate(fd, 4096) || fcntl(fd, F_GETFD) != FD_CLOEXEC) {
        close(fd);
        return 2;
    }
    p = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (p == MAP_FAILED) { close(fd); return 3; }
    if (munmap(p, 4096)) { close(fd); return 4; }
    return close(fd);
}
'''
ANDROID_SHM_IMPL = '''#if defined(__ANDROID__)
/* PDVA research only: anonymous FD, no pathname or fallback authority. */
#if !defined(__BIONIC__) || !defined(__aarch64__) || __ANDROID_API__ != 30
#error PDVA research requires Android Bionic AArch64 API 30
#endif
int qemu_shm_alloc(size_t size, Error **errp)
{
    int fd = memfd_create("qemu-shm", MFD_CLOEXEC);

    if (fd < 0) {
        error_setg_errno(errp, errno, "failed to create Android shared memfd");
        return -1;
    }
    /* Preserve the original mode-0 restriction on reopening through a path. */
    if (fchmod(fd, 0) == -1) {
        error_setg_errno(errp, errno, "failed to restrict Android shared memfd");
        close(fd);
        return -1;
    }
    if (ftruncate(fd, size) == -1) {
        error_setg_errno(errp, errno,
                         "failed to resize Android shared memfd to %zu", size);
        close(fd);
        return -1;
    }
    return fd;
}
#else
'''
QEMU_RT_ANCHOR = """rt = not_found
if host_os != 'windows'
  have_shm_open = cc.has_function('shm_open')
  if not have_shm_open
    rt = cc.find_library('rt', required: true)
  endif
endif
"""
QEMU_SHM_ANCHOR = 'int qemu_shm_alloc(size_t size, Error **errp)\n{'
# Exact output of the unchanged, hash-checked shared-memory adaptation above.
QEMU_FDT_PATCH_INPUT = '51ac2ab6820b085cce6eaab28adb087885ef12465d81db47ff7899cea117fe6c'
QEMU_FDT_ANCHOR = "  fdt = cc.find_library('fdt', required: fdt_opt == 'system')\n"
FDT_OBJECTS = ('fdt', 'fdt_addresses', 'fdt_check', 'fdt_empty_tree', 'fdt_overlay',
               'fdt_ro', 'fdt_rw', 'fdt_strerror', 'fdt_sw', 'fdt_wip')
FDT_HEADERS = ('libfdt.h', 'libfdt_env.h', 'fdt.h')
ANDROID_FDT_PROBE = '''#include <libfdt.h>
#include <libfdt_env.h>
#if !defined(__ANDROID__) || !defined(__BIONIC__) || !defined(__aarch64__) || __ANDROID_API__ != 30
#error PDVA research requires Android Bionic AArch64 API 30
#endif
int main(void) { fdt_find_max_phandle(NULL, NULL); return 0; }
'''

PCRE2_BUILD_TARGETS = ('libpcre2-8.la', 'libpcre2-posix.la')
PCRE2_INSTALL_TARGETS = ('install-libLTLIBRARIES', 'install-includeHEADERS',
                         'install-nodist_includeHEADERS', 'install-pkgconfigDATA')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(path, expected):
    actual = digest(path)
    if actual != expected:
        raise RuntimeError(f'Hash mismatch: {Path(path).name}: {actual}')
    print(f'VERIFIED {Path(path).name} sha256={actual}', flush=True)


def render_android_patch(sources, target):
    if target != 'aarch64-linux-android30' or set(sources) != set(QEMU_PATCH_INPUTS):
        raise RuntimeError('Unexpected QEMU patch target or file set')
    for name, expected in QEMU_PATCH_INPUTS.items():
        if hashlib.sha256(sources[name]).hexdigest() != expected:
            raise RuntimeError(f'QEMU patch input identity mismatch: {name}')
    meson, oslib = (sources[name].decode('utf-8') for name in QEMU_PATCH_INPUTS)
    if (meson.count(QEMU_RT_ANCHOR) != 1 or oslib.count(QEMU_SHM_ANCHOR) != 1
            or not oslib.endswith('    return fd;\n}\n')):
        raise RuntimeError('QEMU patch anchors mismatch')
    # Compiler identity matters: QEMU configure calls Bionic "linux".
    android_rt = ("rt = not_found\nif cc.get_define('__ANDROID__') != ''\n"
                  "  if not cc.links('''" + ANDROID_SHM_PROBE +
                  "''', name: 'PDVA Android shared memfd')\n"
                  "    error('PDVA Android shared memfd functionality unavailable')\n"
                  "  endif\nelif host_os != 'windows'\n")
    patched = {
        'meson.build': meson.replace(QEMU_RT_ANCHOR, QEMU_RT_ANCHOR.replace(
            "rt = not_found\nif host_os != 'windows'\n", android_rt), 1).encode(),
        'util/oslib-posix.c': (oslib.replace(QEMU_SHM_ANCHOR,
            ANDROID_SHM_IMPL + QEMU_SHM_ANCHOR, 1) + '#endif /* __ANDROID__ */\n').encode(),
    }
    return patched


def apply_android_patch(qemu, emit):
    sources = {}
    for name in QEMU_PATCH_INPUTS:
        path = qemu / name
        if (not stat.S_ISREG(path.lstat().st_mode) or path.is_symlink()
                or any(p.is_symlink() for p in path.parents)):
            raise RuntimeError('Unsafe QEMU patch input')
        sources[name] = path.read_bytes()
    patched = render_android_patch(sources, 'aarch64-linux-android30')
    diff = ''.join(''.join(difflib.unified_diff(
        sources[name].decode().splitlines(keepends=True),
        patched[name].decode().splitlines(keepends=True),
        fromfile='a/' + name, tofile='b/' + name, n=0)) for name in sorted(patched))
    # Validate all input identities before writing either file; duplicate use fails.
    for name, data in patched.items():
        (qemu / name).write_bytes(data)
        verify(qemu / name, hashlib.sha256(data).hexdigest())
        emit(f'PATCH {name} before={QEMU_PATCH_INPUTS[name]} after={digest(qemu / name)}')
    emit('LOCAL RESEARCH PATCH sha256=' + hashlib.sha256(diff.encode()).hexdigest() + '\n' + diff)


def validate_fdt_inspection(members, headers, symbols):
    if members.splitlines() != [name + '.o' for name in FDT_OBJECTS]:
        raise RuntimeError('Unexpected libfdt archive members')
    # Inspect every archive member, not merely one compatible ELF header.
    expected = {'Class': 'ELF64', 'Data': "2's complement, little endian",
                'Type': 'REL (Relocatable file)', 'Machine': 'AArch64'}
    for field, value in expected.items():
        values = re.findall(r'^\s*' + field + r':\s*(.*?)\s*$', headers, re.M)
        if values != [value] * len(FDT_OBJECTS):
            raise RuntimeError('Unexpected libfdt target ABI')
    if len(re.findall(r'^[0-9a-fA-F]+ T fdt_find_max_phandle$', symbols, re.M)) != 1:
        raise RuntimeError('Missing or ambiguous libfdt required symbol')


def verify_fdt_identity(prefix, archive_sha, header_hashes):
    if set(header_hashes) != set(FDT_HEADERS):
        raise RuntimeError('Unexpected libfdt headers')
    artifacts = [(prefix / 'lib/libfdt.a', archive_sha)]
    artifacts += [(prefix / 'include' / name, header_hashes[name]) for name in FDT_HEADERS]
    for path, expected in artifacts:
        if (not stat.S_ISREG(path.lstat().st_mode) or path.is_symlink()
                or any(p.is_symlink() for p in path.parents)):
            raise RuntimeError('Unsafe libfdt artifact')
        verify(path, expected)


def render_android_fdt_patch(source, library_dir, target):
    if target != 'aarch64-linux-android30':
        raise RuntimeError('Unexpected libfdt patch target')
    # Production research paths are absolute POSIX paths without shell/Meson
    # metacharacters. The caller supplies only its own separate target prefix.
    if (not re.fullmatch(r'/(?:[A-Za-z0-9_.-]+/)*target/lib', library_dir)
            or any(part in ('.', '..') for part in library_dir.split('/'))):
        raise RuntimeError('Unexpected libfdt search path')
    if hashlib.sha256(source).hexdigest() != QEMU_FDT_PATCH_INPUT:
        raise RuntimeError('QEMU FDT patch input identity mismatch')
    text = source.decode('utf-8')
    if text.count(QEMU_FDT_ANCHOR) != 1:
        raise RuntimeError('QEMU FDT patch anchor mismatch')
    replacement = ("  if cc.get_define('__ANDROID__') != ''\n"
                   "    fdt = cc.find_library('fdt', dirs: ['" + library_dir +
                   "'], static: true, required: fdt_opt == 'system')\n"
                   "  else\n" + QEMU_FDT_ANCHOR + "  endif\n")
    return text.replace(QEMU_FDT_ANCHOR, replacement, 1).encode()


def apply_android_fdt_patch(qemu, prefix, emit):
    if prefix != qemu.parent.parent / 'target':
        raise RuntimeError('Unexpected libfdt target prefix')
    path = qemu / 'meson.build'
    if (not stat.S_ISREG(path.lstat().st_mode) or path.is_symlink()
            or any(p.is_symlink() for p in path.parents)):
        raise RuntimeError('Unsafe QEMU FDT patch input')
    source = path.read_bytes()
    patched = render_android_fdt_patch(source, (prefix / 'lib').as_posix(),
                                      'aarch64-linux-android30')
    diff = ''.join(difflib.unified_diff(source.decode().splitlines(keepends=True),
                   patched.decode().splitlines(keepends=True), fromfile='a/meson.build',
                   tofile='b/meson.build', n=0))
    path.write_bytes(patched)
    emit(f'FDT PATCH meson.build before={QEMU_FDT_PATCH_INPUT} after={digest(path)}')
    emit('LOCAL FDT RESEARCH PATCH sha256=' + hashlib.sha256(diff.encode()).hexdigest() + '\n' + diff)


def download(url, destination, expected):
    # HTTPS only; bounded bytes and socket timeout; no retry or alternate source.
    if not url.startswith('https://'):
        raise ValueError('HTTPS required')
    with urllib.request.urlopen(url, timeout=60) as response, destination.open('xb') as out:
        if not response.url.startswith('https://'):
            raise ValueError('Insecure redirect')
        total = 0
        while block := response.read(1024 ** 2):
            total += len(block)
            if total > GIB:
                raise RuntimeError('Download exceeds 1 GiB')
            out.write(block)
    verify(destination, expected)


def unpack(archive, destination):
    destination.mkdir()
    with tarfile.open(archive) as source:
        members = source.getmembers()
        if len(members) > 100000 or sum(m.size for m in members) > 2 * GIB:
            raise RuntimeError('Source archive exceeds budget')
        source.extractall(destination, members=members, filter='data')


def git_object_id(kind, data):
    return hashlib.sha1(kind.encode('ascii') + b' ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def source_path(name):
    if (not name or any(ord(c) < 32 for c in name) or '\\' in name or ':' in name
            or any(part in ('', '.', '..') or part.lower() == '.git' for part in name.split('/'))):
        raise RuntimeError('Unsafe source path')
    return PurePosixPath(name)


def source_link(name, data):
    link = data.decode('utf-8')
    # Symlinks may use .. only while staying inside this source root. Never
    # follow links while writing files; reject file/link ancestor conflicts too.
    if (not link or link.startswith('/') or '\\' in link or ':' in link
            or any(ord(c) < 32 for c in link)):
        raise RuntimeError('Unsafe source symlink')
    parts = list(source_path(name).parent.parts)
    for part in link.split('/'):
        if part == '..':
            if not parts:
                raise RuntimeError('Escaping source symlink')
            parts.pop()
        elif part not in ('', '.'):
            if part.lower() == '.git':
                raise RuntimeError('Unsafe source symlink')
            parts.append(part)
    return link


def git_source_manifest(repository, revision, tree, env):
    """Trust anchors are reviewed pins, never freshly computed expected hashes."""
    if not all(re.fullmatch(r'[0-9a-f]{40}', oid) for oid in (revision, tree)):
        raise RuntimeError('Immutable Git pins required')
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repository), *args], env=env,
                                       stderr=subprocess.PIPE, timeout=60)
    # fsck verifies recursive object hashes/structure, including nested trees.
    git('fsck', '--strict', '--no-reflogs', '--no-dangling')
    commit = git('cat-file', 'commit', revision)
    if git_object_id('commit', commit) != revision or commit.splitlines()[0] != b'tree ' + tree.encode():
        raise RuntimeError('Commit/tree identity mismatch')
    if git_object_id('tree', git('cat-file', 'tree', tree)) != tree:
        raise RuntimeError('Tree object mismatch')
    manifest = {}
    for entry in git('ls-tree', '-rz', '--full-tree', tree).split(b'\0'):
        if not entry:
            continue
        metadata, path = entry.split(b'\t', 1)
        mode, kind, oid = metadata.decode('ascii').split()
        name = path.decode('utf-8')
        source_path(name)
        if mode not in ('100644', '100755', '120000') or kind != 'blob' or name in manifest:
            raise RuntimeError('Unsupported or duplicate Git source entry')
        manifest[name] = (mode, oid)
    if not manifest or len(manifest) > 100000:
        raise RuntimeError('Source entry budget exceeded')
    for name in manifest:
        if any(parent.as_posix() in manifest for parent in source_path(name).parents):
            raise RuntimeError('Source file/link ancestor conflict')
    return manifest


def verify_source_tree(destination, manifest):
    """Compare every materialized leaf and directory; never follow a symlink."""
    expected_dirs = {p.as_posix() for name in manifest for p in source_path(name).parents
                     if p.as_posix() != '.'}
    seen, directories = set(), set()
    for base, dirs, files in os.walk(destination, followlinks=False):
        for name in dirs[:]:
            path = Path(base) / name
            if path.is_symlink():
                dirs.remove(name)
                files.append(name)
            else:
                directories.add(path.relative_to(destination).as_posix())
        for name in files:
            path = Path(base) / name
            relative = path.relative_to(destination).as_posix()
            if relative not in manifest:
                raise RuntimeError('Extra source file')
            mode, oid = manifest[relative]
            info = path.lstat()
            if mode == '120000':
                if not stat.S_ISLNK(info.st_mode):
                    raise RuntimeError('Source symlink type mismatch')
                data = os.readlink(path).encode('utf-8')
                source_link(relative, data)
                if not path.resolve().is_relative_to(destination.resolve()):
                    raise RuntimeError('Escaping source symlink chain')
            else:
                if not stat.S_ISREG(info.st_mode):
                    raise RuntimeError('Source file type mismatch')
                if info.st_size > 128 * 1024 ** 2:
                    raise RuntimeError('Source blob budget exceeded')
                data = path.read_bytes()
                # Windows cannot represent POSIX executable mode. Production
                # main() requires Linux; its filesystem-mode check is mandatory.
                if os.name != 'nt' and stat.S_IMODE(info.st_mode) != int(mode[-3:], 8):
                    raise RuntimeError('Source file mode mismatch')
            if git_object_id('blob', data) != oid:
                raise RuntimeError('Source blob mismatch')
            seen.add(relative)
    if seen != set(manifest) or directories != expected_dirs:
        raise RuntimeError('Missing source or unexpected directory')


def materialize_git_source(repository, revision, tree, destination, env):
    manifest = git_source_manifest(repository, revision, tree, env)
    names = list(manifest)
    request = ''.join(manifest[name][1] + '\n' for name in names).encode('ascii')
    command = ['git', '-C', str(repository), 'cat-file']
    # Bound sizes before asking Git for contents. Binary stdout goes to a
    # temporary file, never through text decoding/newline conversion or logs.
    sizes = subprocess.check_output(command + ['--batch-check'], input=request,
                                    env=env, stderr=subprocess.PIPE, timeout=60).splitlines()
    total = 0
    if len(sizes) != len(names):
        raise RuntimeError('Missing Git blob metadata')
    for name, record in zip(names, sizes):
        oid, kind, size = record.decode('ascii').split()
        count = int(size)
        if oid != manifest[name][1] or kind != 'blob' or not 0 <= count <= 128 * 1024 ** 2:
            raise RuntimeError('Invalid Git blob metadata')
        total += count
    if total > 2 * GIB:
        raise RuntimeError('Source byte budget exceeded')
    destination.mkdir()
    links = []
    with tempfile.TemporaryFile(dir=destination.parent) as blobs:
        subprocess.run(command + ['--batch'], input=request, stdout=blobs,
                       stderr=subprocess.PIPE, env=env, timeout=90, check=True)
        if blobs.tell() != total + sum(len(row) + 2 for row in sizes):
            raise RuntimeError('Unexpected Git blob stream length')
        blobs.seek(0)
        for name, record in zip(names, sizes):
            if blobs.readline(256).rstrip(b'\n') != record:
                raise RuntimeError('Substituted Git blob header')
            count = int(record.split()[2])
            data = blobs.read(count)
            mode, oid = manifest[name]
            if len(data) != count or blobs.read(1) != b'\n' or git_object_id('blob', data) != oid:
                raise RuntimeError('Corrupt Git blob')
            path = destination.joinpath(*source_path(name).parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            if mode == '120000':
                links.append((path, source_link(name, data)))
            else:
                with path.open('xb') as output:
                    output.write(data)
                path.chmod(int(mode[-3:], 8))
    for path, link in links:
        path.symlink_to(link)
    verify_source_tree(destination, manifest)
    print(f'VERIFIED Git commit={revision} tree={tree} files={len(manifest)} bytes={total}', flush=True)


def regular_archive_manifest(archive, expected, top):
    """The reviewed GLib fallback archives contain only directories and files."""
    verify(archive, expected)
    if len(source_path(top).parts) != 1:
        raise RuntimeError('Unexpected archive root')
    manifest, directories, seen = {}, set(), set()
    with tarfile.open(archive) as source:
        members = source.getmembers()
        if len(members) > 100000 or sum(m.size for m in members) > 2 * GIB:
            raise RuntimeError('Source archive exceeds budget')
        for member in members:
            path = source_path(member.name.rstrip('/'))
            if path.parts[0] != top or path in seen:
                raise RuntimeError('Unexpected or duplicate archive path')
            seen.add(path)
            name = PurePosixPath(*path.parts[1:]).as_posix()
            if member.isdir():
                directories.add(name)
            elif (member.isfile() and name != '.' and 0 <= member.size <= 128 * 1024 ** 2
                  and member.mode in (0o644, 0o664, 0o755, 0o775)):
                data = source.extractfile(member).read()
                if len(data) != member.size:
                    raise RuntimeError('Truncated archive source')
                # Same safe regular-file modes as tarfile's data filter.
                mode = '100755' if member.mode & 0o100 else '100644'
                manifest[name] = (mode, git_object_id('blob', data))
            else:
                raise RuntimeError('Unexpected archive entry type or mode')
    expected_dirs = {p.as_posix() for name in manifest for p in source_path(name).parents}
    if not manifest or directories != expected_dirs or set(manifest) & directories:
        raise RuntimeError('Unexpected archive directory layout')
    return manifest


def materialize_glib_subproject(name, archive, source, glib):
    # Identities observed in the exact hash-pinned GLib archive, not permissive
    # alternatives: gvdb is an empty gitlink placeholder, proxy is absent.
    locations = {'gvdb': ('gvdb', 'empty'), 'proxy': ('proxy-libintl-0.5', 'absent')}
    relative, expected_state = locations[name]
    parent = glib / 'subprojects'
    destination = parent / relative
    # Reject symlink ancestors as well as destination links before any writes.
    for directory in (source, glib, parent):
        for component in (directory, *directory.parents):
            if not stat.S_ISDIR(component.lstat().st_mode):
                raise RuntimeError('Source/destination ancestor is not a real directory')

    def check_destination():
        if expected_state == 'absent':
            if os.path.lexists(destination):
                raise RuntimeError('Expected absent GLib subproject destination')
        elif (not stat.S_ISDIR(destination.lstat().st_mode)
              or any(destination.iterdir())):
            raise RuntimeError('Expected empty real GLib subproject directory')

    check_destination()
    _, sha, top = ARCHIVES[name]
    manifest = regular_archive_manifest(archive, sha, top)
    verify_source_tree(source, manifest)
    # Stage and verify without merging/overwriting. Only rmdir of the checked
    # empty placeholder is allowed; never recursively remove a destination.
    with tempfile.TemporaryDirectory(prefix='.pdva-source-', dir=parent) as staging:
        staged = Path(staging) / relative
        shutil.copytree(source, staged, symlinks=True)
        verify_source_tree(staged, manifest)
        check_destination()
        if expected_state == 'empty':
            destination.rmdir()
        staged.rename(destination)
    verify_source_tree(destination, manifest)
    print(f'VERIFIED GLib subproject={relative} initial={expected_state} files={len(manifest)}', flush=True)


def verify_host_ninja(path, expected_sha=None):
    # Inspect before execution: this research host is Linux x86-64, not Android.
    if (not path.is_absolute() or not path.is_file() or path.is_symlink()
            or not os.access(path, os.X_OK)):
        raise RuntimeError('Ninja must be an available absolute host executable')
    with path.open('rb') as stream:
        header = stream.read(64)
        if (len(header) != 64 or header[:7] != b'\x7fELF\x02\x01\x01'
                or struct.unpack_from('<HHI', header, 16) not in ((2, 62, 1), (3, 62, 1))):
            raise RuntimeError('Ninja must be Linux x86-64 ELF64')
        offset = struct.unpack_from('<Q', header, 32)[0]
        entry_size, count = struct.unpack_from('<HH', header, 54)
        file_size = os.fstat(stream.fileno()).st_size
        if (entry_size != 56 or not 1 <= count <= 128
                or offset < 64 or offset + entry_size * count > file_size):
            raise RuntimeError('Invalid Ninja ELF program headers')
        interpreters = []
        for index in range(count):
            stream.seek(offset + index * entry_size)
            entry = stream.read(entry_size)
            if len(entry) != entry_size:
                raise RuntimeError('Truncated Ninja ELF program headers')
            if struct.unpack_from('<I', entry)[0] == 3:  # PT_INTERP
                start, size = struct.unpack_from('<Q', entry, 8)[0], struct.unpack_from('<Q', entry, 32)[0]
                if not 1 <= size <= 256 or start + size > file_size:
                    raise RuntimeError('Invalid Ninja host interpreter')
                stream.seek(start)
                interpreters.append(stream.read(size))
        # Require the Ubuntu host-loader ABI; never execute an Android loader.
        if interpreters not in ([b'/lib64/ld-linux-x86-64.so.2\0'],
                                [b'/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2\0']):
            raise RuntimeError('Unexpected Ninja host interpreter (target or unreviewed executable)')
    actual = digest(path)
    if expected_sha is not None and actual != expected_sha:
        raise RuntimeError('Selected Ninja executable changed')
    return actual


def select_host_ninja(env, run, emit):
    search = env.get('PATH', '')
    if not search or any(not Path(part).is_absolute() for part in search.split(os.pathsep)):
        raise RuntimeError('Ninja discovery requires an absolute host PATH')
    specified = env.get('NINJA')
    if specified is not None and (not specified or not Path(specified).is_absolute()):
        raise RuntimeError('NINJA override must be an absolute executable path')
    selected = specified if specified is not None else shutil.which('ninja', path=search)
    if not selected:
        raise RuntimeError('Host Ninja not found; no fallback or installation')
    path = Path(selected).resolve(strict=True)
    sha = verify_host_ninja(path)
    output = run(path, '--version', env=env, timeout=30, show=True).strip()
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', output):
        raise RuntimeError('Unexpected Ninja version output')
    if tuple(map(int, output.split('.'))) < (1, 8, 2):
        raise RuntimeError('Ninja version must be >= 1.8.2')
    verify_host_ninja(path, sha)
    emit(f'HOST NINJA selected={selected} resolved={path} version={output} sha256={sha}; '
         'executable ELF64 x86-64 with Ubuntu host loader; minimum=1.8.2')
    return path, sha


def inspect_android_elf(data, mode):
    """Bounded structural inspection, not runtime or static-startup acceptance."""
    def require(condition, message):
        if not condition:
            raise RuntimeError('ELF: ' + message)

    def block(offset, size):
        require(0 <= offset <= len(data) and 0 <= size <= len(data) - offset, 'truncated/out-of-range data')
        return data[offset:offset + size]

    def unpack(fmt, offset):
        return struct.unpack(fmt, block(offset, struct.calcsize(fmt)))

    def string(table, index):
        require(0 <= index < len(table), 'invalid string index')
        end = table.find(b'\0', index)
        require(end >= index, 'unterminated string')
        return table[index:end].decode('ascii', errors='strict')

    require(mode in ('dynamic', 'static'), 'unknown requested mode')
    require(64 <= len(data) <= 256 * 1024 * 1024, 'file size outside inspection bound')
    h = unpack('<16sHHIQQQIHHHHHH', 0)
    require(h[0][:9] == b'\x7fELF\x02\x01\x01\0\0' and h[1:4] == (3, 183, 1),
            'expected little-endian Android AArch64 ELF64 ET_DYN')
    require(h[8:10] == (64, 56) and 1 <= h[10] <= 128, 'invalid program header table')
    require(h[11] == 64 and 1 <= h[12] <= 4096 and h[13] < h[12], 'missing/invalid section table')
    require(h[5] >= 64 and h[6] >= 64, 'header tables overlap ELF header')
    ph = [unpack('<IIQQQQQQ', h[5] + i * 56) for i in range(h[10])]
    sh = [unpack('<IIQQQQIIQQ', h[6] + i * 64) for i in range(h[12])]
    for p in ph:
        block(p[2], p[5])
        require(p[5] <= p[6], 'segment file size exceeds memory size')
    for s in sh:
        if s[1] != 8:  # SHT_NOBITS has no file contents.
            block(s[4], s[5])
    names = block(sh[h[13]][4], sh[h[13]][5])
    sections = {string(names, s[0]): s for s in sh}
    require(len(sections) == len(sh), 'duplicate section names')
    loads = [p for p in ph if p[0] == 1]
    require(len(loads) >= 2, 'missing LOAD segments')
    for p in loads:
        require(p[1] & 7 == p[1] and p[1] & 3 != 3, 'writable/executable or invalid LOAD flags')
        require(p[7] >= 16384 and p[7] & (p[7] - 1) == 0 and p[2] % p[7] == p[3] % p[7],
                'invalid 16 KiB LOAD alignment/congruence')
    ordered = sorted(loads, key=lambda p: p[3])
    require(all(a[3] + a[6] <= b[3] for a, b in zip(ordered, ordered[1:])), 'overlapping LOAD segments')

    def mapped(address, size, flag=0, file_backed=False):
        return [p for p in loads if p[1] & flag == flag and p[3] <= address
                and address + size <= p[3] + (p[5] if file_backed else p[6])]

    for s in sh:
        if s[2] & 2 and s[5]:
            parents = mapped(s[3], s[5], file_backed=s[1] != 8)
            require(len(parents) == 1, 'allocated section outside LOAD')
            if s[1] != 8:
                require(s[4] == parents[0][2] + s[3] - parents[0][3], 'section/LOAD offset mismatch')
    require(h[4] > 0 and len(mapped(h[4], 4, 1, True)) == 1, 'entrypoint outside executable file-backed LOAD')
    stack = [p for p in ph if p[0] == 0x6474e551]
    require(len(stack) == 1 and stack[0][1] & 1 == 0, 'missing or executable GNU_STACK')
    relro = [p for p in ph if p[0] == 0x6474e552]
    require(len(relro) == 1 and relro[0][6] > 0 and mapped(relro[0][3], relro[0][6], 2), 'invalid GNU_RELRO')
    dynamic = [p for p in ph if p[0] == 2]
    require(len(dynamic) == 1 and dynamic[0][5] % 16 == 0, 'invalid PT_DYNAMIC')
    dp = dynamic[0]
    ds = sections.get('.dynamic')
    require(ds is not None and ds[1] == 6 and (ds[3], ds[4], ds[5]) == (dp[3], dp[2], dp[5]),
            'section/PT_DYNAMIC mismatch')
    require(relro[0][3] <= dp[3] and dp[3] + dp[6] <= relro[0][3] + relro[0][6], 'dynamic table outside RELRO')
    tags = {}
    terminated = False
    for offset in range(dp[2], dp[2] + dp[5], 16):
        tag, value = unpack('<qQ', offset)
        if tag == 0:
            terminated = True
            break
        require(tag == 1 or tag not in tags, 'duplicate dynamic tag')
        tags.setdefault(tag, []).append(value)
    require(terminated, 'unterminated dynamic table')
    get = lambda tag, default=0: tags.get(tag, [default])[0]
    require(not {14, 15, 22, 29}.intersection(tags) and get(30) & 4 == 0, 'SONAME/RPATH/RUNPATH/TEXTREL forbidden')
    require(get(0x6ffffffb) & 0x08000000, 'missing DF_1_PIE executable flag')
    require(24 in tags or get(30) & 8 or get(0x6ffffffb) & 1, 'missing bind-now')
    dynstr = sections.get('.dynstr')
    require(dynstr is not None and get(5) == dynstr[3] and get(10) == dynstr[5], 'dynamic string table mismatch')
    strings = block(dynstr[4], dynstr[5])
    needed = [string(strings, index) for index in tags.get(1, [])]
    interp = [block(p[2], p[5]) for p in ph if p[0] == 3]
    if mode == 'dynamic':
        require(interp == [b'/system/bin/linker64\0'], 'dynamic PIE requires Android interpreter')
        require(needed and set(needed) <= {'libc.so', 'libdl.so', 'libm.so', 'libz.so', 'liblog.so'},
                'unexpected or empty dynamic dependencies')
    else:
        require(not interp and not needed, 'static PIE must have no interpreter or dependencies')

    notes = []
    for s in sh:
        if s[1] != 7:
            continue
        pos, end = s[4], s[4] + s[5]
        while pos < end:
            require(pos + 12 <= end, 'truncated note')
            nsize, dsize, kind = unpack('<III', pos)
            start = pos + 12
            desc = start + ((nsize + 3) & ~3)
            pos = desc + ((dsize + 3) & ~3)
            require(pos <= end, 'note exceeds section')
            if block(start, nsize) == b'Android\0' and kind == 1:
                notes.append(block(desc, dsize))
    require(len(notes) == 1 and len(notes[0]) == 132, 'missing/ambiguous Android identification note')
    note = notes[0]
    require(struct.unpack_from('<I', note)[0] == 30 and note[4:68].split(b'\0')[0] == b'r28c'
            and note[68:].split(b'\0')[0] == b'13676358', 'wrong Android API/NDK identity')

    symbols, undefined = {}, []
    require(sum(s[1] == 11 for s in sh) == 1 and sum(s[1] == 2 for s in sh) == 1,
            'missing/ambiguous dynamic or static symbol table')
    for s in sh:
        if s[1] == 3:
            require(b'GLIBC_' not in block(s[4], s[5]), 'glibc symbol-version contamination')
        if s[1] not in (2, 11):
            continue
        require(s[9] == 24 and s[5] % 24 == 0 and s[6] < len(sh), 'invalid symbol table')
        st = sh[s[6]]
        require(st[1] == 3, 'invalid symbol string table')
        strings = block(st[4], st[5])
        if s[1] == 11:
            require(get(6) == s[3] and get(11) == 24, 'dynamic symbol table mismatch')
            if mode == 'static':
                require(s[5] == 24 and block(s[4], 24) == bytes(24), 'static PIE has dynamic symbols')
        for offset in range(s[4], s[4] + s[5], 24):
            name, info, other, index, value, size = unpack('<IBBHQQ', offset)
            name = string(strings, name)
            if index and name:
                symbols[name] = (value, size, info & 15)
            elif name and s[1] == 2:
                undefined.append((name, info >> 4))
    require('_start' in symbols and symbols['_start'][0] == h[4] and symbols['_start'][2] == 2,
            'missing executable _start at entrypoint')

    relocations = {}
    if mode == 'static':
        require(not {17, 18, 19, 23, 35, 36, 37, 0x6000000f, 0x60000010, 0x60000011, 0x60000012}.intersection(tags),
                'unsupported static REL/PLT/packed relocation encoding')
        rela = sections.get('.rela.dyn')
        require(rela is not None and rela[1] == 4 and rela[9] == 24 and rela[5] > 0 and rela[5] % 24 == 0
                and get(7) == rela[3] and get(8) == rela[5] and get(9) == 24, 'missing/mismatched static RELA table')
        require(get(0x6ffffff9) == rela[5] // 24, 'static RELACOUNT mismatch')
        require(all(s[1] not in (4, 9, 19) or not s[2] & 2 or s == rela for s in sh), 'unexpected allocated relocation table')
        targets = set()
        for offset in range(rela[4], rela[4] + rela[5], 24):
            target, info, addend = unpack('<QQq', offset)
            require(info == 1027, 'unsupported static relocation (requires reviewed R_AARCH64_RELATIVE)')
            require(target % 8 == 0 and len(mapped(target, 8, 2)) == 1 and target not in targets,
                    'invalid/duplicate relocation target')
            require(addend >= 0 and mapped(addend, 1), 'relative relocation addend outside image')
            targets.add(target)
        relocations['R_AARCH64_RELATIVE'] = len(targets)
        require('__libc_init' in symbols and symbols['__libc_init'][2] == 2
                and mapped(symbols['__libc_init'][0], 4, 1, True), 'missing Bionic static startup symbol')
        allowed_local = {'__rela_iplt_start', '__rela_iplt_end'}
        require(all(bind == 2 or name in allowed_local and bind == 0 for name, bind in undefined),
                'unresolved non-weak static symbol')
    return {'mode': mode, 'classification': mode + ' Android PIE candidate', 'entry': hex(h[4]),
            'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'needed': needed,
            'load_segments': len(loads), 'relocations': relocations, 'android_api': 30,
            'ndk': 'r28c/13676358', 'undefined_static_symbols': undefined[:32] if mode == 'static' else [],
            'static_startup_accepted': False}


def require_static_startup(report, evidence):
    if (report.get('mode') != 'static' or evidence.get('binary_sha256') != report['sha256'] or evidence.get('mode') != 'static'
            or not evidence.get('crtbegin') or not evidence.get('libc_static_init')):
        raise RuntimeError('Static PIE startup evidence missing or does not match output/mode')
    # No supported self-relocating startup has been established for this exact
    # NDK route. An ELF shape, Android note, flag or caller boolean cannot waive it.
    raise RuntimeError('Unsupported Android static PIE startup: NDK r28c selects crtbegin_dynamic.o; '
                       'Bionic self-relocation and load-bias-aware RELRO are not established. '
                       'Candidate linked; executable acceptance FAILED; NOT EXECUTED')


def qemu_link_evidence(binary, build, toolbin, commands_log, compile_log, emit):
    """Capture real Ninja/driver/map evidence before ELF acceptance can fail."""
    def read_bounded(path, limit):
        if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
            raise RuntimeError('Missing/unsafe/oversized link evidence: ' + path.name)
        return path.read_text(encoding='utf-8', errors='strict')

    def output_path(args):
        if args.count('-o') != 1:
            return None
        index = args.index('-o')
        if index + 1 == len(args):
            return None
        return (build / args[index + 1]).resolve()

    commands = read_bounded(commands_log, 32 * 1024 * 1024).splitlines()
    drivers = read_bounded(compile_log, 32 * 1024 * 1024).splitlines()
    final = []
    for line in commands:
        args = shlex.split(line)
        if output_path(args) == binary.resolve():
            final.append((line, args))
    if len(final) != 1:
        raise RuntimeError('Missing/ambiguous generated QEMU final link command')
    line, args = final[0]
    if (len(line) > 60000 or any(a.startswith('@') or a in ('&&', ';', '|') for a in args)
            or Path(args[0]).resolve() not in { (toolbin / ('aarch64-linux-android30-clang' + suffix)).resolve()
                                               for suffix in ('', '++') }
            or args.count('-static-pie') != 1 or any(a in args for a in ('-shared', '-static', '-no-pie'))):
        raise RuntimeError('Unsupported/ambiguous QEMU link command or target/mode mismatch')
    emit('ACTUAL NINJA FINAL LINK\n' + line)
    compiler_sha = digest(Path(args[0]))
    linker = []
    for line in drivers:
        # Only the verbose Clang driver linker invocation; build progress is not shell code.
        if 'ld.lld' not in line:
            continue
        args = shlex.split(line)
        if args and Path(args[0]).resolve() == (toolbin / 'ld.lld').resolve() and output_path(args) == binary.resolve():
            linker.append((line, args))
    if len(linker) != 1 or len(linker[0][0]) > 60000:
        raise RuntimeError('Missing/ambiguous/bounded-out actual NDK linker invocation')
    line, args = linker[0]
    emit('ACTUAL NDK LINKER\n' + line)
    if not {'-static', '-pie', '--no-dynamic-linker'}.issubset(args) or '-shared' in args:
        raise RuntimeError('Actual linker mode disagrees with static PIE request')
    sysroot = toolbin.parent / 'sysroot/usr/lib/aarch64-linux-android'
    crt = {}
    for name in ('crtbegin_dynamic.o', 'crtend_android.o'):
        expected = (sysroot / '30' / name).resolve()
        found = [a for a in args if Path(a).name == name]
        if len(found) != 1 or Path(found[0]).resolve() != expected:
            raise RuntimeError('Missing/substituted Android API-30 CRT input')
        crt[name] = digest(expected)
    mapfile = build / 'qemu.map'
    maptext = read_bounded(mapfile, 64 * 1024 * 1024)
    inputs = sorted(set(re.findall(r'^\s*[0-9a-f]+\s+[0-9a-f]+\s+[0-9a-f]+\s+\d+\s+(.+):\(', maptext, re.M)))
    libc = sysroot / 'libc.a'
    # Resolve only actual map paths; a symbol or substring cannot supply CRT provenance.
    static_init = any(item.endswith('(libc_init_static.o)') and
                      Path(item.split('(', 1)[0]).resolve() == libc.resolve() for item in inputs)
    if not inputs or not static_init:
        raise RuntimeError('No exact NDK libc.a static startup input in link map')
    records = {}
    for item in inputs:
        source = (build / item.split('(', 1)[0]).resolve()
        if source.suffix in ('.a', '.o') and source.is_file() and str(source) not in records:
            if not source.is_relative_to(build.parent):
                raise RuntimeError('Link input outside verified research tree')
            records[str(source)] = {'size': source.stat().st_size, 'sha256': digest(source)}
    evidence = {'mode': 'static', 'binary_sha256': digest(binary), 'size': binary.stat().st_size,
                'compiler_sha256': compiler_sha, 'linker_sha256': digest(toolbin / 'ld.lld'),
                'verified_ndk_archive_sha256': NDK_SHA256,
                'crtbegin': crt, 'libc_static_init': static_init, 'libc_sha256': digest(libc),
                'commands_sha256': digest(commands_log), 'compile_log_sha256': digest(compile_log),
                'map_sha256': digest(mapfile), 'map_input_count': len(inputs)}
    emit('LINK EVIDENCE ' + json.dumps(evidence, sort_keys=True))
    emit('ACTUAL MAP INPUTS (bounded display; complete map identified above)\n' + '\n'.join(inputs))
    emit('LINK INPUT IDENTITIES ' + json.dumps(records, sort_keys=True))
    return evidence


def tree_size(root):
    return sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink())


class Research:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix='pdva-qemu-', dir=os.environ.get('RUNNER_TEMP'))).resolve()
        checkout = Path(__file__).resolve().parents[2]
        if self.root.is_relative_to(checkout) or any(c in str(self.root) for c in ' :\n\r'):
            raise RuntimeError('Research requires a separate path without whitespace or colons')
        self.logs = self.root / 'logs'
        self.logs.mkdir()
        self.stage = 'host preflight'
        self.sequence = 0
        self.host_ninja = None
        self.ninja_sha = None
        self.env = {key: os.environ[key] for key in ('PATH', 'HOME', 'TMPDIR') if key in os.environ}
        self.env.update(LC_ALL='C.UTF-8', LANG='C.UTF-8', TZ='UTC',
                        PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1',
                        PYTHONNOUSERSITE='1', GIT_TERMINAL_PROMPT='0',
                        GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', GIT_NO_REPLACE_OBJECTS='1',
                        PKG_CONFIG_PATH='', PKG_CONFIG_DIR='')

    def emit(self, value):
        value = str(value).replace(str(self.root), '$RESEARCH')
        value = value.replace(str(Path.home()), '$HOME')
        if len(value) > 65536:
            sha = hashlib.sha256(value.encode()).hexdigest()
            value = value[:64000] + f'\n[bounded display; full sanitized text chars={len(value)} sha256={sha}]'
        print(value, flush=True)

    def run(self, *args, cwd=None, env=None, timeout=900, show=False):
        env = self.env if env is None else env
        if self.host_ninja is not None:
            if env.get('NINJA') != str(self.host_ninja):
                raise RuntimeError('Selected Ninja environment changed')
            verify_host_ninja(self.host_ninja, self.ninja_sha)
        self.sequence += 1
        self.emit(f'RUN [{self.stage}] ' + shlex.join(map(str, args)))
        log = self.logs / f'{self.sequence:03d}.log'
        with log.open('wb') as output:
            process = subprocess.Popen(list(map(str, args)), cwd=cwd or self.root,
                                       env=env, stdout=output,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            started = time.monotonic()
            try:
                while process.poll() is None:
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        if time.monotonic() - started > timeout:
                            raise RuntimeError('Command deadline exceeded')
                        if tree_size(self.root) > 8 * GIB:
                            raise RuntimeError('Research storage exceeds 8 GiB')
            except BaseException:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                raise
        with log.open('rb') as stream:
            stream.seek(max(0, log.stat().st_size - 100000))
            text = stream.read().decode('utf-8', errors='replace')
        if show or process.returncode:
            self.emit(text)
        if process.returncode:
            raise RuntimeError(f'Command exit {process.returncode}; dependent stages NOT RUN')
        return text

    def phase(self, name):
        self.stage = name
        self.emit(f'STAGE {name}')
        if tree_size(self.root) > 8 * GIB:
            raise RuntimeError('Research storage exceeds 8 GiB')

    def build(self):
        self.emit(f'Linux research only; Python {platform.python_version()}')
        for name in ('ImageOS', 'ImageVersion'):
            self.emit(f'{name}={os.environ.get(name, "Unknown")}')
        self.emit(Path('/etc/os-release').read_text())
        for command in (['git', '--version'], ['cc', '--version'], ['make', '--version'],
                        ['pkg-config', '--version']):
            self.run(*command, show=True)
        self.run('sh', '-c', 'command -v ninja', show=True)
        legacy_ninja = Path('/usr/bin/ninja')
        self.emit(f'NINJA legacy /usr/bin/ninja exists={legacy_ninja.exists()} '
                  f'executable={os.access(legacy_ninja, os.X_OK)}; not selected by assumption')
        self.host_ninja, self.ninja_sha = select_host_ninja(self.env, self.run, self.emit)
        self.env['NINJA'] = str(self.host_ninja)
        self.run(sys.executable, '-c',
                 'import setuptools, wheel, pip; print(setuptools.__version__, wheel.__version__, pip.__version__)', show=True)
        self.phase('verified source acquisition')
        sources = {}
        for name, (url, sha, directory) in ARCHIVES.items():
            archive = self.root / (name + '.archive')
            download(url, archive, sha)
            destination = self.root / (name + '-source')
            unpack(archive, destination)
            sources[name] = destination / directory
        qemu, glib = sources['qemu'], sources['glib']
        for name, (revision, tree) in GIT_INPUTS.items():
            repository = self.root / (name + '-git')
            self.run('git', 'init', '--quiet', repository)
            self.run('git', '-C', repository, '-c', 'protocol.file.allow=never', 'fetch',
                     '--depth=1', '--no-tags', f'https://gitlab.com/qemu-project/{name}.git', revision, timeout=180)
            destination = qemu / 'subprojects' / name
            materialize_git_source(repository, revision, tree, destination, self.env)
            # QEMU's reviewed packagefiles are the wrap overlays, not new patches.
            overlay = qemu / 'subprojects/packagefiles' / name
            if overlay.exists():
                shutil.copytree(overlay, destination, dirs_exist_ok=True)
        for name in ('gvdb', 'proxy'):
            materialize_glib_subproject(name, self.root / (name + '.archive'), sources[name], glib)
        for name, sha in WHEELS.items():
            verify(qemu / 'python/wheels' / name, sha)
        self.phase('reviewed Android shared-memory adaptation')
        apply_android_patch(qemu, self.emit)
        self.phase('declared Kconfig closure control')
        (qemu / 'configs/devices/aarch64-softmmu/pdva.mak').write_text('CONFIG_ARM_VIRT=y\n')
        closure = self.run(sys.executable, 'scripts/minikconf.py', '--allnoconfig',
                           self.root / 'virt-config.mak', self.root / 'virt-config.d',
                           'configs/devices/aarch64-softmmu/pdva.mak', 'Kconfig',
                           'CONFIG_TCG=y', 'CONFIG_FDT=y', 'CONFIG_LINUX=y',
                           'CONFIG_AARCH64=y', 'CONFIG_ARM=y', 'CONFIG_TARGET_BIG_ENDIAN=n',
                           cwd=qemu, show=True)
        self.emit(f'DECLARED closure symbols={closure.count("=y")}; compare PR #5 count 41; not compiled inventory')
        self.phase('verified Linux NDK acquisition')
        archive = self.root / 'ndk.zip'
        download(NDK_URL, archive, NDK_SHA256)
        with zipfile.ZipFile(archive) as source:
            entries = source.infolist()
            if sum(e.file_size for e in entries) > 4 * GIB:
                raise RuntimeError('NDK exceeds extraction budget')
            links = []
            for entry in entries:
                target = (self.root / entry.filename).resolve()
                if not target.is_relative_to(self.root) or not entry.filename.startswith('android-ndk-r28c/'):
                    raise RuntimeError('Unsafe NDK archive path')
                if stat.S_ISLNK(entry.external_attr >> 16):
                    link = source.read(entry).decode('utf-8')
                    if not (target.parent / link).resolve().is_relative_to(self.root / 'android-ndk-r28c'):
                        raise RuntimeError('Unsafe NDK symlink')
                    links.append((target, link))
                    continue
                source.extract(entry, self.root)
                if not entry.is_dir():
                    target.chmod((entry.external_attr >> 16) & 0o777)
            link_paths = {target for target, _ in links}
            if any(parent in link_paths for target, _ in links for parent in target.parents):
                raise RuntimeError('NDK symlink ancestor conflict')
            for target, link in links:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(link)
            for target, _ in links:
                if not target.resolve().is_relative_to(self.root / 'android-ndk-r28c'):
                    raise RuntimeError('Unsafe NDK symlink chain')
        ndk = self.root / 'android-ndk-r28c'
        properties = (ndk / 'source.properties').read_text()
        if '28.2.13676358' not in properties:
            raise RuntimeError('Unexpected NDK revision')
        self.emit(properties)
        toolbin = ndk / 'toolchains/llvm/prebuilt/linux-x86_64/bin'
        cc, cxx = toolbin / 'aarch64-linux-android30-clang', toolbin / 'aarch64-linux-android30-clang++'
        self.run(cc, '--version', show=True)
        prefix = self.root / 'target'
        prefix.mkdir()
        (prefix / 'lib/pkgconfig').mkdir(parents=True)
        (prefix / 'include').mkdir()
        target_env = self.env | {
            'CC': str(cc), 'CXX': str(cxx), 'AR': str(toolbin / 'llvm-ar'),
            'RANLIB': str(toolbin / 'llvm-ranlib'), 'NM': str(toolbin / 'llvm-nm'),
            'STRIP': str(toolbin / 'llvm-strip'), 'READELF': str(toolbin / 'llvm-readelf'),
            'LD': str(toolbin / 'ld.lld'), 'OBJCOPY': str(toolbin / 'llvm-objcopy'),
            'CFLAGS': '-O2 -fPIC -fstack-protector-strong -D_FORTIFY_SOURCE=2',
            'CXXFLAGS': '-O2 -fPIC -fstack-protector-strong -D_FORTIFY_SOURCE=2',
            'LDFLAGS': '-Wl,-z,relro,-z,now,-z,max-page-size=16384',
            'PKG_CONFIG_LIBDIR': str(prefix / 'lib/pkgconfig'), 'PKG_CONFIG_SYSROOT_DIR': '',
        }
        self.phase('NDK positive link control')
        probe = self.root / 'control.c'
        probe.write_text('#include <zlib.h>\n#include <iconv.h>\nint main(void) { iconv_t c=iconv_open("UTF-8","UTF-8"); iconv_close(c); return zlibVersion()==0; }\n')
        self.run(cc, '-Werror', '-fPIE', '-pie', '-Wl,-z,relro,-z,now,-z,max-page-size=16384', probe, '-lz', '-o', self.root / 'control')
        self.inspect(self.root / 'control', toolbin)
        self.phase('Android shared-memory link control')
        probe = self.root / 'shm-control.c'
        probe.write_text(ANDROID_SHM_PROBE)
        self.run(cc, '-Werror', '-fPIE', '-pie', '-Wl,-z,relro,-z,now,-z,max-page-size=16384',
                 probe, '-o', self.root / 'shm-control')
        self.inspect(self.root / 'shm-control', toolbin)
        self.emit('LINKED Android shared-memory control; NOT EXECUTED; runtime authority Unknown')
        self.phase('host Meson preparation')
        self.run(sys.executable, '-m', 'venv', '--system-site-packages', self.root / 'host-tools')
        host_python = self.root / 'host-tools/bin/python'
        self.run(host_python, '-m', 'pip', 'install', '--no-index', '--no-deps', '--ignore-installed',
                 *[qemu / 'python/wheels' / name for name in WHEELS])
        meson = self.root / 'host-tools/bin/meson'
        self.run(meson, '--version', show=True)
        cross = self.root / 'android.ini'
        cross.write_text("[binaries]\n" +
                         f"c = '{cc}'\ncpp = '{cxx}'\nar = '{toolbin}/llvm-ar'\nstrip = '{toolbin}/llvm-strip'\npkg-config = '/usr/bin/pkg-config'\n" +
                         "[host_machine]\nsystem = 'android'\ncpu_family = 'aarch64'\ncpu = 'aarch64'\nendian = 'little'\n" +
                         "[properties]\nneeds_exe_wrapper = true\n" +
                         f"pkg_config_libdir = '{prefix}/lib/pkgconfig'\n" +
                         "[built-in options]\nc_args = ['-O2', '-fPIC', '-fstack-protector-strong', '-D_FORTIFY_SOURCE=2']\n" +
                         "c_link_args = ['-Wl,-z,relro,-z,now,-z,max-page-size=16384']\n")
        # The compiler supplies the NDK sysroot. A pkg-config sys_root would
        # incorrectly prepend it to our already absolute target prefix.
        native = self.root / 'native.ini'
        native.write_text("[binaries]\nc = '/usr/bin/cc'\ncpp = '/usr/bin/c++'\nar = '/usr/bin/ar'\nstrip = '/usr/bin/strip'\n")
        # Autoconf release scripts; no autoreconf, PCRE2 JIT or target tests.
        for name, options in (
            ('pcre2', ['--disable-shared', '--enable-static', '--with-pic', '--disable-jit',
                       '--enable-option-checking=fatal', '--disable-pcre2-16', '--disable-pcre2-32']),
            ('libffi', ['--disable-shared', '--enable-static', '--with-pic', '--disable-docs', '--disable-multi-os-directory']),
        ):
            self.phase(name + ' Android build')
            build = self.root / (name + '-build')
            build.mkdir()
            self.run('sh', sources[name] / 'configure', '--host=aarch64-linux-android',
                     f'--prefix={prefix}', f'--libdir={prefix}/lib', *options, cwd=build, env=target_env, show=True)
            if name == 'pcre2':
                # PCRE2 10.46's Autoconf build has no switch to omit programs.
                # only its reviewed library/header/pkg-config Makefile targets.
                self.run('make', '-j2', 'V=1', *PCRE2_BUILD_TARGETS,
                         cwd=build, env=target_env, show=True)
                self.run('make', *PCRE2_INSTALL_TARGETS, cwd=build, env=target_env, show=True)
                for directory in (build, build / '.libs', prefix / 'bin'):
                    for tool in ('pcre2grep', 'pcre2test', 'pcre2posix_test', 'pcre2_jit_test'):
                        if os.path.lexists(directory / tool):
                            raise RuntimeError('Unexpected PCRE2 program built or installed')
                for artifact in ('lib/libpcre2-8.a', 'lib/libpcre2-posix.a', 'include/pcre2.h',
                                 'include/pcre2posix.h', 'lib/pkgconfig/libpcre2-8.pc',
                                 'lib/pkgconfig/libpcre2-posix.pc'):
                    if not (prefix / artifact).is_file():
                        raise RuntimeError('Missing PCRE2 library build output')
                self.emit('VERIFIED PCRE2 library/header/pkg-config outputs; grep/test programs absent')
            else:
                self.run('make', '-j2', cwd=build, env=target_env)
                self.run('make', 'install', cwd=build, env=target_env)
            self.emit(f'BUILT {name}; target execution NOT RUN')
            for artifact in sorted((prefix / 'lib').glob('*.a')):
                self.emit(f'DEPENDENCY {artifact.name} sha256={digest(artifact)}')
        self.phase('libfdt Android build')
        fdt = qemu / 'subprojects/dtc/libfdt'
        objects = []
        for name in FDT_OBJECTS:
            obj = self.root / (name + '.o')
            self.run(cc, *shlex.split(target_env['CFLAGS']), '-I', fdt, '-c', fdt / (name + '.c'), '-o', obj)
            objects.append(obj)
        self.run(toolbin / 'llvm-ar', 'rcsD', prefix / 'lib/libfdt.a', *objects)
        for name in FDT_HEADERS:
            shutil.copy2(fdt / name, prefix / 'include' / name)
        self.emit(f'BUILT libfdt sha256={digest(prefix / "lib/libfdt.a")}; target execution NOT RUN')
        fdt_archive_sha = digest(prefix / 'lib/libfdt.a')
        fdt_header_hashes = {name: digest(fdt / name) for name in FDT_HEADERS}
        self.phase('GLib Android configure and build')
        glib_build = self.root / 'glib-build'
        self.run(meson, 'setup', glib_build, glib, '--cross-file', cross, '--native-file', native, '--wrap-mode=nodownload',
                 f'--prefix={prefix}', '--libdir=lib', '-Ddefault_library=static', '-Db_staticpic=true',
                 '-Dtests=false', '-Dinstalled_tests=false', '-Ddocumentation=false', '-Dman-pages=disabled',
                 '-Dintrospection=disabled', '-Dnls=disabled', '-Dlibmount=disabled', '-Dselinux=disabled',
                 '-Dxattr=false', '-Dlibelf=disabled', '-Ddtrace=disabled', '-Dsystemtap=disabled',
                 '-Dsysprof=disabled', env=target_env, show=True)
        self.run(self.host_ninja, '-C', glib_build, '-j2', env=target_env)
        self.run(meson, 'install', '-C', glib_build, '--no-rebuild', env=target_env)
        self.emit('BUILT GLib graph; target execution NOT RUN')
        for artifact in sorted((prefix / 'lib').glob('*.a')):
            self.emit(f'DEPENDENCY {artifact.name} size={artifact.stat().st_size} sha256={digest(artifact)}')
        self.phase('verified libfdt archive and Android link control')
        archive = prefix / 'lib/libfdt.a'
        verify_fdt_identity(prefix, fdt_archive_sha, fdt_header_hashes)
        members = self.run(toolbin / 'llvm-ar', 't', archive, show=True)
        headers = self.run(toolbin / 'llvm-readelf', '-h', archive, show=True)
        symbols = self.run(toolbin / 'llvm-nm', '--defined-only', '--extern-only', archive, show=True)
        validate_fdt_inspection(members, headers, symbols)
        probe = self.root / 'fdt-control.c'
        probe.write_text(ANDROID_FDT_PROBE)
        self.run(cc, '-Werror', '-fPIE', '-pie', '-Wl,-z,relro,-z,now,-z,max-page-size=16384',
                 '-I', prefix / 'include', probe, archive, '-o', self.root / 'fdt-control')
        self.inspect(self.root / 'fdt-control', toolbin)
        verify_fdt_identity(prefix, fdt_archive_sha, fdt_header_hashes)
        self.emit('LINKED verified Android libfdt control; NOT EXECUTED')
        self.phase('reviewed Android libfdt discovery adaptation')
        apply_android_fdt_patch(qemu, prefix, self.emit)
        self.phase('QEMU Android configure')
        (qemu / 'configs/devices/aarch64-softmmu/pdva.mak').write_text('CONFIG_ARM_VIRT=y\n')
        build = self.root / 'qemu-build'
        build.mkdir()
        target_env['PKG_CONFIG'] = '/usr/bin/pkg-config --static'
        self.run('sh', qemu / 'configure', '--target-list=aarch64-softmmu', '--cross-prefix=',
                 f'--cc={cc}', f'--cxx={cxx}', '--host-cc=cc', '--cpu=aarch64',
                 f'--python={host_python}', f'--ninja={self.host_ninja}', '--disable-download',
                 '--without-default-features', '--without-default-devices', '--with-devices-aarch64=pdva',
                 '--enable-tcg', '--enable-stack-protector', '--enable-fdt=system', '--disable-rust', '--disable-docs',
                 '--disable-tools', '--disable-guest-agent', '--disable-plugins', '--disable-pixman',
                 '--disable-gio', '--disable-modules', '--disable-install-blobs', '--audio-drv-list=',
                 '--disable-slirp', '--disable-virtfs', '--disable-libusb', '--disable-opengl', '--disable-kvm',
                 f'--extra-cflags=-I{prefix}/include',
                 f'--extra-ldflags=-L{prefix}/lib -Wl,-Map,{build}/qemu.map -v',
                 '-Dprefer_static=true', '-Db_staticpic=true', cwd=build, env=target_env, show=True)
        self.emit('CONFIGURED QEMU; compilation not yet proved')
        for path in sorted(build.glob('*config*.mak')) + sorted(build.glob('*config*.h')):
            self.emit(f'CONFIG {path.name} sha256={digest(path)}\n{path.read_text()}')
        self.phase('QEMU Android compile and link')
        self.run(self.host_ninja, '-j2', 'qemu-system-aarch64', cwd=build, env=target_env, timeout=1500)
        compile_log = self.logs / f'{self.sequence:03d}.log'
        binary = build / 'qemu-system-aarch64'
        self.emit(f'BUILT QEMU size={binary.stat().st_size} sha256={digest(binary)}')
        self.phase('actual QEMU link provenance before ELF acceptance')
        self.run(self.host_ninja, '-t', 'commands', 'qemu-system-aarch64', cwd=build)
        evidence = qemu_link_evidence(binary, build, toolbin, self.logs / f'{self.sequence:03d}.log',
                                      compile_log, self.emit)
        self.phase('native output inspection')
        self.inspect(binary, toolbin, mode='static', evidence=evidence)
        self.run(toolbin / 'llvm-size', '-A', binary, show=True)
        linkmap = build / 'qemu.map'
        self.emit(f'LINK MAP sha256={digest(linkmap)}')
        inventory = sorted({line.strip() for line in linkmap.read_text().splitlines()
                            if ('.a(' in line or '/hw/' in line or '/tcg/' in line) and ':(' not in line})
        self.emit('LINKED OBJECT INVENTORY\n' + '\n'.join(inventory))
        self.run(meson, 'introspect', '--dependencies', build, show=True)
        self.run(meson, 'introspect', '--buildoptions', build, show=True)
        for path in sorted((prefix / 'lib').glob('*.a')):
            self.emit(f'DEPENDENCY {path.name} size={path.stat().st_size} sha256={digest(path)}')
        self.emit('COMPLETE: cross-build only. Android execution Unknown. Gate 0 Unresolved; A-G Not reached.')

    def inspect(self, binary, toolbin, mode='dynamic', evidence=None):
        text = self.run(toolbin / 'llvm-readelf', '-h', '-l', '-d', '-W', binary, show=True)
        if binary.stat().st_size > 256 * 1024 * 1024:
            raise RuntimeError('ELF exceeds inspection budget')
        report = inspect_android_elf(binary.read_bytes(), mode)
        self.emit('STRUCTURED ELF ' + json.dumps(report, sort_keys=True))
        if mode == 'static':
            require_static_startup(report, evidence or {})
        # Keep every original dynamic-PIE control check as an additional gate.
        if ('AArch64' not in text or 'ELF64' not in text or
                '/system/bin/linker64' not in text or 'DYN' not in text):
            raise RuntimeError('Output is not the expected Android AArch64 PIE')
        if any(token in text for token in ('GLIBC_', 'RPATH', 'RUNPATH', 'TEXTREL')):
            raise RuntimeError('Unexpected loader dependency or relocation property')
        self.run(toolbin / 'llvm-readelf', '--dyn-syms', '--version-info', '-W', binary, show=True)
        symbols_log = self.logs / f'{self.sequence:03d}.log'
        if 'GLIBC_' in symbols_log.read_text(errors='replace'):
            raise RuntimeError('GNU libc symbol version in Android output')
        needed = set(re.findall(r'Shared library: \[([^\]]+)\]', text))
        if not needed or not needed <= {'libc.so', 'libdl.so', 'libm.so', 'libz.so', 'liblog.so'}:
            raise RuntimeError(f'Unexpected DT_NEEDED closure: {sorted(needed)}')
        for line in text.splitlines():
            fields = line.split()
            if fields and fields[0] == 'LOAD' and int(fields[-1], 16) < 16384:
                raise RuntimeError('LOAD alignment below 16 KiB')
            if fields and fields[0] == 'GNU_STACK' and 'E' in ''.join(fields[6:-1]):
                raise RuntimeError('Executable stack')
        if 'GNU_RELRO' not in text or ('BIND_NOW' not in text and 'NOW' not in text):
            raise RuntimeError('Missing RELRO/bind-now')


def main():
    if sys.version_info < (3, 12) or platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise RuntimeError('Requires Linux x86-64 and Python >=3.12; no target executed')
    research = Research()
    def terminated(signum, _frame):
        # Raising unwinds run() and kills its separate process group on timeout
        # or cancellation instead of leaving compiler descendants behind.
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, terminated)
    try:
        research.build()
    except Exception as exc:
        research.emit(f'FAILED [{research.stage}]: {exc}; later stages NOT RUN; no gate change.')
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            research.emit(exc.stderr[-24000:].decode('utf-8', errors='replace'))
        # Preserve bounded, sanitized compiler diagnostics, including configure failures.
        for path in sorted(research.root.rglob('meson-log.txt')) + sorted(research.root.rglob('config.log')):
            with path.open('rb') as stream:
                stream.seek(max(0, path.stat().st_size - 24000))
                research.emit(f'DIAGNOSTIC {path.relative_to(research.root)}\n' + stream.read().decode('utf-8', errors='replace'))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
