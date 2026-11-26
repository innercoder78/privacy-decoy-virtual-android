"""Single disposable cross-link supervisor and exact reviewed probe."""
import hashlib
import json
import os
import stat
import sys
from pathlib import Path


PROBE = r'''use std::os::fd::FromRawFd;
use std::os::unix::net::UnixStream;
use vmm_sys_util::sock_ctrl_msg::ScmSocket;

#[no_mangle]
pub unsafe extern "C" fn pdva_scm_probe(tx: i32, rx: i32, payload: i32) -> i32 {
    let sender = unsafe { UnixStream::from_raw_fd(tx) };
    let receiver = unsafe { UnixStream::from_raw_fd(rx) };
    if !matches!(sender.send_with_fd(&[0x51_u8][..], payload), Ok(1)) {
        return -1;
    }
    let mut byte = [0_u8];
    match receiver.recv_with_fd(&mut byte) {
        Ok((1, Some(_received))) if byte == [0x51] => 0,
        _ => -2,
    }
}
'''

RECIPE = r'''set -eu
T=aarch64-linux-android
common=(--target "$T" --crate-type rlib -C codegen-units=1 -C panic=abort -C relocation-model=pic)
CARGO_PKG_VERSION=1.3.2 "$R" "${common[@]}" --edition 2018 --crate-name bitflags \
  --cfg 'feature="default"' "$D/extra_versions/crates/bitflags/src/lib.rs" -o "$O/libbitflags.rlib" || exit 71
CARGO_PKG_VERSION=0.2.183 "$R" "${common[@]}" --edition 2021 --crate-name libc \
  --cfg freebsd12 --cfg 'feature="default"' --cfg 'feature="std"' --cfg 'feature="extra_traits"' \
  "$D/crates/libc/src/lib.rs" -o "$O/liblibc.rlib" || exit 72
CARGO_PKG_VERSION=0.15.0 "$R" "${common[@]}" --edition 2021 --crate-name vmm_sys_util \
  --extern "libc=$O/liblibc.rlib" --extern "bitflags=$O/libbitflags.rlib" \
  "$D/crates/vmm-sys-util/src/lib.rs" -o "$O/libvmm_sys_util.rlib" || exit 73
"$R" --target "$T" --edition 2021 --crate-type cdylib -C codegen-units=1 -C panic=abort -C relocation-model=pic \
  -C "linker=$N/bin/aarch64-linux-android30-clang" -C "link-arg=-Wl,-Map,$O/probe.map" \
  -C link-arg=-Wl,--threads=1 -C link-arg=-Wl,-z,defs,-z,max-page-size=16384 -L "dependency=$O" \
  --extern "vmm_sys_util=$O/libvmm_sys_util.rlib" probe.rs -o "$O/libprobe.so" || exit 74
"$N/bin/llvm-readelf" -h -lW -d -rW --dyn-syms --version-info "$O/libprobe.so" || exit 75
'''


CRATE_TREES = {
    'extra_versions/crates/bitflags': ('e775d9fbf16e476410d0b632bb6c8799ea2438de', 41, 'LICENSE-APACHE'),
    'crates/libc': ('e74103e9adb95bdc9755bc8366d30c455c158602', 369, 'LICENSE-APACHE'),
    'crates/vmm-sys-util': ('e788dce7bc549fcc32ff9ddcd185bddc72007385', 41, 'LICENSE-BSD-3-Clause'),
}


def tree_inventory(directory, license_target):
    """Reconstruct canonical Git trees from a sealed Linux source export."""
    inventory = {}
    def walk(folder):
        rows = []
        for item in folder.iterdir():
            key = item.relative_to(directory).as_posix()
            name = item.name.encode('utf-8')
            mode = item.lstat().st_mode
            if stat.S_ISDIR(mode):
                rows.append((name + b'/', b'40000 ' + name + b'\0' + walk(item)))
                continue
            if stat.S_ISLNK(mode):
                data = os.fsencode(os.readlink(item))
                if key != 'LICENSE' or data != license_target.encode():
                    raise ValueError('source-link')
                gitmode = '120000'
            else:
                if not stat.S_ISREG(mode) or mode & 0o111:
                    raise ValueError('source-mode')
                gitmode = '100644'
                data = item.read_bytes()
            oid = git_object('blob', data)
            inventory[key] = (gitmode, oid.hex(), hashlib.sha256(data).hexdigest())
            rows.append((name, gitmode.encode() + b' ' + name + b'\0' + oid))
        return git_object('tree', b''.join(row for _, row in sorted(rows)))
    return walk(directory).hex(), inventory


def git_object(kind, data):
    return hashlib.sha1(f'{kind} {len(data)}\0'.encode() + data).digest()


