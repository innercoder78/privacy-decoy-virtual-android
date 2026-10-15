#!/usr/bin/env python3
"""Research-only ARM64 FD snapshot primitive and Linux controls, NOT QEMU wiring.

The generated C uses unchanged SHA-256 functions from the already pinned GLib.
No guest, Android target, or QEMU process is executed. See the evidence record.
"""
import hashlib
import os
from pathlib import Path
import platform
import stat
import struct
import subprocess

CHECKSUM_SHA256 = '55e03a7ed5d654419a24505f39f73bacdbe79d3f2d8075b2724f34c3133dede1'


def checksum_source(data):
    if hashlib.sha256(data).hexdigest() != CHECKSUM_SHA256:
        raise RuntimeError('GLib checksum identity mismatch')
    text = data.decode('utf-8')
    # Preserve both the file license and SHA-256 attribution. No function edits.
    return (text[:text.index('*/') + 2] + '\n' +
            text[text.index('#define SHA256_DATASIZE'):text.index('/* SHA2 is common')] +
            text[text.index('/* adapted from the SHA256 implementation'):
                 text.index('static gchar *\nsha256_sum_to_string')])


PRELUDE = r'''
#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
typedef uint32_t guint32;
typedef uint8_t guint8;
typedef unsigned char guchar;
typedef size_t gsize;
#define G_STMT_START do
#define G_STMT_END while (0)
_Static_assert(sizeof(off_t) >= 8, "64-bit positional IO required");
'''

