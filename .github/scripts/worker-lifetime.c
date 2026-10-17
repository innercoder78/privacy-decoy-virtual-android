#define _GNU_SOURCE
#ifndef __linux__
#error This research fixture requires Linux.
#endif
/* Original PDVA research source. No Android/production integration.
 * A/B/D: one non-forking child; C: one child and one grandchild, fixed source.
 * Timers are safety backstops,
 * not hostile-code containment. All mutations run AFTER verified cleanup. */
#include <errno.h>
#include <fcntl.h>
#include <linux/sched.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static pid_t owned = -1;
static int identity = -1, reaped = 0;
static void (*failure_cleanup)(const char *) = NULL;

static int ready(int fd, short events, int milliseconds) {
    struct pollfd p = {fd, events, 0};
    /* EINTR is a failure, not an unbounded deadline extension. */
    return poll(&p, 1, milliseconds) == 1 && (p.revents & events) != 0;
}

static int send_signal(int sig) {
    if (owned <= 0 || reaped) return -1;
    if (identity >= 0) return (int)syscall(SYS_pidfd_send_signal, identity, sig, NULL, 0);
    /* Setup failure only: own unreaped direct child, SIGCHLD is SIG_DFL,
     * no other thread/reaper exists. Its numeric PID cannot yet be reused. */
    return kill(owned, sig);
}

static int collect(int *status) {
    if (identity >= 0 && !ready(identity, POLLIN, 3000)) return 0;
    /* Bounded fallback also covers failure to open a pidfd during setup. */
    for (int i = 0; i < 300; ++i) {
        pid_t result = waitpid(owned, status, WNOHANG);
        if (result == owned) { reaped = 1; return 1; }
        if (result < 0) return 0;
        struct timespec pause = {0, 10000000};
        if (nanosleep(&pause, NULL)) return 0;
    }
    return 0;
}

static void fail(const char *reason) {
    if (failure_cleanup) failure_cleanup(reason);
    int status = 0, clean = owned < 0 || reaped;
    if (!clean) {
        int result = send_signal(SIGKILL);
        clean = (result == 0 || errno == ESRCH) && collect(&status);
    }
    fprintf(stderr, "FAIL:%s cleanup=%s\n", reason,
            owned < 0 ? "no-child" : clean ? "reaped" : "UNPROVEN");
    exit(clean ? 1 : 2); /* Runner stops on either; neither is negative evidence. */
}

static void require(int condition, const char *reason) {
    if (!condition) fail(reason);
}

static void limit(int resource, rlim_t value) {
    struct rlimit bound = {value, value};
    require(setrlimit(resource, &bound) == 0, "resource-limit");
}

static void byte_out(int fd, char value) {
    require(ready(fd, POLLOUT, 1000) && write(fd, &value, 1) == 1, "write");
}

static void byte_in(int fd, char value) {
    char actual = 0;
    require(ready(fd, POLLIN, 1000) && read(fd, &actual, 1) == 1 && actual == value, "read");
}

static void child(int command, int response, int data, int mode) {
    limit(RLIMIT_CPU, 1);
    limit(RLIMIT_AS, 64 * 1024 * 1024);
    limit(RLIMIT_NOFILE, 32);
    limit(RLIMIT_FSIZE, 4096);
    limit(RLIMIT_CORE, 0);
    if (mode == 1) require(signal(SIGTERM, SIG_IGN) != SIG_ERR, "ignore-term");
    int duplicate = -1;
    if (mode == 2) {
        duplicate = fcntl(data, F_DUPFD_CLOEXEC, 3);
        require(duplicate >= 0 && close(data) == 0, "duplicate-close");
    }
    byte_out(response, 'R');
    byte_in(command, 'G'); /* Controller has pidfd before permitting transition. */
    if (mode == 0) _exit(42);
    if (mode == 1) {
        byte_out(response, 'A'); /* Challenge after successful TERM delivery. */
        byte_in(command, 'X'); /* Controller never sends X: requires SIGKILL. */
        _exit(91);
    }
    char buffer[5] = {0};
    require(pread(duplicate, buffer, sizeof(buffer), 0) == 4 &&
            memcmp(buffer, "PDVA", 4) == 0, "retained-read");
    require(close(duplicate) == 0, "duplicate-final-close");
    byte_out(response, 'D');
    _exit(0);
}

