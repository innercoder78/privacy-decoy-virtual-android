/* Original PDVA disposable Linux research. Fixed scripts, not a secure broker. */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <unistd.h>

#if !defined(__linux__) || !defined(__x86_64__)
#error Native Linux x86_64 is required
#endif

/* Exactly one mutation per build; zero is the real implementation. */
#ifndef MUTATION
#define MUTATION 0
#endif
enum { OK = 1, DENIED_REVOKED, DENIED_EPOCH, DENIED_INSTANCE,
       DENIED_REPLAY, DENIED_STATE, UNKNOWN_TRANSPORT };
struct packet { uint32_t instance, epoch, sequence, value; };
_Static_assert(sizeof(struct packet) == 16, "fixed local ABI");
_Static_assert(sizeof(void *) == 8, "native LP64 only");

static void fail(void) { fputs("FAIL:fixture\n", stderr); exit(1); }
static void limit(int kind, rlim_t value) {
    struct rlimit bound = {value, value};
    if (setrlimit(kind, &bound)) fail();
}
static char command(void) {
    char c;
    if (read(STDIN_FILENO, &c, 1) != 1) fail();
    return c;
}
static void expect(char wanted) { if (command() != wanted) fail(); }
static void send_packet(int fd, struct packet p) {
    if (send(fd, &p, sizeof(p), MSG_NOSIGNAL) != sizeof(p)) fail();
}
static struct packet receive(int fd) {
    struct packet p;
    if (recv(fd, &p, sizeof(p), MSG_TRUNC) != sizeof(p)) fail();
    return p;
}
static int descriptor(const char *s) {
    char *end;
    long n = strtol(s, &end, 10);
    if (!*s || *end || n < 3 || n >= 64) fail();
    return (int)n;
}
static volatile unsigned char *mapping(int fd, int writeable, int private_map) {
    void *p = mmap(NULL, 4096, PROT_READ | (writeable ? PROT_WRITE : 0),
                   private_map ? MAP_PRIVATE : MAP_SHARED, fd, 0);
    if (p == MAP_FAILED) fail();
    return p;
}
static void unmap(volatile unsigned char *p) {
    if (munmap((void *)p, 4096)) fail();
}

static void mapped(int fd, int writer) {
    volatile unsigned char *p = mapping(fd, writer, writer && MUTATION == 1);
    if (close(fd)) fail();
    puts("MAPPED_FD_CLOSED");
    for (unsigned i = 0; i < 12; ++i) {
        char c = command();
        if (c == 'X') { unmap(p); return; }
        if (c == 'W' && writer) { p[0] = 90; puts("WROTE_90"); }
        else if (c == 'S' && !writer) printf("STATE %u %u\n", p[0], p[1]);
        else fail();
    }
    fail();
}

static void worker(int fd) {
    uint32_t next = 1, copied = 0;
    int disclosed = 0, uncertain = 0;
    puts("WORKER_READY");
    for (unsigned i = 0; i < 12; ++i) {
        char c = command();
        if (c == 'X') { if (close(fd)) fail(); return; }
        if (c == 'K') { printf("COPY %d %u\n", disclosed, copied); continue; }
        if (c != 'Q' && c != 'E' && c != 'I' && c != 'P') fail();
        if (uncertain && MUTATION != 9) { puts("LOCKED_UNKNOWN"); continue; }
        struct packet request = {7, 11, next++, 0};
        if (c == 'E') request.epoch = 10;
        if (c == 'I') request.instance = 8;
        if (c == 'P') request.sequence = 1;
        ssize_t sent = send(fd, &request, sizeof(request), MSG_NOSIGNAL);
        struct packet reply = {0, 0, UNKNOWN_TRANSPORT, 0};
        if (sent == sizeof(request)) {
            ssize_t got = recv(fd, &reply, sizeof(reply), MSG_TRUNC);
            if (got == 0 || (got == -1 && errno == ECONNRESET)) {
                reply = (struct packet){0, 0, UNKNOWN_TRANSPORT, 0};
            } else if (got != sizeof(reply)) fail();
        } else if (!(sent == -1 && (errno == EPIPE || errno == ECONNRESET))) fail();
        if (reply.instance || reply.epoch || reply.sequence < OK ||
            reply.sequence > UNKNOWN_TRANSPORT) fail();
        if (reply.sequence == OK) { copied = reply.value; disclosed = 1; }
        if (reply.sequence == UNKNOWN_TRANSPORT) uncertain = 1;
        if (MUTATION == 3 && reply.sequence == DENIED_REVOKED) {
            copied = 0; disclosed = 0;
        }
        printf("REPLY %u %u\n", reply.sequence, reply.value);
    }
    fail();
}

