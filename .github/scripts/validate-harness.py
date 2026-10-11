#!/usr/bin/env python3
"""Exact zero-permission manifest and artifact checks; no Android runtime claim."""
import argparse
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
A = "{http://schemas.android.com/apk/res/android}"
SOURCE = ROOT / "android/gate0-harness/src/main/AndroidManifest.xml"

def manifest(text, release=False, packaged=False):
    root = ET.fromstring(text)
    if any("permission" in item.tag for item in root):
        raise ValueError("Manifest permission declaration")
    app = root.find("application")
    if app is None or app.get(A + "allowBackup") != "false":
        raise ValueError("Backup must be disabled")
    if release and app.get(A + "debuggable", "false") != "false":
        raise ValueError("Release must not be debuggable")
    if app.get(A + "usesCleartextTraffic") != "false" or app.get(A + "fullBackupContent") != "false":
        raise ValueError("Application authority changed")
    if packaged:
        sdk = root.find("uses-sdk")
        if sdk is None or sdk.get(A + "targetSdkVersion") != "37" or sdk.get(A + "minSdkVersion") != "30":
            raise ValueError("Research SDK contract changed")
        if app.get(A + "extractNativeLibs") != "true":
            raise ValueError("Fixed executable requires installer extraction")
    services = app.findall("service")
    if len(services) != 1:
        raise ValueError("Exactly one isolated worker required")
    service = services[0]
    if not service.get(A + "name", "").endswith(".WorkerService"):
        raise ValueError("Unexpected service")
    for key, value in {"isolatedProcess": "true", "exported": "false",
                       "process": ":gate0_worker", "useAppZygote": "false"}.items():
        if service.get(A + key) != value:
            raise ValueError("Worker authority attribute: " + key)
    if service.get(A + "allowSharedIsolatedProcess", "false") != "false":
        raise ValueError("Shared isolated worker")
    if service.get(A + "permission") or service.findall("intent-filter"):
        raise ValueError("Unexpected service interface")
    if app.findall("provider") or app.findall("receiver"):
        raise ValueError("Unexpected component authority")
    activities = app.findall("activity")
    if len(activities) != 1 or not activities[0].get(A + "name", "").endswith(".MainActivity"):
        raise ValueError("Unexpected activity")
    if (app.findall("activity-alias") or app.findall("profileable")
            or app.get(A + "permission") or root.get(A + "sharedUserId")):
        raise ValueError("Unexpected shared UID or component")


def elf(data, machine, executable):
    """Inspect bytes actually in the APK, never trust the .so suffix or build success."""
    def need(condition, reason):
        if not condition:
            raise ValueError("ELF: " + reason)
    def take(offset, size):
        need(0 <= offset <= len(data) and 0 <= size <= len(data)-offset, "range")
        return data[offset:offset+size]
    need(data[:7] == b"\x7fELF\x02\x01\x01", "ELF64 little endian")
    h = struct.unpack("<16sHHIQQQIHHHHHH", take(0, 64))
    need(h[1] == 3 and h[2] == machine and h[3] == 1, "ET_DYN and ABI")
    need(h[8] == 64 and h[9] == 56 and 0 < h[10] <= 32, "header sizes")
    segments = [struct.unpack("<IIQQQQQQ", take(h[5] + i*56, 56)) for i in range(h[10])]
    loads = [p for p in segments if p[0] == 1]
    need(bool(loads), "missing load segments")
    for p in loads:
        take(p[2], p[5])
        need(p[5] <= p[6] and p[1] & 3 != 3, "writable executable segment")
        need(p[7] >= 16384 and p[2] % 16384 == p[3] % 16384, "16 KiB alignment")
    stacks = [p for p in segments if p[0] == 0x6474e551]
    need(len(stacks) == 1 and not stacks[0][1] & 1, "executable or absent GNU_STACK")
    need(any(p[0] == 0x6474e552 for p in segments), "RELRO")
    android_notes = []
    for p in segments:
        if p[0] != 4:
            continue
        notes = take(p[2], p[5])
        offset = 0
        while offset < len(notes):
            need(offset+12 <= len(notes), "note header")
            namesz, descsz, kind = struct.unpack_from("<III", notes, offset)
            offset += 12
            name = notes[offset:offset+namesz]
            offset += (namesz+3) & ~3
            description = notes[offset:offset+descsz]
            offset += (descsz+3) & ~3
            need(offset <= len(notes), "note range")
            if name == b"Android\0" and kind == 1:
                android_notes.append(description)
    need(len(android_notes) == 1 and len(android_notes[0]) == 132, "Android toolchain note")
    note = android_notes[0]
    need(struct.unpack_from("<I", note)[0] == 30 and note[4:68].rstrip(b"\0") == b"r28c"
         and note[68:132].rstrip(b"\0") == b"13676358", "API 30 and NDK r28c identity")
    interpreters = [take(p[2], p[5]) for p in segments if p[0] == 3]
    dynamics = [p for p in segments if p[0] == 2]
    need(len(dynamics) == 1 and dynamics[0][5] % 16 == 0, "dynamic section")
    p = dynamics[0]
    tags = {}
    for offset in range(p[2], p[2]+p[5], 16):
        tag, value = struct.unpack("<qQ", take(offset, 16))
        if tag == 0:
            break
        tags.setdefault(tag, []).append(value)
    need(5 in tags and 10 in tags and len(tags[5]) == len(tags[10]) == 1, "string table")
    address, size = tags[5][0], tags[10][0]
    tables = [take(p[2]+address-p[3], size) for p in loads
              if p[3] <= address and address+size <= p[3]+p[5]]
    need(len(tables) == 1, "mapped string table")
    strings = tables[0]
    def string(index):
        need(0 <= index < len(strings), "string index")
        end = strings.find(b"\0", index)
        need(end >= 0, "unterminated string")
        return strings[index:end].decode("ascii")
    dependencies = [string(i) for i in tags.get(1, [])]
    need(set(dependencies) <= {"libc.so", "libdl.so", "libm.so"}
         and "libc.so" in dependencies, "unreviewed dependency")
    need(22 not in tags and not any(v & 4 for v in tags.get(30, [])), "text relocations")
    need(15 not in tags and 29 not in tags, "RPATH or RUNPATH")
    need(24 in tags or any(v & 8 for v in tags.get(30, []))
         or any(v & 1 for v in tags.get(0x6ffffffb, [])), "immediate binding")
    pie = any(v & 0x08000000 for v in tags.get(0x6ffffffb, []))
    if executable:
        need(interpreters == [b"/system/bin/linker64\0"] and pie and h[4] != 0,
             "dynamic executable versus JNI library")
        need(any(p[1] & 1 and p[3] <= h[4] < p[3]+p[6] for p in loads), "entry outside executable load")
        need(14 not in tags, "executable SONAME")
        need(b"__stack_chk_fail\0" in strings, "stack protector")
    else:
        need(not interpreters and not pie and h[4] == 0, "JNI versus executable")
        need([string(i) for i in tags.get(14, [])] == ["libsubstrate.so"], "JNI SONAME")
    return dependencies


