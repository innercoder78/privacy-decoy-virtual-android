# Gate 0: Linux-hosted QEMU Android cross-build research

**2026-10-08. Gate 0: Unresolved. Gates A–G: Not reached.**
ADR-0001 remains Accepted; ADR-0002 remains Proposed. No engine selected.

## Third revision: Android shared-memory portability (2026-10-09)

**Head `6b91edab5f1bf3e6fe78f56daf8e3eb8c1cae30f` built all requested dependency
libraries on Ubuntu for Android ARM64, then failed during QEMU configuration.**
QEMU compilation/linking was NOT RUN. The next patched head's CI remains pending
at publication; neither a full QEMU executable nor Android runtime behavior is
established by the local controls below.

Live preflight matched main `d5466f1943e3cd7e33cbd62c8a23571e4de52ae5` and
sole open PR #6 at `6b91eda`. Foundation and Android succeeded, cross-build failed;
all 39 Linux repository tests passed. The Android harness passed 48 protocol/report
checks, without any emulator. Reviews, comments and unresolved threads were empty;
combined statuses had no contexts and branch rules were empty. GitHub Status was
operational, updated `2026-10-09T17:14:42.469Z`. The clean existing branch, single
worktree, no stashes, full six-file base diff, ordinary 100644 modes, requirements,
ADRs, evidence, source/license/dependency records and binary inventory were reviewed.
The historical repository remains untouched and read-only.

### What the third Linux attempt actually executed

[Run 37964351266](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/37964351266),
job `113934830958`, checked out the exact `6b91eda` head. It completed source/archive/
Git-object verification, both GLib subproject installations, 41-symbol declared
Kconfig closure, verified NDK r28c acquisition, Android ARM64 link control and ELF
inspection of that control, host Meson preparation, PCRE2, libffi, libfdt and GLib
configuration/build/installation. The earlier two source failures remain failures;
this run separately proves that their corrections advanced the pipeline.

The log records these installed static-library identities (not QEMU DT_NEEDED or
proof that every GLib component will link into the selected QEMU executable):

| Library | Bytes | SHA-256 from the executed run |
|---|---:|---|
| libpcre2-8.a | 464610 | `c4f985898d2e83835716dc43c65471b7dbaccbf5b597f9b012fa908d60d004d3` |
| libpcre2-posix.a | 7258 | `49392a5adfd5a4e59b85153047a86f65414fd38018caeb486a2268b4ce31cf84` |
| libffi.a | 107830 | `5f2765c56ed6d25dcf8b773c5b3a0be3e4b8bd8aedfd44cb44122919bba55b43` |
| libfdt.a | 62028 | `a541b09de75db673691c3779bee30391a54fbd8211a5a6ffd212685f68d0d356` |
| libglib-2.0.a | 8037372 | `50f110beceae022fc3890d72fee5f27bea65a6e5c888edcc6c35c0184f2ea8e5` |
| libgio-2.0.a | 19719336 | `23d4c1c9ab4677084e52b17ec3bc7c421673191e79707f76178c63bae0ed65d0` |
| libgirepository-2.0.a | 2831942 | `783192eb06f376ee3c47660a7972631954c100258d4d2324d902458254feea9f` |
| libgmodule-2.0.a | 71990 | `22a3caf8de2c274831161b38f4fdb77fbc3f3196d74734e1f4f1b08c12a2b695` |
| libgobject-2.0.a | 2732352 | `4ffc851217b8e812a5f524766b49cb4cd951c26a8bcaf662989796fb9d2e3eb6` |
| libgthread-2.0.a | 6222 | `34f76c4c92b363a53c163ef9f19b8c012655da639c351eaa30fad68dd19add92` |
| libintl.a | 12996 | `ab4bc64ec11ef0966e46f610bcc872ac5bb9d3bbeda8453ebee212d06383b26c` |

QEMU configure then reported `Checking for function "shm_open" : NO` and:

```text
meson.build:1375:12: ERROR: C prefer_static library 'rt' not found
FAILED [QEMU Android configure]: Command exit 1; dependent stages NOT RUN
```

The underlying link probe reported an undefined `shm_open`; the next probe could
not find `-lrt`. Other failed optional feature/compiler probes in diagnostic tails
are not the first fatal blocker and are not individually suppressed.

### Exact source behavior and selected adaptation