# Original PDVA research code. No pathname, QEMU state, or boot publication API.
ADAPTER = r'''
enum pdva_result {
    PDVA_OK, PDVA_ARGUMENT, PDVA_FD, PDVA_SIZE, PDVA_ALLOC, PDVA_IO,
    PDVA_CHANGED, PDVA_DIGEST, PDVA_HEADER, PDVA_RANGE, PDVA_CLOSE
};
#define PDVA_FILE_MAX (16ULL * 1024 * 1024)
#define PDVA_IMAGE_MAX (64ULL * 1024 * 1024)
#define PDVA_READ_MAX 8192U
#define PDVA_CHUNK 65536U
struct pdva_request {
    uint32_t version;       /* exactly 1: raw ARM64 subset, no mode fallback */
    uint64_t length;        /* exact file length, not header image_size */
    uint8_t sha256[32];     /* trusted controller input; NOT origin authentication */
    uint64_t ram_base, ram_size;
};
struct pdva_snapshot {
    uint8_t *bytes;         /* owned private copy; release after consumption */
    size_t length;
    uint64_t entry, image_size;
};
static uint64_t pdva_le64(const uint8_t *p) {
    uint64_t n = 0;
    for (unsigned i = 0; i < 8; i++) { n |= (uint64_t)p[i] << (8 * i); }
    return n;
}
static int pdva_stat(int fd, struct stat *s) {
    for (unsigned i = 0; i < 8; i++) {
        if (fstat(fd, s) == 0) { return 0; }
        if (errno != EINTR) { break; }
    }
    return -1;
}
static int pdva_flags(int fd) {
    for (unsigned i = 0; i < 8; i++) {
        int flags = fcntl(fd, F_GETFL);
        if (flags >= 0 || errno != EINTR) { return flags; }
    }
    return -1;
}
static int pdva_same(const struct stat *a, const struct stat *b) {
    return a->st_dev == b->st_dev && a->st_ino == b->st_ino &&
        a->st_mode == b->st_mode && a->st_size == b->st_size &&
        a->st_mtim.tv_sec == b->st_mtim.tv_sec &&
        a->st_mtim.tv_nsec == b->st_mtim.tv_nsec &&
        a->st_ctim.tv_sec == b->st_ctim.tv_sec &&
        a->st_ctim.tv_nsec == b->st_ctim.tv_nsec;
}
void pdva_snapshot_release(struct pdva_snapshot *s) {
    if (s) { free(s->bytes); memset(s, 0, sizeof(*s)); }
}
/* Consumes fd on ALL returns (including invalid arguments); never duplicates it.
 * Caller grants exclusive descriptor-table ownership for the duration. It must
 * not close/reuse fd concurrently. req/out must be valid, disjoint private objects;
 * out->bytes must be NULL. Failure leaves *out byte-for-byte unchanged.
 * Blocking regular-file IO needs an external wall-clock supervisor. Iteration
 * budgets cannot bound a single kernel call. This is not hostile-code isolation.
 */
enum pdva_result pdva_snapshot_take(int fd, const struct pdva_request *req,
                                     struct pdva_snapshot *out) {
    enum pdva_result result = PDVA_ARGUMENT;
    struct stat before, after;
    uint8_t *bytes = NULL;
    size_t done = 0;
    uint64_t entry = 0, image_size = 0;
    Sha256sum hash;
    if (!req || !out || out->bytes || req->version != 1) { goto finish; }
    if (req->length < 68 || req->length > PDVA_FILE_MAX ||
        req->length > SIZE_MAX || req->length > INT64_MAX) {
        result = PDVA_SIZE; goto finish;
    }
    result = PDVA_FD;
    int flags = pdva_flags(fd);
    if (flags < 0 || (flags & O_ACCMODE) != O_RDONLY || (flags & O_PATH) ||
        (flags & O_DIRECT) || pdva_stat(fd, &before) != 0 ||
        !S_ISREG(before.st_mode)) { goto finish; }
    result = PDVA_SIZE;
    if (before.st_size < 0 || (uint64_t)before.st_size != req->length) { goto finish; }
    result = PDVA_ALLOC;
    bytes = malloc((size_t)req->length);
    if (!bytes) { goto finish; }
    result = PDVA_IO;
    for (unsigned calls = 0; done < req->length && calls < PDVA_READ_MAX; calls++) {
        size_t n = (size_t)req->length - done;
        if (n > PDVA_CHUNK) { n = PDVA_CHUNK; }
        ssize_t got = pread(fd, bytes + done, n, (off_t)done);
        if (got < 0 && errno == EINTR) { continue; }
        if (got <= 0 || (size_t)got > n) { goto finish; }
        done += (size_t)got;
    }
    if (done != req->length) { goto finish; }
    result = PDVA_CHANGED;
    if (pdva_stat(fd, &after) != 0 || !pdva_same(&before, &after)) { goto finish; }
    /* Hash precisely the private bytes subsequently parsed and returned. A
     * same-size writer may evade metadata detection; it cannot change this copy.
     * Matching a digest is only as trustworthy as the expected digest's source.
     */
    sha256_sum_init(&hash);
    sha256_sum_update(&hash, bytes, done);
    sha256_sum_close(&hash);
    result = PDVA_DIGEST;
    if (memcmp(hash.digest, req->sha256, 32) != 0) { goto finish; }
    result = PDVA_HEADER;
    /* Deliberately narrow, non-EFI raw Image subset: forward B, code1=0,
     * fixed 512-KiB offset, modern nonzero size, LE/4K/low placement flags,
     * reserved fields and PE offset zero. No decompression or legacy fallback.
     * This is an admission grammar, NOT proof the bytes are a bootable kernel.
     */
    uint64_t code = pdva_le64(bytes);
    uint64_t branch = (code & UINT64_C(0x01ffffff)) << 2;
    if ((code >> 32) || (code & UINT64_C(0xfe000000)) != UINT64_C(0x14000000) ||
        branch < 64 || branch > req->length - 4 ||
        pdva_le64(bytes + 8) != UINT64_C(0x80000) ||
        pdva_le64(bytes + 24) != 2 || pdva_le64(bytes + 32) ||
        pdva_le64(bytes + 40) || pdva_le64(bytes + 48) ||
        memcmp(bytes + 56, "ARM\x64\0\0\0\0", 8) != 0) { goto finish; }
    image_size = pdva_le64(bytes + 16);
    if (image_size < req->length || image_size > PDVA_IMAGE_MAX) { goto finish; }
    result = PDVA_RANGE;
    if (req->ram_base % (2ULL * 1024 * 1024) ||
        req->ram_size > UINT64_MAX - req->ram_base ||
        req->ram_base + req->ram_size > (UINT64_C(1) << 48) ||
        req->ram_size < UINT64_C(0x80000) ||
        image_size > req->ram_size - UINT64_C(0x80000)) { goto finish; }
    entry = req->ram_base + UINT64_C(0x80000);
    result = PDVA_OK;
finish:
    /* Linux close may have already released the number on EINTR. Never retry
     * and accidentally close a reused descriptor. Close error blocks publication.
     */
    if (fd >= 0 && close(fd) != 0 && result == PDVA_OK) { result = PDVA_CLOSE; }
    if (result != PDVA_OK) { free(bytes); return result; }
    struct pdva_snapshot ready = { bytes, done, entry, image_size };
    *out = ready; /* The only publication, after validation AND descriptor close. */
    return PDVA_OK;
}
'''

