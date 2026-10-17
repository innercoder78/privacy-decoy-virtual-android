#!/usr/bin/env python3
"""Exact independent result oracle for disposable Linux seccomp research."""
import hashlib
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile


SOURCE = Path(__file__).with_name("seccomp-process.c")
EXPECTED = {
    "tsync": (0, "EVIDENCE:tsync nnp=1 install=0 pre=EPERM post=EPERM clone3=ENOSYS "
              "exec=EPERM reset=EINVAL allow-stack=still-denied retained=PDVA probes=5 "
              "created=0 worker=exit0 identity=pidfd cleanup=verified controller=unchanged\n", ""),
    "thread-only": (42, "EVIDENCE:thread-only nnp=1 install=0 main=EPERM peer=process-created probes=2 "
                    "worker=exit42 probe=exit95 identity=pidfd cleanup=verified controller=unchanged\n",
                    "REJECTED:thread-only-is-all-threads:cleanup-verified\n"),
    "invalid-install": (0, "EVIDENCE:invalid-install nnp=1 install=EINVAL terminal=1 probes=0 "
                        "worker=exit43 identity=pidfd cleanup=verified controller=unchanged\n", ""),
    "divergent-tsync": (0, "EVIDENCE:divergent-tsync nnp=1 install=peer-tid terminal=1 probes=0 "
                        "worker=exit43 identity=pidfd cleanup=verified controller=unchanged\n", ""),
}


def accept(case, status, out, err):
    if (status, out, err) != EXPECTED[case]:
        raise ValueError(f"Rejected {case} status={status}; exact receipts required")


def check_oracle():
    rejected = 0
    for case, (status, out, err) in EXPECTED.items():
        accept(case, status, out, err)
        invalid = [(None, out, err), (-9, out, err), (-31, out, err), (124, out, err),
                   (77, out, err), (status + 1, out, err), (status, "", err),
                   (status, out + "EXTRA\n", err), (status, out, err + "EXTRA\n")]
        for field in out.strip().split()[1:]:
            invalid.extend([(status, out.replace(field, ""), err),
                            (status, out.replace(field, field + "-wrong"), err)])
        # Incorrect assertions: attempted == installed; ENOSYS == EPERM;
        # unfiltered peer == all threads; created process == created thread;
        # normal exit == SIGKILL; absent descendants == no new child.
        invalid.extend((status, out.replace(a, b), err) for a, b in (
            ("install=0", "install=attempted"), ("pre=EPERM", "pre=ENOSYS"),
            ("clone3=ENOSYS", "clone3=EPERM"), ("peer=process-created", "peer=thread-created"),
            ("created=0", "descendants=0"), ("worker=exit0", "worker=SIGKILL"),
            ("install=peer-tid", "install=0"), ("probes=0", "probes=1"),
        ) if a in out)
        if case == "thread-only":
            invalid.extend([(0, out, err), (42, out, ""), (42, out, "REJECTED\n")])
        for fixture in invalid:
            try:
                accept(case, *fixture)
            except ValueError:
                rejected += 1
            else:
                raise RuntimeError("Oracle accepted an incorrect assertion fixture")
    # A plausible successful-installation report cannot stand in for another case.
    for case in EXPECTED:
        for other, fixture in EXPECTED.items():
            if other != case:
                try:
                    accept(case, *fixture)
                except ValueError:
                    rejected += 1
                else:
                    raise RuntimeError("Oracle accepted evidence from another case")
    print(f"PASS: seccomp modeled invalid fixtures rejected={rejected}; valid fixtures=4")


def run():
    check_oracle()
    if sys.argv[1:] == ["--check-oracle"]:
        return
    if sys.argv[1:]:
        raise RuntimeError("Only --check-oracle or no arguments are supported")
    if sys.platform != "linux" or platform.machine() != "x86_64":
        raise RuntimeError("Requires native Linux x86_64; unsupported is failure, not a skip")
    if os.getuid() == 0 or os.geteuid() == 0:
        raise RuntimeError("Unprivileged execution required")
    compiler = shutil.which("cc")
    if compiler is None:
        raise RuntimeError("Existing host compiler required")
    flags = ["-std=c11", "-O0", "-Wall", "-Wextra", "-Werror", "-pthread"]
    print(f"Linux release={platform.release()} machine={platform.machine()} libc={platform.libc_ver()}", flush=True)
    print(f"Source SHA256={hashlib.sha256(SOURCE.read_bytes()).hexdigest()}", flush=True)
    subprocess.run([compiler, "--version"], check=True, timeout=5)
    with tempfile.TemporaryDirectory(prefix="pdva-seccomp-") as directory:
        root = Path(directory)
        os.chmod(root, 0o700)
        binary = root / "seccomp-process"
        subprocess.run([compiler, *flags, str(SOURCE), "-o", str(binary)],
                       stdin=subprocess.DEVNULL, close_fds=True, check=True, timeout=30)
        print(f"Build flags={' '.join(flags)} binary SHA256={hashlib.sha256(binary.read_bytes()).hexdigest()}", flush=True)
        for case in EXPECTED:
            cwd = root / case
            cwd.mkdir(mode=0o700)
            result = subprocess.run([str(binary), case], cwd=cwd, env={"LANG": "C"},
                                    stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                    close_fds=True, timeout=15, check=False)
            # No timeout/compile/crash expected-failure catch. Any uncertainty
            # ends the whole suite; never start another process scenario.
            try:
                accept(case, result.returncode, result.stdout, result.stderr)
            except ValueError:
                print(f"FAIL: case={case} exact-status={result.returncode}", file=sys.stderr)
                for line in result.stderr.splitlines()[:2]:
                    if re.fullmatch(r"FAIL:[a-z0-9-]+ cleanup=(verified|UNPROVEN)", line):
                        print(line, file=sys.stderr)
                    elif re.fullmatch(r"OBSERVED:worker wait=\d+ exit=-?\d+ signal=\d+ install-tried=[01] install-result=-?\d+ install-errno=\d+", line):
                        print(line, file=sys.stderr)
                raise
            if list(cwd.iterdir()):
                raise RuntimeError("Unexpected research residue")
            print(result.stdout, end="")
            print(result.stderr, end="")
            print(f"PASS: {case} exact-status={result.returncode}", flush=True)
    print("PASS: seccomp real cases=4 all-owned-children-reaped; not Android evidence")


if __name__ == "__main__":
    try:
        run()
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print(f"FAIL: seccomp research stopped ({type(error).__name__}); "
              "no later case authorized; incomplete cleanup is NOT success", file=sys.stderr)
        sys.exit(1)
