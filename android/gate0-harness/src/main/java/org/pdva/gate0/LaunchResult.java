package org.pdva.gate0;

/** Typed, bounded launch observations. No aggregate Gate 0 verdict. */
final class LaunchResult {
    static final int COUNT = 24;
    private final long[] v;
    LaunchResult(long[] raw) {
        if (raw == null || raw.length != COUNT) throw new IllegalArgumentException("launch_shape");
        v = raw.clone();
        for (long value : v) if (value < -1 || value > 65536)
            throw new IllegalArgumentException("launch_bounds");
        for (int i : new int[]{0,1,12,13,15,16,17}) range(i, 0, 1);
        for (int i : new int[]{3,6,8,14}) range(i, -1, 1);
        for (int i : new int[]{2,4,5,7,9,22}) range(i, 0, 4095);
        range(10, -1, 255); range(11, 0, 64); range(18, 0, 2);
        range(19, -1, 2); range(20, -1, 1); range(21, 0, 2);
        if (v[3] != 1 && (v[8] != 0 || v[6] != 0 || v[14] != 0 || v[13] != 1))
            throw new IllegalArgumentException("launch_creation");
        if (v[3] == 1 && v[13] == 1 && v[8] != 1)
            throw new IllegalArgumentException("launch_cleanup");
        if ((v[0] == 0 || v[1] == 0 || v[2] != 0) && v[3] != 0)
            throw new IllegalArgumentException("launch_preflight");
        if (v[6] == 1 && v[5] != 0)
            throw new IllegalArgumentException("launch_setup");
        if (v[8] != 1 && (v[10] != -1 || v[11] != 0))
            throw new IllegalArgumentException("launch_termination");
        if (v[14] != 1 && (v[15] != 0 || v[16] != 0 || v[17] != 0
                || v[18] != 0 || v[19] != -1 || v[20] != -1 || v[23] != -1))
            throw new IllegalArgumentException("launch_identity");
        if ((v[6] == -1) != (v[7] != 0) || (v[3] == -1) != (v[4] != 0)
                || (v[8] == -1) != (v[9] != 0) || (v[6] == 1) != (v[14] == 1))
            throw new IllegalArgumentException("launch_consistency");
    }
    private void range(int index, int min, int max) {
        if (v[index] < min || v[index] > max) throw new IllegalArgumentException("launch_enum");
    }
    boolean cleanupKnown() { return v[13] == 1; }
    private void row(Report r, String name, String expected, String value, long error, String status) {
        r.add("launch_" + name, expected, value, error, status,
                "One synthetic executable observation. Physical acceptance remains Unknown");
    }
    void append(Report r) {
        row(r, "payload", "pdva_launch_v1", "pdva_launch_v1", 0, "UNKNOWN");
        row(r, "abi", "arm64-v8a", v[0] == 1 ? "arm64-v8a" : "unsupported",
                0, v[0] == 1 ? "UNKNOWN" : "UNSUPPORTED");
        row(r, "elf", "dynamic_pie", v[1] == 1 ? "verified_headers" : "not_verified",
                v[2], v[1] == 1 ? "PASS" : "UNKNOWN");
        row(r, "mechanism", "fork_execve", "fixed_installed_payload", 0, "UNKNOWN");
        row(r, "create", "created", v[3] == 1 ? "created" : v[3] == -1 ? "failed" : "not_attempted",
                v[4], v[3] == 1 ? "PASS" : v[3] == -1 ? "FAIL" : "UNKNOWN");
        row(r, "setup", "no_error", v[5] == 0 ? "no_error_reported" : "failed", v[5], "UNKNOWN");
        row(r, "execve", "payload_reached_main", v[6] == 1 ? "payload_reached_main" :
                v[6] == -1 ? "returned_errno" : "unknown_or_not_attempted", v[7],
                v[6] == 1 ? "PASS" : v[6] == -1 ? "FAIL" : "UNKNOWN");
        row(r, "wait", "reaped", v[8] == 1 ? "reaped" : "not_observed", v[9], v[8] == 1 ? "PASS" : "UNKNOWN");
        row(r, "exit", "42", Long.toString(v[10]), 0, v[10] == 42 && v[14] == 1 ? "PASS" : "UNKNOWN");
        row(r, "signal", "none", Long.toString(v[11]), 0, "UNKNOWN");
        row(r, "timeout", "false", Boolean.toString(v[12] == 1), 0, v[12] == 1 ? "FAIL" : "UNKNOWN");
        row(r, "cleanup", "known", cleanupKnown() ? "known" : "incomplete", v[22], cleanupKnown() ? "PASS" : "UNKNOWN");
        row(r, "output", "fixed_40_bytes_result_42", v[14] == 1 ? "valid" : v[14] == -1 ? "invalid" : "absent",
                0, v[14] == 1 ? "PASS" : "UNKNOWN");
        String[] names = {"distinct_pid", "same_worker_uid", "same_worker_euid"};
        for (int i = 0; i < names.length; i++) row(r, names[i], "true",
                v[14] == 1 ? Boolean.toString(v[15+i] == 1) : "not_observed", 0,
                v[14] != 1 ? "UNKNOWN" : v[15+i] == 1 ? "PASS" : "FAIL");
        row(r, "selinux", "isolated_app", v[18] == 1 ? "isolated_app" : v[18] == 2 ? "other" : "unobserved", 0, "UNKNOWN");
        row(r, "seccomp", "inventory", Long.toString(v[19]), 0, "UNKNOWN");
        row(r, "effective_capabilities", "zero", v[20] == 0 ? "zero" : v[20] == 1 ? "nonzero" : "unobserved", 0, "UNKNOWN");
        row(r, "extra_fds", "0", Long.toString(v[23]), 0, v[23] == 0 ? "PASS" : "UNKNOWN");
        row(r, "linker_diagnostic", "inventory", v[21] == 1 ? "cannot_link_executable" :
                v[21] == 2 ? "other_discarded" : "not_observed", 0, "UNKNOWN");
        row(r, "selinux_denial", "attributed_denial", "unobserved", 0, "UNKNOWN");
    }
}
