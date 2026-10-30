#!/usr/bin/env python3
"""Bounded independent research builds; no APK execution, repair or uploads.

Original PDVA standard-library research tooling. Trusts the runner and approved
SDK tools. This is correspondence evidence, not a supply-chain attestation.
"""
import hashlib
import importlib.util
import io
import itertools
import json
import os
from pathlib import Path
import re
import shlex
import struct
import subprocess
import sys
import tempfile
import zipfile

SOURCE = "aa517dfdfe2b72986d67ad65f7f1b34d8494118b"
TREE = "5965f746c6093c2bb86a99f3b4f361b6c315798c"
ROOT = Path(__file__).resolve().parents[2]
NATIVE = ("lib/arm64-v8a/libsubstrate.so", "lib/x86_64/libsubstrate.so",
          "lib/arm64-v8a/libpdva_launch.so")
INPUT_KEYS = {"source", "tree", "tools", "dependencies", "verification", "configuration"}
TOOL_NAMES = {"jdk", "sdk", "build_tools", "ndk", "cmake", "command_tools"}
CONFIG_NAMES = ("android/build.py", "android/build.gradle", "android/settings.gradle",
                "android/gradle.properties", "android/gate0-harness/build.gradle",
                "android/gate0-harness/src/main/cpp/CMakeLists.txt")


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


class SigningReader:
    """Bounded little-endian diagnostic reader; never emits field contents."""
    def __init__(self, raw, offset=0):
        self.raw, self.offset, self.position = raw, offset, 0

    def take(self, count):
        need(0 <= count <= len(self.raw) - self.position, "Truncated signing field")
        start = self.position
        self.position += count
        return SigningReader(self.raw[start:self.position], self.offset + start)

    def u32(self):
        return struct.unpack("<I", self.take(4).raw)[0]

    def field(self):
        return self.take(self.u32())

    def finish(self):
        need(self.position == len(self.raw), "Trailing signing data")

    def identity(self):
        return {"offset": self.offset, "size": len(self.raw), "sha256": digest(self.raw)}

    def sequence(self):
        rows = []
        while self.position < len(self.raw):
            need(len(rows) < 64, "Oversized signing sequence")
            rows.append(self.field())
        return rows


SIGNATURE_ALGORITHMS = {0x0101: "RSA-PSS-SHA256", 0x0102: "RSA-PSS-SHA512",
                        0x0103: "RSA-PKCS1-v1_5-SHA256", 0x0104: "RSA-PKCS1-v1_5-SHA512",
                        0x0201: "ECDSA-SHA256", 0x0202: "ECDSA-SHA512", 0x0301: "DSA-SHA256",
                        0x0421: "verity-RSA-PKCS1-v1_5-SHA256", 0x0423: "verity-ECDSA-SHA256",
                        0x0425: "verity-DSA-SHA256"}


def algorithm_records(reader):
    result = []
    for item in reader.sequence():
        algorithm = item.u32()
        value = item.field()
        item.finish()
        need(value.raw and algorithm not in [x["id"] for x in result], "Empty or duplicate algorithm record")
        result.append({"id": algorithm, "algorithm": SIGNATURE_ALGORITHMS.get(algorithm, "Unknown"),
                       "value": value.identity()})
    need(result, "Missing signing algorithms")
    return result


def v2_signers(value):
    signers = value.field()
    value.finish()
    result = []
    for signer in signers.sequence():
        data, signatures, key = signer.field(), signer.field(), signer.field()
        signer.finish()
        need(key.raw, "Missing signer public key")
        digests, certificates, attributes = data.field(), data.field(), data.field()
        # Pinned apksig 9.4.0 emits a fourth length-prefixed empty element.
        # Recognize exactly its four-byte encoding here, not arbitrary padding.
        empty_field = None
        if data.position < len(data.raw):
            extension = data.take(4)
            need(extension.raw == bytes(4), "Unsupported v2 signed-data extension")
            empty_field = extension.identity()
        data.finish()
        digest_rows, signature_rows = algorithm_records(digests), algorithm_records(signatures)
        need([x["id"] for x in digest_rows] == [x["id"] for x in signature_rows],
             "Digest/signature algorithm lists differ")
        cert_rows = certificates.sequence()
        need(cert_rows and all(x.raw for x in cert_rows), "Missing signer certificate")
        attrs = []
        for item in attributes.sequence():
            identifier = item.u32()
            need(identifier not in [x["id"] for x in attrs], "Duplicate signed attribute")
            attrs.append({"id": identifier, "value": item.take(len(item.raw) - item.position).identity()})
        result.append({"signed_data": data.identity(), "apksig_empty_field": empty_field, "digests": digest_rows,
                       "certificates": [x.identity() for x in cert_rows], "attributes": attrs,
                       "signatures": signature_rows, "public_key": key.identity()})
    need(result, "Missing v2 signers")
    return result


