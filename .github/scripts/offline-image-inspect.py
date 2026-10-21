#!/usr/bin/env python3
"""Bounded offline structural observation. Never execution or isolation evidence."""
import argparse
import bz2
from contextlib import contextmanager
import hashlib
import json
import lzma
import os
from pathlib import Path
import re
import stat
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "android/build/private-image-inspection"
CHUNK = 1024 * 1024
MAX_FILE = 64 * 1024**3
HARD_MAX = 1024**4
MAX_ITEMS = 4096
MAX_METADATA = 8 * CHUNK
MAX_EXPANDED = 8 * CHUNK
MAX_JOURNAL = 2 * CHUNK
HEX = re.compile(r"[0-9a-f]{64}\Z")


class Rejected(ValueError):
    """Fixed diagnostic codes only; never include input strings."""


def need(ok, code="invalid-structure"):
    if not ok:
        raise Rejected(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def span(offset, length, size):
    need(0 <= offset <= size and 0 <= length <= size - offset, "out-of-range")


def align(n, page):
    return (n + page - 1) // page * page


def power(n):
    return n > 0 and n & (n - 1) == 0


class Reader:
    def __init__(self, stream, size, base=0):
        self.stream, self.size, self.base = stream, size, base
        self.used = 0

    def read(self, offset, length):
        span(offset, length, self.size)
        need(length <= CHUNK and self.used + length <= 32 * CHUNK, "read-budget")
        self.used += length
        self.stream.seek(self.base + offset)
        data = self.stream.read(length)
        need(len(data) == length, "short-read")
        return data

    def unpack(self, fmt, offset=0):
        return struct.unpack(fmt, self.read(offset, struct.calcsize(fmt)))

    def u32(self, offset):
        return self.unpack("<I", offset)[0]

    def child(self, offset, length):
        span(offset, length, self.size)
        return Reader(self.stream, length, self.base + offset)


def elf(r):
    ident = r.read(0, 16)
    need(ident[:4] == b"\x7fELF" and ident[4] in (1, 2) and ident[5] in (1, 2)
         and ident[6] == 1 and not any(ident[9:]))
    endian = "<" if ident[5] == 1 else ">"
    wide = ident[4] == 2
    h = r.unpack(endian + ("HHIQQQIHHHHHH" if wide else "HHIIIIIHHHHHH"), 16)
    typ, machine, version, entry, phoff, shoff, flags, eh, pe, pn, se, sn, si = h
    need(typ in (1, 2, 3, 4) and machine != 0 and version == 1)
    need(eh == (64 if wide else 52) and pn < MAX_ITEMS and sn < MAX_ITEMS)
    need((pn == 0 and phoff == 0) or (pn > 0 and phoff >= eh and pe == (56 if wide else 32)))
    need((sn == 0 and shoff == 0 and si == 0) or
         (sn > 0 and shoff >= eh and se == (64 if wide else 40) and si < sn))
    span(phoff, pn * pe, r.size)
    span(shoff, sn * se, r.size)
    need(pn or sn, "unsupported-variant")
    for i in range(pn):
        p = r.unpack(endian + ("IIQQQQQQ" if wide else "IIIIIIII"), phoff + i * pe)
        if wide:
            pt, pf, off, va, pa, fs, ms, al = p
        else:
            pt, off, va, pa, fs, ms, pf, al = p
        span(off, fs, r.size)
        need(al in (0, 1) or power(al))
        if pt == 1:
            need(fs <= ms and (al < 2 or off % al == va % al))
    for i in range(sn):
        s = r.unpack(endian + ("IIQQQQIIQQ" if wide else "IIIIIIIIII"), shoff + i * se)
        _, st, _, _, off, size, link, _, al, ent = s
        need(link < sn and (al in (0, 1) or power(al)) and (ent == 0 or size % ent == 0))
        if st != 8:  # NOBITS occupies no file bytes.
            span(off, size, r.size)
    return {"elf_class": 64 if wide else 32, "machine": machine,
            "byte_order": ident[5], "osabi": ident[7], "abi_version": ident[8]}


def boot(r):
    need(r.read(0, 8) == b"ANDROID!")
    version = r.u32(40)
    need(version in (3, 4), "unsupported-variant")
    hs = 1580 if version == 3 else 1584
    h = r.read(0, hs)
    kernel, ramdisk, osver, header = struct.unpack_from("<4I", h, 8)
    need(header == hs and h[24:40] == bytes(16) and (kernel or ramdisk))
    sig = r.u32(1580) if version == 4 else 0
    roff = 4096 + align(kernel, 4096)
    soff = roff + align(ramdisk, 4096)
    span(0, 4096, r.size)
    span(4096, kernel, r.size)
    span(roff, ramdisk, r.size)
    span(soff, sig, r.size)
    embedded = []
    if kernel >= 16 and r.read(4096, 4) == b"\x7fELF":
        try:
            embedded.append({"format": "ELF", "role": "kernel-slot",
                             "metadata": elf(r.child(4096, kernel))})
        except Rejected:
            pass
    return {"version": version, "kernel_slot_bytes": kernel,
            "ramdisk_bytes": ramdisk, "signature_bytes": sig}, embedded


def vendor_boot(r):
    need(r.read(0, 8) == b"VNDRBOOT")
    ver, page = r.unpack("<II", 8)
    need(ver in (3, 4), "unsupported-variant")
    need(power(page) and 2048 <= page <= 65536)
    hs = 2112 if ver == 3 else 2128
    r.read(0, hs)
    need(r.u32(2096) == hs)
    ram, dtb = r.u32(24), r.u32(2100)
    need(ram > 0 and dtb > 0)
    start = align(hs, page)
    span(start, ram, r.size)
    doff = start + align(ram, page)
    span(doff, dtb, r.size)
    if ver == 4:
        table, count, esize, config = r.unpack("<4I", 2112)
        need(0 < count <= MAX_ITEMS and esize == 108 and table == count * esize)
        toff = doff + align(dtb, page)
        span(toff, table, r.size)
        ranges = []
        for i in range(count):
            size, off, kind = r.unpack("<III", toff + i * esize)
            need(size > 0 and kind <= 3)
            span(off, size, ram)
            ranges.append((off, off + size))
        nonoverlap(ranges)
        span(toff + align(table, page), config, r.size)
    return {"version": ver, "page_bytes": page, "ramdisk_bytes": ram, "dtb_bytes": dtb}


def nonoverlap(ranges):
    ordered = sorted(ranges)
    need(all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:])), "overlap")


