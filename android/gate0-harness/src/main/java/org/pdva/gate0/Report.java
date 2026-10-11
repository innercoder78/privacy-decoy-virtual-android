package org.pdva.gate0;

import java.util.ArrayList;
import java.util.List;

/** Export fields accept labels/numbers only; never exception messages or raw paths. */
public final class Report {
    private final String epoch;
    private final int api;
    private final List<String> rows = new ArrayList<>();
    public Report(String epoch, int api) {
        if (!Protocol.validEpoch(epoch)) throw new IllegalArgumentException("epoch");
        this.epoch = epoch;
        this.api = api;
    }
    public static String label(String text) {
        if (text == null || text.length() > 256 || !text.matches("[A-Za-z0-9_ .:+,=-]*"))
            return "REDACTED";
        return text;
    }
    private static String q(String s) { return "\"" + label(s) + "\""; }
    public void add(String name, String expected, String observed, long error,
                    String status, String limit) {
        if (!status.matches("PASS|FAIL|UNKNOWN|UNSUPPORTED") || rows.size() >= 160)
            throw new IllegalArgumentException("report");
        rows.add("{\"probe\":" + q(name) + ",\"expected\":" + q(expected)
                + ",\"observed\":" + q(observed) + ",\"errno\":" + error
                + ",\"status\":" + q(status) + ",\"limitations\":" + q(limit) + "}");
    }
    public void bool(String name, boolean ok, String limit) {
        add(name, "true", Boolean.toString(ok), 0, ok ? "PASS" : "FAIL", limit);
    }
    public String json() {
        String s = "{\"schema\":1,\"epoch\":\"" + epoch
                + "\",\"appVersion\":\"0.1-substrate\",\"hostApi\":" + api
                + ",\"gate0\":\"Unresolved\",\"physicalEvidence\":\"UNKNOWN\",\"probes\":["
                + String.join(",", rows) + "]}";
        if (s.length() > Protocol.MAX_REPORT) throw new IllegalArgumentException("report_size");
        return s;
    }
}