def signing_block_snapshot(raw, offset=0):
    need(32 <= len(raw) <= 4 * 1024 * 1024 and raw[-16:] == b"APK Sig Block 42",
         "Missing or oversized APK signing block")
    need(struct.unpack_from("<Q", raw)[0] == struct.unpack_from("<Q", raw, len(raw) - 24)[0]
         == len(raw) - 8, "Invalid signing block sizes")
    reader = SigningReader(raw[8:-24], offset + 8)
    blocks = []
    names = {0x7109871a: "v2", 0xf05368c0: "v3", 0x1b93ad61: "v3.1",
             0x42726577: "verity-padding", 0x504b4453: "dependency-info"}
    while reader.position < len(reader.raw):
        need(len(blocks) < 64, "Too many signing blocks")
        size = struct.unpack("<Q", reader.take(8).raw)[0]
        need(size >= 4, "Invalid signing pair size")
        pair = reader.take(size)
        identifier = pair.u32()
        need(identifier not in [x["id"] for x in blocks], "Duplicate signing block ID")
        value = pair.take(len(pair.raw) - pair.position)
        row = {"id": identifier, "kind": names.get(identifier, "Unknown"), **value.identity()}
        if identifier == 0x7109871a:
            row["signers"] = v2_signers(value)
        elif identifier == 0x42726577:
            row["all_zero"] = not any(value.raw)
        blocks.append(row)
    need(any(x["id"] == 0x7109871a for x in blocks), "Missing v2 signing block")
    return {"offset": offset, "size": len(raw), "sha256": digest(raw), "blocks": blocks}


def verified_signing_snapshot(apk, verified):
    apk_snapshot(apk)  # Existing bounded ZIP admission, with no byte exclusions.
    raw = Path(apk).read_bytes()
    end = raw.rfind(b"PK\x05\x06", max(0, len(raw) - 65557))
    central = struct.unpack_from("<I", raw, end + 16)[0]
    need(central >= 32 and raw[central - 16:central] == b"APK Sig Block 42", "Missing signing magic")
    size = struct.unpack_from("<Q", raw, central - 24)[0]
    need(24 <= size <= min(4 * 1024 * 1024 - 8, central - 8), "Invalid signing block bounds")
    start = central - size - 8
    result = signing_block_snapshot(raw[start:central], start)
    signers = next(x["signers"] for x in result["blocks"] if x["id"] == 0x7109871a)
    need(len(signers) == 1 and signers[0]["certificates"][0]["sha256"] == verified["certificate_sha256"]
         and verified["schemes"].get("v2") == "true", "Parsed signer differs from verified signer")
    return result


def signing_mutation_control(apk, report, verifier, output):
    """Alter a disposable copy only; real APKs remain the comparison inputs."""
    need(sys.platform == "linux" and os.environ.get("GITHUB_ACTIONS") == "true",
         "Signature mutation controls require authorized hosted Linux")
    signers = next(x["signers"] for x in report["blocks"] if x["id"] == 0x7109871a)
    raw = bytearray(Path(apk).read_bytes())
    for signer in signers:
        for sig in signer["signatures"]:
            raw[sig["value"]["offset"]] ^= 1
    with Path(output).open("xb") as stream:
        stream.write(raw)
    check = subprocess.run([str(verifier), "verify", "--verbose", str(output)],
                           capture_output=True, text=True, timeout=900)
    need(check.returncode == 1 and "DOES NOT VERIFY" in check.stdout + check.stderr,
         "Altered-signature control did not fail cryptographic verification")
    return {"altered_signature_rejected": True, "verifier_sha256": file_hash(verifier)}


def signing_differences(left, right):
    """Report field paths only; this never decides whole-APK equality."""
    changed = []
    def visit(a, b, path):
        if type(a) is dict and type(b) is dict and a.keys() == b.keys():
            for key in sorted(a):
                visit(a[key], b[key], path + "/" + key)
        elif type(a) is list and type(b) is list and len(a) == len(b):
            for i, (x, y) in enumerate(zip(a, b)):
                visit(x, y, path + "/" + str(i))
        elif a != b:
            need(len(changed) < 4096, "Too many signing diagnostic differences")
            changed.append(path)
    visit(left, right, "")
    return changed


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


