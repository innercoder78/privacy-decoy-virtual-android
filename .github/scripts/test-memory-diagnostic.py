#!/usr/bin/env python3
"""Source, desktop JVM and unsigned-package checks; never installs or runs Android."""
import argparse
import ast
import hashlib
import inspect
import io
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import stat
import time
import zlib

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / 'android/memory-diagnostic'
JAVA = MODULE / 'src/main/java/org/pdva/memorydiagnostic'
NS = '{http://schemas.android.com/apk/res/android}'

# Public source evidence, derived from canonical Git blobs at this exact base.
# This is a review boundary, not authentication of the machine or this verifier.
SOURCE_BASE = '69a7165043e1e7fc565a9ff10f044adc4874c595'
BUILD_PATH = 'android/memory-diagnostic/build.gradle'
REVIEWED_FILES = frozenset({
    '.github/scripts/test-memory-diagnostic.py',
    'docs/evidence/gate-0-companion-source-controls.md',
    'docs/evidence/README.md',
})
PROTECTED = {
    'build': (9, '9d2f3c65e56afe1ddbb172e8315f63071b6a0bda8c69a75e6a71072c79ac0816'),
    'checks': (30, 'bc602236d6d38c868b7257b5cf5efdf6962b08502db68466dd535159abb2c3d4'),
    'cleanup': (1, '2d2854e1726811fc5703c325f71ba3ab541ae28e41853b06a870d1ad615deeba'),
    'diagnostic': (7, '4256dfa721e55f8217d4253546fcdaa8dbeced4353f94981ee79847e6bf4aa7e'),
    'governance': (109, '384c3a4289c41a25e00a5a90f5eaee5f5a8b7208438fe8de099ad359cb57c45c'),
    'host': (22, 'dd352694ada63116991b5e8743f36b23e170b435c49d1614e1beb7ba77e703da'),
    'lock': (1, '9fee0fc620a37c57b9fa5be64d24ecdda0335d024486697fa54e4aaa3404b751'),
}
BASE_BUILD = b"""plugins { id 'com.android.application' }
android {
    namespace 'org.pdva.memorydiagnostic'
    compileSdk 37
    buildToolsVersion '36.0.0'
    defaultConfig {
        applicationId 'org.pdva.memorydiagnostic'
        minSdk 37
        targetSdk 37
        versionCode 1
        versionName '0.1-diagnostic'
    }
    // Development compilation/packaging only. No installable signed output.
    buildTypes {
        debug { signingConfig null }
        release { signingConfig null; debuggable false; minifyEnabled false }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}
// The physical candidate is release-equivalent only. Debug compatibility DEX
// adds an unnecessary surface; no debug APK is an intended diagnostic artifact.
androidComponents.beforeVariants(androidComponents.selector().withBuildType('debug')) { variant ->
    variant.enable = false
}
tasks.register('compileDiagnosticTests', JavaCompile) {
    source = files('src/main/java/org/pdva/memorydiagnostic/Experiment.java',
                   'src/main/java/org/pdva/memorydiagnostic/Attempt.java',
                   'src/test/java/org/pdva/memorydiagnostic/ExperimentTest.java')
    classpath = files()
    destinationDirectory = layout.buildDirectory.dir('diagnostic-tests')
    sourceCompatibility = '17'
    targetCompatibility = '17'
}
tasks.register('diagnosticTest', JavaExec) {
    dependsOn 'compileDiagnosticTests'
    classpath = files(layout.buildDirectory.dir('diagnostic-tests'))
    mainClass = 'org.pdva.memorydiagnostic.ExperimentTest'
}
"""
METADATA_LINES = b'    dependenciesInfo {\n        includeInApk = false\n    }\n'
PROPOSED_BUILD = BASE_BUILD.replace(b'    compileSdk 37\n', b'    compileSdk 37\n' + METADATA_LINES)


class SourceRejection(AssertionError):
    """An identified source assertion, distinct from infrastructure failures."""


def source_require(condition, code):
    if not condition:
        raise SourceRejection(code)


def protected_group(path):
    if path == 'android/gate0-harness/src/main/java/org/pdva/gate0/Session.java':
        return 'lock'
    if path == 'android/memory-diagnostic/src/main/java/org/pdva/memorydiagnostic/Experiment.java':
        return 'cleanup'
    for prefix, group in (('android/gate0-harness/', 'host'),
                          ('android/memory-diagnostic/', 'diagnostic'),
                          ('android/', 'build'), ('.github/', 'checks')):
        if path.startswith(prefix):
            return group
    return 'governance'


def protected_evidence(snapshot):
    """Length-delimited exact path/blob bytes; modes are checked independently."""
    groups = {group: [] for group in PROTECTED}
    for path, (_, data) in snapshot.items():
        if path not in REVIEWED_FILES and path != BUILD_PATH:
            groups[protected_group(path)].append((path, data))
    result = {}
    for group, rows in groups.items():
        digest = hashlib.sha256()
        for path, data in sorted(rows):
            for value in (path.encode('utf-8'), data):
                digest.update(len(value).to_bytes(8, 'big'))
                digest.update(value)
        result[group] = (len(rows), digest.hexdigest())
    return result


def check_baseline(evidence):
    source_require(evidence == (SOURCE_BASE, PROTECTED), 'baseline-evidence')


def check_source_modes(snapshot):
    source_require(isinstance(snapshot, dict) and all(
        isinstance(path, str) and isinstance(entry, tuple) and len(entry) == 2
        and entry[0] == '100644' and isinstance(entry[1], bytes)
        for path, entry in snapshot.items()), 'regular-source-modes')


def check_review_scope(snapshot):
    # These three files need independent full-diff review. Their contents cannot
    # self-certify that review; no wildcard exemption or caller allowlist exists.
    source_require(REVIEWED_FILES <= snapshot.keys(), 'reviewed-file-inventory')


def check_metadata_delta(snapshot):
    source_require(snapshot.get(BUILD_PATH, (None, None))[1] == PROPOSED_BUILD,
                   'exact-companion-delta')


def check_protected_source(snapshot):
    actual = protected_evidence(snapshot)
    for group, expected in PROTECTED.items():
        source_require(actual[group] == expected, 'protected-' + group)


def verify_companion_delta(snapshot, evidence):
    """Only a source-delta result; never build, signing or operation admission.

    Evidence must be the reviewed public baseline receipt. Unknown/missing
    evidence fails; never derive a replacement baseline from candidate inputs.
    All content outside the exact proposal and enumerated review files is pinned,
    including documentation, file additions/deletions and the failure ledger.
    """
    check_baseline(evidence)
    check_source_modes(snapshot)
    check_review_scope(snapshot)
    check_metadata_delta(snapshot)
    check_protected_source(snapshot)


def git_source(*arguments):
    return subprocess.check_output(['git', '--no-optional-locks', *arguments], cwd=ROOT, timeout=60)


def committed_source(ref):
    # Resolve to a commit before using a ref in subsequent plumbing commands.
    commit = git_source('rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
    rows = git_source('ls-tree', '-rz', '--full-tree', commit).split(b'\0')
    entries = []
    for row in filter(None, rows):
        meta, path = row.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        source_require(kind == 'blob', 'unsupported-git-entry')
        entries.append((path.decode('utf-8'), mode, oid))
    # One bounded batch; no fetch, checkout, filters, Gradle or filesystem writes.
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=''.join(oid + '\n' for _, _, oid in entries).encode(),
                            capture_output=True, check=True, timeout=60).stdout
    snapshot, offset = {}, 0
    for path, mode, oid in entries:
        end = result.index(b'\n', offset)
        header = result[offset:end].split()
        source_require(len(header) == 3 and header[:2] == [oid.encode(), b'blob'], 'git-blob-receipt')
        size = int(header[2]); offset = end + 1
        data = result[offset:offset + size]; offset += size
        source_require(len(data) == size and result[offset:offset + 1] == b'\n'
                       and path not in snapshot, 'git-blob-extent')
        offset += 1
        snapshot[path] = (mode, data)
    source_require(offset == len(result), 'git-batch-extent')
    return snapshot


def working_source():
    """Tracked and nonignored new files, without opening ignored/private assets."""
    snapshot = {}
    for row in filter(None, git_source('ls-files', '--stage', '-z').split(b'\0')):
        meta, path = row.split(b'\t', 1)
        mode, _, stage = meta.decode().split()
        source_require(stage == '0', 'unmerged-source')
        snapshot[path.decode('utf-8')] = (mode, b'')
    for path in filter(None, git_source('ls-files', '--others', '--exclude-standard', '-z').split(b'\0')):
        snapshot[path.decode('utf-8')] = ('100644', b'')
    for path, (mode, _) in snapshot.copy().items():
        file = ROOT / path
        source_require(not file.is_symlink() and file.is_file(), 'nonregular-working-source')
        # POSIX executable worktree changes must be caught before staging too.
        if os.name != 'nt' and file.stat().st_mode & 0o111:
            mode = '100755'
        snapshot[path] = (mode, file.read_bytes())
    return snapshot


def expect_source_rejection(verifier, snapshot, evidence, code, name):
    try:
        verifier(snapshot, evidence)
    except SourceRejection as failure:
        require(str(failure) == code, 'wrong source rejection: ' + name)
    else:
        raise AssertionError('negative accepted: ' + name)


def detector_removed(detector):
    """Compile a real detector-body deletion, not a mocked success/exception."""
    node = ast.parse(inspect.getsource(globals()[detector])).body[0]
    node.body = [ast.Pass()]
    verifier = ast.parse(inspect.getsource(verify_companion_delta)).body[0]
    module = ast.fix_missing_locations(ast.Module(body=[node, verifier], type_ignores=[]))
    namespace = globals().copy()
    exec(compile(module, '<source-detector-removal>', 'exec'), namespace)
    return namespace['verify_companion_delta']


def source_cli_tests(snapshot):
    """Real subprocess/Git fixture; no baseline history or active module edits."""
    with tempfile.TemporaryDirectory(prefix='pdva-source-fixture-') as temp:
        root = Path(temp)
        subprocess.run(['git', 'init', '--quiet', str(root)], check=True,
                       capture_output=True, timeout=30)
        stream = bytearray(b'commit refs/heads/fixture\n'
                           b'committer Source Fixture <fixture@example.invalid> 0 +0000\n'
                           b'data 7\nfixture\n')
        for path, (mode, data) in sorted(snapshot.items()):
            stream.extend(f'M {mode} inline {json.dumps(path)}\ndata {len(data)}\n'.encode())
            stream.extend(data + b'\n')
        stream.extend(b'\ndone\n')
        subprocess.run(['git', 'fast-import', '--quiet', '--done'], cwd=root,
                       input=bytes(stream), check=True, capture_output=True, timeout=30)
        # Only this reviewed Python file is written to the fixture worktree.
        # The proposed module remains a disposable Git blob, never a build input.
        script = root / '.github/scripts/test-memory-diagnostic.py'
        script.parent.mkdir(parents=True)
        script.write_bytes(snapshot['.github/scripts/test-memory-diagnostic.py'][1])
        result = subprocess.run([sys.executable, str(script), '--check-source-ref', 'refs/heads/fixture'],
                                capture_output=True, text=True, timeout=30)
        require(result.returncode == 0 and not result.stderr and result.stdout.startswith(
            'PASS: exact proposed source delta only;'), 'isolated Git proposal CLI')
        result = subprocess.run([sys.executable, str(script), '--verify-source-baseline'],
                                capture_output=True, text=True, timeout=30)
        require(result.returncode == 1 and not result.stdout and 'CalledProcessError' in result.stderr
                and 'exit status 128' in result.stderr and 'rev-parse' in result.stderr,
                'missing exact Git baseline must reject recomputation')
    print('PASS: real isolated Git proposal CLI; missing exact baseline rejected at Git resolution')


