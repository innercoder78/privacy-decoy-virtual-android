#define _GNU_SOURCE
#include <jni.h>
#include <dirent.h>
#include <elf.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include "launch_wire.h"

/* Array positions are validated by LaunchResult. No raw strings cross JNI. */
enum { ABI, ELF, PRE_ERR, CREATE, CREATE_ERR, SETUP_ERR, EXEC, EXEC_ERR,
       WAIT, WAIT_ERR, EXIT_CODE, SIGNAL, TIMEOUT, CLEAN, OUTPUT, PID_OK,
       UID_OK, EUID_OK, CONTEXT, SECCOMP, CAPS, LINKER, KILL_ERR, FDS, COUNT };

#if defined(__aarch64__)
#include "launch_wait.h"
static int64_t millis(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t)) return -1;
    return (int64_t)t.tv_sec * 1000 + t.tv_nsec / 1000000;
}
static int wait_child(int pid, int *status) { return waitpid(pid, status, WNOHANG); }
static int kill_child(int pid) { return kill(pid, SIGKILL); }
static void pause_wait(void) {
    struct timespec delay = {0, 10000000};
    nanosleep(&delay, NULL);
}

static bool elf_ok(int fd) {
    Elf64_Ehdr h;
    if (pread(fd, &h, sizeof(h), 0) != sizeof(h) || memcmp(h.e_ident, ELFMAG, SELFMAG)
            || h.e_ident[EI_CLASS] != ELFCLASS64 || h.e_ident[EI_DATA] != ELFDATA2LSB
            || h.e_type != ET_DYN || h.e_machine != EM_AARCH64 || !h.e_entry
            || h.e_phentsize != sizeof(Elf64_Phdr) || h.e_phnum > 32
            || h.e_phoff > 4096) return false;
    bool interp = false, dynamic = false;
    for (unsigned i = 0; i < h.e_phnum; ++i) {
        Elf64_Phdr p;
        if (pread(fd, &p, sizeof(p), (off_t)(h.e_phoff + i*sizeof(p))) != sizeof(p)) return false;
        if (p.p_type == PT_DYNAMIC) dynamic = true;
        if (p.p_type == PT_LOAD && (p.p_flags & (PF_W|PF_X)) == (PF_W|PF_X)) return false;
        if (p.p_type == PT_INTERP) {
            char text[sizeof("/system/bin/linker64")];
            if (p.p_filesz != sizeof(text) || p.p_offset > 65536
                    || pread(fd, text, sizeof(text), (off_t)p.p_offset) != sizeof(text)
                    || memcmp(text, "/system/bin/linker64", sizeof(text))) return false;
            interp = true;
        }
    }
    return interp && dynamic;
}

static void child_error(int stage, int error) {
    int message[2] = { stage, error };
    (void)write(3, message, sizeof(message));
    _exit(126);
}

/* Only syscall wrappers below: no JNI, allocation, locks, stdio or logging after fork. */
static void child(const char *path, int out, int errors, int diagnostic, int nullfd,
                  int maxfd, pid_t parent) {
    /* All sources were moved above 3 before fork, avoiding dup2 source collisions. */
    if (dup2(errors, 3) < 0 || fcntl(3, F_SETFD, FD_CLOEXEC)) _exit(125);
    if (prctl(PR_SET_PDEATHSIG, SIGKILL)) child_error(1, errno);
    if (getppid() != parent) _exit(125);
    if (dup2(nullfd, 0) < 0 || dup2(out, 1) < 0 || dup2(diagnostic, 2) < 0)
        child_error(1, errno);
    for (int fd = 4; fd < maxfd; ++fd) close(fd);
    struct rlimit cpu = { 1, 1 }, core = { 0, 0 };
    if (setrlimit(RLIMIT_CPU, &cpu) || setrlimit(RLIMIT_CORE, &core)) child_error(1, errno);
    struct sigaction action = { .sa_handler = SIG_DFL };
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGALRM, &action, NULL) || sigaction(SIGPIPE, &action, NULL)) child_error(1, errno);
    sigset_t empty;
    sigemptyset(&empty);
    if (sigprocmask(SIG_SETMASK, &empty, NULL)) child_error(1, errno);
    alarm(2); /* Persists across exec; backstop if the parent vanishes or stalls. */
    char *const argv[] = { "pdva_launch_v1", NULL };
    char *const environment[] = { "LANG=C", NULL };
    execve(path, argv, environment);
    child_error(2, errno);
}

