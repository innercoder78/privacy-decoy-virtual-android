#define _GNU_SOURCE
#include "launch_wire.h"
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <unistd.h>

/* No arguments, input, network, guest code, or host-data access. */
int main(int argc, char **argv) {
    (void)argv;
    if (argc != 1) return 64;
    struct pdva_wire r = { .magic = PDVA_MAGIC, .pid = (uint32_t)getpid(),
        .ppid = (uint32_t)getppid(), .uid = (uint32_t)getuid(),
        .euid = (uint32_t)geteuid(), .context = 0, .capabilities = -1,
        .seccomp = prctl(PR_GET_SECCOMP), .extra_fds = -1 };
    /* Deterministic synthetic arithmetic: sum 1..6 = 21, doubled = 42. */
    volatile uint32_t sum = 0;
    for (uint32_t i = 1; i <= 6; ++i) sum += i;
    r.result = sum * 2;
    DIR *fds = opendir("/proc/self/fd");
    if (fds) {
        r.extra_fds = 0;
        struct dirent *entry;
        errno = 0;
        while ((entry = readdir(fds)) != NULL) {
            char *end;
            long fd = strtol(entry->d_name, &end, 10);
            if (*entry->d_name && !*end && fd > 2 && fd != dirfd(fds)) ++r.extra_fds;
        }
        if (errno) r.extra_fds = -1;
        closedir(fds);
    }
    char buffer[4096] = {0};
    int fd = open("/proc/self/attr/current", O_RDONLY | O_CLOEXEC);
    if (fd >= 0) {
        ssize_t n = read(fd, buffer, 255);
        if (n > 0) r.context = strncmp(buffer, "u:r:isolated_app:", 17) == 0 ? 1 : 2;
        close(fd);
    }
    memset(buffer, 0, sizeof(buffer));
    fd = open("/proc/self/status", O_RDONLY | O_CLOEXEC);
    if (fd >= 0) {
        ssize_t n = read(fd, buffer, sizeof(buffer)-1);
        if (n > 0) {
            char *cap = strstr(buffer, "\nCapEff:\t");
            if (cap) {
                char *end;
                unsigned long long value = strtoull(cap + 9, &end, 16);
                if (end != cap + 9 && *end == '\n') r.capabilities = value == 0 ? 0 : 1;
            }
        }
        close(fd);
    }
    /* Exactly 40 bytes; errno/loader text is never included. Exit 42 is intentional. */
    ssize_t written;
    do { written = write(STDOUT_FILENO, &r, sizeof(r)); } while (written < 0 && errno == EINTR);
    return written == sizeof(r) && r.result == 42 ? 42 : 65;
}
