#define _GNU_SOURCE
/* Original PDVA fixed research fixture, not a production sandbox.
 * Linux native x86_64 only. The supervisor NEVER installs seccomp or NNP.
 * No arbitrary payloads. At most one worker plus one registered process probe;
 * at most one peer thread is live, joined on the normal success path. */
#if !defined(__linux__) || !defined(__x86_64__) || defined(__ILP32__)
#error This fixture requires the native Linux x86_64 LP64 ABI.
#endif
#include <errno.h>
#include <fcntl.h>
#include <linux/audit.h>
#include <linux/capability.h>
#include <linux/filter.h>
#include <linux/sched.h>
#include <linux/seccomp.h>
#include <poll.h>
#include <pthread.h>
#include <signal.h>
#include <stddef.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

_Static_assert(SYS_clone == 56 && SYS_fork == 57 && SYS_vfork == 58 &&
               SYS_execve == 59 && SYS_execveat == 322 && SYS_clone3 == 435 &&
               SYS_prctl == 157 && SYS_seccomp == 317, "Unexpected syscall ABI");
_Static_assert(ATOMIC_INT_LOCK_FREE == 2, "Require lock-free thread handshake");

enum { SYNC, LOCAL, INVALID, DIVERGENT };
struct receipts {
    /* Kernel writes this PID before waking a process probe. Never overwritten
     * or reaped by the worker; subreaper ownership prevents PID reuse. */
    pid_t process;
    int nnp, installed, pre, post, clone3_denied, exec_denied;
    int immutable, stacked, retained, terminal, attempted, created, local_denied;
    int install_tried, install_errno;
    long install_result;
    pid_t peer_tid;
};
static struct receipts *r;
static pid_t worker = -1;
static int worker_fd = -1, worker_reaped;
static int go[2], ack[2], mode;
static pid_t worker_tgid;
static atomic_int peer_ready, peer_go;

static int ready(int fd, short events, int ms) {
    struct pollfd p = {fd, events, 0};
    return poll(&p, 1, ms) == 1 && (p.revents & events);
}
static int reap(pid_t pid, int *status) {
    for (int i = 0; i < 200; ++i) {
        pid_t result = waitpid(pid, status, WNOHANG);
        if (result == pid) return 1;
        if (result < 0) return 0;
        struct timespec delay = {0, 10000000};
        if (nanosleep(&delay, NULL)) return 0;
    }
    return 0;
}
static int kill_owned(int fd) {
    if (fd < 0) return 0;
    int result = (int)syscall(SYS_pidfd_send_signal, fd, SIGKILL, NULL, 0);
    return result == 0 || errno == ESRCH;
}
static int no_children(void) {
    int status;
    errno = 0;
    return waitpid(-1, &status, WNOHANG) == -1 && errno == ECHILD;
}
static void fail(const char *stage) {
    int status, clean = 1;
    /* Stop/reap the sole creator before reading its final registration slot.
     * No numeric-PID signaling, scanning, or reliance on the tested filter. */
    if (worker > 0 && !worker_reaped) {
        (void)kill_owned(worker_fd);
        worker_reaped = reap(worker, &status);
        clean = worker_reaped;
    }
    if (worker > 0 && worker_reaped && r && r->process > 0) {
        int fd = (int)syscall(SYS_pidfd_open, r->process, 0);
        (void)kill_owned(fd);
        if (!reap(r->process, &status)) clean = 0;
        if (fd >= 0) close(fd);
    }
    if (!no_children()) clean = 0;
    fprintf(stderr, "FAIL:%s cleanup=%s\n", stage, clean ? "verified" : "UNPROVEN");
    exit(clean ? 1 : 2);
}
static void need(int ok, const char *stage) { if (!ok) fail(stage); }
static void child_need(int ok) { if (!ok) _exit(90); }
static void bound(int resource, rlim_t value) {
    struct rlimit lim = {value, value};
    need(setrlimit(resource, &lim) == 0, "limits");
}
static void send_byte(int fd) {
    child_need(ready(fd, POLLOUT, 1000) && write(fd, "G", 1) == 1);
}
static void receive_byte(int fd) {
    char c;
    child_need(ready(fd, POLLIN, 1000) && read(fd, &c, 1) == 1 && c == 'G');
}
static int nnp(void) { return prctl(PR_GET_NO_NEW_PRIVS, 0L, 0L, 0L, 0L); }
static int secmode(void) { return prctl(PR_GET_SECCOMP, 0L, 0L, 0L, 0L); }

