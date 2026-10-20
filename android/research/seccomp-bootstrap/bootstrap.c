/* Original PDVA dormant research fixture. NOT linked or packaged by Gradle.
 * No main, JNI_OnLoad, constructor, loader, callback or arbitrary payload.
 * Future JNI activation and independent observation require separate review.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

#ifndef PDVA_MODEL
#if !defined(__ANDROID__) || !defined(__aarch64__) || __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "Only Android little-endian AArch64 LP64 is supported"
#endif
_Static_assert(sizeof(long) == 8 && sizeof(void *) == 8, "LP64 required");
_Static_assert(__NR_getpid == 172 && __NR_seccomp == 277, "Unexpected syscall ABI");
#endif
_Static_assert(offsetof(struct seccomp_data, args) == 16, "Unexpected seccomp ABI");

#define MARKER UINT64_C(0x5044564150524f42)
/* Deliberately NOT a containment policy. Other syscalls are untouched.
 * Reject other audit architectures; never reinterpret this policy on them.
 * Dedicated read-only section permits independent inspection of shipped bytes.
 */
__attribute__((section(".pdva_filter"), used))
static const struct sock_filter filter[] = {
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, 4),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_AARCH64, 1, 0),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, 0),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_getpid, 0, 5),
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, 16),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, (uint32_t)MARKER, 0, 3),
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, 20),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, (uint32_t)(MARKER >> 32), 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EACCES),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
};

struct sample { long pid, tid, marked, error, nnp, seccomp; };
struct receipt {
    long version, mode, uid, euid;
    long nnp_set, nnp_error, nnp_read, install, install_error, attempted;
    long peer_create, peer_join, new_create, new_join, failure, payload;
    struct sample before, peer_before, after, peer_after, newborn;
};
static struct receipt result;
/* Pre-sample is immutable after ready; post-samples are copied only after join.
 * Even timeout receipts have no concurrent writers and are safe to inspect. */
static struct sample peer_pre, peer_post, new_sample;
static atomic_flag consumed = ATOMIC_FLAG_INIT;
static atomic_int ready, command, done;

static void sample(struct sample *s) {
    s->pid = syscall(__NR_getpid, 0L, 0L, 0L, 0L, 0L, 0L);
    s->tid = syscall(__NR_gettid);
    errno = 0;
    s->marked = syscall(__NR_getpid, (long)MARKER, 0L, 0L, 0L, 0L, 0L);
    s->error = errno;
    s->nnp = prctl(PR_GET_NO_NEW_PRIVS, 0L, 0L, 0L, 0L);
    s->seccomp = prctl(PR_GET_SECCOMP, 0L, 0L, 0L, 0L);
}
/* Scheduling failure is Unknown. No deadline is a cleanup certificate. */
static int await(atomic_int *flag) {
    struct timespec start, now, pause = {0, 1000000};
    if (clock_gettime(CLOCK_MONOTONIC, &start)) return -1;
    for (int i = 0; i < 2000; ++i) {
        if (atomic_load(flag)) return 0;
        if (clock_gettime(CLOCK_MONOTONIC, &now) || now.tv_sec - start.tv_sec >= 2)
            return -1;
        if (nanosleep(&pause, NULL)) return -1;
    }
    return -1;
}
static void *peer(void *unused) {
    (void)unused;
    sample(&peer_pre);
    atomic_store(&ready, 1);
    if (await(&command) == 0 && atomic_load(&command) == 1)
        sample(&peer_post);
    atomic_store(&done, 1);
    return NULL;
}
static void *newborn(void *unused) {
    (void)unused;
    sample(&new_sample);
    atomic_store(&done, 1);
    return NULL;
}
static int baseline(const struct sample *s) {
    return s->pid > 0 && s->tid > 0 && s->marked == s->pid && s->error == 0;
}
static int denied(const struct sample *s) {
    return s->pid == result.before.pid && s->tid > 0 && s->marked == -1 &&
        s->error == EACCES && s->nnp == 1 && s->seccomp == SECCOMP_MODE_FILTER;
}
static void fixed_payload(void) { result.payload = 42; }