def sparse(r):
    magic, major, minor, fh, ch, bs, blocks, count, checksum = r.unpack("<I4H4I")
    need(magic == 0xED26FF3A)
    need((major, minor, fh, ch) == (1, 0, 28, 12), "unsupported-variant")
    need(bs > 0 and bs % 4 == 0 and 0 < blocks * bs <= HARD_MAX and 0 < count <= MAX_ITEMS)
    # Checksummed sparse variants require expanded CRC accounting; stay UNKNOWN.
    need(checksum == 0, "unsupported-checksum")
    off, total = fh, 0
    for _ in range(count):
        kind, reserved, n, size = r.unpack("<HHII", off)
        need(reserved == 0 and n > 0)
        expected = {0xCAC1: n * bs, 0xCAC2: 4, 0xCAC3: 0}
        need(kind in expected, "unsupported-chunk")
        need(size == ch + expected[kind])
        span(off, size, r.size)
        off += size
        total += n
        need(total <= blocks)
    need(total == blocks and off == r.size)
    return {"block_bytes": bs, "expanded_bytes": blocks * bs, "chunks": count}


def vbmeta(r):
    h = r.read(0, 256)
    need(h[:4] == b"AVB0")
    major, minor, auth, aux, alg = struct.unpack_from(">IIQQI", h, 4)
    need(major == 1 and minor <= 3 and alg <= 6, "unsupported-variant")
    need(auth % 64 == aux % 64 == 0 and not any(h[176:]))
    span(256, auth + aux, r.size)
    pairs = [struct.unpack_from(">QQ", h, off) for off in (32, 48, 64, 80, 96)]
    for i, (off, size) in enumerate(pairs):
        span(off, size, auth if i < 2 else aux)
    nonoverlap([(o, o + n) for o, n in pairs[:2] if n])
    nonoverlap([(o, o + n) for o, n in pairs[2:] if n])
    if alg == 0:
        need(auth == 0 and all(n == 0 for _, n in pairs[:3]))
    else:
        hash_sizes = (0, 32, 32, 32, 64, 64, 64)
        sig_sizes = (0, 256, 512, 1024, 256, 512, 1024)
        need(pairs[0][1] == hash_sizes[alg] and pairs[1][1] == sig_sizes[alg]
             and pairs[2][1] == 8 + 2 * sig_sizes[alg])
    doff, dsize = pairs[4]
    need(dsize <= MAX_METADATA)
    off, count = 0, 0
    while off < dsize:
        tag, length = r.unpack(">QQ", 256 + auth + doff + off)
        need(length % 8 == 0)
        span(off, 16 + length, dsize)
        count += 1
        need(count <= MAX_ITEMS)
        off += 16 + length
    return {"algorithm": alg, "descriptors": count}


