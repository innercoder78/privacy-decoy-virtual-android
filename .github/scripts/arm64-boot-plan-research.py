#!/usr/bin/env python3
"""One-shot typed ARM64 reservation control; no QEMU boot/ROM dispatch wiring.

Adds a research translation unit to a verified ephemeral QEMU source tree.
Linux tests compile that exact unit with an observed OS include context.
"""
import difflib
import hashlib
import importlib.util
from pathlib import Path
import platform
import stat

_spec = importlib.util.spec_from_file_location(
    'plan_kernel_fd', Path(__file__).with_name('kernel-fd-research.py'))
fd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fd)

INPUTS = {
    'hw/arm/meson.build': '8efe237c39a11996ea7fb6cbd9bcbeb87412796c3c9e48bbb0634768e1efcfd9',
    'hw/arm/boot.c': '3ee33e386c78e816410d7f897d616a1f2c44203e7a609671184a95153412311f',
    'hw/arm/virt.c': 'd6073388bed5bfc2b20f9d8928d0715d524db835a0f5a7f533eb690dda4068a4',
    'system/device_tree.c': 'fcfc8835626a75192c5f1335973469db7bd09c856231cac0bc465a4b94b130ed',
    'hw/core/machine.c': '189c891714f0928cdd6648f7d2799b529029345a4c47fcf1fc92adb01a9d6e27',
    'system/vl.c': 'a5fb2a78e45ec8edb256188eed44e8f06f7dba99c1dd029dd8a0d74cfab74266',
    'include/hw/arm/boot.h': '0989956cac29b6652f1182edf314df328859b71900304f296df7db40c27e8129',
}
SOURCE = 'hw/arm/pdva-boot-plan.c'
# Exact PR #12 original adapter text, before the two static-linkage edits below.
ADAPTER_SHA256 = '95e69229f79201e2f644ec1af7e731dd95e4e21c1e97843092ff4a822d5b5805'

