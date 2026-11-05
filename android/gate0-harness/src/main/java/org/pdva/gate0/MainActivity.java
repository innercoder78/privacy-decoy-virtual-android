package org.pdva.gate0;

import android.app.Activity;
import android.os.Bundle;
import android.widget.*;

/** Information only: this research build has no experimental launch actions. */
public final class MainActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this); layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(24, 64, 24, 32);
        TextView title = new TextView(this);
        title.setText("Gate 0 isolated-worker substrate harness\nResearch only. Gate 0 Unresolved. No QEMU or guest.");
        layout.addView(title);
        TextView output = new TextView(this); output.setTextIsSelectable(true);
        output.setText(R.string.initial_status);
        ScrollView scroll = new ScrollView(this); scroll.addView(output);
        layout.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(layout);
    }
}
