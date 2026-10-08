#!/usr/bin/env python3
"""Conservative repository hygiene, not a security or feasibility assessment.

No dependencies beyond Python's standard library and Git. Run from any directory.
Checks working copies of tracked plus non-ignored new files (including before
staging). CI's clean checkout checks the committed tree. Markdown support is
limited to ordinary inline links and reference definitions; fragments are not
validated. External URLs are not fetched.
"""

import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
ROOT_FILES = {".editorconfig", ".gitattributes", ".gitignore", "README.md"}
ROOT_DIRS = {".github", "android", "docs"}
HISTORY = "docs/reference/privacy-decoy-history/"
SOURCE_SHA = "5320b3b44b38df4b8f3361ecbcb530386ff195e9"
ALLOWED_CODE = {
    ".github/scripts/qemu-android-research.py",
    ".github/workflows/qemu-android-research.yml",
    ".github/scripts/test-repository-validation.py",
    ".github/scripts/validate-foundation.py",
    ".github/scripts/validate-harness.py",
    ".github/workflows/android-harness.yml",
    ".github/workflows/foundation.yml",
    "android/build.gradle",
    "android/build.py",
    "android/gate0-harness/build.gradle",
    "android/gate0-harness/src/androidTest/java/org/pdva/gate0/HarnessInstrumentation.java",
    "android/gate0-harness/src/main/AndroidManifest.xml",
    "android/gate0-harness/src/main/cpp/CMakeLists.txt",
    "android/gate0-harness/src/main/cpp/probe.c",
    "android/gate0-harness/src/main/java/org/pdva/gate0/MainActivity.java",
    "android/gate0-harness/src/main/java/org/pdva/gate0/NativeProbe.java",
    "android/gate0-harness/src/main/java/org/pdva/gate0/Protocol.java",
    "android/gate0-harness/src/main/java/org/pdva/gate0/Report.java",
    "android/gate0-harness/src/main/java/org/pdva/gate0/Session.java",
    "android/gate0-harness/src/main/java/org/pdva/gate0/WorkerService.java",
    "android/gate0-harness/src/main/res/values/strings.xml",
    "android/gate0-harness/src/main/res/xml/data_extraction_rules.xml",
    "android/gate0-harness/src/test/java/org/pdva/gate0/ProtocolTest.java",
    "android/gradle.properties",
    "android/gradle/verification-metadata.xml",
    "android/settings.gradle",
}
BLOCKED_SUFFIXES = {
    ".apk", ".aab", ".apks", ".aar", ".so", ".jar", ".dex", ".o", ".a",
    ".dll", ".exe", ".bin", ".img", ".iso", ".qcow", ".qcow2", ".vdi",
    ".vmdk", ".vhd", ".vhdx", ".zip", ".gz", ".xz", ".7z", ".tar",
    ".jks", ".keystore", ".p12", ".pfx", ".pem", ".key", ".der",
    ".pcap", ".pcapng", ".hprof",
}
SECRET_NAMES = {
    "id_rsa", "id_ed25519", "credentials.json", "google-services.json",
    "key.properties", "signing.properties", "local.properties",
}
INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+[^)\n]*)?\)")
REFERENCE_LINK = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)", re.M)
REQ_DEFINITION = re.compile(r"^\|\s*(PDVA-REQ-[^\s|]+)\s*\|", re.M)


def git(*args):
    return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=ROOT)


def without_fences(text):
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            value = marker.group(1)
            if fence is None:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)