def zip_metadata(r):
    # Narrow single-disk, non-ZIP64, no descriptors/encryption/extensions.
    tail = r.read(max(0, r.size - 65557), min(r.size, 65557))
    index = tail.rfind(b"PK\x05\x06")
    need(index >= 0 and len(tail) - index >= 22)
    eocd = r.size - len(tail) + index
    _, disk, cdisk, n_disk, count, csize, coff, comment = struct.unpack_from("<4s4H2IH", tail, index)
    need(disk == cdisk == 0 and n_disk == count and count <= MAX_ITEMS)
    need(index + 22 + comment == len(tail) and csize <= MAX_METADATA)
    need(coff + csize == eocd and coff != 0xFFFFFFFF)
    span(coff, csize, r.size)
    cursor, local = coff, []
    for _ in range(count):
        h = r.unpack("<4s6H3I5H2I", cursor)
        sig, made, ver, flags, method, tm, date, crc, cs, us, nl, ex, cm, disk, ia, ea, loff = h
        need(sig == b"PK\x01\x02" and ver <= 20 and flags & ~0x800 == 0
             and method in (0, 8) and disk == 0 and ex == 0, "unsupported-zip")
        need(cs != 0xFFFFFFFF and us != 0xFFFFFFFF and nl > 0)
        span(cursor, 46 + nl + cm, coff + csize)
        name = r.read(cursor + 46, nl)
        lh = r.unpack("<4s5H3I2H", loff)
        need(lh == (b"PK\x03\x04", ver, flags, method, tm, date, crc, cs, us, nl, 0))
        need(r.read(loff + 30, nl) == name)
        end = loff + 30 + nl + cs
        span(loff, end - loff, coff)
        if method == 0:
            need(cs == us)
        local.append((loff, end))
        cursor += 46 + nl + cm
    need(cursor == coff + csize)
    nonoverlap(local)
    need((not local and coff == 0) or (local and min(local)[0] == 0))
    return {"entries": count}


def compressed(r, kind):
    need(r.size <= MAX_METADATA, "compression-input-budget")
    if kind == "GZIP":
        d = zlib.decompressobj(31)
    elif kind == "XZ":
        d = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=64 * CHUNK)
    else:
        d = bz2.BZ2Decompressor()
    off = expanded = 0
    pending = b""
    while not d.eof:
        if kind == "GZIP":
            fetch = not pending
        else:
            fetch = d.needs_input
        if fetch:
            need(off < r.size, "truncated-compression")
            pending = r.read(off, min(65536, r.size - off))
            off += len(pending)
        out = d.decompress(pending, min(65536, MAX_EXPANDED - expanded + 1))
        expanded += len(out)
        need(expanded <= MAX_EXPANDED, "compression-output-budget")
        pending = d.unconsumed_tail if kind == "GZIP" else b""
    need(off == r.size and not d.unused_data, "trailing-compression-data")
    return {"expanded_bytes": expanded}


def ext_super(r):
    s = r.read(1024, 1024)
    u = lambda off: struct.unpack_from("<I", s, off)[0]
    need(s[56:58] == b"\x53\xef" and u(76) == 1)
    shift, blocks, inodes = u(24), u(4), u(0)
    need(shift <= 6)
    bs = 1024 << shift
    need(u(96) & 0x40, "not-ext4-extents")
    need(u(96) & ~0x42 == 0 and u(100) & ~0x7 == 0, "unsupported-features")
    need(0 < blocks and 0 < inodes and u(20) == (1 if bs == 1024 else 0))
    need(0 < u(32) <= bs * 8 and 0 < u(40) <= bs * 8)
    inode_size = struct.unpack_from("<H", s, 88)[0]
    need(power(inode_size) and 128 <= inode_size <= bs)
    need(u(12) <= blocks and u(16) <= inodes and u(8) <= blocks)
    span(0, blocks * bs, r.size)
    return {"block_bytes": bs, "blocks": blocks, "inodes": inodes}


