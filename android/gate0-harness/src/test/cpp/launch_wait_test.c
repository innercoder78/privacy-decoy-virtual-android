#include <stdint.h>
/* Fake Linux errno values supplied by the injected operations, no host libc needed. */
static int control_errno;
#define errno control_errno
enum { EPERM = 1, EINTR = 4, ECHILD = 10 };
#define assert(condition) ((condition) ? (void)0 : __builtin_trap())
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
    const struct pdva_wait_ops ops = {wait_control, kill_control, clock_control, pause_control};
    return pdva_wait(123, 0, &ops);
}
int main(void) {
    struct pdva_wait_result r = run(0);
    assert(r.reaped && !r.timeout && !r.error && calls == 1 && kills == 0);
    r = run(1);
    assert(r.reaped && calls == 3 && kills == 0);
    r = run(2);
    assert(r.reaped && r.timeout && kills == 1 && calls <= 301);
    r = run(3);
    assert(!r.reaped && r.error == ECHILD && kills == 0 && calls == 1);
    r = run(4);
    assert(!r.reaped && r.timeout && r.kill_error == EPERM && calls <= 350 && kills == 1);
    r = run(5);
    assert(!r.reaped && r.timeout && kills == 1 && calls == 51);
    r = run(6);
    assert(!r.reaped && r.timeout && calls == 350 && pauses == 350 && kills == 1);
    return 0;
}