static void owner(int fd, int channel) {
    volatile unsigned char *p = mapping(fd, 1, 0);
    int revoked = 0, state = 1, pending = 0;
    uint32_t last = 0;
    puts("OWNER_READY");
    for (unsigned i = 0; i < 16; ++i) {
        char c = command();
        if (c == 'X' || c == 'L') {
            /* Explicit injected transport loss, never a revocation receipt. */
            if (pending && c == 'X') fail();
            if (close(channel) || close(fd)) fail();
            unmap(p); puts(c == 'L' ? "TRANSPORT_LOST" : "OWNER_STOPPED"); return;
        }
        if (c == 'V') { revoked = 1; puts(pending ? "REVOCATION_PENDING" : "REVOKED"); continue; }
        if (c == 'M') { state = 0; puts("STATE_MISSING"); continue; }
        if (c == 'A' || c == 'H') {
            if (pending) fail();
            struct packet r = receive(channel);
            uint32_t status = OK;
            if (!state && MUTATION != 8) status = DENIED_STATE;
            else if (revoked && MUTATION != 2) status = DENIED_REVOKED;
            else if (r.instance != 7 && MUTATION != 6) status = DENIED_INSTANCE;
            else if (r.epoch != 11 && MUTATION != 5) status = DENIED_EPOCH;
            else if (r.sequence <= last && MUTATION != 7) status = DENIED_REPLAY;
            if (status != OK) {
                send_packet(channel, (struct packet){0, 0, status, 0});
                puts("REQUEST_DENIED"); continue;
            }
            last = r.sequence; pending = 1;
            if (c == 'H') { puts("AUTHORIZED_PENDING"); continue; }
        } else if (c != 'C' && c != 'U') fail();
        if (!pending) fail();
        uint32_t status = OK, value = 0;
        if (revoked && MUTATION != 4 && MUTATION != 2) status = DENIED_REVOKED;
        else if (!state && MUTATION != 8) status = DENIED_STATE;
        else {
            /* The ONLY protected operation: fetch-and-increment fixed byte.
             * Both effect and operation count are independently observed. */
            value = p[0]; p[0] = (unsigned char)(value + 1); p[1]++;
        }
        pending = 0;
        if (c == 'U') {
            /* Effect committed, reply deliberately lost: outcome is uncertain
             * to worker even though observer knows the synthetic effect. */
            if (close(channel) || close(fd)) fail();
            unmap(p); puts("OUTCOME_UNACKNOWLEDGED"); return;
        }
        send_packet(channel, (struct packet){0, 0, status, value});
        puts(status == OK ? "COMMITTED" : "ABORTED");
    }
    fail();
}

int main(int argc, char **argv) {
    if (getuid() == 0 || geteuid() == 0 || argc < 3 || argc > 4) fail();
    if (setvbuf(stdout, NULL, _IONBF, 0)) fail();
    alarm(8); /* Safety backstop only; supervisor timeout is always failure. */
    limit(RLIMIT_CORE, 0); limit(RLIMIT_CPU, 2);
    limit(RLIMIT_AS, 64 * 1024 * 1024); limit(RLIMIT_NOFILE, 64);
    limit(RLIMIT_FSIZE, 4096); limit(RLIMIT_NPROC, 0);
    int fd = descriptor(argv[2]);
    /* Supervisor opens pidfd before this startup barrier is released. */
    expect('G');
    if (argc == 3 && !strcmp(argv[1], "mapper")) mapped(fd, 1);
    else if (argc == 3 && !strcmp(argv[1], "observer")) mapped(fd, 0);
    else if (argc == 3 && !strcmp(argv[1], "worker")) worker(fd);
    else if (argc == 4 && !strcmp(argv[1], "owner")) owner(fd, descriptor(argv[3]));
    else fail();
    puts("DONE");
    return 0;
}
