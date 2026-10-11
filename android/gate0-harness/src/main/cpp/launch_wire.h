#ifndef PDVA_LAUNCH_WIRE_H
#define PDVA_LAUNCH_WIRE_H
#include <stdint.h>
/* Private fixed-size pipe protocol, not an IPC command interface. */
#define PDVA_MAGIC 0x50445641u
struct pdva_wire {
    uint32_t magic, result, pid, ppid, uid, euid;
    int32_t context, seccomp, capabilities, extra_fds;
};
_Static_assert(sizeof(struct pdva_wire) == 40, "fixed wire size");
#endif