def verify_sources(directory):
    inventory = {}
    for crate, (oid, count, license_target) in CRATE_TREES.items():
        observed, rows = tree_inventory(directory / crate, license_target)
        if (observed, len(rows)) != (oid, count):
            raise ValueError('source-tree')
        inventory[crate] = rows
    return hashlib.sha256(json.dumps(inventory, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def verify_digest(stream, expected, algorithm):
    if hashlib.file_digest(stream, algorithm).hexdigest() != expected:
        raise ValueError('distribution-' + algorithm)


def identity_controls():
    import io
    good = b'fixture'
    for name in ('sha256', 'sha1'):
        expected = hashlib.new(name, good).hexdigest()
        verify_digest(io.BytesIO(good), expected, name)
        try:
            verify_digest(io.BytesIO(b'fixturf'), expected, name)
        except ValueError as failure:
            if str(failure) != 'distribution-' + name:
                raise
        else:
            raise AssertionError('corrupted-input-accepted')
    print('PASS unchanged and corrupted synthetic bytes for both digest algorithms')



"""Acquisition metadata checks. Call only on sealed inputs in the disposable VM."""
import hashlib
import os
import subprocess
import tarfile
import tomllib
import zipfile
from pathlib import Path

PRIMARY = "108F66205EAEB0AAA8DD5E1C85AB96E6FA1BE5FE"
MANIFEST = "3051e859570f64a8c5acb9d09e87425db52c7d97287c67e8f6d57d7d34ef9258"
PINS = {
    ("rustc", "x86_64-unknown-linux-gnu"): "f1d0b1dec81dab6f523cd098507763487b0d4bd7fd2c87582f154128719be03b",
    ("rust-std", "x86_64-unknown-linux-gnu"): "4591b6486594ded52ecd6135db95bf9355bbd3ca7a380888b141528bbcf9a5d4",
    ("rust-std", "aarch64-linux-android"): "5e7503cc0cb87b710457d13ec97b2e7729a1210a2fdce9ad99bd0c86e0f69186",
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def gpg_status(output, returncode):
    rows = [line.split()[1:] for line in output.splitlines() if line.startswith("[GNUPG:] ")]
    require(returncode == 0 and all(row and row[0] in {
        "NEWSIG", "SIG_ID", "KEY_CONSIDERED", "GOODSIG", "VALIDSIG", "VERIFICATION_COMPLIANCE_MODE"
    } for row in rows), "signature-status")
    valid = [row for row in rows if row[0] == "VALIDSIG"]
    require(len(valid) == 1 and len(valid[0]) == 11 and valid[0][-1] == PRIMARY, "primary-signer")


def authenticated(path, expected, ring):
    result = subprocess.run(["/usr/bin/gpgv", "--homedir", str(ring.parent), "--keyring", str(ring),
                             "--status-fd", "1", str(path) + ".asc", str(path)],
                            close_fds=True, capture_output=True, timeout=90, text=True,
                            env={"PATH": "/usr/bin", "LC_ALL": "C"})
    gpg_status(result.stdout, result.returncode)
    with path.open("rb") as stream:
        verify_digest(stream, expected, "sha256")


def verify_distribution(directory, ring):
    path = directory / "channel-rust-1.100.0.toml"
    authenticated(path, MANIFEST, ring)
    manifest = tomllib.loads(path.read_text())
    for (package, target), pin in PINS.items():
        name = f"{package}-1.100.0-{target}.tar.xz"
        row = manifest["pkg"][package]["target"][target]
        require(row["available"] and row["xz_hash"] == pin and
                row["xz_url"] == "https://static.rust-lang.org/dist/2026-11-12/" + name,
                "manifest-entry")
        authenticated(directory / name, pin, ring)
    ndk = directory / "android-ndk-r28c-linux.zip"
    require(ndk.stat().st_size == 722261334, "ndk-size")
    for algorithm, pin in (("sha1", "a7b54a5de87fecd125a17d54f73c446199e72a64"),
                           ("sha256", "dfb20d396df28ca02a8c708314b814a4d961dc9074f9a161932746f815aa552f")):
        with ndk.open("rb") as stream:
            verify_digest(stream, pin, algorithm)


GIB = 1 << 30
LIMIT = 10 * GIB
SOURCE_TAG = "76914b4705208e870f8ef1ddcef0343fbc622c39"
SOURCE_COMMIT = "1f5e95cd6e996995023c9c0f7df0f15a8a43269e"
BASE_ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "HOME": "/nonexistent"}


def command(*args, output=False):
    return subprocess.run(args, check=True, close_fds=True, env={**BASE_ENV, "GIT_CONFIG_NOSYSTEM":"1", "GIT_CONFIG_GLOBAL":"/dev/null", "GIT_TERMINAL_PROMPT":"0"},
                          stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          stdout=subprocess.PIPE if output else subprocess.DEVNULL).stdout


def portable(name):
    require(name and not name.startswith("/") and "\\" not in name and
            all(token not in ("", ".", "..") for token in name.split("/")), "archive-path")
    return Path(name)


def copy_stream(src, dst, maximum):
    n = 0
    while data := src.read(1 << 20):
        n += len(data)
        require(n <= maximum, "stream-extent")
        dst.write(data)
    return n


def extract(path, destination):
    import shutil
    destination.mkdir()
    zipped = path.suffix == ".zip"
    with (zipfile.ZipFile(path) if zipped else tarfile.open(path, "r:xz")) as archive:
        members = archive.infolist() if zipped else archive.getmembers()
        size = lambda row: row.file_size if zipped else row.size
        require(sum(size(row) + 4096 for row in members) <= shutil.disk_usage(destination).free,
                "expansion-budget")
        links = []
        seen = set()
        for row in members:
            name = (row.filename if zipped else row.name).rstrip("/")
            entry = destination / portable(name)
            require(entry not in seen, "duplicate-member")
            seen.add(entry)
            mode = row.external_attr >> 16 if zipped else row.mode
            if (row.is_dir() if zipped else row.isdir()):
                entry.mkdir(parents=True, exist_ok=True)
                continue
            entry.parent.mkdir(parents=True, exist_ok=True)
            if (stat.S_ISLNK(mode) if zipped else row.issym()):
                require(size(row) <= 4096, "link-size")
                target = archive.read(row).decode() if zipped else row.linkname
                require(target and not os.path.isabs(target) and "\\" not in target, "link-target")
                links.append((entry, target))
                continue
            require(stat.S_IFMT(mode) in (0, stat.S_IFREG) if zipped else row.isfile(), "archive-type")
            with (archive.open(row) if zipped else archive.extractfile(row)) as src, entry.open("xb") as dst:
                require(copy_stream(src, dst, size(row)) == size(row), "member-length")
            entry.chmod(0o755 if mode & 0o111 else 0o644)
        for entry, target in links:
            entry.symlink_to(target)
        for entry, _ in links:
            require(entry.resolve(strict=True).is_relative_to(destination), "escaping-link")


def prefix_install(root, prefix, expected):
    require((root / "components").read_text().splitlines() == [expected], "component-identity")
    for component in (expected,):
        folder = root / portable(component)
        for line in (folder / "manifest.in").read_text().splitlines():
            kind, name = line.split(":", 1)
            item = folder / portable(name)
            require(item.resolve(strict=True).is_relative_to(folder), "component-escape")
            require((kind == "file" and item.is_file()) or (kind == "dir" and item.is_dir()),
                    "component-entry")
            for src in ([item] if kind == "file" else sorted(p for p in item.rglob("*") if p.is_file())):
                resolved = src.resolve(strict=True)
                require(resolved.is_relative_to(folder), "payload-escape")
                out = prefix / src.relative_to(folder)
                out.parent.mkdir(parents=True, exist_ok=True)
                os.link(resolved, out)
                require(os.path.samefile(resolved, out), "installed-inode")


def fetch(url, path, maximum):
    import urllib.request
    class RejectRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args):
            raise ValueError("redirect")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), RejectRedirect)
    with opener.open(url, timeout=40) as response, path.open("xb") as stream:
        require(response.geturl() == url, "redirect")
        copy_stream(response, stream, maximum)