def companion_source_tests():
    current = working_source()
    evidence = (SOURCE_BASE, PROTECTED.copy())
    positive = current.copy()
    # Require the approved delta in the actual working source, not just a fixture.
    verify_companion_delta(positive, evidence)
    # A shallow CI checkout needs no baseline fetch. The explicit
    # --verify-source-baseline procedure independently recomputes this receipt
    # from the exact Git object and fails if that object is unavailable.
    cases = []

    def add(name, path, data, code, detector, mode='100644'):
        changed = positive.copy()
        changed[path] = (mode, data)
        require(changed != positive, 'ineffective fixture: ' + name)
        cases.append((name, changed, evidence, code, detector))

    def change(name, path, old, new, code, detector):
        data = positive[path][1]
        require(data.count(old) == 1, 'unique fixture anchor: ' + name)
        add(name, path, data.replace(old, new), code, detector)

    for name, old, new in (
        ('missing-setting', METADATA_LINES, b''),
        ('duplicate-setting', METADATA_LINES, METADATA_LINES * 2),
        ('true-setting', b'includeInApk = false', b'includeInApk = true'),
        ('bundle-opt-out', b'includeInApk = false', b'includeInApk = false\n        includeInBundle = false'),
        ('enable-debug', b'variant.enable = false', b'variant.enable = true'),
        ('compile-api', b'compileSdk 37', b'compileSdk 36'),
        ('minimum-api', b'minSdk 37', b'minSdk 36'),
        ('target-api', b'targetSdk 37', b'targetSdk 36'),
        ('namespace', b"namespace 'org.pdva.memorydiagnostic'", b"namespace 'org.pdva.other'"),
        ('identity', b"applicationId 'org.pdva.memorydiagnostic'", b"applicationId 'org.pdva.other'"),
        ('version-code', b'versionCode 1', b'versionCode 2'),
        ('version-name', b"versionName '0.1-diagnostic'", b"versionName 'production'"),
        ('debuggable-release', b'debuggable false', b'debuggable true'),
        ('minified-release', b'minifyEnabled false', b'minifyEnabled true'),
        ('signed-release', b'release { signingConfig null;', b'release { signingConfig signingConfigs.debug;'),
        ('signed-debug', b'debug { signingConfig null }', b'debug { signingConfig signingConfigs.debug }'),
        ('build-type', b'    buildTypes {', b'    buildTypes {\n        production {}'),
        ('flavor', b'    defaultConfig {', b'    productFlavors { other {} }\n    defaultConfig {'),
        ('test-apk', b'    defaultConfig {', b'    testBuildType "release"\n    defaultConfig {'),
        ('wrong-dsl-location', b'    compileSdk 37\n' + METADATA_LINES,
         METADATA_LINES + b'    compileSdk 37\n'),
        ('CRLF-drift', b'plugins { id \'com.android.application\' }\n', b'plugins { id \'com.android.application\' }\r\n'),
    ):
        change(name, BUILD_PATH, old, new, 'exact-companion-delta', 'check_metadata_delta')
    for name, extra in (
        ('plugin-hook', b"apply plugin: 'unreviewed'\n"),
        ('packaging-hook', b'afterEvaluate { android.dependenciesInfo.includeInApk = true }\n'),
        ('distribution', b"tasks.register('publishRelease') {}\n"),
        ('dependency', b"dependencies { implementation 'example:unreviewed:1' }\n"),
        ('native-build', b'android { externalNativeBuild { cmake {} } }\n'),
    ):
        add(name, BUILD_PATH, PROPOSED_BUILD + extra, 'exact-companion-delta', 'check_metadata_delta')

    host = 'android/gate0-harness/build.gradle'
    java = 'android/memory-diagnostic/src/main/java/org/pdva/memorydiagnostic/'
    mutations = [
        ('host-opt-out', host, b'android {', b'android {\n' + METADATA_LINES),
        ('root-opt-out', 'android/build.gradle', b'apply false }',
         b'apply false }\nsubprojects { afterEvaluate { android.dependenciesInfo.includeInApk = false } }'),
        ('global-setting', 'android/gradle.properties', b'android.useAndroidX=false',
         b'android.useAndroidX=false\nandroid.dependenciesInfo.includeInApk=false'),
        ('execution-lock', 'android/gate0-harness/src/main/java/org/pdva/gate0/Session.java',
         b'throw new SecurityException("research_execution_disabled");', b'return;'),
        ('close-cleanup', java + 'Experiment.java', b'ops.close();', b''),
        ('rx-cleanup', java + 'Experiment.java', b'ops.unmapRX(size);', b''),
        ('rw-cleanup', java + 'Experiment.java', b'ops.unmapRW(size);', b''),
        ('runtime-api', java + 'Experiment.java', b'ops.api() != 37', b'ops.api() != 36'),
        ('attempt-reset', java + 'Attempt.java', b'consumed = true;\n        try', b'consumed = false;\n        try'),
        ('network', java + 'AndroidOps.java', b'import java.io.FileDescriptor;',
         b'import java.io.FileDescriptor;\nimport java.net.Socket;'),
        ('jni', java + 'AndroidOps.java', b'private FileDescriptor fd;', b'private FileDescriptor fd;\n    native void launch();'),
        ('permission', 'android/memory-diagnostic/src/main/AndroidManifest.xml', b'    <application ',
         b'    <uses-permission android:name="android.permission.INTERNET"/>\n    <application '),
        ('check-skip', '.github/workflows/android-harness.yml', b'  android:\n', b'  android:\n    if: false\n'),
        ('failure-suppression', '.github/workflows/android-harness.yml', b'  android:\n',
         b'  android:\n    continue-on-error: true\n'),
        ('trigger-filter', '.github/workflows/android-harness.yml', b'  pull_request:\n',
         b'  pull_request:\n    branches: [never]\n'),
        ('check-deletion', '.github/workflows/foundation.yml', b'          python3 .github/scripts/test-memory-diagnostic.py\n', b''),
        ('expected-failure-conversion', '.github/workflows/foundation.yml',
         b'          python3 .github/scripts/test-memory-diagnostic.py\n',
         b'          python3 .github/scripts/test-memory-diagnostic.py || true\n'),
        ('passing-wrapper', '.github/workflows/foundation.yml',
         b'          python3 .github/scripts/test-memory-diagnostic.py\n', b'          echo PASS\n'),
    ]
    for name, path, old, new in mutations:
        change(name, path, old, new, 'protected-' + protected_group(path), 'check_protected_source')
    for name, path, data in (
        ('new-native-payload', 'android/memory-diagnostic/src/main/jni/payload.c', b'void payload(void) {}\n'),
        ('new-publish-workflow', '.github/workflows/publish.yml', b'name: unauthorized\n'),
        ('unknown-scope', 'unreviewed.txt', b'unreviewed\n'),
        ('comparator-exclusion', '.github/scripts/unreviewed-comparator.py', b'print("PASS")\n'),
    ):
        add(name, path, data, 'protected-' + protected_group(path), 'check_protected_source')
    for mode in ('100755', '120000', '160000'):
        add('mode-' + mode, BUILD_PATH, PROPOSED_BUILD, 'regular-source-modes', 'check_source_modes', mode)
    for path in (host, 'docs/requirements.md'):
        changed = positive.copy(); del changed[path]
        cases.append(('deleted-' + protected_group(path), changed, evidence,
                      'protected-' + protected_group(path), 'check_protected_source'))
    changed = positive.copy(); del changed[BUILD_PATH]
    cases.append(('missing-module', changed, evidence, 'exact-companion-delta', 'check_metadata_delta'))
    for path in REVIEWED_FILES:
        changed = positive.copy(); del changed[path]
        cases.append(('missing-review-file-' + path, changed, evidence,
                      'reviewed-file-inventory', 'check_review_scope'))
    for name, bad_evidence in (('missing-baseline', None), ('wrong-baseline', ('unknown', PROTECTED)),
                               ('incomplete-baseline', (SOURCE_BASE, {}))):
        cases.append((name, positive, bad_evidence, 'baseline-evidence', 'check_baseline'))

    mutants = {detector: detector_removed(detector) for *_, detector in cases}
    for mutant in mutants.values():
        mutant(positive, evidence)
    for name, snapshot, receipt, code, detector in cases:
        expect_source_rejection(verify_companion_delta, snapshot, receipt, code, name)
        # The same defective input must now be admitted, and its negative
        # assertion must fail specifically because it was accepted. Any other
        # exception, wrong detector, parse/compile error or timeout fails the run.
        mutant = mutants[detector]
        mutant(snapshot, receipt)
        try:
            expect_source_rejection(mutant, snapshot, receipt, code, name)
        except AssertionError as failure:
            require(type(failure) is AssertionError and str(failure) == 'negative accepted: ' + name,
                    'wrong detector-removal outcome: ' + name)
        else:
            raise AssertionError('ineffective detector-removal assertion: ' + name)
    print(f'PASS: exact active companion delta; {len(cases)} specific negatives; '
          f'{len(cases)} detector-removal assertion failures ({len(mutants)} detector bodies)')
    source_cli_tests(positive)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def manifest_policy(root, packaged=False):
    require(root.tag == 'manifest', 'manifest root')
    require(NS + 'sharedUserId' not in root.attrib, 'no shared identity')
    require(set(child.tag for child in root) <= {'application', 'uses-sdk'}, 'no permissions/components')
    apps = root.findall('application')
    require(len(apps) == 1, 'one application')
    app = apps[0]
    require(app.get(NS + 'debuggable', 'false') == 'false'
            and app.get(NS + 'testOnly', 'false') == 'false', 'release-equivalent package')
    require(not any(NS + name in app.attrib for name in ('process', 'persistent', 'sharedUserId', 'manageSpaceActivity')),
            'no extra application authority')
    require(app.get(NS + 'allowBackup') == 'false', 'backup disabled')
    require(app.get(NS + 'usesCleartextTraffic') == 'false', 'cleartext disabled')
    require(app.get(NS + 'fullBackupContent') == 'false', 'full backup disabled')
    require(app.get(NS + 'dataExtractionRules', '').startswith('@'), 'explicit extraction rules')
    require([c.tag for c in app] == ['activity'], 'one Activity only')
    activity = app[0]
    require(activity.get(NS + 'name') in {'.MainActivity', 'org.pdva.memorydiagnostic.MainActivity'}, 'Activity identity')
    require(activity.get(NS + 'exported') == 'true' and NS + 'process' not in activity.attrib, 'ordinary launcher')
    require([c.tag for c in activity] == ['intent-filter'], 'only launcher intent')
    require([(c.tag, c.get(NS + 'name')) for c in activity[0]] == [
        ('action', 'android.intent.action.MAIN'), ('category', 'android.intent.category.LAUNCHER')], 'launcher only')
    if packaged:
        require(root.get('package') == 'org.pdva.memorydiagnostic', 'package identity')
        require(root.get(NS + 'versionCode') == '1' and root.get(NS + 'versionName') == '0.1-diagnostic', 'package version')
        sdk = root.find('uses-sdk')
        require(sdk is not None and sdk.get(NS + 'targetSdkVersion') == '37'
                and sdk.get(NS + 'minSdkVersion') == '37', 'packaged SDK')


