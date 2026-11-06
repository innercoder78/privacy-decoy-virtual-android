#!/usr/bin/env python3
"""Official hash-pinned Gradle bootstrap; no wrapper JAR or third-party Python modules."""
import hashlib
import io
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
VERSION = "9.6.0"
SHA256 = "bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01"


def checked_stat(path, directory=False):
    value = path.lstat()
    if (stat.S_ISLNK(value.st_mode)
            or getattr(value, "st_file_attributes", 0) & 0x400
            or not (stat.S_ISDIR(value.st_mode) if directory else stat.S_ISREG(value.st_mode))
            or (not directory and value.st_nlink != 1)):
        raise RuntimeError("Unsafe distribution filesystem type")
    return value


def check_parents(path):
    for parent in reversed(path.absolute().parents):
        checked_stat(parent, directory=True)


def read_regular(path):
    check_parents(path)
    before = checked_stat(path)
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(os.open(path, flags), "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)):
            raise RuntimeError("Distribution file changed during validation")
        data = stream.read()
        after = os.fstat(stream.fileno())
    def identity(value):
        # Windows path stat synthesizes executable bits from .bat/.exe suffixes;
        # descriptor stat does not. Compare the actual type there.
        mode = stat.S_IFMT(value.st_mode) if os.name == "nt" else value.st_mode
        return (value.st_dev, value.st_ino, mode, value.st_nlink,
                value.st_size, value.st_mtime_ns)
    final = path.lstat()
    if (identity(before) != identity(after) or identity(final) != identity(after)
            or before.st_ctime_ns != final.st_ctime_ns
            or opened.st_ctime_ns != after.st_ctime_ns):
        raise RuntimeError("Distribution file changed during validation")
    return data


def distribution_manifest(z):
    """Reject ambiguous Windows/Linux names and types before creating anything."""
    root = "gradle-" + VERSION
    entries, directories, files, aliases = set(), set(), {}, {}
    for entry in z.infolist():
        name = entry.filename[:-1] if entry.is_dir() else entry.filename
        parts = name.split("/")
        if (entry.orig_filename != entry.filename or parts[0] != root
                or any(not re.fullmatch(r"[A-Za-z0-9_.+-]+", part)
                       or part in (".", "..") or part.endswith(".")
                       or part.split(".")[0].upper() in
                       {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(10)],
                        *[f"LPT{i}" for i in range(10)]} for part in parts)):
            raise RuntimeError("Unsafe distribution path")
        kind = stat.S_IFMT(entry.external_attr >> 16)
        if (kind not in (0, stat.S_IFDIR if entry.is_dir() else stat.S_IFREG)
                or entry.flag_bits & 1 or (entry.is_dir() and entry.file_size)):
            raise RuntimeError("Unsafe distribution archive type")
        if name in entries:
            raise RuntimeError("Conflicting distribution entries")
        entries.add(name)
        for i in range(1, len(parts) + 1):
            prefix = "/".join(parts[:i])
            if aliases.setdefault(prefix.casefold(), prefix) != prefix:
                raise RuntimeError("Conflicting distribution entries")
        directories.update("/".join(parts[:i]) for i in range(1, len(parts)))
        if entry.is_dir():
            directories.add(name)
            z.read(entry)  # Also validate directory CRC/local header.
        else:
            data = z.read(entry)  # CRC, truncation and local-header checks.
            files[name] = (len(data), hashlib.sha256(data).digest(), entry)
    if directories & files.keys() or root not in directories:
        raise RuntimeError("Conflicting distribution entries")
    for command in ("bin/gradle", "bin/gradle.bat"):
        if root + "/" + command not in files:
            raise RuntimeError("Missing distribution launcher")
    return directories, files


def validate_installation(store, home, directories, files):
    check_parents(home)
    found_dirs, found_files = set(), set()

    def visit(directory):
        checked_stat(directory, directory=True)
        found_dirs.add(directory.relative_to(store).as_posix())
        for path in sorted(directory.iterdir()):
            name = path.relative_to(store).as_posix()
            if name in directories:
                visit(path)
            elif name in files:
                data = read_regular(path)
                if (len(data), hashlib.sha256(data).digest()) != files[name][:2]:
                    raise RuntimeError("Installed distribution content mismatch")
                found_files.add(name)
            else:
                raise RuntimeError("Unexpected installed distribution entry")

    visit(home)
    if found_dirs != directories or found_files != files.keys():
        raise RuntimeError("Missing installed distribution entry")


def prepare_distribution(archive, store):
    # Hash and parse the SAME immutable snapshot, not a subsequently reopened ZIP.
    data = read_regular(archive)
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise RuntimeError("Gradle distribution checksum mismatch")
    home = store / ("gradle-" + VERSION)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        directories, files = distribution_manifest(z)
        if not os.path.lexists(home):
            check_parents(home)
            # Exclusive creation: failures leave all evidence; never repair/reuse
            # a partial installation or overwrite a competing creator's files.
            for name in sorted(directories, key=lambda value: (value.count("/"), value)):
                target = store / name
                check_parents(target)
                target.mkdir()
            for name, (_, _, entry) in sorted(files.items()):
                target = store / name
                check_parents(target)
                with target.open("xb") as output, z.open(entry) as source:
                    shutil.copyfileobj(source, output)
            if os.name != "nt":
                (home / "bin" / "gradle").chmod(0o755)
        validate_installation(store, home, directories, files)
    return home


