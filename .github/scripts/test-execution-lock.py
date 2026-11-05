#!/usr/bin/env python3
"""Execute real Session entry bytecode against throwing SDK stubs, never Android."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "android/gate0-harness/src"
PASS = "PASS: 200 management entry denials before Android access\n"
CALL = "        rejectResearchExecution();"


def tool(name):
    suffix = ".exe" if os.name == "nt" else ""
    return str(Path(os.environ["JAVA_HOME"]) / "bin" / (name + suffix)) if os.environ.get("JAVA_HOME") else name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--android-jar", required=True, type=Path)
    args = parser.parse_args()
    android_jar = args.android_jar.resolve(strict=True)
    names = ("Session", "ResearchAttempt", "Protocol", "Report", "LaunchResult", "NativeProbe", "WorkerService")
    paths = [SOURCE / "main/java/org/pdva/gate0" / (name + ".java") for name in names]
    paths.append(SOURCE / "test/java/org/pdva/gate0/ExecutionLockTest.java")
    original = {path: path.read_bytes() for path in paths}
    session = original[paths[0]].decode("utf-8")
    if session.count(CALL) != 1:
        raise RuntimeError("Expected exactly one unconditional execution denial call")
    variants = {"normal": CALL, "removed": "",
                "ordinary-only": "        if (!simulateDeath) rejectResearchExecution();",
                "death-only": "        if (simulateDeath) rejectResearchExecution();"}
    try:
        with tempfile.TemporaryDirectory(prefix="pdva-execution-lock-") as temporary:
            for variant, replacement in variants.items():
                work = Path(temporary) / variant
                classes, fixture = work / "classes", work / "fixture"
                classes.mkdir(parents=True)
                fixture.mkdir()
                copies = []
                for path, data in original.items():
                    copy = work / path.name
                    if path == paths[0]:
                        data = session.replace(CALL, replacement, 1).encode("utf-8")
                    copy.write_bytes(data)
                    copies.append(str(copy))
                # Compilation errors and timeouts never satisfy a negative control.
                subprocess.run([tool("javac"), "-Xlint:all", "-classpath", str(android_jar),
                                "-d", str(classes), *copies], check=True, timeout=60)
                for restart in range(3 if variant == "normal" else 1):
                    result = subprocess.run([tool("java"), "-cp", str(classes) + os.pathsep + str(android_jar),
                                             "org.pdva.gate0.ExecutionLockTest"], cwd=fixture,
                                            capture_output=True, text=True, timeout=30)
                    if list(fixture.iterdir()):
                        raise RuntimeError("Denied entry created a fixture file")
                    if variant == "normal":
                        result.check_returncode()
                        if result.stdout != PASS or result.stderr:
                            raise RuntimeError("Incomplete normal denial test")
                        print(f"Fresh JVM {restart + 1}: " + result.stdout.strip(), flush=True)
                    else:
                        if (result.returncode != 1 or result.stdout
                                or not result.stderr.startswith('Exception in thread "main" java.lang.AssertionError: '
                                                                'execution lock failed before Android access\n')
                                or "Caused by: java.lang.RuntimeException: Stub!" not in result.stderr
                                or "at android.os.Binder.<init>" not in result.stderr):
                            raise RuntimeError("Mutant did not reach the expected SDK Binder tripwire")
                        print(f"PASS: {variant} mutant detected at the SDK Binder constructor tripwire", flush=True)
    finally:
        if any(path.read_bytes() != data for path, data in original.items()):
            raise RuntimeError("Production/test sources changed during lock controls")
    print("PASS: execution lock; 600 denials, 3 fresh JVMs, 3 rejected mutants; Android runtime UNKNOWN")


if __name__ == "__main__":
    main()