The source remains QEMU v11.1.2 at
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`. Its `meson.build:1371` assumes every
non-Windows target missing libc `shm_open` must supply librt. Android has neither
that API nor a separate librt in the reviewed NDK API-30 stubs. The NDK's
`sys/mman.h` declares `memfd_create` under GNU feature selection from API 30;
AArch64 API-30 libc exports it as `memfd_create@LIBC_R`. The reviewed Linux and
existing Windows r28c copies of this header and libc link stub are byte-identical.
This establishes build-time API identity, not SELinux/seccomp/isolated-UID authority.

`util/oslib-posix.c:985` creates a unique mode-0 POSIX shm object, unlinks its
name, truncates it to the requested size and returns an owning FD, closing on
resize failure. `util/meson.build` includes this file for POSIX targets.
`backends/hostmem-shm.c` is included by the non-Windows/non-Emscripten system
source set, and `system/physmem.c` calls the function for RAM_SHARED when the
memfd availability check fails. The latter intentionally requests size zero
before later RAM sizing. Thus this is included, potentially reachable source in
the selected system build, not safely removable dead functionality. Actual linked
reachability remains unproved until a QEMU link/map exists. No new backend is enabled.

The local Android-only implementation creates a real memfd with `MFD_CLOEXEC`,
applies `fchmod(fd, 0)` to preserve the original reopening restriction, and uses
`ftruncate` with the existing requested size (including zero). Each syscall error
reports through QEMU's existing Error API; permission/resize errors close the FD.
There is no named filesystem object, ambient directory fallback, raw syscall shim,
dummy rt library, broker, privileged helper or success stub. Non-Android C retains
the original function unchanged. Meson detects the target compiler's `__ANDROID__`
macro (QEMU configure labels Bionic as Linux), requires the reviewed memfd/fchmod/
ftruncate/shared-mmap link control, and preserves its original librt logic for
other targets. Both new C paths require Bionic, AArch64 and API 30 explicitly.

The [memfd API semantics](https://man7.org/linux/man-pages/man2/memfd_create.2.html)
support FD-backed shared mappings and automatic release after all references are
dropped. The name is diagnostic, not a rendezvous pathname. Close-on-exec limits
exec inheritance; it does not prevent deliberate FD passing or fork inheritance.
No seals or huge pages are requested: callers still need writable, resizable RAM,
and the old API supplied no sealing guarantee. Resizing is not physical-page
reservation; allocation/page faults can still exhaust memory or fail. memfd avoids
a `/dev/shm` mount limit but does not supply resource quotas. Android accounting,
FD limits, policy denials, sharing, process death and mapping cleanup remain runtime
Unknowns. This patch does not establish cross-process isolation or a trusted peer.

TCG does **not** call `qemu_shm_alloc` for its split-W^X buffer: `tcg/region.c`
uses `qemu_memfd_alloc`, maps RW/RX aliases and closes the FD after successful
mapping. `util/memfd.c` already retries memfd then falls back to mkstemp; TCG's
default-on split-W^X mode can also fall back, unlike force-on. Neither existing
fallback is newly introduced or used by this adaptation. Both still require a
separate fail-closed authority review before any Android runtime experiment; this
research executable is not approved for launch or harness integration.

### Reproducible patch identity and exact diff

The script verifies both complete pre-patch file SHA-256 values and unique anchors,
rejects a changed/missing/extra patch-input file or duplicate application, validates
all inputs before writing either file, and logs before/after hashes plus the full
unified diff. It changes only these two files inside disposable verified QEMU
source, after acquisition and before any source build code. The original archive,
commit, dependency pins, license notices and provenance remain unchanged. The
oslib file's existing permissive notice is retained; no new third-party dependency
or production adoption is made. This is a repository-owned research adaptation.

| Patched file | Original SHA-256 | Patched SHA-256 |
|---|---|---|
| meson.build | `7d45b715ca8e740d787eee6d4a1e8ae4a7456aecfe16dda2a7d32a0f2cc10591` | `51ac2ab6820b085cce6eaab28adb087885ef12465d81db47ff7899cea117fe6c` |
| util/oslib-posix.c | `ad7bc820a4ab61fa0b00502a0a04540228a7cc60da5cb8908fcbc2af2419b869` | `0e473f258bce59cad1e63d90b424c3994c02816529fbbb4349564b2704876bdc` |

The following UTF-8/LF zero-context unified diff, including its final newline, has SHA-256
`7b9289b30f08c53e29049530c496e1572ac133ae39a0182116e3bc26299c1441`:

```diff
--- a/meson.build
+++ b/meson.build
@@ -1372 +1372,29 @@
-if host_os != 'windows'
+if cc.get_define('__ANDROID__') != ''
+  if not cc.links('''#ifndef _GNU_SOURCE
+#define _GNU_SOURCE
+#endif
+#include <sys/mman.h>
+#include <sys/stat.h>
+#include <unistd.h>
+#include <fcntl.h>
+#if !defined(__ANDROID__) || !defined(__BIONIC__) || !defined(__aarch64__) || __ANDROID_API__ != 30
+#error PDVA research requires Android Bionic AArch64 API 30
+#endif
+int main(void)
+{
+    int fd = memfd_create("pdva-shm-control", MFD_CLOEXEC);
+    void *p;
+    if (fd < 0) { return 1; }
+    if (fchmod(fd, 0) || ftruncate(fd, 4096) || fcntl(fd, F_GETFD) != FD_CLOEXEC) {
+        close(fd);
+        return 2;
+    }
+    p = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
+    if (p == MAP_FAILED) { close(fd); return 3; }
+    if (munmap(p, 4096)) { close(fd); return 4; }
+    return close(fd);
+}
+''', name: 'PDVA Android shared memfd')
+    error('PDVA Android shared memfd functionality unavailable')
+  endif
+elif host_os != 'windows'
--- a/util/oslib-posix.c
+++ b/util/oslib-posix.c
@@ -984,0 +985,28 @@
+#if defined(__ANDROID__)
+/* PDVA research only: anonymous FD, no pathname or fallback authority. */
+#if !defined(__BIONIC__) || !defined(__aarch64__) || __ANDROID_API__ != 30
+#error PDVA research requires Android Bionic AArch64 API 30
+#endif
+int qemu_shm_alloc(size_t size, Error **errp)
+{
+    int fd = memfd_create("qemu-shm", MFD_CLOEXEC);
+
+    if (fd < 0) {
+        error_setg_errno(errp, errno, "failed to create Android shared memfd");
+        return -1;
+    }
+    /* Preserve the original mode-0 restriction on reopening through a path. */
+    if (fchmod(fd, 0) == -1) {
+        error_setg_errno(errp, errno, "failed to restrict Android shared memfd");
+        close(fd);
+        return -1;
+    }
+    if (ftruncate(fd, size) == -1) {
+        error_setg_errno(errp, errno,
+                         "failed to resize Android shared memfd to %zu", size);
+        close(fd);
+        return -1;
+    }
+    return fd;
+}
+#else
@@ -1035,0 +1064 @@
+#endif /* __ANDROID__ */
```

### PCRE2 warnings and explicit minimal targets

The exact PCRE2 10.46 `configure --help`, `configure.ac`, `Makefile.am` and generated
`Makefile.in` were inspected and matched to the pinned archive. There are no
`--disable-pcre2grep` or `--disable-pcre2test` options. The previous configure
completed with both warnings; its selected 8-bit configuration includes pcre2grep,
and pcre2test is a default program. Successful default `make` therefore implies
those targets were built by the reviewed Makefile, not disabled by the rejected
flags. The run did not expose their individual artifact hashes or quiet compiler
logs, so exact utility binaries/object inventory cannot be independently reported.
The installed two library hashes above are direct log evidence.

The revision removes the unsupported flags and adds supported
`--enable-option-checking=fatal`. It explicitly builds `libpcre2-8.la` and
`libpcre2-posix.la` and installs only the reviewed library, include-header,
generated-header and pkg-config targets. Existing static/PIC, no JIT, no 16/32-bit
settings remain. Build/install commands are now logged; the recipe requires both
libraries, headers and pkg-config files and rejects grep/test program outputs in
the build, .libs and installed bin directories. This is target selection, not
warning suppression. The new target sequence awaits execution on Linux.

### Local validation and next evidence boundary

Local Windows controls reverified the actual pinned QEMU archive, rendered the
exact patch, compiled the added qemu_shm_alloc function against real r28c API-30
headers (object only, QEMU Error API declared but not stub-linked), and linked the
standalone shared-memory control without librt. Wrong API 29, x86-64 Android,
non-Android identity and a deliberately missing memfd symbol were rejected.
Non-Android preprocessing of the patched function exactly matched the original.
The resulting standalone control was 7,056 bytes, SHA-256
`e678e948ff1dbd497d5e1b4117df7df4a30d766539d684f4fc01fdbe82c02493`:
ELF64/AArch64 PIE with `/system/bin/linker64`, libc.so/libdl.so, LIBC/LIBC_R
imports, RELRO/bind-now, non-executable stack and 0x4000 LOAD alignment; no
SONAME/RPATH/RUNPATH/TEXTREL/GLIBC versions. Undefined dynamic imports were
memfd_create, fchmod, ftruncate, fcntl, close, mmap, munmap and the normal Bionic
startup imports __libc_init, __cxa_atexit, __register_atfork. This is a link-control
executable, **not QEMU or a JNI library**, and was never executed.

The regression suite now contains 47 tests, preserving all prior 39 unchanged:
43 pass locally, four explicitly skip on Windows (three filesystem tests and one
host-C unit/control test). The new controls cover patch identity, anchors,
duplicate application, exact file set, target/platform isolation and library-only
PCRE2 targets. The next Linux run will also compile/run modeled host syscall-failure/
cleanup tests and reject absent APIs/identities; these are test fixtures, never production API
stubs or Android runtime results. Foundation/Markdown links, harness, Python
syntax, unchanged-workflow shell/manual YAML review, whitespace, exact-base modes,
immutable pins, dependency/license/provenance and public secret/binary checks are
passed before commit. No standalone YAML parser is available locally.

Next: let the unchanged bounded Ubuntu workflow attempt QEMU configure and Ninja
compile/link with this explicit patch, then review the first actual result at the
new exact head. If linking succeeds, inspect the QEMU ELF and full runner-local
link map/inventory before a separate narrow PIC/export/loader experiment. If it
fails, preserve its first genuine diagnostic. Neither local control results nor
successful dependencies imply a QEMU build. New CI remains pending at publication;
no post-push polling or reruns. No phone, ADB, emulator, Cloud, privileged host
installation, Android permission/broker change, host VpnService, guest image or
committed native binary. Gate 0 Unresolved; A–G Not reached; ADR-0002 Proposed;
no production-engine, containment, security or performance claim.

## Second revision record: GLib subproject materialization (2026-10-09)

**Head `b981a47430f5781d79d783237282f42d71a3c092` proved the corrected Git
source verification on Linux, then failed at the existing gvdb directory.**
It did not compile dependencies or configure QEMU. The next head's CI results
remain pending at publication; the local correction below is source-copy evidence.

Live preflight again matched main `d5466f1943e3cd7e33cbd62c8a23571e4de52ae5`
and the sole open PR #6 at that head. Foundation and Android succeeded; cross-build
failed. Both Linux test invocations passed all 29 tests without skips. The Android
job built its harness and passed 48 protocol/report checks, not an emulator.
Reviews, comments and unresolved threads were empty. Combined commit statuses
contained no contexts; its empty pending aggregate is not a check failure. Main's
classic required-check endpoint reported unprotected and its branch rules list
was empty; no protection setting or workflow is changed. GitHub Status reported
All Systems Operational, updated `2026-10-09T16:00:14.488Z`. The clean existing
branch, one worktree, no stashes, full six-file exact-base diff/100644 modes,
requirements, ADRs, source/license/dependency scope and binary inventory were
reviewed. No unrelated work or Android authority is changed.

### Observed second Linux run

[Run 37887280609](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/37887280609),
job `113680005143`, checked out the exact `b981a47` head on 2026-10-09 UTC,
Ubuntu 24.04.5 image `20261004.327.1`. Foundation/harness validation, 29 tests,
six pinned source archive hashes and all four pinned Git commit/tree/source
verifications passed. The latter covered 1,013 files with actual Linux type/mode
checks. This directly confirms the prior CRLF/archive-identity correction.

The next operation failed with:

```text
FAILED [verified source acquisition]: [Errno 17] File exists:
'$RESEARCH/glib-source/glib-e05063ccc6c8f222465a1080927f4c14349f3de6/subprojects/gvdb';
later stages NOT RUN; no gate change.
```

The unconditional `shutil.copytree` assumed an absent destination. This is a
source-materialization defect, not a compiler/portability or CI outage result.
The later proxy copy and wheel verification were not reached. Kconfig closure,
NDK acquisition/link control, Meson preparation, PCRE2, libffi, libfdt, GLib,
QEMU configure/compile/link and ELF inspection were **NOT RUN** in this run.

### Exact archive identities and correction

The existing GLib archive was rehashed against its unchanged SHA-256 pin and
its actual tar records inspected:

| Destination | Exact GLib archive observation | Required initial state |
|---|---|---|
| `subprojects/gvdb` | One directory record, type `5`, size 0, mode 0775, no link target or descendants; an empty submodule placeholder | Empty real directory |
| `subprojects/proxy-libintl-0.5` | No record and no descendants | Absent |

GLib's pinned `.gitmodules`/gvdb wrap identify commit
`2b42fc75f09dbe1cd1057580b5782b08f2dcb400`; the upstream exact-ref contents API
also identifies gvdb as a submodule at that commit. Its proxy wrap names version
0.5, the same source URL, directory and SHA-256 already in the recipe. These are
the intended sources, not alternate content chosen to resolve a collision.
The gvdb archive has 14 regular files and four directory records (108,451 file
bytes); proxy has five regular files and one directory (39,244 bytes). Neither
archive contains links or special entries. Their COPYING/license files remain
included, with the existing LGPL scope below; no dependency/version is added.

The new helper requires each destination's specific initial state, rejects
symlink ancestors, and rechecks the source archive's SHA-256. Its bounded manifest
allows only unique safe paths under the expected archive root and regular files
and directories; links, special entries, unexpected layouts and modes fail closed.
Every extracted source file is compared with the authenticated archive for bytes,
type and safe extraction mode, with exact file/directory sets. A new staging copy
is verified again before the destination is rechecked. Only `rmdir` of the empty
gvdb placeholder is permitted, followed by renaming the staged directory and a
final verification. There is no recursive destination deletion, merge, overwrite
or acceptance of even apparently correct populated content. Proxy must remain
absent until installation. The existing Git verifier and all immutable pins remain.

Local Windows verification successfully installed both real pinned archives into
the exact destination skeleton extracted from the authenticated GLib tar. Only
that skeleton was extracted for this test because Windows cannot recreate GLib's
unrelated license symlinks; no complete Linux extraction/build is claimed. The
39-test suite retains the prior 29 tests and adds ten materialization tests:
36 pass locally and three filesystem tests explicitly skip on Windows. Coverage
includes both accepted states, incorrect absent/empty states, populated and
ordinary-file conflicts, destination/ancestor symlinks (Linux), substituted,
missing or extra source files, corruption during staging, corrupt archive/hash,
wrong root, traversal, archive links and duplicate paths. Linux runs all 39.

The pinned QEMU archive's `VERSION` is **11.1.2**, commit
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`. The PR body's 11.0.1 wording was a
typo; the source pin and the already-correct evidence inventory do not change.
Foundation/Markdown links, harness authority, Python syntax, workflow shell and
manual YAML review, whitespace, exact-base modes, pin/license/dependency and
binary/secret checks passed before committing this correction. A standalone
YAML parser remains unavailable. All build stages and compiler/provenance gates
are retained; no speculative dependency migration or warning suppression is added.