def acquire(volume):
    import shutil
    data = volume / "inputs"
    data.mkdir()
    key = volume / "key.asc"
    ring = volume / "release.gpg"
    fetch("https://raw.githubusercontent.com/dariogriffo/rust-stable-debian/"
          "ca0035d95a1c6469f88653c061c2cb5f7465566f/debian/upstream/signing-key.asc", key, 1 << 16)
    command("gpg", "--batch", "--homedir", str(volume), "--dearmor", "-o", str(ring), str(key))
    dist = "https://static.rust-lang.org/dist/"
    name = "channel-rust-1.100.0.toml"
    for ext in ("", ".asc"):
        fetch(dist + name + ext, volume / (name + ext), 8 << 20)
    authenticated(volume / name, MANIFEST, ring)
    for package, target in PINS:
        name = f"{package}-1.100.0-{target}.tar.xz"
        for ext, limit in (("", GIB), (".asc", 1 << 16)):
            fetch(dist + "2026-11-12/" + name + ext, volume / (name + ext), limit)
    ndk = volume / "android-ndk-r28c-linux.zip"
    fetch("https://dl.google.com/android/repository/" + ndk.name, ndk, 722261334)
    verify_distribution(volume, ring)
    REPORT.passed("distribution")
    REPORT.begin("installed-inputs")
    for package, target in PINS:
        name = f"{package}-1.100.0-{target}"
        archive = volume / (name + ".tar.xz")
        temporary = volume / "expand"
        extract(archive, temporary)
        prefix_install(temporary / name, data / "rust", "rustc" if package == "rustc" else "rust-std-" + target)
        shutil.rmtree(temporary)
        archive.unlink()
    extract(ndk, data / "ndk")
    ndk.unlink()
    require("Pkg.Revision = 28.2.13676358" in
            (data / "ndk/android-ndk-r28c/source.properties").read_text().splitlines(), "ndk-revision")
    return data


def release_sources(volume, data):
    import shutil
    db = volume / "release.git"
    command("git", "init", "--bare", "--template=", str(db))
    def git(*args):
        return command("git", "--git-dir", str(db), *args, output=True)
    ref = "refs/tags/android-17.0.0_r1"
    git("-c", "http.followRedirects=false", "-c", "fetch.fsckObjects=true", "fetch", "--no-tags", "--depth=1",
        "https://android.googlesource.com/platform/external/rust/android-crates-io", ref + ":" + ref)
    require(git("rev-parse", ref, ref + "^{}").decode().splitlines() ==
            [SOURCE_TAG, SOURCE_COMMIT], "release-tag")
    git("fsck", "--full", "--strict", "--no-reflogs", SOURCE_TAG)
    for crate, (oid, _, license_target) in CRATE_TREES.items():
        require(git("rev-parse", SOURCE_COMMIT + ":" + crate).decode().strip() == oid, "release-tree")
        for row in git("ls-tree", "-rz", oid).split(b"\0"):
            if not row:
                continue
            meta, name = row.split(b"\t", 1)
            mode, kind, blob = meta.decode().split()
            path = data / "D" / crate / portable(name.decode())
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = git("cat-file", "blob", blob)
            require(kind == "blob" and git_object("blob", raw).hex() == blob, "release-blob")
            if mode == "120000":
                require(name == b"LICENSE" and raw == license_target.encode(), "release-link")
                path.symlink_to(license_target)
            else:
                require(mode == "100644", "release-mode")
                path.write_bytes(raw)
    (data / "source-inventory.sha256").write_text(verify_sources(data / "D") + "\n")
    shutil.rmtree(db)


def memory_group():
    fields = Path("/proc/self/cgroup").read_text().splitlines()
    require(len(fields) == 1 and fields[0].startswith("0::/"), "cgroup-v2")
    cg = Path("/sys/fs/cgroup") / fields[0][3:].lstrip("/")
    memory_bounds(cg)
    return cg


def memory_bounds(group):
    require((group / "memory.max").read_text().strip() == str(8 * GIB) and
            (group / "memory.swap.max").read_text().strip() == "0", "memory-limit")


def filesystem_limit(path):
    usage = os.statvfs(path)
    require(0 < usage.f_blocks * usage.f_frsize <= LIMIT, "storage-limit")


def seccomp():
    import ctypes
    import errno
    lib = ctypes.CDLL("libseccomp.so.2")
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    ctx = lib.seccomp_init(0x7fff0000)
    require(ctx, "filter-init")
    try:
        for name in ("socket", "socketpair", "connect", "unshare", "setns", "mount", "umount2",
                     "pivot_root", "open_tree", "move_mount", "fsopen", "fsmount", "mount_setattr",
                     "io_uring_setup", "ptrace", "bpf", "open_by_handle_at", "clone3"):
            nr = lib.seccomp_syscall_resolve_name(name.encode())
            error = errno.ENOSYS if name == "clone3" else errno.EPERM
            require(nr >= 0 and lib.seccomp_rule_add(ctx, 0x50000 | error, nr, 0) == 0, "filter-rule")
        class Compare(ctypes.Structure):
            _fields_ = [("arg", ctypes.c_uint), ("op", ctypes.c_int),
                        ("mask", ctypes.c_uint64), ("value", ctypes.c_uint64)]
        lib.seccomp_rule_add_array.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int,
                                               ctypes.c_uint, ctypes.POINTER(Compare)]
        for bit in (0x80, 0x20000, 0x2000000, 0x4000000, 0x8000000, 0x10000000, 0x20000000, 0x40000000):
            mask = Compare(0, 7, bit, bit)
            require(lib.seccomp_rule_add_array(ctx, 0x50001, lib.seccomp_syscall_resolve_name(b"clone"),
                                               1, ctypes.byref(mask)) == 0, "clone-filter")
        require(lib.seccomp_load(ctx) == 0, "filter-load")
    finally:
        lib.seccomp_release(ctx)


def network_identity(child, parent, routes):
    require(child != parent and len(routes.splitlines()) == 1, "network-namespace")


def socket_denial(factory):
    import errno
    try:
        sock = factory()
    except OSError as failure:
        require(failure.errno == errno.EPERM, "network-filter")
    else:
        sock.close()
        raise ValueError("network-filter")


