package org.pdva.gate0;

import android.app.Activity;
import android.content.*;
import android.os.Bundle;
import android.widget.*;
import java.util.concurrent.*;

public final class MainActivity extends Activity {
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private volatile Session active;
    private TextView output;
    private volatile boolean abortCycles;
    private String report = "";
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this); layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(24, 64, 24, 32);
        TextView title = new TextView(this);
        title.setText("Gate 0 isolated-worker substrate harness\nResearch only. Gate 0 Unresolved. No QEMU or guest.");
        layout.addView(title);
        button(layout, "Run fresh epoch", () -> run(1, false));
        button(layout, "Run five start/stop cycles", () -> run(5, false));
        button(layout, "Worker death / rebind exercise", () -> run(2, true));
        button(layout, "Stop", () -> { abortCycles = true; if (active != null) active.cancel(); });
        button(layout, "Copy sanitized JSON", () -> {
            if (!report.isEmpty()) {
                android.content.ClipboardManager clipboard =
                        (android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);
                clipboard.setPrimaryClip(ClipData.newPlainText("PDVA synthetic research report", report));
            }
        });
        output = new TextView(this); output.setTextIsSelectable(true);
        output.setText(R.string.initial_status);
        ScrollView scroll = new ScrollView(this); scroll.addView(output);
        layout.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(layout);
    }
    private void button(LinearLayout layout, String text, Runnable action) {
        Button button = new Button(this); button.setText(text);
        button.setOnClickListener(v -> action.run()); layout.addView(button);
    }
    private void run(int count, boolean death) {
        if (active != null) return;
        abortCycles = false;
        report = "";
        active = new Session(this);
        output.setText(R.string.running_status);
        executor.execute(() -> {
            StringBuilder all = new StringBuilder("[");
            try {
                for (int i = 0; i < count; i++) {
                    if (i != 0) { all.append(','); active = new Session(this); }
                    all.append(active.run(death && i == 0));
                    if (abortCycles || isFinishing() || isDestroyed()) break;
                }
                all.append(']'); report = all.toString();
                runOnUiThread(() -> output.setText(report));
            } finally { active = null; }
        });
    }
    @Override protected void onStop() {
        abortCycles = true; if (active != null) active.cancel();
        super.onStop();
    }
    @Override protected void onDestroy() {
        executor.shutdown(); super.onDestroy();
    }
}
