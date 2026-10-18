#!/usr/bin/env python3
"""Independent supervision/state oracle for fixed Linux revocation controls.

--check-oracle exercises modeled acceptance only, including on Windows.
No argument runs every real case and semantic mutant; unavailable is failure.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import select
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time

SOURCE = Path(__file__).with_name("revocation-control.c")
FLAGS = ["-std=c11", "-O0", "-Wall", "-Wextra", "-Werror"]
STATUS = {1: "OK", 2: "DENIED_REVOKED", 3: "DENIED_EPOCH",
          4: "DENIED_INSTANCE", 5: "DENIED_REPLAY", 6: "DENIED_STATE",
          7: "UNKNOWN_TRANSPORT"}
EXPECTED = {
    "mapping": ["STATE 80 0", "WROTE_90", "STATE 90 0"],
    "mediated": ["OK 80", "STATE 81 1", "REVOKED", "DENIED_REVOKED 0", "STATE 81 1"],
    "disclosure": ["OK 80", "REVOKED", "DENIED_REVOKED 0", "COPY 1 80", "STATE 81 1"],
    "inflight": ["AUTHORIZED_PENDING", "STATE 80 0", "REVOCATION_PENDING",
                 "ABORTED", "DENIED_REVOKED 0", "STATE 80 0"],
    "epoch": ["DENIED_EPOCH 0", "STATE 80 0"],
    "instance": ["DENIED_INSTANCE 0", "STATE 80 0"],
    "replay": ["OK 80", "DENIED_REPLAY 0", "STATE 81 1"],
    "missing": ["STATE_MISSING", "DENIED_STATE 0", "STATE 80 0"],
    "loss": ["TRANSPORT_LOST", "UNKNOWN_TRANSPORT 0", "LOCKED_UNKNOWN", "STATE 80 0"],
    "uncertain": ["AUTHORIZED_PENDING", "OUTCOME_UNACKNOWLEDGED",
                  "UNKNOWN_TRANSPORT 0", "LOCKED_UNKNOWN", "STATE 81 1"],
}
# These are alternate *runtime effects*, never merely alternate exit codes.
MUTANTS = {
    "mapping": (1, ["STATE 80 0", "WROTE_90", "STATE 80 0"]),
    "mediated": (2, ["OK 80", "STATE 81 1", "REVOKED", "OK 81", "STATE 82 2"]),
    "disclosure": (3, ["OK 80", "REVOKED", "DENIED_REVOKED 0", "COPY 0 0", "STATE 81 1"]),
    "inflight": (4, ["AUTHORIZED_PENDING", "STATE 80 0", "REVOCATION_PENDING",
                    "COMMITTED", "OK 80", "STATE 81 1"]),
    "epoch": (5, ["OK 80", "STATE 81 1"]),
    "instance": (6, ["OK 80", "STATE 81 1"]),
    "replay": (7, ["OK 80", "OK 81", "STATE 82 2"]),
    "missing": (8, ["STATE_MISSING", "OK 80", "STATE 81 1"]),
    "loss": (9, ["TRANSPORT_LOST", "UNKNOWN_TRANSPORT 0", "UNKNOWN_TRANSPORT 0", "STATE 80 0"]),
    "uncertain": (9, ["AUTHORIZED_PENDING", "OUTCOME_UNACKNOWLEDGED",
                      "UNKNOWN_TRANSPORT 0", "UNKNOWN_TRANSPORT 0", "STATE 81 1"]),
}


def receipt(case, observations):
    roles = ["observer", "mapper"] if case == "mapping" else ["observer", "owner", "worker"]
    return {"observations": observations, "exits": {role: 0 for role in roles},
            "pidfds": len(roles), "reaped": len(roles), "eof": len(roles),
            "worker_observer_resource_fds_absent": True, "creator_fd_closed": True,
            "residue": False}


def accept(case, result):
    if result != receipt(case, EXPECTED[case]):
        raise ValueError("Exact positive observations and cleanup required")


def accept_mutant(case, result):
    if result != receipt(case, MUTANTS[case][1]):
        raise ValueError("Missing exact semantic mutation or cleanup")
    try:
        accept(case, result)
    except ValueError:
        return
    raise ValueError("Positive oracle accepted mutant")


def check_oracle():
    count = 0
    for case in EXPECTED:
        checks = [(accept, receipt(case, EXPECTED[case]))]
        if case in MUTANTS:
            checks.append((accept_mutant, receipt(case, MUTANTS[case][1])))
        for check, good in checks:
            check(case, good)
            bad = []
            for key in good:
                changed = dict(good)
                del changed[key]
                bad.append(changed)
                changed = dict(good)
                changed[key] = None
                bad.append(changed)
            for index in range(len(good["observations"])):
                changed = dict(good)
                changed["observations"] = list(good["observations"])
                changed["observations"][index] = "MISSING_OR_WRONG"
                bad.append(changed)
            for role in good["exits"]:
                for code in (-9, -6, 1, 42, 77, 124, None):
                    changed = dict(good)
                    changed["exits"] = dict(good["exits"], **{role: code})
                    bad.append(changed)
            for changed in bad:
                try:
                    check(case, changed)
                except ValueError:
                    count += 1
                else:
                    raise RuntimeError("Oracle accepted incomplete/crashed fixture")
    print(f"PASS: modeled revocation oracle rejections={count}; not Linux evidence", flush=True)


class Child:
    def __init__(self, binary, role, fds, group):
        self.role, self.pidfd, self.finished = role, None, False
        self.p = subprocess.Popen([str(binary), role, *map(str, fds)],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, bufsize=0, close_fds=True,
                                  pass_fds=tuple(fds), cwd=group.directory,
                                  env={"LANG": "C"})
        # Register immediately, including pidfd-setup failure cleanup.
        group.children.append(self)
        self.pidfd = os.pidfd_open(self.p.pid)
        self.send("G")

    def send(self, command):
        if len(command) != 1 or os.write(self.p.stdin.fileno(), command.encode("ascii")) != 1:
            raise RuntimeError("Control pipe write failed")

    def line(self):
        deadline = time.monotonic() + 2
        data = bytearray()
        while len(data) < 100:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.p.stdout], [], [], remaining)[0]:
                raise RuntimeError("Timed out: not denial evidence")
            c = os.read(self.p.stdout.fileno(), 1)
            if not c:
                raise RuntimeError("Unexpected EOF")
            if c == b"\n":
                return data.decode("ascii")
            data.extend(c)
        raise RuntimeError("Oversized receipt")

    def expect(self, value):
        if self.line() != value:
            raise RuntimeError("Incorrect protocol receipt")

    def finish(self, stop=True):
        if stop:
            self.send("X")
            if self.role == "owner":
                self.expect("OWNER_STOPPED")
        self.expect("DONE")
        if not select.select([self.pidfd], [], [], 2)[0]:
            raise RuntimeError("Owned child did not terminate")
        if self.p.wait(timeout=1) != 0:
            raise RuntimeError("Unexpected child exit")
        verify_reaped(self.p)
        if os.read(self.p.stdout.fileno(), 101) or os.read(self.p.stderr.fileno(), 101):
            raise RuntimeError("Extra output or diagnostic")
        self.finished = True


def verify_reaped(process):
    try:
        os.waitpid(process.pid, os.WNOHANG)
    except ChildProcessError:
        return
    raise RuntimeError("Expected ECHILD for this owned child")


class Group:
    def __init__(self, directory):
        self.directory, self.children = directory, []

    def cleanup(self):
        errors = []
        for child in self.children:
            try:
                if child.p.returncode is None:
                    try:
                        if child.pidfd is not None:
                            signal.pidfd_send_signal(child.pidfd, signal.SIGKILL)
                        else:
                            # Only this still-owned unreaped direct child; never a
                            # worker-reported PID, scan, process group or descendant.
                            child.p.kill()
                    except ProcessLookupError:
                        pass  # Already exited still requires exact owned wait.
                    child.p.wait(timeout=2)
                verify_reaped(child.p)
            except (OSError, subprocess.SubprocessError, RuntimeError) as error:
                errors.append(type(error).__name__)
            finally:
                for stream in (child.p.stdin, child.p.stdout, child.p.stderr):
                    stream.close()
                if child.pidfd is not None:
                    os.close(child.pidfd)
        if errors:
            raise RuntimeError("Cleanup UNPROVEN; stop all later experiments")


def no_resource_fd(child, identity):
    # Bounded inspection of an owned unreaped process, not PID discovery/scanning.
    if select.select([child.pidfd], [], [], 0)[0]:
        raise RuntimeError("Child exited before authority observation")
    for fd in range(64):
        try:
            st = os.stat(f"/proc/{child.p.pid}/fd/{fd}")
        except FileNotFoundError:
            continue
        if (st.st_dev, st.st_ino) == identity:
            raise RuntimeError("Resource descriptor retained")
    if select.select([child.pidfd], [], [], 0)[0]:
        raise RuntimeError("Child exited during authority observation")


def state(observer):
    observer.send("S")
    return observer.line()


def reply(worker, *, allow_locked=False):
    line = worker.line()
    # Only the post-loss retry can return this non-packet control receipt.
    # A mutant instead returns a normal REPLY packet; normalize it exactly as
    # every other reply before applying the unchanged semantic oracle.
    if allow_locked and line == "LOCKED_UNKNOWN":
        return line
    fields = line.split()
    if len(fields) != 3 or fields[0] != "REPLY":
        raise RuntimeError("Missing worker reply")
    return f"{STATUS[int(fields[1])]} {int(fields[2])}"


def request(worker, owner, command="Q"):
    worker.send(command)
    owner.send("A")
    owner_result = owner.line()
    worker_result = reply(worker)
    if owner_result != ("COMMITTED" if worker_result.startswith("OK ") else "REQUEST_DENIED"):
        raise RuntimeError("Invalid admission result")
    return worker_result


def experiment(case, binary, directory):
    group = Group(directory)
    resource_fd = os.memfd_create("pdva-fixed-synthetic", os.MFD_CLOEXEC)
    endpoints = []
    try:
        os.ftruncate(resource_fd, 4096)
        if os.pwrite(resource_fd, b"\x50\x00", 0) != 2:
            raise RuntimeError("Synthetic initialization failed")
        st = os.fstat(resource_fd)
        identity = (st.st_dev, st.st_ino)
        observer = Child(binary, "observer", [resource_fd], group)
        observer.expect("MAPPED_FD_CLOSED")
        no_resource_fd(observer, identity)
        observations = []
        if case == "mapping":
            worker = Child(binary, "mapper", [resource_fd], group)
            worker.expect("MAPPED_FD_CLOSED")
            no_resource_fd(worker, identity)
            os.close(resource_fd)
            resource_fd = None
            # Both processes' mapping FDs and original creator FD are now closed.
            observations.append(state(observer))
            worker.send("W")
            observations.extend([worker.line(), state(observer)])
        else:
            endpoints = list(socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET))
            owner = Child(binary, "owner", [resource_fd, endpoints[0].fileno()], group)
            owner.expect("OWNER_READY")
            worker = Child(binary, "worker", [endpoints[1].fileno()], group)
            worker.expect("WORKER_READY")
            for endpoint in endpoints:
                endpoint.close()
            endpoints = []
            no_resource_fd(worker, identity)
            # exec + close_fds + only the request socket: no resource mapping
            # inherited either. Same-UID bypass resistance is NOT established.
            os.close(resource_fd)
            resource_fd = None
            if case in ("mediated", "disclosure", "replay"):
                observations.append(request(worker, owner))
            if case in ("mediated", "disclosure"):
                if case == "mediated":
                    observations.append(state(observer))
                owner.send("V")
                observations.extend([owner.line(), request(worker, owner)])
                if case == "disclosure":
                    worker.send("K")
                    observations.append(worker.line())
            elif case in ("inflight", "uncertain"):
                worker.send("Q")
                owner.send("H")
                observations.append(owner.line())
                if case == "inflight":
                    observations.append(state(observer))
                    owner.send("V")
                    observations.append(owner.line())
                    owner.send("C")
                else:
                    owner.send("U")
                observations.extend([owner.line(), reply(worker)])
                if case == "uncertain":
                    owner.finish(stop=False)
            elif case in ("epoch", "instance", "replay"):
                observations.append(request(worker, owner, {"epoch": "E", "instance": "I", "replay": "P"}[case]))
            elif case == "missing":
                owner.send("M")
                observations.extend([owner.line(), request(worker, owner)])
            elif case == "loss":
                owner.send("L")
                observations.append(owner.line())
                owner.finish(stop=False)
                worker.send("Q")
                observations.append(reply(worker))
            else:
                raise RuntimeError("Unknown scenario")
            if case in ("loss", "uncertain"):
                worker.send("Q")
                observations.append(reply(worker, allow_locked=True))
            observations.append(state(observer))
        for child in reversed(group.children):
            if not child.finished:
                child.finish()
        # Values are recorded only after each real zero exit, ECHILD and EOF.
        result = {"observations": observations,
                  "exits": {c.role: c.p.returncode for c in group.children},
                  "pidfds": sum(c.pidfd is not None for c in group.children),
                  "reaped": sum(c.finished for c in group.children),
                  "eof": sum(c.finished for c in group.children),
                  "worker_observer_resource_fds_absent": True, "creator_fd_closed": True,
                  "residue": bool(list(directory.iterdir()))}
    finally:
        try:
            group.cleanup()
        finally:
            for endpoint in endpoints:
                endpoint.close()
            if resource_fd is not None:
                os.close(resource_fd)
    return result


def run():
    check_oracle()
    if sys.argv[1:] == ["--check-oracle"]:
        return
    if sys.argv[1:]:
        raise RuntimeError("Only --check-oracle or no arguments supported")
    if sys.platform != "linux" or platform.machine() != "x86_64":
        raise RuntimeError("Native Linux x86_64 required; no skip/pass fallback")
    if os.getuid() == 0 or os.geteuid() == 0:
        raise RuntimeError("Unprivileged execution required")
    own_status = Path("/proc/self/status").read_text().splitlines()
    for name in ("CapInh", "CapPrm", "CapEff", "CapAmb"):
        values = [line.split()[1] for line in own_status if line.startswith(name + ":")]
        if len(values) != 1 or int(values[0], 16) != 0:
            raise RuntimeError("Capability-free test process required")
    if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
        raise RuntimeError("Stable child identities required")
    import resource
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    signal.pthread_sigmask(signal.SIG_SETMASK, [])
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    for kind, bound in ((resource.RLIMIT_CPU, 10), (resource.RLIMIT_AS, 256 * 1024 * 1024),
                        (resource.RLIMIT_NOFILE, 64), (resource.RLIMIT_FSIZE, 16 * 1024 * 1024)):
        resource.setrlimit(kind, (bound, bound))
    def interrupted(signum, frame):
        raise RuntimeError("Supervisor interrupted; cleanup required")
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGALRM):
        signal.signal(sig, interrupted)
    signal.alarm(120)
    compiler = shutil.which("cc")
    if not compiler:
        raise RuntimeError("Existing C compiler required")
    print(f"Linux={platform.release()} ABI={platform.machine()} libc={platform.libc_ver()} Python={platform.python_version()}", flush=True)
    for source in (SOURCE, Path(__file__)):
        print(f"SOURCE {source.name} SHA256={hashlib.sha256(source.read_bytes()).hexdigest()}", flush=True)
    subprocess.run([compiler, "--version"], check=True, timeout=5)
    with tempfile.TemporaryDirectory(prefix="pdva-revocation-") as directory:
        root = Path(directory)
        os.chmod(root, 0o700)
        binaries = {}
        for mutation in range(10):
            binary = root / f"control-{mutation}"
            subprocess.run([compiler, *FLAGS, f"-DMUTATION={mutation}", str(SOURCE), "-o", str(binary)],
                           check=True, timeout=30, stdin=subprocess.DEVNULL, close_fds=True)
            print(f"BUILD mutation={mutation} flags={' '.join(FLAGS)} SHA256={hashlib.sha256(binary.read_bytes()).hexdigest()}", flush=True)
            binaries[mutation] = binary
        for case in EXPECTED:
            for mutation in ([0, MUTANTS[case][0]] if case in MUTANTS else [0]):
                case_dir = root / f"{case}-{mutation}"
                case_dir.mkdir(mode=0o700)
                result = experiment(case, binaries[mutation], case_dir)
                (accept_mutant if mutation else accept)(case, result)
                print(f"EVIDENCE case={case} mutation={mutation} {json.dumps(result, sort_keys=True)}", flush=True)
                print(f"PASS: {case} {'semantic mutant rejected' if mutation else 'positive'}", flush=True)
                case_dir.rmdir()
    if root.exists():
        raise RuntimeError("Temporary directory cleanup incomplete")
    signal.alarm(0)
    print("PASS: revocation real cases=10 semantic mutants=10; owned processes reaped; temporary files removed", flush=True)


if __name__ == "__main__":
    try:
        run()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError):
        print("FAIL: revocation research stopped; no later experiment; timeout/crash/uncertainty is not denial evidence", file=sys.stderr)
        sys.exit(1)