def audit_build(uid, parent_net):
    import errno
    import socket
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines())
    require(os.getresuid() == (uid,) * 3 and os.getresgid() == (uid,) * 3 and not os.getgroups(),
            "worker-identity")
    require(all(int(status[k], 16) == 0 for k in ("CapPrm", "CapEff", "CapBnd", "CapAmb")) and
            int(status["NoNewPrivs"]) == 1, "privilege")
    network_identity(os.readlink("/proc/self/ns/net"), parent_net, Path("/proc/net/route").read_text())
    for family in (socket.AF_INET, socket.AF_INET6, socket.AF_UNIX):
        socket_denial(lambda: socket.socket(family))
    for fd in Path("/proc/self/fd").iterdir():
        try:
            target = os.readlink(fd)
        except FileNotFoundError:
            continue
        require(int(fd.name) < 3 and target == "/dev/null", "inherited-descriptor")
    for line in Path("/proc/self/mountinfo").read_text().splitlines():
        row = line.split()
        if "rw" in row[5].split(","):
            require(row[4] == "/out" and "noexec" in row[5].split(","), "writable-mount")
    for p in ("/", "/inputs", "/proc", "/limits"):
        require(not os.access(p, os.W_OK), "readonly-input")
    try:
        Path("/inputs/.write-test").touch(exist_ok=False)
    except OSError as exc:
        require(exc.errno in (errno.EROFS,errno.EACCES), "input-write-denial")
    else:
        raise ValueError("input-write-denial")
    memory_bounds(Path("/limits"))
    require(str(os.getpid()) in Path("/limits/cgroup.procs").read_text().split(), "group-membership")
    require(not os.access("/limits/memory.max", os.W_OK), "delegated-limit")
    filesystem_limit("/out")


def worker(mode, uid, net):
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if mode != "control-filter":
        seccomp()
    expected = {"control-net":"network-namespace","control-filter":"network-filter"}.get(mode)
    try:
        audit_build(uid, net)
    except ValueError as failure:
        if expected and str(failure) == expected:
            return
        raise
    require(expected is None, "ineffective-isolation-control")
    if mode == "preflight":
        return
    if mode == "inspect":
        import runpy
        inspect = runpy.run_path("/inspector.py")["native_artifact"]
        inspect(Path("/sealed/libprobe.so"), Path("/sealed/probe.map"), Path("/inputs"))
        return
    require(mode == "build", "worker-mode")
    require(verify_sources(Path("/inputs/D")) ==
            Path("/inputs/source-inventory.sha256").read_text().strip(), "mounted-source")
    compiler = "/inputs/rust/bin/rustc"
    version = command(compiler, "-vV", output=True).decode().splitlines()
    require("release: 1.100.0" in version and
            "commit-hash: 0ef1bc386059596dada8fb65b50425aab2ea637a" in version and
            "host: x86_64-unknown-linux-gnu" in version, "rustc-version")
    ndk = "/inputs/ndk/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64"
    require(Path(ndk + "/bin/aarch64-linux-android30-clang").resolve(strict=True).is_relative_to(ndk),
            "ndk-linker")
    # RECIPE and PROBE come verbatim from the reviewed evidence apart from the two thread controls.
    Path("/out/tmp").mkdir(exist_ok=True)
    os.chdir("/inputs")
    result = subprocess.run(["/bin/bash", "-eu", "-c", RECIPE], close_fds=True, env={
        **BASE_ENV, "D": "/inputs/D", "N": ndk, "R": compiler, "O": "/out", "TMPDIR": "/out/tmp"})
    if result.returncode:
        reasons = {71:"compile-bitflags",72:"compile-libc",73:"compile-vmm-sys-util",
                   74:"link-probe",75:"readelf-summary"}
        raise ValueError(reasons.get(result.returncode,"command-failed"))



def run_cage(volume, group, mode, uid, inputs, output):
    script = Path(__file__).resolve()
    net = os.readlink("/proc/self/ns/net")
    # The outer unit bounds acquisition and all children. The child cgroup can be killed independently.
    cg = group / ("phase-" + mode)
    cg.mkdir()
    (cg / "memory.max").write_text(str(8 * GIB))
    (cg / "memory.swap.max").write_text("0")
    memory_bounds(cg)
    args = ["bwrap", "--die-with-parent", "--unshare-net", "--unshare-pid", "--unshare-ipc",
            "--unshare-uts", "--new-session", "--ro-bind", str(volume / "host-usr"), "/usr",
            "--symlink", "usr/bin", "/bin", "--symlink", "usr/lib", "/lib",
            "--symlink", "usr/lib64", "/lib64", "--proc", "/proc", "--remount-ro", "/proc",
            "--dir", "/dev", "--ro-bind", "/dev/null", "/dev/null",
            "--ro-bind", str(inputs), "/inputs", "--ro-bind", str(script), "/supervisor.py",
            "--ro-bind", str(script.with_name("inspect-rust-cross-link.py")), "/inspector.py",
            "--ro-bind", str(cg), "/limits", "--bind", str(output), "/out"]
    if mode == "inspect":
        args += ["--ro-bind", str(volume / "build"), "/sealed"]
    args += ["--remount-ro", "/", "--clearenv", "--setenv", "PATH", "/usr/bin:/bin",
             "--setenv", "LANG", "C", "--", "/usr/bin/setpriv", "--reuid", str(uid),
             "--regid", str(uid), "--clear-groups", "--no-new-privs", "--bounding-set=-all",
             "--inh-caps=-all", "--ambient-caps=-all", "/usr/bin/python3", "-IB",
             "/supervisor.py", "worker", mode, str(uid), net]
    if mode == "control-net":
        args.remove("--unshare-net")
    def enter():
        (cg / "cgroup.procs").write_text(str(os.getpid()))
    try:
        with open("/dev/null", "r+b", buffering=0) as null:
            child = subprocess.Popen(args, env=BASE_ENV, stdin=null, stdout=null, stderr=null,
                                     close_fds=True, preexec_fn=enter)
            status = watchdog(child, 27*60, lambda: (cg / "cgroup.kill").write_text("1"))
            if status != 0:
                reason = WORKER_REASONS[status-32] if 32 <= status < 32+len(WORKER_REASONS) else "worker-launch"
                raise ValueError(reason)
    except Exception as error:
        REPORT.failure(error)
        raise
    finally:
        (cg / "cgroup.kill").write_text("1")
        import time
        deadline = time.monotonic() + 3
        while "populated 1" in (cg / "cgroup.events").read_text() and time.monotonic() < deadline:
            time.sleep(0.02)
        require("populated 0" in (cg / "cgroup.events").read_text(), "cgroup-cleanup")
        events = dict(row.split() for row in (cg / "memory.events").read_text().splitlines())
        require(int(events["oom"]) == 0 and int(events["max"]) == 0 and
                int((cg / "memory.peak").read_text()) <= 8 * GIB, "memory-events")
        peak = int((cg / "memory.peak").read_text())
        cg.rmdir()
    return peak