def source_policy(adapter=None, manifest=None):
    manifest_policy(ET.fromstring(manifest or (MODULE / 'src/main/AndroidManifest.xml').read_text()))
    texts = {p.name: p.read_text() for p in JAVA.glob('*.java')}
    if adapter is not None:
        texts['AndroidOps.java'] = adapter
    require(set(texts) == {'Experiment.java', 'Attempt.java', 'AndroidOps.java', 'MainActivity.java'}, 'source inventory')
    all_text = '\n'.join(texts.values())
    for forbidden in ('java.net', 'android.net', 'System.load', 'Runtime.getRuntime', 'ProcessBuilder',
                      'Thread(', 'Executor', 'Worker', 'native ', 'reflect', 'Unsafe', 'WebView',
                      'android.util.Log', 'printStackTrace', 'getMessage()', 'MAP_FIXED', 'mprotect'):
        require(forbidden not in all_text, 'prohibited source capability: ' + forbidden)
    adapter = texts['AndroidOps.java']
    calls = re.findall(r'Os\.(\w+)\(', adapter)
    require(calls == ['sysconf', 'memfd_create', 'ftruncate', 'mmap', 'mmap', 'munmap', 'munmap', 'close'], 'exact syscall adapter')
    maps = re.findall(r'Os\.mmap\((.*?)\);', adapter, re.S)
    expected = [f'0, size, OsConstants.PROT_READ | OsConstants.PROT_{kind}, OsConstants.MAP_SHARED, fd, 0'
                for kind in ('WRITE', 'EXEC')]
    require([' '.join(s.split()) for s in maps] == expected, 'bounded split RW/RX mappings')
    require('Os.memfd_create("pdva-diagnostic", OsConstants.MFD_CLOEXEC)' in adapter, 'fixed anonymous allocation')
    require('Os.ftruncate(fd, size)' in adapter, 'one-page backing')
    activity = texts['MainActivity.java']
    require(activity.count('attempt.activate(') == 1 and
            activity.index('setOnClickListener') < activity.index('attempt.activate('), 'explicit initiation')
    require('state != null' in activity and 'button.setEnabled(false)' in activity, 'recreation/repetition guard')
    require('putBoolean("started", true).commit()' in activity, 'synchronous durable marker')
    build = (MODULE / 'build.gradle').read_text()
    require(build.count('signingConfig null') == 2 and 'signingConfigs.' not in build, 'unsigned variants only')
    require("withBuildType('debug')" in build and 'variant.enable = false' in build, 'release-only module')
    require('dependencies {' not in build and 'externalNativeBuild' not in build, 'no native/runtime dependencies')
    files = [p for p in (MODULE / 'src/main').rglob('*') if p.is_file()]
    require(len(files) == 6, 'no payloads/resources beyond reviewed source')
    extraction_policy(ET.parse(MODULE / 'src/main/res/xml/data_extraction_rules.xml').getroot())


def extraction_policy(root):
    require(root.tag == 'data-extraction-rules' and [c.tag for c in root] == ['cloud-backup', 'device-transfer'],
            'backup and transfer rules')
    domains = {'root', 'file', 'database', 'sharedpref', 'external', 'device_root',
               'device_file', 'device_database', 'device_sharedpref'}
    for branch in root:
        require(len(branch) == len(domains) and all(c.tag == 'exclude' and c.get('path') == '.' for c in branch)
                and {c.get('domain') for c in branch} == domains, 'exclude all data domains')


def binary_manifest(data):
    """Decode the packaged Android XML subset; fail closed on unsupported structure."""
    kind, header, size = struct.unpack_from('<HHI', data)
    require(kind == 3 and header == 8 and size == len(data), 'binary XML envelope')
    strings, stack, root = [], [], None
    offset = header
    while offset < size:
        kind, head, length = struct.unpack_from('<HHI', data, offset)
        require(length >= head >= 8 and offset + length <= size, 'XML chunk bounds')
        if kind == 1:
            count, styles, flags, start, _ = struct.unpack_from('<IIIII', data, offset + 8)
            require(count < 4096 and styles == 0, 'bounded XML strings')
            def read_length(pos, utf8):
                unit = 1 if utf8 else 2
                value = int.from_bytes(data[pos:pos + unit], 'little'); pos += unit
                mask = 0x80 if utf8 else 0x8000
                if value & mask:
                    value = ((value & (mask - 1)) << (8 * unit)) | int.from_bytes(data[pos:pos + unit], 'little')
                    pos += unit
                return value, pos
            for index in range(count):
                position = offset + start + struct.unpack_from('<I', data, offset + head + 4 * index)[0]
                utf8 = bool(flags & 0x100)
                length_chars, position = read_length(position, utf8)
                if utf8:
                    count_bytes, position = read_length(position, True)
                else:
                    count_bytes = length_chars * 2
                require(position + count_bytes <= offset + length, 'string bounds')
                strings.append(data[position:position + count_bytes].decode('utf-8' if utf8 else 'utf-16le'))
        elif kind == 0x102:
            ns, name, attr_start, attr_size, count = struct.unpack_from('<IIHHH', data, offset + 16)
            require(attr_size == 20 and count < 128, 'attribute bounds')
            element = ET.Element(strings[name])
            for i in range(count):
                pos = offset + 16 + attr_start + i * attr_size
                require(pos + 20 <= offset + length, 'attribute extent')
                ans, aname, raw, _, _, value_type, value = struct.unpack_from('<IIIHBBI', data, pos)
                key = ('' if ans == 0xffffffff else '{' + strings[ans] + '}') + strings[aname]
                if raw != 0xffffffff:
                    text = strings[raw]
                elif value_type == 3:
                    text = strings[value]
                elif value_type == 0x12:
                    text = 'true' if value else 'false'
                elif value_type in (0x10, 0x11):
                    text = str(value)
                elif value_type == 1:
                    text = '@' + str(value)
                else:
                    raise AssertionError('unsupported attribute value')
                require(key not in element.attrib, 'duplicate attribute')
                element.set(key, text)
            if stack:
                stack[-1].append(element)
            else:
                require(root is None, 'one XML root'); root = element
            stack.append(element)
        elif kind == 0x103:
            require(stack and stack[-1].tag == strings[struct.unpack_from('<I', data, offset + 20)[0]], 'balanced XML')
            stack.pop()
        else:
            require(kind in (0x100, 0x101, 0x180), 'unsupported XML chunk')
        offset += length
    require(root is not None and not stack, 'complete XML')
    return root


def unsigned_metadata_policy(data, archive):
    # Dependency information is an APK signing-block pair, not a ZIP member.
    # No signing block is allowed in this explicitly unsigned development output.
    require(data[archive.start_dir - 16:archive.start_dir] != b'APK Sig Block 42',
            'no APK signing block')
    require(not any(n.startswith('BUNDLE-METADATA/com.android.tools.build.libraries/')
                    or n.rsplit('/', 1)[-1] in ('sdkDependencyData.pb', 'dependencies.pb')
                    for n in archive.namelist()), 'no packaged dependency metadata')


def metadata_outputs_policy(build):
    # Stale outputs are a failure too: use a fresh build directory, never delete
    # evidence to make this check pass. The ordinary dependency report may exist;
    # it is NOT the encrypted SDK payload or evidence of signing-block insertion.
    for relative in ('intermediates/sdk_dependency_data', 'outputs/sdk-dependencies'):
        require(not os.path.lexists(build / relative), 'no generated SDK dependency payload/report')


def metadata_package_tests():
    def check(data):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            unsigned_metadata_policy(data, archive)

    def fixture(name):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr(name, b'fixture')
        return stream.getvalue()

    plain = fixture('classes.dex')
    check(plain)
    # Synthetic block marker placed before the central directory, with its ZIP
    # offset updated. No real APK is modified; no signature validity is claimed.
    with zipfile.ZipFile(io.BytesIO(plain)) as archive:
        start = archive.start_dir
    blocked = bytearray(plain[:start] + b'APK Sig Block 42' + plain[start:])
    struct.pack_into('<I', blocked, len(blocked) - 6, start + 16)
    cases = [(blocked, 'no APK signing block')]
    cases += [(fixture(name), 'no packaged dependency metadata') for name in (
        'sdkDependencyData.pb', 'dependencies.pb',
        'BUNDLE-METADATA/com.android.tools.build.libraries/other.pb')]
    for data, reason in cases:
        try:
            check(data)
        except AssertionError as failure:
            require(str(failure) == reason, 'specific unsigned metadata rejection')
        else:
            raise AssertionError('unsigned metadata negative accepted')
    with tempfile.TemporaryDirectory(prefix='pdva-metadata-fixture-') as temp:
        root = Path(temp)
        metadata_outputs_policy(root)
        report = root / 'intermediates/metadata_library_dependencies_report/release/dependencies.pb'
        report.parent.mkdir(parents=True)
        report.write_bytes(b'ordinary-report-fixture')
        metadata_outputs_policy(root)
        for index, relative in enumerate(('intermediates/sdk_dependency_data', 'outputs/sdk-dependencies')):
            build = root / str(index)
            (build / relative).mkdir(parents=True)
            try:
                metadata_outputs_policy(build)
            except AssertionError as failure:
                require(str(failure) == 'no generated SDK dependency payload/report',
                        'specific intermediate rejection')
            else:
                raise AssertionError('SDK output negative accepted')
    print('PASS: unsigned metadata fixtures; 6 specific negatives; ordinary report allowed (not APK evidence)')


def package_policy(apk):
    data = apk.read_bytes()
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'unique ZIP entries')
        require(not any(n.startswith(('lib/', 'assets/')) or n.lower().endswith(('.so', '.rsa', '.dsa', '.ec', '.sf'))
                        for n in names), 'no native payloads/assets/v1 signatures')
        unsigned_metadata_policy(data, archive)
        manifest_policy(binary_manifest(archive.read('AndroidManifest.xml')), packaged=True)
        # AAPT2 shortens resource ZIP paths in release packages. Inspect the sole
        # compiled XML resource without rewriting or normalizing any APK bytes.
        resources = [n for n in names if n.startswith('res/') and n.endswith('.xml')]
        require(len(resources) == 1, 'one compiled extraction-rules resource')
        extraction_policy(binary_manifest(archive.read(resources[0])))
        dex = [archive.read(n) for n in names if re.fullmatch(r'classes\d*\.dex', n)]
        require(dex, 'packaged DEX exists')
        for content in dex:
            for forbidden in (b'Ljava/net/', b'Landroid/net/', b'Ljava/lang/ProcessBuilder;',
                              b'Ljava/lang/Runtime;', b'Ljava/lang/reflect/', b'Ldalvik/system/DexClassLoader;'):
                require(forbidden not in content, 'prohibited DEX reference')
    require(tuple(apk.parts[-4:]) == ('outputs', 'apk', 'release',
                                    'memory-diagnostic-release-unsigned.apk'), 'diagnostic output location')
    metadata_outputs_policy(apk.parents[3])
    require(apk.read_bytes() == data, 'package unchanged during inspection')
    print('PASS: unsigned package manifest/DEX/native/signature inventory; no SDK dependency outputs '
          '(not signed-stage proof or qualification)')


