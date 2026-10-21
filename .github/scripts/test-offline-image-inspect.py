#!/usr/bin/env python3
"""Deterministic synthetic controls. No samples, external tools or network."""
import bz2
from contextlib import redirect_stdout
import gzip
import importlib.util
import io
import json
import lzma
import os
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import zipfile

SCRIPT = Path(__file__).with_name("offline-image-inspect.py")
spec = importlib.util.spec_from_file_location("image_inspect", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def put(data, off, fmt, *values):
    struct.pack_into(fmt, data, off, *values)
    return data


def elf(wide=True, endian="<"):
    data = bytearray(120 if wide else 84)
    data[:7] = b"\x7fELF" + bytes((2 if wide else 1, 1 if endian == "<" else 2, 1))
    fmt = "HHIQQQIHHHHHH" if wide else "HHIIIIIHHHHHH"
    put(data, 16, endian + fmt, 2, 183 if wide else 40, 1, 0, 64 if wide else 52,
        0, 0, 64 if wide else 52, 56 if wide else 32, 1, 0, 0, 0)
    if wide:
        put(data, 64, endian + "IIQQQQQQ", 1, 5, 0, 0, 0, len(data), len(data), 4096)
    else:
        put(data, 52, endian + "IIIIIIII", 1, 0, 0, 0, len(data), len(data), 5, 4096)
    return data


def boot(version=4):
    data = bytearray(12288)
    data[:8] = b"ANDROID!"
    put(data, 8, "<4I", 120, 16, 0, 1584 if version == 4 else 1580)
    put(data, 40, "<I", version)
    data[4096:4216] = elf()
    return data


def vendor(version=4):
    data = bytearray(20480)
    data[:8] = b"VNDRBOOT"
    put(data, 8, "<II", version, 4096)
    put(data, 24, "<I", 32)
    put(data, 2096, "<II", 2128 if version == 4 else 2112, 16)
    if version == 4:
        put(data, 2112, "<4I", 108, 1, 108, 4)
        put(data, 12288, "<3I", 32, 0, 1)
    return data


def sparse():
    return bytearray(struct.pack("<I4H4I", 0xED26FF3A, 1, 0, 28, 12, 4096, 3, 3, 0)
                     + struct.pack("<HHII", 0xCAC1, 0, 1, 4108) + bytes(4096)
                     + struct.pack("<HHII", 0xCAC2, 0, 1, 16) + bytes(4)
                     + struct.pack("<HHII", 0xCAC3, 0, 1, 12))


def vbmeta():
    data = bytearray(320)
    data[:4] = b"AVB0"
    put(data, 4, ">IIQQI", 1, 0, 0, 64, 0)
    put(data, 96, ">QQ", 0, 16)
    put(data, 256, ">QQ", 0, 0)
    return data


def archive():
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as z:
        info = zipfile.ZipInfo("synthetic", date_time=(2020, 1, 1, 0, 0, 0))
        z.writestr(info, b"synthetic fixture")
    return bytearray(output.getvalue())


def ext4():
    data = bytearray(8192)
    for off, val in {0: 8, 4: 8, 20: 1, 32: 8, 40: 8, 76: 1, 96: 0x40}.items():
        put(data, 1024 + off, "<I", val)
    put(data, 1080, "<H", 0xEF53)
    put(data, 1112, "<H", 128)
    return data


def erofs():
    data = bytearray(8192)
    put(data, 1024, "<I", 0xE0F5E1E2)
    data[1036] = 12
    put(data, 1040, "<Q", 1)
    put(data, 1060, "<II", 2, 1)
    put(data, 4096, "<HHH", 0, 0, 0x41ED)
    return data


def geometry():
    data = bytearray(20480)
    g = bytearray(52)
    put(g, 0, "<II", 0x616C4467, 52)
    put(g, 40, "<III", 4096, 1, 4096)
    g[8:40] = m.hashlib.sha256(g).digest()
    data[4096:4148] = data[8192:8244] = g
    return data


def scan(data):
    return m.inspect(m.Reader(io.BytesIO(data), len(data)))


class FormatTests(unittest.TestCase):
    def test_boot_versions_and_embedded_elf(self):
        for version in (3, 4):
            r = scan(boot(version))
            self.assertEqual(r["outer_format"], "ANDROID_BOOT")
            self.assertEqual(r["embedded"][0]["metadata"]["machine"], 183)
            self.assertEqual(r["execution_architecture"], "UNKNOWN")

    def test_vendor_versions(self):
        for v in (3, 4):
            self.assertEqual(scan(vendor(v))["outer_format"], "VENDOR_BOOT")

    def test_sparse_all_supported_chunks(self):
        r = scan(sparse())
        self.assertEqual(r["outer_format"], "ANDROID_SPARSE")
        self.assertEqual(r["metadata"]["expanded_bytes"], 12288)
        self.assertEqual(r["partition_evidence"], "UNKNOWN")

    def test_vbmeta_is_structural_not_trust(self):
        r = scan(vbmeta())
        self.assertEqual(r["outer_format"], "VBMETA")
        self.assertIn("signature-trust-and-descriptor-semantics-unchecked", r["unknowns"])

    def test_elf_classes_and_endianness(self):
        for wide in (True, False):
            for endian in ("<", ">"):
                self.assertEqual(scan(elf(wide, endian))["outer_format"], "ELF")

    def test_zip_metadata(self):
        r = scan(archive())
        self.assertEqual(r["outer_format"], "ZIP")
        self.assertEqual(r["metadata"], {"entries": 1})
        self.assertIn("archive-payload-crc-and-content-unchecked", r["unknowns"])

    def test_compression_complete_streams(self):
        for name, fn in (("GZIP", lambda d: gzip.compress(d, mtime=0)), ("XZ", lzma.compress), ("BZIP2", bz2.compress)):
            r = scan(fn(b"deterministic" * 10))
            self.assertEqual(r["outer_format"], name)
            self.assertEqual(r["metadata"]["expanded_bytes"], 130)

    def test_filesystem_metadata_is_not_validated_filesystem(self):
        for make, name in ((ext4, "EXT4_SUPERBLOCK"), (erofs, "EROFS_SUPERBLOCK"), (geometry, "DYNAMIC_PARTITION_GEOMETRY")):
            r = scan(make())
            self.assertEqual(r["outer_format"], "UNKNOWN")
            self.assertEqual(r["candidate"], name)
            self.assertEqual(r["validation"], "limited-metadata-only")
            self.assertEqual(r["userspace_evidence"], "UNKNOWN")

    def test_truncated_headers_and_magic_only(self):
        for make in (boot, vendor, sparse, vbmeta, elf, archive):
            data = make()
            for length in (0, 1, 4, 8, 16, 27):
                with self.subTest(format=make.__name__, length=length):
                    self.assertEqual(scan(data[:length])["outer_format"], "UNKNOWN")

    def test_boot_bounds_reserved_and_unsupported(self):
        for off, val in ((8, 0xFFFFFFFF), (12, 0xFFFFFFFF), (20, 0), (24, 1), (40, 2), (40, 5), (1580, 0xFFFFFFFF)):
            self.assertEqual(scan(put(boot(), off, "<I", val))["outer_format"], "UNKNOWN")

    def test_bad_embedded_elf_does_not_become_kernel_proof(self):
        data = boot()
        put(data, 4096 + 32, "<Q", 0xFFFFFFFF)
        r = scan(data)
        self.assertEqual(r["outer_format"], "ANDROID_BOOT")
        self.assertEqual(r["embedded"], [])

    def test_vendor_out_of_range_partition_and_table(self):
        for off, val in ((12, 3), (2100, 0xFFFFFFFF), (2112, 1), (2116, 4097), (12292, 33)):
            self.assertEqual(scan(put(vendor(), off, "<I", val))["outer_format"], "UNKNOWN")

    def test_sparse_bad_lengths_totals_variants(self):
        for off, fmt, val in ((4, "<H", 2), (12, "<I", 3), (16, "<I", 2), (20, "<I", 4097),
                              (24, "<I", 1), (28, "<H", 0xCAC4), (36, "<I", 4096)):
            self.assertEqual(scan(put(sparse(), off, fmt, val))["outer_format"], "UNKNOWN")
        self.assertEqual(scan(sparse() + b"x")["outer_format"], "UNKNOWN")

    def test_vbmeta_bad_offsets_algorithm_descriptor(self):
        for off, fmt, val in ((4, ">I", 2), (12, ">Q", 63), (28, ">I", 7), (64, ">Q", 1000),
                              (96, ">Q", 65), (264, ">Q", 16), (176, "B", 1)):
            self.assertEqual(scan(put(vbmeta(), off, fmt, val))["outer_format"], "UNKNOWN")

    def test_elf_invalid_tables_segments_and_extended_counts(self):
        for off, fmt, val in ((32, "<Q", 1000), (52, "<H", 1), (56, "<H", 0xFFFF),
                              (72, "<Q", 121), (96, "<Q", 121), (104, "<Q", 1), (112, "<Q", 3)):
            self.assertEqual(scan(put(elf(), off, fmt, val))["outer_format"], "UNKNOWN")

    def test_zip_bad_directory_local_header_and_unsupported(self):
        original = archive()
        cd = original.index(b"PK\x01\x02")
        eo = original.index(b"PK\x05\x06")
        for off, fmt, val in ((cd + 42, "<I", 0xFFFFFF00), (cd + 20, "<I", 0xFFFFFF00),
                              (cd + 8, "<H", 1), (eo + 16, "<I", 1), (0, "B", 0), (18, "<I", 1)):
            self.assertEqual(scan(put(bytearray(original), off, fmt, val))["outer_format"], "UNKNOWN")
        self.assertEqual(scan(original[:-1])["outer_format"], "UNKNOWN")

    def test_compressed_truncation_crc_trailing_and_bomb(self):
        for fn in (lambda d: gzip.compress(d, mtime=0), lzma.compress, bz2.compress):
            good = fn(b"synthetic")
            for bad in (good[:-1], good + b"x", good + good):
                self.assertEqual(scan(bad)["outer_format"], "UNKNOWN")
            self.assertEqual(scan(fn(bytes(m.MAX_EXPANDED + 1)))["outer_format"], "UNKNOWN")
        bad = bytearray(gzip.compress(b"fixture", mtime=0))
        bad[-8] ^= 1
        self.assertEqual(scan(bad)["outer_format"], "UNKNOWN")

    def test_filesystem_bounds_features_and_magic_only(self):
        for make, off, fmt, val in ((ext4, 1028, "<I", 0xFFFFFFFF), (ext4, 1120, "<I", 0xFFFFFFFF),
                                   (erofs, 1060, "<I", 0xFFFFFFFF), (erofs, 1104, "<I", 8),
                                   (geometry, 4136, "<I", 0xFFFFFFFF)):
            r = scan(put(make(), off, fmt, val))
            self.assertEqual(r["validation"], "none")
            self.assertEqual(r["metadata"], {})
        for offset, magic in ((1080, b"\x53\xef"), (1024, b"\xe2\xe1\xf5\xe0"), (4096, b"gDla")):
            data = bytearray(16384)
            data[offset:offset + len(magic)] = magic
            self.assertEqual(scan(data)["validation"], "none")

    def test_geometry_valid_checksum_but_out_of_range_metadata(self):
        data = geometry()
        g = bytearray(data[4096:4148])
        put(g, 40, "<I", 8192)
        g[8:40] = bytes(32)
        g[8:40] = m.hashlib.sha256(g).digest()
        data[4096:4148] = data[8192:8244] = g
        self.assertEqual(scan(data)["validation"], "none")

    def test_vendor_ramdisk_overlap_rejected(self):
        data = vendor()
        put(data, 2112, "<4I", 216, 2, 108, 4)
        put(data, 12288, "<3I", 24, 0, 1)
        put(data, 12396, "<3I", 16, 16, 1)
        self.assertEqual(scan(data)["outer_format"], "UNKNOWN")

    def test_opaque_and_misleading_embedded_strings(self):
        for data in (random.Random(37).randbytes(8192), b"x" * 30 + boot(),
                     b"system/framework kernel Android boot" * 100):
            self.assertEqual(scan(data)["outer_format"], "UNKNOWN")

    def test_read_bounds_and_budget(self):
        r = m.Reader(io.BytesIO(bytes(32)), 32)
        for off, size in ((-1, 1), (0, -1), (31, 2), (33, 0), (0, m.CHUNK + 1)):
            with self.assertRaises(m.Rejected):
                r.read(off, size)
        r.used = 32 * m.CHUNK
        with self.assertRaises(m.Rejected):
            r.read(0, 1)

    def test_large_sparse_file_bounded_reads(self):
        # A real seek-created 5 GiB logical file. No whole-file allocation/read.
        with tempfile.TemporaryFile() as f:
            f.seek(5 * 1024**3 - 1)
            f.write(b"\0")
            f.flush()
            r = m.Reader(f, 5 * 1024**3)
            self.assertEqual(m.inspect(r)["outer_format"], "UNKNOWN")
            self.assertLess(r.used, 1024)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        m.STORE.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=m.STORE)
        self.addCleanup(self.temp.cleanup)
        self.store = Path(self.temp.name)
        self.patch = patch.object(m, "STORE", self.store)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.sample = self.store / "synthetic.dat"
        self.sample.write_bytes(boot())
        self.name = "control"

    def records(self):
        with m.journal_path(self.name).open("rb") as f:
            return m.read_journal(f, self.name)

    def interrupted(self):
        with patch.object(m, "inspect", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                m.execute(self.name, self.sample)
        self.assertEqual(self.records()[-1]["kind"], "SCAN_INTENT")

    def test_success_hash_receipt_and_readonly_sample(self):
        before = self.sample.read_bytes()
        result = m.execute(self.name, self.sample)
        records = self.records()
        self.assertEqual([r["kind"] for r in records], ["START", "HASH_INTENT", "IDENTIFIED", "SCAN_INTENT", "OBSERVED", "VERIFY_INTENT", "COMPLETED"])
        self.assertEqual(records[-1]["data"]["report_sha256"], m.sha(m.canonical(result)))
        self.assertEqual(before, self.sample.read_bytes())
        raw = m.journal_path(self.name).read_bytes()
        self.assertNotIn(str(self.sample).encode(), raw)

    def test_resume_reconciles_and_reexecutes(self):
        self.interrupted()
        m.execute(self.name, self.sample, resume=True)
        records = self.records()
        self.assertEqual(records[-1]["kind"], "COMPLETED")
        self.assertEqual([r["kind"] for r in records][4:7], ["RECONCILE_INTENT", "RECONCILED", "SCAN_INTENT"])

    def test_changed_input_blocks_resume(self):
        self.interrupted()
        self.sample.write_bytes(vendor())
        with self.assertRaises(m.Rejected):
            m.execute(self.name, self.sample, resume=True)
        self.assertEqual(self.records()[-1]["kind"], "FAILED")

    def test_mutation_during_inspection_is_not_completed(self):
        real = m.inspect
        def mutate(r):
            result = real(r)
            with self.sample.open("r+b") as f:
                f.seek(8192)
                f.write(b"mutation")
            return result
        with patch.object(m, "inspect", side_effect=mutate):
            with self.assertRaises(m.Rejected):
                m.execute(self.name, self.sample)
        self.assertEqual(self.records()[-1]["kind"], "FAILED")

    def test_hash_detects_same_metadata_content_mutation(self):
        with self.sample.open("rb") as f:
            first = m.fingerprint(f, self.sample, m.MAX_FILE)
            with self.sample.open("r+b") as out:
                out.seek(8192)
                out.write(b"changed")
            # Controlled stat oracle holds all metadata constant; bytes still differ.
            with patch.object(m, "stat_identity", return_value=first["stat"]):
                second = m.fingerprint(f, self.sample, m.MAX_FILE)
        self.assertNotEqual(first["sha256"], second["sha256"])

    def test_interruption_before_identity_cannot_resume(self):
        with patch.object(m, "fingerprint", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                m.execute(self.name, self.sample)
        with self.assertRaises(m.Rejected):
            m.execute(self.name, self.sample, resume=True)
        self.assertEqual(self.records()[-1]["kind"], "HASH_INTENT")

    def test_completed_and_failed_cannot_resume(self):
        m.execute(self.name, self.sample)
        with self.assertRaises(m.Rejected):
            m.execute(self.name, self.sample, resume=True)
        with self.assertRaises(FileExistsError):
            m.execute(self.name, self.sample)
        with patch.object(m, "inspect", side_effect=OSError):
            with self.assertRaises(OSError):
                m.execute("failed", self.sample)
        with self.assertRaises(m.Rejected):
            m.execute("failed", self.sample, resume=True)

    def test_input_cannot_alias_new_journal(self):
        target = m.journal_path(self.name)
        with self.assertRaises(m.Rejected):
            m.execute(self.name, target)
        self.assertFalse(target.exists())

    def test_final_verification_interruption_remains_unknown(self):
        real = m.fingerprint
        calls = []
        def stop_second(*args):
            calls.append(1)
            if len(calls) == 2:
                raise KeyboardInterrupt
            return real(*args)
        with patch.object(m, "fingerprint", side_effect=stop_second):
            with self.assertRaises(KeyboardInterrupt):
                m.execute(self.name, self.sample)
        self.assertEqual(self.records()[-1]["kind"], "VERIFY_INTENT")
        m.execute(self.name, self.sample, resume=True)
        self.assertEqual(self.records()[-1]["kind"], "COMPLETED")

    def test_resume_interrupted_during_reconciliation_rehashes_again(self):
        self.interrupted()
        with patch.object(m, "fingerprint", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                m.execute(self.name, self.sample, resume=True)
        self.assertEqual(self.records()[-1]["kind"], "RECONCILE_INTENT")
        m.execute(self.name, self.sample, resume=True)
        self.assertEqual(self.records()[-1]["kind"], "COMPLETED")

    def test_oversized_checkpoint_rejected_before_parse(self):
        target = m.journal_path(self.name)
        target.write_bytes(b"x" * (m.MAX_JOURNAL + 1))
        with self.assertRaises(m.Rejected):
            self.records()

    def test_resume_wrong_path_tool_limit_and_name(self):
        self.interrupted()
        other = self.store / "other.dat"
        other.write_bytes(self.sample.read_bytes())
        for path, limit in ((other, m.MAX_FILE), (self.sample, 100000)):
            with self.assertRaises(m.Rejected):
                m.execute(self.name, path, resume=True, limit=limit)
        with patch.object(m, "sha", return_value="a" * 64):
            with self.assertRaises(m.Rejected):
                m.execute(self.name, self.sample, resume=True)
        with self.assertRaises(m.Rejected):
            with m.journal_path(self.name).open("rb") as f:
                m.read_journal(f, "other")

    def test_missing_unreadable_nonregular_and_file_limit(self):
        self.sample.unlink()
        with self.assertRaises(FileNotFoundError):
            m.execute(self.name, self.sample)
        self.assertEqual(self.records()[-1]["kind"], "FAILED")
        self.sample.write_bytes(boot())
        with self.assertRaises(m.Rejected):
            m.execute("limit", self.sample, limit=1)
        with self.assertRaises(m.Rejected):
            m.execute("directory", self.store)
        real = Path.open
        def denied(path, *args, **kwargs):
            if path == self.sample:
                raise PermissionError("synthetic private diagnostic")
            return real(path, *args, **kwargs)
        with patch.object(Path, "open", denied):
            with self.assertRaises(PermissionError):
                m.execute("unreadable", self.sample)

    def test_corrupt_empty_truncated_duplicate_and_bad_hash(self):
        self.interrupted()
        path = m.journal_path(self.name)
        good = path.read_bytes()
        for bad in (b"", good[:-1], good + good.splitlines()[0] + b"\n", good.replace(b'SCAN_INTENT', b'SCAN_BROKEN'), b"{}\n"):
            path.write_bytes(bad)
            with self.assertRaises((m.Rejected, ValueError)):
                m.execute(self.name, self.sample, resume=True)
            self.assertEqual(path.read_bytes(), bad)
        path.write_bytes(good)

    def test_rehashed_illegal_transition_and_forged_receipt(self):
        self.interrupted()
        with m.journal_path(self.name).open("r+b") as f:
            records = m.read_journal(f, self.name)
            m.append(f, records, "COMPLETED", {})
        with self.assertRaises(m.Rejected):
            self.records()

    def test_fsync_failure_prevents_inspection(self):
        with patch.object(m.os, "fsync", side_effect=OSError), patch.object(m, "inspect") as inspector:
            with self.assertRaises(OSError):
                m.execute(self.name, self.sample)
        inspector.assert_not_called()
        self.assertNotEqual(self.records()[-1]["kind"], "COMPLETED")

    def test_partial_write_not_repaired(self):
        self.interrupted()
        path = m.journal_path(self.name)
        with path.open("ab") as f:
            f.write(b'{"version":')
        before = path.read_bytes()
        with self.assertRaises(m.Rejected):
            m.execute(self.name, self.sample, resume=True)
        self.assertEqual(before, path.read_bytes())

    def test_journal_names_and_storage_redirect(self):
        for name in ("../escape", "con", "nul", "com1", "a/b", "a:b", "x" * 49):
            with self.assertRaises(m.Rejected):
                m.journal_path(name)
        with patch.object(m, "STORE", self.store / ".." / self.store.name):
            # abspath intentionally normalizes ..; no escape remains.
            self.assertEqual(m.journal_path("normal").resolve().parent, self.store)

    def test_real_process_interruption_concurrent_writer_and_resume(self):
        # Only this repository-owned Python control executes. Handshake precedes kill.
        child = """
import importlib.util, pathlib, sys, time
spec = importlib.util.spec_from_file_location('scanner', sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.STORE = pathlib.Path(sys.argv[2])
def pause(reader):
    (m.STORE / 'ready').write_text('READY')
    print('READY', flush=True)
    time.sleep(30)
m.inspect = pause
m.execute('control', pathlib.Path(sys.argv[3]))
"""
        proc = subprocess.Popen([sys.executable, "-u", "-c", child, str(SCRIPT), str(self.store), str(self.sample)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if (self.store / 'ready').exists():
                    break
                self.assertIsNone(proc.poll(), "control process exited before handshake")
                time.sleep(0.02)
            else:
                self.fail("control never reached persisted scan intent")
            with self.assertRaises(OSError):
                m.execute(self.name, self.sample, resume=True)
            proc.kill()
            stdout, stderr = proc.communicate(timeout=10)
            self.assertIn("READY", stdout)
            self.assertEqual(stderr, "")
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(self.records()[-1]["kind"], "SCAN_INTENT")
            self.assertEqual(len(self.records()), 4)
            m.execute(self.name, self.sample, resume=True)
            self.assertEqual(self.records()[-1]["kind"], "COMPLETED")
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.communicate(timeout=10)

    def test_cli_sanitizes_invalid_args_and_failures(self):
        for args in (["inspect", "--journal", "bad/name", "--input", "private-marker"],
                     ["unknown-private-marker"], ["inspect", "--journal", "sample", "--max-bytes", "private-marker"]):
            result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("private-marker", result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_cli_success_and_readonly_status_are_sanitized(self):
        output = io.StringIO()
        with patch.object(sys, "argv", [str(SCRIPT), "inspect", "--journal", self.name, "--input", str(self.sample)]), redirect_stdout(output):
            m.main()
        path = m.journal_path(self.name)
        before = path.read_bytes()
        with patch.object(sys, "argv", [str(SCRIPT), "status", "--journal", self.name]), redirect_stdout(output):
            m.main()
        self.assertEqual(path.read_bytes(), before)
        self.assertIn("Checkpoint: COMPLETED", output.getvalue())
        self.assertNotIn(str(self.sample), output.getvalue())
        self.assertNotIn(m.sha(self.sample.read_bytes()), output.getvalue())

    def test_report_schema_rejects_claims_and_private_strings(self):
        result = scan(boot())
        for key, value in (("execution_architecture", "independent"), ("outer_format", "private-marker"),
                           ("metadata", {"private": "private-marker"}), ("unknowns", ["private-marker"] * 5)):
            altered = dict(result, **{key: value})
            with self.assertRaises(m.Rejected):
                m.report_schema(altered)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped or result.testsRun == 0:
        sys.exit(1)