WORKER_REASONS = (
    'address-mode',
    'aggregate-memory-events',
    'allocation-ownership',
    'allocation-size',
    'archive-control',
    'archive-location',
    'archive-path',
    'archive-type',
    'authorization-identity',
    'call-return',
    'cgroup-cleanup',
    'cgroup-v2',
    'clone-filter',
    'command-failed',
    'compare-operands',
    'compile-bitflags',
    'compile-libc',
    'compile-vmm-sys-util',
    'component-entry',
    'component-escape',
    'component-identity',
    'deadline',
    'delegated-limit',
    'disassembly-load-bytes',
    'distribution-sha1',
    'distribution-sha256',
    'duplicate-dynamic-tag',
    'duplicate-instruction',
    'duplicate-jump-slot',
    'duplicate-member',
    'duplicate-relocation',
    'dynamic-binding',
    'dynamic-extent',
    'dynamic-loader-override',
    'dynamic-mapping',
    'dynamic-pointer',
    'dynamic-search-path',
    'dynamic-string',
    'dynamic-symbol-count',
    'dynamic-symbol-row',
    'dynamic-table',
    'dynamic-tables-disagree',
    'dynamic-tag',
    'dynamic-terminator',
    'elf-class-data',
    'elf-target',
    'empty-map',
    'entry-point',
    'escaping-link',
    'executable-load',
    'expansion-budget',
    'export-address',
    'export-allowlist',
    'failed-git',
    'failed-gpg',
    'failed-ldd',
    'failed-mkfs.ext4',
    'failed-mount',
    'failed-umount',
    'fd-ownership',
    'filter-init',
    'filter-load',
    'filter-rule',
    'foreign-loader',
    'gnu-hash-chain',
    'gnu-hash-index',
    'gnu-hash-size',
    'gnu-stack',
    'group-membership',
    'header-extent',
    'host-file',
    'host-library',
    'host-origin',
    'host-python',
    'host-tools',
    'import-allowlist',
    'import-version',
    'incomplete-report',
    'indirect-control',
    'ineffective-isolation-control',
    'inert-elf-control',
    'inherited-descriptor',
    'input-write-denial',
    'inspection-size',
    'installed-inode',
    'instruction-extent',
    'instruction-map',
    'interpreter',
    'link-probe',
    'link-size',
    'link-target',
    'load-alignment',
    'load-congruence',
    'loader-control',
    'loader-positive',
    'manifest-entry',
    'map-format',
    'map-input',
    'map-positive',
    'member-length',
    'memory-events',
    'memory-limit',
    'memory-operation',
    'message-name',
    'message-order',
    'missing-call-endpoint',
    'missing-map-origins',
    'missing-reachable-endpoint',
    'mounted-source',
    'msghdr-contract',
    'native-runtime',
    'ndk-linker',
    'ndk-revision',
    'ndk-size',
    'needed-allowlist',
    'needed-table',
    'network-filter',
    'network-namespace',
    'operating-system',
    'os-EACCES',
    'os-EBUSY',
    'os-EIO',
    'os-ENOENT',
    'os-ENOMEM',
    'os-ENOSPC',
    'os-EPERM',
    'os-EROFS',
    'os-ETIMEDOUT',
    'output-type',
    'packed-relocations',
    'page-alias',
    'pair-width',
    'payload-escape',
    'plt-addend',
    'plt-binding',
    'plt-control',
    'plt-extent',
    'plt-offset',
    'plt-sequence',
    'portable-control',
    'positive-control',
    'primary-signer',
    'privilege',
    'probe-binding',
    'probe-object',
    'program-table',
    'project-archive',
    'readelf-summary',
    'readonly-input',
    'redirect',
    'rela-size',
    'release-blob',
    'release-link',
    'release-mode',
    'release-tag',
    'release-tree',
    'relocation-count',
    'relocation-format',
    'relocation-kind',
    'relocation-mapping',
    'relocation-record',
    'relocation-string',
    'relocation-symbol',
    'relocation-tag-family',
    'relocation-target',
    'relocation-tool-disagreement',
    'report-overflow',
    'required-imports',
    'return-address',
    'runner',
    'runner-capacity',
    'runtime-member',
    'rust-runtime',
    'rustc-version',
    'scm-method-origin',
    'scm-receive-contract',
    'scm-send-contract',
    'segment-extent',
    'shifted-operand',
    'signature-status',
    'source-link',
    'source-mode',
    'source-tree',
    'stage-status',
    'storage-limit',
    'stream-extent',
    'string-table-size',
    'successful-scm-witness',
    'supervisor-deadline',
    'symbol-binding',
    'symbol-stride',
    'text-relocation',
    'unexpected',
    'unknown-condition',
    'unknown-memory',
    'unknown-register',
    'unmodeled-external',
    'unsupported-register',
    'unsupported-witness-instruction',
    'version-chain',
    'version-count',
    'version-index',
    'version-library',
    'version-tag-pair',
    'volume-cleanup',
    'witness-budget',
    'worker-identity',
    'worker-launch',
    'worker-mode',
    'writable-executable',
    'writable-mount',
    'write-region',
    'wrong-rejection',
    'wrong-specific-rejection',
)

# Only the privileged supervisor emits public records. All descendant stdio stays private.
STAGES = ("runner", "limits", "host-runtime", "preflight", "control-net", "control-filter",
          "distribution", "installed-inputs", "release-sources", "build", "seal", "inspect",
          "resource-events", "cleanup")
PUBLIC_REASONS = frozenset(("unexpected", "command-failed", "deadline", "operating-system",
                            "authorization-identity", "incomplete-report", "report-overflow",
                            "worker-launch", "invalid-proof", "stage-status")) | frozenset(WORKER_REASONS)