PLAN = r'''
/* Original PDVA research control, compiled in the QEMU research build only.
 * No machine property, CLI switch, RPC, ROM registration or byte-export API.
 * One process, one owning thread, one attempt. No concurrent/reentrant calls.
 * All caller objects must be valid, private and disjoint for each call. The
 * admission output must remain at the same address until abort/plan completion.
 * The private registry prevents a copied token from becoming a second owner;
 * it is NOT a boundary against code that can corrupt this process's memory.
 */
enum pdva_plan_result {
    PDVA_PLAN_OK = 0, PDVA_PLAN_ORDINARY, PDVA_PLAN_STATE, PDVA_PLAN_IDENTITY,
    PDVA_PLAN_POLICY, PDVA_PLAN_RANGE, PDVA_PLAN_OVERLAP, PDVA_PLAN_ARGUMENT,
    PDVA_PLAN_SNAPSHOT = 100
};
enum pdva_boot_mode { PDVA_BOOT_ORDINARY = 0, PDVA_BOOT_RESEARCH_RAW64 = 1 };
enum pdva_resource_bits {
    PDVA_FIRMWARE = 1, PDVA_PFLASH0 = 2, PDVA_PFLASH1 = 4, PDVA_BIOS = 8,
    PDVA_SHIM = 16, PDVA_INITRD = 32, PDVA_EXTERNAL_DTB = 64,
    PDVA_KERNEL_PATH = 128, PDVA_OPTION_ROM = 256, PDVA_OTHER_RESOURCE = 512
};
/* This is a declaration to be supplied by a future reviewed machine adapter,
 * not a measurement of MachineState. All unknown bits are rejected too.
 * features: secure/EL2/MTE/NUMA/hotplug/memory-backend/board hooks/extra devices.
 * Only the exact single-CPU, AArch64 virt, TCG, plain RAM subset is modeled.
 */
struct pdva_boot_config {
    uint32_t version, mode, architecture, machine, accelerator, cpus;
    uint64_t features, resources;
    uint32_t dtb_kind; /* 1 = generated virt reservation; no external blob */
    uint64_t ram_base, ram_size, boot_start, boot_size, dtb_start, dtb_size;
};
struct pdva_resource_identity {
    uint64_t resource, epoch; /* nonzero controller values; NOT authentication */
    uint8_t sha256[32];
};
struct pdva_boot_admission {
    uint32_t version, format; /* 1, 1 = PR #12 strict raw ARM64 subset */
    struct pdva_resource_identity identity;
};
struct pdva_boot_plan {
    uint32_t version, reservation_only; /* always 1; never boot authorization */
    uint64_t entry, kernel_size, boot_start, boot_size, dtb_start, dtb_size;
};
enum pdva_plan_result pdva_boot_admit(int descriptor,
    const struct pdva_request *request, const struct pdva_resource_identity *id,
    struct pdva_boot_admission *out);
enum pdva_plan_result pdva_boot_reserve(const struct pdva_boot_admission *admission,
    const struct pdva_resource_identity *expected,
    const struct pdva_boot_config *config, struct pdva_boot_plan *out);
void pdva_boot_abort(void);

static struct {
    enum { PLAN_EMPTY, PLAN_ADMITTED, PLAN_RESERVED, PLAN_DEAD } state;
    struct pdva_snapshot snapshot;
    struct pdva_boot_admission token;
    const struct pdva_boot_admission *owner;
    uint64_t ram_base, ram_size;
} pdva_slot;

void pdva_boot_abort(void)
{
    pdva_snapshot_release(&pdva_slot.snapshot);
    memset(&pdva_slot.token, 0, sizeof(pdva_slot.token));
    pdva_slot.owner = NULL;
    pdva_slot.ram_base = pdva_slot.ram_size = 0;
    pdva_slot.state = PLAN_DEAD; /* never reset to EMPTY, including on failure */
}

static enum pdva_plan_result pdva_plan_fail(enum pdva_plan_result result)
{
    pdva_boot_abort();
    return result;
}

static int pdva_identity_equal(const struct pdva_resource_identity *a,
                               const struct pdva_resource_identity *b)
{
    return a->resource == b->resource && a->epoch == b->epoch &&
           memcmp(a->sha256, b->sha256, 32) == 0;
}

/* Consumes descriptor on EVERY return. Only the constructor can create an
 * admission: it takes the actual PR #12 validated private snapshot, never a
 * caller-supplied pointer/length pair or a filename. No exported snapshot copy.
 */
enum pdva_plan_result pdva_boot_admit(int descriptor,
    const struct pdva_request *request, const struct pdva_resource_identity *id,
    struct pdva_boot_admission *out)
{
    enum pdva_plan_result error = PDVA_PLAN_ARGUMENT;
    struct pdva_snapshot snapshot = { 0 };
    if (pdva_slot.state != PLAN_EMPTY) {
        error = PDVA_PLAN_STATE;
        goto reject;
    }
    if (!request || !id || !out || !id->resource || !id->epoch ||
        out->version || out->format || out->identity.resource || out->identity.epoch ||
        memcmp(out->identity.sha256, (uint8_t[32]){0}, 32) != 0 ||
        memcmp(request->sha256, id->sha256, 32) != 0) {
        goto reject;
    }
    enum pdva_result result = pdva_snapshot_take(descriptor, request, &snapshot);
    if (result != PDVA_OK) {
        return pdva_plan_fail((enum pdva_plan_result)(PDVA_PLAN_SNAPSHOT + result));
    }
    struct pdva_boot_admission ready = { .version = 1, .format = 1, .identity = *id };
    pdva_slot.snapshot = snapshot;
    pdva_slot.token = ready;
    pdva_slot.owner = out;
    pdva_slot.ram_base = request->ram_base;
    pdva_slot.ram_size = request->ram_size;
    pdva_slot.state = PLAN_ADMITTED;
    *out = ready;
    return PDVA_PLAN_OK;
reject:
    if (descriptor >= 0) { (void)close(descriptor); } /* once, never retry close */
    return pdva_plan_fail(error);
}

static int pdva_inside(uint64_t start, uint64_t size, uint64_t base, uint64_t ram)
{
    /* ram/base overflow has already been checked; subtraction avoids wrap. */
    return size && start >= base && start - base <= ram &&
           size <= ram - (start - base);
}

static int pdva_overlap(uint64_t a, uint64_t an, uint64_t b, uint64_t bn)
{
    /* Called only after containment proves both additions cannot overflow. */
    return a < b + bn && b < a + an;
}

enum pdva_plan_result pdva_boot_reserve(const struct pdva_boot_admission *admission,
    const struct pdva_resource_identity *expected,
    const struct pdva_boot_config *config, struct pdva_boot_plan *out)
{
    if (!config || !out) { return pdva_plan_fail(PDVA_PLAN_ARGUMENT); }
    /* Off is a no-op only BEFORE admission. It cannot rescue a failed attempt. */
    if (config->version == 1 && config->mode == PDVA_BOOT_ORDINARY &&
        pdva_slot.state == PLAN_EMPTY && !admission && !expected) {
        return PDVA_PLAN_ORDINARY;
    }
    if (pdva_slot.state != PLAN_ADMITTED || !admission ||
        admission != pdva_slot.owner) {
        return pdva_plan_fail(PDVA_PLAN_STATE);
    }
    if (!expected || admission->version != 1 || admission->format != 1 ||
        !pdva_identity_equal(&admission->identity, &pdva_slot.token.identity) ||
        !pdva_identity_equal(expected, &pdva_slot.token.identity)) {
        return pdva_plan_fail(PDVA_PLAN_IDENTITY);
    }
    if (config->version != 1 || config->mode != PDVA_BOOT_RESEARCH_RAW64 ||
        config->architecture != 64 || config->machine != 1 ||
        config->accelerator != 1 || config->cpus != 1 || config->features ||
        config->resources != 0 || config->dtb_kind != 1) {
        return pdva_plan_fail(PDVA_PLAN_POLICY);
    }
    uint64_t base = config->ram_base, ram = config->ram_size;
    uint64_t entry = pdva_slot.snapshot.entry, extent = pdva_slot.snapshot.image_size;
    if (base != pdva_slot.ram_base || ram != pdva_slot.ram_size ||
        ram > UINT64_MAX - base || base + ram > (UINT64_C(1) << 48) ||
        !pdva_inside(entry, extent, base, ram) ||
        !pdva_inside(config->boot_start, config->boot_size, base, ram) ||
        !pdva_inside(config->dtb_start, config->dtb_size, base, ram)) {
        return pdva_plan_fail(PDVA_PLAN_RANGE);
    }
    if (pdva_overlap(entry, extent, config->boot_start, config->boot_size) ||
        pdva_overlap(entry, extent, config->dtb_start, config->dtb_size) ||
        pdva_overlap(config->boot_start, config->boot_size, config->dtb_start, config->dtb_size)) {
        return pdva_plan_fail(PDVA_PLAN_OVERLAP);
    }
    /* Narrow plain virt low-RAM shape, not a general QEMU address-space model.
     * BOOTLOADER_MAX_SIZE and FDT_MAX_SIZE are exact-source-derived below.
     * DTB reservation is 2-MiB aligned and after the full declared Image extent.
     * No alignment arithmetic on an unchecked sum and no blob publication.
     */
    if (base != UINT64_C(0x40000000) || ram > UINT64_C(0x40000000) ||
        config->boot_start != base || config->boot_size != PDVA_BOOT_RESERVE ||
        config->dtb_size != PDVA_DTB_RESERVE || config->dtb_start % UINT64_C(0x200000) ||
        config->dtb_start < entry + extent) {
        return pdva_plan_fail(PDVA_PLAN_RANGE);
    }
    struct pdva_boot_plan ready = {
        .version = 1, .reservation_only = 1, .entry = entry, .kernel_size = extent,
        .boot_start = config->boot_start, .boot_size = config->boot_size,
        .dtb_start = config->dtb_start, .dtb_size = config->dtb_size
    };
    /* Only private output, after ALL checks. No ROM/DTB/CPU/machine state writes. */
    *out = ready;
    pdva_slot.state = PLAN_RESERVED;
    return PDVA_PLAN_OK;
}
'''


