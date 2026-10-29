#!/usr/bin/env python3
"""Bounded independent research builds; no APK execution, repair or uploads.

Original PDVA standard-library research tooling. Trusts the runner and approved
SDK tools. This is correspondence evidence, not a supply-chain attestation.
"""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import zipfile

SOURCE = "61c68f87404a1b7e70e0314b73532322ee2de252"
TREE = "452cc52b115f7d0c5d8cb63be1f092f189d4b26d"
ROOT = Path(__file__).resolve().parents[2]
NATIVE = ("lib/arm64-v8a/libsubstrate.so", "lib/x86_64/libsubstrate.so",
          "lib/arm64-v8a/libpdva_launch.so")
INPUT_KEYS = {"source", "tree", "tools", "dependencies", "verification", "configuration"}
TOOL_NAMES = {"jdk", "sdk", "build_tools", "ndk", "cmake", "command_tools"}
CONFIG_NAMES = ("android/build.py", "android/build.gradle", "android/settings.gradle",
                "android/gradle.properties", "android/gate0-harness/build.gradle")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def directory_hash(path):
    """Hash every file's relative name and bytes; no cache content is published."""
    path = Path(path)
    rows = [(p.relative_to(path).as_posix(), file_hash(p))
            for p in sorted(path.rglob("*")) if p.is_file()]
    need(rows, "Missing input directory")
    return {"files": len(rows), "sha256": digest(canonical(rows).encode())}


def command(args, cwd=ROOT, env=None):
    return subprocess.check_output(args, cwd=cwd, env=env, text=True,
                                   stderr=subprocess.STDOUT, timeout=900).strip()


def signature(text):
    certs = re.findall(r"^Signer #\d+ certificate SHA-256 digest: ([0-9a-f]{64})$", text, re.M)
    schemes = re.findall(r"^Verified using (v\d+(?:\.\d+)?) scheme .*: (true|false)$", text, re.M)
    need(text.startswith("Verifies\n") and len(certs) == 1 and len(set(schemes)) == len(schemes),
         "Incomplete signature verification")
    need(dict(schemes).get("v2") == "true", "Missing verified v2 signature")
    return {"certificate_sha256": certs[0], "schemes": dict(schemes)}


def apk_snapshot(path):
    path = Path(path)
    need(path.is_file() and 0 < path.stat().st_size <= 128 * 1024 * 1024, "Missing or oversized APK")
    raw = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        need(0 < len(entries) <= 4096, "Empty or oversized ZIP inventory")
        need(len({e.filename for e in entries}) == len(entries), "Duplicate ZIP entry")
        rows = []
        for e in entries:
            need(e.file_size <= 32 * 1024 * 1024, "Oversized ZIP entry")
            payload = archive.read(e)  # Includes CRC validation; every entry, no exclusions.
            rows.append({"name": e.filename, "size": e.file_size, "compressed_size": e.compress_size,
                         "method": e.compress_type, "crc": e.CRC, "timestamp": list(e.date_time),
                         "flags": e.flag_bits, "offset": e.header_offset,
                         "extra": e.extra.hex(), "comment": e.comment.hex(),
                         "create_system": e.create_system, "create_version": e.create_version,
                         "extract_version": e.extract_version, "internal_attr": e.internal_attr,
                         "external_attr": e.external_attr, "sha256": digest(payload)})
    # Preserve raw local records, signing region, central directory and EOCD.
    # Restrict this research comparator to conventional single-disk, non-ZIP64 APKs.
    end = raw.rfind(b"PK\x05\x06", max(0, len(raw) - 65557))
    need(end >= 0 and end + 22 <= len(raw), "Missing EOCD")
    disk, cd_disk, n_disk, n, size, offset, comment = struct.unpack_from("<4H2IH", raw, end + 4)
    need(disk == cd_disk == 0 and n_disk == n == len(rows) and offset + size == end
         and end + 22 + comment == len(raw), "Unsupported or partial ZIP layout")
    start = offset
    if offset >= 24 and raw[offset - 16:offset] == b"APK Sig Block 42":
        block_size = struct.unpack_from("<Q", raw, offset - 24)[0]
        start = offset - block_size - 8
        need(0 <= start < offset - 24 and struct.unpack_from("<Q", raw, start)[0] == block_size,
             "Malformed APK signing block")
    return {"sha256": digest(raw), "size": len(raw), "entries": rows,
            "regions": {"local_records": digest(raw[:start]), "signing_block": digest(raw[start:offset]),
                        "central_directory": digest(raw[offset:end]), "eocd": digest(raw[end:])}}