def jvm_tests(java_home, android_jar):
    suffix = '.exe' if os.name == 'nt' else ''
    def tool(name):
        return str(java_home / 'bin' / (name + suffix))
    sources = [JAVA / 'Experiment.java', JAVA / 'Attempt.java',
               MODULE / 'src/test/java/org/pdva/memorydiagnostic/ExperimentTest.java']
    with tempfile.TemporaryDirectory(prefix='pdva-memory-') as temp:
        work = Path(temp)
        def compile_java(arguments):
            result = subprocess.run([tool('javac'), *arguments], capture_output=True, text=True, check=True, timeout=60)
            require(not result.stderr and not result.stdout, 'clean compiler completion')
        compile_java(['-d', str(work), *map(str, sources)])
        result = subprocess.run([tool('java'), '-cp', str(work), 'org.pdva.memorydiagnostic.ExperimentTest'],
                                capture_output=True, text=True, check=True, timeout=30)
        require(result.stdout.startswith('PASS: ') and not result.stderr, 'JVM complete receipt')
        print(result.stdout.strip())
        # Compile a real cleanup-removal mutant; reject at a behavioral assertion,
        # not because compilation, startup or a timeout happened to fail.
        mutant = work / 'Experiment.java'
        original = sources[0].read_text()
        require(original.count('ops.close();') == 1, 'mutation anchor')
        mutant.write_text(original.replace('ops.close();', ''), encoding='utf-8')
        compile_java(['-d', str(work), str(mutant), *map(str, sources[1:])])
        result = subprocess.run([tool('java'), '-cp', str(work), 'org.pdva.memorydiagnostic.ExperimentTest'],
                                capture_output=True, text=True, timeout=30)
        require(result.returncode == 1 and 'AssertionError: exact bounded sequence' in result.stderr,
                'cleanup-removal mutant must fail expected assertion')
        print('PASS: compiled cleanup-removal mutant rejected')
        activity_fixture(work, tool, compile_java)
        if android_jar:
            compile_java(['-classpath', str(android_jar), '-d', str(work / 'sdk-classes'),
                          *map(str, JAVA.glob('*.java'))])
            print('PASS: all application Java compiles against Android SDK (no runtime execution)')


def activity_fixture(work, tool, compile_java):
    # Execute the actual Activity bytecode against tiny deterministic desktop
    # framework doubles. These are intentionally NOT Android lifecycle evidence.
    fixtures = {
        'android/os/Bundle.java': 'package android.os; public class Bundle {}',
        'android/content/SharedPreferences.java': '''package android.content;
public class SharedPreferences {
 public static boolean started;
 public boolean getBoolean(String key, boolean fallback) { return started; }
 public SharedPreferences edit() { return this; }
 public SharedPreferences putBoolean(String key, boolean value) { return this; }
 public boolean commit() { started = true; return true; }
}''',
        'android/app/Activity.java': '''package android.app;
public class Activity {
 public static final int MODE_PRIVATE = 0;
 public void onCreate(android.os.Bundle state) {}
 public android.content.SharedPreferences getSharedPreferences(String name, int mode) {
  return new android.content.SharedPreferences();
 }
 public void setContentView(android.view.View view) {}
}''',
        'android/view/View.java': '''package android.view;
public class View {
 public interface OnClickListener { void onClick(View v); }
 public interface OnApplyWindowInsetsListener { WindowInsets onApplyWindowInsets(View v, WindowInsets i); }
 public void setPadding(int a, int b, int c, int d) {}
 public void setOnApplyWindowInsetsListener(OnApplyWindowInsetsListener listener) {}
}''',
        'android/graphics/Insets.java': '''package android.graphics;
public class Insets { public int left, top, right, bottom; }''',
        'android/view/WindowInsets.java': '''package android.view;
public class WindowInsets {
 public static class Type {
  public static int systemBars() { return 1; }
  public static int displayCutout() { return 2; }
 }
 public android.graphics.Insets getInsets(int type) { return new android.graphics.Insets(); }
}''',
        'android/widget/ScrollView.java': '''package android.widget;
public class ScrollView extends android.view.View {
 public ScrollView(android.app.Activity context) {}
 public void addView(LinearLayout layout) {}
}''',
        'android/widget/TextView.java': '''package android.widget;
public class TextView extends android.view.View {
 public String text;
 public TextView(android.app.Activity context) {}
 public void setText(String value) { text = value; }
}''',
        'android/widget/Button.java': '''package android.widget;
public class Button extends TextView {
 public static Button last;
 public boolean enabled;
 public android.view.View.OnClickListener listener;
 public Button(android.app.Activity context) { super(context); last = this; }
 public void setEnabled(boolean value) { enabled = value; }
 public void setOnClickListener(android.view.View.OnClickListener value) { listener = value; }
}''',
        'android/widget/LinearLayout.java': '''package android.widget;
public class LinearLayout extends android.view.View {
 public static final int VERTICAL = 1;
 public static java.util.List<TextView> children;
 public LinearLayout(android.app.Activity context) { children = new java.util.ArrayList<>(); }
 public void setOrientation(int value) {}
 public void setPadding(int a, int b, int c, int d) {}
 public void addView(TextView view) { children.add(view); }
}''',
        'org/pdva/memorydiagnostic/AndroidOps.java': '''package org.pdva.memorydiagnostic;
final class AndroidOps implements Experiment.Ops {
 static int creates;
 public int api() { return 37; }
 public boolean arm64() { return true; }
 public boolean bit64() { return true; }
 public long pageSize() { return 4096; }
 public void create() {
  if (!android.content.SharedPreferences.started) throw new AssertionError("marker precedes acquisition");
  creates++;
 }
 public void resize(long size) {}
 public void mapRW(long size) {}
 public void mapRX(long size) {}
 public void unmapRX(long size) {}
 public void unmapRW(long size) {}
 public void close() {}
}''',
        'org/pdva/memorydiagnostic/ActivityTest.java': '''package org.pdva.memorydiagnostic;
import android.widget.Button;
import android.widget.LinearLayout;
public class ActivityTest {
 static void check(boolean ok) { if (!ok) throw new AssertionError("Activity control"); }
 public static void main(String[] args) {
  new MainActivity().onCreate(null);
  check(AndroidOps.creates == 0 && Button.last.enabled);
  Button first = Button.last;
  first.listener.onClick(first);
  check(AndroidOps.creates == 1 && !first.enabled);
  check(LinearLayout.children.get(2).text.startsWith("Result=Admitted"));
  first.listener.onClick(first);
  check(AndroidOps.creates == 1);
  new MainActivity().onCreate(new android.os.Bundle());
  check(AndroidOps.creates == 1 && !Button.last.enabled);
  check(LinearLayout.children.get(2).text.startsWith("Result=Unknown"));
  new MainActivity().onCreate(null);
  check(!Button.last.enabled && AndroidOps.creates == 1);
  android.content.SharedPreferences.started = false;
  new MainActivity().onCreate(new android.os.Bundle());
  check(!Button.last.enabled && AndroidOps.creates == 1);
  System.out.println("PASS: actual Activity initiation/recreation bytecode with desktop framework doubles");
 }
}''',
    }
    paths = []
    for name, content in fixtures.items():
        path = work / 'activity-fixture' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        paths.append(str(path))
    classes = work / 'activity-classes'
    compile_java(['-d', str(classes), *paths, *map(str, [JAVA / 'Experiment.java', JAVA / 'Attempt.java', JAVA / 'MainActivity.java'])])
    result = subprocess.run([tool('java'), '-cp', str(classes), 'org.pdva.memorydiagnostic.ActivityTest'],
                            check=True, capture_output=True, text=True, timeout=30)
    require(result.stdout.startswith('PASS: actual Activity') and not result.stderr, 'Activity receipt')
    print(result.stdout.strip())


class QualificationRejection(ValueError):
    """Stable public reason only; never include private paths, bytes or receipts."""


QUALIFICATION_EXPIRES = 1796688000  # 2026-12-08 00:00 UTC; earlier stop conditions still apply


def qualification_require(condition, code):
    if not condition:
        raise QualificationRejection(code)


class SigningFields:
    """Re-reviewed historical PDVA framing; independent approval remains required."""
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, size):
        qualification_require(0 <= size <= len(self.data) - self.pos, 'signing-field-bounds')
        value = self.data[self.pos:self.pos + size]
        self.pos += size
        return value

    def number(self, size=4):
        return int.from_bytes(self.take(size), 'little')

    def field(self):
        return self.take(self.number())

    def end(self):
        qualification_require(self.pos == len(self.data), 'signing-trailing-field')


def signed_v2(value):
    outer = SigningFields(value)
    sequence = SigningFields(outer.field()); outer.end()
    signer = SigningFields(sequence.field()); sequence.end()  # exactly one signer
    signed = SigningFields(signer.field())
    signatures, key = signer.field(), signer.field(); signer.end()
    digests, certificates, attributes = signed.field(), signed.field(), signed.field()
    # No undocumented extensions, rotation, attributes or extra certificates.
    signed.end()
    qualification_require(key and not attributes, 'unsupported-v2-attributes-or-key')
    certs = SigningFields(certificates)
    certificate = certs.field(); certs.end()
    qualification_require(certificate, 'missing-v2-certificate')

    def algorithms(raw, digest=False):
        fields, seen = SigningFields(raw), []
        while fields.pos < len(raw):
            record = SigningFields(fields.field())
            algorithm, payload = record.number(), record.field(); record.end()
            qualification_require(algorithm not in seen, 'duplicate-signature-algorithm')
            qualification_require(algorithm in (0x0103, 0x0201) and payload
                                  and (not digest or len(payload) == 32), 'unsupported-signature-algorithm')
            seen.append(algorithm)
        qualification_require(seen, 'missing-signature-algorithm')
        return seen

    qualification_require(algorithms(digests, True) == algorithms(signatures), 'signature-algorithm-mismatch')
    return hashlib.sha256(certificate).hexdigest()  # identity only, NOT verification


def signed_block(raw):
    qualification_require(32 <= len(raw) <= 4 * 1024 * 1024
                          and raw[-16:] == b'APK Sig Block 42', 'signing-envelope')
    qualification_require(int.from_bytes(raw[:8], 'little') ==
                          int.from_bytes(raw[-24:-16], 'little') == len(raw) - 8, 'signing-size')
    fields, seen, certificate = SigningFields(raw[8:-24]), set(), None
    while fields.pos < len(fields.data):
        pair = SigningFields(fields.take(fields.number(8)))
        identifier = pair.number()
        qualification_require(identifier not in seen, 'duplicate-signing-pair')
        seen.add(identifier)
        qualification_require(identifier != 0x504b4453, 'dependency-metadata-pair')
        qualification_require(identifier in (0x7109871a, 0x42726577), 'unsupported-signing-pair')
        value = pair.take(len(pair.data) - pair.pos)
        if identifier == 0x7109871a:
            certificate = signed_v2(value)
        else:
            qualification_require(not any(value), 'nonzero-signing-padding')
    qualification_require(certificate is not None, 'missing-v2-pair')
    return certificate