def render(sources, checksum):
    if set(sources) != set(INPUTS):
        raise RuntimeError('Unexpected boot-plan source set')
    for name, expected in INPUTS.items():
        if hashlib.sha256(sources[name]).hexdigest() != expected:
            raise RuntimeError('Boot-plan identity mismatch: ' + name)
    if hashlib.sha256(fd.ADAPTER.encode()).hexdigest() != ADAPTER_SHA256:
        raise RuntimeError('Unreviewed PR12 snapshot adapter')
    boot, tree = sources['hw/arm/boot.c'].decode(), sources['system/device_tree.c'].decode()
    if ('#define BOOTLOADER_MAX_SIZE         (4 * KiB)\n' not in boot or
            '#define FDT_MAX_SIZE  0x100000\n' not in tree):
        raise RuntimeError('Unreviewed reservation constants')
    # No reader logic changes. Private linkage prevents bypassing its constructor.
    adapter = fd.ADAPTER.replace('void pdva_snapshot_release(', 'static void pdva_snapshot_release(')
    adapter = adapter.replace('enum pdva_result pdva_snapshot_take(',
                              'static enum pdva_result pdva_snapshot_take(')
    code = ('/* Original PDVA research additions to the GPL QEMU experiment.\n'
            ' * PR12 reader logic unchanged; GLib notices follow. No distribution approval.\n */\n'
            '#include "qemu/osdep.h"\n'
            '_Static_assert(sizeof(off_t) >= 8, "64-bit positional IO required");\n' +
            fd.checksum_source(checksum) + adapter +
            '\n#define PDVA_BOOT_RESERVE UINT64_C(4096)\n'
            '#define PDVA_DTB_RESERVE UINT64_C(1048576)\n' + PLAN)
    meson = sources['hw/arm/meson.build'].decode()
    old = "arm_common_ss.add(when: 'CONFIG_ARM_VIRT', if_true: files('virt.c'))"
    if meson.count(old) != 1:
        raise RuntimeError('Ambiguous boot-plan Meson anchor')
    return {SOURCE: code.encode(), 'hw/arm/meson.build': meson.replace(
        old, "arm_common_ss.add(when: 'CONFIG_ARM_VIRT', if_true: files('virt.c', 'pdva-boot-plan.c'))").encode()}