REPORT = None


def safe_reason(error):
    if isinstance(error, ValueError) and error.args and isinstance(error.args[0],str) and error.args[0] in PUBLIC_REASONS:
        return error.args[0]
    if isinstance(error, subprocess.TimeoutExpired):
        return "deadline"
    if isinstance(error, subprocess.CalledProcessError):
        name = Path(str(error.cmd[0])).name if isinstance(error.cmd,(list,tuple)) and error.cmd else ""
        label = "failed-" + name
        return label if label in PUBLIC_REASONS else "command-failed"
    if isinstance(error, OSError):
        import errno
        label = "os-" + errno.errorcode.get(error.errno,"")
        return label if label in PUBLIC_REASONS else "operating-system"
    return "unexpected"


class Evidence:
    def __init__(self, commit, image, emit):
        import re
        require(re.fullmatch(r"[0-9a-f]{40}", commit) and
                re.fullmatch(r"[0-9]{6,8}\.[0-9]+\.[0-9]+", image), "authorization-identity")
        self.count = 0
        self.emit = emit
        self.done = []
        self.active = "runner"
        self.failed = None
        self.cleanup = "unobserved"
        self.record("identity", source=commit, runner="ubuntu-24.04-x64", image=image,
                    release=SOURCE_COMMIT, rust_manifest=MANIFEST, ndk="28.2.13676358")

    def record(self, event, **fields):
        row = json.dumps({"event":event, **fields}, sort_keys=True, separators=(",",":"))
        require(len(row) <= 1024, "report-overflow")
        self.count += 1
        require(self.count <= 36, "report-overflow")
        self.emit(row)

    def begin(self, stage):
        require(stage in STAGES and stage not in self.done, "stage-status")
        self.active = stage
        self.record("begin", stage=stage)

    def passed(self, stage, **measurements):
        require(stage == self.active and stage not in self.done, "stage-status")
        require(all(k in {"available_ram","free_disk","peak_memory"} and
                    type(v) is int and 0 <= v < 2**64 for k,v in measurements.items()), "stage-status")
        self.done.append(stage)
        claims = {
            "distribution":"manifest-signature-three-archive-signatures-and-pins-ndk-size-sha1-sha256",
            "release-sources":"tag-commit-tree-blob-mode-inventory",
            "control-net":"missing-namespace-rejected",
            "control-filter":"missing-socket-filter-rejected",
            "preflight":"uid-gid-caps-network-mounts-descriptors-cgroup-storage",
            "build":"four-serial-compiler-steps-and-readelf-summary",
            "inspect":"elf-loader-versions-relocations-map-and-two-scm-witnesses",
            "cleanup":"private-volume-unmounted"
        }
        self.record("pass", stage=stage, checks=claims.get(stage,stage), **measurements)

    def failure(self, error):
        failure = (self.active, safe_reason(error))
        if self.failed is None:
            self.failed = failure
        self.record("failure", stage=failure[0], reason=failure[1])

    def finish(self):
        complete = self.failed is None and self.done == list(STAGES) and self.cleanup == "unmounted"
        self.record("final", outcome="pass" if complete else "incomplete", cleanup=self.cleanup,
                    unconfirmed=[s for s in STAGES if s not in self.done],
                    unrun=["android-execution","independent-rebuild","production-qualification"])
        require(complete, "incomplete-report")


def reported_run(commit, image, action, emit):
    global REPORT
    REPORT = Evidence(commit,image,emit)
    try:
        action()
    except Exception as failure:
        if REPORT.failed is None or REPORT.active == "cleanup" and REPORT.cleanup != "unmounted":
            REPORT.failure(failure)
    REPORT.finish()


def read_report(source, commit, image, publish):
    """Validate the entire bounded protocol before emitting any line into the Actions log."""
    rows = []
    data = source.read(32769)
    require(len(data)<=32768, "report-overflow")
    lines=data.splitlines()
    import re
    exit_line = lines.pop() if lines else b""
    match = re.fullmatch(rb"unit=([0-9]{1,3})",exit_line)
    require(match is not None and int(match[1])<=255, "incomplete-report")
    unit_status = int(match[1])
    require(0<len(lines)<=36 and data.endswith(b"\n"), "incomplete-report")
    expected=[]
    replay=Evidence(commit,image,expected.append)
    for i,line in enumerate(lines):
        require(len(line)<=1024, "report-overflow")
        row=json.loads(line)
        require(type(row) is dict,"stage-status")
        event=row.pop("event",None)
        if i==0:
            require(event=="identity","stage-status")
        elif event=="begin":
            stage=row["stage"]
            require(stage=="cleanup" or (len(replay.done)<len(STAGES) and stage==STAGES[len(replay.done)]),
                    "stage-status")
            replay.begin(stage)
        elif event=="pass":
            stage=row.pop("stage")
            row.pop("checks")
            replay.passed(stage,**row)
            if stage=="cleanup":
                replay.cleanup="unmounted"
        elif event=="failure":
            require(row["reason"] in PUBLIC_REASONS,"stage-status")
            replay.failure(ValueError(row["reason"]))
        elif event=="final" and i==len(lines)-1:
            try:
                replay.finish()
            except ValueError as exc:
                require(str(exc)=="incomplete-report","stage-status")
        else:
            raise ValueError("stage-status")
        require(len(expected)==i+1 and expected[-1].encode()==line, "stage-status")
        rows.append(expected[-1])
    if unit_status and event=="final" and json.loads(rows[-1])["outcome"]=="pass":
        rows.pop()
        for line in rows:
            publish(line)
        publish("FAIL supervisor unit returned nonzero after its report")
        raise ValueError("incomplete-report")
    for line in rows:
        publish(line)
    require(unit_status==0 and event=="final" and json.loads(rows[-1])["outcome"]=="pass","incomplete-report")