def signed_zip(raw):
    """Conservative non-ZIP64 profile; original bytes are never rewritten."""
    qualification_require(22 <= len(raw) <= 32 * 1024 * 1024, 'apk-size')
    # No ZIP comment, trailing data, multi-disk, ZIP64, prefixes or hidden records.
    end = len(raw) - 22
    qualification_require(raw[end:end + 4] == b'PK\x05\x06', 'zip-eocd')
    disk, cd_disk, count_disk, count, size, central, comment = struct.unpack_from('<4H2IH', raw, end + 4)
    qualification_require(disk == cd_disk == comment == 0 and 0 < count == count_disk <= 128
                          and central + size == end and central >= 32, 'zip-layout')
    block_size = int.from_bytes(raw[central - 24:central - 16], 'little')
    qualification_require(24 <= block_size <= min(4 * 1024 * 1024 - 8, central - 8), 'signing-block-bounds')
    start = central - block_size - 8
    certificate = signed_block(raw[start:central])
    local, cursor, payloads = 0, central, {}

    def extras(data):
        fields, seen = SigningFields(data), set()
        while fields.pos < len(data):
            identifier, length = fields.number(2), fields.number(2)
            value = fields.take(length)
            qualification_require(identifier not in seen, 'duplicate-zip-extra')
            seen.add(identifier)
            qualification_require(identifier == 0xd935 and len(value) >= 2
                                  and int.from_bytes(value[:2], 'little') in (4, 4096, 16384)
                                  and not any(value[2:]), 'unsupported-zip-extra')

    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = archive.infolist()
            qualification_require(len(entries) == count and archive.start_dir == central, 'zip-inventory')
            total = 0
            for entry in entries:
                qualification_require(cursor + 46 <= end and raw[cursor:cursor + 4] == b'PK\x01\x02', 'central-header')
                name_len, extra_len, comment_len = struct.unpack_from('<3H', raw, cursor + 28)
                next_cursor = cursor + 46 + name_len + extra_len + comment_len
                qualification_require(next_cursor <= end and not comment_len, 'central-extent')
                name = raw[cursor + 46:cursor + 46 + name_len]
                qualification_require(re.fullmatch(rb'[A-Za-z0-9_./-]+', name) is not None
                                      and all(p not in ('', '.', '..') for p in entry.filename.split('/'))
                                      and entry.filename.encode('ascii') == name, 'zip-name')
                qualification_require(entry.filename not in payloads, 'duplicate-zip-name')
                qualification_require(entry.flag_bits in (0, 0x800) and entry.compress_type in (0, 8)
                                      and entry.extract_version <= 20 and entry.volume == 0
                                      and entry.file_size <= 8 * 1024 * 1024
                                      and entry.header_offset == local
                                      and (entry.external_attr >> 16) & 0o170000 in (0, stat.S_IFREG),
                                      'unsupported-zip-entry')
                total += entry.file_size
                qualification_require(total <= 16 * 1024 * 1024, 'zip-expanded-size')
                qualification_require(local + 30 <= start and raw[local:local + 4] == b'PK\x03\x04', 'local-header')
                version, flags, method, stamp, date, crc, compressed, expanded, nl, el = struct.unpack_from(
                    '<5H3I2H', raw, local + 4)
                header_end = local + 30 + nl + el
                qualification_require(header_end + compressed <= start and
                                      (version, flags, method, crc, compressed, expanded, nl) ==
                                      (entry.extract_version, entry.flag_bits, entry.compress_type,
                                       entry.CRC, entry.compress_size, entry.file_size, name_len)
                                      and raw[local + 10:local + 14] == raw[cursor + 12:cursor + 16]
                                      and raw[local + 30:local + 30 + nl] == name, 'local-central-mismatch')
                extras(raw[local + 30 + nl:header_end]); extras(entry.extra)
                compressed_bytes = raw[header_end:header_end + compressed]
                if method == 0:
                    qualification_require(compressed == expanded, 'stored-zip-size')
                else:
                    decoder = zlib.decompressobj(-15)
                    decoded = decoder.decompress(compressed_bytes, expanded + 1)
                    qualification_require(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
                                          and len(decoded) == expanded, 'deflate-extent')
                payloads[entry.filename] = archive.read(entry)  # includes CRC verification
                local, cursor = header_end + compressed, next_cursor
            qualification_require(local == start and cursor == end, 'zip-hidden-records')
    except (zipfile.BadZipFile, NotImplementedError, UnicodeError, RuntimeError, zlib.error):
        raise QualificationRejection('zip-decode') from None
    return payloads, certificate


def signed_package(payloads):
    names = set(payloads)
    required = {'AndroidManifest.xml', 'classes.dex', 'resources.arsc'}
    optional = {'META-INF/com/android/build/gradle/app-metadata.properties', 'META-INF/version-control-info.textproto'}
    xmls = {n for n in names if re.fullmatch(r'res/[A-Za-z0-9_-]+\.xml', n)}
    qualification_require(required <= names and len(xmls) == 1 and names <= required | optional | xmls,
                          'signed-package-inventory')
    try:
        manifest = binary_manifest(payloads['AndroidManifest.xml'])
        qualification_require(len(manifest.findall('uses-sdk')) == 1, 'signed-package-sdk-count')
        manifest_policy(manifest, packaged=True)
        extraction_policy(binary_manifest(payloads[next(iter(xmls))]))
    except (AssertionError, IndexError, struct.error, UnicodeError):
        raise QualificationRejection('signed-package-policy') from None
    qualification_require(payloads['classes.dex'].startswith(b'dex\n'), 'signed-package-dex')
    # This is a policy screen; authenticated source/build correspondence remains
    # mandatory for DEX semantics and the unchanged one-attempt boundary.
    for forbidden in (b'Ljava/net/', b'Landroid/net/', b'Ljava/lang/ProcessBuilder;',
                      b'Ljava/lang/Runtime;', b'Ljava/lang/reflect/', b'Ldalvik/system/DexClassLoader;'):
        qualification_require(forbidden not in payloads['classes.dex'], 'signed-package-capability')


def original_snapshot(path):
    path = Path(path)
    qualification_require(not any(p.is_symlink() or getattr(p.lstat(), 'st_file_attributes', 0) & 0x400
                                  for p in (path, *path.parents)), 'artifact-alias')
    qualification_require(stat.S_ISREG(path.lstat().st_mode), 'artifact-type-size')
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        before = os.fstat(stream.fileno())
        qualification_require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= 32 * 1024 * 1024,
                              'artifact-type-size')
        raw = stream.read(32 * 1024 * 1024 + 1)
        after = os.fstat(stream.fileno())
    # CPython 3.12 Windows stat/fstat expose different ctime semantics. Compare
    # ctime only within the open handle; retain portable file ID/mtime plus bytes.
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
    qualification_require(identity(before) == identity(after) == identity(path.stat())
                          and before.st_ctime_ns == after.st_ctime_ns
                          and len(raw) == before.st_size, 'artifact-changed')
    return identity(before), raw


def exact_original_bytes(left, right):
    qualification_require(left == right, 'original-bytes-differ')


def original_pair(paths):
    qualification_require(len(paths) == 2, 'original-pair-count')
    snapshots = [original_snapshot(p) for p in paths]
    qualification_require(snapshots[0][0][:2] != snapshots[1][0][:2], 'same-original-file')
    exact_original_bytes(snapshots[0][1], snapshots[1][1])
    return snapshots


def unchanged_originals(paths, snapshots):
    qualification_require([original_snapshot(p) for p in paths] == snapshots, 'artifact-replaced')


def receipt_consistency(receipts, raw, source, now):
    """Reject contradictions; well-formed claims are NOT authenticated evidence."""
    qualification_require(type(receipts) is list and len(receipts) == 2, 'missing-build-receipts')
    fields = {'build', 'checkout', 'outputs', 'dependency_home', 'retained', 'execution', 'operator',
              'source', 'apk', 'inputs', 'tools', 'signer', 'started', 'finished', 'expires', 'fresh', 'copied'}
    for row in receipts:
        qualification_require(type(row) is dict and set(row) == fields, 'build-receipt-schema')
        qualification_require(all(type(row[k]) is str and re.fullmatch('[0-9a-f]{64}', row[k])
                                  for k in fields - {'started', 'finished', 'expires', 'fresh', 'copied'}),
                              'build-receipt-identity')
        qualification_require(all(type(row[k]) is int for k in ('started', 'finished', 'expires'))
                              and 0 < row['started'] < row['finished'] <= now < row['expires']
                              <= QUALIFICATION_EXPIRES, 'build-receipt-time')
        qualification_require(row['fresh'] is True and row['copied'] is False, 'build-receipt-freshness')
        qualification_require(row['source'] == source and row['apk'] == hashlib.sha256(raw).hexdigest(),
                              'build-receipt-correspondence')
    for key in ('build', 'checkout', 'outputs', 'dependency_home', 'retained', 'execution', 'operator'):
        qualification_require(receipts[0][key] != receipts[1][key], 'build-receipt-independence')
    for key in ('source', 'inputs', 'tools', 'signer'):
        qualification_require(receipts[0][key] == receipts[1][key], 'build-receipt-inputs')


def qualified_authority(receipts):
    """No independent authority/receipt authentication is available in this repo.

    Deliberately no CLI trust hash, environment bypass, boolean approval, fake
    runner or caller-supplied success callback. A separately reviewed integration
    must authenticate the custody, administration, tool and fresh-build packet
    before this boundary can return an authorized signer and SDK tool command.
    Never replace this with acceptance of receipt_consistency alone.
    """
    raise QualificationRejection('independent-qualification-authority-unavailable')


