#ifndef PDVA_LAUNCH_WAIT_H
#define PDVA_LAUNCH_WAIT_H
/* Bounded wait strategy, shared with deterministic host controls. No Android code. */
struct pdva_wait_result { int reaped, status, error, timeout, kill_error; };
struct pdva_wait_ops {
    int (*wait_child)(int, int *);
    int (*kill_child)(int);
    int64_t (*now)(void);
    void (*pause)(void);
};
static struct pdva_wait_result pdva_wait(int pid, int64_t start, const struct pdva_wait_ops *ops) {
    struct pdva_wait_result r = {0};
    for (int step = 0; step < 300; ++step) {
        int result = ops->wait_child(pid, &r.status);
        if (result == pid) { r.reaped = 1; return r; }
        if (result < 0 && errno != EINTR) { r.error = errno; return r; }
        int64_t now = ops->now();
        if (now < 0 || now-start >= 2500) break;
        ops->pause();
    }
    r.timeout = 1;
    /* We still own the child here; a wait error never authorizes signalling a PID. */
    if (ops->kill_child(pid)) r.kill_error = errno;
    for (int step = 0; step < 50; ++step) {
        int result = ops->wait_child(pid, &r.status);
        if (result == pid) { r.reaped = 1; return r; }
        if (result < 0 && errno != EINTR) { r.error = errno; return r; }
        ops->pause();
    }
    return r;
}
#endif
