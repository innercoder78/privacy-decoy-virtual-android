# QEMU Android research: execution ledger

**2026-10-08; local Windows x86_64 build research only.** Read the
[findings and decision](gate-0-qemu-android-crossbuild-feasibility.md) first.
QEMU configure failed. **No QEMU executable/library, guest boot or Android run
result exists.** Successful artifacts below are libfdt and a small API link
probe, not a VM engine. Gate 0 Unresolved; A–G Not reached.

## Environment and preservation

The command runner's sandbox initially failed before starting a process with
`helper_unknown_error: setup refresh had errors`. Approved direct command
execution recovered local access. That workstation tooling failure says nothing
about the proposed Android sandbox. No target Android process was started.

Observed tools: Git 2.56.0.windows.2, GitHub CLI 2.101.0, Git Bash
5.3.15(2)-release x86_64-pc-cygwin, native Windows CPython 3.12.14 and SDK Ninja
1.10.2. No registered WSL distribution was returned by `wsl --list --quiet`.
An existing canonical ignored SDK held NDK r28c, so no new NDK was downloaded.
No host Linux environment was installed or remote build job created.

NDK `source.properties` reported `28.2.13676358` / r28c. Compiler output:

```text
Android (13624864, based on r530567e) clang version 19.0.1
LLVM compiler revision: 97a699bf4812a18fb657c2779f5296a4ab2694d2
Default host target: x86_64-w64-windows-gnu
```

The actual Android command overrides that default with
`--target=aarch64-linux-android30`. The packaged `clang_source_info.md` records
base `3b5e7c83a6e226d5bd7ed2e9b67449b64812074c` and Android patch ledger
`e727bfb014bd436f581a66a450c939a6983a1fc3`, consistent with the existing
[harness tool adoption](gate-0-isolated-worker-adoption.md).

Local source/build/logs are under ignored `android/build/qemu-research/` and a
separate temporary research directory. QEMU rejects source/build directory names
containing whitespace or colons (`configure` lines 166–168). The canonical path
has whitespace, so a separate Git copy under a no-space temporary MSYS path was
used. This was a setup accommodation, not a source patch. Nothing was moved or
deleted from another project; the historical checkout was not consulted.

Below, `$RESEARCH` is that temporary directory, `$NDK_BIN` is the existing
Windows-host NDK LLVM bin directory, `$PYTHON` the existing native Python,
`$NINJA` the SDK Ninja, and `$OUT` ignored research output. These aliases replace
private absolute paths; shell wrappers used MSYS paths obtained with `cygpath`.
Commands show the executed operations with those path substitutions. Raw local
logs are not suitable for public upload. No credential or host identifier is
part of this record. These aliases are not instructions to put outputs in Git.

## Source identities and bootstrap inputs

```sh
git ls-remote https://gitlab.com/qemu-project/qemu.git 'refs/tags/v11.1.2*'
git ls-remote https://github.com/qemu/qemu.git 'refs/tags/v11.1.2*'
git -c core.autocrlf=false clone --depth 1 --branch v11.1.2 --single-branch \
  https://gitlab.com/qemu-project/qemu.git "$OUT/qemu"
git -c core.autocrlf=false clone --no-hardlinks --no-checkout \
  "$OUT/qemu" "$RESEARCH/qemu"
git -C "$RESEARCH/qemu" -c core.autocrlf=false checkout --detach \
  4fc49f46dc95d4a27de2509e7fceb2931e91faeb
```

Tag/commit values are in the findings record. Stable history was deepened by 80
commits in the ignored source clone for the bounded fix review; no source checkout
changed. No signature verification was performed. No firmware submodule was
initialized. QEMU's own Python bootstrap installs the following bundled wheels:

| File | SHA-256 | Metadata license |
|---|---|---|
| meson-1.11.1-py3-none-any.whl | `9b3a023657e393dbc5335b95c561337d49b7a458f5541e47ec44f2cc566e0d80` | Apache-2.0 |
| pycotap-1.3.1-py3-none-any.whl | `1c3a25b3ff89e48f4e00f1f71dbbc1642b4f65c65d416524d07e73492fff25ea` | MIT |
| qemu_qmp-0.0.6-py3-none-any.whl | `5d7c5af0e9de427696e3bf72e333965c3a697929f77f6b7ddc30c989fc7b539b` | GPLv2 and LGPLv2+ classifiers; file-level review still required |

The bootstrap also installs QEMU's local Python source (`qemu==0.6.1.0a1`).
Observed host packaging versions: pip 26.2.1, setuptools 84.0.0, wheel 0.48.0.
The environment is non-isolated and inherits the installed Python package set;
these hashes do not establish hermetic or independently source-rebuilt tools.
Only bundled wheels/local QEMU tooling were requested by the configure bootstrap;
no GLib, PCRE2 or other target binary was fetched to mask a failure.