/* Deny every clone3 call with ENOSYS, never dereference its pointer. This
 * intentionally exercises libc's ENOSYS-to-legacy-clone thread path. Legacy
 * clone remains filtered. No successful clone3 fallback is permitted. */
#define REQUIRED (CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND | CLONE_THREAD | CLONE_SYSVSEM)
#define OPTIONAL (CLONE_SETTLS | CLONE_PARENT_SETTID | CLONE_CHILD_SETTID | CLONE_CHILD_CLEARTID | CLONE_DETACHED)
#define DENY_NR(n) BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, (n), 0, 1), BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM)
static long install(unsigned flags) {
    struct sock_filter code[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, arch)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        /* Also reject x32 and the legacy 512..547 confusion range. */
        BPF_JUMP(BPF_JMP | BPF_JGE | BPF_K, 512, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | ENOSYS),
        DENY_NR(SYS_fork), DENY_NR(SYS_vfork),
        DENY_NR(SYS_execve), DENY_NR(SYS_execveat),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_clone3, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | ENOSYS),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_clone, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, args[0]) + 4),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 0, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, args[0])),
        BPF_STMT(BPF_ALU | BPF_AND | BPF_K, ~(REQUIRED | OPTIONAL)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 0, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, args[0])),
        BPF_STMT(BPF_ALU | BPF_AND | BPF_K, REQUIRED),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, REQUIRED, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    struct sock_fprog program = {sizeof(code) / sizeof(code[0]), code};
    return syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, flags, &program);
}
static long add_allow(unsigned flags) {
    struct sock_filter code[] = { BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW) };
    struct sock_fprog program = {1, code};
    return syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, flags, &program);
}

/* Fixed fork-like clone: no shared address space, no alternate stack/TLS,
 * SIGCHLD disposition default, no worker-side wait. Parent_tid is kernel-written
 * shared registration even if the creator dies before returning from syscall.
 * This cannot create more than one process: any success ends this invocation. */
