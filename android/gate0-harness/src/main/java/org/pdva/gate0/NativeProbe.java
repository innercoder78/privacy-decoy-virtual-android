package org.pdva.gate0;

final class NativeProbe {
    static { System.loadLibrary("substrate"); }
    private NativeProbe() {}
    // Only the manager calls allocation. This is synthetic memory, not app state.
    static native long allocateControl();
    static native boolean releaseControl(long address);
    static native long[] run(String fixedSentinel, int managerPid, long controlAddress,
                             int sentinelNumber, int readOnlyFd, int scratchFd);
    static native String context();
}
