#!/usr/bin/env python3
"""Source, desktop JVM and unsigned-package checks; never installs or runs Android."""
import argparse
import ast
import hashlib
import inspect
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
    require(current[BUILD_PATH] == ('100644', BASE_BUILD), 'active metadata configuration must remain unchanged')
    evidence = (SOURCE_BASE, PROTECTED.copy())
    positive = current.copy()
    positive[BUILD_PATH] = ('100644', PROPOSED_BUILD)
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
    print(f'PASS: exact proposal fixture; {len(cases)} specific negatives; '
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


def package_policy(apk):
    data = apk.read_bytes()
    with zipfile.ZipFile(apk) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'unique ZIP entries')
        require(not any(n.startswith(('lib/', 'assets/')) or n.lower().endswith(('.so', '.rsa', '.dsa', '.ec', '.sf'))
                        for n in names), 'no native payloads/assets/v1 signatures')
        require(data[archive.start_dir - 16:archive.start_dir] != b'APK Sig Block 42', 'no APK signing block')
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
    print('PASS: unsigned package manifest/DEX/native/signature inventory (not qualification)')


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java-home', type=Path)
    parser.add_argument('--android-jar', type=Path)
    parser.add_argument('--apk', type=Path)
    source_mode = parser.add_mutually_exclusive_group()
    source_mode.add_argument('--verify-source-baseline', action='store_true',
                             help='recompute the pinned public evidence from the exact base Git object')
    source_mode.add_argument('--check-source-ref',
                             help='check an existing local commit for the exact proposed source delta only')
    args = parser.parse_args()
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