static int probe_clone(int clone3) {
    child_need(r->process == 0);
    struct clone_args args = {0};
    args.flags = CLONE_PARENT_SETTID;
    args.parent_tid = (uintptr_t)&r->process;
    args.exit_signal = SIGCHLD;
    r->attempted++;
    errno = 0;
    long result = clone3 ? syscall(SYS_clone3, &args, sizeof(args)) :
        syscall(SYS_clone, (unsigned long)(CLONE_PARENT_SETTID | SIGCHLD),
                NULL, &r->process, NULL, NULL);
    int error = errno;
    if (result == 0) {
        /* No libc locks, allocation, extra spawning, inherited alarm assumption,
         * or test continuation in a child of a multithreaded process. */
        alarm(2);
        _exit(95);
    }
    if (result > 0) {
        child_need(result == r->process);
        r->created = 1;
        _exit(mode == LOCAL && !clone3 ? 42 : 91);
    }
    child_need(result == -1 && error == (clone3 ? ENOSYS : EPERM) && r->process == 0);
    return 1;
}
static void *existing_thread(void *unused) {
    (void)unused;
    r->peer_tid = (pid_t)syscall(SYS_gettid);
    child_need(getpid() == worker_tgid && r->peer_tid != worker_tgid);
    if (mode == DIVERGENT) {
        child_need(prctl(PR_SET_NO_NEW_PRIVS, 1L, 0L, 0L, 0L) == 0);
        child_need(add_allow(0) == 0);
    }
    atomic_store_explicit(&peer_ready, 1, memory_order_release);
    send_byte(ack[1]);
    receive_byte(go[0]);
    child_need(atomic_load_explicit(&peer_go, memory_order_acquire) == 1);
    child_need(mode == SYNC || mode == LOCAL);
    if (mode == SYNC) child_need(nnp() == 1 && secmode() == SECCOMP_MODE_FILTER);
    r->pre = probe_clone(0);
    return NULL;
}
static void *inherited_thread(void *unused) {
    (void)unused;
    child_need(getpid() == worker_tgid && syscall(SYS_gettid) != worker_tgid);
    child_need(nnp() == 1 && secmode() == SECCOMP_MODE_FILTER);
    r->post = probe_clone(0);
    return NULL;
}
static void run_worker(int command) {
    alarm(8);
    worker_tgid = getpid();
    receive_byte(command); /* Supervisor already holds atomic worker pidfd. */
    child_need(close(command) == 0 && close(0) == 0 && close(1) == 0 && close(2) == 0);
    struct rlimit cpu = {1, 1};
    child_need(setrlimit(RLIMIT_CPU, &cpu) == 0);
    child_need(pipe2(go, O_CLOEXEC) == 0 && pipe2(ack, O_CLOEXEC) == 0);
    int data[2];
    child_need(pipe2(data, O_CLOEXEC) == 0 && write(data[1], "PDVA", 4) == 4);
    child_need(close(data[1]) == 0);
    pthread_attr_t attr;
    pthread_t thread;
    child_need(pthread_attr_init(&attr) == 0 && pthread_attr_setstacksize(&attr, 256 * 1024) == 0);
    child_need(pthread_create(&thread, &attr, existing_thread, NULL) == 0);
    receive_byte(ack[0]);
    child_need(atomic_load_explicit(&peer_ready, memory_order_acquire) == 1);
    child_need(prctl(PR_SET_NO_NEW_PRIVS, 1L, 0L, 0L, 0L) == 0 && nnp() == 1);
    r->nnp = 1;
    r->install_tried = 1;
    errno = 0;
    long result = install(mode == LOCAL ? 0 : mode == INVALID ? 0x80000000U : SECCOMP_FILTER_FLAG_TSYNC);
    int error = errno;
    r->install_result = result;
    r->install_errno = error;
    if (mode == INVALID || mode == DIVERGENT) {
        /* Installation failure is terminal: zero process probes, no GO, no
         * payload continuation, whole worker exit (including waiting peer). */
        child_need(mode == INVALID ? result == -1 && error == EINVAL :
                   result > 0 && result == r->peer_tid);
        r->terminal = 1;
        _exit(43);
    }
    child_need(result == 0 && secmode() == SECCOMP_MODE_FILTER);
    r->installed = 1;
    if (mode == LOCAL) r->local_denied = probe_clone(0);
    atomic_store_explicit(&peer_go, 1, memory_order_release);
    send_byte(go[1]);
    child_need(pthread_join(thread, NULL) == 0);
    /* LOCAL must have exited 42 inside the existing, unfiltered peer. */
    child_need(mode == SYNC && r->pre == 1);
    r->clone3_denied = probe_clone(1);
    errno = 0;
    child_need(syscall(SYS_execve, "", NULL, NULL) == -1 && errno == EPERM);
    errno = 0;
    child_need(syscall(SYS_execveat, -1, "", NULL, NULL, 0) == -1 && errno == EPERM);
    r->exec_denied = 1; /* No executable or valid pathname was supplied. */
    errno = 0;
    child_need(prctl(PR_SET_NO_NEW_PRIVS, 0L, 0L, 0L, 0L) == -1 && errno == EINVAL);
    errno = 0;
    child_need(prctl(PR_SET_SECCOMP, SECCOMP_MODE_DISABLED, 0L, 0L, 0L) == -1 && errno == EINVAL);
    child_need(nnp() == 1 && secmode() == SECCOMP_MODE_FILTER);
    r->immutable = probe_clone(0);
    child_need(add_allow(SECCOMP_FILTER_FLAG_TSYNC) == 0);
    r->stacked = probe_clone(0);
    child_need(pthread_create(&thread, &attr, inherited_thread, NULL) == 0);
    child_need(pthread_join(thread, NULL) == 0 && r->post == 1);
    child_need(pthread_attr_destroy(&attr) == 0);
    char bytes[4];
    child_need(read(data[0], bytes, 4) == 4 && memcmp(bytes, "PDVA", 4) == 0);
    r->retained = 1;
    _exit(0);
}