def reader_controls():
    import io
    commit,image="a"*40,"20261120.1.0"
    rows=[]
    def emit_all():
        for stage in STAGES:
            REPORT.begin(stage)
            REPORT.passed(stage)
        REPORT.cleanup="unmounted"
    reported_run(commit,image,emit_all,rows.append)
    encoded=lambda seq, status=0: io.BytesIO(("\n".join(seq)+f"\nunit={status}\n").encode())
    published=[]
    read_report(encoded(rows),commit,image,published.append)
    require(published==rows,"report-round-trip")
    published.clear()
    try:
        read_report(encoded(rows,1),commit,image,published.append)
    except ValueError as exc:
        require(str(exc)=="incomplete-report" and rows[-1] not in published,"unit-exit-control")
    else:
        raise AssertionError("failed unit reported success")
    for seq in (rows[:-1],rows[:1]+rows[-1:],rows+["::error::secret"],rows[:1]+['{"event":"private"}']):
        try:
            read_report(encoded(seq),commit,image,lambda s: None)
        except (ValueError,KeyError):
            pass
        else:
            raise AssertionError("malformed report accepted")
    print("PASS complete report round-trip; truncated, forged, extra and invalid records rejected")



def report_controls():
    records = []
    def success():
        for stage in STAGES:
            REPORT.begin(stage)
            REPORT.passed(stage)
        REPORT.cleanup = "unmounted"
    reported_run("a"*40,"20261120.1.0",success,records.append)
    require(json.loads(records[-1])["outcome"] == "pass", "report-positive")
    for code in ("unexpected","incomplete-report"):
        records.clear()
        def fail():
            REPORT.begin("build")
            if code == "unexpected":
                raise ValueError("private detail\n::warning::forged")
        try:
            reported_run("a"*40,"20261120.1.0",fail,records.append)
        except ValueError as exc:
            require(str(exc)=="incomplete-report", "report-negative")
        else:
            raise AssertionError("invalid-success")
        require(json.loads(records[-1])["outcome"]=="incomplete" and
                not any("private detail" in r or "::" in r for r in records), "report-leak")
    print("PASS bounded report, incomplete work, failure exit and untrusted-text suppression")



def supervise():
    import platform
    import shutil
    import tempfile
    REPORT.begin("runner")
    require(os.geteuid() == 0 and platform.machine() == "x86_64" and
            'VERSION_ID="24.04"' in Path("/etc/os-release").read_text().splitlines(), "runner")
    require(not any(p.name not in {"status", "register"} for p in
                    Path("/proc/sys/fs/binfmt_misc").iterdir()), "foreign-loader")
    require(all(shutil.which(cmd) for cmd in ("git", "gpg", "gpgv", "bwrap", "setpriv", "mount",
                "umount", "mkfs.ext4", "readelf", "llvm-objdump-18")), "host-tools")
    mem = next(l for l in Path("/proc/meminfo").read_text().splitlines() if l.startswith("MemAvailable:"))
    require(int(mem.split()[1]) * 1024 >= 8 * GIB and
            shutil.disk_usage("/var/tmp").free >= LIMIT + GIB, "runner-capacity")
    REPORT.passed("runner", available_ram=int(mem.split()[1])*1024, free_disk=shutil.disk_usage("/var/tmp").free)
    REPORT.begin("limits")
    cg = memory_group()
    leaf = cg / "supervisor"
    leaf.mkdir()
    (leaf / "cgroup.procs").write_text(str(os.getpid()))
    (cg / "cgroup.subtree_control").write_text("+memory")
    with tempfile.TemporaryDirectory(dir="/var/tmp") as tmp:
        volume = Path(tmp) / "volume"
        volume.mkdir()
        with (Path(tmp) / "bounded.ext4").open("xb") as backing:
            os.posix_fallocate(backing.fileno(), 0, LIMIT)
            file = backing.name
            command("mkfs.ext4", "-q", "-F", "-m", "0", file)
            command("mount", "-o", "loop,nosuid,nodev", file, str(volume))
            Path(file).unlink()
            try:
                filesystem_limit(volume)
                REPORT.passed("limits")
                REPORT.begin("host-runtime")
                empty = volume / "empty"
                empty.mkdir()
                command("mount", "--make-rprivate", "/")
                transient = volume / "system-tmp"
                transient.mkdir(mode=0o700)
                command("mount", "--bind", str(transient), "/tmp")
                host_runtime(volume)
                REPORT.passed("host-runtime")
                for name, uid in (("preflight", 61001), ("control-net",61001), ("control-filter",61001), ("build", 61001), ("inspect", 61002)):
                    REPORT.begin("distribution" if name == "build" else name)
                    out = volume / name
                    out.mkdir(mode=0o700)
                    os.chown(out, uid, uid)
                    command("mount", "--bind", str(out), str(out))
                    command("mount", "-o", "remount,bind,noexec,nosuid,nodev", str(out))
                    if name == "build":
                        inputs = acquire(volume)
                        REPORT.passed("installed-inputs")
                        REPORT.begin("release-sources")
                        release_sources(volume, inputs)
                        (inputs / "probe.rs").write_text(PROBE)
                        REPORT.passed("release-sources")
                        REPORT.begin("build")
                    peak = run_cage(volume, cg, name, uid, inputs if name in ("build","inspect") else empty, out)
                    REPORT.passed(name,peak_memory=peak)
                    if name == "build":
                        REPORT.begin("seal")
                        for file_name in ("libprobe.so", "probe.map"):
                            artifact = out / file_name
                            st = artifact.lstat()
                            require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
                                    0 < st.st_size <= 128 << 20, "output-type")
                            os.chown(artifact, 0, 0)
                            artifact.chmod(0o444)
                        os.chown(out, 0, 0)
                        out.chmod(0o555)
                        REPORT.passed("seal")
                REPORT.begin("resource-events")
                events = dict(line.split() for line in (cg / "memory.events").read_text().splitlines())
                require(int(events["oom"]) == 0 and int(events["max"]) == 0 and
                        int((cg / "memory.peak").read_text()) <= 8 * GIB, "aggregate-memory-events")
                REPORT.passed("resource-events", peak_memory=int((cg / "memory.peak").read_text()))
            except Exception as error:
                if REPORT.failed != (REPORT.active,safe_reason(error)):
                    REPORT.failure(error)
                raise
            finally:
                REPORT.begin("cleanup")
                if os.path.ismount("/tmp") and os.stat("/tmp").st_dev == volume.stat().st_dev:
                    command("umount", "/tmp")
                command("umount", "--recursive", str(volume))
                require(not os.path.ismount(volume), "volume-cleanup")
                REPORT.cleanup = "unmounted"
                REPORT.passed("cleanup")



