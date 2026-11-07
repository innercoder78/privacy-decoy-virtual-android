# Separate Java memory diagnostic

Development source only; installation is **NOT AUTHORIZED**. See the
[evidence and conditional phone procedure](../../docs/evidence/gate-0-java-memory-diagnostic.md).
This module has no dependency on `gate0-harness`, JNI, native build, runtime Maven
library, VM engine or network. It does not change the harness execution lock.

Using the existing reviewed JDK 17, SDK 37 and build-tools 36.0.0 environment:

```text
python android/build.py --configure-on-demand :memory-diagnostic:assembleRelease :memory-diagnostic:diagnosticTest :memory-diagnostic:lintRelease
python .github/scripts/test-memory-diagnostic.py --java-home <existing-JDK-home> --android-jar <existing-SDK>/platforms/android-37.0/android.jar
python .github/scripts/test-memory-diagnostic.py --apk android/memory-diagnostic/build/outputs/apk/release/memory-diagnostic-release-unsigned.apk
```

Use configuration-on-demand and qualified module task names: the root otherwise
configures the unrelated native harness, which requires NDK/CMake. Do not use
unqualified root `assemble` or any install task. Add `--offline` when the complete
pinned dependency closure is already available. The unchanged bootstrap verifies
the Gradle distribution, installed files, startup inputs and STRICT dependencies.
Do not regenerate verification metadata or weaken verification to resolve errors.
The module deliberately has **no signing configuration** and disables the debug
variant. Only a non-debuggable release variant is an intended diagnostic artifact.
Unsigned local build outputs are disposable development evidence, not qualified
artifacts, signed-byte reproducibility evidence or a changed release signing policy.

`Experiment` owns acquisition flags and independent cleanup. `AndroidOps` keeps
descriptors/addresses private and makes only the public SDK calls in PR #57.
The pure-Java `Attempt` requires a durable started marker before acquisition.
The Activity constructs the adapter only inside the button listener; onCreate
does not run the experiment. No intent extras, automatic retries or background
components exist. Only the boolean marker is persisted, never a result.

The experiment runs synchronously on the foreground UI thread. This avoids
delegation and concurrent Activity cleanup, but there is **no hard syscall latency
or ANR guarantee**. Activity callbacks cannot cancel a syscall in progress.
If interrupted, killed, hung, or reopened after activation, treat the observation
as Unknown. The persisted marker prevents an automatic or second manual attempt;
recreation is conservatively blocked even if the original Activity was still idle.
There is no reset button. Clearing data/reinstalling is not an authorized retry.
Application data corruption, user clearing data, OS failure and adversarial app
modification are outside the one-way local marker's trust boundary.

The source checker is a narrow regression guard, not a Java security verifier.
JVM fault injection and Activity framework doubles do not execute Android, emulate
its lifecycle or prove OEM storage/backup behavior. Packaged manifest/DEX/inventory
checks do not qualify the compiler, signer, device or full runtime behavior.
