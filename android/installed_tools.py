#!/usr/bin/env python3
"""Read-only installed JDK/SDK byte comparison, never provenance approval.

Inventories are private UNTRUSTED observations. Independent authentication and
approval are deliberately outside this program; there is no local promotion flag.
"""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import xml.etree.ElementTree as ET

from build import checked_stat, check_parents, read_regular


PACKAGES = {"jdk", "platform", "build_tools"}
MAX_AGE = timedelta(days=30)  # Observation freshness, not an approval lifetime.


def require(value, message):
    if not value:
        raise ValueError(message)


def safe_name(name):
    require(isinstance(name, str) and len(name) <= 1024, "Invalid relative path")
    for part in name.split("/"):
        require(re.fullmatch(r"[A-Za-z0-9_.+ -]+", part)
                and part not in {".", ".."} and not part.endswith((".", " "))
                and part.split(".")[0].upper() not in
                {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(10)],
                 *[f"LPT{i}" for i in range(10)]}, "Invalid relative path")


def properties(data, quoted=False):
    result = {}
    for line in data.decode("utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition("=")
        require(sep and key not in result, "Ambiguous package metadata")
        if quoted:
            require(value.startswith('"') and value.endswith('"'), "Invalid JDK metadata")
            value = value[1:-1]
        result[key] = value
    return result


def identities(metadata, files, host):
    """Metadata is a claim bound to hashed bytes, not authenticated vendor data."""
    suffix = ".exe" if host == "windows" else ""
    required = {
        "jdk": ["release", "bin/java" + suffix, "bin/javac" + suffix,
                "bin/jar" + suffix, "lib/modules"],
        "platform": ["source.properties", "package.xml", "android.jar"],
        "build_tools": ["source.properties", "package.xml", "aapt2" + suffix,
                        "aidl" + suffix, "zipalign" + suffix, "lib/d8.jar",
                        "d8.bat" if host == "windows" else "d8"],
    }
    for package, names in required.items():
        require(all(name in files[package] and files[package][name]["size"] > 0
                    for name in names), "Required tool identity absent")
    jdk = properties(metadata["jdk"]["release"], quoted=True)
    require(jdk.get("IMPLEMENTOR") == "Eclipse Adoptium"
            and jdk.get("IMPLEMENTOR_VERSION", "").startswith("Temurin-17.")
            and re.fullmatch(r"17\.\d+\.\d+(?:\.\d+)?", jdk.get("JAVA_VERSION", ""))
            and jdk.get("IMAGE_TYPE") == "JDK"
            and jdk.get("OS_NAME") == ("Windows" if host == "windows" else "Linux")
            and jdk.get("OS_ARCH") == "x86_64", "Unexpected JDK identity")
    for package, package_id, revision in (
            ("platform", "platforms;android-37.0", "2"),
            ("build_tools", "build-tools;36.0.0", "36.0.0")):
        props = properties(metadata[package]["source.properties"])
        require(props.get("Pkg.Revision") == revision, "Unexpected package revision")
        if package == "platform":
            require(all(props.get(k) == v for k, v in {
                "AndroidVersion.ApiLevel": "37.0", "AndroidVersion.ExtensionLevel": "22",
                "AndroidVersion.PreviewSdkInt": "0"}.items()), "Unexpected platform identity")
        raw = metadata[package]["package.xml"]
        require(b"<!" not in raw, "Unsupported XML declaration")
        root = ET.fromstring(raw)
        packages = root.findall("localPackage")
        require(len(packages) == 1 and packages[0].get("path") == package_id,
                "Unexpected XML package identity")
        rev = packages[0].find("revision")
        expected = [2, 0, 0] if package == "platform" else [36, 0, 0]
        require(rev is not None and [int(rev.findtext(k, "0")) for k in
                ("major", "minor", "micro")] == expected
                and int(rev.findtext("preview", "0")) == 0, "Unexpected XML revision")


def scan(roots, host):
    require(set(roots) == PACKAGES, "Incomplete package selection")
    result, metadata = {}, {}
    for package, root in sorted(roots.items()):
        require(root.is_absolute() and ".." not in root.parts, "Unsafe root")
        check_parents(root)
        entries, aliases, captured = {}, set(), {}

        def visit(directory):
            before = checked_stat(directory, directory=True)
            children = sorted(directory.iterdir())
            for path in children:
                name = path.relative_to(root).as_posix()
                safe_name(name)
                require(name.casefold() not in aliases, "Aliased installed path")
                aliases.add(name.casefold())
                # lstat first: never use is_dir to follow a junction/symlink.
                if stat.S_ISDIR(path.lstat().st_mode):
                    checked_stat(path, directory=True)
                    entries[name] = {"type": "directory"}
                    visit(path)
                else:
                    data = read_regular(path)
                    entries[name] = {"type": "file", "size": len(data),
                                     "sha256": hashlib.sha256(data).hexdigest()}
                    if name in {"release", "source.properties", "package.xml"}:
                        captured[name] = data
            after = checked_stat(directory, directory=True)
            require((before.st_dev, before.st_ino, before.st_mtime_ns) ==
                    (after.st_dev, after.st_ino, after.st_mtime_ns)
                    and children == sorted(directory.iterdir()), "Directory changed during scan")

        visit(root)
        result[package], metadata[package] = entries, captured
    identities(metadata, result, host)
    return result


def timestamp(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value),
            "Invalid observation time")
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def validate(manifest, now):
    require(isinstance(manifest, dict) and set(manifest) ==
            {"schema", "trust", "observed_utc", "host", "packages"}, "Malformed manifest")
    require(type(manifest["schema"]) is int and manifest["schema"] == 1
            and manifest["trust"] == "UNTRUSTED", "Unsupported manifest or trust claim")
    require(manifest["host"] in {"windows", "linux"}, "Unsupported host")
    age = now - timestamp(manifest["observed_utc"])
    require(timedelta(0) <= age <= MAX_AGE, "Stale or future baseline")
    packages = manifest["packages"]
    require(isinstance(packages, dict) and set(packages) == PACKAGES, "Incomplete manifest")
    for entries in packages.values():
        require(isinstance(entries, dict) and entries, "Empty package inventory")
        aliases = set()
        for name, entry in entries.items():
            safe_name(name)
            require(name.casefold() not in aliases, "Aliased manifest path")
            aliases.add(name.casefold())
            require(isinstance(entry, dict), "Malformed entry")
            if entry.get("type") == "directory":
                require(set(entry) == {"type"}, "Malformed directory")
            else:
                require(set(entry) == {"type", "size", "sha256"} and entry["type"] == "file"
                        and type(entry["size"]) is int and entry["size"] >= 0
                        and isinstance(entry["sha256"], str)
                        and re.fullmatch("[0-9a-f]{64}", entry["sha256"]), "Malformed file")
            for parent in Path(name).parents:
                if parent.as_posix() != ".":
                    require(entries.get(parent.as_posix()) == {"type": "directory"},
                            "Missing manifest parent")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def load(path, now):
    manifest = json.loads(read_regular(path), object_pairs_hook=unique_object)
    validate(manifest, now)
    return manifest


