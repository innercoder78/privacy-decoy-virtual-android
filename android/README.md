# Gate 0 isolated-worker substrate harness

This is a small ordinary Android research APK and JNI probe, preparatory to the
[already specified isolated-QEMU experiment](../docs/evidence/gate-0-isolated-qemu-proof.md).
**Gate 0 remains Unresolved; A–G remain Not reached.** No engine is selected.
There is no QEMU, Linux boot, guest image, Android 17 guest, Google software,
network backend or production Persona implementation.

The [slice specification](../docs/evidence/gate-0-isolated-worker-harness.md)
defines the capabilities, result schema, falsifiers and Unknowns.
The [tool adoption record](../docs/evidence/gate-0-isolated-worker-adoption.md)
and [build dependency inventory](../docs/evidence/gate-0-isolated-worker-dependencies.md)
explain the new build trust. All application and probe sources are new PDVA work;
no historical Android source or Gradle scaffold was copied.

## Build

Use Python 3.11+, JDK 17, and an Android SDK installed from Google. Set
`JAVA_HOME` and `ANDROID_HOME` to local installations. Accept applicable SDK
licenses through the ordinary SDK installation process. Install these packages:

```text
sdkmanager "platforms;android-37.0" "build-tools;36.0.0" "ndk;28.2.13676358" "cmake;3.22.1"
```

From the repository root:

```text
python android/build.py :gate0-harness:assembleDebug :gate0-harness:assembleRelease :gate0-harness:assembleDebugAndroidTest :gate0-harness:protocolTest :gate0-harness:lintDebug
python .github/scripts/validate-foundation.py
python .github/scripts/test-repository-validation.py
python .github/scripts/validate-harness.py
git diff --check
```

The Python bootstrap downloads official Gradle 9.6.0 and checks its pinned SHA-256.
It uses only the standard library, places the distribution under ignored
`android/build/`, and avoids committing a wrapper JAR. It requires network on
first use. Do not use Gradle's verification-metadata write mode in normal builds.

Outputs are local and ignored:

- Release-equivalent APK: `gate0-harness/build/outputs/apk/release/gate0-harness-release.apk`.
- Debug APK: `gate0-harness/build/outputs/apk/debug/gate0-harness-debug.apk`.
- Development instrumentation APK:
  `gate0-harness/build/outputs/apk/androidTest/debug/gate0-harness-debug-androidTest.apk`.

Release is **non-debuggable** and signed with a locally generated ordinary
development app key. That signing identity is not suitable for product release;
no key is committed or uploaded. Neither variant requests any permissions.
Research host floor is API 30 because FD-mode inspection uses `Os.fcntlInt`.
Compile/target API is 37. This floor is not a product device-support claim.
ARM64 has the generated-code fixture; x86-64 intentionally reports Unsupported
for that fixture, encoded as UNKNOWN with an explicit limitation.

## Future ordinary physical experiment

The harness has not been physically run. All physical outcomes are **Unknown**;
the default report preserves that label. A later evidence PR must identify and
attest its actual physical run separately.

These are future instructions, not a requirement for this PR or an automatic
prerequisite before every subsequent PR. Tony does not need to connect a phone
now. Source research, theory, architecture, provenance, build integration, static
analysis and other non-physical falsification work may continue while useful,
including further QEMU research and adoption review, without claiming a substrate
pass. Physical facts remain Unknown wherever later reasoning depends on them.
Only a specific unresolved claim that genuinely cannot advance honestly without
stock physical-device evidence requires stopping at that exact question. ChatGPT
will identify future physical-device tasks separately.

1. On Tony's stock non-rooted ARM64 production phone, install the release APK
   through ordinary sideloading. Optional development installation:
   `adb install -r android/gate0-harness/build/outputs/apk/release/gate0-harness-release.apk`.
   Do not use `-g`, shell permission grants, root, Shizuku or system changes.
2. Disconnect ADB and open **PDVA Gate 0 research** normally.
3. Tap **Run fresh epoch**. Review each probe separately, then tap
   **Copy sanitized JSON**. The clipboard export happens only on that button.
4. Run **five start/stop cycles**, then **Worker death / rebind exercise**.
   Compare synthetic epochs, UID/PID observations, stale requests and Binder death.
   Numeric UID reuse is not evidence of instance reuse.
5. Rotate and background/foreground during a run. The Activity cancels its run
   when stopped and the next launch begins a fresh epoch. No foreground service,
   exemption or persistence mechanism is installed.
6. Record public device model, OS build/security patch, stock/non-rooted attestation,
   exact source revision and APK SHA-256 in a separate reviewed evidence record.
   Never include serials, Android ID, accounts, paths or raw logcat. Preserve
   failures and Unknowns. Do not label any result Gate 0 Passed.

If a worker's death cannot be observed, further sessions in that management
process are blocked. Closing descriptors alone is not revocation. Relaunching
the app must not be treated as independent proof of kernel process reaping.

Optional development instrumentation (not release/physical acceptance evidence):

```text
adb install -r android/gate0-harness/build/outputs/apk/debug/gate0-harness-debug.apk
adb install -r android/gate0-harness/build/outputs/apk/androidTest/debug/gate0-harness-debug-androidTest.apk
adb shell am instrument -w org.pdva.gate0.test/org.pdva.gate0.HarnessInstrumentation
```

This runs repeated sessions, protocol and FD assertions, death/rebind,
Activity recreation, rotation, and foreground/background hooks. It supplies no
permission grants. Installing debug over the locally signed release replaces the
tested variant: reinstall release and launch normally for release evidence.
Instrumentation is compiled in CI but requires an actual Android host to execute.
