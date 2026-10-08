package org.pdva.gate0;

import android.app.*;
import android.content.*;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import org.json.*;

/** Development instrumentation only. Does not assert physical or gate outcomes. */
public final class HarnessInstrumentation extends Instrumentation {
    @Override public void onCreate(Bundle args) { super.onCreate(args); start(); }
    @Override public void onStart() {
        Bundle result = new Bundle();
        try {
            String previous = "";
            for (int i = 0; i < 5; i++) {
                JSONObject report = new JSONObject(new Session(getTargetContext()).run(false));
                if (previous.equals(report.getString("epoch"))) throw new AssertionError("epoch_reuse");
                previous = report.getString("epoch");
                String[] required = { "distinct_worker_uid", "stale_epoch_rejected", "oversized_control_rejected",
                        "trailing_control_rejected", "invalid_frame_rejected", "input_flood_rejected",
                        "readonly_fd_write", "delegated_canary_read", "frame_sequence_1", "frame_sequence_2",
                        "sentinel_integrity", "worker_binder_death" };
                JSONArray rows = report.getJSONArray("probes");
                for (String name : required) {
                    boolean found = false;
                    for (int j = 0; j < rows.length(); j++) {
                        JSONObject row = rows.getJSONObject(j);
                        if (name.equals(row.getString("probe"))) {
                            found = true;
                            if (!"PASS".equals(row.getString("status"))) throw new AssertionError(name);
                        }
                    }
                    if (!found) throw new AssertionError("missing_" + name);
                }
                // Generated return check only where the fixture actually ran.
                for (int j = 0; j < rows.length(); j++) {
                    JSONObject row = rows.getJSONObject(j);
                    if ("generated_return".equals(row.getString("probe")) &&
                            "42".equals(row.getString("expected")) &&
                            !"UNKNOWN".equals(row.getString("status")) &&
                            !"42".equals(row.getString("observed"))) throw new AssertionError("generated_return");
                }
            }
            new Session(getTargetContext()).run(true);
            JSONObject restarted = new JSONObject(new Session(getTargetContext()).run(false));
            if (previous.equals(restarted.getString("epoch"))) throw new AssertionError("restart_epoch");
            Intent launch = new Intent(getTargetContext(), MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            Activity activity = startActivitySync(launch);
            ActivityMonitor monitor = addMonitor(MainActivity.class.getName(), null, false);
            runOnMainSync(activity::recreate);
            Activity recreated = waitForMonitorWithTimeout(monitor, 5000);
            removeMonitor(monitor);
            if (recreated == null) throw new AssertionError("recreation");
            runOnMainSync(() -> recreated.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE));
            waitForIdleSync();
            getTargetContext().startActivity(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            waitForIdleSync();
            getTargetContext().startActivity(launch);
            waitForIdleSync();
            result.putString("result", "PASS development hooks only. Physical status UNKNOWN.");
            finish(Activity.RESULT_OK, result);
        } catch (Throwable e) {
            result.putString("result", "FAIL development hook. No raw exception exported.");
            finish(Activity.RESULT_CANCELED, result);
        }
    }
}
