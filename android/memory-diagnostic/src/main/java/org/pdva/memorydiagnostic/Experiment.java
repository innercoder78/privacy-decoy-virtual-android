package org.pdva.memorydiagnostic;

/** One bounded allocation admission experiment; never reads or writes mapping bytes. */
final class Experiment {
    enum Outcome { Ready, Admitted, Unsupported, Denied, ResourceFailure, Unknown }
    enum Op { None, Initiation, Interrupted, Api, Abi, Bitness, PageSize,
        Create, Resize, MapRW, MapRX, UnmapRX, UnmapRW, Close }
    enum Cleanup { NotNeeded, Complete, Incomplete }
    static final class Fault extends Exception {
        final int errno;
        Fault(int errno) { this.errno = errno; }
    }
    interface Ops {
        int api() throws Fault;
        boolean arm64() throws Fault;
        boolean bit64() throws Fault;
        long pageSize() throws Fault;
        void create() throws Fault;
        void resize(long size) throws Fault;
        void mapRW(long size) throws Fault;
        void mapRX(long size) throws Fault;
        void unmapRX(long size) throws Fault;
        void unmapRW(long size) throws Fault;
        void close() throws Fault;
    }
    static final class Result {
        Outcome outcome;
        Op first = Op.None;
        int errno;
        Cleanup cleanup = Cleanup.NotNeeded;
        Op cleanupFirst = Op.None;
        int cleanupErrno;
        Result(Outcome outcome) { this.outcome = outcome; }
        static Result unknown(Op op) {
            Result result = new Result(Outcome.Unknown);
            result.first = op;
            return result;
        }
        // Only enums and bounded numeric errno; no exception text or resource values.
        String display() {
            return "Result=" + outcome + "\nOperation=" + first + "\nErrno=" + errno
                + "\nCleanup=" + cleanup + "\nCleanupOperation=" + cleanupFirst
                + "\nCleanupErrno=" + cleanupErrno;
        }
    }
    private static int errno(Throwable failure) {
        return failure instanceof Fault && ((Fault) failure).errno > 0
            && ((Fault) failure).errno <= 4095 ? ((Fault) failure).errno : 0;
    }
    private static void fail(Result result, Op op, Throwable failure, boolean cleanup) {
        int number = errno(failure);
        if (result.first == Op.None) {
            result.first = op;
            result.errno = number;
            result.outcome = number == 1 || number == 13 ? Outcome.Denied
                : number == 12 ? Outcome.ResourceFailure : Outcome.Unknown;
        }
        if (cleanup) {
            result.outcome = Outcome.Unknown;
            result.cleanup = Cleanup.Incomplete;
            if (result.cleanupFirst == Op.None) {
                result.cleanupFirst = op;
                result.cleanupErrno = number;
            }
        }
    }
    static Result run(Ops ops) {
        Result result = new Result(Outcome.Admitted);
        Op stage = Op.Api;
        long size = 0;
        boolean fd = false, rw = false, rx = false;
        try {
            if (ops.api() != 37) { result.first = stage; result.outcome = Outcome.Unsupported; return result; }
            stage = Op.Abi;
            if (!ops.arm64()) { result.first = stage; result.outcome = Outcome.Unsupported; return result; }
            stage = Op.Bitness;
            if (!ops.bit64()) { result.first = stage; result.outcome = Outcome.Unsupported; return result; }
            stage = Op.PageSize;
            size = ops.pageSize();
            if (size != 4096 && size != 16384) {
                result.first = stage; result.outcome = Outcome.Unsupported; return result;
            }
            stage = Op.Create;
            ops.create(); fd = true;
            stage = Op.Resize;
            ops.resize(size);
            stage = Op.MapRW;
            ops.mapRW(size); rw = true;
            stage = Op.MapRX;
            ops.mapRX(size); rx = true;
        } catch (Throwable failure) {
            // Includes unexpected VM/linkage errors; never disclose their messages.
            fail(result, stage, failure, false);
        } finally {
            if (fd) result.cleanup = Cleanup.Complete;
            if (rx) {
                try { ops.unmapRX(size); }
                catch (Throwable failure) { fail(result, Op.UnmapRX, failure, true); }
            }
            if (rw) {
                try { ops.unmapRW(size); }
                catch (Throwable failure) { fail(result, Op.UnmapRW, failure, true); }
            }
            if (fd) {
                try { ops.close(); }
                catch (Throwable failure) { fail(result, Op.Close, failure, true); }
            }
        }
        return result;
    }
}