def validate():
    errors = []
    files = set(git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
                .decode("utf-8").rstrip("\0").split("\0")) - {""}
    modes = git("ls-files", "--stage", "-z").decode("utf-8").split("\0")
    for entry in filter(None, modes):
        meta, name = entry.split("\t", 1)
        mode, _, stage = meta.split()
        if mode != "100644" or stage != "0":
            errors.append(f"{name}: repository requires regular 100644 files and no conflicts")

    markdown = {}
    for name in sorted(files):
        relative = PurePosixPath(name)
        path = ROOT / name
        if len(relative.parts) == 1:
            if name not in ROOT_FILES:
                errors.append(f"{name}: unexpected root entry")
        elif relative.parts[0] not in ROOT_DIRS:
            errors.append(f"{name}: unexpected root directory")
        lower = relative.name.lower()
        if (relative.suffix.lower() in BLOCKED_SUFFIXES or lower in SECRET_NAMES
                or lower == ".env" or lower.startswith(".env.")
                or any(p.lower() in {"secrets", "credentials", "signing"} for p in relative.parts)):
            errors.append(f"{name}: prohibited artifact or sensitive filename")
        if name not in ROOT_FILES | ALLOWED_CODE and relative.suffix != ".md":
            errors.append(f"{name}: file type/path outside reviewed exact-path text scope")
        if path.is_symlink() or not path.is_file():
            errors.append(f"{name}: missing or non-regular file")
            continue
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{name}: non-UTF-8/binary content")
            continue
        if any(ord(c) < 32 and c not in "\n\r\t" for c in text):
            errors.append(f"{name}: binary/control bytes")
        if text.startswith("version https://git-lfs.github.com/spec/"):
            errors.append(f"{name}: LFS pointer not permitted in bootstrap")
        if re.search(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----", text):
            errors.append(f"{name}: private-key marker")
        if relative.suffix == ".md":
            markdown[name] = text

    for name, text in markdown.items():
        body = without_fences(text)
        links = [m.group(1).strip("<>") for pattern in (INLINE_LINK, REFERENCE_LINK)
                 for m in pattern.finditer(body)]
        for target in links:
            parts = urlsplit(target)
            if parts.scheme in {"https", "http", "mailto"}:
                continue
            if parts.scheme or parts.netloc or target.startswith(("/", "\\")):
                errors.append(f"{name}: non-portable local link {target}")
                continue
            if not parts.path:
                continue
            resolved = (ROOT / name).parent.joinpath(unquote(parts.path)).resolve()
            try:
                local = resolved.relative_to(ROOT).as_posix()
            except ValueError:
                errors.append(f"{name}: link escapes repository: {target}")
                continue
            if local not in files and not any(p.startswith(local + "/") for p in files):
                errors.append(f"{name}: missing repository link target {target}")
        if not name.startswith(HISTORY) and re.search(r"\bPD-REQ-\d+", text):
            errors.append(f"{name}: predecessor requirement numbering outside historical reference")
        if name.startswith(HISTORY):
            for required in ("Historical / non-normative", "innercoder78/Privacy-Decoy",
                             SOURCE_SHA, "Original scope:", "revalidate", "not VM-isolation evidence"):
                if required not in text:
                    errors.append(f"{name}: missing historical notice field {required}")

    register = markdown.get("docs/requirements.md", "")
    ids = REQ_DEFINITION.findall(register)
    expected = [f"PDVA-REQ-{i:03d}" for i in range(1, len(ids) + 1)]
    if not ids or ids != expected:
        errors.append("requirements: definitions must be unique, consecutive PDVA-REQ-001 onward")
    for name, text in markdown.items():
        if name != "docs/requirements.md" and REQ_DEFINITION.search(text):
            errors.append(f"{name}: requirement definitions belong only in the register")
        for token in re.findall(r"\bPDVA-REQ-[A-Za-z0-9_-]+", text):
            if not re.fullmatch(r"PDVA-REQ-\d{3}", token) or token not in ids:
                errors.append(f"{name}: malformed or undefined requirement {token}")

    adrs = sorted(p for p in files if p.startswith("docs/decisions/"))
    for i, name in enumerate(adrs, 1):
        if not re.fullmatch(rf"docs/decisions/ADR-{i:04d}-[a-z0-9-]+\.md", name):
            errors.append(f"{name}: PDVA ADR sequence must begin at ADR-0001")
    if not adrs:
        errors.append("missing PDVA ADR-0001")
    if errors:
        print("Foundation validation failed:\n" + "\n".join(f"- {e}" for e in errors))
        return 1
    print(f"Foundation validation passed: {len(files)} files, {len(markdown)} Markdown files, "
          f"{len(ids)} requirements, {len(adrs)} ADR(s). No feasibility/security claim.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(validate())
    except (OSError, subprocess.CalledProcessError, UnicodeError, ValueError) as exc:
        print(f"Foundation validation could not complete: {exc}", file=sys.stderr)
        sys.exit(1)
