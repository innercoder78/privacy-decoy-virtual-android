#define _GNU_SOURCE
#include <jni.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/ptrace.h>
#include <sys/syscall.h>
#include <sys/uio.h>
#include <netinet/in.h>

/* Fixed numeric observations only. No file contents, addresses or paths returned. */
typedef struct { jlong values[384]; size_t count; } results;
static void add(results *r, int id, long value, int error) {
    if (r->count + 3 <= sizeof(r->values) / sizeof(r->values[0])) {
        r->values[r->count++] = id;
        r->values[r->count++] = value;
        r->values[r->count++] = error;
    }
}
static void opened(results *r, int id, const char *path, int flags) {
    errno = 0;
    int fd = open(path, flags | O_CLOEXEC);
    int error = fd < 0 ? errno : 0;
    add(r, id, fd, error);
    if (fd >= 0) close(fd);
}
static int entries(const char *path) {
    DIR *d = opendir(path);
    if (!d) return -1;
    int count = 0;
    struct dirent *e;
    while ((e = readdir(d)) != NULL) {
        if (strcmp(e->d_name, ".") && strcmp(e->d_name, "..")) count++;
    }
    closedir(d);
    return count;
}
JNIEXPORT jlong JNICALL Java_org_pdva_gate0_NativeProbe_allocateControl(JNIEnv *env, jclass c) {
    (void)env; (void)c;
    unsigned char *p = calloc(1, 4096);
    if (p) memset(p, 0x5a, 4096);
    return (jlong)(uintptr_t)p;
}
JNIEXPORT jboolean JNICALL Java_org_pdva_gate0_NativeProbe_releaseControl(
        JNIEnv *env, jclass c, jlong address) {
    (void)env; (void)c;
    unsigned char *p = (unsigned char *)(uintptr_t)address;
    if (!p) return JNI_FALSE;
    int intact = 1;
    for (int i = 0; i < 4096; i++) if (p[i] != 0x5a) intact = 0;
    free(p);
    return intact ? JNI_TRUE : JNI_FALSE;
}
JNIEXPORT jstring JNICALL Java_org_pdva_gate0_NativeProbe_context(JNIEnv *env, jclass c) {
    (void)c;
    char buf[256] = {0};
    int fd = open("/proc/self/attr/current", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return (*env)->NewStringUTF(env, "Unknown");
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) return (*env)->NewStringUTF(env, "Unknown");
    for (ssize_t i = 0; i < n; i++) {
        char x = buf[i];
        if (x == '\n' || x == '\0') { buf[i] = 0; break; }
        if (!((x >= 'a' && x <= 'z') || (x >= 'A' && x <= 'Z') ||
              (x >= '0' && x <= '9') || x == ':' || x == ',' || x == '_'))
            return (*env)->NewStringUTF(env, "Unknown");
    }
    return (*env)->NewStringUTF(env, buf);
}
JNIEXPORT jlongArray JNICALL Java_org_pdva_gate0_NativeProbe_run(
        JNIEnv *env, jclass c, jstring locator, jint manager, jlong address,
        jint sentinel_number, jint ro, jint scratch) {
    (void)c;
    results r = { .count = 0 };
    add(&r, 1, getpid(), 0); add(&r, 2, getuid(), 0);
    add(&r, 3, geteuid(), 0); add(&r, 4, getgid(), 0); add(&r, 14, getegid(), 0);
    long page = sysconf(_SC_PAGESIZE); add(&r, 5, page, 0);
    gid_t groups[32];
    errno = 0; int count = getgroups(32, groups);
    add(&r, 6, count, count < 0 ? errno : 0);
    for (int i = 0; i < count; i++) add(&r, 1000 + i, groups[i], 0);
    errno = 0; int fds = entries("/proc/self/fd");
    add(&r, 7, fds, fds < 0 ? errno : 0);
    FILE *maps = fopen("/proc/self/maps", "r");
    int lines = 0, executable = 0;
    if (maps) {
        char line[1024], perms[5];
        while (fgets(line, sizeof(line), maps)) {
            if (sscanf(line, "%*s %4s", perms) == 1) {
                lines++; if (perms[2] == 'x') executable++;
            }
        }
        fclose(maps);
        add(&r, 8, lines, 0); add(&r, 9, executable, 0);
    } else { add(&r, 8, -1, errno); add(&r, 9, -1, errno); }

#if defined(__aarch64__)
    /* mov w0,#42 ; ret. Anonymous RW -> RX, never RWX; no fallback bypass. */
    add(&r, 15, 1, 0);
    const uint32_t code[] = { 0x52800540u, 0xd65f03c0u };
    errno = 0;
    void *codepage = mmap(NULL, (size_t)page, PROT_READ | PROT_WRITE,
                         MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    add(&r, 10, codepage == MAP_FAILED ? -1 : 0, codepage == MAP_FAILED ? errno : 0);
    if (codepage != MAP_FAILED) {
        memcpy(codepage, code, sizeof(code));
        __builtin___clear_cache((char *)codepage, (char *)codepage + sizeof(code));
        errno = 0; int protect = mprotect(codepage, (size_t)page, PROT_READ | PROT_EXEC);
        add(&r, 11, protect, protect < 0 ? errno : 0);
        if (protect == 0) {
            int (*fixture)(void) = (int (*)(void))codepage;
            add(&r, 12, fixture(), 0);
        }
        munmap(codepage, (size_t)page);
    }
#else
    add(&r, 15, 2, 0);
    add(&r, 12, -1, ENOTSUP);
#endif
#ifdef __NR_memfd_create
    errno = 0; int mem = (int)syscall(__NR_memfd_create, "pdva-synthetic", 1u);
    add(&r, 13, mem, mem < 0 ? errno : 0);
    if (mem >= 0) close(mem);
#else
    add(&r, 13, -1, ENOSYS);
#endif
    const char *path = (*env)->GetStringUTFChars(env, locator, NULL);
    if (!path) return NULL;
    opened(&r, 20, path, O_RDONLY);
    errno = 0;
    int alt = (int)syscall(__NR_openat, AT_FDCWD, path, O_RDONLY | O_CLOEXEC, 0);
    add(&r, 21, alt, alt < 0 ? errno : 0);
    if (alt >= 0) close(alt);
    opened(&r, 22, path, O_WRONLY); /* No mutation even if unexpectedly opened. */
    (*env)->ReleaseStringUTFChars(env, locator, path);
    char proc[96];
    snprintf(proc, sizeof(proc), "/proc/%d/fd/%d", manager, sentinel_number);
    opened(&r, 26, proc, O_RDONLY);
    snprintf(proc, sizeof(proc), "/proc/%d/mem", manager);
    opened(&r, 23, proc, O_RDONLY);
    snprintf(proc, sizeof(proc), "/proc/%d/fd", manager);
    opened(&r, 24, proc, O_RDONLY | O_DIRECTORY);
    snprintf(proc, sizeof(proc), "/proc/%d/status", manager);
    opened(&r, 25, proc, O_RDONLY);

    unsigned char byte = 0x5a;
    struct iovec local = { &byte, 1 };
    struct iovec remote = { (void *)(uintptr_t)address, 1 };
    errno = 0; ssize_t rv = process_vm_readv(manager, &local, 1, &remote, 1, 0);
    add(&r, 30, rv, rv < 0 ? errno : 0);
    byte = 0x5a;
    errno = 0; rv = process_vm_writev(manager, &local, 1, &remote, 1, 0);
    add(&r, 31, rv, rv < 0 ? errno : 0);
    remote.iov_base = &byte;
    errno = 0; rv = process_vm_readv(getpid(), &local, 1, &remote, 1, 0);
    add(&r, 32, rv, rv < 0 ? errno : 0);
    errno = 0; rv = process_vm_writev(getpid(), &local, 1, &remote, 1, 0);
    add(&r, 33, rv, rv < 0 ? errno : 0);
    /* Non-stopping peek only. Attach would suspend the management UI. */
    errno = 0;
    long trace = ptrace(PTRACE_PEEKDATA, manager, (void *)(uintptr_t)address, 0);
    add(&r, 34, trace, errno);
    errno = 0; int signal = kill(manager, 0); /* Existence/permission only, no signal. */
    add(&r, 35, signal, signal < 0 ? errno : 0);

    for (int i = 0; i < 4; i++) {
        int family = (i % 2) ? AF_INET6 : AF_INET;
        int type = (i < 2) ? SOCK_STREAM : SOCK_DGRAM;
        errno = 0; int sock = socket(family, type | SOCK_CLOEXEC | SOCK_NONBLOCK, 0);
        add(&r, 40 + i, sock, sock < 0 ? errno : 0);
        if (sock >= 0) {
            int connected;
            errno = 0;
            if (family == AF_INET) {
                struct sockaddr_in a = { .sin_family = AF_INET,
                    .sin_port = htons(9), .sin_addr.s_addr = htonl(INADDR_LOOPBACK) };
                connected = connect(sock, (struct sockaddr *)&a, sizeof(a));
            } else {
                struct sockaddr_in6 a = { .sin6_family = AF_INET6,
                    .sin6_port = htons(9), .sin6_addr = IN6ADDR_LOOPBACK_INIT };
                connected = connect(sock, (struct sockaddr *)&a, sizeof(a));
            }
            add(&r, 50 + i, connected, connected < 0 ? errno : 0);
            close(sock); /* No application data, DNS, external address or blocking wait. */
        }
    }
    byte = 0;
    errno = 0; rv = pread(ro, &byte, 1, 0);
    add(&r, 60, rv == 1 ? byte : -1, rv < 0 ? errno : 0);
    byte = 'X';
    errno = 0; rv = pwrite(ro, &byte, 1, 0);
    add(&r, 61, rv, rv < 0 ? errno : 0);
    errno = 0; rv = pwrite(scratch, &byte, 1, 0);
    add(&r, 62, rv, rv < 0 ? errno : 0);
    int first = dup(ro), second = first < 0 ? -1 : dup(first);
    if (first >= 0) close(first);
    errno = 0; rv = pread(second, &byte, 1, 0);
    add(&r, 63, rv == 1 ? byte : -1, rv < 0 ? errno : 0);
    if (second >= 0) close(second);
    snprintf(proc, sizeof(proc), "/proc/self/fd/%d", ro);
    opened(&r, 64, proc, O_RDONLY);
    opened(&r, 65, proc, O_RDWR);
    const char *nodes[] = { "/sdcard", "/dev/kvm", "/dev/kgsl-3d0",
        "/dev/dri/renderD128", "/dev/video0", "/dev/snd/controlC0" };
    for (int i = 0; i < 6; i++) opened(&r, 70 + i, nodes[i], O_RDONLY | O_NONBLOCK);
    jlongArray out = (*env)->NewLongArray(env, (jsize)r.count);
    if (out) (*env)->SetLongArrayRegion(env, out, 0, (jsize)r.count, r.values);
    return out;
}