def safe_read(path):
    if (not stat.S_ISREG(path.lstat().st_mode) or path.is_symlink() or
            any(p.is_symlink() for p in path.parents)):
        raise RuntimeError('Unsafe boot-plan source')
    return path.read_bytes()


def apply(qemu, checksum, emit):
    sources = {name: safe_read(qemu / name) for name in INPUTS}
    patched = render(sources, checksum)  # validate ALL identities before writing
    if (qemu / SOURCE).exists() or (qemu / SOURCE).is_symlink():
        raise RuntimeError('Boot-plan destination already exists')
    for name, data in patched.items():
        delta = ''.join(difflib.unified_diff(sources.get(name, b'').decode().splitlines(True),
                                           data.decode().splitlines(True), name, name))
        emit(f'BOOT PLAN PATCH {name} after={hashlib.sha256(data).hexdigest()} '
             f'diff-sha256={hashlib.sha256(delta.encode()).hexdigest()}')
    for name, data in patched.items():
        (qemu / name).write_bytes(data)
    return patched


DRIVER = r'''
#undef malloc
#undef free
#undef pread
#undef fstat
#undef fcntl
#undef close
int main(int argc, char **argv)
{
    CHECK(argc == 10, "arguments");
    int descriptor = atoi(argv[1]), scenario = atoi(argv[2]);
    struct pdva_request req = { .version = 1, .length = strtoull(argv[3], NULL, 10),
        .ram_base = strtoull(argv[5], NULL, 10), .ram_size = strtoull(argv[6], NULL, 10) };
    CHECK(strlen(argv[4]) == 64, "digest argument");
    for (unsigned i = 0; i < 32; i++) {
        unsigned v; CHECK(sscanf(argv[4] + 2 * i, "%2x", &v) == 1, "digest parse");
        req.sha256[i] = (uint8_t)v;
    }
    struct pdva_resource_identity id = { .resource = 7, .epoch = 42 };
    memcpy(id.sha256, req.sha256, 32);
    struct pdva_boot_admission admission = {0}, copy;
    struct pdva_boot_config cfg = {
        .version = 1, .mode = PDVA_BOOT_RESEARCH_RAW64, .architecture = 64,
        .machine = 1, .accelerator = 1, .cpus = 1, .dtb_kind = 1,
        .ram_base = req.ram_base, .ram_size = req.ram_size,
        .boot_start = req.ram_base, .boot_size = 4096,
        .dtb_start = req.ram_base + 0x200000, .dtb_size = 0x100000
    };
    struct pdva_boot_plan plan, sentinel;
    memset(&plan, 0xa5, sizeof(plan)); memcpy(&sentinel, &plan, sizeof(plan));
    enum pdva_plan_result result;
    if (scenario == 50) { denied_path(); }
    if (scenario == 1 || scenario == 2) {
        cfg.mode = scenario == 1 ? PDVA_BOOT_ORDINARY : PDVA_BOOT_RESEARCH_RAW64;
        close(descriptor);
        result = pdva_boot_reserve(NULL, NULL, &cfg, &plan);
    } else {
        if (scenario == 43) { id.epoch = 0; }
        if (scenario == 44) { admission.version = 1; }
        if (scenario == 45) { fault = 5; } /* reader allocation failure */
        if (scenario == 46) { fault = 4; } /* interrupted IO with terminal EIO */
        if (scenario == 53) { req.version = 2; }
        if (scenario == 54) { id.sha256[0] ^= 1; }
        if (scenario == 55) { id.resource = 0; }
        memcpy(&copy, &admission, sizeof(copy));
        result = pdva_boot_admit(descriptor, scenario == 49 ? NULL : &req,
                                scenario == 51 ? NULL : &id,
                                scenario == 52 ? NULL : &admission);
        if (result != PDVA_PLAN_OK) {
            CHECK(memcmp(&admission, &copy, sizeof(copy)) == 0, "partial admission publication");
        }
        CHECK(closes == 1, "admission consumes one FD");
        errno = 0;
        CHECK(fcntl(descriptor, F_GETFD) == -1 && errno == EBADF, "closed descriptor");
        if (result == PDVA_PLAN_OK) {
            CHECK(live == 1 && admission.version == 1 && admission.format == 1,
                  "owned typed admission");
            /* The backing can change now; only the private snapshot remains. */
            CHECK(ftruncate(atoi(argv[9]), 0) == 0, "change backing after admission");
            const struct pdva_boot_admission *owner = &admission;
            switch (scenario) {
            case 3: owner = NULL; break;
            case 4: copy = admission; owner = &copy; break;
            case 5: admission.version = 2; break;
            case 6: admission.format = 2; break;
            case 7: id.resource++; break;
            case 8: id.epoch++; break;
            case 9: id.sha256[0] ^= 1; break;
            case 10: cfg.mode = PDVA_BOOT_ORDINARY; break;
            case 11: cfg.mode = 2; break;
            case 12: cfg.version = 2; break;
            case 13: cfg.architecture = 32; break;
            case 14: cfg.machine = 2; break;
            case 15: cfg.accelerator = 2; break;
            case 16: cfg.cpus = 2; break;
            case 17: cfg.features = 1; break;
            case 18: cfg.dtb_kind = 2; break;
            case 19: cfg.ram_base += 0x200000; break;
            case 20: cfg.ram_size = UINT64_MAX; break;
            case 21: cfg.boot_start = UINT64_MAX; break;
            case 22: cfg.dtb_size = UINT64_MAX; break;
            case 23: cfg.boot_start = req.ram_base + 0x80000; break;
            case 24: cfg.dtb_start = req.ram_base + 0x80000; break;
            case 25: cfg.dtb_start = cfg.boot_start; break;
            case 26: cfg.dtb_start++; break;
            case 27: cfg.boot_size = 0; break;
            case 28: cfg.boot_size = 8192; break;
            case 29: cfg.dtb_size--; break;
            case 30: cfg.dtb_start = req.ram_base + req.ram_size; break;
            case 31: pdva_boot_abort(); break;
            case 32: {
                int second = dup(atoi(argv[9]));
                CHECK(second >= 0, "second owned FD");
                result = pdva_boot_admit(second, &req, &id, &copy);
                CHECK(result == PDVA_PLAN_STATE && closes == 2, "repeat admission consumes FD");
                errno = 0;
                CHECK(fcntl(second, F_GETFD) == -1 && errno == EBADF, "repeat FD closed");
                break;
            }
            case 33: admission.identity.resource++; break;
            case 34: cfg.features = UINT64_C(1) << 63; break;
            case 35: cfg.resources = UINT64_C(1) << 63; break;
            case 36: cfg.ram_size--; break;
            case 37: cfg.dtb_size = 0; break;
            case 38: cfg.boot_start--; break;
            case 39: cfg.cpus = 0; break;
            case 40: cfg.dtb_start = req.ram_base + 0x400000; break;
            case 41: cfg.dtb_start = req.ram_base + 0x400000; break;
            default: break;
            }
            if (scenario >= 60 && scenario < 70) { cfg.resources = UINT64_C(1) << (scenario - 60); }
            if (scenario >= 70 && scenario < 78) { cfg.features = UINT64_C(1) << (scenario - 70); }
            result = pdva_boot_reserve(owner, scenario == 42 ? NULL : &id,
                                      scenario == 47 ? NULL : &cfg,
                                      scenario == 48 ? NULL : &plan);
        }
    }
    CHECK((int)result == atoi(argv[7]), "plan expected result");
    /* The partial mutant returns the right error but changes private output. */
    if (atoi(argv[7]) != PDVA_PLAN_OK) {
        CHECK(memcmp(&plan, &sentinel, sizeof(plan)) == 0, "partial plan publication");
    }
    if (result == PDVA_PLAN_OK) {
        CHECK(plan.version == 1 && plan.reservation_only == 1 &&
              plan.entry == req.ram_base + 0x80000 && plan.kernel_size >= req.length &&
              plan.boot_start == cfg.boot_start && plan.boot_size == 4096 &&
              plan.dtb_start == cfg.dtb_start && plan.dtb_size == 0x100000,
              "complete reservation");
        memcpy(&sentinel, &plan, sizeof(plan));
        CHECK(pdva_boot_reserve(&admission, &id, &cfg, &plan) == PDVA_PLAN_STATE,
              "repeat plan terminal");
        CHECK(memcmp(&plan, &sentinel, sizeof(plan)) == 0, "repeat plan unchanged");
    } else if (result != PDVA_PLAN_ORDINARY) {
        CHECK(live == 0 && !pdva_slot.snapshot.bytes && pdva_slot.state == PLAN_DEAD,
              "terminal cleanup");
        cfg.mode = PDVA_BOOT_ORDINARY;
        CHECK(pdva_boot_reserve(NULL, NULL, &cfg, &plan) == PDVA_PLAN_STATE,
              "no ordinary fallback after failure");
    }
    pdva_boot_abort(); pdva_boot_abort();
    CHECK(live == 0 && !pdva_slot.snapshot.bytes && !pdva_slot.owner, "idempotent abort");
    CHECK(allocs <= 1, "bounded single snapshot");
    puts("PASS: typed boot plan case"); return 0;
}
'''


