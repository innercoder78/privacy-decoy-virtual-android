#!/usr/bin/env python3
"""Offline genuine compiled controls. Disposable APKs are unsigned, never installable evidence."""
import argparse
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import subprocess
import struct
import tempfile
import unittest
import warnings
import xml.etree.ElementTree as ET
import zipfile


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


h = load("validate-harness")
d = load("desktop-readiness")


class CompiledPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="compiled-rules-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.counter = 0
        cls.aapt = h.aapt2_path(ARGS.apkanalyzer)
        # Mandatory real positive; no mock analyzer or synthetic ELF on this path.
        with redirect_stdout(io.StringIO()):
            cls.positive = h.inspect_apk(ARGS.apk, ARGS.apkanalyzer, "release")
        cls.policy = h.RULES.read_text(encoding="utf-8")

    def fixture(self, policy=None, reference="@xml/data_extraction_rules", extra=None):
        type(self).counter += 1
        work = self.work / str(self.counter)
        work.mkdir()
        res = work / "res/xml"
        res.mkdir(parents=True)
        (res / "data_extraction_rules.xml").write_text(
            self.policy if policy is None else policy, encoding="utf-8")
        if extra:
            name, value = extra
            target = work / "res" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(value, encoding="utf-8")
        root = ET.fromstring(h.SOURCE.read_text(encoding="utf-8"))
        root.set("package", "org.pdva.gate0")
        ET.SubElement(root, "uses-sdk", {h.A + "minSdkVersion": "30", h.A + "targetSdkVersion": "37"})
        app = root.find("application")
        app.set(h.A + "extractNativeLibs", "true")
        if reference is None:
            del app.attrib[h.A + "dataExtractionRules"]
        else:
            app.set(h.A + "dataExtractionRules", reference)
        manifest = work / "AndroidManifest.xml"
        ET.ElementTree(root).write(manifest, encoding="utf-8", xml_declaration=True)
        compiled, linked = work / "compiled.zip", work / "linked.apk"
        for command in ([str(self.aapt), "compile", "--dir", str(work / "res"), "-o", str(compiled)],
                        [str(self.aapt), "link", "-o", str(linked), "--manifest", str(manifest),
                         "-I", str(ARGS.android_jar), str(compiled)]):
            subprocess.run(command, check=True, capture_output=True, timeout=120)
        # Replace only manifest/resources in a disposable copy; never sign/install.
        with zipfile.ZipFile(ARGS.apk) as original, zipfile.ZipFile(linked) as resources:
            entries = {n: original.read(n) for n in original.namelist()
                       if n not in {"AndroidManifest.xml", "resources.arsc"}
                       and not n.startswith(("res/", "META-INF/"))}
            entries.update({n: resources.read(n) for n in resources.namelist()})
        return self.write(work / "control.apk", entries)

    def write(self, path, entries):
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, value in entries.items():
                archive.writestr(name, value)
        return path

    def rejected(self, path, reason):
        with redirect_stdout(io.StringIO()), self.assertRaisesRegex(
                (ValueError, KeyError, subprocess.CalledProcessError, ET.ParseError), reason):
            h.inspect_apk(path, ARGS.apkanalyzer, "release")

    def test_real_apk_and_recompiled_policy_pass(self):
        self.assertEqual(self.positive["extraction_rules"]["policy"], "all-domains-excluded-v1")
        with redirect_stdout(io.StringIO()):
            result = h.inspect_apk(self.fixture(), ARGS.apkanalyzer, "release")
        self.assertEqual(result["native"], self.positive["native"])

    def test_compiled_policy_mutations(self):
        mutations = {}
        for section in ("cloud-backup", "device-transfer"):
            root = ET.fromstring(self.policy)
            root.remove(root.find(section))
            mutations["missing-" + section] = ET.tostring(root, encoding="unicode")
            for domain in ("root", "sharedpref", "device_root", "device_sharedpref"):
                root = ET.fromstring(self.policy)
                node = root.find(section)
                node.remove(next(x for x in node if x.get("domain") == domain))
                mutations[section + "-missing-" + domain] = ET.tostring(root, encoding="unicode")
        mutations.update({
            "path": self.policy.replace('path="."', 'path="subdir"', 1),
            "domain": self.policy.replace('domain="root"', 'domain="unknown"', 1),
            "include": self.policy.replace("<exclude", "<include", 1),
            "duplicate-domain": self.policy.replace('domain="root"', 'domain="file"', 1),
            "section-attribute": self.policy.replace("<cloud-backup>", '<cloud-backup disableIfNoEncryptionCapabilities="true">'),
            "duplicate-section": self.policy.replace("device-transfer", "cloud-backup"),
            "wrong-root": self.policy.replace("data-extraction-rules", "full-backup-content"),
            "nested-rule": self.policy.replace('<exclude domain="root" path="." />', '<exclude domain="root" path="."><include domain="file" path="." /></exclude>', 1),
        })
        for name, policy in mutations.items():
            with self.subTest(case=name):
                self.rejected(self.fixture(policy), "Extraction policy")

    def test_compiled_reference_mutations(self):
        self.rejected(self.fixture(reference=None), "dataExtractionRules")
        # aapt2 correctly refuses to link a nonexistent symbol. Mutate exactly
        # one typed reference in the real compiled manifest, preserving its size.
        with zipfile.ZipFile(ARGS.apk) as archive:
            entries = {n: archive.read(n) for n in archive.namelist()}
        old = struct.pack("<I", int(self.positive["extraction_rules"]["resource_id"], 16))
        raw = entries["AndroidManifest.xml"]
        self.assertEqual(raw.count(old), 1)
        entries["AndroidManifest.xml"] = raw.replace(old, struct.pack("<I", 0x7f02ffff))
        self.rejected(self.write(self.work / "nonexistent.apk", entries), "Extraction resource")
        self.rejected(self.fixture(reference="@xml/other", extra=("xml/other.xml", self.policy)), "Extraction resource")
        self.rejected(self.fixture(extra=("xml-v31/data_extraction_rules.xml", self.policy)), "Extraction resource")

    def test_missing_replaced_truncated_and_duplicate_payload(self):
        entry = self.positive["extraction_rules"]["entry"]
        with zipfile.ZipFile(ARGS.apk) as archive:
            entries = {n: archive.read(n) for n in archive.namelist()}
        missing = dict(entries)
        del missing[entry]
        self.rejected(self.write(self.work / "missing.apk", missing), "archive")
        for name, raw in (("truncated", entries[entry][:-1]), ("text", self.policy.encode()),
                          ("malformed", entries[entry][:8] + b"\xff" * (len(entries[entry]) - 8))):
            with self.subTest(case=name):
                self.rejected(self.write(self.work / (name + ".apk"), dict(entries, **{entry: raw})),
                              "Extraction|returned non-zero|syntax error|no element found")
        stale = self.fixture(self.policy.replace('path="."', 'path="old"', 1))
        with zipfile.ZipFile(stale) as archive:
            replacement = archive.read("res/xml/data_extraction_rules.xml")
        self.rejected(self.write(self.work / "replaced.apk", dict(entries, **{entry: replacement})), "Extraction policy")
        duplicate = self.write(self.work / "duplicate.apk", entries)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(duplicate, "a") as archive:
                archive.writestr(entry, entries[entry])
        self.rejected(duplicate, "Duplicate APK entry")

    def test_real_journal_completion_and_policy_failure(self):
        paths = {}
        with zipfile.ZipFile(ARGS.apk) as archive:
            for i, name in enumerate(self.positive["native"]):
                paths[name] = self.work / (str(i) + ".native")
                paths[name].write_bytes(archive.read(name))
        invalid = self.fixture(self.policy.replace("device-transfer", "cloud-backup"))
        for name, apk, expected in (("positive", ARGS.apk, "COMPLETED"), ("negative", invalid, "FAILED")):
            build = {"source": d.git("rev-parse", "HEAD"), "apk_sha256": d.file_hash(apk), "variant": "release"}
            journal = self.work / (name + ".jsonl")
            d.initialize(journal, build)
            d.mutate(journal, build, "inspection", "PREPARED")
            if expected == "COMPLETED":
                d.execute(journal, build, "inspection", apk, ARGS.apkanalyzer, paths)
            else:
                with self.assertRaisesRegex(ValueError, "Extraction policy"):
                    d.execute(journal, build, "inspection", apk, ARGS.apkanalyzer, paths)
            self.assertEqual(d.status(journal)["operations"]["inspection"]["state"], expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--apkanalyzer", type=Path, required=True)
    parser.add_argument("--android-jar", type=Path, required=True)
    ARGS = parser.parse_args()
    unittest.main(argv=[__file__], verbosity=2)
