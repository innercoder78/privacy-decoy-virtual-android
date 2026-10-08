#!/usr/bin/env python3
"""Exact zero-permission manifest and artifact checks; no Android runtime claim."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
A = "{http://schemas.android.com/apk/res/android}"
SOURCE = ROOT / "android/gate0-harness/src/main/AndroidManifest.xml"

def manifest(text, release=False):
    root = ET.fromstring(text)
    if any("permission" in item.tag for item in root):
        raise ValueError("Manifest permission declaration")
    app = root.find("application")
    if app is None or app.get(A + "allowBackup") != "false":
        raise ValueError("Backup must be disabled")
    if release and app.get(A + "debuggable", "false") != "false":
        raise ValueError("Release must not be debuggable")
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apkanalyzer")
    parser.add_argument("--apk")
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
        manifest(output, release=True)
    print("Harness manifest authority validation passed. No runtime/isolation claim.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, ET.ParseError, OSError, subprocess.CalledProcessError) as error:
        print("Harness validation failed: " + str(error), file=sys.stderr)
        sys.exit(1)
