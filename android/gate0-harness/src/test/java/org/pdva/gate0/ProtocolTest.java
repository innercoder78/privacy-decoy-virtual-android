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
        rejects(() -> p.launch(E));
        rejects(() -> p.check("0".repeat(32)));
        rejects(() -> p.run("0".repeat(32)));
        p.run(E); rejects(() -> p.run(E));
        rejects(() -> p.launch("0".repeat(32)));
        p.launch(E); rejects(() -> p.launch(E));
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
        rejects(() -> p.launch(E));
        rejects(() -> new LaunchResult(null));
        rejects(() -> new LaunchResult(new long[25]));
        long[] launch = new long[24];
        launch[13] = 1; launch[10] = launch[19] = launch[20] = launch[23] = -1;
        LaunchResult unsupported = new LaunchResult(launch);
        check(unsupported.cleanupKnown());
        Report unsupportedReport = new Report(E, 37);
        unsupported.append(unsupportedReport);
        check(unsupportedReport.json().contains("UNSUPPORTED"));
        launch[0] = launch[1] = launch[3] = 1;
        rejects(() -> new LaunchResult(launch)); // Claimed cleanup without wait.
        launch[13] = 0; launch[12] = 1;
        check(!new LaunchResult(launch).cleanupKnown());
        Report timeout = new Report(E, 37);
        new LaunchResult(launch).append(timeout);
        check(timeout.json().contains("incomplete"));
        launch[8] = launch[13] = 1; launch[6] = -1; launch[7] = 13;
        Report denied = new Report(E, 37);
        new LaunchResult(launch).append(denied);
        check(denied.json().contains("returned_errno"));
        check(denied.json().contains("\"errno\":13"));
        launch[6] = 1; launch[7] = 0; launch[14] = 1; launch[10] = 42;
        Report executed = new Report(E, 37);
        new LaunchResult(launch).append(executed);
        check(executed.json().contains("payload_reached_main"));
        check(executed.json().contains("\"gate0\":\"Unresolved\""));
        check(executed.json().contains("\"physicalEvidence\":\"UNKNOWN\""));
        launch[7] = 4096; rejects(() -> new LaunchResult(launch));
        launch[7] = 0; launch[18] = 3; rejects(() -> new LaunchResult(launch));
        launch[18] = 0; launch[14] = 0; rejects(() -> new LaunchResult(launch));
        Protocol concurrent = new Protocol(); concurrent.initialize(E); concurrent.run(E);
        java.util.concurrent.atomic.AtomicInteger winners = new java.util.concurrent.atomic.AtomicInteger();
        Thread[] threads = new Thread[8];
        for (int i = 0; i < threads.length; i++) {
            threads[i] = new Thread(() -> {
                try { concurrent.launch(E); winners.incrementAndGet(); }
                catch (IllegalArgumentException expected) { }
            });
            threads[i].start();
        }
        for (Thread thread : threads) {
            try { thread.join(); } catch (InterruptedException error) { throw new AssertionError(error); }
        }
        check(winners.get() == 1);
        System.out.println("Protocol/report checks passed: " + checks);
    }
}