# Syscall and allocation observers surround the actual adapter, not a mock of it.
OBSERVER = r'''
static int fault, calls, stats, flag_calls, closes, live, allocs, writer = -1;
#define CHECK(c, m) do { if (!(c)) { fprintf(stderr, "FAIL: %s\n", m); exit(90); } } while (0)
static void *observed_malloc(size_t n) {
    CHECK(n <= 16U * 1024 * 1024, "allocation bound"); allocs++;
    if (fault == 5) { return NULL; }
    void *p = malloc(n); if (p) { live++; } return p;
}
static void observed_free(void *p) { if (p) { live--; } free(p); }
static int observed_close(int fd) {
    closes++; int r = close(fd);
    if (fault == 6) { errno = EINTR; return -1; }
    return r;
}
static int observed_flags(int fd, int command) {
    flag_calls++; CHECK(command == F_GETFL, "fcntl operation");
    if (fault == 11 || (fault == 12 && flag_calls < 3)) { errno = EINTR; return -1; }
    return fcntl(fd, command);
}
static int observed_stat(int fd, struct stat *s) {
    stats++;
    if (fault == 9 || (fault == 10 && stats < 3)) { errno = EINTR; return -1; }
    if (fault == 13 && stats == 2) { errno = EIO; return -1; }
    return fstat(fd, s);
}
static ssize_t observed_pread(int fd, void *p, size_t n, off_t off) {
    calls++;
    CHECK(n <= 65536 && off >= 0 && calls <= 8192, "read bounds");
    if (fault == 2 || (fault == 1 && calls <= 2)) { errno = EINTR; return -1; }
    if (fault == 3) { return 0; }
    if (fault == 4) { errno = EIO; return -1; }
    if (fault == 7 && calls == 2) { CHECK(ftruncate(writer, 1) == 0, "truncate backing"); }
    if (fault == 8 && calls == 2) {
        uint8_t v = 99; CHECK(pwrite(writer, &v, 1, off) == 1, "change backing");
        /* A size change makes the metadata assertion deterministic even on a
         * filesystem with coarse timestamp resolution. Same-size change is
         * separately tested against the controller's pre-change digest. */
        struct stat s; CHECK(fstat(writer, &s) == 0 && ftruncate(writer, s.st_size + 1) == 0,
                             "grow backing");
    }
    if (fault == 14) { return (ssize_t)n + 1; }
    if (fault == 16 && n > 1) { n = 1; }
    if ((fault == 1 || fault == 7 || fault == 8) && n > 17) { n = 17; }
    return pread(fd, p, n, off);
}
static void denied_path(void) { fputs("DENIED: adapter pathname/fallback\n", stderr); exit(93); }
/* These are compile-time call-boundary observers, not a seccomp sandbox. */
#define open(...) (denied_path(), -1)
#define openat(...) (denied_path(), -1)
#define fopen(...) (denied_path(), (FILE *)0)
#define g_file_get_contents(...) (denied_path(), 0)
#define malloc observed_malloc
#define free observed_free
#define pread observed_pread
#define fstat observed_stat
#define fcntl observed_flags
#define close observed_close
'''

