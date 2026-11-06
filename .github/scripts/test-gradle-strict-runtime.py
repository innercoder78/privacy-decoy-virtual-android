#!/usr/bin/env python3
"""Bounded Linux CI experiment; real Gradle, generated local data, no downloads."""
import hashlib
from html.parser import HTMLParser
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
STRICT = "--dependency-verification=strict"
BAD = "0" * 64
EXCEPTION = "org.gradle.api.internal.artifacts.verification.exceptions.DependencyVerificationException"
BUILD = r'''
import groovy.json.JsonOutput
import java.security.MessageDigest
repositories {
    maven { url = uri('repo'); metadataSources { mavenPom() } }
}
configurations { probe { canBeConsumed = false; transitive = false } }
dependencies { probe 'org.pdva.fixture:sample:1.0' }
tasks.register('resolveFixture') {
    doLast {
        def receipt = [mode: gradle.startParameter.dependencyVerificationMode.name(),
                       gradle: gradle.gradleVersion,
                       java: System.getProperty('java.version'),
                       vendor: System.getProperty('java.vendor'),
                       offline: gradle.startParameter.offline]
        try {
            def files = configurations.probe.resolve()
            if (files.size() != 1) throw new GradleException('Unexpected artifact count')
            def artifact = files.iterator().next()
            receipt.artifact = artifact.name
            receipt.sha256 = MessageDigest.getInstance('SHA-256').digest(artifact.bytes).encodeHex().toString()
            receipt.resolved = true
        } catch (Exception failure) {
            receipt.resolved = false
            receipt.causes = []
            def cause = failure
            while (cause != null && receipt.causes.size() < 20) {
                receipt.causes.add(cause.class.name)
                cause = cause.cause
            }
            throw failure
        } finally {
            file('receipt.json').text = JsonOutput.toJson(receipt)
        }
    }
}
'''
POM = b'''<project xmlns="http://maven.apache.org/POM/4.0.0">
<modelVersion>4.0.0</modelVersion><groupId>org.pdva.fixture</groupId>
<artifactId>sample</artifactId><version>1.0</version><packaging>jar</packaging>
</project>
'''


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run(command, cwd, environment):
    # Bound the launcher AND any single-use daemon descendants on timeout.
    with subprocess.Popen(command, cwd=cwd, env=environment, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True, start_new_session=True) as child:
        try:
            output, _ = child.communicate(timeout=90)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.communicate()
            raise RuntimeError("Gradle fixture timed out; not a verification result") from None
    return child.returncode, output


