#!/usr/bin/env python3
"""Private offline preparation only. No device commands or cleanup authority."""
import argparse
from contextlib import contextmanager, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "android/build/private-readiness"
HEX = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[a-z0-9][a-z0-9-]{0,63}\Z")
PRECONDITIONS = {"offline_only": True, "phone_authorized": False,
                 "cleanup_authority": "none"}


class Rejected(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Rejected(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def identity(value):
    require(isinstance(value, dict) and set(value) == {"source", "apk_sha256", "variant"},
            "Invalid build identity schema")
    require(isinstance(value["source"], str) and
            re.fullmatch(r"[0-9a-f]{40}", value["source"]), "Full source SHA required")
    require(isinstance(value["apk_sha256"], str) and HEX.fullmatch(value["apk_sha256"]),
            "APK SHA-256 required")
    require(value["variant"] in ("debug", "release"), "Invalid variant")
    return value


def receipt(data, build):
    require(isinstance(data, dict) and set(data) == {"build", "validation", "artifacts",
            "validator_sha256", "analyzer_sha256", "source_tree", "scope"},
            "Invalid completion schema")
    require(data["build"] == build and data["scope"] == "offline-inspection-only",
            "Completion identity/scope mismatch")
    require(all(isinstance(data[k], str) and HEX.fullmatch(data[k])
                for k in ("validator_sha256", "analyzer_sha256")) and
            isinstance(data["source_tree"], str) and
            re.fullmatch(r"[0-9a-f]{40}", data["source_tree"]), "Invalid tool/source identity")
    validation = data["validation"]
    require(isinstance(validation, dict) and set(validation) == {"manifest", "native"} and
            validation["manifest"] == "passed" and isinstance(validation["native"], dict) and
            len(validation["native"]) == 3, "Incomplete validation receipt")
    require(isinstance(data["artifacts"], dict) and
            set(data["artifacts"]) == set(validation["native"]), "Artifact identity mismatch")
    for name, item in validation["native"].items():
        require(isinstance(item, dict) and set(item) == {"sha256", "role", "needed"} and
                isinstance(item["sha256"], str) and HEX.fullmatch(item["sha256"]) and
                item["role"] in {"dynamic-PIE", "JNI-shared"} and
                isinstance(item["needed"], list) and item["needed"] and
                all(isinstance(s, str) for s in item["needed"]), "Invalid native receipt")
        local = data["artifacts"][name]
        require(isinstance(local, dict) and set(local) == {"path", "sha256"} and
                isinstance(local["path"], str) and local["path"] and
                local["sha256"] == item["sha256"], "Invalid local native receipt")


def check_id(value):
    require(isinstance(value, str) and ID.fullmatch(value), "Invalid operation/journal ID")
    require(value not in {"con", "prn", "aux", "nul", *["com" + str(n) for n in range(10)],
                          *["lpt" + str(n) for n in range(10)]}, "Reserved Windows name")
    return value


def safe_path(name):
    check_id(name)
    # Refuse junction/symlink redirection out of the designated ignored directory.
    require(STORE.resolve() == Path(os.path.abspath(STORE)), "Redirected journal directory")
    path = STORE / (name + ".jsonl")
    require(not path.is_symlink() and path.resolve().parent == STORE.resolve(),
            "Redirected journal file")
    return path


@contextmanager
def locked(stream):
    """Nonblocking OS lock, automatically released on process death, never stolen."""
    stream.seek(0)
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        yield
    finally:
        stream.seek(0)
        if os.name == "nt":
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def sync(stream):
    stream.flush()
    os.fsync(stream.fileno())


def append(stream, records, kind, operation, data):
    record = {"version": 1, "sequence": len(records),
              "previous": records[-1]["hash"] if records else "0" * 64,
              "kind": kind, "operation": operation, "data": data}
    record["hash"] = digest(canonical(record))
    stream.seek(0, os.SEEK_END)
    stream.write(canonical(record) + b"\n")
    sync(stream)  # Must return successfully before dispatch or any next transition.
    records.append(record)


def decode(raw):
    require(raw and raw.endswith(b"\n"), "Missing/truncated journal; UNKNOWN, stop")
    records = []
    for line in raw.splitlines():
        try:
            record = json.loads(line)
        except (ValueError, UnicodeError) as error:
            raise Rejected("Malformed journal; UNKNOWN, stop") from error
        require(isinstance(record, dict) and set(record) ==
                {"version", "sequence", "previous", "kind", "operation", "data", "hash"},
                "Unknown record schema")
        require(canonical(record) == line, "Noncanonical/duplicate-key journal record")
        supplied = record["hash"]
        body = {k: v for k, v in record.items() if k != "hash"}
        require(type(record["version"]) is int and record["version"] == 1 and
                type(record["sequence"]) is int and record["sequence"] == len(records) and
                record["previous"] == (records[-1]["hash"] if records else "0" * 64) and
                supplied == digest(canonical(body)), "Broken sequence/hash; UNKNOWN, stop")
        records.append(record)
    replay(records)
    return records


def replay(records):
    first = records[0]
    require(first["kind"] == "INIT" and first["operation"] is None and
            isinstance(first["data"], dict) and set(first["data"]) == {"journal", "build"},
            "Missing initialization")
    check_id(first["data"]["journal"])
    identity(first["data"]["build"])
    operations = {}
    for r in records[1:]:
        op, kind, data = r["operation"], r["kind"], r["data"]
        check_id(op)
        if kind == "PREPARED":
            require(op not in operations, "Duplicate operation")
            require(canonical(data) == canonical({"intended_operation": "inspect-apk", "preconditions": PRECONDITIONS}),
                    "Unsupported action/preconditions")
            require(not any(v["state"] in {"IN_PROGRESS", "CLEANUP_UNKNOWN"} for v in operations.values()),
                    "Unresolved prior operation")
            operations[op] = {"state": kind}
        elif kind == "IN_PROGRESS":
            require(op in operations and operations[op]["state"] == "PREPARED" and data == {},
                    "Replay or invalid dispatch")
            require(not any(v["state"] in {"IN_PROGRESS", "CLEANUP_UNKNOWN"}
                            for v in operations.values()), "Unresolved operation blocks dispatch")
            operations[op] = {"state": kind}
        elif kind in {"COMPLETED", "FAILED"}:
            require(op in operations and operations[op]["state"] == "IN_PROGRESS",
                    "Completion without dispatch or replay")
            if kind == "COMPLETED":
                receipt(data, first["data"]["build"])
            else:
                require(data == {"observation": "offline-validation-rejected"}, "Invalid failure")
            operations[op] = {"state": kind, "observation": data}
        elif kind == "CLEANUP_UNKNOWN":
            require(op not in operations and data == {"observation": "external-uncertainty",
                    "phone_authorized": False}, "Invalid external uncertainty")
            operations[op] = {"state": kind}
        else:
            raise Rejected("Unsupported transition; no cleanup-clear or manual completion")
    return operations


def read(path, stream=None):
    if stream is None:
        with path.open("rb") as source:
            raw = source.read()
    else:
        stream.seek(0)
        raw = stream.read()
    records = decode(raw)
    require(records[0]["data"]["journal"] == path.stem, "Journal identity mismatch")
    return records


def initialize(path, build):
    identity(build)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: a crash can leave an empty file; it is never reinitialized.
    with path.open("x+b") as stream:
        with locked(stream):
            append(stream, [], "INIT", None, {"journal": path.stem, "build": build})


def mutate(path, build, operation, kind):
    identity(build)
    check_id(operation)
    with path.open("r+b") as stream, locked(stream):
        records = read(path, stream)
        require(records[0]["data"]["build"] == build, "Build identity mismatch")
        ops = replay(records)
        require(operation not in ops, "Duplicate operation; never retry an ID")
        require(not any(v["state"] in {"IN_PROGRESS", "CLEANUP_UNKNOWN"} for v in ops.values()),
                "Uncertainty blocks new operations")
        if kind == "PREPARED":
            data = {"intended_operation": "inspect-apk", "preconditions": PRECONDITIONS}
        else:
            require(kind == "CLEANUP_UNKNOWN", "Unsupported operation")
            data = {"observation": "external-uncertainty", "phone_authorized": False}
        append(stream, records, kind, operation, data)


def git(*args):
    return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=ROOT,
                                   timeout=30).decode("utf-8").strip()


def check_source(source):
    require(git("rev-parse", "HEAD") == source, "Declared revision is not checked-out HEAD")
    require(not git("diff", "HEAD", "--", "android"), "Android source differs from declared revision")
    require(not git("ls-files", "--others", "--exclude-standard", "android"),
            "Untracked Android input")
    return git("rev-parse", "HEAD^{tree}")


def inspect(build, apk, analyzer, artifacts):
    """Trusted local tools only; never accept a saved manifest as APK validation."""
    identity(build)
    tree = check_source(build["source"])
    require(file_hash(apk) == build["apk_sha256"], "APK identity mismatch")
    validator_path = ROOT / ".github/scripts/validate-harness.py"
    before = {"apk": file_hash(apk), "validator": file_hash(validator_path),
              "analyzer": file_hash(analyzer)}
    require(artifacts, "Declare exact local native artifact correspondence")
    spec = importlib.util.spec_from_file_location("pdva_harness", validator_path)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    with redirect_stdout(io.StringIO()):
        validation = validator.inspect_apk(apk, analyzer, build["variant"])
    require(set(artifacts) == set(validation["native"]), "Missing or extra local native artifacts")
    local = {}
    for name, path in artifacts.items():
        value = file_hash(path)
        require(value == validation["native"][name]["sha256"], "Local native artifact mismatch")
        local[name] = {"path": str(Path(path).resolve()), "sha256": value}
    require(before == {"apk": file_hash(apk), "validator": file_hash(validator_path),
                       "analyzer": file_hash(analyzer)}, "Inputs changed during inspection")
    check_source(build["source"])
    return {"build": build, "validation": validation, "artifacts": local,
            "validator_sha256": before["validator"], "analyzer_sha256": before["analyzer"],
            "source_tree": tree, "scope": "offline-inspection-only"}


def execute(path, build, operation, apk, analyzer, artifacts):
    identity(build)
    with path.open("r+b") as stream, locked(stream):
        records = read(path, stream)
        require(records[0]["data"]["build"] == build, "Build identity mismatch")
        ops = replay(records)
        require(operation in ops and ops[operation]["state"] == "PREPARED",
                "Only a prepared, never-dispatched offline inspection can run")
        require(not any(v["state"] in {"IN_PROGRESS", "CLEANUP_UNKNOWN"} for v in ops.values()),
                "Uncertainty blocks dispatch")
        append(stream, records, "IN_PROGRESS", operation, {})
        try:
            result = inspect(build, apk, analyzer, artifacts)
            receipt(result, build)
        except Exception:
            append(stream, records, "FAILED", operation,
                   {"observation": "offline-validation-rejected"})
            raise
        # BaseException/process death intentionally leaves IN_PROGRESS -> UNKNOWN.
        append(stream, records, "COMPLETED", operation, result)
        return result


def status(path):
    records = read(path)
    ops = replay(records)
    # Read-only and conservative even if a writer is still live. No timeout/PID oracle.
    for value in ops.values():
        if value["state"] == "IN_PROGRESS":
            value["recorded_state"] = "IN_PROGRESS"
            value["state"] = "UNKNOWN"
    blocked = any(v["state"] in {"UNKNOWN", "CLEANUP_UNKNOWN"} for v in ops.values())
    return {"build": records[0]["data"]["build"], "operations": ops,
            "state": "NOT_STARTED" if not ops else "RECORDED",
            "next": "STOP; preserve journal; no retry or cleanup clearance" if blocked else
                    "May explicitly run a PREPARED offline inspection; no phone operation authorized"}


def main():
    require(sys.version_info >= (3, 11), "Python 3.11+ required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "prepare", "inspect", "status", "resume-plan",
                                            "record-cleanup-unknown"))
    parser.add_argument("--journal", required=True, help="Private journal name, not a path")
    parser.add_argument("--source")
    parser.add_argument("--apk-sha256")
    parser.add_argument("--variant", choices=("release", "debug"))
    parser.add_argument("--operation")
    parser.add_argument("--apk", type=Path)
    parser.add_argument("--apkanalyzer", type=Path)
    parser.add_argument("--native", action="append", default=[], metavar="APK_ENTRY=LOCAL_FILE")
    args = parser.parse_args()
    path = safe_path(args.journal)
    if args.command in {"status", "resume-plan"}:
        print(json.dumps(status(path), indent=2))
        return
    build = identity({"source": args.source, "apk_sha256": args.apk_sha256, "variant": args.variant})
    if args.command == "init":
        initialize(path, build)
    elif args.command in {"prepare", "record-cleanup-unknown"}:
        mutate(path, build, args.operation,
               "PREPARED" if args.command == "prepare" else "CLEANUP_UNKNOWN")
    else:
        require(args.apk and args.apkanalyzer, "APK and installed apkanalyzer required")
        artifacts = {}
        for value in args.native:
            name, separator, local = value.partition("=")
            require(separator and name not in artifacts and local, "Ambiguous native mapping")
            artifacts[name] = local
        execute(path, build, args.operation, args.apk, args.apkanalyzer, artifacts)
    print("Private record persisted. Offline only; no device/support/cleanup claim.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("STOP: " + str(error) + "; preserve records; no automatic retry", file=sys.stderr)
        sys.exit(1)