## Actual QEMU configure attempts

Three local shell wrappers executed the existing tools, preserving arguments:

```sh
# $RESEARCH/bin/cc
#!/bin/sh
exec "$NDK_BIN/clang.exe" --target=aarch64-linux-android30 "$@"

# $RESEARCH/bin/py
#!/bin/sh
exec "$PYTHON" "$@"

# $RESEARCH/bin/ninja
#!/bin/sh
exec "$NINJA" "$@"
```

In execution the tool paths were embedded as quoted absolute paths in the
wrappers, rather than relying on exported variables. The target compiler ran
and linked configure's PIE check. Empty `--cross-prefix=` requests cross mode;
it does not supply LLVM binutils or an Android dependency sysroot to pkg-config.
Those generated defaults (`ar`, `ranlib`, `pkg-config`, etc.) need replacement
before a real build on a prepared host. No claim that this is a complete portable
build recipe is made.

Attempt A, in a fresh `$RESEARCH/build-android` directory:

```sh
sh ../qemu/configure \
  --target-list=aarch64-softmmu --cross-prefix= \
  --cc="$RESEARCH/bin/cc" --cpu=aarch64 \
  --python="$RESEARCH/bin/py" --ninja="$RESEARCH/bin/ninja" \
  --without-default-features --without-default-devices \
  --enable-tcg --enable-fdt=internal \
  --disable-rust --disable-docs --disable-tools \
  --disable-guest-agent --disable-plugins --disable-pixman \
  > configure.log 2>&1
```

**Exit 1.** Configure generated cross metadata for Linux/aarch64/little-endian.
It accepted the actual option spellings. It did not reach dependency resolution
or generate a working Ninja build. Attempt A had no explicit machine selection;
source inspection showed that minimal-device mode additionally needs ARM_VIRT.
Attempt B corrected this with one temporary source-tree configuration input:

```text
# configs/devices/aarch64-softmmu/pdva.mak
CONFIG_ARM_VIRT=y
```

In a separate fresh `$RESEARCH/build-virt`, the same command additionally used
`--with-devices-aarch64=pdva --disable-install-blobs`. **Exit 1, same failure.**
That one-line untracked temporary configuration is the only QEMU source-tree
addition; no QEMU C, Meson or configure patch was applied. No upstream code was
changed to suppress checks. Sanitized decisive diagnostics from both runs:

```text
python version: Python 3.12.14
mkvenv: Creating non-isolated virtual environment at 'pyvenv'
mkvenv: installing meson==1.11.1, pycotap==1.3.1
../qemu/configure: line 970: cd: pyvenv/bin: No such file or directory
../qemu/configure: line 1168: $BUILD/meson: No such file or directory
../qemu/configure: line 1949: $BUILD/meson: No such file or directory
ERROR: meson setup failed
```

Windows Python created `pyvenv/Scripts`; configure explicitly looked in
`pyvenv/bin`. Earlier Python-store-alias messages did not prevent selection of
the explicit Python wrapper. `config.log` also contains a deliberate LITTLE
endianness diagnostic and an unsuccessful optional guest-test `-lgcc` probe;
neither is the terminal failure. Do not mislabel these as a QEMU/Bionic compile
failure. No Ninja build was started. No undefined-symbol, binary-size or linked
QEMU dependency inventory can therefore be reported.

**Failure class: build-host/toolchain orchestration.** GLib and target pkg-config
are further unfinished prerequisites; this run did not reach their tests.
A Linux-native Python/compiler/build stack avoids this particular Windows layout
mismatch, but has not been shown here to complete the Android build. Installing
a new OS/tool distribution or patching the bootstrap was not used as a substitute
for reviewing that environment. Full compilation and platform portability remain
Unknown; isolated-process authority was not exercised.

## Executed device-closure check

From the temporary QEMU source, native Python ran:

```sh
"$PYTHON" scripts/minikconf.py --allnoconfig \
  ../virt-config.mak ../virt-config.d \
  configs/devices/aarch64-softmmu/pdva.mak Kconfig \
  CONFIG_TCG=y CONFIG_FDT=y CONFIG_LINUX=y CONFIG_AARCH64=y \
  CONFIG_ARM=y CONFIG_TARGET_BIG_ENDIAN=n > ../virt-config.mak
```

Exit 0; 41 output symbols below. This is a direct Kconfig check with declared
capability inputs, not Meson's complete detected configuration. `CONFIG_ARM=y`
represents the target base architecture. No Pixman/Rust/PCI_DEVICES/TEST_DEVICES
capability was enabled. The selected machine still pulls in PCI infrastructure.