def host_runtime(volume):
    """Stage the approved runner's userspace on the same volume as all other inputs."""
    import re
    import shutil
    root = volume / "host-usr"
    root.mkdir()
    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    require(version == "python3.12", "host-python")
    library = Path("/usr/lib") / version
    shutil.copytree(library, root / "lib" / version, symlinks=False,
                    ignore=shutil.ignore_patterns("__pycache__", "site-packages", "dist-packages",
                                                  "test", "tests", "ensurepip", "idlelib"))
    def logical(path):
        parts = path.parts
        require(path.is_absolute() and parts[1] in {"usr","lib","lib64","bin"}, "host-file")
        return root.joinpath(*(parts[2:] if parts[1] == "usr" else parts[1:]))
    def stage(path):
        out = logical(path)
        src = path.resolve(strict=True)
        require(src.is_file() and src.is_relative_to("/usr"), "host-origin")
        out.parent.mkdir(parents=True, exist_ok=True)
        if not out.exists():
            shutil.copyfile(src, out)
            out.chmod(0o555 if src.stat().st_mode & 0o111 else 0o444)
        return src
    files = list((library/"lib-dynload").glob("*.so"))
    for name in ("python3","bash","setpriv","ar","readelf","llvm-objdump-18","env","dirname","readlink","realpath"):
        files.append(Path("/usr/bin")/name)
    for name in ("libseccomp.so.2","libgcc_s.so.1","libstdc++.so.6","libz.so.1","libtinfo.so.6","libzstd.so.1"):
        files.append(Path("/usr/lib/x86_64-linux-gnu") / name)
    for file in files:
        src = stage(file)
        # Only independently installed runner objects are passed to ldd.
        output = command("ldd", str(src), output=True).decode()
        require("not found" not in output, "host-library")
        for dependency in re.findall(r"(?:=>\s+|^\s*)(/[^\s]+)\s+\(0x[0-9a-f]+\)",output,re.M):
            stage(Path(dependency))
    return root


def watchdog(process, seconds, terminate):
    import time
    end = time.monotonic() + seconds
    try:
        return process.wait(timeout=max(0, end-time.monotonic()))
    except subprocess.TimeoutExpired:
        terminate()
        process.wait(timeout=5)
        raise ValueError("supervisor-deadline") from None


def extra_controls():
    import io
    import tempfile
    from types import SimpleNamespace
    from unittest.mock import patch
    def reject(fn, message):
        try:
            fn()
        except ValueError as failure:
            require(str(failure) == message, "wrong-rejection")
        else:
            raise AssertionError("accepted-" + message)
    network_identity("child","parent","header\n")
    reject(lambda: network_identity("parent","parent","header\n"),"network-namespace")
    reject(lambda: network_identity("child","parent","header\nroute\n"),"network-namespace")
    import errno
    from unittest.mock import Mock
    denied = Mock(side_effect=PermissionError(errno.EPERM, "denied"))
    socket_denial(denied)
    reject(lambda: socket_denial(Mock()), "network-filter")
    good = "[GNUPG:] VALIDSIG " + PRIMARY + " 2026-11-12 1 0 4 0 1 10 00 " + PRIMARY
    gpg_status(good, 0)
    reject(lambda: gpg_status(good, 1), "signature-status")
    reject(lambda: gpg_status(good + "\n[GNUPG:] EXPKEYSIG x", 0), "signature-status")
    reject(lambda: gpg_status(good + "\n" + good, 0), "primary-signer")
    reject(lambda: gpg_status(good.replace(PRIMARY, "F"*40), 0), "primary-signer")
    require(portable("safe/file").parts == ("safe","file"),"portable-control")
    for name in ("../x","/abs","bad//name","bad\\name"):
        reject(lambda: portable(name), "archive-path")
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        (root/"memory.max").write_text(str(8*GIB))
        (root/"memory.swap.max").write_text("0")
        memory_bounds(root)
        for file,value in (("memory.max","max"),("memory.swap.max","1")):
            p=root/file
            saved=p.read_text()
            p.write_text(value)
            reject(lambda: memory_bounds(root),"memory-limit")
            p.write_text(saved)
        with patch.object(os,"statvfs",create=True,return_value=SimpleNamespace(f_blocks=LIMIT,f_frsize=1)):
            filesystem_limit(tmp)
        with patch.object(os,"statvfs",create=True,return_value=SimpleNamespace(f_blocks=LIMIT+1,f_frsize=1)):
            reject(lambda: filesystem_limit(tmp),"storage-limit")
        normal=root/"fixture.zip"
        with zipfile.ZipFile(normal,"w") as arc:
            arc.writestr("valid/file",b"ok")
        extract(normal,root/"normal")
        require((root/"normal/valid/file").read_bytes()==b"ok","archive-control")
        bad=root/"bad.zip"
        with zipfile.ZipFile(bad,"w") as arc:
            arc.writestr("../outside",b"x")
        reject(lambda: extract(bad,root/"bad"),"archive-path")
    with subprocess.Popen([sys.executable,"-IB","-c","import time; time.sleep(10)"]) as child:
        reject(lambda: watchdog(child,0.1,child.kill),"supervisor-deadline")
    print("PASS signature, archive, memory, storage, namespace, socket and watchdog controls")



if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == 'supervise':
        reported_run(sys.argv[2],sys.argv[3],supervise,lambda row: print(row,flush=True))
    elif len(sys.argv) == 4 and sys.argv[1] == 'read-report':
        try:
            read_report(sys.stdin.buffer,sys.argv[2],sys.argv[3],print)
        except Exception:
            print("FAIL incomplete or invalid evidence; successful cleanup and experiment cannot be inferred")
            raise SystemExit(1) from None
    elif len(sys.argv) == 5 and sys.argv[1] == 'worker':
        try:
            worker(sys.argv[2],int(sys.argv[3]),sys.argv[4])
        except Exception as error:
            raise SystemExit(32 + WORKER_REASONS.index(safe_reason(error))) from None
    elif sys.argv[1:] == ['--self-test']:
        identity_controls()
        extra_controls()
        report_controls()
        reader_controls()
    elif len(sys.argv) == 3 and sys.argv[1] == '--verify-source-trees':
        print(verify_sources(Path(sys.argv[2])))
    elif sys.argv[1:] == ['--show-probe']:
        print(PROBE, end='')
    elif sys.argv[1:] == ['--show-recipe']:
        print(RECIPE, end='')
    else:
        raise SystemExit('unknown mode')
