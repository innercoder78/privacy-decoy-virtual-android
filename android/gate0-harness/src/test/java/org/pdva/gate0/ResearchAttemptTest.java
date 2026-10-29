package org.pdva.gate0;

import java.io.IOException;
import java.nio.file.*;
import java.util.Arrays;
import java.util.Comparator;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

/** Actual guard and real temporary files; directory-sync callbacks are injected, not Android. */
public final class ResearchAttemptTest {
    private static int checks;
    private static void check(boolean ok) {
        checks++;
        if (!ok) throw new AssertionError("reservation check " + checks);
    }
    private static final ResearchAttempt.DirectorySync SYNC = path -> { };
    private static final class Fixture implements AutoCloseable {
        final Path data = Files.createTempDirectory("pdva-attempt-test-");
        final Path files = Files.createDirectory(data.resolve("files"));
        Fixture() throws IOException { }
        Path marker() { return files.resolve(ResearchAttempt.MARKER); }
        @Override public void close() throws IOException {
            // Only this fixture's unique temporary tree, never application/repository state.
            try (var paths = Files.walk(data)) {
                for (Path path : paths.sorted(Comparator.reverseOrder()).toList()) Files.delete(path);
            }
        }
    }
    public static void run() throws Exception {
        try (Fixture f = new Fixture()) {
            ResearchAttempt guard = new ResearchAttempt();
            AtomicInteger syncs = new AtomicInteger();
            check(guard.reserve(f.data, f.files, path -> {
                check(Files.readString(f.marker()).equals("RESERVED\n"));
                check(path.equals(syncs.getAndIncrement() == 0 ? f.files : f.data));
            }));
            check(syncs.get() == 2);
            byte[] reserved = Files.readAllBytes(f.marker());
            check(!guard.reserve(f.data, f.files, SYNC));
            // New manager object under INTACT state: honest completion cannot change admission.
            check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
            check(Arrays.equals(reserved, Files.readAllBytes(f.marker())));
        }
        String[] legacy = {"<map><boolean name=\"uncertain_child\" value=\"false\" /></map>",
                "<map><boolean name=\"uncertain_child\" value=\"true\" /></map>",
                "<map><string name=\"uncertain_child\">false</string></map>",
                "<map><int name=\"uncertain_child\" value=\"0\" /></map>",
                "<map />", "", "corrupt", "<map"};
        for (String value : legacy) {
            try (Fixture f = new Fixture()) {
                Path prefs = Files.createDirectory(f.data.resolve("shared_prefs"));
                Path old = Files.writeString(prefs.resolve("launch_lifetime.xml"), value);
                check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
                check(Files.readString(old).equals(value));
                check(!Files.exists(f.marker()));
            }
        }
        for (String residue : new String[]{"empty-preferences-directory", "backup-only", "wrong-directory-type"}) {
            try (Fixture f = new Fixture()) {
                Path prefs = f.data.resolve("shared_prefs");
                if (residue.equals("wrong-directory-type")) Files.writeString(prefs, "wrong type");
                else {
                    Files.createDirectory(prefs);
                    if (residue.equals("backup-only")) Files.writeString(prefs.resolve("launch_lifetime.xml.bak"), "false");
                }
                check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
                check(!Files.exists(f.marker()));
            }
        }
        for (String value : new String[]{"", "false", "RESERVED\n", "corrupt"}) {
            try (Fixture f = new Fixture()) {
                Files.writeString(f.marker(), value);
                check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
                check(Files.readString(f.marker()).equals(value));
            }
        }
        try (Fixture f = new Fixture()) {
            Files.createDirectory(f.marker()); // Marker of the wrong filesystem type.
            check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
        }
        try (Fixture f = new Fixture()) {
            Files.writeString(f.files.resolve("gate0-sentinel"), "prior INIT evidence");
            check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
            check(!Files.exists(f.marker()));
        }
        // Missing/non-directory roots and exceptions are denial, never empty-state defaults.
        try (Fixture f = new Fixture()) {
            ResearchAttempt guard = new ResearchAttempt();
            check(!guard.reserve(f.data.resolve("missing"), f.files, SYNC));
            check(!guard.reserve(f.data, f.files, SYNC));
            Path wrong = Files.writeString(f.data.resolve("not-a-directory"), "x");
            check(!new ResearchAttempt().reserve(f.data, wrong, SYNC));
            check(!new ResearchAttempt().reserve(f.data, f.data.resolve("missing"), SYNC));
            check(!Files.exists(f.marker()));
        }
        // Both commit-boundary failures retain the marker; neither can reach a caller's bind.
        for (int failureAt : new int[]{1, 2}) {
            try (Fixture f = new Fixture()) {
                AtomicInteger syncs = new AtomicInteger(), binds = new AtomicInteger();
                ResearchAttempt guard = new ResearchAttempt();
                if (guard.reserve(f.data, f.files, path -> {
                    if (syncs.incrementAndGet() == failureAt) throw new IOException("injected_sync_failure");
                })) binds.incrementAndGet();
                check(binds.get() == 0);
                check(Files.exists(f.marker()));
                check(!guard.reserve(f.data, f.files, SYNC));
                check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
            }
        }
        try (Fixture f = new Fixture()) {
            ResearchAttempt guard = new ResearchAttempt();
            check(!guard.reserve(f.data, f.files, path -> { throw new SecurityException("injected"); }));
            check(Files.exists(f.marker()));
            check(!guard.reserve(f.data, f.files, SYNC));
        }
        try (Fixture f = new Fixture()) {
            ResearchAttempt guard = new ResearchAttempt();
            CountDownLatch start = new CountDownLatch(1);
            AtomicInteger winners = new AtomicInteger();
            Thread[] callers = new Thread[8];
            for (int i = 0; i < callers.length; i++) {
                callers[i] = new Thread(() -> {
                    try {
                        start.await();
                        if (guard.reserve(f.data, f.files, SYNC)) winners.incrementAndGet();
                    } catch (InterruptedException failure) { throw new AssertionError(failure); }
                });
                callers[i].start();
            }
            start.countDown();
            for (Thread caller : callers) caller.join();
            check(winners.get() == 1);
            check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
        }
        System.out.println("Research-attempt checks passed: " + checks + " (no Android durability claim)");
    }
}