def erofs_super(r):
    s = r.read(1024, 128)
    u = lambda off: struct.unpack_from("<I", s, off)[0]
    need(u(0) == 0xE0F5E1E2 and 9 <= s[12] <= 12)
    need(u(8) == 0 and s[13] == 0 and u(80) == 0 and s[86:90] == bytes(4),
         "unsupported-features")
    bs, blocks = 1 << s[12], u(36)
    need(blocks > 0 and struct.unpack_from("<Q", s, 16)[0] > 0)
    span(0, blocks * bs, r.size)
    need(u(40) < blocks and u(44) < blocks)
    root = u(40) * bs + struct.unpack_from("<H", s, 14)[0] * 32
    span(root, 32, blocks * bs)
    inode = r.read(root, 32)
    fmt, _, mode = struct.unpack_from("<HHH", inode)
    need(fmt == 0 and mode & 0xF000 == 0x4000, "unsupported-root-inode")
    return {"block_bytes": bs, "blocks": blocks}


def lp_geometry(r):
    a, b = r.read(4096, 52), r.read(8192, 52)
    need(a == b and struct.unpack_from("<II", a) == (0x616C4467, 52))
    need(hashlib.sha256(a[:8] + bytes(32) + a[40:]).digest() == a[8:40], "geometry-checksum")
    size, slots, block = struct.unpack_from("<III", a, 40)
    need(512 <= size <= MAX_METADATA and size % 512 == 0 and 1 <= slots <= 4
         and power(block) and 512 <= block <= 65536)
    span(12288, 2 * size * slots, r.size)
    # Geometry alone cannot validate slot selection, logical extents or partitions.
    return {"metadata_slot_bytes": size, "slots": slots, "block_bytes": block}


def inspect(r):
    result = {"outer_format": "UNKNOWN", "validation": "none", "metadata": {},
              "embedded": [], "boot_evidence": "UNKNOWN", "userspace_evidence": "UNKNOWN",
              "partition_evidence": "UNKNOWN", "execution_architecture": "UNKNOWN",
              "unknowns": ["runtime-execution", "guest-host-boundary", "Android-version",
                           "provenance", "payload-semantics"], "candidate": "none"}
    head = r.read(0, min(16, r.size))
    candidates = [(b"ANDROID!", "ANDROID_BOOT", boot), (b"VNDRBOOT", "VENDOR_BOOT", vendor_boot),
                  (b"AVB0", "VBMETA", vbmeta), (b"\x3a\xff\x26\xed", "ANDROID_SPARSE", sparse),
                  (b"\x7fELF", "ELF", elf), (b"PK", "ZIP", zip_metadata),
                  (b"\x1f\x8b", "GZIP", lambda x: compressed(x, "GZIP")),
                  (b"\xfd7zXZ\x00", "XZ", lambda x: compressed(x, "XZ")),
                  (b"BZh", "BZIP2", lambda x: compressed(x, "BZIP2"))]
    for magic, name, parser in candidates:
        if head.startswith(magic):
            result["candidate"] = name
            try:
                parsed = parser(r)
                if name == "ANDROID_BOOT":
                    parsed, result["embedded"] = parsed
                    result["boot_evidence"] = "bounded-boot-container-kernel-slot-not-execution"
                elif name == "VENDOR_BOOT":
                    result["boot_evidence"] = "bounded-vendor-boot-container-no-kernel"
                result.update(outer_format=name, validation="structural-only", metadata=parsed)
                if name == "ZIP":
                    result["unknowns"].append("archive-payload-crc-and-content-unchecked")
                if name == "VBMETA":
                    result["unknowns"].append("signature-trust-and-descriptor-semantics-unchecked")
            except (Rejected, zlib.error, lzma.LZMAError, EOFError, OSError):
                result["unknowns"].append("malformed-unsupported-or-budget-limited")
            return result
    probes = [(1080, b"\x53\xef", "EXT4_SUPERBLOCK", ext_super),
              (1024, b"\xe2\xe1\xf5\xe0", "EROFS_SUPERBLOCK", erofs_super),
              (4096, b"gDla", "DYNAMIC_PARTITION_GEOMETRY", lp_geometry)]
    for offset, magic, name, parser in probes:
        if r.size >= offset + len(magic) and r.read(offset, len(magic)) == magic:
            result["candidate"] = name
            try:
                result["metadata"] = parser(r)
                result["validation"] = "limited-metadata-only"
                result["unknowns"].append("full-filesystem-or-partition-layout-unvalidated")
            except Rejected:
                result["unknowns"].append("malformed-unsupported-or-budget-limited")
            return result
    result["unknowns"].append("opaque-wrapped-encrypted-or-unrecognized-not-distinguishable")
    return result


