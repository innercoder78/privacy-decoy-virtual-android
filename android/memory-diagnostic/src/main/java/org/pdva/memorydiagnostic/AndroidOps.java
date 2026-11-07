package org.pdva.memorydiagnostic;

import android.os.Build;
import android.os.Process;
import android.system.ErrnoException;
import android.system.Os;
import android.system.OsConstants;
import java.io.FileDescriptor;

/** Public SDK only. Resource values remain private and are never formatted. */
final class AndroidOps implements Experiment.Ops {
    private FileDescriptor fd;
    private long rw, rx;
    private static Experiment.Fault fault(ErrnoException e) { return new Experiment.Fault(e.errno); }
    public int api() { return Build.VERSION.SDK_INT; }
    public boolean arm64() {
        for (String abi : Build.SUPPORTED_ABIS) if ("arm64-v8a".equals(abi)) return true;
        return false;
    }
    public boolean bit64() { return Process.is64Bit(); }
    public long pageSize() { return Os.sysconf(OsConstants._SC_PAGESIZE); }
    public void create() throws Experiment.Fault {
        try { fd = Os.memfd_create("pdva-diagnostic", OsConstants.MFD_CLOEXEC); }
        catch (ErrnoException e) { throw fault(e); }
    }
    public void resize(long size) throws Experiment.Fault {
        try { Os.ftruncate(fd, size); } catch (ErrnoException e) { throw fault(e); }
    }
    public void mapRW(long size) throws Experiment.Fault {
        try { rw = Os.mmap(0, size, OsConstants.PROT_READ | OsConstants.PROT_WRITE,
            OsConstants.MAP_SHARED, fd, 0); } catch (ErrnoException e) { throw fault(e); }
    }
    public void mapRX(long size) throws Experiment.Fault {
        try { rx = Os.mmap(0, size, OsConstants.PROT_READ | OsConstants.PROT_EXEC,
            OsConstants.MAP_SHARED, fd, 0); } catch (ErrnoException e) { throw fault(e); }
    }
    public void unmapRX(long size) throws Experiment.Fault {
        try { Os.munmap(rx, size); } catch (ErrnoException e) { throw fault(e); }
    }
    public void unmapRW(long size) throws Experiment.Fault {
        try { Os.munmap(rw, size); } catch (ErrnoException e) { throw fault(e); }
    }
    public void close() throws Experiment.Fault {
        try { Os.close(fd); } catch (ErrnoException e) { throw fault(e); }
    }
}