def compare(a, b, inputs_a, inputs_b, sign_a, sign_b):
    need(Path(a).resolve() != Path(b).resolve(), "Same artifact supplied twice")
    for inputs in (inputs_a, inputs_b):
        need(set(inputs) == INPUT_KEYS and all(inputs.values()), "Missing build inputs")
        need(re.fullmatch(r"[0-9a-f]{40}", inputs["source"]) and
             re.fullmatch(r"[0-9a-f]{40}", inputs["tree"]), "Malformed source identity")
        need(type(inputs["tools"]) is dict and set(inputs["tools"]) == TOOL_NAMES | {"java_version"}
             and inputs["tools"]["java_version"], "Incomplete tool inputs")
        for row in [inputs["dependencies"], *(inputs["tools"][k] for k in TOOL_NAMES)]:
            need(type(row) is dict and set(row) == {"files", "sha256"} and
                 type(row["files"]) is int and row["files"] > 0 and
                 re.fullmatch(r"[0-9a-f]{64}", row["sha256"]), "Incomplete input inventory")
        need(type(inputs["configuration"]) is dict and set(inputs["configuration"]) == set(CONFIG_NAMES),
             "Incomplete configuration inputs")
        need(all(re.fullmatch(r"[0-9a-f]{64}", value) for value in
                 [inputs["verification"], *inputs["configuration"].values()]), "Malformed input digest")
    need(inputs_a == inputs_b, "Different source or build inputs")
    for sign in (sign_a, sign_b):
        need(set(sign) == {"certificate_sha256", "schemes"} and
             re.fullmatch(r"[0-9a-f]{64}", sign["certificate_sha256"]) and
             sign["schemes"].get("v2") == "true", "Incomplete signing inputs")
    left, right = apk_snapshot(a), apk_snapshot(b)
    lrows = {x["name"]: x for x in left["entries"]}
    rrows = {x["name"]: x for x in right["entries"]}
    changed = [name for name in sorted(lrows.keys() | rrows.keys()) if lrows.get(name) != rrows.get(name)]
    content = [name for name in changed if lrows.get(name, {}).get("sha256") != rrows.get(name, {}).get("sha256")]
    same_signer = sign_a == sign_b
    return {"version": 1, "scope": "controlled-research-builds-only", "inputs": inputs_a,
            "a": left, "b": right, "signing_a": sign_a, "signing_b": sign_b,
            "signed_bytes_equal": left == right and same_signer,
            "entry_content_equal": not content, "entry_order_equal": list(lrows) == list(rrows),
            "changed_entries": changed, "changed_content": content,
            "changed_regions": [k for k in left["regions"] if left["regions"][k] != right["regions"][k]],
            "same_signing_identity_and_schemes": same_signer}


def verify_result(result, *args):
    # No imported claim can substitute for recomputation from both existing APKs.
    need(type(result) is dict and canonical(result) == canonical(compare(*args)),
         "Malformed, partial or substituted comparison result")
    need(result["signed_bytes_equal"], "APK bytes or signing identity differ")


