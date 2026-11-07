package org.pdva.memorydiagnostic;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import static org.pdva.memorydiagnostic.Experiment.*;

/** Desktop JVM fault injection, not Android runtime evidence. No test libraries. */
public final class ExperimentTest {
    static int checks;
    static void check(boolean condition, String message) {
        checks++;
        if (!condition) throw new AssertionError(message);
    }
    static final class Fake implements Ops {
        int api = 37, number = 13;
        boolean arm = true, bits = true, unexpected;
        long page = 4096;
        final EnumSet<Op> failures = EnumSet.noneOf(Op.class);
        final List<Op> calls = new ArrayList<>();
        void call(Op op) throws Fault {
            calls.add(op);
            if (failures.contains(op)) {
                if (unexpected) throw new IllegalStateException("PRIVATE /path 0x1234 device-id");
                throw new Fault(number);
            }
        }
        void size(long size) { check(size == page && (size == 4096 || size == 16384), "one page only"); }
        public int api() throws Fault { call(Op.Api); return api; }
        public boolean arm64() throws Fault { call(Op.Abi); return arm; }
        public boolean bit64() throws Fault { call(Op.Bitness); return bits; }
        public long pageSize() throws Fault { call(Op.PageSize); return page; }
        public void create() throws Fault { call(Op.Create); }
        public void resize(long size) throws Fault { size(size); call(Op.Resize); }
        public void mapRW(long size) throws Fault { size(size); call(Op.MapRW); }
        public void mapRX(long size) throws Fault { size(size); call(Op.MapRX); }
        public void unmapRX(long size) throws Fault { size(size); call(Op.UnmapRX); }
        public void unmapRW(long size) throws Fault { size(size); call(Op.UnmapRW); }
        public void close() throws Fault { call(Op.Close); }
    }
    static final class MemoryStore implements Attempt.Store {
        boolean started, persist = true, throwsOnWrite;
        public boolean started() { return started; }
        public boolean markStarted() {
            if (throwsOnWrite) throw new IllegalStateException("PRIVATE");
            if (persist) started = true;
            return persist;
        }
    }
    public static void main(String[] args) {
        List<Op> success = List.of(Op.Api, Op.Abi, Op.Bitness, Op.PageSize, Op.Create,
            Op.Resize, Op.MapRW, Op.MapRX, Op.UnmapRX, Op.UnmapRW, Op.Close);
        for (long page : new long[] {4096, 16384}) {
            Fake f = new Fake(); f.page = page;
            Result r = Experiment.run(f);
            check(r.outcome == Outcome.Admitted && r.cleanup == Cleanup.Complete, "admission");
            check(f.calls.equals(success), "exact bounded sequence");
        }
        for (Op failure : success) {
            Fake f = new Fake(); f.failures.add(failure);
            Result r = Experiment.run(f);
            check(r.first == failure && r.errno == 13, "first operation and errno");
            List<Op> expected = new ArrayList<>(success.subList(0, success.indexOf(failure) + 1));
            if (failure.ordinal() >= Op.UnmapRX.ordinal()) {
                expected = success;
                check(r.outcome == Outcome.Unknown && r.cleanup == Cleanup.Incomplete, "cleanup unknown");
            } else {
                if (failure == Op.MapRX) expected.add(Op.UnmapRW);
                if (failure == Op.Resize || failure == Op.MapRW || failure == Op.MapRX) expected.add(Op.Close);
            }
            check(f.calls.equals(expected), "partial acquisition cleanup: " + failure);
        }
        Fake f = new Fake(); f.failures.addAll(EnumSet.of(Op.MapRX, Op.UnmapRW, Op.Close));
        Result r = Experiment.run(f);
        check(r.outcome == Outcome.Unknown && r.first == Op.MapRX && r.cleanupFirst == Op.UnmapRW,
            "preserve first failure despite multiple cleanup failures");
        check(f.calls.get(f.calls.size() - 1) == Op.Close, "close after unmap failure");
        f = new Fake(); f.failures.addAll(EnumSet.of(Op.UnmapRX, Op.UnmapRW, Op.Close));
        r = Experiment.run(f);
        check(f.calls.equals(success) && r.first == Op.UnmapRX, "independent cleanup");
        for (Op failure : success) {
            f = new Fake(); f.unexpected = true; f.failures.add(failure);
            r = Experiment.run(f);
            check(r.outcome == Outcome.Unknown && r.first == failure && r.errno == 0,
                "unexpected exception at every operation");
            if (failure == Op.UnmapRX || failure == Op.UnmapRW || failure == Op.Close) {
                check(f.calls.equals(success) && r.cleanup == Cleanup.Incomplete, "unexpected cleanup still independent");
            }
        }
        for (long page : new long[] {-1, 0, 1, 8192, 32768, Long.MAX_VALUE}) {
            f = new Fake(); f.page = page; r = Experiment.run(f);
            check(r.outcome == Outcome.Unsupported && !f.calls.contains(Op.Create), "reject page");
        }
        for (int api : new int[] {0, 30, 36, 38, Integer.MAX_VALUE}) {
            f = new Fake(); f.api = api;
            check(Experiment.run(f).outcome == Outcome.Unsupported && f.calls.equals(List.of(Op.Api)), "reject API");
        }
        f = new Fake(); f.arm = false;
        check(Experiment.run(f).first == Op.Abi && !f.calls.contains(Op.Create), "reject ABI");
        f = new Fake(); f.bits = false;
        check(Experiment.run(f).first == Op.Bitness && !f.calls.contains(Op.Create), "reject bitness");
        for (int number : new int[] {1, 13, 12, 22, 38, 5, -1, 99999}) {
            f = new Fake(); f.number = number; f.failures.add(Op.MapRX); r = Experiment.run(f);
            check(r.outcome == (number == 1 || number == 13 ? Outcome.Denied
                : number == 12 ? Outcome.ResourceFailure : Outcome.Unknown), "errno classification");
            check(r.errno == (number > 0 && number <= 4095 ? number : 0), "bounded errno");
        }
        f = new Fake(); f.unexpected = true; f.failures.add(Op.MapRX); r = Experiment.run(f);
        check(r.outcome == Outcome.Unknown && r.errno == 0 && r.cleanup == Cleanup.Complete, "unexpected failure");
        check(r.display().equals("Result=Unknown\nOperation=MapRX\nErrno=0\nCleanup=Complete\nCleanupOperation=None\nCleanupErrno=0"), "sanitized fixed report");
        MemoryStore store = new MemoryStore();
        Attempt attempt = new Attempt(store, false); f = new Fake();
        check(attempt.ready() && f.calls.isEmpty() && !store.started, "explicit initiation only");
        check(attempt.activate(f).outcome == Outcome.Admitted && store.started, "durable admission");
        int count = f.calls.size();
        check(attempt.activate(f).outcome == Outcome.Unknown && f.calls.size() == count, "repeated activation");
        check(!new Attempt(store, false).ready(), "fresh process blocks persisted attempt");
        check(!new Attempt(new MemoryStore(), true).ready(), "Activity recreation blocks");
        for (boolean throwing : new boolean[] {false, true}) {
            store = new MemoryStore(); store.persist = false; store.throwsOnWrite = throwing;
            attempt = new Attempt(store, false); f = new Fake();
            check(attempt.activate(f).first == Op.Initiation && f.calls.isEmpty(), "marker failure blocks acquisition");
            check(!attempt.ready(), "no retry after marker failure");
        }
        System.out.println("PASS: " + checks + " diagnostic JVM assertions; Android runtime NOT TESTED");
    }
}