The new commit triggers the existing bounded Ubuntu pipeline. Its actual next
stage remains **Unknown/pending**, with no post-publication polling or reruns.
No phone, ADB, physical execution, Codex Cloud, new host permission, privileged
Android API or host VpnService is involved. Gate 0 **Unresolved**, Gates A–G
**Not reached**, ADR-0002 **Proposed**, no production engine or isolation claim.

## First revision record: original Linux failure and correction (2026-10-09)

**The original Linux run failed in source acquisition. No dependency compiled,
no QEMU configure ran, and no QEMU ELF exists.** The revised head's Linux result
was pending at that publication and subsequent owner review; it was not inferred from
local source-verification tests. Gate 0 remains Unresolved; A–G Not reached.

The live revision preflight matched main
`d5466f1943e3cd7e33cbd62c8a23571e4de52ae5` and the only open PR, #6, head
`96b0e3c9aab1ede4907d4d6fa0d22c2409126b2a`. The full six-file base diff and
100644 modes were inspected. Foundation and Android checks succeeded; cross-build
failed. No reviews, issue/review comments or unresolved threads were present;
combined statuses were empty. GitHub Status reported operational, page update
`2026-10-09T04:09:18.387Z`. The clean existing branch, one worktree, absence of
stashes, unchanged harness/manifest, provenance policy and dependency inventory
were checked. No new branch or PR, runtime dependency or native binary is added.