class ReportText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def main():
    require(sys.platform == "linux" and os.environ.get("GITHUB_ACTIONS") == "true",
            "This experiment requires the existing GitHub-hosted Linux CI route")
    spec = importlib.util.spec_from_file_location("bootstrap", ROOT / "android/build.py")
    bootstrap = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bootstrap)
    store = ROOT / "android/build/gradle-distribution"
    archive = store / ("gradle-" + bootstrap.VERSION + "-bin.zip")
    installation = store / ("gradle-" + bootstrap.VERSION)
    # Validation only: never download, extract, repair or change the installation.
    archive_bytes = bootstrap.read_regular(archive)
    require(digest(archive_bytes) == bootstrap.SHA256, "Distribution ZIP pin mismatch")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as source:
        directories, files = bootstrap.distribution_manifest(source)
    bootstrap.validate_installation(store, installation, directories, files)
    production_metadata = ROOT / "android/gradle/verification-metadata.xml"
    production_before = production_metadata.read_bytes()
    java = Path(os.environ["JAVA_HOME"])
    require(java == Path(os.environ["JAVA_HOME_17_X64"]), "CI-selected JDK 17 required")
    require((java / "bin/java").is_file(), "Selected Java launcher missing")
    jar_buffer = io.BytesIO()
    with zipfile.ZipFile(jar_buffer, "w", compression=zipfile.ZIP_STORED) as jar:
        for name, data in [("META-INF/MANIFEST.MF", b"Manifest-Version: 1.0\r\n\r\n"),
                           ("fixture.txt", b"PDVA generated checksum fixture v1\n")]:
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            jar.writestr(entry, data)
    jar_bytes = jar_buffer.getvalue()
    jar_sha = digest(jar_bytes)
    require(jar_sha != BAD, "Invalid negative-control checksum")
    print(json.dumps({"gradle": bootstrap.VERSION, "distribution_sha256": bootstrap.SHA256,
                      "jar_sha256": jar_sha, "pom_sha256": digest(POM),
                      "runner_sha256": digest(Path(__file__).read_bytes()),
                      "build_fixture_sha256": digest(BUILD.encode()),
                      "java_launcher_sha256": digest((java / "bin/java").read_bytes()),
                      "java_release_sha256": digest((java / "release").read_bytes())}), flush=True)
    with tempfile.TemporaryDirectory(prefix="pdva-strict-", dir=ROOT / "android/build") as temporary:
        root = Path(temporary)
        count = 0
        # Each pair starts cold. The option-removal invocation reuses ONLY its own
        # fixture inputs/cache; no real user-home or Android cache is consulted.
        for name, location, mode, good in [
                ("good", None, None, True), ("bad", None, None, False),
                ("project-off", "project", "off", False),
                ("project-lenient", "project", "lenient", False),
                ("user-off", "user", "off", False),
                ("user-lenient", "user", "lenient", False)]:
            case = root / name
            project, user, home = case / "project", case / "gradle-home", case / "home"
            for directory in (project / "gradle", user, home, case / "tmp"):
                directory.mkdir(parents=True)
            repository = project / "repo/org/pdva/fixture/sample/1.0"
            repository.mkdir(parents=True)
            (repository / "sample-1.0.jar").write_bytes(jar_bytes)
            (repository / "sample-1.0.pom").write_bytes(POM)
            (project / "settings.gradle").write_text("rootProject.name = 'pdva-strict-fixture'\n")
            (project / "build.gradle").write_text(BUILD)
            expected = jar_sha if good else BAD
            metadata = f'''<?xml version="1.0" encoding="UTF-8"?>
<verification-metadata xmlns="https://schema.gradle.org/dependency-verification">
<configuration><verify-metadata>true</verify-metadata><verify-signatures>false</verify-signatures></configuration>
<components><component group="org.pdva.fixture" name="sample" version="1.0">
<artifact name="sample-1.0.jar"><sha256 value="{expected}"/></artifact>
<artifact name="sample-1.0.pom"><sha256 value="{digest(POM)}"/></artifact>
</component></components></verification-metadata>
'''
            (project / "gradle/verification-metadata.xml").write_text(metadata)
            if location:
                target = project if location == "project" else user
                (target / "gradle.properties").write_text(f"org.gradle.dependency.verification={mode}\n")
            protected = {p: p.read_bytes() for p in case.rglob("*") if p.is_file()}
            environment = {"JAVA_HOME": str(java), "PATH": str(java / "bin") + ":/usr/bin:/bin",
                           "HOME": str(home), "GRADLE_USER_HOME": str(user),
                           "TMPDIR": str(case / "tmp"), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}
            command = [str(installation / "bin/gradle"), "-p", str(project), "--no-daemon",
                       "-g", str(user), STRICT, "--offline", "--console=plain", "--stacktrace",
                       "--no-build-cache", "--no-configuration-cache", "--max-workers=1",
                       "-Duser.home=" + str(home), "-Djava.io.tmpdir=" + str(case / "tmp"),
                       "-Dorg.gradle.dependency.verification.console=verbose", "resolveFixture"]
            for strict in ([True, False] if location else [True]):
                invocation = command if strict else [arg for arg in command if arg != STRICT]
                receipt_path = project / "receipt.json"
                if receipt_path.exists():
                    receipt_path.unlink()  # Only the prior generated receipt in this fixture.
                code, output = run(invocation, project, environment)
                if not receipt_path.is_file():
                    # Only this generated fixture's diagnostics; redact host locations.
                    safe = output.replace(str(ROOT), "<checkout>").replace(str(java), "<jdk>")
                    print(safe[-6000:], flush=True)
                require(receipt_path.is_file(), name + ": task not reached (infrastructure/parser error)")
                receipt = json.loads(receipt_path.read_text())
                selected = "STRICT" if strict else mode.upper()
                require(receipt["mode"] == selected and receipt["offline"] is True,
                        name + ": unexpected selected mode/offline state")
                require(receipt["gradle"] == "9.6.0" and receipt["java"].startswith("17."),
                        name + ": unexpected Gradle/JDK identity")
                rejected = not good and strict
                if rejected:
                    require(code != 0 and receipt["resolved"] is False
                            and EXCEPTION in receipt["causes"] and EXCEPTION in output,
                            name + ": not an actual dependency-verification exception")
                else:
                    require(code == 0 and receipt["resolved"] is True
                            and receipt["artifact"] == "sample-1.0.jar"
                            and receipt["sha256"] == jar_sha,
                            name + ": exact local artifact was not successfully resolved")
                if rejected or selected == "LENIENT":
                    require("Dependency verification failed" in output
                            and BAD in output and jar_sha in output and "sample-1.0.jar" in output,
                            name + ": missing specific checksum mismatch diagnostic")
                    reports = list(project.glob("build/reports/dependency-verification/**/dependency-verification-report.html"))
                    require(bool(reports), name + ": missing Gradle verification report")
                    texts = []
                    for report in reports:
                        parser = ReportText()
                        parser.feed(report.read_text())
                        texts.append(re.sub(r"\s+", " ", " ".join(parser.parts)))
                    detail = f"Expected a sha256 checksum of {BAD} but was {jar_sha}"
                    require(any(detail in text and "sample-1.0.jar" in text for text in texts),
                            name + ": report does not establish expected/actual checksum mismatch")
                require(all(path.read_bytes() == data for path, data in protected.items()),
                        name + ": fixture inputs changed")
                count += 1
                print(json.dumps({"case": name, "trusted_strict_option": strict,
                                  "exit": code, "outcome": "checksum-rejected" if rejected else "resolved",
                                  "receipt": receipt}), flush=True)
        require(count == 10, "Incomplete runtime control matrix")
    bootstrap.validate_installation(store, installation, directories, files)
    require(production_metadata.read_bytes() == production_before, "Production metadata changed")
    print("PASS: 10 real offline Gradle controls; installation and production metadata preserved", flush=True)


if __name__ == "__main__":
    main()