```text
ACPI ACPI_APEI ACPI_CXL ACPI_HMAT ACPI_HW_REDUCED ACPI_MEMORY_HOTPLUG
ACPI_NVDIMM ACPI_PCI ACPI_PCIHP ACPI_PCI_BRIDGE ACPI_VIOT
ARM_COMPATIBLE_SEMIHOSTING ARM_GIC ARM_GICV3 ARM_GICV5 ARM_SMMUV3 ARM_V7M
ARM_VIRT DEVICE_TREE DIMM FW_CFG_DMA GPIO_KEY GPIO_PWR MEM_DEVICE
MSI_NONBROKEN PCI PCI_EXPRESS PCI_EXPRESS_GENERIC_BRIDGE PFLASH_CFI01
PL011 PL011_C PL031 PL061 PLATFORM_BUS PTIMER SEMIHOSTING SMBIOS
VIRTIO VIRTIO_MEM_SUPPORTED VIRTIO_MMIO WDT_SBSA
```

Actual output uses `CONFIG_<name>=y`, one per line. PowerShell's UTF-8 file
serialization produced SHA-256
`75d27de6bbd0a7874b745c264c3fea1cb02c7a95a61c61aa38d1d69dce4ba3d8`;
line-ending changes in another host's redirection can change that hash. No
semihosting host-file access is authorized by this compiled-symbol inventory.

## Successful libfdt Android cross-build

QEMU's exact [dtc wrap](https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/subprojects/dtc.wrap)
was used, not a system prebuilt library. The ignored checkout was cloned from
`https://gitlab.com/qemu-project/dtc.git`, fetched with `--depth 1` at
`b6910bec11614980a21e46fbccc35934b671bd81`, and checked out detached at that ID.
Its `libfdt/meson.build` enumerates the ten C units below. Headers and those
units were checked for GPL-2.0-or-later OR BSD-2-Clause SPDX notices. DTC's
compiler, lexer/parser generators and tests were not built. No libfdt patch.

The actual PowerShell build loops over the following names. With `$SRC` pointing
to that checkout's libfdt directory and `$LIBOUT` to a separate ignored directory:

```powershell
$names = @('fdt','fdt_addresses','fdt_check','fdt_empty_tree','fdt_overlay',
           'fdt_ro','fdt_rw','fdt_strerror','fdt_sw','fdt_wip')
$objects = @()
foreach ($name in $names) {
    $obj = Join-Path $LIBOUT "$name.o"
    & "$NDK_BIN/clang.exe" --target=aarch64-linux-android30 -O2 -fPIC `
      -fstack-protector-strong -D_FORTIFY_SOURCE=2 -I $SRC `
      -c (Join-Path $SRC "$name.c") -o $obj
    if ($LASTEXITCODE -ne 0) { throw 'compile failed' }
    $objects += $obj
}
& "$NDK_BIN/llvm-ar.exe" rcsD (Join-Path $LIBOUT 'libfdt.a') @objects
& "$NDK_BIN/clang.exe" --target=aarch64-linux-android30 -shared `
  '-Wl,--no-undefined' '-Wl,-soname,libfdt.so' '-Wl,-z,relro,-z,now' `
  '-Wl,--build-id=sha1' @objects -o (Join-Path $LIBOUT 'libfdt.so')
& "$NDK_BIN/llvm-readelf.exe" -h -l -d --dyn-syms `
  (Join-Path $LIBOUT 'libfdt.so')
