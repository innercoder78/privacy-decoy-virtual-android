package org.pdva.gate0;

import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.*;
import android.system.Os;
import android.system.OsConstants;
import java.io.File;
import java.nio.ByteBuffer;

public final class WorkerService extends Service {
    private final Protocol protocol = new Protocol();
    private final Handler timer = new Handler(Looper.getMainLooper());
    private ParcelFileDescriptor canary, scratch;
    private SharedMemory frame;
    private ByteBuffer pixels;
    private IBinder owner;
    private int managerPid, sentinelNumber;
    private long controlAddress;
    private boolean initialized, stopping;
    // Private entry point, never called by the management process or exposed through IPC.
    private static native long[] launchNative(String installedNativeDirectory);
    private final IBinder.DeathRecipient ownerDeath = this::terminate;
    private void terminate() { android.os.Process.killProcess(android.os.Process.myPid()); }

    @Override public void onCreate() {
        super.onCreate();
        // Absolute lease, independent of requests. No service restart or keepalive.
        timer.postDelayed(this::terminate, 30000);
    }
    @Override public IBinder onBind(Intent ignored) { return endpoint; }
    @Override public boolean onUnbind(Intent ignored) { terminate(); return false; }
    @Override public void onDestroy() { closeResources(); super.onDestroy(); }
    private void closeResources() {
        try { if (canary != null) canary.close(); } catch (Exception ignored) { }
        try { if (scratch != null) scratch.close(); } catch (Exception ignored) { }
        if (pixels != null) { SharedMemory.unmap(pixels); pixels = null; }
        if (frame != null) { frame.close(); frame = null; }
        if (owner != null) { owner.unlinkToDeath(ownerDeath, 0); owner = null; }
    }
    private static void file(ParcelFileDescriptor fd, int mode) throws Exception {
        if (fd == null || !OsConstants.S_ISREG(Os.fstat(fd.getFileDescriptor()).st_mode)
                || Os.fstat(fd.getFileDescriptor()).st_size != 4096
                || (Os.fcntlInt(fd.getFileDescriptor(), OsConstants.F_GETFL, 0)
                    & OsConstants.O_ACCMODE) != mode) throw new IllegalArgumentException("fd");
    }
    private final Binder endpoint = new Binder() {
        @Override protected synchronized boolean onTransact(int code, Parcel data, Parcel reply,
                                                           int flags) throws RemoteException {
            if (Binder.getCallingUid() != getApplicationInfo().uid || stopping)
                throw new SecurityException("caller");
            if (reply == null || flags != 0 || data.dataSize() > Protocol.MAX_CONTROL)
                throw new IllegalArgumentException("control_size");
            if (code < Protocol.INIT || code > Protocol.LAUNCH)
                throw new IllegalArgumentException("operation");
            data.enforceInterface(Protocol.DESCRIPTOR);
            String epoch = data.readString();
            try {
                if (code == Protocol.INIT) {
                    if (initialized) throw new IllegalArgumentException("initialized");
                    // Set before parsing: a partially failed initialization cannot be retried.
                    initialized = true;
                    protocol.initialize(epoch);
                    managerPid = Binder.getCallingPid();
                    controlAddress = data.readLong();
                    sentinelNumber = data.readInt();
                    if (sentinelNumber < 0) throw new IllegalArgumentException("sentinel_number");
                    if (controlAddress == 0) throw new IllegalArgumentException("memory_control");
                    owner = data.readStrongBinder();
                    canary = data.readTypedObject(ParcelFileDescriptor.CREATOR);
                    scratch = data.readTypedObject(ParcelFileDescriptor.CREATOR);
                    frame = data.readTypedObject(SharedMemory.CREATOR);
                    if (data.dataAvail() != 0 || owner == null || frame == null
                            || frame.getSize() != Protocol.BYTES)
                        throw new IllegalArgumentException("init");
                    file(canary, OsConstants.O_RDONLY); file(scratch, OsConstants.O_RDWR);
                    pixels = frame.mapReadWrite();
                    owner.linkToDeath(ownerDeath, 0);
                    reply.writeNoException();
                    reply.writeInt(android.os.Process.myPid());
                    reply.writeInt(android.os.Process.myUid());
                    return true;
                }
                protocol.check(epoch);
                if (code == Protocol.FRAME) {
                    int w = data.readInt(), h = data.readInt(), stride = data.readInt();
                    int length = data.readInt();
                    if (data.dataAvail() != 0) throw new IllegalArgumentException("trailing");
                    int sequence = protocol.frame(epoch, w, h, stride, length);
                    for (int i = 0; i < Protocol.BYTES; i++) pixels.put(i, (byte)(i + sequence));
                    reply.writeNoException(); reply.writeInt(sequence);
                } else if (code == Protocol.INPUT) {
                    int sequence = data.readInt(), token = data.readInt();
                    if (data.dataAvail() != 0) throw new IllegalArgumentException("trailing");
                    int ack = protocol.input(epoch, sequence, token);
                    reply.writeNoException(); reply.writeInt(ack);
                } else {
                    if (data.dataAvail() != 0) throw new IllegalArgumentException("trailing");
                    if (code == Protocol.RUN) {
                        protocol.run(epoch);
                        String result = runProbes(epoch);
                        reply.writeNoException(); reply.writeString(result);
                    } else if (code == Protocol.LAUNCH) {
                        protocol.launch(epoch);
                        if (!android.os.Process.isIsolated()) throw new SecurityException("isolation");
                        // Framework-owned installation location; no caller-supplied path.
                        long[] result = launchNative(getApplicationInfo().nativeLibraryDir);
                        LaunchResult checked = new LaunchResult(result);
                        if (!checked.cleanupKnown()) stopping = true;
                        reply.writeNoException(); reply.writeLongArray(result);
                        if (stopping) timer.postDelayed(WorkerService.this::terminate, 100);
                    } else if (code == Protocol.KILL) {
                        protocol.stop(epoch); stopping = true;
                        reply.writeNoException();
                        // Death injection: leave capabilities open for kernel teardown.
                        timer.postDelayed(WorkerService.this::terminate, 100);
                    } else {
                        protocol.stop(epoch); stopping = true;
                        closeResources();
                        reply.writeNoException();
                        // Let the synchronous response leave before self-termination.
                        timer.postDelayed(WorkerService.this::terminate, 100);
                    }
                }
                return true;
            } catch (Exception e) {
                if (code == Protocol.INIT) {
                    closeResources(); stopping = true; timer.postDelayed(WorkerService.this::terminate, 100);
                }
                // Never transmit platform exception messages containing private paths.
                throw new IllegalArgumentException("rejected");
            }
        }
    };