def admit_verification_input(argument=None, property_key=None):
    """Reserve verification policy for reviewed source, not caller overrides."""
    reserved = "org.gradle.dependency.verification"
    if property_key is not None:
        key = property_key.casefold()
        prohibited = key in {reserved, "systemprop." + reserved,
                            "org.gradle.project." + reserved}
    else:
        option = argument.lstrip("-").split("=", 1)[0]
        names = {"dependency-verification", "write-verification-metadata",
                 "refresh-keys", "export-keys"}
        prohibited = (option in {"F", "M"} or option in names
                      or (len(option) > 1 and any(n.startswith(option) for n in names)))
        if not argument.startswith("--"):
            # Attached short values are supported. Clusters containing these
            # argument-taking aliases are ambiguous and refused conservatively.
            # D/P/x consume attached values; do not search inside those values.
            prohibited |= (option.startswith(("F", "M"))
                           or re.match(r"[qwidsSmtavh?VU]+[FM]", option) is not None)
    if prohibited:
        raise RuntimeError("Gradle dependency verification override refused") from None


def admit_startup(arguments, environment, user_home):
    """Bound known startup inputs, not configuration/cache or tool provenance."""
    def reject():
        # Never echo caller values, private paths or filesystem exception details.
        raise RuntimeError("Unreviewed or ambiguous Gradle startup configuration") from None

    injected = {"JAVA_OPTS", "GRADLE_OPTS", "JAVA_TOOL_OPTIONS",
                "JDK_JAVA_OPTIONS", "_JAVA_OPTIONS"}
    properties = {"gradle.user.home", "user.home", "user.dir", "gradle.home",
                  "org.gradle.jvmargs"}

    def check_property(value):
        # Windows environment keys are case-insensitive; refuse case ambiguity
        # for these few reserved keys on both hosts.
        key = value.split("=", 1)[0].casefold()
        admit_verification_input(property_key=key)
        if not key or key in properties or key.removeprefix("systemprop.") in properties:
            reject()

    for name, value in environment.items():
        if name in injected and value:
            reject()
        if name.startswith("ORG_GRADLE_PROJECT_"):
            check_property(name[len("ORG_GRADLE_PROJECT_"):])

    prohibited = {"init-script", "gradle-user-home", "project-dir", "include-build"}
    property_options = {"system-prop", "project-prop", "D", "P"}
    pending_property = False
    for argument in arguments:
        if (not argument or any(c in argument for c in '\"\r\n\x00')
                or (os.name == "nt" and any(c in argument for c in "%!^&|<>"))):
            reject()
        if pending_property:
            if argument.startswith("-"):
                reject()
            check_property(argument)
            pending_property = False
            continue
        if not argument.startswith("-"):
            continue
        admit_verification_input(argument=argument)
        option, separator, value = argument.lstrip("-").partition("=")
        # Gradle accepts single-dash long names and double-dash short names.
        # Reject truncated long spellings too, without relying on Gradle errors.
        if (option in {"I", "g", "p"} or option in prohibited
                or (len(option) > 1 and any(p.startswith(option) for p in prohibited))):
            reject()
        if option in property_options:
            if separator:
                check_property(value)
            else:
                pending_property = True
        elif argument.startswith(("-D", "-P")) and not argument.startswith("--"):
            check_property(argument[2:])
        elif not argument.startswith("--"):
            # Attached short values and clusters must not conceal a prohibited alias.
            # These registered long options win over their first short letter;
            # -x consumes its attached value as an excluded task name.
            if option in {"profile", "parallel", "priority", "project-cache-dir"}:
                continue
            if (option.startswith(("I", "g", "p"))
                    or re.match(r"[qwidsSmtavh?V]+[Igp]", option)):
                reject()
        elif option and any(p.startswith(option) for p in property_options):
            reject()
    if pending_property:
        reject()

    try:
        if (not user_home.is_absolute() or ".." in user_home.parts
                or not environment.get("GRADLE_USER_HOME", "default")
                or any(c in str(user_home) for c in '\"\r\n\x00')
                or (os.name == "nt" and any(c in str(user_home) for c in "%!^&|<>"))):
            reject()
        # Metadata only: no home listing, script/property reads, cache inspection,
        # creation, repair or deletion. Refuse even an empty init.d entry.
        for directory in [*reversed(user_home.parents), user_home]:
            try:
                checked_stat(directory, directory=True)
            except FileNotFoundError:
                continue
        for name in ("init.gradle", "init.gradle.kts", "init.gradle.dcl", "init.d"):
            try:
                (user_home / name).lstat()
            except FileNotFoundError:
                continue
            reject()
    except (OSError, ValueError, RuntimeError):
        reject()


def main():
    arguments = sys.argv[1:]
    environment = dict(os.environ)
    user_home = (Path(environment["GRADLE_USER_HOME"]) if "GRADLE_USER_HOME" in environment
                 else Path.home() / ".gradle")
    admit_startup(arguments, environment, user_home)
    store = ROOT / "build" / "gradle-distribution"
    for directory in [*reversed(store.absolute().parents), store]:
        if not os.path.lexists(directory):
            directory.mkdir()
        checked_stat(directory, directory=True)
    archive = store / ("gradle-" + VERSION + "-bin.zip")
    check_parents(archive)
    if not os.path.lexists(archive):
        temporary = archive.with_suffix(".download")
        with temporary.open("xb") as output:
            with urllib.request.urlopen("https://services.gradle.org/distributions/" + archive.name) as source:
                shutil.copyfileobj(source, output)
        if hashlib.sha256(read_regular(temporary)).hexdigest() != SHA256:
            raise RuntimeError("Gradle distribution checksum mismatch")
        with archive.open("xb") as output, temporary.open("rb") as source:
            shutil.copyfileobj(source, output)
    home = prepare_distribution(archive, store)
    command = home / "bin" / ("gradle.bat" if os.name == "nt" else "gradle")
    return subprocess.call([str(command), "-p", str(ROOT), "--no-daemon",
                            "-g", str(user_home), *arguments], env=environment)

if __name__ == "__main__":
    sys.exit(main())