### Observed original run

[Run 37859565828](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/37859565828),
job `113591801036`, tested original head `96b0e3c...` on 2026-10-08 UTC. Its
runner was Ubuntu 24.04.5, image `20261004.327.1`, Git 2.55.0, Python 3.12.3,
GCC 13.3.0, Make 4.3, Ninja 1.13.2, pkg-config 1.8.1 and host
setuptools/wheel/pip 68.1.2/0.42.0/24.0. These are observed host tools, not
executed Android compilers. The exact-head log shows:

```text
STAGE verified source acquisition
[six upstream source archives verified]
[pinned dtc commit fetched; git archive --format=tar run]
FAILED [verified source acquisition]: Hash mismatch: dtc.tar:
1fb660c56f7c255b930f9763f58e0b3f3c59d1815fa11bc5cb01d01823540ba4
Process completed with exit code 1
```

Expected Windows-generated tar SHA-256:
`1df504e71aa4704157ec94f37da2aa82d672349f20bd92ca79516a0a56a1a29a`.
Actual Ubuntu tar SHA-256:
`1fb660c56f7c255b930f9763f58e0b3f3c59d1815fa11bc5cb01d01823540ba4`.
This is a source-verification/tooling defect in the recipe, not a Bionic compiler
failure or GitHub outage. NDK acquisition, the declared Kconfig control, Meson
preparation, PCRE2, libffi, libfdt, GLib, QEMU configure/compile/link and ELF
inspection were **NOT RUN**. No later-stage success or compiler error is reported.

### Established root cause, not a tar-metadata assumption

Local Git 2.56.0.windows.2 inherited system `core.autocrlf=true`. The original
review command's `git archive` applied CRLF conversion. With the same dtc commit,
`tar.umask=0002` and **only** `core.autocrlf=false`, local Git reproduced the
Ubuntu digest exactly. Thus Git-version difference is not needed to explain this
failure. The Windows archive was 1,116,160 bytes; the LF archive 1,095,680 bytes.

Both archives have the same 317 paths: 310 regular files and seven directories,
no symlinks or gitlinks. Exactly 305 file contents differ; for each, converting
CRLF to LF reproduces the other byte-for-byte. All 310 LF files independently
match their Git blob IDs. The same pinned commit references tree
`5de1e174f53a6ea499a49ac7b5eb7fe816dd9902`. Modes, uid/gid, mtime, entry type,
link target, owner/group names and PAX metadata match; the PAX commit comment is
unchanged. Content sizes, consequent header checksums/block offsets/padding and
archive length differ. No dtc export-ignore/export-subst attribute is present.
The old tar hash therefore attested transformed files, not exact repository bytes.

The other inputs were reviewed for the same issue. In particular, keycodemapdb's
`.gitattributes` marks `.gitattributes` and `.gitignore` export-ignore. Merely
setting autocrlf=false would still omit tracked source files from that archive.
Export-subst can likewise rewrite content. These transformations are bypassed,
not accepted as alternative exact-source identities.

### Corrected source identity and review

For the four Git inputs, the recipe now pins both the original **commit ID** and
an independently reviewed **tree ID** (table below). Fresh temporary upstream
fetches reproduced the tree IDs from the prior local objects. No source revision
changed. `git fsck --strict` checks recursive object integrity; raw commit and root
tree hashes are independently recomputed and the commit's tree header must match
the pin. The complete recursive tree supplies paths, blob IDs and modes; only
regular 100644/100755 files and 120000 symlinks are allowed. Gitlinks, unsafe paths
and leaf/ancestor conflicts are rejected.