@contextmanager
def locked(stream):
    stream.seek(0)
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        yield
    finally:
        stream.seek(0)
        if os.name == "nt":
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def journal_path(name):
    need(re.fullmatch(r"[a-z][a-z0-9-]{0,47}", name) is not None, "journal-name")
    need(name not in {"con", "prn", "aux", "nul", *["com" + str(i) for i in range(10)],
                     *["lpt" + str(i) for i in range(10)]}, "journal-name")
    need(STORE.resolve() == Path(os.path.abspath(STORE)), "redirected-storage")
    path = STORE / (name + ".jsonl")
    need(not path.is_symlink() and path.resolve().parent == STORE.resolve(), "redirected-storage")
    return path


def append(stream, records, kind, data):
    need(len(records) < 256, "journal-budget")
    record = {"version": 1, "sequence": len(records), "previous": records[-1]["hash"] if records else "0" * 64,
              "kind": kind, "data": data}
    record["hash"] = sha(canonical(record))
    raw = canonical(record) + b"\n"
    stream.seek(0, os.SEEK_END)
    need(stream.tell() + len(raw) <= MAX_JOURNAL, "journal-budget")
    need(stream.write(raw) == len(raw), "journal-write")
    stream.flush()
    os.fsync(stream.fileno())
    records.append(record)


def is_hash(v):
    return isinstance(v, str) and HEX.fullmatch(v) is not None


def identity_schema(v):
    need(isinstance(v, dict) and set(v) == {"sha256", "stat"} and is_hash(v["sha256"]))
    need(isinstance(v["stat"], list) and len(v["stat"]) == 5
         and all(type(n) is int and n >= 0 for n in v["stat"]))


def report_schema(data):
    need(set(data) == {"outer_format", "validation", "metadata", "embedded", "boot_evidence",
                       "userspace_evidence", "partition_evidence", "execution_architecture", "unknowns", "candidate"})
    formats = {"ANDROID_BOOT", "VENDOR_BOOT", "ANDROID_SPARSE", "VBMETA", "ELF", "ZIP", "GZIP", "XZ", "BZIP2"}
    limited = {"EXT4_SUPERBLOCK", "EROFS_SUPERBLOCK", "DYNAMIC_PARTITION_GEOMETRY"}
    need(data["outer_format"] in formats | {"UNKNOWN"} and data["candidate"] in formats | limited | {"none"})
    need(data["validation"] in {"none", "structural-only", "limited-metadata-only"})
    need((data["outer_format"] != "UNKNOWN") == (data["validation"] == "structural-only"))
    if data["outer_format"] != "UNKNOWN":
        need(data["candidate"] == data["outer_format"])
    if data["validation"] == "limited-metadata-only":
        need(data["candidate"] in limited)
    need(all(data[k] == "UNKNOWN" for k in ("userspace_evidence", "partition_evidence", "execution_architecture")))
    need(data["boot_evidence"] in {"UNKNOWN", "bounded-boot-container-kernel-slot-not-execution",
                                    "bounded-vendor-boot-container-no-kernel"})
    need(isinstance(data["metadata"], dict) and len(data["metadata"]) <= 8
         and all(isinstance(k, str) and re.fullmatch(r"[a-z_]{1,32}", k) and type(v) is int
                 and 0 <= v <= HARD_MAX for k, v in data["metadata"].items()))
    need(isinstance(data["embedded"], list) and len(data["embedded"]) <= 1)
    for item in data["embedded"]:
        need(isinstance(item, dict) and set(item) == {"format", "role", "metadata"}
             and item["format"] == "ELF" and item["role"] == "kernel-slot"
             and data["outer_format"] == "ANDROID_BOOT")
        need(isinstance(item["metadata"], dict) and set(item["metadata"]) ==
             {"elf_class", "machine", "byte_order", "osabi", "abi_version"}
             and all(type(v) is int and 0 <= v <= 65535 for v in item["metadata"].values()))
    need(isinstance(data["unknowns"], list) and 5 <= len(data["unknowns"]) <= 8)
    allowed = {"runtime-execution", "guest-host-boundary", "Android-version", "provenance", "payload-semantics",
               "archive-payload-crc-and-content-unchecked", "signature-trust-and-descriptor-semantics-unchecked",
               "malformed-unsupported-or-budget-limited", "full-filesystem-or-partition-layout-unvalidated",
               "opaque-wrapped-encrypted-or-unrecognized-not-distinguishable"}
    need(all(isinstance(v, str) and v in allowed for v in data["unknowns"]))