def observed_source(source, mutation=None):
    text = source.decode()
    if text.count('#include "qemu/osdep.h"\n') != 1:
        raise RuntimeError('Unexpected boot-plan include context')
    if mutation == 'policy':
        old, new = 'config->resources != 0', '0'
    elif mutation == 'partial':
        old, new = 'uint64_t base = config->ram_base', 'out->version = 1;\n    uint64_t base = config->ram_base'
    elif mutation == 'fallback':
        old, new = 'pdva_boot_abort();\n    return result;', 'pdva_boot_abort();\n    (void)open("forbidden", O_RDONLY);\n    return result;'
    elif mutation is not None:
        raise ValueError('Unknown plan mutation')
    if mutation:
        if text.count(old) != 1:
            raise RuntimeError('Ambiguous boot-plan mutation')
        text = text.replace(old, new)
    return text.replace('#include "qemu/osdep.h"\n', fd.PRELUDE + fd.OBSERVER) + DRIVER


def cases():
    good = fd.fixture()
    expected = {
        0: 0, 1: 1, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3,
        **{i: 4 for i in range(10, 19)}, **{i: 5 for i in range(19, 23)},
        23: 6, 24: 6, 25: 6, **{i: 5 for i in range(26, 31)},
        31: 2, 32: 2, 33: 3, 34: 4, 35: 4, 36: 5, 37: 5, 38: 5, 39: 4,
        42: 3, 43: 7, 44: 7, 45: 104, 46: 105, 47: 7, 48: 7, 49: 7,
        51: 7, 52: 7, 53: 101, 54: 7, 55: 7,
        **{i: 4 for i in range(60, 78)},
    }
    for scenario, result in expected.items():
        yield f'plan-{scenario}', good, {'fault': scenario}, result
    # Full declared image extent, not file length: DTB at +2MiB overlaps.
    import struct
    large = bytearray(good)
    struct.pack_into('<Q', large, 16, 0x300000)
    yield 'declared-extent-overlap', bytes(large), {}, 6
    yield 'declared-extent-separated', bytes(large), {'fault': 40}, 0
    yield 'exact-reservation-RAM-fit', good, {'fault': 41, 'ram': 0x500000}, 0
    yield 'one-byte-outside-RAM', good, {'fault': 41, 'ram': 0x4fffff}, 5
    adjacent = bytearray(good)
    struct.pack_into('<Q', adjacent, 16, 0x180000)
    yield 'kernel-DTB-adjacent', bytes(adjacent), {}, 0
    yield 'unsupported-virt-base', good, {'base': 0x40200000}, 5
    yield 'unsupported-RAM-cap', good, {'ram': 0x40000001}, 5
    # Actual constructor -> snapshot -> plan controls, not fabricated tokens.
    for name, data, options, result in fd.cases():
        if name in {'digest-mismatch', 'changed-before-read', 'ELF', 'uImage', 'gzip',
                    'zboot', 'legacy', 'image-huge', 'image-zero', 'offset-wrap',
                    'RAM-end-overflow', 'oversized-file'}:
            yield name, data, options, 100 + result