def read_build_receipts(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            qualification_require(key not in result, 'duplicate-receipt-field')
            result[key] = value
        return result
    with Path(path).open('rb') as stream:
        data = stream.read(65537)
    qualification_require(len(data) <= 65536, 'receipt-size')
    try:
        return json.loads(data, object_pairs_hook=unique)
    except (UnicodeError, json.JSONDecodeError):
        raise QualificationRejection('receipt-json') from None


def verified_signature_output(result, expected):
    """Parse SDK verification output; calling this on fixture text proves no signature."""
    qualification_require(result.returncode == 0 and not result.stderr and result.stdout.startswith('Verifies\n'),
                          'signature-verification-failed')
    text = result.stdout
    schemes = re.findall(r'^Verified using (v[0-9.]+) scheme .*: (true|false)$', text, re.M)
    qualification_require(len(schemes) == 5 and dict(schemes) ==
                          {'v1': 'false', 'v2': 'true', 'v3': 'false', 'v3.1': 'false', 'v4': 'false'},
                          'unsupported-verified-schemes')
    certs = re.findall(r'^Signer #1 certificate SHA-256 digest: ([0-9a-f]{64})$', text, re.M)
    qualification_require(certs == [expected] and text.count('certificate SHA-256 digest:') == 1
                          and re.findall(r'^Number of signers: (.+)$', text, re.M) == ['1'], 'unauthorized-signer')
    qualification_require('WARNING' not in text and 'DOES NOT VERIFY' not in text, 'signature-warning')


def qualification_source_identity(snapshot):
    return hashlib.sha256(b''.join(
        len(part).to_bytes(8, 'big') + part
        for path, (mode, blob) in sorted(snapshot.items()) for part in (path.encode(), mode.encode(), blob)
    )).hexdigest()


def qualify_signed_pair(paths, receipts=None):
    """Read-only staged verifier. There is currently NO successful admission path."""
    snapshot = working_source()
    verify_companion_delta(snapshot, (SOURCE_BASE, PROTECTED.copy()))
    originals = original_pair(paths)
    certificates = []
    for _, raw in originals:
        payloads, certificate = signed_zip(raw)
        signed_package(payloads)
        certificates.append(certificate)
    source = qualification_source_identity(snapshot)
    receipt_consistency(receipts, originals[0][1], source, int(time.time()))
    authority = qualified_authority(receipts)  # STOP until independent authentication exists
    # Integration contract for a future reviewed authority, not an active trust
    # configuration. command must be an authenticated absolute SDK/JDK invocation
    # with a qualified, sanitized process environment (no ambient JVM injections).
    for path, certificate in zip(paths, certificates):
        qualification_require(certificate == authority['signer'], 'unauthorized-signer')
        result = subprocess.run([*authority['command'], 'verify', '--verbose', '--print-certs',
                                 '--min-sdk-version', '37', '--max-sdk-version', '37', '-Werr', str(Path(path).resolve())],
                                capture_output=True, text=True, timeout=60, env=authority['environment'], check=False)
        verified_signature_output(result, authority['signer'])
    unchanged_originals(paths, originals)
    qualification_require(working_source() == snapshot, 'qualification-source-changed')
    # Even a future adapter must explicitly add and review final admission;
    # removing the unavailable-authority detector alone cannot qualify artifacts.
    raise QualificationRejection('final-admission-not-implemented')


def signed_qualification_tests():
    """Disposable synthetic bytes ONLY: no keys, signing, APK execution or admission."""
    import copy
    from types import SimpleNamespace
    cases = []
    require(time.gmtime(QUALIFICATION_EXPIRES)[:6] == (2026, 12, 8, 0, 0, 0), 'fixed qualification expiration')

    def negative(function, arguments, code):
        cases.append((function, arguments, code))

    def rejected(function, arguments, code):
        try:
            function(*arguments)
        except QualificationRejection as failure:
            require(str(failure) == code, 'wrong qualification rejection: ' + code)
        else:
            raise AssertionError('qualification negative accepted: ' + code)

    def field(raw):
        return struct.pack('<I', len(raw)) + raw

    def v2(algorithm=0x0103, attributes=b'', duplicate=False):
        digest = field(struct.pack('<I', algorithm) + field(bytes(32)))
        signature = field(struct.pack('<I', algorithm) + field(b'SYNTHETIC-NOT-A-SIGNATURE'))
        data = field(digest * (2 if duplicate else 1)) + field(field(b'SYNTHETIC-NOT-A-CERTIFICATE')) + field(attributes)
        return field(field(field(data) + field(signature) + field(b'SYNTHETIC-NOT-A-KEY')))

    def block(pairs=None):
        if pairs is None:
            pairs = [(0x7109871a, v2())]
        data = b''.join(struct.pack('<QI', len(value) + 4, identifier) + value for identifier, value in pairs)
        size = struct.pack('<Q', len(data) + 24)
        return size + data + size + b'APK Sig Block 42'

    def xml(root):
        # Minimal string-valued binary XML fixture. Never compiled or installable.
        strings = []
        def index(value):
            if value not in strings:
                strings.append(value)
            return strings.index(value)
        def chunk(kind, body):
            return struct.pack('<HHI', kind, 16, 16 + len(body)) + bytes(8) + body
        def node(element):
            attrs = []
            for key, value in element.attrib.items():
                ns = index(NS[1:-1]) if key.startswith(NS) else 0xffffffff
                key = key[len(NS):] if key.startswith(NS) else key
                attrs.append(struct.pack('<IIIHBBI', ns, index(key), index(value), 8, 0, 3, index(value)))
            name = index(element.tag)
            begin = chunk(0x102, struct.pack('<II6H', 0xffffffff, name, 20, 20, len(attrs), 0, 0, 0) + b''.join(attrs))
            return begin + b''.join(node(c) for c in element) + chunk(0x103, struct.pack('<II', 0xffffffff, name))
        nodes = node(root)
        pool, offsets = b'', []
        for string in strings:
            encoded = string.encode()
            require(len(encoded) < 128, 'bounded fixture string')
            offsets.append(len(pool)); pool += bytes([len(string), len(encoded)]) + encoded + b'\0'
        start = 28 + 4 * len(strings)
        pool = (struct.pack('<HHI5I', 1, 28, start + len(pool), len(strings), 0, 0x100, start, 0)
                + b''.join(struct.pack('<I', n) for n in offsets) + pool)
        return struct.pack('<HHI', 3, 8, 8 + len(pool) + len(nodes)) + pool + nodes

    manifest = ET.parse(MODULE / 'src/main/AndroidManifest.xml').getroot()
    manifest.set('package', 'org.pdva.memorydiagnostic')
    manifest.set(NS + 'versionCode', '1'); manifest.set(NS + 'versionName', '0.1-diagnostic')
    ET.SubElement(manifest, 'uses-sdk', {NS + 'minSdkVersion': '37', NS + 'targetSdkVersion': '37'})
    payloads = {'AndroidManifest.xml': xml(manifest), 'classes.dex': b'dex\nSYNTHETIC-NOT-DEX',
                'resources.arsc': b'SYNTHETIC-NOT-RESOURCES',
                'res/policy.xml': xml(ET.parse(MODULE / 'src/main/res/xml/data_extraction_rules.xml').getroot())}

    def apk(signing=None, timestamp=(2026, 1, 1, 0, 0, 0), compression=0, extra=b''):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            for name, data in payloads.items():
                entry = zipfile.ZipInfo(name, timestamp); entry.compress_type = compression
                entry.extra = extra
                archive.writestr(entry, data)
        raw = stream.getvalue(); central = struct.unpack_from('<I', raw, len(raw) - 6)[0]
        signing = block() if signing is None else signing
        result = bytearray(raw[:central] + signing + raw[central:])
        struct.pack_into('<I', result, len(result) - 6, central + len(signing))
        return bytes(result)

    raw = apk()
    parsed, certificate = signed_zip(raw)
    require(parsed == payloads and certificate == signed_block(block()), 'synthetic structural positive')
    require(signed_zip(apk(compression=8))[0] == payloads, 'synthetic deflate positive')
    signed_package(parsed); exact_original_bytes(raw, bytes(raw))
    for changed in (raw[:-1], raw + b'x', bytes([raw[0] ^ 1]) + raw[1:], apk(timestamp=(2026, 1, 2, 0, 0, 0))):
        negative(exact_original_bytes, (raw, changed), 'original-bytes-differ')
    for changed in (raw[:-1], raw + b'x'):
        negative(signed_zip, (changed,), 'zip-eocd')
    bad = bytearray(raw); struct.pack_into('<H', bad, len(bad) - 18, 1)
    negative(signed_zip, (bytes(bad),), 'zip-layout')
    bad = bytearray(raw); bad[10] ^= 1
    negative(signed_zip, (bytes(bad),), 'local-central-mismatch')
    bad = bytearray(raw); bad[30 + len('AndroidManifest.xml') + 4] ^= 1
    negative(signed_zip, (bytes(bad),), 'zip-decode')
    bad = bytearray(raw); central = struct.unpack_from('<I', bad, len(bad) - 6)[0]
    struct.pack_into('<I', bad, central + 42, 1)
    negative(signed_zip, (bytes(bad),), 'unsupported-zip-entry')
    negative(signed_zip, (apk(extra=struct.pack('<HHH', 0xd935, 2, 4) * 2),), 'duplicate-zip-extra')
    negative(signed_zip, (apk(extra=struct.pack('<HH', 0x9999, 0)),), 'unsupported-zip-extra')
    bad = bytearray(raw); struct.pack_into('<H', bad, central + 8, 1)
    negative(signed_zip, (bytes(bad),), 'unsupported-zip-entry')
    negative(signed_block, (block([(0x7109871a, v2()), (0x504b4453, b'metadata')]),), 'dependency-metadata-pair')
    negative(signed_block, (block([(0x7109871a, v2())] * 2),), 'duplicate-signing-pair')
    negative(signed_block, (block([(0xf05368c0, b'unsupported')]),), 'unsupported-signing-pair')
    negative(signed_block, (block([(0x42726577, b'x')]),), 'nonzero-signing-padding')
    negative(signed_block, (block([]),), 'missing-v2-pair')
    negative(signed_block, (bytes(8) + block()[8:],), 'signing-size')
    negative(signed_block, (block()[:-1],), 'signing-envelope')
    bad = bytearray(block()); struct.pack_into('<Q', bad, 8, 0xffffffffffffffff)
    negative(signed_block, (bytes(bad),), 'signing-field-bounds')
    negative(signed_v2, (v2() + b'x',), 'signing-trailing-field')
    negative(signed_v2, (v2(duplicate=True),), 'duplicate-signature-algorithm')
    negative(signed_v2, (v2(algorithm=0x9999),), 'unsupported-signature-algorithm')
    negative(signed_v2, (v2(attributes=field(struct.pack('<I', 1))),), 'unsupported-v2-attributes-or-key')
    for size in range(4):
        negative(signed_v2, (v2()[:size],), 'signing-field-bounds')
    for extra in ('lib/arm64-v8a/payload.so', 'assets/payload', 'sdkDependencyData.pb', 'META-INF/CERT.RSA'):
        negative(signed_package, ({**payloads, extra: b'synthetic'},), 'signed-package-inventory')
    for key, value in (('package', 'wrong.package'), (NS + 'versionCode', '2'), (NS + 'versionName', 'wrong')):
        tree = copy.deepcopy(manifest); tree.set(key, value)
        negative(signed_package, ({**payloads, 'AndroidManifest.xml': xml(tree)},), 'signed-package-policy')
    for target, key, value in (('application', 'debuggable', 'true'), ('uses-sdk', 'minSdkVersion', '36'),
                               ('uses-sdk', 'targetSdkVersion', '36')):
        tree = copy.deepcopy(manifest); tree.find(target).set(NS + key, value)
        negative(signed_package, ({**payloads, 'AndroidManifest.xml': xml(tree)},), 'signed-package-policy')
    tree = copy.deepcopy(manifest); ET.SubElement(tree, 'uses-permission', {NS + 'name': 'android.permission.INTERNET'})
    negative(signed_package, ({**payloads, 'AndroidManifest.xml': xml(tree)},), 'signed-package-policy')
    negative(signed_package, ({**payloads, 'classes.dex': b'dex\nLjava/net/Socket;'},), 'signed-package-capability')
    tree = copy.deepcopy(manifest); tree.append(copy.deepcopy(tree.find('uses-sdk')))
    negative(signed_package, ({**payloads, 'AndroidManifest.xml': xml(tree)},), 'signed-package-sdk-count')

    now = 1794355200  # fixed synthetic clock, not a current-time assertion
    row = {k: hashlib.sha256(k.encode()).hexdigest() for k in (
        'build', 'checkout', 'outputs', 'dependency_home', 'retained', 'execution', 'operator',
        'source', 'apk', 'inputs', 'tools', 'signer')}
    row.update(apk=hashlib.sha256(raw).hexdigest(), started=now - 20, finished=now - 10,
               expires=now + 60, fresh=True, copied=False)
    second = row.copy()
    for key in ('build', 'checkout', 'outputs', 'dependency_home', 'retained', 'execution', 'operator'):
        second[key] = hashlib.sha256(('second-' + key).encode()).hexdigest()
    receipts = [row, second]
    receipt_consistency(receipts, raw, row['source'], now)
    negative(receipt_consistency, (None, raw, row['source'], now), 'missing-build-receipts')
    for key, value, code in (
        ('expires', now, 'build-receipt-time'), ('started', now + 1, 'build-receipt-time'),
        ('expires', QUALIFICATION_EXPIRES + 1, 'build-receipt-time'),
        ('copied', True, 'build-receipt-freshness'), ('fresh', False, 'build-receipt-freshness'),
        ('apk', '0' * 64, 'build-receipt-correspondence'), ('source', '0' * 64, 'build-receipt-correspondence'),
        ('build', row['build'], 'build-receipt-independence'), ('retained', row['retained'], 'build-receipt-independence'),
        ('tools', '0' * 64, 'build-receipt-inputs'), ('signer', '0' * 64, 'build-receipt-inputs')):
        changed = copy.deepcopy(receipts); changed[1][key] = value
        negative(receipt_consistency, (changed, raw, row['source'], now), code)
    changed = copy.deepcopy(receipts); del changed[1]['execution']
    negative(receipt_consistency, (changed, raw, row['source'], now), 'build-receipt-schema')
    # Even complete, consistent synthetic claims cannot authenticate themselves.
    negative(qualified_authority, (receipts,), 'independent-qualification-authority-unavailable')
    output = 'Verifies\n' + ''.join(f'Verified using {v} scheme (fixture): {str(v == "v2").lower()}\n'
                                    for v in ('v1', 'v2', 'v3', 'v3.1', 'v4'))
    output += 'Number of signers: 1\nSigner #1 certificate SHA-256 digest: ' + certificate + '\n'
    result = SimpleNamespace(returncode=0, stdout=output, stderr='')
    verified_signature_output(result, certificate)  # parser test ONLY
    negative(verified_signature_output, (SimpleNamespace(returncode=1, stdout='DOES NOT VERIFY\n', stderr=''), certificate),
             'signature-verification-failed')
    negative(verified_signature_output, (result, '0' * 64), 'unauthorized-signer')
    negative(verified_signature_output, (SimpleNamespace(returncode=0, stdout=output.replace('v2 scheme (fixture): true',
             'v2 scheme (fixture): false'), stderr=''), certificate), 'unsupported-verified-schemes')
    negative(verified_signature_output, (SimpleNamespace(returncode=0, stdout=output +
             'Signer #2 certificate SHA-256 digest: ' + certificate + '\n', stderr=''), certificate), 'unauthorized-signer')

    with tempfile.TemporaryDirectory(prefix='pdva-synthetic-signed-structure-') as temp:
        paths = [Path(temp) / name for name in ('synthetic-a.bin', 'synthetic-b.bin')]
        for path in paths:
            path.write_bytes(raw)
        originals = original_pair(paths)
        unchanged_originals(paths, originals)
        rejected(original_pair, ([paths[0], paths[0]],), 'same-original-file')
        paths[1].write_bytes(raw + b'replacement')
        rejected(unchanged_originals, (paths, originals), 'artifact-replaced')
        paths[1].write_bytes(raw)
        replacement = Path(temp) / 'synthetic-replacement.bin'
        replacement.write_bytes(raw)
        originals = original_pair(paths)
        replacement.replace(paths[1])
        rejected(unchanged_originals, (paths, originals), 'artifact-replaced')
        receipt_file = Path(temp) / 'synthetic-receipts.json'
        receipt_file.write_text('{"build":1,"build":2}')
        rejected(read_build_receipts, (receipt_file,), 'duplicate-receipt-field')
        # Actual complete verifier never qualifies these structurally positive
        # fixtures: absence of receipts is a named, observed rejection.
        rejected(qualify_signed_pair, (paths,), 'missing-build-receipts')
        cli = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--signed-pair',
                              *map(str, paths)], capture_output=True, text=True, timeout=30)
        require(cli.returncode == 1 and not cli.stderr and cli.stdout.strip() ==
                'NOT QUALIFIED: missing-build-receipts; admission NOT RUN / Unknown', 'real signed-pair CLI denial')
        consistent = copy.deepcopy(receipts)
        current = int(time.time())
        for item in consistent:
            item.update(source=qualification_source_identity(working_source()), started=current - 20,
                        finished=current - 10, expires=min(current + 60, QUALIFICATION_EXPIRES))
        # The fixed policy expires: after that, time rejection replaces authority
        # rejection. Tests must never extend the actual policy to stay green.
        expected = ('independent-qualification-authority-unavailable'
                    if current < QUALIFICATION_EXPIRES else 'build-receipt-time')
        rejected(qualify_signed_pair, (paths, consistent), expected)
        receipt_file.write_text(json.dumps(consistent))
        cli = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--signed-pair', *map(str, paths),
                              '--build-receipts', str(receipt_file)], capture_output=True, text=True, timeout=30)
        require(cli.returncode == 1 and not cli.stderr and cli.stdout.strip() ==
                'NOT QUALIFIED: ' + expected + '; admission NOT RUN / Unknown', 'real untrusted-receipts CLI denial')

    mutants = {}
    for function, arguments, code in cases:
        rejected(function, arguments, code)
        if function.__name__ not in mutants:
            tree = ast.parse(inspect.getsource(function))
            tree.body[0].body = [ast.Pass()]
            namespace = globals().copy()
            exec(compile(ast.fix_missing_locations(tree), '<qualification-detector-removal>', 'exec'), namespace)
            mutants[function.__name__] = namespace[function.__name__]
        mutant = mutants[function.__name__]
        mutant(*arguments)  # must complete: arbitrary exceptions are not a kill
        try:
            rejected(mutant, arguments, code)
        except AssertionError as failure:
            require(type(failure) is AssertionError and str(failure) == 'qualification negative accepted: ' + code,
                    'wrong qualification mutant outcome')
        else:
            raise AssertionError('qualification mutant survived')
    print(f'PASS: synthetic signed-structure/byte/package/receipt/output controls; {len(cases)} specific negatives; '
          f'{len(cases)} detector-removal assertion failures ({len(mutants)} bodies); 8 file/CLI/admission negatives')
    print('Signed-APK qualification: NOT RUN / Unknown; fixtures and parsed signature text are not verification')