int main(int argc, char **argv) {
    if (argc != 2) return 64;
    const char *names[] = {"tsync", "thread-only", "invalid-install", "divergent-tsync"};
    for (mode = 0; mode < 4 && strcmp(argv[1], names[mode]); ++mode) {}
    if (mode == 4) return 64;
    need(getuid() != 0 && geteuid() != 0, "unprivileged");
    struct __user_cap_header_struct header = {_LINUX_CAPABILITY_VERSION_3, 0};
    struct __user_cap_data_struct caps[2] = {{0}};
    need(syscall(SYS_capget, &header, caps) == 0, "capability-query");
    for (int i = 0; i < 2; ++i)
        need(!(caps[i].effective | caps[i].permitted | caps[i].inheritable), "capability-free");
    need(syscall(SYS_close_range, 3U, ~0U, 0U) == 0, "close-inherited");
    struct sigaction sa = {0};
    sa.sa_handler = SIG_DFL;
    need(sigemptyset(&sa.sa_mask) == 0 && sigaction(SIGCHLD, &sa, NULL) == 0 &&
         sigaction(SIGALRM, &sa, NULL) == 0, "signal-disposition");
    sigset_t empty;
    need(sigemptyset(&empty) == 0 && sigprocmask(SIG_SETMASK, &empty, NULL) == 0, "signal-mask");
    sa.sa_handler = SIG_IGN;
    need(sigaction(SIGPIPE, &sa, NULL) == 0, "pipe-signal");
    bound(RLIMIT_CORE, 0); bound(RLIMIT_CPU, 2); bound(RLIMIT_AS, 64 * 1024 * 1024);
    bound(RLIMIT_NOFILE, 32); bound(RLIMIT_FSIZE, 4096);
    alarm(12);
    int original_nnp = nnp(), original_mode = secmode();
    need(original_nnp >= 0 && original_mode >= 0, "controller-state");
    need(prctl(PR_SET_CHILD_SUBREAPER, 1L, 0L, 0L, 0L) == 0, "subreaper");
    int subreaper = 0;
    need(prctl(PR_GET_CHILD_SUBREAPER, &subreaper, 0L, 0L, 0L) == 0 && subreaper == 1, "subreaper-readback");
    r = mmap(NULL, sizeof(*r), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (r == MAP_FAILED) { r = NULL; fail("registration-map"); }
    int command[2];
    need(pipe2(command, O_CLOEXEC) == 0, "command-pipe");
    struct clone_args args = {0};
    args.flags = CLONE_PIDFD;
    args.pidfd = (uintptr_t)&worker_fd;
    args.exit_signal = SIGCHLD;
    worker = (pid_t)syscall(SYS_clone3, &args, sizeof(args));
    need(worker >= 0, "worker-clone3");
    if (worker == 0) {
        child_need(close(command[1]) == 0);
        run_worker(command[0]);
        _exit(90);
    }
    need(worker_fd >= 0 && close(command[0]) == 0, "worker-identity");
    need(ready(command[1], POLLOUT, 1000) && write(command[1], "G", 1) == 1, "release");
    need(close(command[1]) == 0, "release-close");
    /* Independent expiration: timeout triggers pidfd kill and reaping below. */
    need(ready(worker_fd, POLLIN, 5000), "worker-deadline");
    int status;
    worker_reaped = reap(worker, &status);
    need(worker_reaped, "worker-reap");
    int expected = mode == SYNC ? 0 : mode == LOCAL ? 42 : 43;
    if (!WIFEXITED(status) || WEXITSTATUS(status) != expected) {
        fprintf(stderr, "OBSERVED:worker wait=%d exit=%d signal=%d install-tried=%d install-result=%ld install-errno=%d\n",
                status, WIFEXITED(status) ? WEXITSTATUS(status) : -1,
                WIFSIGNALED(status) ? WTERMSIG(status) : 0,
                r->install_tried, r->install_result, r->install_errno);
    }
    need(WIFEXITED(status) && WEXITSTATUS(status) == expected, "worker-status");
    if (mode == LOCAL) {
        need(r->process > 0 && r->process != worker && r->process != getpid(), "probe-registration");
        int fd = (int)syscall(SYS_pidfd_open, r->process, 0);
        need(fd >= 0, "probe-identity");
        need(ready(fd, POLLIN, 1000), "probe-expiration");
        int probe_status;
        int done = reap(r->process, &probe_status);
        /* Avoid re-signaling/reaping a consumed identity on a later failure. */
        if (done) r->process = 0;
        need(done && WIFEXITED(probe_status) && WEXITSTATUS(probe_status) == 95, "probe-status");
        need(close(fd) == 0, "probe-close");
    } else need(r->process == 0, "unexpected-process");
    need(no_children(), "echild");
    need(nnp() == original_nnp && secmode() == original_mode, "controller-unchanged");
    need(r->nnp == 1 && r->install_tried == 1, "nnp-install-receipt");
    if (mode == INVALID) need(r->install_result == -1 && r->install_errno == EINVAL, "invalid-install-receipt");
    else if (mode == DIVERGENT) need(r->install_result > 0 && r->install_result == r->peer_tid, "tsync-tid-receipt");
    else need(r->install_result == 0 && r->install_errno == 0, "installed-receipt");
    if (mode == SYNC) {
        need(r->installed == 1 && r->pre == 1 && r->post == 1 && r->clone3_denied == 1 &&
             r->exec_denied == 1 && r->immutable == 1 && r->stacked == 1 && r->retained == 1 &&
             r->attempted == 5 && r->created == 0 && r->terminal == 0, "sync-receipts");
        puts("EVIDENCE:tsync nnp=1 install=0 pre=EPERM post=EPERM clone3=ENOSYS exec=EPERM reset=EINVAL allow-stack=still-denied retained=PDVA probes=5 created=0 worker=exit0 identity=pidfd cleanup=verified controller=unchanged");
    } else if (mode == LOCAL) {
        need(r->installed == 1 && r->local_denied == 1 && r->created == 1 && r->attempted == 2 && r->pre == 0 && r->post == 0 && r->terminal == 0, "local-receipts");
        puts("EVIDENCE:thread-only nnp=1 install=0 main=EPERM peer=process-created probes=2 worker=exit42 probe=exit95 identity=pidfd cleanup=verified controller=unchanged");
        fputs("REJECTED:thread-only-is-all-threads:cleanup-verified\n", stderr);
    } else {
        need(r->installed == 0 && r->terminal == 1 && r->attempted == 0 && r->created == 0, "terminal-receipts");
        printf("EVIDENCE:%s nnp=1 install=%s terminal=1 probes=0 worker=exit43 identity=pidfd cleanup=verified controller=unchanged\n",
               names[mode], mode == INVALID ? "EINVAL" : "peer-tid");
    }
    need(close(worker_fd) == 0 && munmap(r, sizeof(*r)) == 0, "final-close");
    r = NULL;
    return mode == LOCAL ? 42 : 0;
}
