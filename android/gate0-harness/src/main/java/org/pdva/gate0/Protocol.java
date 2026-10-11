package org.pdva.gate0;

/** Fixed one-shot protocol. No command, path-open, forwarding or broker operation. */
public final class Protocol {
    public static final String DESCRIPTOR = "org.pdva.gate0.substrate.v1";
    public static final int INIT = 1, RUN = 2, FRAME = 3, INPUT = 4, STOP = 5, KILL = 6;
    public static final int LAUNCH = 7;
    public static final int MAX_CONTROL = 4096, MAX_REPORT = 32768;
    public static final int WIDTH = 64, HEIGHT = 64, STRIDE = WIDTH * 4;
    public static final int BYTES = HEIGHT * STRIDE, MAX_INPUT = 16;
    private String epoch;
    private boolean ran, initialized, launched;
    private int frames, inputs;
    public synchronized void initialize(String value) {
        if (initialized || !validEpoch(value)) throw new IllegalArgumentException("epoch");
        epoch = value;
        initialized = true;
    }
    public static boolean validEpoch(String value) {
        return value != null && value.matches("[0-9a-f]{32}");
    }
    public synchronized void check(String value) {
        if (epoch == null || !epoch.equals(value)) throw new IllegalArgumentException("stale_epoch");
    }
    public synchronized void run(String value) {
        check(value);
        if (ran) throw new IllegalArgumentException("already_run");
        ran = true;
    }
    public synchronized void launch(String value) {
        check(value);
        if (!ran || launched) throw new IllegalArgumentException("launch_state");
        launched = true; // Consumed before native work, including failed launches.
    }
    public synchronized int frame(String value, int width, int height, int stride, int length) {
        check(value);
        size(width, height, stride, length);
        if (++frames > 2) throw new IllegalArgumentException("frame_quota");
        return frames;
    }
    public static int size(int width, int height, int stride, int length) {
        if (width != WIDTH || height != HEIGHT || stride != STRIDE || length != BYTES
                || (long) height * stride != length) throw new IllegalArgumentException("bounds");
        return length;
    }
    public synchronized int input(String value, int sequence, int token) {
        check(value);
        if (sequence != inputs || token < 0 || token > 255 || inputs >= MAX_INPUT)
            throw new IllegalArgumentException("input_bounds");
        inputs++;
        return token ^ 0x5a;
    }
    public synchronized void stop(String value) { check(value); epoch = null; }
}