def unsigned_execution_claims(records, paths, originals, source, now):
    """Contradiction detection only; local records cannot authenticate execution."""
    qualification_require(type(records) is list and len(records) == 2, 'unsigned-execution-records')
    locations = []
    for row, path, (identity, raw) in zip(records, paths, originals):
        qualification_require(type(row) is dict and {
            'source', 'sdk', 'android_home', 'gradle_home', 'started_ns', 'finished_ns',
            'exit', 'initial_build_absent', 'source_unchanged', 'sdk_unchanged',
            'source_identity', 'apk', 'apk_identity', 'apk_sha256', 'trust'
        } <= row.keys(), 'unsigned-execution-schema')
        qualification_require(row['exit'] == 0 and row['initial_build_absent'] is True
                              and row['source_unchanged'] is True and row['sdk_unchanged'] is True
                              and row['trust'] == 'UNTRUSTED', 'unsigned-execution-state')
        qualification_require(type(row['started_ns']) is int and type(row['finished_ns']) is int
                              and 0 < row['started_ns'] < identity[3] <= row['finished_ns'] <= now,
                              'unsigned-execution-time')
        qualification_require(row['source_identity'] == source
                              and row['apk_sha256'] == hashlib.sha256(raw).hexdigest()
                              and row['apk_identity'] == list(identity)
                              and Path(row['apk']).resolve() == Path(path).resolve(),
                              'unsigned-execution-correspondence')
        roots = [Path(row[k]).resolve() for k in ('source', 'sdk', 'android_home', 'gradle_home')]
        qualification_require(Path(path).resolve() == roots[0] / 'android/memory-diagnostic/build/outputs/apk/release/memory-diagnostic-release-unsigned.apk',
                              'unsigned-output-location')
        locations.extend(roots)
    qualification_require(all(a != b and a not in b.parents and b not in a.parents
                              for i, a in enumerate(locations) for b in locations[i + 1:]),
                          'unsigned-execution-separation')


def unsigned_task_execution(log):
    tasks = re.findall(r'^> Task (:memory-diagnostic:\S+)([^\r\n]*)$', log, re.M)
    executed = {name for name, state in tasks if not state.strip()}
    empty = {':memory-diagnostic:' + name for name in ('preBuild', 'preReleaseBuild', 'generateReleaseAssets')}
    qualification_require('BUILD SUCCESSFUL' in log and 'BUILD FAILED' not in log
                          and 'FROM-CACHE' not in log
                          and all(state.strip() != 'UP-TO-DATE' or name in empty for name, state in tasks)
                          and {':memory-diagnostic:' + name for name in (
                              'compileReleaseJavaWithJavac', 'dexBuilderRelease', 'packageRelease',
                              'assembleRelease', 'diagnosticTest', 'lintRelease')} <= executed,
                          'unsigned-task-execution')


def unsigned_source_correspondence(source, snapshot):
    qualification_require(all((source / name).is_file() and not (source / name).is_symlink()
                              and (source / name).read_bytes() == blob
                              for name, (_, blob) in snapshot.items()), 'unsigned-source-correspondence')


def compare_unsigned_pair(paths, source_ref, records):
    """Bounded development observation, never signed or independent qualification."""
    snapshot = committed_source(source_ref)
    verify_companion_delta(snapshot, (SOURCE_BASE, PROTECTED.copy()))
    originals = original_pair(paths)  # ALL original bytes, before any ZIP interpretation.
    print('PASS: complete original unsigned bytes equal; package/execution checks still pending')
    unsigned_execution_claims(records, paths, originals, qualification_source_identity(snapshot), time.time_ns())
    for row, path, (_, raw) in zip(records, paths, originals):
        source = Path(row['source'])
        unsigned_source_correspondence(source, snapshot)
        log = (source.parent / 'execution.log').read_text(errors='strict')
        unsigned_task_execution(log)
        package_policy(Path(path))
        qualification_require(raw[-22:-18] == b'PK\x05\x06' and raw[-2:] == b'\0\0', 'unsigned-zip-end')
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            signed_package({entry.filename: archive.read(entry) for entry in archive.infolist()})
    unchanged_originals(paths, originals)
    print('PASS: complete original unsigned bytes equal; source/package/execution claims consistent; '
          'UNTRUSTED local observation, NOT independently authenticated or signed qualification')