def load_inspector(root):
    spec = importlib.util.spec_from_file_location("readiness", root / ".github/scripts/desktop-readiness.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    need(sys.platform == "linux" and os.environ.get("GITHUB_ACTIONS") == "true",
         "Independent native builds require authorized hosted Linux")
    sdk, java = Path(os.environ["ANDROID_HOME"]), Path(os.environ["JAVA_HOME"])
    version = command([str(java / "bin/java"), "-version"])
    need("Temurin-17.0.21+9" in version, "Unqualified JDK patch; STOP")
    packages = {"jdk": java, "sdk": sdk / "platforms/android-37.0",
                "build_tools": sdk / "build-tools/36.0.0", "ndk": sdk / "ndk/28.2.13676358",
                "cmake": sdk / "cmake/3.22.1", "command_tools": sdk / "cmdline-tools/latest"}
    for name, expected in (("sdk", "2"), ("build_tools", "36.0.0"), ("ndk", "28.2.13676358"),
                           ("cmake", "3.22.1"), ("command_tools", "12.0")):
        props = (packages[name] / "source.properties").read_text()
        need(re.search(r"^Pkg.Revision\s*=\s*" + re.escape(expected) + r"\s*$", props, re.M),
             "Unqualified SDK package revision; STOP")
    tools = {name: directory_hash(path) for name, path in packages.items()}
    tools["java_version"] = version
    need(command(["git", "rev-parse", SOURCE + "^{tree}"]) == TREE, "Reviewed source unavailable")
    # New directories only. Never delete or reuse worktrees or compilation state.
    scratch = Path(tempfile.mkdtemp(prefix="pdva-repro-", dir=os.environ["RUNNER_TEMP"]))
    results = []
    for label in ("a", "b"):
        checkout = scratch / label
        command(["git", "worktree", "add", "--detach", str(checkout), SOURCE])
        need(not command(["git", "status", "--porcelain", "--ignored"], cwd=checkout), "Nonempty build state")
        env = dict(os.environ, GRADLE_USER_HOME=str(scratch / (label + "-gradle")))
        args = [sys.executable, "android/build.py", "--no-build-cache", "--no-configuration-cache",
                "--rerun-tasks", "--dependency-verification=strict", ":gate0-harness:assembleRelease"]
        print("INDEPENDENT_BUILD_START=" + label, flush=True)
        log = command(args, cwd=checkout, env=env)
        (scratch / (label + "-build.txt")).write_text(log)
        need("BUILD SUCCESSFUL" in log and "FROM-CACHE" not in log, "Build incomplete or restored outputs")
        print("INDEPENDENT_BUILD_COMPLETE=" + label, flush=True)
        apk = checkout / "android/gate0-harness/build/outputs/apk/release/gate0-harness-release.apk"
        sign = signature(command([str(packages["build_tools"] / "apksigner"), "verify", "--verbose",
                                  "--print-certs", str(apk)]))
        inspector = load_inspector(checkout)
        native = checkout / "android/gate0-harness/build/intermediates/stripped_native_libs/release/stripReleaseDebugSymbols/out"
        receipt = inspector.inspect({"source": SOURCE, "apk_sha256": file_hash(apk), "variant": "release"},
                                    apk, packages["command_tools"] / "bin/apkanalyzer",
                                    {name: native / name for name in NATIVE})
        need(receipt["source_tree"] == TREE, "Wrong inspected tree")
        inputs = {"source": SOURCE, "tree": TREE, "tools": tools,
                  "dependencies": directory_hash(Path(env["GRADLE_USER_HOME"]) / "caches/modules-2/files-2.1"),
                  "verification": file_hash(checkout / "android/gradle/verification-metadata.xml"),
                  "configuration": {name: file_hash(checkout / name) for name in CONFIG_NAMES}}
        print("BUILD_INPUTS=" + canonical({"build": label, "inputs": inputs}), flush=True)
        print("OFFLINE_INSPECTION=" + canonical({"build": label, "validation": receipt["validation"],
              "validator_sha256": receipt["validator_sha256"], "analyzer_sha256": receipt["analyzer_sha256"]}), flush=True)
        results.append((apk, inputs, sign))
    need(tools == dict({name: directory_hash(path) for name, path in packages.items()}, java_version=version),
         "Tool installation changed during builds")
    a, b = results
    args = (a[0], b[0], a[1], b[1], a[2], b[2])
    result = compare(*args)
    print("APK_REPRODUCIBILITY=" + canonical(result), flush=True)
    verify_result(result, *args)
    print("SIGNED_APK_EQUALITY=PASS; no installation or safety claim", flush=True)


if __name__ == "__main__":
    try:
        run()
    except Exception as error:
        # Never dump private paths, raw build logs, environment or signing material.
        print("APK_REPRODUCIBILITY=STOP: " + (str(error) if isinstance(error, ValueError)
                                              else type(error).__name__), file=sys.stderr)
        sys.exit(1)