DRIVER = r'''
#undef malloc
#undef free
#undef pread
#undef fstat
#undef fcntl
#undef close
static uint64_t number(const char *p) {
    char *end; errno = 0; unsigned long long n = strtoull(p, &end, 10);
    CHECK(!errno && *p && !*end, "numeric control input"); return n;
}
int main(int argc, char **argv) {
    CHECK(argc == 10, "control arguments");
    int fd = atoi(argv[1]); fault = atoi(argv[2]); writer = atoi(argv[9]);
    struct pdva_request req = { .version = (uint32_t)number(argv[8]),
        .length = number(argv[3]), .ram_base = number(argv[5]), .ram_size = number(argv[6]) };
    CHECK(strlen(argv[4]) == 64, "digest input");
    for (unsigned i = 0; i < 32; i++) {
        unsigned n; CHECK(sscanf(argv[4] + i * 2, "%2x", &n) == 1, "digest hex");
        req.sha256[i] = (uint8_t)n;
    }
    struct pdva_snapshot out = { .bytes = NULL, .length = 123, .entry = 456, .image_size = 789 };
    if (fault == 19) { out.bytes = (uint8_t *)&req; }
    struct pdva_snapshot sentinel; memcpy(&sentinel, &out, sizeof(out));
    if (fault == 15) { denied_path(); } /* observer positive control */
    enum pdva_result result = pdva_snapshot_take(fd, fault == 17 ? NULL : &req,
                                                  fault == 18 ? NULL : &out);
    CHECK((int)result == atoi(argv[7]), "expected result");
    CHECK(closes == (fd >= 0 ? 1 : 0), "one close attempt");
    if (fd >= 0) { errno = 0; CHECK(fcntl(fd, F_GETFD) == -1 && errno == EBADF, "FD closed"); }
    if (result != PDVA_OK) {
        CHECK(memcmp(&out, &sentinel, sizeof(out)) == 0, "partial publication");
        CHECK(live == 0, "failure allocation cleanup");
    } else {
        CHECK(out.length == req.length && out.entry == req.ram_base + 0x80000 &&
              out.image_size >= out.length && live == 1, "complete publication");
        /* Real backing mutation AFTER success must not change the private copy. */
        if (writer >= 0) { CHECK(ftruncate(writer, 0) == 0, "post-snapshot mutation"); }
        Sha256sum hash; sha256_sum_init(&hash); sha256_sum_update(&hash, out.bytes, out.length);
        sha256_sum_close(&hash); CHECK(memcmp(hash.digest, req.sha256, 32) == 0, "stable snapshot");
        pdva_snapshot_release(&out); pdva_snapshot_release(&out);
        CHECK(live == 0 && !out.bytes && !out.length && !out.entry && !out.image_size, "release");
    }
    CHECK(allocs <= 1, "single bounded allocation");
    if (result == PDVA_ARGUMENT || result == PDVA_FD || result == PDVA_SIZE) {
        CHECK(allocs == 0 && calls == 0, "reject before allocation/read");
    }
    if (fault == 2) { CHECK(calls == 8192, "EINTR exhaustion"); }
    if (fault == 9) { CHECK(stats == 8, "stat exhaustion"); }
    if (fault == 11) { CHECK(flag_calls == 8, "flags exhaustion"); }
    if (fault == 1) { CHECK(calls > 2, "short read and EINTR exercised"); }
    if (fault == 16) { CHECK(calls == 8192, "short-read exhaustion"); }
    puts("PASS: FD snapshot case"); return 0;
}
'''