def unsigned_pair_tests():
    """Synthetic contradiction controls; real builds are a separate experiment."""
    import copy
    raw = b'synthetic unsigned observation; not an APK'
    paths = [Path(tempfile.gettempdir()) / ('pdva-unsigned-fixture-' + x) / 'source/android/memory-diagnostic/build/outputs/apk/release/memory-diagnostic-release-unsigned.apk' for x in ('a', 'b')]
    originals = [((1, i + 1, len(raw), 20), raw) for i in range(2)]
    records = []
    for path, (identity, _) in zip(paths, originals):
        base = path.parents[7]
        records.append(dict(source=str(base / 'source'), sdk=str(base / 'sdk'),
                            android_home=str(base / 'android-home'), gradle_home=str(base / 'gradle-home'),
                            started_ns=10, finished_ns=30, exit=0, initial_build_absent=True,
                            source_unchanged=True, sdk_unchanged=True, source_identity='fixture',
                            apk=str(path), apk_identity=list(identity), apk_sha256=hashlib.sha256(raw).hexdigest(),
                            trust='UNTRUSTED'))
    unsigned_execution_claims(records, paths, originals, 'fixture', 40)
    cases = []
    for field, value, reason in (
        ('initial_build_absent', False, 'state'), ('exit', 1, 'state'),
        ('source_unchanged', False, 'state'), ('sdk_unchanged', False, 'state'),
        ('trust', 'APPROVED', 'state'), ('started_ns', 21, 'time'),
        ('finished_ns', 41, 'time'), ('source_identity', 'wrong', 'correspondence'),
        ('apk_sha256', 'wrong', 'correspondence'), ('apk_identity', [1, 99, len(raw), 20], 'correspondence'),
        ('apk', str(paths[0]), 'correspondence'),
        ('gradle_home', records[0]['gradle_home'], 'separation'),
        ('sdk', records[0]['sdk'], 'separation'),
        ('android_home', records[0]['android_home'], 'separation')):
        changed = copy.deepcopy(records); changed[1][field] = value
        cases.append((changed, 'unsigned-execution-' + reason))
    cases.extend([(None, 'unsigned-execution-records'), ([{}, {}], 'unsigned-execution-schema')])
    node = ast.parse(inspect.getsource(unsigned_execution_claims)).body[0]
    node.body = [ast.Pass()]
    namespace = globals().copy()
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<unsigned-detector-removal>', 'exec'), namespace)
    def reject(fn, rows, reason):
        try:
            fn(rows, paths, originals, 'fixture', 40)
        except QualificationRejection as failure:
            require(str(failure) == reason, 'specific unsigned rejection')
        else:
            raise AssertionError('unsigned negative accepted')
    for rows, reason in cases:
        reject(unsigned_execution_claims, rows, reason)
        namespace['unsigned_execution_claims'](rows, paths, originals, 'fixture', 40)
        try:
            reject(namespace['unsigned_execution_claims'], rows, reason)
        except AssertionError as failure:
            require(str(failure) == 'unsigned negative accepted', 'effective unsigned detector removal')
        else:
            raise AssertionError('unsigned detector removal survived')
    print('PASS: unsigned execution claims; 16 negatives / 16 effective detector-removal assertions (synthetic only)')
    log = ''.join('> Task :memory-diagnostic:' + name + '\n' for name in (
        'compileReleaseJavaWithJavac', 'dexBuilderRelease', 'packageRelease', 'assembleRelease',
        'diagnosticTest', 'lintRelease')) + 'BUILD SUCCESSFUL\n'
    unsigned_task_execution(log)
    unsigned_task_execution(log + '> Task :memory-diagnostic:preBuild UP-TO-DATE\n')
    bad_logs = [log.replace('packageRelease\n', 'packageRelease ' + state + '\n')
                for state in ('FROM-CACHE', 'UP-TO-DATE', 'SKIPPED', 'NO-SOURCE')]
    bad_logs += [log.replace('BUILD SUCCESSFUL', 'BUILD FAILED'),
                 log.replace('> Task :memory-diagnostic:compileReleaseJavaWithJavac\n', '')]
    node = ast.parse(inspect.getsource(unsigned_task_execution)).body[0]; node.body = [ast.Pass()]
    namespace = globals().copy()
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<task-detector-removal>', 'exec'), namespace)
    def reject_log(fn, text):
        try:
            fn(text)
        except QualificationRejection as failure:
            require(str(failure) == 'unsigned-task-execution', 'specific task rejection')
        else:
            raise AssertionError('task negative accepted')
    for text in bad_logs:
        reject_log(unsigned_task_execution, text)
        namespace['unsigned_task_execution'](text)
        try:
            reject_log(namespace['unsigned_task_execution'], text)
        except AssertionError as failure:
            require(str(failure) == 'task negative accepted', 'effective task detector removal')
        else:
            raise AssertionError('task detector removal survived')
    print('PASS: task execution claims; 6 negatives / 6 effective detector-removal assertions (synthetic only)')
    with tempfile.TemporaryDirectory(prefix='pdva-source-correspondence-') as temp:
        source = Path(temp)
        (source / 'fixture').write_bytes(b'fixture')
        unsigned_source_correspondence(source, {'fixture': ('100644', b'fixture')})
        node = ast.parse(inspect.getsource(unsigned_source_correspondence)).body[0]; node.body = [ast.Pass()]
        namespace = globals().copy()
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<export-detector-removal>', 'exec'), namespace)
        def reject_source(fn, snapshot):
            try:
                fn(source, snapshot)
            except QualificationRejection as failure:
                require(str(failure) == 'unsigned-source-correspondence', 'specific source correspondence rejection')
            else:
                raise AssertionError('source correspondence negative accepted')
        for snapshot in ({'missing': ('100644', b'fixture')}, {'fixture': ('100644', b'changed')}):
            reject_source(unsigned_source_correspondence, snapshot)
            namespace['unsigned_source_correspondence'](source, snapshot)
            try:
                reject_source(namespace['unsigned_source_correspondence'], snapshot)
            except AssertionError as failure:
                require(str(failure) == 'source correspondence negative accepted', 'effective correspondence removal')
            else:
                raise AssertionError('source correspondence removal survived')
    print('PASS: exported source correspondence; 2 negatives / 2 effective detector-removal assertions')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--android-jar', type=Path)
    parser.add_argument('--apk', type=Path)
    parser.add_argument('--unsigned-pair', nargs=2, type=Path)
    parser.add_argument('--unsigned-source-ref')
    parser.add_argument('--unsigned-executions', type=Path, help='private local observations; not authenticated receipts')
    parser.add_argument('--signed-pair', nargs=2, type=Path,
                        help='read-only preliminary checks; real admission remains unavailable and exits nonzero')
    parser.add_argument('--build-receipts', type=Path, help='private untrusted claim packet; never grants approval')
    source_mode = parser.add_mutually_exclusive_group()
    source_mode.add_argument('--verify-source-baseline', action='store_true',
                             help='recompute the pinned public evidence from the exact base Git object')
    source_mode.add_argument('--check-source-ref',
                             help='check an existing local commit for the exact proposed source delta only')
    args = parser.parse_args()
    if args.unsigned_pair:
        try:
            qualification_require(args.unsigned_source_ref and args.unsigned_executions
                                  and not (args.signed_pair or args.build_receipts or args.java_home
                                           or args.android_jar or args.apk or args.verify_source_baseline
                                           or args.check_source_ref), 'unsigned-options')
            compare_unsigned_pair(args.unsigned_pair, args.unsigned_source_ref, read_build_receipts(args.unsigned_executions))
        except QualificationRejection as failure:
            print('FAIL/Unknown unsigned observation: ' + str(failure))
            raise SystemExit(1) from None
        except (OSError, ValueError, TypeError, KeyError, AssertionError, struct.error, subprocess.SubprocessError):
            print('FAIL/Unknown unsigned observation: inspection-unavailable')
            raise SystemExit(1) from None
        return
    require(not (args.unsigned_source_ref or args.unsigned_executions), 'unsigned options require unsigned pair')
    if args.signed_pair:
        try:
            qualification_require(not (args.java_home or args.android_jar or args.apk or args.verify_source_baseline
                                       or args.check_source_ref), 'incompatible-qualification-options')
            qualify_signed_pair(args.signed_pair, read_build_receipts(args.build_receipts) if args.build_receipts else None)
        except QualificationRejection as failure:
            print('NOT QUALIFIED: ' + str(failure) + '; admission NOT RUN / Unknown')
            raise SystemExit(1) from None
        except (OSError, ValueError, AssertionError, struct.error, subprocess.SubprocessError, RecursionError):
            print('NOT QUALIFIED: inspection-unavailable; admission NOT RUN / Unknown')
            raise SystemExit(1) from None
        raise SystemExit('NOT QUALIFIED: no admission result')
    require(args.build_receipts is None, 'build receipts require signed pair')
    if args.verify_source_baseline or args.check_source_ref:
        require(not (args.java_home or args.android_jar or args.apk), 'source-only options cannot build/inspect packages')
        snapshot = committed_source(SOURCE_BASE if args.verify_source_baseline else args.check_source_ref)
        if args.verify_source_baseline:
            check_source_modes(snapshot)
            require(snapshot[BUILD_PATH][1] == BASE_BUILD, 'baseline module bytes')
            require(protected_evidence(snapshot) == PROTECTED, 'baseline protected evidence')
            print('PASS: public baseline Git blobs/modes recomputed (not independent authentication)')
        else:
            verify_companion_delta(snapshot, (SOURCE_BASE, PROTECTED.copy()))
            print('PASS: exact proposed source delta only; independent review and qualification still required')
        return
    companion_source_tests()
    metadata_package_tests()
    signed_qualification_tests()
    unsigned_pair_tests()
    source_policy()
    adapter = (JAVA / 'AndroidOps.java').read_text()
    manifest = (MODULE / 'src/main/AndroidManifest.xml').read_text()
    for mutation in ('rwx', 'permission'):
        try:
            source_policy(adapter=adapter.replace('OsConstants.PROT_READ | OsConstants.PROT_WRITE,',
                'OsConstants.PROT_READ | OsConstants.PROT_WRITE | OsConstants.PROT_EXEC,') if mutation == 'rwx' else None,
                manifest=manifest.replace('<application ', '<uses-permission android:name="android.permission.INTERNET"/><application ')
                if mutation == 'permission' else None)
        except AssertionError as failure:
            require(str(failure) == ('bounded split RW/RX mappings' if mutation == 'rwx' else 'no permissions/components'),
                    'specific mutation rejection')
        else:
            raise AssertionError('unsafe mutation accepted')
    print('PASS: source policy; RWX and INTERNET negative controls rejected')
    if args.java_home:
        jvm_tests(args.java_home, args.android_jar)
    if args.apk:
        package_policy(args.apk)


if __name__ == '__main__':
    main()
