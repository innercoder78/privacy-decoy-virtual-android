package org.pdva.gate0;

import android.content.*;
import android.os.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import org.json.*;

/** Management-only supervisor. Each instance has a new service identity and epoch. */
final class Session {
    private static String previousEpoch;
    private static final AtomicBoolean ACTIVE = new AtomicBoolean();
    final String epoch = java.util.UUID.randomUUID().toString().replace("-", "");
    private final Context context;
    private final CountDownLatch connected = new CountDownLatch(1), dead = new CountDownLatch(1);
    private volatile IBinder worker;
    private volatile boolean cancelled;
    private boolean bound;
    private final Binder owner = new Binder(); // No application operations implemented.
    Session(Context context) { this.context = context.getApplicationContext(); }
    void cancel() { cancelled = true; }
    interface Writer { void write(Parcel data); }
    private Parcel request(int code, String requestEpoch, Writer writer) throws Exception {
        if (cancelled && code != Protocol.STOP) throw new InterruptedException();
        IBinder current = worker;
        if (current == null) throw new IllegalStateException("not_connected");
        Parcel data = Parcel.obtain(), reply = Parcel.obtain();
        try {
            data.writeInterfaceToken(Protocol.DESCRIPTOR);
            data.writeString(requestEpoch);
            writer.write(data);
            if (!current.transact(code, data, reply, 0)) throw new IllegalStateException("transaction");
            reply.readException();
            return reply;
        } catch (Exception e) { reply.recycle(); throw e; }
        finally { data.recycle(); }
    }
    private boolean rejected(int code, String e, Writer writer) throws Exception {
        try { Parcel p = request(code, e, writer); p.recycle(); return false; }
        catch (IllegalArgumentException | SecurityException expected) { return true; }
    }
    private final ServiceConnection connection = new ServiceConnection() {
        @Override public void onServiceConnected(ComponentName name, IBinder service) {
            worker = service;
            try { service.linkToDeath(() -> dead.countDown(), 0); }
            catch (RemoteException e) { if (!service.isBinderAlive()) dead.countDown(); }
            connected.countDown();
        }
        @Override public void onServiceDisconnected(ComponentName name) {
            if (worker != null && !worker.isBinderAlive()) dead.countDown();
        }
        @Override public void onBindingDied(ComponentName name) {
            if (worker != null && !worker.isBinderAlive()) dead.countDown();
        }
        @Override public void onNullBinding(ComponentName name) { connected.countDown(); }
    };
    private static byte[] digest(File f) throws Exception {
        if (f.length() != 4096) return new byte[0];
        try (FileInputStream in = new FileInputStream(f)) {
            byte[] bytes = new byte[4096];
            int offset = 0, n;
            while (offset < bytes.length && (n = in.read(bytes, offset, bytes.length-offset)) > 0) offset += n;
            return offset == bytes.length ? MessageDigest.getInstance("SHA-256").digest(bytes) : new byte[0];
        }
    }
    private static void create(File f, byte[] bytes) throws IOException {
        try (FileOutputStream out = new FileOutputStream(f, false)) { out.write(bytes); }
    }

