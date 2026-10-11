#ifdef NDEBUG
#error Native wait controls require assertions; do not define NDEBUG.
#endif
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "../../main/cpp/launch_wait.h"

/* No Android target execution, fork, sleep, or real signals in this control. */
static int scenario, calls, kills, pauses;
static int64_t clock_value;
static int wait_control(int pid, int *status) {
    ++calls;
    *status = 42;
    if (scenario == 0 || (scenario == 1 && calls == 3) || (scenario == 2 && kills)) return pid;
    if (scenario == 1) { errno = EINTR; return -1; }
    if (scenario == 3) { errno = ECHILD; return -1; }
    return 0;
}
static int kill_control(int pid) {
    assert(pid == 123); ++kills;
    if (scenario == 4) { errno = EPERM; return -1; }
    return 0;
}
static int64_t clock_control(void) {
    if (scenario == 5) return -1;
    if (scenario != 6) clock_value += 10;
    return clock_value;
}
static void pause_control(void) { ++pauses; }
static struct pdva_wait_result run(int value) {
    scenario = value; calls = kills = pauses = 0; clock_value = 0;
    errno = 0;
    const struct pdva_wait_ops ops = {wait_control, kill_control, clock_control, pause_control};
    return pdva_wait(123, 0, &ops);
}
int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--fail-assert") == 0) {
        assert(0 && "PDVA injected assertion failure");
        return 2; /* CI must observe assertion termination, not this fallback. */
    }
    if (argc != 1) return 2;
    struct pdva_wait_result r = run(0);
    assert(r.reaped && r.status == 42 && !r.timeout && !r.error && !r.kill_error
            && calls == 1 && kills == 0 && pauses == 0);
    puts("PASS: immediate successful reap");
    r = run(1);
    assert(r.reaped && r.status == 42 && !r.timeout && !r.error && !r.kill_error
            && calls == 3 && kills == 0 && pauses == 2);
    puts("PASS: EINTR retry");
    r = run(2);
    assert(r.reaped && r.status == 42 && r.timeout && !r.error && !r.kill_error
            && kills == 1 && calls == 251 && pauses == 249);
    puts("PASS: timeout and successful reap");
    r = run(3);
    assert(!r.reaped && !r.timeout && r.error == ECHILD && !r.kill_error
            && kills == 0 && calls == 1 && pauses == 0);
    puts("PASS: ECHILD without unsafe kill");
    r = run(4);
    assert(!r.reaped && r.timeout && !r.error && r.kill_error == EPERM
            && calls == 300 && kills == 1 && pauses == 299);
    puts("PASS: kill failure");
    r = run(5);
    assert(!r.reaped && r.timeout && !r.error && !r.kill_error
            && kills == 1 && calls == 51 && pauses == 50);
    puts("PASS: clock failure");
    r = run(6);
    assert(!r.reaped && r.timeout && !r.error && !r.kill_error
            && calls == 350 && pauses == 350 && kills == 1);
    puts("PASS: frozen-clock iteration bound");
    return 0;
}