def inventory(apk):
    expected = {"lib/arm64-v8a/libsubstrate.so": (183, False),
                "lib/x86_64/libsubstrate.so": (62, False),
                "lib/arm64-v8a/libpdva_launch.so": (183, True)}
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate APK entry")
        native = {name for name in names if name.startswith("lib/") and not name.endswith("/")}
        if native != set(expected):
            raise ValueError("Unknown or missing packaged native payload")
        for info in archive.infolist():
            if info.is_dir():
                continue
            if info.file_size > 32*1024*1024:
                raise ValueError("Unexpected APK entry size")
            with archive.open(info) as stream:
                magic = stream.read(4)
            if (magic in {b"\x7fELF", b"\0asm", b"!<ar"} or magic[:2] == b"MZ"
                    or info.filename.lower().endswith((".so", ".exe", ".dll", ".dylib", ".a", ".o", ".wasm"))) and info.filename not in expected:
                raise ValueError("Unknown native binary outside native directory")
        for name, (machine, executable) in expected.items():
            info = archive.getinfo(name)
            if info.compress_type != zipfile.ZIP_DEFLATED:
                raise ValueError("Native payload must use reviewed extraction packaging")
            data = archive.read(name)
            dependencies = elf(data, machine, executable)
            print(name, "dynamic-PIE" if executable else "JNI-shared", "SHA256=" + hashlib.sha256(data).hexdigest(),
                  "NEEDED=" + ",".join(dependencies))
    print("APK SHA256=" + hashlib.sha256(Path(apk).read_bytes()).hexdigest())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apkanalyzer")
    parser.add_argument("--apk")
    parser.add_argument("--variant", choices=("debug", "release"), default="release")
    args = parser.parse_args()
    manifest(SOURCE.read_text(encoding="utf-8"))
    # Check generated merged manifests when present, including default build additions.
    for path in (ROOT / "android/gate0-harness/build/intermediates/merged_manifests").glob(
            "*/process*Manifest/AndroidManifest.xml"):
        manifest(path.read_text(encoding="utf-8"), release="release" in path.parts)
    if bool(args.apk) != bool(args.apkanalyzer):
        raise ValueError("Supply both APK and apkanalyzer")
    if args.apk:
        command = [args.apkanalyzer]
        if os.name == "nt" and args.apkanalyzer.endswith(".bat"):
            # SDK launcher leaves its toolsdir JVM option unquoted for paths with spaces.
            java = Path(os.environ["JAVA_HOME"]) / "bin/java.exe"
            jar = Path(args.apkanalyzer).resolve().parents[1] / "lib/apkanalyzer-classpath.jar"
            command = [str(java), "-Dcom.android.sdklib.toolsdir=" + str(jar.parent.parent), "-classpath", str(jar), "com.android.tools.apk.analyzer.ApkAnalyzerCli"]
        output = subprocess.check_output([*command, "manifest", "print", args.apk],
                                         text=True, encoding="utf-8")
        manifest(output, release=args.variant == "release", packaged=True)
        inventory(args.apk)
    print("Harness manifest authority validation passed. No runtime/isolation claim.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, ET.ParseError, OSError, subprocess.CalledProcessError) as error:
        print("Harness validation failed: " + str(error), file=sys.stderr)
        sys.exit(1)
