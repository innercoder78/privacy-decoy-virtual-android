package org.pdva.memorydiagnostic;

/** Persistent one-way admission, including across Activity/process recreation. */
final class Attempt {
    interface Store {
        boolean started();
        boolean markStarted();
    }
    private final Store store;
    private boolean consumed;
    Attempt(Store store, boolean recreated) { this.store = store; consumed = recreated; }
    boolean ready() {
        try { return !consumed && !store.started(); }
        catch (Throwable failure) { consumed = true; return false; }
    }
    synchronized Experiment.Result activate(Experiment.Ops ops) {
        if (!ready()) return Experiment.Result.unknown(Experiment.Op.Interrupted);
        consumed = true;
        try {
            if (!store.markStarted()) return Experiment.Result.unknown(Experiment.Op.Initiation);
        } catch (Throwable failure) {
            return Experiment.Result.unknown(Experiment.Op.Initiation);
        }
        return Experiment.run(ops);
    }
}
