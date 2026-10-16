#define _GNU_SOURCE
#ifndef __linux__
#error This research fixture requires Linux.
#endif
/* Original PDVA research source. No Android/production integration.
 * One trusted, non-forking child per invocation. Timers are safety backstops,
 * not hostile-code containment. All mutations run AFTER verified cleanup. */
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static pid_t owned = -1;
static int identity = -1, reaped = 0;

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

int main(int argc, char **argv) {
    if (argc != 3) return 64;
    int mode = strcmp(argv[1], "exit") == 0 ? 0 :
               strcmp(argv[1], "term") == 0 ? 1 :
               strcmp(argv[1], "fd") == 0 ? 2 : -1;
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