/* Fixed two-descendant case. The kernel publishes the grandchild PID into a
 * shared slot BEFORE waking it (CLONE_PARENT_SETTID). Neither fixture process
 * writes the slot or waits/reaps. Therefore the PID remains reserved through
 * subreaper adoption until this controller reaps it, including setup failures.
 * This is a trusted-source topology invariant, NOT a hostile-worker registry. */
static pid_t *grand_slot;
static pid_t direct_pid = -1, grand_pid = -1;
static int direct_fd = -1, grand_fd = -1, direct_done, grand_done;
static int grand_command = -1;

static int fixed_collect(pid_t pid, int fd, int *done, int *status) {
    if (*done) return 1;
    if (pid <= 0) return 0;
    if (fd >= 0 && !ready(fd, POLLIN, 3000)) return 0;
    for (int i = 0; i < 300; ++i) {
        pid_t result = waitpid(pid, status, WNOHANG);
        if (result == pid) { *done = 1; return 1; }
        if (result < 0) return 0;
        struct timespec pause = {0, 10000000};
        if (nanosleep(&pause, NULL)) return 0;
    }
    return 0;
}

static int fixed_kill(int fd) {
    if (fd < 0) return 0; /* Never numeric-PID signal fallback. */
    int result = (int)syscall(SYS_pidfd_send_signal, fd, SIGKILL, NULL, 0);
    return result == 0 || errno == ESRCH;
}

static void grand_fail(const char *reason) {
    int status = 0, clean = 1;
    /* Terminate an already-registered grandchild even if creator reaping fails. */
    if (grand_fd >= 0 && !grand_done) (void)fixed_kill(grand_fd);
    /* End the only possible creator first. Reaping synchronizes the final
     * kernel-written slot even if failure interrupted registration. */
    if (direct_pid > 0 && !direct_done) {
        (void)fixed_kill(direct_fd);
        clean = fixed_collect(direct_pid, direct_fd, &direct_done, &status);
    }
    if (direct_pid > 0 && direct_done && grand_slot) {
        grand_pid = *grand_slot;
        if (grand_pid > 0 && !grand_done) {
            if (grand_fd < 0) grand_fd = (int)syscall(SYS_pidfd_open, grand_pid, 0U);
            (void)fixed_kill(grand_fd);
            /* Unsupported pidfd is still failure. EOF asks the fixed fixture
             * to exit; only an actual reap can establish failure-path cleanup. */
            if (grand_command >= 0) { close(grand_command); grand_command = -1; }
            if (!fixed_collect(grand_pid, grand_fd, &grand_done, &status)) clean = 0;
        }
    }
    errno = 0;
    if (waitpid(-1, &status, WNOHANG) != -1 || errno != ECHILD) clean = 0;
    fprintf(stderr, "FAIL:%s cleanup=%s\n", reason, clean ? "reaped" : "UNPROVEN");
    exit(clean ? 1 : 2);
}

static void fixed_eof(int fd) {
    char extra;
    require(ready(fd, POLLIN | POLLHUP, 1000) && read(fd, &extra, 1) == 0, "fixed-eof");
}

static void fixed_live(int fd) {
    struct pollfd p = {fd, POLLIN, 0};
    require(fd >= 0 && poll(&p, 1, 0) == 0 &&
            syscall(SYS_pidfd_send_signal, fd, 0, NULL, 0) == 0, "fixed-live-identity");
}