```

All ten compiles, archiving and linking exited 0. This is a direct compilation
of the Meson source list, **not a successful execution of the libfdt Meson build**;
it does not apply its version script or install rules. The diagnostic shared
library exposes libfdt exports and has no JNI entry points.

| Actual local artifact | Size | SHA-256 |
|---|---:|---|
| libfdt.a | 61,740 bytes | `4152c382c137ec57a4a3ce012c12e0c23db9d143db4dec9596a12585caa4980e` |
| libfdt.so | 47,624 bytes | `c76f7da8169ab06a26c455fdd0c009b63e6159fa94481337f2e1b159d1921213` |

ELF observation: ELF64 little-endian AArch64, ET_DYN shared object,
SONAME `libfdt.so`, DT_NEEDED `libdl.so` and `libc.so`, no PT_INTERP,
no RPATH/RUNPATH, LOAD alignment `0x4000`, distinct R/RX/RW LOAD segments,
RW/non-executable GNU_STACK, GNU_RELRO and BIND_NOW. There is no generated-code
or TCG allocation in libfdt. These properties do not prove Android loading.

Undefined dynamic imports are the expected versioned Bionic entries:
`__cxa_finalize`, `__cxa_atexit`, `__register_atfork`, `__stack_chk_fail`,
`strlen`, `memcmp`, `memmove`, `memchr`, `strtoul`, `strchr`, `memcpy`, `strrchr`,
`strnlen`, `memset`, each `@LIBC`. No glibc `GLIBC_*`, GNU/Linux interpreter or
C++ shared runtime was observed. `--no-undefined` checks resolution against NDK
link stubs; dynamic imports naturally remain and require the Android loader.
No artifact was loaded into Android, installed in an APK, or independently
reproduced. Local hashes identify one unstripped build, not reproducibility proof.

## API-floor controls — compiled, never executed

Negative control source:

```c
#include <ucontext.h>
int main(void) { makecontext(0, 0, 0); return 0; }
```

`clang.exe --target=aarch64-linux-android30 -Werror ucontext-probe.c -o ucontext-probe`
exited 1: `call to undeclared function 'makecontext'`. This is an API/header
observation for the exact r28c/API-30 setup, not a runtime denial.

Positive link-control source (`posix-probe.c`):

```c
#define _GNU_SOURCE
#include <pthread.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/eventfd.h>
#include <unistd.h>
static void *worker(void *x) { return x; }
int main(void) {
    pthread_t t;
    sigset_t mask;
    stack_t old;
    sigemptyset(&mask);
    pthread_sigmask(SIG_BLOCK, &mask, 0);
    sigaltstack(0, &old);
    int fd = memfd_create("pdva-build-probe", MFD_CLOEXEC);
    if (fd >= 0) close(fd);
    int e = eventfd(0, EFD_CLOEXEC);
    if (e >= 0) close(e);
    if (pthread_create(&t, 0, worker, 0) == 0) pthread_join(t, 0);
    return 0;
}
```

`clang.exe --target=aarch64-linux-android30 -O2 -fPIE -pie -Werror posix-probe.c -o posix-probe`
exited 0. The actual source (LF, no trailing newline) SHA-256 is
`2613972fa7ec53a1e56f08e0dfceec084fc954fe037cbf3c8cecf86e9ae5b1cf`.
Output size 7,168 bytes; SHA-256
`e9030fbad35ac556d8083bcbbf9cdb27f568d3d955f3cb8744bde0679ce15a0b`.
Readelf reports AArch64 ET_DYN with PT_INTERP `/system/bin/linker64`, and
DT_NEEDED libc.so/libdl.so: an Android PIE executable, not a JNI shared library.
This shows declarations/link stubs for the referenced operations. It does not
test successful memfd creation, executable mappings, thread creation, signal
coexistence, syscall access, isolated UID, JIT execution or QEMU.

## Unbuilt GLib graph and next-run obligations

GNOME upstream tag `2.90.1` peeled to
`e05063ccc6c8f222465a1080927f4c14349f3de6`, annotated tag
`7971940db22b0c290e521d28b3651232100bb55b`.
Exact-source Meson/options/COPYING/NEWS and wraps were retrieved from the GNOME
GitHub mirror by that commit. Only source review occurred. QEMU needs GLib
>=2.66.0, this GLib candidate needs Meson >=1.4.0; use the stricter QEMU minimum.

The following values are **upstream wrap declarations**, not downloaded or
independently verified archive contents. Full licensing/security review of
transitive source and Meson patches remains a prerequisite to their build:

| Declared input | SHA-256 in exact GLib wrap |
|---|---|
| PCRE2 10.46 tar.bz2, PCRE2Project/pcre2 release | `15fbc5aba6beee0b17aecb04602ae39432393aba1ebd8e39b7cabf7db883299f` |
| Meson wrapdb pcre2_10.46-1 patch.zip | `761d16c89b9c13812842916b7ee970650ee7c1810f83bc567351faf7365b66be` |
| libffi 3.5.2 tar.gz, libffi/libffi release | `f3a3082a23b37c293a4fcd1053147b371f2ff91fa7ea1b2a52e335676bac82dc` |
| Meson wrapdb libffi_3.5.2-1 patch.zip | `1ee3035d92e4df3541d0b2b8d192d2fa183b46e4a3d68c00d8f71ede354bee74` |
| frida/proxy-libintl 0.5 tag tar.gz | `f7a1cbd7579baaf575c66f9d99fb6295e9b0684a28b095967cfda17857595303` |

The PCRE2 wrap additionally references GLib's local
`pcre2/fix-build-on-apple-platforms.patch`; it is not silently approved here.
Android API 30 supplies iconv declarations, but actual GLib configuration must
verify whether public libc satisfies the chosen feature checks. Likewise,
intl's fallback must be selected explicitly and reviewed. `libffi` is a GLib
build-graph dependency even if the eventual QEMU executable does not link
GObject. Do not misreport build dependencies as all being loaded runtime code.

The next build must freeze source archive/signature/patch identities, license
notices, native host tools and target dependency options; build PIC where JNI
will require it; isolate `PKG_CONFIG_LIBDIR`; record Meson's actual dependency
and coroutine choices; and inspect final ELF/link maps. No GLib/Pixman artifact,
complete QEMU graph, firmware distribution or JNI dependency closure was produced
by this run. The successful libfdt artifact does not close those Unknowns.