    String run(boolean simulateDeath) {
        Report report = new Report(epoch, Build.VERSION.SDK_INT);
        SharedPreferences launchState = context.getSharedPreferences("launch_lifetime", Context.MODE_PRIVATE);
        if (launchState.getBoolean("uncertain_child", false)) {
            report.add("launch_lockout", "known_cleanup", "blocked", 0, "UNKNOWN",
                    "A previous launch lacks cleanup acknowledgement. No automatic retry after restart");
            return report.json();
        }
        if (!ACTIVE.compareAndSet(false, true)) {
            report.add("session", "exclusive", "busy", 0, "UNKNOWN", "Another experiment still owns resources");
            return report.json();
        }
        File sentinel = new File(context.getFilesDir(), "gate0-sentinel");
        File canaryFile = new File(context.getFilesDir(), "gate0-canary");
        File scratchFile = new File(context.getFilesDir(), "gate0-scratch");
        ParcelFileDescriptor canary = null, scratch = null, protectedFile = null;
        SharedMemory frame = null;
        ByteBuffer pixels = null;
        byte[] expected = null;
        long control = 0;
        boolean initialized = false, returned = false;
        try {
            byte[] secret = new byte[4096];
            new SecureRandom().nextBytes(secret);
            create(sentinel, secret); expected = digest(sentinel);
            if (expected.length != 32) throw new IllegalStateException("sentinel_control");
            Arrays.fill(secret, (byte)0);
            protectedFile = ParcelFileDescriptor.open(sentinel, ParcelFileDescriptor.MODE_READ_ONLY);
            byte[] publicCanary = new byte[4096]; Arrays.fill(publicCanary, (byte)'C');
            create(canaryFile, publicCanary); create(scratchFile, new byte[4096]);
            canary = ParcelFileDescriptor.open(canaryFile, ParcelFileDescriptor.MODE_READ_ONLY);
            scratch = ParcelFileDescriptor.open(scratchFile, ParcelFileDescriptor.MODE_READ_WRITE);
            frame = SharedMemory.create("pdva-frame", Protocol.BYTES);
            pixels = frame.mapReadOnly();
            control = NativeProbe.allocateControl();
            if (control == 0) throw new IllegalStateException("memory_control");
            bound = context.bindIsolatedService(new Intent(context, WorkerService.class),
                    Context.BIND_AUTO_CREATE, "epoch_" + epoch, context.getMainExecutor(), connection);
            if (!bound || !connected.await(10, TimeUnit.SECONDS) || worker == null)
                throw new IllegalStateException("bind_failed");
            final long address = control;
            final int sentinelNumber = protectedFile.getFd();
            final ParcelFileDescriptor ro = canary, rw = scratch;
            final SharedMemory transport = frame;
            Parcel p = request(Protocol.INIT, epoch, d -> {
                d.writeLong(address); d.writeInt(sentinelNumber); d.writeStrongBinder(owner);
                d.writeTypedObject(ro, 0); d.writeTypedObject(rw, 0); d.writeTypedObject(transport, 0);
            });
            int pid = p.readInt(), uid = p.readInt(); p.recycle(); initialized = true;
            report.bool("distinct_worker_pid", pid != android.os.Process.myPid(), "Live response only");
            report.bool("distinct_worker_uid", uid != android.os.Process.myUid(), "No UID persistence assumption");
            if (pid == android.os.Process.myPid() || uid == android.os.Process.myUid())
                throw new IllegalStateException("not_isolated");
            report.bool("stale_epoch_rejected", rejected(Protocol.RUN, (previousEpoch == null ? "00000000000000000000000000000000" : previousEpoch), d -> {}),
                    "Current worker rejects incorrect epoch");
            report.bool("unknown_operation_rejected", rejected(99, epoch, d -> {}), "Fixed operation set");
            report.bool("oversized_control_rejected", rejected(Protocol.INPUT, epoch,
                    d -> d.writeByteArray(new byte[Protocol.MAX_CONTROL])), "4096 byte transaction limit");
            report.bool("trailing_control_rejected", rejected(Protocol.RUN, epoch, d -> d.writeInt(1)),
                    "No ignored trailing fields");
            report.bool("invalid_frame_rejected", rejected(Protocol.FRAME, epoch, d -> {
                d.writeInt(Integer.MAX_VALUE); d.writeInt(64); d.writeInt(256); d.writeInt(16384);
            }), "Exact dimensions and overflow-safe byte arithmetic");
            report.bool("input_out_of_range_rejected", rejected(Protocol.INPUT, epoch, d -> {
                d.writeInt(0); d.writeInt(256);
            }), "No arbitrary input strings");
            for (int sequence = 1; sequence <= 2; sequence++) {
                p = request(Protocol.FRAME, epoch, d -> {
                    d.writeInt(64); d.writeInt(64); d.writeInt(256); d.writeInt(16384);
                });
                int ack = p.readInt(); p.recycle();
                byte[] bytes = new byte[Protocol.BYTES]; boolean valid = ack == sequence;
                for (int i = 0; i < bytes.length; i++) {
                    bytes[i] = pixels.get(i);
                    valid &= bytes[i] == (byte)(i + sequence);
                }
                report.bool("frame_sequence_" + sequence, valid, "Synthetic transport. Not Android guest graphics");
                StringBuilder hex = new StringBuilder();
                for (byte b : MessageDigest.getInstance("SHA-256").digest(bytes))
                    hex.append(String.format(java.util.Locale.ROOT, "%02x", b & 255));
                String hash = hex.toString();
                report.add("frame_hash_" + sequence, "inventory", hash, 0, "UNKNOWN", "Synthetic fixed RGBA bytes");
            }
            report.bool("frame_quota_rejected", rejected(Protocol.FRAME, epoch, d -> {
                d.writeInt(64); d.writeInt(64); d.writeInt(256); d.writeInt(16384);
            }), "Two frames maximum per epoch");
            boolean input = true;
            for (int i = 0; i < Protocol.MAX_INPUT; i++) {
                final int index = i;
                p = request(Protocol.INPUT, epoch, d -> { d.writeInt(index); d.writeInt(42); });
                input &= p.readInt() == (42 ^ 0x5a); p.recycle();
            }
            report.bool("input_acknowledgements", input, "Synthetic tokens only");
            report.bool("input_flood_rejected", rejected(Protocol.INPUT, epoch,
                    d -> { d.writeInt(16); d.writeInt(42); }), "Sixteen tokens maximum per epoch");
            if (simulateDeath) {
                p = request(Protocol.KILL, epoch, d -> {}); p.recycle();
                boolean observed = dead.await(3, TimeUnit.SECONDS);
                report.add("worker_self_kill", "binder_death", observed ? "observed" : "not_observed",
                        0, observed ? "PASS" : "UNKNOWN",
                        "Ordinary self-kill with open capabilities. No independent process-reaping observation");
            } else {
                p = request(Protocol.RUN, epoch, d -> {});
                String raw = p.readString(); p.recycle(); returned = true;
                if (raw == null || raw.length() > Protocol.MAX_REPORT) throw new IllegalArgumentException("report");
                JSONObject object = new JSONObject(raw);
                if (!epoch.equals(object.getString("epoch")) || object.getInt("schema") != 1)
                    throw new IllegalArgumentException("report_epoch");
                JSONArray rows = object.getJSONArray("probes");
                if (rows.length() > 100) throw new IllegalArgumentException("report_count");
                for (int i = 0; i < rows.length(); i++) {
                    JSONObject row = rows.getJSONObject(i);
                    report.add(row.getString("probe"), row.getString("expected"), row.getString("observed"),
                            row.getLong("errno"), row.getString("status"), row.getString("limitations"));
                }
                report.bool("repeated_run_rejected", rejected(Protocol.RUN, epoch, d -> {}), "One native run per worker");
                report.bool("launch_stale_epoch_rejected", rejected(Protocol.LAUNCH,
                        "0".repeat(32), d -> {}), "Launch requires the authorized current epoch");
                report.bool("launch_trailing_rejected", rejected(Protocol.LAUNCH, epoch,
                        d -> d.writeInt(1)), "No launch arguments or path accepted");
                // Durable BEFORE IPC: owner death or a lost reply must not enable a new launch.
                if (!launchState.edit().putBoolean("uncertain_child", true).commit())
                    throw new IllegalStateException("launch_guard");
                p = request(Protocol.LAUNCH, epoch, d -> {});
                long[] launchValues = new long[LaunchResult.COUNT];
                p.readLongArray(launchValues); // Reject a different length before allocation.
                LaunchResult launch = new LaunchResult(launchValues);
                if (p.dataAvail() != 0) throw new IllegalArgumentException("launch_trailing");
                p.recycle();
                launch.append(report);
                if (launch.cleanupKnown()) {
                    if (!launchState.edit().putBoolean("uncertain_child", false).commit())
                        throw new IllegalStateException("launch_guard_clear");
                    report.bool("repeated_launch_rejected", rejected(Protocol.LAUNCH, epoch,
                            d -> {}), "One attempt including failure or Unsupported per worker");
                }
            }
        } catch (Throwable e) {
            // Categories only, never Throwable.toString/message/stack traces in exported evidence.
            report.add("experiment_completion", "completed", e instanceof LinkageError ? "native_load_failure" :
                    e instanceof InterruptedException ? "cancelled" : "operation_failed",
                    0, e instanceof LinkageError ? "FAIL" : "UNKNOWN", "Inspect separately. Missing result is never a pass");
        } finally {
            if (initialized && dead.getCount() != 0) {
                try {
                    Parcel p = request(Protocol.STOP, epoch, d -> {}); p.recycle();
                    try {
                        report.bool("stopped_epoch_rejected", rejected(Protocol.RUN, epoch, d -> {}),
                                "Old endpoint rejects control after stop");
                    } catch (DeadObjectException e) {
                        report.bool("stopped_epoch_rejected", true, "Old endpoint died before stale transaction");
                    }
                }
                catch (Exception ignored) { }
            }
            try {
                boolean death = worker != null && dead.await(3, TimeUnit.SECONDS);
                report.add("worker_binder_death", "observed", death ? "observed" : "not_observed",
                        0, death ? "PASS" : "UNKNOWN", "Binder death is not independent kernel reaping evidence");
                report.add("worker_reaped", "independent_observer", "not_measured", 0, "UNKNOWN",
                        "No reaping or no-surviving-child claim");
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
            if (bound) context.unbindService(connection);
            try {
                if (expected != null) report.bool("sentinel_integrity",
                        Arrays.equals(expected, digest(sentinel)), "Manager positive control before and after probes");
                byte[] scratchBytes = new byte[4096];
                try (FileInputStream in = new FileInputStream(scratchFile)) {
                    int n = in.read(scratchBytes);
                    boolean valid = scratchFile.length() == 4096 && n == 4096 && scratchBytes[0] == 'X';
                    for (int i = 1; i < n; i++) valid &= scratchBytes[i] == 0;
                    if (returned) report.bool("scratch_manager_verification", valid, "Only delegated synthetic scratch changed");
                }
            } catch (Exception e) {
                report.add("integrity_verification", "completed", "unavailable", 0, "UNKNOWN", "Do not infer intact state");
            }
            if (control != 0 && (returned || dead.getCount() == 0 || !initialized)) {
                report.bool("synthetic_memory_integrity", NativeProbe.releaseControl(control),
                        "Synthetic memory only. Allowed write control uses same byte");
            } else if (control != 0) {
                // Keep allocation alive until process exit if worker lifetime is uncertain.
                report.add("memory_control_lifetime", "released_after_worker", "retained", 0, "UNKNOWN",
                        "Uncertain death. Do not reuse address while worker may retain it");
            }
            try { if (protectedFile != null) protectedFile.close(); } catch (IOException ignored) {}
            try { if (canary != null) canary.close(); } catch (IOException ignored) {}
            try { if (scratch != null) scratch.close(); } catch (IOException ignored) {}
            if (pixels != null) SharedMemory.unmap(pixels);
            if (frame != null) frame.close();
            // A fresh session is blocked if an old worker might still hold capabilities.
            previousEpoch = epoch;
            if ((worker == null || dead.getCount() == 0)
                    && !launchState.getBoolean("uncertain_child", false)) ACTIVE.set(false);
        }
        try { return report.json(); }
        catch (IllegalArgumentException e) {
            Report bounded = new Report(epoch, Build.VERSION.SDK_INT);
            bounded.add("result_budget", "bounded_report", "rejected", 0, "UNKNOWN",
                    "Result exceeded export budget. No completed experiment conclusion");
            return bounded.json();
        }
    }
}