def byte_differences(left, right):
    """Half-open offsets; never remove or normalize differing bytes."""
    ranges, start, count, total_ranges = [], None, 0, 0
    for offset, (a, b) in enumerate(itertools.zip_longest(left, right, fillvalue=None)):
        if a != b:
            count += 1
            if start is None:
                start = offset
        elif start is not None:
            total_ranges += 1
            if len(ranges) < 4096:
                ranges.append([start, offset])
            start = None
    if start is not None:
        total_ranges += 1
        if len(ranges) < 4096:
            ranges.append([start, max(len(left), len(right))])
    return {"different_bytes": count, "ranges": ranges, "range_count": total_ranges,
            "ranges_complete": total_ranges == len(ranges), "sizes": [len(left), len(right)]}


def elf_sections(raw):
    """Diagnostic labels only; existing validator owns ELF admission."""
    need(raw[:6] == b"\x7fELF\x02\x01" and len(raw) >= 64, "Unsupported diagnostic ELF")
    offset = struct.unpack_from("<Q", raw, 40)[0]
    size, count, names_index = struct.unpack_from("<HHH", raw, 58)
    need(size == 64 and 0 < count <= 4096 and names_index < count and
         offset + size * count <= len(raw), "Unsupported diagnostic ELF sections")
    rows = [struct.unpack_from("<IIQQQQIIQQ", raw, offset + size * i) for i in range(count)]
    names = rows[names_index]
    need(names[4] + names[5] <= len(raw), "Invalid diagnostic ELF names")
    strings = raw[names[4]:names[4] + names[5]]
    result = []
    for row in rows:
        if row[1] in (0, 8):  # NULL / NOBITS have no section payload to compare.
            continue
        need(row[0] < len(strings) and row[4] + row[5] <= len(raw), "Invalid diagnostic ELF section")
        end = strings.find(b"\0", row[0])
        need(end >= 0, "Unterminated diagnostic section name")
        name = strings[row[0]:end].decode("ascii")
        result.append({"name": name, "offset": row[4], "size": row[5],
                       "sha256": digest(raw[row[4]:row[4] + row[5]])})
    return result


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
    details = {}
    with zipfile.ZipFile(a) as az, zipfile.ZipFile(b) as bz:
        for name in content:
            if name not in lrows or name not in rrows:
                details[name] = {"presence": [name in lrows, name in rrows]}
                continue
            x, y = az.read(name), bz.read(name)
            details[name] = byte_differences(x, y)
            if x[:6] == y[:6] == b"\x7fELF\x02\x01":
                details[name]["elf_sections_a"] = elf_sections(x)
                details[name]["elf_sections_b"] = elf_sections(y)
    same_signer = sign_a == sign_b
    return {"version": 1, "scope": "controlled-research-builds-only", "inputs": inputs_a,
            "a": left, "b": right, "signing_a": sign_a, "signing_b": sign_b,
            "signed_bytes_equal": left == right and same_signer,
            "entry_content_equal": not content, "entry_order_equal": list(lrows) == list(rrows),
            "changed_entries": changed, "changed_content": content,
            "content_differences": details,
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


def diagnostic_elf(raw, checkout, build_dir):
    """Hash original bytes; path facts are observations, never equality inputs."""
    sections = elf_sections(raw)
    return {"sha256": digest(raw), "size": len(raw), "sections": sections,
            "debug_path_sections": [row["name"] for row in sections
                                    if row["name"].startswith(".debug") and
                                    str(checkout).encode() in raw[row["offset"]:row["offset"] + row["size"]]],
            "contains_checkout_path": str(checkout).encode() in raw,
            "contains_build_path": str(build_dir).encode() in raw}


def build_note(snapshot):
    notes = [row for row in snapshot["sections"] if row["name"] == ".note.gnu.build-id"]
    need(len(notes) == 1, "Missing or ambiguous diagnostic build-ID section")
    return {key: notes[0][key] for key in ("size", "sha256")}


def command_facts(text):
    # Never publish raw command strings: compiler paths can disclose host paths.
    tokens = shlex.split(text)
    flags = ("-g", "-g0", "-g1", "-g2", "-O2", "-DNDEBUG", "-fPIC",
             "-fstack-protector-strong", "-Wl,-z,relro,-z,now", "-Wl,--build-id=sha1")
    return {"sha256": digest(text.encode()), "flags": [x for x in flags if x in tokens],
            "prefix_map_options": sum(x.startswith(("-fdebug-prefix-map=", "-ffile-prefix-map="))
                                      for x in tokens)}


def public_commands(text, checkout, sdk):
    result = []
    for line in text.splitlines():
        tokens = []
        for token in shlex.split(line):
            token = token.replace(str(checkout), "<checkout>").replace(str(sdk), "<sdk>")
            # Unknown path-bearing tokens are hashed, never printed. Known roots
            # are labels for display only; all identities hash the original bytes.
            tokens.append({"path_token_sha256": digest(token.encode())}
                          if "/" in token and "<checkout>" not in token and "<sdk>" not in token
                          else token)
        result.append(tokens)
    return result


def require_debug_mapping(tokens, source_dir, build_dir):
    expected = ["-fdebug-prefix-map=" + str(source_dir) + "=/pdva/jni/src",
                "-fdebug-prefix-map=" + str(build_dir) + "=/pdva/jni/build"]
    actual = [x for x in tokens if x.startswith(("-fdebug-prefix-map=", "-ffile-prefix-map="))]
    need(actual == expected, "Missing or changed JNI debug-path mappings")
    need("-g" in tokens and "-g0" not in tokens and "-fstack-protector-strong" in tokens,
         "Missing JNI debug information or stack protection")
    return expected


def verify_mapping_control(mapped, replay, unmapped, checkout, build_dir):
    need(mapped == replay, "Mapped compiler replay differs from real build object")
    a = diagnostic_elf(mapped, checkout, build_dir)
    b = diagnostic_elf(unmapped, checkout, build_dir)
    sections = lambda snap: {x["name"]: (x["size"], x["sha256"]) for x in snap["sections"]}
    left, right = sections(a), sections(b)
    need(all(rows.get(name, (0,))[0] > 0 for rows in (left, right)
             for name in (".debug_info", ".debug_str", ".debug_line")),
         "Full JNI debug sections missing")
    need(any(name.startswith(".text") and size > 0 for name, (size, _) in left.items()),
         "JNI code sections missing")
    # Debug-string offsets can also change relocations targeting debug sections.
    # This control is not the APK comparator, which still checks every byte.
    debug_prefixes = (".debug", ".rel.debug", ".rela.debug")
    need({k: v for k, v in left.items() if not k.startswith(debug_prefixes)} ==
         {k: v for k, v in right.items() if not k.startswith(debug_prefixes)},
         "Mapping changed non-debug object sections")
    need(not a["contains_checkout_path"] and not a["contains_build_path"] and
         b"/pdva/jni/build" in mapped,
         "Mapped object retains private paths or lacks stable debug identities")
    need(mapped != unmapped and b["contains_checkout_path"] and b["contains_build_path"],
         "Removing mappings did not expose the expected path-sensitive difference")
    return {"mapped_sha256": a["sha256"], "replay_sha256": digest(replay),
            "unmapped_sha256": b["sha256"], "non_debug_sections_equal": True,
            "mapped_replay_equal": True, "missing_mapping_detected": True}


def mapping_control(entry, mapped, checkout, build_dir, packages, output_dir):
    """Compile real JNI source controls on hosted Linux; never alter built objects."""
    need(sys.platform == "linux" and os.environ.get("GITHUB_ACTIONS") == "true",
         "Compiler controls require authorized hosted Linux")
    tokens = shlex.split(entry["command"])
    maps = require_debug_mapping(tokens, checkout / "android/gate0-harness/src/main/cpp", build_dir)
    compiler = packages["ndk"] / "toolchains/llvm/prebuilt/linux-x86_64/bin/clang"
    need(Path(tokens[0]) == compiler and tokens.count("-c") == tokens.count("-o") == 1 and
         tokens[tokens.index("-c") + 1] == entry["file"], "Unexpected JNI control command")
    need(not any(x in tokens for x in ("-MD", "-MMD", "-MF", "-MT", "-MQ", "-save-temps")),
         "Unexpected extra compiler outputs")
    outputs = []
    for label in ("mapped", "unmapped"):
        args = list(tokens)
        output = output_dir / (Path(entry["file"]).name + "." + label + ".o")
        need(not output.exists(), "Compiler control output already exists")
        args[args.index("-o") + 1] = str(output)
        if label == "unmapped":
            args = [x for x in args if x not in maps]
        command(args, cwd=build_dir)
        outputs.append(output.read_bytes())
    return verify_mapping_control(mapped, *outputs, checkout, build_dir)


def native_diagnostics(checkout, packages, apk, native, scratch, label):
    """Inspect real outputs and compile separate controls; never rewrite outputs."""
    module = checkout / "android/gate0-harness"
    report = {}
    private = {}
    for abi in ("arm64-v8a", "x86_64"):
        databases = list((module / ".cxx").glob("RelWithDebInfo/*/" + abi + "/compile_commands.json"))
        need(len(databases) == 1, "Missing or ambiguous release compile database")
        database = databases[0]
        build_dir = database.parent
        entries = json.loads(database.read_text())
        need(len(entries) == 2 and {Path(x["file"]).name for x in entries} == {"probe.c", "launch.c"},
             "Unexpected JNI compile inputs")
        commands = command([str(packages["cmake"] / "bin/ninja"), "-C", str(build_dir),
                            "-t", "commands", "substrate"])
        private[abi] = {"compile_database": entries, "ninja_commands": commands}
        controls_dir = scratch / (label + "-controls-" + abi)
        controls_dir.mkdir()  # Fresh outputs; no reuse or overwrite.
        objects = {}
        for entry in entries:
            need(Path(entry["directory"]).resolve() == build_dir.resolve(), "Unexpected compile directory")
            tokens = shlex.split(entry["command"])
            need(tokens.count("-o") == 1, "Ambiguous object output")
            obj = (build_dir / tokens[tokens.index("-o") + 1]).resolve()
            need(obj.is_relative_to(build_dir.resolve()), "Object outside diagnostic build directory")
            mapped = obj.read_bytes()
            objects[Path(entry["file"]).name] = {
                "command": command_facts(entry["command"]),
                "elf": diagnostic_elf(mapped, checkout, build_dir),
                "mapping_control": mapping_control(entry, mapped, checkout, build_dir, packages, controls_dir)}
        libraries = list((module / "build/intermediates/cxx").glob(
            "RelWithDebInfo/*/obj/" + abi + "/libsubstrate.so"))
        need(len(libraries) == 1, "Missing or ambiguous unstripped JNI library")
        unstripped = diagnostic_elf(libraries[0].read_bytes(), checkout, build_dir)
        name = "lib/" + abi + "/libsubstrate.so"
        stripped_bytes = (native / name).read_bytes()
        stripped = diagnostic_elf(stripped_bytes, checkout, build_dir)
        with zipfile.ZipFile(apk) as archive:
            need(archive.read(name) == stripped_bytes, "Stripped JNI output differs from packaged bytes")
        need(build_note(unstripped) == build_note(stripped), "Build-ID changed during stripping")
        report[abi] = {"objects": objects, "unstripped": unstripped, "stripped": stripped,
                       "strip_preserves_build_id": True, "packaged_bytes_equal_stripped": True,
                       "generated_inputs": {name: file_hash(build_dir / name) for name in
                                            ("compile_commands.json", "CMakeCache.txt", "build.ninja",
                                             "CMakeFiles/rules.ninja")},
                       "ninja_commands": command_facts(commands),
                       "display_commands": public_commands(commands, checkout, packages["ndk"].parents[1])}
    # Ephemeral private runner record only, never an uploaded artifact or log dump.
    (scratch / (label + "-native-inputs.json")).write_text(canonical(private))
    print("NATIVE_BUILD_DIAGNOSTICS=" + canonical({"build": label, "abis": report}), flush=True)


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
    results, signing_reports = [], []
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
        signing_report = verified_signing_snapshot(apk, sign)
        verifier = packages["build_tools"] / "apksigner"
        verifier_version = command([str(verifier), "version"])
        need(re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", verifier_version), "Unexpected verifier version")
        print("APK_SIGNING_DIAGNOSTICS=" + canonical({"build": label, "report": signing_report,
              "apksigner_version": verifier_version,
              "apksigner_jar_sha256": file_hash(packages["build_tools"] / "lib/apksigner.jar")}), flush=True)
        control = signing_mutation_control(apk, signing_report, verifier, scratch / (label + "-altered-signature.apk"))
        print("SIGNATURE_NEGATIVE_CONTROL=" + canonical({"build": label, **control}), flush=True)
        signing_reports.append(signing_report)
        inspector = load_inspector(checkout)
        native = checkout / "android/gate0-harness/build/intermediates/stripped_native_libs/release/stripReleaseDebugSymbols/out"
        receipt = inspector.inspect({"source": SOURCE, "apk_sha256": file_hash(apk), "variant": "release"},
                                    apk, packages["command_tools"] / "bin/apkanalyzer",
                                    {name: native / name for name in NATIVE})
        need(receipt["source_tree"] == TREE, "Wrong inspected tree")
        native_diagnostics(checkout, packages, apk, native, scratch, label)
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
    print("SIGNING_BLOCK_CHANGED_FIELDS=" + canonical(signing_differences(*signing_reports)), flush=True)
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