def render(data, observed=False, mutation=None):
    adapter = ADAPTER
    if mutation == 'digest':
        adapter = adapter.replace('memcmp(hash.digest, req->sha256, 32) != 0', '0')
    elif mutation == 'partial':
        adapter = adapter.replace('result = PDVA_DIGEST;', 'out->length = done; result = PDVA_DIGEST;')
    elif mutation == 'fallback':
        adapter = adapter.replace('free(bytes); return result;',
                                  'free(bytes); (void)open("forbidden", O_RDONLY); return result;')
    elif mutation is not None:
        raise ValueError('Unknown negative control')
    return PRELUDE + checksum_source(data) + (OBSERVER if observed else '') + adapter + (DRIVER if observed else '')


def require_result(result, code=0, stdout='PASS: FD snapshot case\n', stderr=''):
    if (result.returncode, result.stdout, result.stderr) != (code, stdout, stderr):
        raise RuntimeError(f'Unexpected FD control result: {result.returncode}, '
                           f'{result.stdout!r}, {result.stderr!r}')


def fixture(length=4096):
    data = bytearray((i * 37) % 256 for i in range(length))
    data[:64] = struct.pack('<IIQQQQQQII', 0x14000010, 0, 0x80000,
                            length, 2, 0, 0, 0, 0x644d5241, 0)
    return bytes(data)


