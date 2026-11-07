#!/usr/bin/env python3
"""Source, desktop JVM and unsigned-package checks; never installs or runs Android."""
import argparse
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / 'android/memory-diagnostic'
JAVA = MODULE / 'src/main/java/org/pdva/memorydiagnostic'
NS = '{http://schemas.android.com/apk/res/android}'


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
    args = parser.parse_args()
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
