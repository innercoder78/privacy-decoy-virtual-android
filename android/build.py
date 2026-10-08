#!/usr/bin/env python3
"""Official hash-pinned Gradle bootstrap; no wrapper JAR or third-party Python modules."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
VERSION = "9.6.0"
SHA256 = "bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01"

def main():
    store = ROOT / "build" / "gradle-distribution"
    store.mkdir(parents=True, exist_ok=True)
    archive = store / ("gradle-" + VERSION + "-bin.zip")
    if not archive.exists():
        temporary = archive.with_suffix(".download")
        urllib.request.urlretrieve("https://services.gradle.org/distributions/" + archive.name, temporary)
        with temporary.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != SHA256:
                raise RuntimeError("Gradle distribution checksum mismatch")
        temporary.replace(archive)
    with archive.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != SHA256:
            raise RuntimeError("Gradle distribution checksum mismatch")
    home = store / ("gradle-" + VERSION)
    if not home.is_dir():
        with zipfile.ZipFile(archive) as z:
            for entry in z.infolist():
                target = (store / entry.filename).resolve()
                if not target.is_relative_to(store.resolve()):
                    raise RuntimeError("Unsafe distribution path")
            z.extractall(store)
    command = home / "bin" / ("gradle.bat" if os.name == "nt" else "gradle")
    if os.name != "nt":
        command.chmod(0o755)
    return subprocess.call([str(command), "-p", str(ROOT), "--no-daemon", *sys.argv[1:]])

if __name__ == "__main__":
    sys.exit(main())