def cases():
    """Independent controller expectations, including recomputed malformed digests."""
    good = fixture()
    yield 'valid', good, {}, 0
    yield 'minimum-image', fixture(68), {}, 0
    yield 'header-without-branch-target', fixture(64), {}, 3
    for length in (119, 120, 127, 128, 129, 193):
        yield f'SHA-padding-{length}', fixture(length), {}, 0
    yield 'multi-chunk', fixture(131073), {}, 0
    yield 'short-EINTR', good, {'fault': 1}, 0
    yield 'EINTR-exhaustion', good, {'fault': 2}, 5
    yield 'premature-EOF', good, {'fault': 3}, 5
    yield 'read-EIO', good, {'fault': 4}, 5
    yield 'allocation-failure', good, {'fault': 5}, 4
    yield 'close-EINTR', good, {'fault': 6}, 10
    yield 'truncate-during-read', good, {'fault': 7}, 5
    yield 'change-during-read', good, {'fault': 8}, 6
    yield 'stat-EINTR-exhaustion', good, {'fault': 9}, 2
    yield 'stat-EINTR-retry', good, {'fault': 10}, 0
    yield 'flags-EINTR-exhaustion', good, {'fault': 11}, 2
    yield 'flags-EINTR-retry', good, {'fault': 12}, 0
    yield 'final-stat-failure', good, {'fault': 13}, 6
    yield 'impossible-read-count', good, {'fault': 14}, 5
    yield 'short-read-exhaustion', fixture(8193), {'fault': 16}, 5
    yield 'null-request', good, {'fault': 17}, 1
    yield 'null-output', good, {'fault': 18}, 1
    yield 'nonempty-output', good, {'fault': 19}, 1
    yield 'digest-mismatch', good, {'digest': '00' * 32}, 7
    changed = good[:-1] + bytes([good[-1] ^ 1])
    yield 'changed-before-read', changed, {'digest': hashlib.sha256(good).hexdigest()}, 7
    yield 'invalid-FD', good, {'kind': 'invalid'}, 2
    yield 'write-only-FD', good, {'kind': 'write'}, 2
    yield 'read-write-FD', good, {'kind': 'readwrite'}, 2
    yield 'O_PATH-FD', good, {'kind': 'path'}, 2
    yield 'directory-FD', good, {'kind': 'directory'}, 2
    yield 'pipe-FD', good, {'kind': 'pipe'}, 2
    yield 'truncated-file', good[:-1], {'length': len(good)}, 3
    yield 'tiny-file', b'X', {}, 3
    yield 'zero-file', b'', {}, 3
    yield 'oversized-file', good, {'sparse': 16 * 1024 * 1024 + 1}, 3
    yield 'oversized-backing', good, {'sparse': 16 * 1024 * 1024 + 1, 'length': 4096}, 3
    yield 'length-u64-max', good, {'length': 2**64 - 1}, 3
    yield 'unknown-version', good, {'version': 2}, 1
    yield 'base-misaligned', good, {'base': 0x40000001}, 9
    yield 'RAM-end-overflow', good, {'base': 2**64 - 2**21}, 9
    yield 'RAM-above-48bit', good, {'base': 2**48}, 9
    yield 'RAM-short', good, {'ram': 0x80000 + len(good) - 1}, 9
    yield 'RAM-below-offset', good, {'ram': 0x7ffff}, 9
    yield 'RAM-exact-fit', good, {'ram': 0x80000 + len(good)}, 0
    for name, offset, payload in (
        ('ELF', 0, b'\x7fELF'), ('uImage', 0, b'\x27\x05\x19\x56'),
        ('gzip', 0, b'\x1f\x8b'), ('zboot', 0, b'MZ'), ('legacy', 56, b'xxxx'),
        ('EFI-offset', 60, struct.pack('<I', 64)),
        ('branch-in-header', 0, struct.pack('<I', 0x14000001)),
        ('branch-past-file', 0, struct.pack('<I', 0x14000400)),
        ('backward-branch', 0, struct.pack('<I', 0x17ffffff)),
        ('offset-wrap', 8, struct.pack('<Q', 2**64 - 1)),
        ('image-zero', 16, bytes(8)), ('image-small', 16, struct.pack('<Q', 64)),
        ('image-huge', 16, struct.pack('<Q', 2**64 - 1)),
        ('big-endian', 24, struct.pack('<Q', 3)),
        ('unknown-flags', 24, struct.pack('<Q', 16)),
        ('16K-page', 24, struct.pack('<Q', 4)),
        ('reserved', 32, struct.pack('<Q', 1)),
    ):
        malformed = bytearray(good); malformed[offset:offset + len(payload)] = payload
        yield name, bytes(malformed), {}, 8
    larger = bytearray(good); struct.pack_into('<Q', larger, 16, 65536)
    yield 'declared-image-larger', bytes(larger), {}, 0
    yield 'declared-image-outside-RAM', bytes(larger), {'ram': 0x80000 + 4096}, 9
    later = bytearray(good); struct.pack_into('<I', later, 0, 0x14000020)
    yield 'branch-later-in-image', bytes(later), {}, 0


def execute(binary, root, data, options, expected, observation=None):
    """Only this trusted fixture controller opens paths; C receives inherited FDs."""
    path = root / 'synthetic-resource'
    path.write_bytes(data)
    descriptors = []
    try:
        writer = os.open(path, os.O_RDWR)
        descriptors.append(writer)
        if 'sparse' in options:
            os.ftruncate(writer, options['sparse'])
        kind = options.get('kind', 'read')
        if kind == 'invalid':
            fd = -1
        elif kind == 'pipe':
            fd, other = os.pipe(); descriptors.extend([fd, other])
        else:
            flags = {'read': os.O_RDONLY, 'write': os.O_WRONLY,
                     'readwrite': os.O_RDWR, 'path': os.O_PATH,
                     'directory': os.O_RDONLY | os.O_DIRECTORY}[kind]
            fd = os.open(root if kind == 'directory' else path, flags)
            descriptors.append(fd)
        # Positional IO must leave the shared open-file-description offset alone.
        if kind in ('read', 'write', 'readwrite'):
            os.lseek(fd, 7, os.SEEK_SET)
        length = options.get('length', options.get('sparse', len(data)))
        args = [str(binary), str(fd), str(options.get('fault', 0)), str(length),
                options.get('digest', hashlib.sha256(data).hexdigest()),
                str(options.get('base', 0x40000000)), str(options.get('ram', 128 * 1024 * 1024)),
                str(expected), str(options.get('version', 1)), str(writer)]
        result = subprocess.run(args, capture_output=True, text=True, timeout=5,
                                pass_fds=tuple(descriptors), check=False)
        require_result(result, **(observation or {}))
        if kind in ('read', 'write', 'readwrite') and os.lseek(fd, 0, os.SEEK_CUR) != 7:
            raise RuntimeError('Positional read changed shared FD offset')
    finally:
        for fd in descriptors:
            os.close(fd)
        path.unlink()