def read_journal(stream, name):
    stream.seek(0)
    raw = stream.read(MAX_JOURNAL + 1)
    need(0 < len(raw) <= MAX_JOURNAL and raw.endswith(b"\n"), "corrupt-checkpoint")
    records, state, identity, report = [], None, None, None
    transitions = {None: {"START"}, "START": {"HASH_INTENT"}, "HASH_INTENT": {"IDENTIFIED"},
                   "IDENTIFIED": {"SCAN_INTENT", "RECONCILE_INTENT"},
                   "SCAN_INTENT": {"OBSERVED", "RECONCILE_INTENT"},
                   "OBSERVED": {"VERIFY_INTENT", "RECONCILE_INTENT"},
                   "VERIFY_INTENT": {"COMPLETED", "RECONCILE_INTENT"},
                   "RECONCILE_INTENT": {"RECONCILED", "RECONCILE_INTENT"},
                   "RECONCILED": {"SCAN_INTENT", "RECONCILE_INTENT"}}
    for line in raw.splitlines():
        need(len(records) < 256)
        rec = json.loads(line)
        need(isinstance(rec, dict) and set(rec) == {"version", "sequence", "previous", "kind", "data", "hash"})
        need(canonical(rec) == line and type(rec["version"]) is int and rec["version"] == 1
             and type(rec["sequence"]) is int and rec["sequence"] == len(records))
        body = {k: v for k, v in rec.items() if k != "hash"}
        need(rec["hash"] == sha(canonical(body)) and rec["previous"] ==
             (records[-1]["hash"] if records else "0" * 64), "corrupt-checkpoint")
        kind, data = rec["kind"], rec["data"]
        need(isinstance(kind, str) and isinstance(data, dict))
        need(kind in transitions.get(state, set()) or
             (kind == "FAILED" and state not in (None, "COMPLETED", "FAILED")), "invalid-transition")
        if kind == "START":
            need(set(data) == {"journal", "path_token", "tool", "max_bytes", "scope"}
                 and data["journal"] == name and is_hash(data["path_token"]) and is_hash(data["tool"])
                 and type(data["max_bytes"]) is int and 0 < data["max_bytes"] <= HARD_MAX
                 and data["scope"] == "read-only-no-device-no-cleanup-authority")
        elif kind == "IDENTIFIED":
            identity_schema(data)
            identity = data
        elif kind == "OBSERVED":
            # Results are private and never imported as an execution instruction.
            report_schema(data)
            report = data
        elif kind == "COMPLETED":
            need(set(data) == {"identity", "report_sha256"} and data["identity"] == identity
                 and report is not None and data["report_sha256"] == sha(canonical(report)))
        else:
            need(data == {})
        records.append(rec)
        state = kind
    return records


def stat_identity(s):
    need(stat.S_ISREG(s.st_mode), "regular-file-required")
    # Windows path-stat and descriptor-stat can disagree on legacy ctime.
    # File ID, size, mtime and full content hashes remain mandatory on both.
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns,
            0 if os.name == "nt" else s.st_ctime_ns]


def fingerprint(stream, path, limit):
    before = stat_identity(os.fstat(stream.fileno()))
    need(before == stat_identity(path.stat()) and before[2] <= limit, "input-identity-or-limit")
    stream.seek(0)
    h, total = hashlib.sha256(), 0
    while total < before[2]:
        data = stream.read(min(CHUNK, before[2] - total))
        need(data, "short-read")
        total += len(data)
        h.update(data)
    need(before == stat_identity(os.fstat(stream.fileno())) == stat_identity(path.stat()), "input-mutated")
    return {"sha256": h.hexdigest(), "stat": before}


