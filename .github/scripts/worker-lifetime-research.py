#!/usr/bin/env python3
"""Bounded real Linux controls; --check-oracle is platform-neutral fixture logic."""
import hashlib
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile


SOURCE = Path(__file__).with_name("worker-lifetime.c")
CASES = {"exit": ("exit42", 0), "term": ("SIGKILL", 1), "fd": ("exit0", 1)}


def expected(case):
    status, observed = CASES[case]
    return (f"EVIDENCE:{case} status={status} observed={observed} "
            "identity=pidfd reaped=1 echild=1 eof=1\n")


def accept(case, mutant, code, stdout, stderr):
    """Exact independent oracle: never accept generic nonzero or absent evidence."""
    diagnostic = f"REJECTED:{case}:cleanup-verified\n" if mutant else ""
    if (code, stdout, stderr) != (42 if mutant else 0, expected(case), diagnostic):
        raise ValueError(f"Rejected invalid {case} result (mutant={mutant}, status={code})")


def check_oracle():
    count = 0
    for case in CASES:
        for mutant in (False, True):
            code = 42 if mutant else 0
            out = expected(case)
            err = f"REJECTED:{case}:cleanup-verified\n" if mutant else ""
            accept(case, mutant, code, out, err)
            # Modeled invalid observations only. Never crash or abandon children.
            invalid = [(code + 1, out, err), (-6, out, err), (124, out, err),
                       (77, out, err), (None, out, err), (code, "", err),
                       (code, out + "EXTRA\n", err), (code, out, err + "EXTRA\n"),
                       (code, out.replace("reaped=1", "reaped=0"), err),
                       (code, out.replace("echild=1", "echild=0"), err),
                       (code, out.replace("identity=pidfd", "identity=unknown"), err),
                       (code, out.replace("eof=1", "eof=0"), err),
                       (code, out.replace("status=", "status=wrong"), err)]
            if mutant:
                invalid.extend([(0, out, err), (42, out, ""),
                                (42, out, f"REJECTED:{case}:cleanup-UNPROVEN\n")])
            for result in invalid:
                try:
                    accept(case, mutant, *result)
                except ValueError:
                    count += 1
                else:
                    raise RuntimeError("Result oracle accepted a false observation")
    print(f"PASS: modeled oracle rejection controls={count}")


def run():
    check_oracle()
    if sys.argv[1:] == ["--check-oracle"]:
        return
    if sys.argv[1:]:
        raise RuntimeError("Only --check-oracle or no arguments are supported")
    if sys.platform != "linux":
        raise RuntimeError("Real process controls require Linux; no skip/pass fallback")
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    compiler = shutil.which("cc")
    if not compiler:
        raise RuntimeError("Missing existing host C compiler")
    print(f"Linux release={platform.release()} machine={platform.machine()}", flush=True)
    print(f"Source SHA256={hashlib.sha256(SOURCE.read_bytes()).hexdigest()}", flush=True)
    # Compiler and libc are existing CI infrastructure, not pinned product inputs.
    subprocess.run([compiler, "--version"], check=True, timeout=5)
    with tempfile.TemporaryDirectory(prefix="pdva-lifetime-") as directory:
        root = Path(directory)
        os.chmod(root, 0o700)
        binary = root / "worker-lifetime"
        subprocess.run([compiler, "-std=c11", "-O0", "-Wall", "-Wextra", "-Werror",
                        str(SOURCE), "-o", str(binary)], check=True, timeout=30,
                       stdin=subprocess.DEVNULL, close_fds=True)
        for case in CASES:
            for mutant in (False, True):
                case_dir = root / f"{case}-{mutant}"
                case_dir.mkdir(mode=0o700)
                # No shell, network, imported binary, inherited private environment,
                # or caller-specified operation. Each C controller owns one child.
                result = subprocess.run(
                    [str(binary), case, "mutant" if mutant else "positive"],
                    cwd=case_dir, env={"LANG": "C"}, stdin=subprocess.DEVNULL,
                    capture_output=True, text=True, timeout=15, close_fds=True,
                    check=False,
                )
                # No expected-failure catch around execution. Timeout/compile error
                # aborts the entire runner; no subsequent adversarial cases run.
                try:
                    accept(case, mutant, result.returncode, result.stdout, result.stderr)
                except ValueError:
                    print(f"FAIL: {case} mutant={mutant} exact-status={result.returncode}",
                          file=sys.stderr)
                    for line in result.stderr.splitlines()[:4]:
                        if re.fullmatch(r"FAIL:[a-z-]+ cleanup=(reaped|UNPROVEN|no-child)", line):
                            print(line, file=sys.stderr)
                    raise
                if list(case_dir.iterdir()):
                    raise RuntimeError("Unexpected synthetic fixture residue")
                print(result.stdout, end="")
                print(result.stderr, end="")
                print(f"PASS: {case} {'mutation rejected (42)' if mutant else 'positive (0)'}", flush=True)
    print("PASS: Linux lifetime controls=3 mutations=3 all-owned-children-reaped")


if __name__ == "__main__":
    try:
        run()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        # Do not dump argv, host paths, or uncontrolled child stderr into public logs.
        print(f"FAIL: lifetime research stopped ({type(error).__name__}); "
              "no later case authorized; incomplete cleanup is NOT success", file=sys.stderr)
        sys.exit(1)
