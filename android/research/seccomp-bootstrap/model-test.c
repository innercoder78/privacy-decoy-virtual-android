/* Host-only independent fault driver. Real pthreads; ALL prctl/seccomp modeled.
 * Never compile this into an Android artifact. One invocation per process.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <pthread.h>
#include <stdarg.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

static int scenario, creates;
static atomic_int synchronized_filter;
static _Thread_local int local_filter, local_nnp;
static void *(*next_start)(void *);
static void *next_argument;
static int inherited_filter, inherited_nnp;

static void *start(void *unused) {
    (void)unused;
    local_filter = inherited_filter; local_nnp = inherited_nnp;
    return next_start(next_argument);
}
static int modeled_create(pthread_t *t, const pthread_attr_t *attr,
                          void *(*entry)(void *), void *arg) {
    ++creates;
    if ((scenario == 6 && creates == 1) || (scenario == 7 && creates == 2)) return EAGAIN;
    next_start = entry; next_argument = arg;
    inherited_filter = local_filter; inherited_nnp = local_nnp;
    return pthread_create(t, attr, start, NULL);
}
static int modeled_prctl(int option, ...) {
    if (option == PR_SET_NO_NEW_PRIVS) {
        if (scenario == 5) { errno = EPERM; return -1; }
        local_nnp = 1; return 0;
    }
    if (option == PR_GET_NO_NEW_PRIVS) return local_nnp || atomic_load(&synchronized_filter);
    if (option == PR_GET_SECCOMP) return 2; /* inherited baseline already filtered */
    abort();
}
static long modeled_syscall(long nr, ...) {
    va_list ap;
    va_start(ap, nr);
    long value;
    if (nr == SYS_gettid) {
        value = syscall(SYS_gettid);
    } else if (nr == SYS_getpid) {
        long marker = va_arg(ap, long);
        if ((uint64_t)marker == UINT64_C(0x5044564150524f42) &&
                (scenario == 8 || local_filter || atomic_load(&synchronized_filter))) {
            errno = EACCES; value = -1;
        } else value = getpid();
    } else if (nr == SYS_seccomp) {
        int operation = va_arg(ap, int);
        unsigned long flags = va_arg(ap, unsigned long);
        const struct sock_fprog *program = va_arg(ap, const struct sock_fprog *);
        if (operation != SECCOMP_SET_MODE_FILTER) abort();
        if (!program->len) { errno = EINVAL; value = -1; }
        else {
            local_filter = 1;
            if (flags == SECCOMP_FILTER_FLAG_TSYNC) atomic_store(&synchronized_filter, 1);
            else if (flags != 0) abort();
            /* Deliberately inconsistent observations ensure late probe checks
             * cannot conceal a bypass of the exact-zero installation guard. */
            if (scenario == 3) value = 123;
            else if (scenario == 4) { errno = EINVAL; value = -1; }
            else value = 0;
        }
    } else abort();
    va_end(ap);
    return value;
}

#define PDVA_MODEL 1
#define syscall modeled_syscall
#define prctl modeled_prctl
#define pthread_create modeled_create
#include "bootstrap.c"

int main(int argc, char **argv) {
    if (argc != 2 || getuid() == 0) return 90;
    scenario = atoi(argv[1]);
    if (scenario < 0 || scenario > 8) return 90;
    const struct receipt *r = pdva_bootstrap(scenario == 1 ? 1 : scenario == 2 ? 2 : 0);
    if ((scenario == 3 || scenario == 4) && r && r->payload != 0) {
        puts("REJECTED: payload after failed install"); return 42;
    }
    static const long failures[] = {0, 9, 6, 6, 6, 5, 3, 11, 2};
    if (!r || r->failure != failures[scenario] || r->payload != (scenario == 0 ? 42 : 0)) return 91;
    if (scenario == 0 && (r->install != 0 || r->peer_join || r->new_join ||
            r->peer_after.marked != -1 || r->newborn.marked != -1)) return 92;
    if (scenario == 1 && (r->after.marked != -1 ||
            r->peer_after.marked != r->before.pid || r->peer_after.error != 0 || r->peer_join)) return 93;
    if (pdva_bootstrap(0) != NULL) return 94;
    puts("PASS: modeled contract");
    return 0;
}
