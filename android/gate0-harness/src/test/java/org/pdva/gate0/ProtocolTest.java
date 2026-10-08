package org.pdva.gate0;

public final class ProtocolTest {
    private static int checks;
    private static final String E = "1".repeat(32);
    private static void check(boolean ok) { checks++; if (!ok) throw new AssertionError("check " + checks); }
    private static void rejects(Runnable action) {
        boolean rejected = false;
        try { action.run(); } catch (IllegalArgumentException e) { rejected = true; }
        check(rejected);
    }
    public static void main(String[] ignored) {
        Protocol p = new Protocol();
        rejects(() -> p.check(E)); rejects(() -> p.initialize("../bad"));
        p.initialize(E); rejects(() -> p.initialize(E));
        rejects(() -> p.check("0".repeat(32)));
        rejects(() -> p.run("0".repeat(32)));
        p.run(E); rejects(() -> p.run(E));
        rejects(() -> Protocol.size(Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE, 1));
        rejects(() -> Protocol.size(64, 64, 256, -1));
        rejects(() -> Protocol.size(64, 64, 255, 16384));
        check(Protocol.size(64,64,256,16384) == 16384);
        rejects(() -> p.frame(E, 65, 64, 256, 16384));
        check(p.frame(E,64,64,256,16384) == 1);
        check(p.frame(E,64,64,256,16384) == 2);
        rejects(() -> p.frame(E,64,64,256,16384));
        rejects(() -> p.input(E, 0, 256)); rejects(() -> p.input(E, 1, 1));
        for (int i = 0; i < 16; i++) check(p.input(E, i, 42) == (42 ^ 0x5a));
        rejects(() -> p.input(E,16,42)); rejects(() -> p.input(E,0,42));
        p.stop(E); rejects(() -> p.initialize(E)); rejects(() -> p.check(E)); rejects(() -> p.input(E,0,42));
        Report r = new Report(E,37);
        r.add("path", "sanitized", "/data/user/0/private/secret", 13, "UNKNOWN", "not inspected");
        r.add("error", "sanitized", "quote\" newline\n backslash\\", 0, "UNKNOWN", "raw errors excluded");
        String json = r.json();
        check(json.equals(r.json())); check(!json.contains("/data")); check(!json.contains("secret"));
        check(!json.contains("backslash")); check(json.contains("REDACTED"));
        check(json.contains("\"errno\":13")); check(json.contains("\"schema\":1"));
        check(json.contains("\"epoch\":\"" + E + "\""));
        rejects(() -> r.add("a","b","c",0,"SAFE","d"));
        check(Report.label("a".repeat(257)).equals("REDACTED"));
        check(Report.label("device@example.test").equals("REDACTED"));
        System.out.println("Protocol/report checks passed: " + checks);
    }
}