def input_path(value):
    # Explicit regular local files only. Reject device namespaces, UNC and ADS.
    p = Path(value)
    absolute = Path(os.path.abspath(p))
    need(not str(absolute).startswith(("\\\\", "//")), "local-file-required")
    if os.name == "nt":
        need(":" not in str(absolute)[len(absolute.drive):], "stream-path-rejected")
        need(not absolute.is_reserved(), "device-path-rejected")
    need(absolute.resolve() == absolute and not absolute.is_symlink(), "redirected-input")
    return absolute


def execute(name, value, resume=False, limit=MAX_FILE):
    need(type(limit) is int and 0 < limit <= HARD_MAX, "file-limit")
    path = input_path(value)
    target = journal_path(name)
    need(path != target, "input-output-alias")
    target.parent.mkdir(parents=True, exist_ok=True)
    tool = sha(Path(__file__).read_bytes())
    declared = {"journal": name, "path_token": sha(os.fsencode(str(path))), "tool": tool,
                "max_bytes": limit, "scope": "read-only-no-device-no-cleanup-authority"}
    with target.open("r+b" if resume else "x+b") as journal, locked(journal):
        if resume:
            records = read_journal(journal, name)
            need(records[0]["data"] == declared, "resume-identity-mismatch")
            need(records[-1]["kind"] not in ("START", "HASH_INTENT", "FAILED", "COMPLETED"), "unsafe-resume")
            prior = next((r["data"] for r in records if r["kind"] == "IDENTIFIED"), None)
            need(prior is not None, "unsafe-resume")
            append(journal, records, "RECONCILE_INTENT", {})
        else:
            records = []
            append(journal, records, "START", declared)
            append(journal, records, "HASH_INTENT", {})
        try:
            # Stat before open prevents accidentally opening devices/FIFOs.
            stat_identity(path.stat())
            with path.open("rb") as source:
                ident = fingerprint(source, path, limit)
                if resume:
                    need(ident == prior, "input-mutated")
                    append(journal, records, "RECONCILED", {})
                else:
                    append(journal, records, "IDENTIFIED", ident)
                append(journal, records, "SCAN_INTENT", {})
                result = inspect(Reader(source, ident["stat"][2]))
                report_schema(result)
                append(journal, records, "OBSERVED", result)
                append(journal, records, "VERIFY_INTENT", {})
                need(fingerprint(source, path, limit) == ident, "input-mutated")
                append(journal, records, "COMPLETED", {"identity": ident, "report_sha256": sha(canonical(result))})
                return result
        except Exception:
            # A partial journal append must remain corrupt; no truncation/repair.
            current = read_journal(journal, name)
            if current[-1]["kind"] not in ("COMPLETED", "FAILED"):
                append(journal, current, "FAILED", {})
            raise


class PrivateParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "STOP: invalid arguments; use --help.\n")


def main():
    need(sys.version_info >= (3, 11), "python-version")
    p = PrivateParser(description=__doc__)
    p.add_argument("command", choices=("inspect", "status", "resume"))
    p.add_argument("--journal", required=True, help="Generic local record ID; never use a sample name")
    p.add_argument("--input", help="Explicit local regular file; never searched or downloaded")
    p.add_argument("--max-bytes", type=int, default=MAX_FILE)
    args = p.parse_args()
    if args.command == "status":
        need(args.input is None, "status-arguments")
        with journal_path(args.journal).open("rb") as f:
            records = read_journal(f, args.journal)
        last = records[-1]["kind"]
        print("Checkpoint: " + (last if last in ("COMPLETED", "FAILED") else "UNKNOWN"))
        print("Private local record only; no device or cleanup authority.")
    else:
        need(args.input is not None, "explicit-input-required")
        result = execute(args.journal, args.input, args.command == "resume", args.max_bytes)
        print("Inspection recorded: " + result["outer_format"] + "; structural observation only.")
        print("Private report retained locally. Execution architecture: UNKNOWN.")


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt):
        print("STOP: inspection incomplete or rejected; preserve the private checkpoint.", file=sys.stderr)
        sys.exit(1)
