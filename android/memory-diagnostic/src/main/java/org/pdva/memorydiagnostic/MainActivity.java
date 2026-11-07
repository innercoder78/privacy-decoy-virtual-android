package org.pdva.memorydiagnostic;

import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Insets;
import android.os.Bundle;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Foreground, synchronous, single activation. No scheduling or automatic retry. */
public final class MainActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        SharedPreferences preferences = getSharedPreferences("attempt", MODE_PRIVATE);
        Attempt attempt = new Attempt(new Attempt.Store() {
            public boolean started() { return preferences.getBoolean("started", false); }
            public boolean markStarted() { return preferences.edit().putBoolean("started", true).commit(); }
        }, state != null);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(24, 64, 24, 64);
        ScrollView scroll = new ScrollView(this);
        scroll.setOnApplyWindowInsetsListener((view, insets) -> {
            Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
            view.setPadding(bars.left, bars.top, bars.right, bars.bottom);
            return insets;
        });
        TextView explanation = new TextView(this);
        explanation.setText("One memory-mapping admission test. No code is written or executed. "
            + "Press once only after approval. If interrupted or unresponsive, stop and report Unknown. "
            + "Reopening does not retry. Results are not saved or uploaded.");
        TextView result = new TextView(this);
        Button button = new Button(this);
        button.setText("Run one test");
        boolean ready = attempt.ready();
        button.setEnabled(ready);
        result.setText(ready ? new Experiment.Result(Experiment.Outcome.Ready).display()
            : Experiment.Result.unknown(Experiment.Op.Interrupted).display());
        button.setOnClickListener(view -> {
            button.setEnabled(false);
            result.setText(Experiment.Result.unknown(Experiment.Op.Interrupted).display());
            result.setText(attempt.activate(new AndroidOps()).display());
        });
        layout.addView(explanation);
        layout.addView(button);
        layout.addView(result);
        scroll.addView(layout);
        setContentView(scroll);
    }
}
