package org.pdva.gate0;

import java.io.IOException;
import java.nio.file.*;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Map;
import java.util.TreeMap;
import java.util.HexFormat;
import java.util.ArrayDeque;
import java.nio.file.attribute.BasicFileAttributes;
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
    // Never follow links while recording evidence or cleaning fixtures. Targets are
    // separately owned disposable fixtures, never application/private directories.
    private static Map<String, String> snapshot(Path root) throws IOException {
        Map<String, String> result = new TreeMap<>();
        ArrayDeque<Path> pending = new ArrayDeque<>();
        pending.add(root);
        while (!pending.isEmpty()) {
            Path path = pending.remove();
            BasicFileAttributes a = Files.readAttributes(path, BasicFileAttributes.class,
                    LinkOption.NOFOLLOW_LINKS);
            String value = a.isSymbolicLink() ? "link:" + Files.readSymbolicLink(path) :
                    a.isOther() ? "other" : a.isDirectory() ? "directory" :
                    a.isRegularFile() ? "file:" + HexFormat.of().formatHex(Files.readAllBytes(path)) : "unknown";
            result.put(root.relativize(path).toString(), value);
            if (a.isDirectory() && !a.isSymbolicLink() && !a.isOther()) {
                try (DirectoryStream<Path> entries = Files.newDirectoryStream(path)) {
                    for (Path entry : entries) pending.add(entry);
                }
            }
        }
        return result;
    }
    private static void symlinks() throws Exception {
        int cases = 0;
        for (String name : new String[]{"files", "cache", "code_cache"}) {
            for (String kind : new String[]{"empty-directory", "residual-directory", "file", "dangling", "internal-alias"}) {
                try (Fixture f = new Fixture(); Fixture outside = new Fixture()) {
                    Path link = f.data.resolve(name);
                    if (name.equals("files")) Files.delete(f.files); // Empty, fixture-owned directory only.
                    Path target = outside.files;
                    if (kind.equals("residual-directory")) Files.writeString(target.resolve("evidence"), "prior attempt");
                    if (kind.equals("file")) target = Files.writeString(outside.data.resolve("evidence"), "prior attempt");
                    if (kind.equals("dangling")) target = outside.data.resolve("missing");
                    if (kind.equals("internal-alias")) {
                        target = name.equals("files") ? Files.createDirectory(f.data.resolve("cache")) : f.files;
                    }
                    // Creation failure is a failing/unsupported run, never a skipped pass.
                    Files.createSymbolicLink(link, target);
                    check(Files.isSymbolicLink(link));
                    Map<String, String> external = snapshot(outside.data);
                    ResearchAttempt guard = rejectedAlias(f.data, f.files, outside.data);
                    Files.delete(link); // Delete link itself, never its target.
                    if (name.equals("files")) Files.createDirectory(f.files);
                    check(!guard.reserve(f.data, f.files, p -> { throw new AssertionError("sync after denial"); }));
                    check(!Files.exists(f.marker(), LinkOption.NOFOLLOW_LINKS));
                    check(external.equals(snapshot(outside.data)));
                    cases++;
                }
            }
        }
        System.out.println("Real symlink cases passed: " + cases + " (no concurrent-mutation claim)");
    }
    // Shared oracle for real symlinks and externally constructed disposable junctions.
    // Call only with test-owned fixtures; this helper does not delete or repair them.
    static ResearchAttempt rejectedAlias(Path data, Path files, Path outside) throws IOException {
        Map<String, String> original = snapshot(data), external = snapshot(outside);
        ResearchAttempt guard = new ResearchAttempt();
        AtomicInteger syncs = new AtomicInteger(), delegations = new AtomicInteger();
        boolean admitted = guard.reserve(data, files, p -> syncs.incrementAndGet());
        if (admitted) delegations.incrementAndGet();
        if (admitted) throw new AssertionError("filesystem alias admitted");
        check(delegations.get() == 0);
        check(syncs.get() == 0);
        check(!Files.exists(files.resolve(ResearchAttempt.MARKER), LinkOption.NOFOLLOW_LINKS));
        check(original.equals(snapshot(data)));
        check(external.equals(snapshot(outside)));
        check(!new ResearchAttempt().reserve(data, files, p -> syncs.incrementAndGet()));
        check(syncs.get() == 0);
        check(original.equals(snapshot(data)));
        check(external.equals(snapshot(outside)));
        return guard;
    }
    public static void run() throws Exception {
        // Source-supported empty installd directories are not prior-attempt evidence.
        for (String[] names : new String[][]{{"cache"}, {"code_cache"}, {"cache", "code_cache"}}) {
            try (Fixture f = new Fixture()) {
                for (String name : names) Files.createDirectory(f.data.resolve(name));
                check(new ResearchAttempt().reserve(f.data, f.files, SYNC));
                check(Files.readString(f.marker()).equals("RESERVED\n"));
                for (String name : names) {
                    try (var entries = Files.newDirectoryStream(f.data.resolve(name))) {
                        check(!entries.iterator().hasNext());
                    }
                }
                check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
            }
        }
        // Names and empty directories do not authenticate history. Unsupported state
        // is conservatively denied, even when it might have a benign explanation.
        for (String name : new String[]{"unexpected", "databases", "no_backup", "cache", "code_cache"}) {
            for (String kind : new String[]{"empty", "residue", "nested", "wrong-type"}) {
                if (kind.equals("empty") && (name.equals("cache") || name.equals("code_cache"))) continue;
                try (Fixture f = new Fixture()) {
                    Path entry = f.data.resolve(name), evidence = entry;
                    if (kind.equals("wrong-type")) Files.writeString(entry, "prior attempt");
                    else {
                        Files.createDirectory(entry);
                        if (kind.equals("residue")) evidence = Files.writeString(entry.resolve("prior-attempt"), "prior attempt");
                        if (kind.equals("nested")) evidence = Files.createDirectory(entry.resolve("nested"));
                    }
                    ResearchAttempt guard = new ResearchAttempt();
                    AtomicInteger syncs = new AtomicInteger(), delegations = new AtomicInteger();
                    if (guard.reserve(f.data, f.files, p -> syncs.incrementAndGet())) delegations.incrementAndGet();
                    check(delegations.get() == 0);
                    check(syncs.get() == 0);
                    check(!Files.exists(f.marker()));
                    check(Files.exists(evidence));
                    if (kind.equals("residue") || kind.equals("wrong-type"))
                        check(Files.readString(evidence).equals("prior attempt"));
                    check(!new ResearchAttempt().reserve(f.data, f.files, SYNC));
                    // Fixture-only removal tests the permanent process latch, not recovery.
                    if (!evidence.equals(entry)) Files.delete(evidence);
                    Files.delete(entry);
                    check(!guard.reserve(f.data, f.files, SYNC));
                    check(!Files.exists(f.marker()));
                }
            }
        }
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
        symlinks();
    }
}