static int grandchild_case(int mutant) {
    failure_cleanup = grand_fail;
    require(getuid() != 0 && geteuid() != 0, "unprivileged-controller");
    require(prctl(PR_SET_CHILD_SUBREAPER, 1L, 0L, 0L, 0L) == 0, "set-subreaper");
    int subreaper = 0;
    require(prctl(PR_GET_CHILD_SUBREAPER, &subreaper, 0L, 0L, 0L) == 0 &&
            subreaper == 1, "verify-subreaper");
    grand_slot = mmap(NULL, sizeof(*grand_slot), PROT_READ | PROT_WRITE,
                      MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (grand_slot == MAP_FAILED) { grand_slot = NULL; fail("shared-registration"); }
    *grand_slot = 0;
    int pc[2], pr[2], gc[2], gr[2];
    require(pipe2(pc, O_CLOEXEC) == 0 && pipe2(pr, O_CLOEXEC) == 0 &&
            pipe2(gc, O_CLOEXEC) == 0 && pipe2(gr, O_CLOEXEC) == 0, "fixed-pipes");
    grand_command = gc[1];
    pid_t controller = getpid();
    struct clone_args first = {0};
    first.flags = CLONE_PIDFD;
    first.pidfd = (uintptr_t)&direct_fd;
    first.exit_signal = SIGCHLD;
    direct_pid = (pid_t)syscall(SYS_clone3, &first, sizeof(first));
    require(direct_pid >= 0, "direct-clone-pidfd");
    if (direct_pid == 0) {
        alarm(10); /* clone, like fork, clears the inherited alarm. */
        failure_cleanup = NULL;
        limit(RLIMIT_CPU, 1);
        require(close(0) == 0 && close(1) == 0 && close(pc[1]) == 0 &&
                close(pr[0]) == 0 && close(gc[1]) == 0 && close(gr[0]) == 0,
                "direct-close");
        byte_in(pc[0], 'F'); /* Controller already owns direct child's pidfd. */
        struct clone_args second = {0};
        second.flags = CLONE_PARENT_SETTID;
        second.parent_tid = (uintptr_t)grand_slot;
        second.exit_signal = SIGCHLD;
        pid_t created = (pid_t)syscall(SYS_clone3, &second, sizeof(second));
        require(created >= 0, "grand-clone-registration");
        if (created == 0) {
            alarm(8);
            require(close(pc[0]) == 0 && close(pr[1]) == 0, "grand-close");
            require(getpid() == *grand_slot, "grand-kernel-identity");
            byte_out(gr[1], 'R');
            byte_in(gc[0], 'I'); /* Stable identity acquired before registration ACK. */
            byte_out(gr[1], 'A');
            byte_in(gc[0], 'C'); /* Sent only AFTER parent's exact reap. */
            require(getppid() == controller, "grand-adoption");
            byte_out(gr[1], 'S');
            byte_in(gc[0], 'X'); /* Never sent: controller must terminate by pidfd. */
            _exit(93);
        }
        require(created == *grand_slot, "direct-kernel-registration");
        require(close(gc[0]) == 0 && close(gr[1]) == 0, "direct-grand-close");
        byte_out(pr[1], 'R');
        byte_in(pc[0], 'E');
        _exit(42); /* No wait: grandchild identity cannot be recycled. */
    }
    require(direct_fd >= 0, "direct-stable-identity");
    require(close(pc[0]) == 0 && close(pr[1]) == 0 && close(gc[0]) == 0 &&
            close(gr[1]) == 0, "fixed-controller-close");
    fixed_live(direct_fd);
    byte_out(pc[1], 'F');
    byte_in(pr[0], 'R');
    grand_pid = *grand_slot;
    require(grand_pid > 0 && grand_pid != direct_pid && grand_pid != controller,
            "kernel-registration");
    grand_fd = (int)syscall(SYS_pidfd_open, grand_pid, 0U);
    require(grand_fd >= 0, "grand-stable-identity");
    byte_in(gr[0], 'R');
    fixed_live(grand_fd);
    byte_out(gc[1], 'I');
    byte_in(gr[0], 'A');
    fixed_live(direct_fd);
    fixed_live(grand_fd);
    byte_out(pc[1], 'E');
    int status = 0;
    require(fixed_collect(direct_pid, direct_fd, &direct_done, &status), "direct-reap");
    require(WIFEXITED(status) && WEXITSTATUS(status) == 42, "direct-exit-status");
    fixed_eof(pr[0]);
    byte_out(gc[1], 'C');
    byte_in(gr[0], 'S');
    fixed_live(grand_fd);
    int survived = 1;
    require(syscall(SYS_pidfd_send_signal, grand_fd, SIGKILL, NULL, 0) == 0,
            "grand-kill-receipt");
    require(fixed_collect(grand_pid, grand_fd, &grand_done, &status), "grand-reap");
    require(WIFSIGNALED(status) && WTERMSIG(status) == SIGKILL, "grand-death-receipt");
    fixed_eof(gr[0]);
    errno = 0;
    require(waitpid(direct_pid, &status, WNOHANG) == -1 && errno == ECHILD, "direct-reap-once");
    errno = 0;
    require(waitpid(grand_pid, &status, WNOHANG) == -1 && errno == ECHILD, "grand-reap-once");
    errno = 0;
    require(waitpid(-1, &status, WNOHANG) == -1 && errno == ECHILD, "fixed-tree-echild");
    require(close(direct_fd) == 0 && close(grand_fd) == 0 && close(pc[1]) == 0 &&
            close(pr[0]) == 0 && close(gc[1]) == 0 && close(gr[0]) == 0 &&
            munmap(grand_slot, sizeof(*grand_slot)) == 0, "fixed-final-close");
    grand_slot = NULL;
    grand_command = -1;
    puts("EVIDENCE:grandchild status=exit42 registered=1 identity=pidfd "
         "parent-reaped=1 post-reap-challenge=1 alive=1 adopted=1 "
         "termination=SIGKILL grand-reaped=1 echild=1 parent-eof=1 grand-eof=1 cleanup=verified");
    /* False assertion: once the direct child is reaped, the complete tree is gone.
     * Evaluate only after every real observation AND eventual cleanup. */
    if (mutant && survived) {
        fputs("REJECTED:grandchild:cleanup-verified\n", stderr);
        return 42;
    }
    return mutant ? 3 : 0;
}

int main(int argc, char **argv) {
    if (argc != 3) return 64;
    int mode = strcmp(argv[1], "exit") == 0 ? 0 :
               strcmp(argv[1], "term") == 0 ? 1 :
               strcmp(argv[1], "fd") == 0 ? 2 :
               strcmp(argv[1], "grandchild") == 0 ? 3 : -1;
    int mutant = strcmp(argv[2], "mutant") == 0;
    if (mode < 0 || (!mutant && strcmp(argv[2], "positive") != 0)) return 64;
    /* Runner supplies a private cwd and closes inherited FDs. Bound our own
     * descriptors too, without enumerating arbitrary host processes or data. */
    require(syscall(SYS_close_range, 3U, ~0U, 0U) == 0, "close-inherited");
    struct sigaction default_action = {0};
    default_action.sa_handler = SIG_DFL;
    require(sigemptyset(&default_action.sa_mask) == 0 &&
            sigaction(SIGCHLD, &default_action, NULL) == 0 &&
            sigaction(SIGALRM, &default_action, NULL) == 0 &&
            signal(SIGPIPE, SIG_IGN) != SIG_ERR, "signal-setup");
    sigset_t empty;
    require(sigemptyset(&empty) == 0 && sigprocmask(SIG_SETMASK, &empty, NULL) == 0, "signal-mask");
    limit(RLIMIT_CORE, 0);
    limit(RLIMIT_CPU, 2);
    limit(RLIMIT_AS, 64 * 1024 * 1024);
    limit(RLIMIT_NOFILE, 32);
    limit(RLIMIT_FSIZE, 4096);
    alarm(12); /* Whole controller backstop; runner deadline is separately 15s. */
    if (mode == 3) return grandchild_case(mutant);
    int commands[2], replies[2], data = -1;
    require(pipe2(commands, O_CLOEXEC) == 0 && pipe2(replies, O_CLOEXEC) == 0, "pipes");
    if (mode == 2) {
        data = open("synthetic", O_CREAT | O_EXCL | O_RDWR | O_CLOEXEC, 0600);
        require(data >= 0 && write(data, "PDVA", 4) == 4, "synthetic-file");
        require(close(data) == 0, "writer-close");
        data = open("synthetic", O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        require(data >= 0 && unlink("synthetic") == 0, "synthetic-unlink");
    }
    owned = fork();
    require(owned >= 0, "fork");
    if (owned == 0) {
        /* fork clears alarms: re-arm before setup or blocking handshakes.
         * There is no child exec/fork. Parent's expiration is independent. */
        alarm(10);
        owned = -1; /* Child failure must never invoke controller cleanup. */
        require(close(STDIN_FILENO) == 0 && close(STDOUT_FILENO) == 0 &&
                close(commands[1]) == 0 && close(replies[0]) == 0, "child-fd-close");
        child(commands[0], replies[1], data, mode);
        _exit(92);
    }
    identity = (int)syscall(SYS_pidfd_open, owned, 0U);
    require(identity >= 0, "pidfd-open"); /* Unsupported is failure, never skip. */
    require(close(commands[0]) == 0 && close(replies[1]) == 0, "controller-fd-close");
    byte_in(replies[0], 'R');
    if (data >= 0) require(close(data) == 0, "owner-close");
    if (mode == 1) require(send_signal(SIGTERM) == 0, "term-delivery");
    byte_out(commands[1], 'G');
    int observed = 0;
    if (mode == 1) {
        byte_in(replies[0], 'A');
        struct pollfd p = {identity, POLLIN, 0};
        require(poll(&p, 1, 0) == 0, "live-pidfd-after-term");
        observed = 1;
        require(send_signal(SIGKILL) == 0, "kill-delivery");
    }
    if (mode == 2) { byte_in(replies[0], 'D'); observed = 1; }
    int status = 0;
    require(collect(&status), "exact-child-reap");
    int spare = 0;
    errno = 0;
    require(waitpid(owned, &spare, WNOHANG) == -1 && errno == ECHILD, "single-reap");
    errno = 0;
    require(waitpid(-1, &spare, WNOHANG) == -1 && errno == ECHILD, "no-owned-children");
    /* Child never forks: ECHILD plus source topology is not a general tree proof. */
    char extra;
    require(read(replies[0], &extra, 1) == 0, "reply-eof");
    require(close(identity) == 0 && close(commands[1]) == 0 && close(replies[0]) == 0, "final-close");
    int expected = mode == 0 ? (WIFEXITED(status) && WEXITSTATUS(status) == 42) :
                   mode == 1 ? (WIFSIGNALED(status) && WTERMSIG(status) == SIGKILL) :
                               (WIFEXITED(status) && WEXITSTATUS(status) == 0);
    require(expected, "wait-status");
    printf("EVIDENCE:%s status=%s observed=%d identity=pidfd reaped=1 echild=1 eof=1\n",
           argv[1], mode == 0 ? "exit42" : mode == 1 ? "SIGKILL" : "exit0", observed);
    /* Deliberate semantic assertion mutations. Setup, exact status, EOF and
     * cleanup must already pass; arbitrary failures cannot reach this branch. */
    if (mutant) {
        int false_assumption = mode == 0 ? WEXITSTATUS(status) == 0 : observed == 0;
        if (!false_assumption) {
            fprintf(stderr, "REJECTED:%s:cleanup-verified\n", argv[1]);
            return 42;
        }
        return 3; /* Mutant unexpectedly survived. */
    }
    return 0;
}
