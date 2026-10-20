#!/usr/bin/env python3
"""Cross-build/inspect dormant AArch64 bytes, or run syscall-MODELED host controls.

Never loads the Android library, installs a filter, or runs an Android process.
Python standard library only; existing NDK r28c, no downloads.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "android/research/seccomp-bootstrap/bootstrap.c"
MODEL = SOURCE.with_name("model-test.c")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(argv):
    r = subprocess.run([str(a) for a in argv], capture_output=True, text=True, timeout=45)
    need(r.returncode == 0, f"tool failed ({r.returncode}): {r.stderr}")
    return r.stdout


def sections(data):
    need(data[:7] == b"\x7fELF\x02\x01\x01", "ELF64 little endian")
    h = struct.unpack_from("<16sHHIQQQIHHHHHH", data)
    need(h[1] == 3 and h[2] == 183 and h[4] == 0, "AArch64 shared library, no entry")
    need(h[11] == 64 and 0 < h[12] < 100, "section table")
    table = [struct.unpack_from("<IIQQQQIIQQ", data, h[6] + 64*i) for i in range(h[12])]
    strings = table[h[13]]
    names = data[strings[4]:strings[4]+strings[5]]
    return {names[s[0]:].split(b"\0", 1)[0].decode():
            (s, data[s[4]:s[4]+s[5]]) for s in table}


def evaluate(code, arch, number, arg):
    packet = struct.pack("<IIQQQQQQQ", number, arch, 0, arg, 0, 0, 0, 0, 0)
    pc = acc = 0
    for _ in range(64):
        need(0 <= pc < len(code), "BPF jump outside filter")
        op, yes, no, k = code[pc]
        pc += 1
        if op == 0x20:
            need(k % 4 == 0 and k <= len(packet)-4, "BPF load")
            acc = struct.unpack_from("<I", packet, k)[0]
        elif op == 0x15:
            pc += yes if acc == k else no
        elif op == 0x06:
            return k
        else:
            raise ValueError("unexpected BPF instruction")
    raise ValueError("BPF did not terminate")


def oracle(code):
    # Independent numeric ABI/spec, not parsed from C constants or emitted policy.
    marker = 0x5044564150524f42
    cases = 0
    for arch in (0xc00000b7, 0x40000028, 0xc000003e, 0):
        for nr in list(range(512)) + [0xffffffff, 0x400000ac]:
            for arg in (0, marker, marker ^ 1, marker ^ (1 << 32), 0xffffffffffffffff):
                expected = 0x80000000 if arch != 0xc00000b7 else (
                    0x5000d if nr == 172 and arg == marker else 0x7fff0000)
                need(evaluate(code, arch, nr, arg) == expected, "filter semantics mismatch")
                cases += 1
    return cases


def dormant():
    # Independent build/source inventory: the fixture must have NO application reference.
    paths = list((ROOT / "android/gate0-harness/src").rglob("*"))
    paths += list((ROOT / "android").glob("*.gradle"))
    paths += [ROOT / "android/gate0-harness/build.gradle"]
    for p in paths:
        if p.is_file():
            need(not re.search(r"pdva_bootstrap|seccomp.bootstrap|research[/\\]", p.read_text()),
                 "dormant fixture referenced by app: " + p.name)
    source = SOURCE.read_text()
    # Complements imported-symbol and exact raw syscall-site review below.
    need(not re.search(r"\b(fork|vfork|clone|clone3|execve|execveat|dlopen|system|popen)\s*\(", source),
         "forbidden process/loader call")
    numbers = re.findall(r"syscall\(\s*(__NR_\w+)", source)
    need(sorted(numbers) == sorted(["__NR_getpid", "__NR_getpid", "__NR_gettid", "__NR_seccomp"]),
         "unexpected raw syscall sites")
    need(source.count("syscall(") == len(numbers), "indirect raw syscall number")
    print("PASS: dormant source/build reachability and fixed syscall inventory (static)")


def cross(ndk):
    need("Pkg.Revision = 28.2.13676358" in (ndk / "source.properties").read_text(), "NDK pin")
    platform = "windows-x86_64" if os.name == "nt" else "linux-x86_64"
    bins = ndk / "toolchains/llvm/prebuilt" / platform / "bin"
    suffix = ".exe" if os.name == "nt" else ""
    compiler = bins / ("clang" + suffix)
    readelf = bins / ("llvm-readelf" + suffix)
    print("Compiler SHA256=" + hashlib.sha256(compiler.read_bytes()).hexdigest())
    print(run([compiler, "--version"]).splitlines()[0])
    with tempfile.TemporaryDirectory(prefix="pdva-bootstrap-") as directory:
        output = Path(directory) / "bootstrap.so"
        run([compiler, "--target=aarch64-linux-android30", "-std=c11", "-O2",
             "-Wall", "-Wextra", "-Werror", "-fPIC", "-shared", "-nostartfiles",
             "-mno-outline-atomics", "-nodefaultlibs",
             "-fvisibility=hidden", "-fstack-protector-strong",
             "-Wl,-z,relro,-z,now,-z,noexecstack,-z,max-page-size=16384",
             "-Wl,--no-undefined", SOURCE, "-lc", "-o", output])
        data = output.read_bytes()
        parts = sections(data)
        need(not any(name in parts for name in (".init", ".init_array", ".preinit_array", ".fini_array")),
             "unexpected load-time executable hook")
        dynamic = list(struct.iter_unpack("<qQ", parts[".dynamic"][1]))
        strings = parts[".dynstr"][1]
        needed = [strings[val:].split(b"\0", 1)[0] for tag, val in dynamic if tag == 1]
        need(needed == [b"libc.so"], "unexpected direct dependency graph")
        need(not any(tag in (12, 13, 25, 26, 32) for tag, _ in dynamic), "dynamic constructor hook")
        need(any(tag == 30 and val & 8 for tag, val in dynamic), "immediate binding required")
        # ELF load permissions and alignment, independent of linker arguments.
        h = struct.unpack_from("<16sHHIQQQIHHHHHH", data)
        segments = [struct.unpack_from("<IIQQQQQQ", data, h[5]+i*h[9]) for i in range(h[10])]
        need(any(s[0] == 0x6474e552 for s in segments), "RELRO absent")
        need(any(s[0] == 0x6474e551 and not s[1] & 1 for s in segments), "nonexec stack absent")
        for s in segments:
            if s[0] == 1:
                need(s[1] & 3 != 3 and s[7] >= 16384, "W+X or alignment")
        imports, exports = set(), set()
        for name, info, other, index, value, size in struct.iter_unpack("<IBBHQQ", parts[".dynsym"][1]):
            symbol = strings[name:].split(b"\0", 1)[0].decode()
            if symbol:
                (imports if index == 0 else exports).add(symbol)
        need(exports == {"pdva_bootstrap"}, "unexpected export/entry")
        need(imports == {"__errno", "__stack_chk_fail", "clock_gettime", "geteuid", "getuid",
                         "nanosleep", "prctl", "pthread_create", "pthread_join", "syscall"},
             "unexpected native imports: " + repr(imports))
        code = list(struct.iter_unpack("<HBBI", parts[".pdva_filter"][1]))
        cases = oracle(code)
        # Deliberate independent byte mutations: weaken syscall and both argument halves,
        # wrong errno, wrong audit architecture; each must be rejected by the numeric oracle.
        for index, field, replacement in ((4, 3, 173), (6, 2, 0), (8, 2, 0), (9, 3, 0x50001), (1, 3, 0xc000003e)):
            changed = [list(row) for row in code]
            changed[index][field] = replacement
            try:
                oracle(changed)
            except ValueError:
                pass
            else:
                raise ValueError("filter mutant escaped independent oracle")
        print(run([readelf, "-d", output]))
        print("Filter bytes=" + parts[".pdva_filter"][1].hex())
        print("ELF SHA256=" + hashlib.sha256(data).hexdigest())
        print(f"PASS: compiled AArch64 BPF vectors={cases}, semantic mutants=5; NOT kernel execution")
        print("PASS: no ELF constructors/entry; only libc.so; exact imports/exports; W^X/RELRO/NOW")


def model():
    need(sys.platform == "linux", "Host modeled execution requires Linux; no skip/pass")
    with tempfile.TemporaryDirectory(prefix="pdva-bootstrap-model-") as directory:
        directory = Path(directory)
        source = SOURCE.read_text()
        for mutant in (False, True):
            body = source
            if mutant:
                needle = "if (result.install != 0)"
                need(body.count(needle) == 1, "mutation anchor")
                body = body.replace(needle, "if (0)")
            (directory / "bootstrap.c").write_text(body)
            (directory / "model-test.c").write_text(MODEL.read_text())
            output = directory / "model"
            run(["cc", "-std=c11", "-O0", "-Wall", "-Wextra", "-Werror", "-pthread",
                 directory / "model-test.c", "-o", output])
            for case in ((3, 4) if mutant else range(9)):
                r = subprocess.run([str(output), str(case)], capture_output=True, text=True, timeout=6)
                rejects = mutant and case in (3, 4)
                need(r.returncode == (42 if rejects else 0) and r.stdout ==
                     ("REJECTED: payload after failed install\n" if rejects else "PASS: modeled contract\n")
                     and not r.stderr, f"modeled case {case} mutant={mutant}: {r}")
        print("PASS: source-executed modeled controls=9; failed-install continuation mutants=2")
        print("No real seccomp call executed; pthreads real; NOT Linux kernel or Android enforcement")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ndk", type=Path)
    group.add_argument("--model", action="store_true")
    args = parser.parse_args()
    dormant()
    print("Source SHA256=" + hashlib.sha256(SOURCE.read_bytes()).hexdigest())
    cross(args.ndk) if args.ndk else model()


if __name__ == "__main__":
    main()