    private String runProbes(String epoch) {
        Report report = new Report(epoch, Build.VERSION.SDK_INT);
        report.bool("framework_isolated", android.os.Process.isIsolated(),
                "Framework predicate and distinct UID are scoped observations");
        report.add("host_abi", "inventory", Build.SUPPORTED_ABIS[0], 0, "UNKNOWN",
                "Installed native ABI reported separately by fixture availability");
        report.add("android_release", "inventory", Build.VERSION.RELEASE, 0, "UNKNOWN", "Public OS version only");
        report.add("security_patch", "inventory", Build.VERSION.SECURITY_PATCH, 0, "UNKNOWN", "Public patch level only");
        String sentinel = new File(getApplicationInfo().dataDir, "files/gate0-sentinel").getPath();
        try {
            long[] raw = NativeProbe.run(sentinel, managerPid, controlAddress,
                    sentinelNumber, canary.getFd(), scratch.getFd());
            report.bool("native_load_and_run", true, "Packaged JNI execution only");
            for (int i = 0; i < raw.length; i += 3) observation(report, (int)raw[i], raw[i+1], raw[i+2]);
            report.add("selinux_context", "inventory", NativeProbe.context(), 0, "UNKNOWN",
                    "Context readability does not establish enforcement");
        } catch (LinkageError e) {
            report.add("native_load", "load_and_run", "linkage_failure", 0, "FAIL",
                    "Required native substrate could not load");
        }
        String[] permissions = { "INTERNET", "ACCESS_NETWORK_STATE", "CAMERA", "RECORD_AUDIO",
                "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION", "READ_EXTERNAL_STORAGE",
                "WRITE_EXTERNAL_STORAGE", "MANAGE_EXTERNAL_STORAGE" };
        for (String permission : permissions) {
            boolean denied = checkSelfPermission("android.permission." + permission)
                    == PackageManager.PERMISSION_DENIED;
            report.bool("permission_absent_" + permission, denied,
                    "Permission check only. Does not exhaust direct or deputy service routes");
        }
        String[] services = { CAMERA_SERVICE, AUDIO_SERVICE, LOCATION_SERVICE, STORAGE_SERVICE };
        for (String service : services) {
            String observed;
            try { observed = getSystemService(service) == null ? "unavailable" : "visible_wrapper"; }
            catch (RuntimeException e) { observed = "access_rejected"; }
            report.add("service_" + service, "inventory", observed, 0, "UNKNOWN",
                    "No capture or location query. Binder handles and deputies not exhaustively inventoried");
        }
        return report.json();
    }

