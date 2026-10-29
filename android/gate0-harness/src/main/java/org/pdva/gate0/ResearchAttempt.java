package org.pdva.gate0;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

/** One-way research guard, conditional on intact fresh app data; not recovery authority. */
final class ResearchAttempt {
    static final String MARKER = "research-attempt-reserved-v1";
    private boolean attempted;

    interface DirectorySync { void sync(Path directory) throws Exception; }

    // Session owns ONE process-wide instance. There is deliberately no reset API.
    synchronized boolean reserve(Path data, Path files, DirectorySync sync) {
        if (attempted) return false;
        attempted = true; // Even failed reads/writes cannot trigger an in-process retry.
        try {
            // Enumerate rather than treating exists()==false as proof of absence.
            // Any old preference directory is evidence, including false, malformed,
            // empty, backup-only, or unreadable uncertain_child data. Never load/repair it.
            try (DirectoryStream<Path> entries = Files.newDirectoryStream(data)) {
                for (Path entry : entries)
                    if (entry.getFileName().toString().equals("shared_prefs")) return false;
            }
            try (DirectoryStream<Path> entries = Files.newDirectoryStream(files)) {
                if (entries.iterator().hasNext()) return false;
            }
            // Absence is ONLY a conditional first-use predicate, not authenticated freshness.
            // CREATE_NEW also denies a concurrent creator without truncating its evidence.
            try (FileChannel out = FileChannel.open(files.resolve(MARKER),
                    StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
                ByteBuffer bytes = StandardCharsets.US_ASCII.encode("RESERVED\n");
                while (bytes.hasRemaining()) {
                    if (out.write(bytes) <= 0) throw new IOException("reservation_write");
                }
                out.force(true);
            }
            sync.sync(files);
            sync.sync(data); // Include the files directory entry if Android just created it.
            return true;
        } catch (Exception failure) {
            // Preserve partial files and earlier evidence; no delete, repair, migration or retry.
            return false;
        }
    }
}