`git cat-file --batch` reads raw blobs without checkout/archive filters. Before
writing, every object's type, size and independently recomputed Git blob ID are
checked, with count/per-blob/total-size bounds. The destination must be new. Files
are created exclusively with exact bytes and executable modes; relative in-root
symlinks are deferred until ordinary writes finish. The resulting tree is checked
again for exact content/type/mode correspondence, missing or extra files and
unexpected directories. Symlink text and resolved chains must remain inside the
source root; unsafe paths, type changes and modified contents fail closed. Linux
requires POSIX mode checks. Windows local tests verify pinned mode metadata but
cannot establish actual POSIX filesystem execute bits; main() still refuses a
Windows build. SHA-1 here is Git's object identity, not a newly asserted signature
or independent SHA-256 supply-chain guarantee.

All four freshly fetched inputs passed raw-object materialization locally:
310 dtc files, 19 keycodemapdb files, 478 SoftFloat files and 206 TestFloat files.
This is **source-integrity evidence only**. The six upstream archive URLs and
SHA-256 pins, NDK pin, bundled wheel pins, library versions and license scope
remain unchanged. QEMU's previously reviewed Berkeley build overlays are applied
after upstream-tree verification; they remain explicit source modifications from
the separately hash-verified QEMU archive, not part of the upstream tree identity.
No source build code executes before these checks.

The successful-skip optimization was removed. Every triggered workflow attempts
its real bounded pipeline; there is no per-step success condition, informational
compiler failure or continue-on-error. Existing path filters, read-only permissions,
checkout pin, runner/time/resource limits and no-upload policy remain. The script
review also found that its separate compiler process groups needed explicit
cleanup on SIGTERM: the new handler unwinds run() so it kills that process group
on timeout/cancellation. Linux cancellation behavior is source-reviewed, not
claimed locally executed on Windows. Host/target routing, API 30, configuration,
ELF checks and all build stages remain intact; no speculative portability patch
or fake API was added. NDK extraction additionally rejects symlink ancestor
conflicts and resolved chains outside the NDK root; all 35 links in the pinned
archive were inspected for ancestor conflicts locally.

### Revision validation and next evidence boundary

Local Windows: 29 tests discovered, 27 passed, two explicit POSIX filesystem
mode/symlink tests skipped because Windows cannot provide that observation. Those
two tests run on Linux, including the unchanged foundation workflow. Added tests
cover exact bytes despite CRLF/export attributes, wrong tree pins, corrupt Git
objects, modified/missing/extra files, extra directories and unsafe paths/links.
Foundation, harness authority, Python syntax, workflow shell/static review,
whitespace, exact-base modes, unchanged archive pins and binary/public-data review
passed before this revision's commit. No standalone YAML parser is available
locally; the straightforward YAML structure is manually reviewed, not claimed
parser-validated. Source-copy success is not any library or emulator build success.

The updated branch will trigger a new real Linux attempt. Its checks/results
remain **pending** at publication. The next exact-head review must record the
first actual later-stage result, if any, without rewriting this original failure.
No phone, ADB, Android emulator, Android execution, host root or Codex Cloud is
used. No selected production QEMU engine; ADR-0002 remains Proposed. Publication
updates only PR #6 and stops without polling or rerunning Actions.

## Original publication record (2026-10-08)

**No new QEMU compilation or link result is available.** Local Linux was unavailable,
so this change prepares a constrained GitHub Actions Ubuntu 24.04 attempt. The
owner explicitly requires stopping after pushing and opening the PR, without
watching or querying CI. The Linux job therefore begins at publication; its
configuration, dependency builds, QEMU link and ELF inspection remain **pending /
Unknown**, not successful. This is a reproducible attempt recipe with verified
inputs, not a claim of a reproduced build. A subsequent exact-head review must
supply the actual Linux results before drawing a build-feasibility conclusion.

The [Windows execution ledger](gate-0-qemu-android-crossbuild-execution.md) remains
valid: QEMU configure failed at the Python `pyvenv/Scripts` versus `pyvenv/bin`
layout, while libfdt and a POSIX link control compiled independently. Those old
artifacts are not a working emulator and are not Linux-hosted results.

| Evidence class | Observation at publication | Limit |
|---|---|---|
| Verified Fact / direct repository observation | Canonical main is `d5466f1943e3cd7e33cbd62c8a23571e4de52ae5`; zero open PRs at preflight | Pre-publication snapshot |
| Verified Fact / local observation | No registered WSL distribution; no Docker/Podman executable found on PATH | No OS/container installed; does not assert every possible remote host is absent |
| Verified Fact / local observation | Source archives downloaded and hashed; all 11,245 QEMU archive blobs match the exact Git commit | No independent release-signature authentication; not a full security audit |
| Source Observation | GLib requires PCRE2, libffi, zlib, iconv, intl and gvdb; QEMU configures extra test-source subprojects | Actual successful configured/linked closure pending |
| Inference | Linux-native Python should remove the specific Windows virtualenv layout mismatch | Does not predict Bionic compilation success |
| Hypothesis | A minimal full-system Android ARM64 executable can link from the reviewed graph | Falsified for this recipe by its first reproducible configuration/compiler/linker blocker |
| Upstream Claim | QEMU's security policy excludes TCG from guest-isolation guarantees | No PDVA containment result |
| Unsupported | Root/KVM/privileged host repair, broad storage, shipping this experimental payload | Intentional scope restrictions, not measured denials |
| Unknown | Every Linux build stage, Android load/run, ART coexistence, isolated-worker containment and performance | No gate pass or platform support claim |

## Original preflight and preservation

The original clean PR #5 branch was preserved. One existing worktree and no
stashes were observed. Fetch verified remote main; the new
`codex/qemu-android-linux-crossbuild` branch starts at that exact commit. The
baseline contains 66 regular mode-100644 files. No tracked emulator, guest image,
submodule or native binary was adopted. Existing ignored build tools and research
outputs remain untouched; the historical repository was not modified or needed.

Every open PR was enumerated: zero, so open-head/base diffs, modes, reviews,
comments and unresolved review threads were inapplicable. Exact-main foundation
check `113448802270` was completed/success, workflow run `37817216631`. The
combined-status API returned no separate contexts (its empty `pending` aggregate
is not a failed check). Latest Android workflow `37739885820` succeeded at
`a7b0d2c6044cc3acf4569edb114c6e0622655ee9`; the documentation-only merge did not
trigger it. Both existing workflows were inspected and remain unchanged.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported
`All Systems Operational`, indicator `none`, page update
`2026-10-08T20:27:42.115Z` during preflight.