static int high_fd(int fd) {
    if (fd < 0) return -1;
    int copy = fcntl(fd, F_DUPFD_CLOEXEC, 4);
    int error = errno;
    close(fd);
    errno = error;
    return copy;
}

static void launch(JNIEnv *env, jstring directory, jlong *r) {
    r[ABI] = 1;
    const char *dir = (*env)->GetStringUTFChars(env, directory, NULL);
    if (!dir) return;
    char path[PATH_MAX];
    int length = snprintf(path, sizeof(path), "%s/libpdva_launch.so", dir);
    bool absolute = dir[0] == '/';
    (*env)->ReleaseStringUTFChars(env, directory, dir);
    if (!absolute || length < 0 || length >= (int)sizeof(path)) { r[PRE_ERR] = EINVAL; return; }
    int payload = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    struct stat st;
    if (payload < 0) { r[PRE_ERR] = errno; return; }
    bool valid = fstat(payload, &st) == 0 && S_ISREG(st.st_mode)
        && st.st_size > 0 && st.st_size <= 1048576 && st.st_uid != getuid()
        && !(st.st_mode & (S_IWGRP|S_IWOTH|S_ISUID|S_ISGID)) && elf_ok(payload);
    close(payload);
    if (!valid) { r[PRE_ERR] = ENOEXEC; return; }
    r[ELF] = 1;
    struct rlimit files;
    if (getrlimit(RLIMIT_NOFILE, &files)) { r[PRE_ERR] = errno; return; }
    /* Refuse unbounded descriptor cleanup. Hard ceiling also covers previously opened FDs. */
    if (files.rlim_max > 65536 || files.rlim_cur > files.rlim_max) { r[PRE_ERR] = EOVERFLOW; return; }
    // Account for descriptors opened before a previous hard-limit reduction too.
    DIR *fds = opendir("/proc/self/fd");
    if (!fds) { r[PRE_ERR] = errno; return; }
    struct dirent *entry;
    bool bounded = true;
    errno = 0;
    while ((entry = readdir(fds)) != NULL) {
        unsigned long number = 0;
        const char *name = entry->d_name;
        if (*name == '.') continue;
        while (*name >= '0' && *name <= '9' && number < 65536) number = number*10 + (unsigned)(*name++ - '0');
        if (*name || number >= 65536) bounded = false;
    }
    int scan_error = errno;
    closedir(fds);
    if (!bounded || scan_error) { r[PRE_ERR] = scan_error ? scan_error : EOVERFLOW; return; }
    int pipes[6] = {-1,-1,-1,-1,-1,-1}, nullfd = -1;
    for (int i = 0; i < 6; i += 2) {
        if (pipe2(pipes+i, O_CLOEXEC | O_NONBLOCK)) { r[PRE_ERR] = errno; goto done; }
        pipes[i] = high_fd(pipes[i]); pipes[i+1] = high_fd(pipes[i+1]);
        if (pipes[i] < 0 || pipes[i+1] < 0) { r[PRE_ERR] = errno; goto done; }
    }
    nullfd = high_fd(open("/dev/null", O_RDWR | O_CLOEXEC));
    if (nullfd < 0) { r[PRE_ERR] = errno; goto done; }
    int64_t start = millis();
    if (start < 0) { r[PRE_ERR] = errno; goto done; }
    pid_t parent = getpid(), pid = fork();
    if (pid < 0) { r[CREATE] = -1; r[CREATE_ERR] = errno; goto done; }
    if (!pid) child(path, pipes[1], pipes[3], pipes[5], nullfd, 65536, parent);
    r[CREATE] = 1; r[CLEAN] = 0;
    for (int i = 1; i < 6; i += 2) { close(pipes[i]); pipes[i] = -1; }
    /* Wait without blocking the worker indefinitely. Child writes at most pipe capacity. */
    const struct pdva_wait_ops ops = { wait_child, kill_child, millis, pause_wait };
    struct pdva_wait_result waited = pdva_wait(pid, start, &ops);
    r[TIMEOUT] = waited.timeout; r[KILL_ERR] = waited.kill_error;
    if (waited.error) { r[WAIT] = -1; r[WAIT_ERR] = waited.error; }
    if (waited.reaped) {
        r[WAIT] = 1; r[CLEAN] = 1;
        if (WIFEXITED(waited.status)) r[EXIT_CODE] = WEXITSTATUS(waited.status);
        if (WIFSIGNALED(waited.status)) r[SIGNAL] = WTERMSIG(waited.status);
    }
    int error_message[3] = {0};
    ssize_t en = read(pipes[2], error_message, sizeof(error_message));
    if (en == 2*sizeof(int) && error_message[0] == 2 && error_message[1] > 0) {
        r[EXEC] = -1; r[EXEC_ERR] = error_message[1];
    } else if (en == 2*sizeof(int) && error_message[0] == 1 && error_message[1] > 0) {
        r[SETUP_ERR] = error_message[1];
    }
    unsigned char bytes[sizeof(struct pdva_wire)+1];
    ssize_t n = read(pipes[0], bytes, sizeof(bytes));
    struct pdva_wire wire;
    if (n == sizeof(wire)) {
        memcpy(&wire, bytes, sizeof(wire));
        if (wire.magic == PDVA_MAGIC && wire.result == 42 && wire.pid == (uint32_t)pid
                && wire.ppid == (uint32_t)parent && wire.context >= 0 && wire.context <= 2
                && wire.seccomp >= -1 && wire.seccomp <= 2
                && wire.capabilities >= -1 && wire.capabilities <= 1
                && wire.extra_fds >= -1 && wire.extra_fds <= 65536 && en == 0) {
            r[OUTPUT] = 1; r[EXEC] = 1; r[PID_OK] = pid != parent;
            r[UID_OK] = wire.uid == (uint32_t)getuid();
            r[EUID_OK] = wire.euid == (uint32_t)geteuid();
            r[CONTEXT] = wire.context; r[SECCOMP] = wire.seccomp;
            r[CAPS] = wire.capabilities; r[FDS] = wire.extra_fds;
        } else r[OUTPUT] = -1;
    } else if (n > 0) r[OUTPUT] = -1;
    char diagnostic[257] = {0};
    n = read(pipes[4], diagnostic, sizeof(diagnostic)-1);
    if (n > 0) r[LINKER] = strstr(diagnostic, "CANNOT LINK EXECUTABLE") ? 1 : 2;
done:
    for (int i = 0; i < 6; ++i) if (pipes[i] >= 0) close(pipes[i]);
    if (nullfd >= 0) close(nullfd);
}
#endif

JNIEXPORT jlongArray JNICALL Java_org_pdva_gate0_WorkerService_launchNative(
        JNIEnv *env, jclass type, jstring directory) {
    (void)type;
    jlong r[COUNT] = {0};
    r[CLEAN] = 1; r[EXIT_CODE] = -1; r[SECCOMP] = -1; r[CAPS] = -1; r[FDS] = -1;
#if defined(__aarch64__)
    r[ABI] = 1;
    if (directory) launch(env, directory, r);
    else r[PRE_ERR] = EINVAL;
#else
    (void)directory;
#endif
    if ((*env)->ExceptionCheck(env)) return NULL;
    jlongArray result = (*env)->NewLongArray(env, COUNT);
    if (result) (*env)->SetLongArrayRegion(env, result, 0, COUNT, r);
    return result;
}