    private static void observation(Report r, int id, long value, long error) {
        String name;
        switch (id) {
            case 1: name="pid"; break; case 2: name="uid"; break;
            case 3: name="euid"; break; case 4: name="gid"; break;
            case 5: name="page_size"; break; case 6: name="group_count"; break;
            case 7: name="self_fd_count"; break; case 8: name="self_mapping_count"; break;
            case 9: name="self_executable_mapping_count"; break;
            case 10: name="generated_mmap_rw"; break;
            case 11: name="generated_mprotect_rx"; break;
            case 12: name="generated_return"; break;
            case 13: name="memfd_create"; break;
            case 14: name="egid"; break;
            case 15: name="native_abi"; break;
            case 20: name="sentinel_open_read"; break;
            case 21: name="sentinel_syscall_openat"; break;
            case 22: name="sentinel_open_write"; break;
            case 23: name="management_proc_mem"; break;
            case 24: name="management_proc_fd_directory"; break;
            case 25: name="management_proc_status"; break;
            case 26: name="sentinel_management_proc_fd"; break;
            case 30: name="management_process_vm_readv"; break;
            case 31: name="management_process_vm_writev"; break;
            case 32: name="self_process_vm_readv"; break;
            case 33: name="self_process_vm_writev"; break;
            case 34: name="management_ptrace_peek"; break;
            case 35: name="management_signal_zero"; break;
            case 40: name="socket_tcp4"; break; case 41: name="socket_tcp6"; break;
            case 42: name="socket_udp4"; break; case 43: name="socket_udp6"; break;
            case 60: name="delegated_canary_read"; break;
            case 61: name="readonly_fd_write"; break;
            case 62: name="scratch_write"; break;
            case 63: name="duplicate_survives_close"; break;
            case 64: name="self_fd_reopen_read"; break;
            case 65: name="self_fd_reopen_write"; break;
            case 70: name="external_storage_directory"; break;
            case 71: name="device_kvm"; break;
            case 72: name="device_gpu_kgsl"; break;
            case 73: name="device_gpu_dri"; break;
            case 74: name="device_video"; break;
            case 75: name="device_sound"; break;
            default: name = id >= 1000 ? "group_" + (id-1000) :
                    id >= 70 ? "fixed_surface_" + (id-70) : "loopback_connect_" + (id-50);
        }
        String status = "UNKNOWN", expected = "inventory";
        String limit = "Scoped syscall observation. No universal isolation claim";
        if (id == 10 || id == 11 || id == 12 || id == 32 || id == 33
                || id == 60 || id == 62 || id == 63) {
            long wanted = id == 12 ? 42 : id == 60 || id == 63 ? 67 : id >= 32 ? 1 : 0;
            expected = Long.toString(wanted);
            status = value == wanted ? "PASS" : "FAIL";
            if (id >= 10 && id <= 12) limit = "Fixed generated code only. Does not prove QEMU TCG";
            if (id == 12 && error == OsConstants.ENOTSUP) {
                status = "UNKNOWN"; limit = "Unsupported generated fixture on non ARM64 ABI";
            }
        }
        if ((id >= 20 && id <= 24) || id == 26 || id == 30 || id == 31 ||
                (id >= 40 && id <= 43) || id == 65 || (id >= 70 && id <= 75)) {
            expected = "denied";
            status = value >= 0 ? "FAIL" :
                    error == OsConstants.EACCES || error == OsConstants.EPERM ? "PASS" : "UNKNOWN";
            if (id == 24 || id >= 70) limit = "Open only. Missing node is Unknown. No contents enumerated";
        }
        if (id == 61) {
            expected = "EBADF";
            status = value == -1 && error == OsConstants.EBADF ? "PASS" : "FAIL";
        }
        if (id == 34) {
            expected = "no_memory_read";
            status = error == 0 ? "FAIL" : "UNKNOWN";
            limit = "Non-stopping PEEK only. No attach test. ESRCH does not establish isolation";
        }
        r.add(name, expected, id == 15 ? (value == 1 ? "arm64-v8a" : "x86_64") : Long.toString(value), error, status, limit);
    }
}
