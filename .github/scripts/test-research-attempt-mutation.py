#!/usr/bin/env python3
"""Real JVM no-follow mutation control; Python/JDK only, no Android execution."""
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "android/gate0-harness/src"
GUARD = "ResearchAttempt.java"
LOOKUP = (b"Files.readAttributes(entry, BasicFileAttributes.class,\n"
          b"                            LinkOption.NOFOLLOW_LINKS)")
FOLLOWING_LOOKUP = b"Files.readAttributes(entry, BasicFileAttributes.class)"
GUARD_PASS = "Research-attempt checks passed: 217 (no Android durability claim)"
NORMAL_OUTPUT = [GUARD_PASS,
                 "Real symlink cases passed: 15 (no concurrent-mutation claim)",
                 "Protocol/report checks passed: 71"]
TRACE = ['Exception in thread "main" java.lang.AssertionError: filesystem alias admitted'] + [
    rf'\s+at org\.pdva\.gate0\.{owner}\.{method}\({owner}\.java:\d+\)'
    for owner, method in [("ResearchAttemptTest", "rejectedAlias"),
                          ("ResearchAttemptTest", "symlinks"),
                          ("ResearchAttemptTest", "run"), ("ProtocolTest", "main")]]


def mutate(source):
    lookup = LOOKUP.replace(b"\n", b"\r\n") if b"\r\n" in source else LOOKUP
    if source.count(lookup) != 1 or source.count(b"LinkOption.NOFOLLOW_LINKS") != 1:
        raise RuntimeError("Expected exactly one production no-follow entry lookup")
    return source.replace(lookup, FOLLOWING_LOOKUP, 1)


def require_mutant_rejection(result):
    lines = result.stderr.splitlines()
    if (result.returncode != 1 or result.stdout.splitlines() != [GUARD_PASS]
            or len(lines) != len(TRACE) or lines[0] != TRACE[0]
            or any(re.fullmatch(pattern, line) is None
                   for pattern, line in zip(TRACE[1:], lines[1:]))):
        raise RuntimeError("Mutant did not produce the exact filesystem alias admitted failure")


def main():
    paths = [SOURCE / "main/java/org/pdva/gate0" / name for name in
             ("Protocol.java", "Report.java", "LaunchResult.java", GUARD)] + [
             SOURCE / "test/java/org/pdva/gate0" / name for name in
             ("ResearchAttemptTest.java", "ProtocolTest.java")]
    originals = {path: path.read_bytes() for path in paths}
    mutant = mutate(originals[paths[3]])
    suffix = ".exe" if os.name == "nt" else ""
    def tool(name):
        return str(Path(os.environ["JAVA_HOME"]) / "bin" / (name + suffix)) if os.environ.get("JAVA_HOME") else name
    try:
        with tempfile.TemporaryDirectory(prefix="pdva-link-mutation-") as temporary:
            for variant in ("normal", "mutant"):
                work = Path(temporary) / variant
                classes, fixtures = work / "classes", work / "fixtures"
                classes.mkdir(parents=True)
                fixtures.mkdir()
                copies = []
                for path, content in originals.items():
                    copy = work / path.name
                    copy.write_bytes(mutant if variant == "mutant" and path.name == GUARD else content)
                    copies.append(str(copy))
                # Compilation is mandatory and outside expected-failure handling.
                subprocess.run([tool("javac"), "-Xlint:all", "-d", str(classes), *copies],
                               check=True, timeout=60)
                result = subprocess.run([tool("java"), "-Djava.io.tmpdir=" + str(fixtures),
                                         "-cp", str(classes), "org.pdva.gate0.ProtocolTest"],
                                        capture_output=True, text=True, timeout=30)
                if variant == "normal":
                    result.check_returncode()
                    if result.stdout.splitlines() != NORMAL_OUTPUT or result.stderr:
                        raise RuntimeError("Normal suite did not complete all required controls")
                    print(result.stdout, end="", flush=True)
                else:
                    require_mutant_rejection(result)
                    print("Observed required mutant failure:", flush=True)
                    print(result.stderr, end="", flush=True)
    finally:
        if any(path.read_bytes() != content for path, content in originals.items()):
            raise RuntimeError("Original production/test source changed during mutation control")
    print("PASS: NOFOLLOW_LINKS mutant rejected by filesystem alias admitted", flush=True)


if __name__ == "__main__":
    main()