Requirements, architecture, roadmap, gates, ADRs, evidence criteria, source policy,
QEMU research/proof records and the isolated-worker contract were reviewed.
The harness still has zero manifest permissions, a non-exported isolated service,
no app zygote and no shared isolated process. No harness implementation, Gradle
input, runtime dependency or broker contract changes. Foundation admits only the
two new exact paths, with positive/negative admission and binary-content tests;
all existing restrictions and regression cases remain.

The Windows sandbox failed before process launch with
`helper_unknown_error: setup refresh had errors`; approved direct execution
recovered local reads, edits and validation. This is workstation infrastructure,
not Android evidence. Local tools observed: Python 3.12.14 and Git 2.56.0.windows.2.
No phone, ADB, Android emulator, Android execution or Codex Cloud was used.

## Reviewed build inputs and correspondence

The authoritative executable recipe is
[the research script](../../.github/scripts/qemu-android-research.py), with exact
URLs, hash checks, commands, options and bounded diagnostics. Hashes below were
measured locally **before** the workflow was created, not accepted from downloads
at runtime. PCRE2/libffi/proxy hashes also match the already pinned GLib wraps.
The Linux NDK archive was checked against the official published r28c SHA-1
`a7b54a5de87fecd125a17d54f73c446199e72a64`, then its SHA-256 was measured for the
recipe. [Official versioned NDK download metadata](https://github.com/android/ndk/wiki/Home/cb1cda2b35f19f5d0014ace408c93ad146efec63)
is the publisher reference. Neither SHA-1 agreement nor HTTPS is an independently
verified signature. No target library is downloaded as an opaque prebuilt.

| Input | Immutable source identity | Archive SHA-256 or current Git tree ID |
|---|---|---|
| QEMU v11.1.2 | `4fc49f46dc95d4a27de2509e7fceb2931e91faeb` | `a5a78e7d395ed096a7b2d98375978d0e2cf73f62c49a081ca48fa665d479b09f` |
| GLib 2.90.1 | `e05063ccc6c8f222465a1080927f4c14349f3de6` | `9c74d8dc96a547a544f3f479bc6f2fe8a333524ff44c997998ebe9963a63ad52` |
| PCRE2 10.46 | tag peeled to `b2bd4254b379b9d7dc9a3dda060a7e27009ccdff` | `15fbc5aba6beee0b17aecb04602ae39432393aba1ebd8e39b7cabf7db883299f` |
| libffi 3.5.2 | tag `e2eda0cf72a0598b44278cc91860ea402273fa29` | `f3a3082a23b37c293a4fcd1053147b371f2ff91fa7ea1b2a52e335676bac82dc` |
| proxy-libintl 0.5 | tag `33934de09af6a6627eb44e310a8079df009abdbb` | `f7a1cbd7579baaf575c66f9d99fb6295e9b0684a28b095967cfda17857595303` |
| gvdb | GLib wrap `2b42fc75f09dbe1cd1057580b5782b08f2dcb400` | `069a00aa1fc893f18423602f4e095583be5a220429f6e8a58d70511490b4b019` |
| libfdt / dtc | QEMU wrap `b6910bec11614980a21e46fbccc35934b671bd81` | tree `5de1e174f53a6ea499a49ac7b5eb7fe816dd9902` |
| keycodemapdb | QEMU wrap `f5772a62ec52591ff6870b7e8ef32482371f22c6` | tree `eaa3f9fb1e2c7687b334f57cb605140cb5450f16` |
| Berkeley SoftFloat test input | QEMU wrap `b64af41c3276f97f0e181920400ee056b9c88037` | tree `5f46f374bcf9aef50442ba5fd25f3b5bcdf963c4` |
| Berkeley TestFloat | QEMU wrap `e7af9751d9f9fd3b47911f51a5cfd08af256a9ab` | tree `9e166ce5ee90e0cb45f975a89c877bc4114de601` |
| Linux NDK r28c | Google `28.2.13676358`, Android API 30 target | `dfb20d396df28ca02a8c708314b814a4d961dc9074f9a161932746f815aa552f` |

QEMU/GLib/gvdb use exact-commit GitHub source archives; PCRE2/libffi use upstream
release source archives; proxy uses the hash-pinned upstream tag archive. GitLab
archive endpoints for dtc/keycodemapdb returned bot challenges, so the four QEMU
subproject rows now identify independently reviewed **Git tree IDs**. The original
host-transformed archive checks were replaced by the complete object/manifest
verification described above. No floating ref is built.
QEMU source correspondence was checked by recomputing Git blob IDs for every
archive file against the prior verified exact-commit checkout, including symlinks.

GLib's two COPYING symlinks could not be created by Windows tar, and Windows tar
lacked its bzip2 helper. These were local review-extraction limitations, not
compiler failures. Python's standard-library tar reader recovered PCRE2 review;
license targets and exact archive bytes remain available. Linux extraction uses
Python's `data` filter. NDK ZIP symlinks are explicitly restored after regular
entries and checked to remain inside the extracted NDK. Downloads have size caps
and hash checks before extraction or execution; no arbitrary URL input exists.

## Scoped adoption, licenses and trust roles

**Decision: adopt these exact inputs solely for this disposable, non-distributing
cross-build attempt.** No production dependency, redistribution approval or
complete vulnerability audit follows. The repository maintainer owns future
re-pinning, source/security review, rebuilds and invalidation of affected evidence.
A suspect or changed input stops its dependent build. No shipment maintenance SLA
or complete file-to-linked-object legal inventory is established.

| Component / reviewed files | License/source observation | Build or possible runtime role |
|---|---|---|
| QEMU `LICENSE`, `system/main.c`, `system/vl.c`, `tcg/region.c`, `util/coroutine-sigaltstack.c`, `util/memfd.c`, Meson/configure | Full emulator GPLv2 with file-specific GPLv2-or-later, permissive and LGPL notices; TCG does not relicense the machine | Experimental target executable; upstream generators are host tools. Firmware excluded from installation; no firmware submodule fetched |
| GLib `glib/gmain.c`, `glib/meson.build`, `glib/libcharset/localcharset.c`, root Meson/options and `LICENSES/` | Core LGPL-2.1-or-later; localcharset carries Library GPL-2-or-later; source tree has other file licenses, including MIT, Apache, MPL and test/document licenses | Core utility/main-loop target library. Whole GLib build graph also builds GObject/GIO/tools, but those must not be called QEMU runtime dependencies without link evidence |
| PCRE2 `LICENCE.md`, `src/pcre2_compile.c`, `ChangeLog`, generated configure | BSD-3-Clause WITH PCRE2-exception; JIT/SLJIT excluded; no Apple-platform wrap patch used | Android static 8-bit regex library for GLib; no target test/grep program requested |
| libffi `LICENSE`, `src/aarch64/ffi.c`, `src/aarch64/sysv.S`, configure | MIT-style notices retained; release Autoconf/build helper licenses separate | Android static dependency required by GLib's GObject graph; not assumed linked into QEMU's core GLib-only route |
| proxy-libintl `libintl.c`, `libintl.h`, `COPYING`, `meson.build` | Library GPL-2-or-later; Meson sets `STUB_ONLY` | Explicit local gettext fallback if Android libc lacks intl; no runtime library searching in the stub branch |
| gvdb `gvdb-reader.c`, `gvdb-builder.c`, `meson.build` | LGPL-2.1-or-later | GLib/GIO source copy-library; omitted from the earlier shortlist, now explicitly supplied |
| libfdt ten C units and headers listed in PR #5 | GPL-2.0-or-later OR BSD-2-Clause SPDX notices | Android static device-tree library; compile only that list, not the DTC tool or lexer/parser |
| keycodemapdb `README`, license files, `tools/keymap-gen`, `data/keymaps.csv` | GPL-2-or-later OR BSD-3-Clause, including generated output | Native Python generator and generated target keymap tables; full-system QEMU config requires it even without a guest input device |
| Berkeley `COPYING.txt`, QEMU's `subprojects/packagefiles/berkeley-*` Meson overlays | BSD-3-Clause; pinned QEMU supplies build overlays | QEMU `tests/fp/meson.build` configures these for TCG; only `qemu-system-aarch64` is requested from Ninja, not the tests |
| zlib, iconv, libc/libm/libdl and possible liblog | Public NDK headers/link stubs and NDK notice inventory; actual platform implementation comes from Android | No host GNU/Linux target library and no separately downloaded zlib/iconv binary. Positive link control requires `iconv_open`, `iconv_close`, `zlibVersion` |

PCRE2's 10.46 changelog records the CVE-2025-58050 bounds fix; the prior QEMU/GLib
security-history observations remain in the [feasibility review](gate-0-qemu-android-crossbuild-feasibility.md).
libffi/gvdb/proxy and generated inputs received bounded source/build/license
review, not an exhaustive contemporary vulnerability clearance. Static LGPL
linking creates future corresponding-source/relinking obligations that this
non-publishing experiment does not resolve. Final linked source correspondence
must be reviewed from the actual configuration and link map before distribution.

PCRE2 and libffi use their reviewed release configure scripts, so their Meson
wrapdb patches are **not adopted**. Proxy and gvdb are pre-extracted into the exact
GLib subproject names. QEMU's existing Berkeley Meson overlays are copied explicitly;
the original recipe introduced no C portability patch, fake API, disabled compiler
failure or warning bypass. The third revision adds the explicit Android patch
recorded above. The original QEMU configuration addition is `CONFIG_ARM_VIRT=y` in
`configs/devices/aarch64-softmmu/pdva.mak` inside temporary source storage.

Host tools are separate: Ubuntu supplies Python, pip/setuptools/wheel, native
C/C++ compiler, binutils, Make, Ninja, Git and pkg-config. Their exact versions,
runner `ImageOS`/`ImageVersion` and `/etc/os-release` are logged by the attempt.
They are mutable runner infrastructure; no apt/pip network installation occurs.
Missing prerequisites are fatal infrastructure blockers, not success or a Bionic
failure. The host venv inherits runner packages; this is not a hermetic build.
QEMU's bundled Meson 1.11.1 (Apache-2.0), pycotap 1.3.1 (MIT), qemu.qmp 0.0.6
(GPL/LGPL notices) and local QEMU Python tooling retain PR #5's source scope.
All three wheel SHA-256 values are rechecked in the script before offline install.
The official Linux NDK is reviewed compiler infrastructure, not a source-rebuilt
compiler or permission to adopt opaque Android runtime libraries.

## Reproduction and bounded workflow

On an existing Linux x86-64 host with Python >=3.12 and the host prerequisites:

```sh
python3 .github/scripts/validate-foundation.py
python3 .github/scripts/test-repository-validation.py
python3 .github/scripts/validate-harness.py
python3 .github/scripts/qemu-android-research.py
```

For the bounded CI invocation, use the exact limits in
[the workflow](../../.github/workflows/qemu-android-research.yml). It uses only
`pull_request`, Ubuntu 24.04, `contents: read`, no supplied secrets, and the
independently rechecked official checkout commit
`3d3c42e5aac5ba805825da76410c181273ba90b1`. Credentials are not persisted. The
script forwards only a small host environment allowlist to subprocesses; Git
ignores global/system config and cannot prompt for credentials.

One job has a 45-minute wall limit and an inner 40-minute process deadline; Make
and Ninja use two workers. Core dumps are disabled; address space is capped at
6 GiB **per process**, individual output files at 4 GiB (Bash's 1024-byte units).
The script enforces per-download/per-extraction limits and checks its own temporary
tree against 8 GiB between phases and every five seconds during commands. This
is a sampled storage budget with possible between-check overshoot, not a kernel
filesystem quota or aggregate process-memory cgroup. No privileged setup, custom
runner, global cleanup, caches, artifact uploads, release, firmware installation
or target program execution is used. Cost is bounded by one standard hosted job;
account billing/minute availability was not inspected or promised free.

Only the workflow and build script trigger this research job. Every triggered relevant PR head runs the real attempt; the original
unchanged-input skip has been removed. New pushes
cancel older work for the same PR. The existing Android path filter includes
`.github/**`, so this PR can also trigger its existing 25-minute harness job,
plus the five-minute foundation check. Those scopes/timeouts are unchanged.

The actual script logs sanitized commands in dependency order: acquisition,
declared 41-symbol Kconfig control, NDK and API link control, offline Meson,
PCRE2, libffi, libfdt, GLib, QEMU configure, QEMU compile/link, output inspection.
Host native compilers are explicit; target compilers use
`aarch64-linux-android30-clang{,++}` and NDK LLVM tools. Target `.pc` files live
in one separate prefix; `PKG_CONFIG_PATH` is empty and `PKG_CONFIG_LIBDIR` is
restricted to that prefix. Meson metadata says Android/aarch64 and requires an
execution wrapper without providing one. The NDK compiler supplies its sysroot;
a pkg-config sysroot is deliberately omitted to avoid incorrectly rewriting the
already absolute dependency prefix. QEMU's own configure may report Linux because
Bionic defines `__linux__`; final ELF evidence, not that label, decides identity.

GLib and QEMU use `--wrap-mode=nodownload` / `--disable-download`. No automatic
wrap, Rust, firmware or target-library fetch is authorized. Configuration or
compiler failure is fatal and logs its named stage and bounded diagnostic tail.
Later stages are NOT RUN, never reported as passing. Infrastructure before a
compiler runs, an actual dependency/compiler failure and a final output-inspection
failure must be distinguished during the later review.

QEMU requests only `aarch64-softmmu`, TCG, ARM virt and minimal serial research,
with default features/devices disabled, no Rust, tools, guest agent, plugins,
modules, GIO, Pixman, installed blobs or audio drivers. Requested flags are from
the pinned configure/Meson options, not a different QEMU release. The actual
Kconfig closure still includes ACPI, PCI, SMMU, flash, semihosting and other
infrastructure: PR #5's 41 symbols are a declared-input control, not proof of 41
compiled devices. Generated detected config and linked object inventory are
printed separately. Compiled generic monitor/QMP and network-capable code are not
claimed absent just because the future launch contract exposes none of them.
No guest NIC, SLIRP, passthrough, host sharing, guest-accessible QMP or external
storage is authorized. No runtime launch occurs. Future launch must select an
explicit 64-bit CPU (e.g. cortex-a53), direct reviewed kernel/initramfs inputs,
TCG and no accelerator fallback; no proprietary firmware is needed for that plan.

## Pending ELF evidence and integration disposition

If QEMU links, the recipe records size/SHA-256, readelf headers/program headers,
dynamic entries/symbols/versions, section allocation, Meson options/dependencies,
generated configuration, link-map hash and linked-object inventory. It rejects
non-AArch64/non-ELF64/non-PIE output, a missing Android `/system/bin/linker64`,
GNU libc versions, unexpected dynamic libraries, RPATH/RUNPATH, text relocations,
executable stack, missing RELRO/bind-now or LOAD alignment below 16 KiB. The full
link map stays on the ephemeral runner, with no binary publication. Log tails
are bounded: missing/truncated detail remains Unknown and requires a later
narrower evidence run; a green command is not a complete human ELF audit.

An ET_DYN executable with PT_INTERP is not a JNI library. No SONAME/export-map,
linker-namespace compatibility, Android load success or 16-KiB runtime behavior
is asserted from its filename or static alignment alone. In particular, segment
alignment is only one page-size check; future packaging and runtime checks remain.
There is no QEMU output hash, native size, resolved QEMU DT_NEEDED list or
compiled-device result. The third Linux run above records successful dependency
builds and the first fatal QEMU configuration diagnostic.

| Next integration question | Source-based disposition; all runtime outcomes Unknown |
|---|---|
| Executable versus PIC/JNI | Build the executable first. Dependencies request PIC, but QEMU exports, entry adapter, linker namespaces and complete PIC closure require a separate narrow link/loader experiment before harness integration |
| Worker initialization and native threads | One fresh dedicated isolated worker per instance; review `qemu_init`, main-loop ownership, cleanup, fatal exits and native-thread interaction with Java. No manager-UID fallback |
| Signals/coroutines and ART | Bionic lacks the earlier tested makecontext interface; QEMU's sigaltstack fallback manipulates SIGUSR2, masks and alternate stacks. Coexistence is unproved; no fake ucontext shim |
| TCG memory and temporary files | `tcg/region.c` uses split W^X aliases; future force-on split-W^X must fail closed. `util/memfd.c` can fall back to mkstemp: reject or replace this ambient path through separately reviewed delegated authority |
| Kernel/initramfs | Bounded immutable, authenticated read-only FD loading needs an adapter. QEMU block fdsets do not cover arbitrary boot-file opens; no worker-selected host path or directory capability |
| Serial/UI | Bounded, rate-limited serial buffer and typed UI transport; no generic QMP or command endpoint. A serial boot would not satisfy interactive guest requirements |
| Death/revocation | Existing worker self-termination/lease is not independent reaping after arbitrary native compromise. Establish host-observed death, descendant handling and capability revocation; closing the manager's FD is insufficient |
| Exhaustion | Guest RAM and TCG cache limits do not bound total RSS, threads, allocation peaks or FD growth. Enforcing quotas and host lifecycle handling remain separate |
| Native compromise | Assume arbitrary QEMU-native code execution. QEMU emulates the guest machine; post-compromise containment depends on host enforcement and narrowly authorized brokers |

**Next smallest non-physical step:** review the newly created PR's exact-head
Linux job once the owner supplies that result. Classify its earliest actual
blocker and retain dependency/configuration evidence. If linking succeeds, first
perform a narrow PIC/export/loader-closure experiment; do not immediately integrate
into the existing harness. If a dependency or portability check fails, fix only
that justified bounded issue and rerun under a separately reviewed head. No phone
is a prerequisite for either next step. No production engine, APK emulator payload,
complete Android 17 guest, security/performance claim or ADR acceptance follows.

## Original local validation (2026-10-08)

Local Windows validation passed: foundation/Markdown links, all 20 repository
regression tests (including corrupt-download and traversal rejection), harness
manifest authority checks, Python AST compilation and whitespace. A direct script
invocation correctly refused Windows before creating a research build; that is a
host-guard check, not a failed Linux attempt. Workflow shell syntax is checked with
Git Bash; YAML/security fields are reviewed as source. A standalone YAML parser
was unavailable locally; no package was installed to conceal that limitation.

The exact-base diff and mode/inventory review cover only the two research files,
the narrow validator/test updates and evidence documentation. No Android source
or permission changed; no source archive, guest/runtime binary, secret or local
private path is intentionally tracked. At original publication all hosted results
were pending; the later observed source-acquisition failure is recorded above.
At original publication no Linux dependency or QEMU build result existed. The
third run above now establishes dependency builds and a QEMU configuration
failure. The newly patched head remains pending and must not inherit a QEMU
success from local controls or prior dependency results.