def run_controls(qemu, patched, root, run, emit):
    if platform.system() != 'Linux':
        raise RuntimeError('Boot-plan controls require Linux')
    source = safe_read(qemu / SOURCE)
    if source != patched[SOURCE]:
        raise RuntimeError('Boot-plan test/source mismatch')
    for mutation, scenario, code, error in (
        (None, None, 0, ''), ('policy', 65, 90, 'FAIL: plan expected result\n'),
        ('partial', 24, 90, 'FAIL: partial plan publication\n'),
        ('fallback', 8, 93, 'DENIED: adapter pathname/fallback\n'),
    ):
        name = 'boot-plan-' + (mutation or 'positive')
        path, binary = root / (name + '.c'), root / name
        path.write_text(observed_source(source, mutation), encoding='utf-8', newline='\n')
        emit(f'BOOT PLAN CONTROL {name} source-sha256={hashlib.sha256(path.read_bytes()).hexdigest()}')
        run('cc', '-std=c11', '-O0', '-Wall', '-Wextra', '-Werror', path, '-o', binary)
        emit(f'BOOT PLAN CONTROL {name} binary-sha256={hashlib.sha256(binary.read_bytes()).hexdigest()}')
        if mutation is None:
            count = 0
            for label, data, options, expected in cases():
                fd.execute(binary, root, data, options, expected,
                           dict(stdout='PASS: typed boot plan case\n'))
                emit(f'BOOT PLAN {label}: exact result={expected}; PASS')
                count += 1
            fd.execute(binary, root, fd.fixture(), {'fault': 50}, 0,
                       dict(code=93, stdout='', stderr='DENIED: adapter pathname/fallback\n'))
        else:
            expected = {'policy': 4, 'partial': 6, 'fallback': 3}[mutation]
            fd.execute(binary, root, fd.fixture(), {'fault': scenario}, expected,
                       dict(code=code, stdout='', stderr=error))
            emit(f'BOOT PLAN NEGATIVE {mutation}: exact exit={code}; PASS')
    emit(f'BOOT PLAN CONTROLS COMPLETE: {count} cases, observer, 3 mutants; reservation only, no ROM dispatch')