/* Modes: 0 TSYNC; 1 deliberately omit TSYNC; 2 invalid empty filter.
 * The caller must be a separately authorized trusted isolated-process adapter.
 * Return is diagnostic data, NEVER independent security attestation.
 * Each attempt consumes this process permanently, including invalid modes.
 * Static storage deliberately survives failed joins. Never dlclose/retry it.
 */
__attribute__((visibility("default")))
const struct receipt *pdva_bootstrap(int mode) {
    if (atomic_flag_test_and_set(&consumed)) return NULL;
    result.version = 1; result.mode = mode;
    result.install = -2; result.nnp_set = -2; result.nnp_read = -2;
    result.peer_create = result.peer_join = result.new_create = result.new_join = -2;
    result.uid = getuid(); result.euid = geteuid();
    if (mode < 0 || mode > 2 || result.uid == 0 || result.uid != result.euid) {
        result.failure = 1; return &result;
    }
    sample(&result.before);
    if (!baseline(&result.before)) { result.failure = 2; return &result; }
    pthread_t t;
    result.peer_create = pthread_create(&t, NULL, peer, NULL);
    if (result.peer_create) { result.failure = 3; return &result; }
    if (await(&ready)) { result.failure = 4; goto cancel; }
    result.peer_before = peer_pre;
    if (!baseline(&result.peer_before) || result.peer_before.pid != result.before.pid ||
            result.peer_before.tid == result.before.tid) {
        result.failure = 4; goto cancel;
    }
    errno = 0;
    result.nnp_set = prctl(PR_SET_NO_NEW_PRIVS, 1L, 0L, 0L, 0L);
    result.nnp_error = errno;
    result.nnp_read = prctl(PR_GET_NO_NEW_PRIVS, 0L, 0L, 0L, 0L);
    if (result.nnp_set != 0 || result.nnp_read != 1) {
        result.failure = 5; goto cancel;
    }
    struct sock_fprog program = { .len = mode == 2 ? 0 : sizeof(filter)/sizeof(filter[0]),
        .filter = (struct sock_filter *)filter };
    errno = 0; result.attempted = 1;
    result.install = syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER,
        mode == 1 ? 0UL : (unsigned long)SECCOMP_FILTER_FLAG_TSYNC, &program);
    result.install_error = errno;
    /* Positive TID is failure, exactly like negative errno. */
    if (result.install != 0) { result.failure = 6; goto cancel; }
    sample(&result.after);
    atomic_store(&command, 1);
    if (await(&done)) { result.failure = 7; return &result; }
    result.peer_join = pthread_join(t, NULL);
    if (result.peer_join) { result.failure = 8; return &result; }
    result.peer_after = peer_post;
    if (!denied(&result.after) || !denied(&result.peer_after) ||
            result.after.tid != result.before.tid || result.peer_after.tid != result.peer_before.tid) {
        result.failure = 9; return &result;
    }
    /* Negative modes can never enter payload, even with surprising observations. */
    if (mode != 0) { result.failure = 10; return &result; }
    atomic_store(&done, 0);
    result.new_create = pthread_create(&t, NULL, newborn, NULL);
    if (result.new_create) { result.failure = 11; return &result; }
    if (await(&done)) { result.failure = 12; return &result; }
    result.new_join = pthread_join(t, NULL);
    if (result.new_join) { result.failure = 13; return &result; }
    result.newborn = new_sample;
    if (!denied(&result.newborn) ||
            result.newborn.tid == result.before.tid) {
        result.failure = 13; return &result;
    }
    fixed_payload();
    return &result;
cancel:
    atomic_store(&command, 2);
    if (await(&done) == 0) result.peer_join = pthread_join(t, NULL);
    return &result;
}
