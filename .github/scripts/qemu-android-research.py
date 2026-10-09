#!/usr/bin/env python3
"""Bounded, non-executing Android cross-build research; see the evidence ledger.

Python standard library only. Linux x86-64, Python >=3.12. Outputs live in a new
runner temporary directory, never in the checkout. Every failed stage is fatal.
No target program is run, installed into Android, uploaded or published.
"""
import hashlib
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat
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


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(path, expected):
    actual = digest(path)
    if actual != expected:
        raise RuntimeError(f'Hash mismatch: {Path(path).name}: {actual}')
    print(f'VERIFIED {Path(path).name} sha256={actual}', flush=True)


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
        self.env = {key: os.environ[key] for key in ('PATH', 'HOME', 'TMPDIR') if key in os.environ}
        self.env.update(LC_ALL='C.UTF-8', LANG='C.UTF-8', TZ='UTC',
                        PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1',
                        PYTHONNOUSERSITE='1', GIT_TERMINAL_PROMPT='0',
                        GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', GIT_NO_REPLACE_OBJECTS='1',
                        PKG_CONFIG_PATH='', PKG_CONFIG_DIR='')

    def emit(self, value):
        value = str(value).replace(str(self.root), '$RESEARCH')
        value = value.replace(str(Path.home()), '$HOME')
        print(value, flush=True)

    def run(self, *args, cwd=None, env=None, timeout=900, show=False):
        self.sequence += 1
        self.emit(f'RUN [{self.stage}] ' + shlex.join(map(str, args)))
        log = self.logs / f'{self.sequence:03d}.log'
        with log.open('wb') as output:
            process = subprocess.Popen(list(map(str, args)), cwd=cwd or self.root,
                                       env=env or self.env, stdout=output,
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
                        ['ninja', '--version'], ['pkg-config', '--version']):
            self.run(*command, show=True)
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
        shutil.copytree(sources['gvdb'], glib / 'subprojects/gvdb')
        shutil.copytree(sources['proxy'], glib / 'subprojects/proxy-libintl-0.5')
        for name, sha in WHEELS.items():
            verify(qemu / 'python/wheels' / name, sha)
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
        # Autoconf release scripts; no autoreconf, Meson patches, JIT or tests.
        for name, options in (
            ('pcre2', ['--disable-shared', '--enable-static', '--with-pic', '--disable-jit',
                       '--disable-pcre2grep', '--disable-pcre2test', '--disable-pcre2-16', '--disable-pcre2-32']),
            ('libffi', ['--disable-shared', '--enable-static', '--with-pic', '--disable-docs', '--disable-multi-os-directory']),
        ):
            self.phase(name + ' Android build')
            build = self.root / (name + '-build')
            build.mkdir()
            self.run('sh', sources[name] / 'configure', '--host=aarch64-linux-android',
                     f'--prefix={prefix}', f'--libdir={prefix}/lib', *options, cwd=build, env=target_env, show=True)
            self.run('make', '-j2', cwd=build, env=target_env)
            self.run('make', 'install', cwd=build, env=target_env)
            self.emit(f'BUILT {name}; target execution NOT RUN')
            for artifact in sorted((prefix / 'lib').glob('*.a')):
                self.emit(f'DEPENDENCY {artifact.name} sha256={digest(artifact)}')
        self.phase('libfdt Android build')
        fdt = qemu / 'subprojects/dtc/libfdt'
        objects = []
        for name in ('fdt', 'fdt_addresses', 'fdt_check', 'fdt_empty_tree', 'fdt_overlay',
                     'fdt_ro', 'fdt_rw', 'fdt_strerror', 'fdt_sw', 'fdt_wip'):
            obj = self.root / (name + '.o')
            self.run(cc, *shlex.split(target_env['CFLAGS']), '-I', fdt, '-c', fdt / (name + '.c'), '-o', obj)
            objects.append(obj)
        self.run(toolbin / 'llvm-ar', 'rcsD', prefix / 'lib/libfdt.a', *objects)
        for name in ('libfdt.h', 'libfdt_env.h', 'fdt.h'):
            shutil.copy2(fdt / name, prefix / 'include' / name)
        self.emit(f'BUILT libfdt sha256={digest(prefix / "lib/libfdt.a")}; target execution NOT RUN')
        self.phase('GLib Android configure and build')
        glib_build = self.root / 'glib-build'
        self.run(meson, 'setup', glib_build, glib, '--cross-file', cross, '--native-file', native, '--wrap-mode=nodownload',
                 f'--prefix={prefix}', '--libdir=lib', '-Ddefault_library=static', '-Db_staticpic=true',
                 '-Dtests=false', '-Dinstalled_tests=false', '-Ddocumentation=false', '-Dman-pages=disabled',
                 '-Dintrospection=disabled', '-Dnls=disabled', '-Dlibmount=disabled', '-Dselinux=disabled',
                 '-Dxattr=false', '-Dlibelf=disabled', '-Ddtrace=disabled', '-Dsystemtap=disabled',
                 '-Dsysprof=disabled', env=target_env, show=True)
        self.run('ninja', '-C', glib_build, '-j2', env=target_env)
        self.run(meson, 'install', '-C', glib_build, '--no-rebuild', env=target_env)
        self.emit('BUILT GLib graph; target execution NOT RUN')
        for artifact in sorted((prefix / 'lib').glob('*.a')):
            self.emit(f'DEPENDENCY {artifact.name} size={artifact.stat().st_size} sha256={digest(artifact)}')
        self.phase('QEMU Android configure')
        (qemu / 'configs/devices/aarch64-softmmu/pdva.mak').write_text('CONFIG_ARM_VIRT=y\n')
        build = self.root / 'qemu-build'
        build.mkdir()
        target_env['PKG_CONFIG'] = '/usr/bin/pkg-config --static'
        self.run('sh', qemu / 'configure', '--target-list=aarch64-softmmu', '--cross-prefix=',
                 f'--cc={cc}', f'--cxx={cxx}', '--host-cc=cc', '--cpu=aarch64',
                 f'--python={host_python}', '--ninja=/usr/bin/ninja', '--disable-download',
                 '--without-default-features', '--without-default-devices', '--with-devices-aarch64=pdva',
                 '--enable-tcg', '--enable-stack-protector', '--enable-fdt=system', '--disable-rust', '--disable-docs',
                 '--disable-tools', '--disable-guest-agent', '--disable-plugins', '--disable-pixman',
                 '--disable-gio', '--disable-modules', '--disable-install-blobs', '--audio-drv-list=',
                 '--disable-slirp', '--disable-virtfs', '--disable-libusb', '--disable-opengl', '--disable-kvm',
                 f'--extra-cflags=-I{prefix}/include',
                 f'--extra-ldflags=-L{prefix}/lib -Wl,-Map,{build}/qemu.map',
                 '-Dprefer_static=true', '-Db_staticpic=true', cwd=build, env=target_env, show=True)
        self.emit('CONFIGURED QEMU; compilation not yet proved')
        for path in sorted(build.glob('*config*.mak')) + sorted(build.glob('*config*.h')):
            self.emit(f'CONFIG {path.name} sha256={digest(path)}\n{path.read_text()}')
        self.phase('QEMU Android compile and link')
        self.run('ninja', '-j2', 'qemu-system-aarch64', cwd=build, env=target_env, timeout=1500)
        binary = build / 'qemu-system-aarch64'
        self.emit(f'BUILT QEMU size={binary.stat().st_size} sha256={digest(binary)}')
        self.phase('native output inspection')
        self.inspect(binary, toolbin)
        self.run(toolbin / 'llvm-size', '-A', binary, show=True)
        commands = self.run('ninja', '-t', 'commands', 'qemu-system-aarch64', cwd=build)
        self.emit('BUILD COMMANDS tail (full log retained only on runner)\n' + commands)
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

    def inspect(self, binary, toolbin):
        text = self.run(toolbin / 'llvm-readelf', '-h', '-l', '-d', '-W', binary, show=True)
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