def run_controls(checksum, root, run, emit):
    if platform.system() != 'Linux':
        raise RuntimeError('Real FD controls require Linux')
    source = root / 'kernel-fd-control.c'
    source.write_text(render(checksum, observed=True), encoding='utf-8', newline='\n')
    emit('FD CONTROL source-sha256=' + hashlib.sha256(source.read_bytes()).hexdigest())
    binary = root / 'kernel-fd-control'
    run('cc', '-std=c11', '-O0', '-Wall', '-Wextra', '-Werror', source, '-o', binary)
    emit('FD CONTROL binary-sha256=' + hashlib.sha256(binary.read_bytes()).hexdigest())
    count = 0
    for name, data, options, expected in cases():
        execute(binary, root, data, options, expected)
        emit(f'FD CONTROL {name}: expected result={expected}; PASS')
        count += 1
    execute(binary, root, fixture(), {'fault': 15}, 0,
            dict(code=93, stdout='', stderr='DENIED: adapter pathname/fallback\n'))
    for mutation, code, error in (
        ('digest', 90, 'FAIL: expected result\n'),
        ('partial', 90, 'FAIL: partial publication\n'),
        ('fallback', 93, 'DENIED: adapter pathname/fallback\n'),
    ):
        source = root / f'kernel-fd-{mutation}.c'
        binary = root / f'kernel-fd-{mutation}'
        source.write_text(render(checksum, observed=True, mutation=mutation), encoding='utf-8', newline='\n')
        emit(f'FD MUTANT {mutation} source-sha256=' + hashlib.sha256(source.read_bytes()).hexdigest())
        run('cc', '-std=c11', '-O0', '-Wall', '-Wextra', '-Werror', source, '-o', binary)
        emit(f'FD MUTANT {mutation} binary-sha256=' + hashlib.sha256(binary.read_bytes()).hexdigest())
        execute(binary, root, fixture(), {'digest': '00' * 32}, 7,
                dict(code=code, stdout='', stderr=error))
        emit(f'FD NEGATIVE {mutation}: exact intended exit={code}; PASS')
    emit(f'FD CONTROLS COMPLETE: {count} cases, observer control, 3 mutants; no QEMU caller integration')


def validate_artifact(report, symbols):
    """Inspect only this standalone, unobserved artifact; not all QEMU access."""
    allowed = {'__cxa_atexit', '__errno', '__libc_init', '__register_atfork',
               '__stack_chk_fail', 'close', 'fcntl', 'free', 'fstat', 'malloc',
               'memcmp', 'memcpy', 'memset', 'pread'}
    required = {'close', 'fcntl', 'free', 'fstat', 'malloc', 'memcmp', 'pread'}
    imports = set(report['dynamic_imports'])
    defined = {line.split()[-1] for line in symbols.splitlines() if line.split()}
    if not required <= imports <= allowed or not {
            'pdva_snapshot_take', 'pdva_snapshot_release'} <= defined:
        raise RuntimeError('Unexpected standalone FD artifact symbols')


def read_checksum(path):
    if (not stat.S_ISREG(path.lstat().st_mode) or path.is_symlink() or
            any(p.is_symlink() for p in path.parents)):
        raise RuntimeError('Unsafe checksum source')
    data = path.read_bytes()
    checksum_source(data)
    return data