def compare(manifest, roots, host, now):
    validate(manifest, now)
    require(manifest["host"] == host, "Host identity mismatch")
    require(scan(roots, host) == manifest["packages"], "Installed inventory mismatch")
    return "MATCH — UNTRUSTED; independent approval NOT ESTABLISHED"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("inventory", "compare"))
    parser.add_argument("--jdk", required=True, type=Path)
    parser.add_argument("--platform", required=True, type=Path)
    parser.add_argument("--build-tools", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    roots = {"jdk": args.jdk, "platform": args.platform, "build_tools": args.build_tools}
    now = datetime.now(timezone.utc)
    require(sys.platform in {"win32", "linux"}, "Unsupported host")
    host = "windows" if os.name == "nt" else "linux"
    if args.operation == "compare":
        print(compare(load(args.manifest, now), roots, host, now))
    else:
        # Output is private and must be outside all three input roots.
        output = args.manifest.absolute()
        require(".." not in output.parts and all(root.is_absolute() and
                not output.is_relative_to(root) for root in roots.values()),
                "Manifest must be outside installed packages")
        check_parents(output)
        manifest = {"schema": 1, "trust": "UNTRUSTED", "host": host,
                    "observed_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "packages": scan(roots, host)}
        validate(manifest, now)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, sort_keys=True, indent=2)
            stream.write("\n")
        print("Inventory created — UNTRUSTED; independent approval NOT ESTABLISHED")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, ET.ParseError, RecursionError):
        # Never print filesystem exceptions, private paths, hashes or metadata.
        print("FAIL: installed-tool check refused; no approval established", file=sys.stderr)
        sys.exit(1)
