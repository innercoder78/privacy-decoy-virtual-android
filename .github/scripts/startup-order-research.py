#!/usr/bin/env python3
"""Pinned first-pass/config-open witness; NOT a resource policy or QEMU entry.

Only emitted controls are compiled. Upstream source is never modified. The
extracted qemu_init interval ends before its second pass; earlier subsystem
initialization and the rest of QEMU are deliberately outside this experiment.
"""
import hashlib
import platform
import re
import stat
import subprocess

INPUTS = {
    'system/vl.c': 'a5fb2a78e45ec8edb256188eed44e8f06f7dba99c1dd029dd8a0d74cfab74266',
    'util/qemu-config.c': '706ec50d468d2754c7278ec9d1904ad19c263bc72457830944c639fa25fd3b79',
    'qemu-options.hx': '39be98e63d1b2d7b65bcec4bca0e704a2bb79cc4bb52a6f6d071babc189c6e63',
}


def extract(text, signature):
    matches = re.findall('^' + re.escape(signature) + r'\([^;]*?\n\{.*?^\}\n',
                         text, re.M | re.S)
    if len(matches) != 1:
        raise RuntimeError('Ambiguous startup extraction: ' + signature)
    return matches[0]


def render(sources, mutation=None):
    if set(sources) != set(INPUTS):
        raise RuntimeError('Unexpected startup source set')
    for name, expected in INPUTS.items():
        if hashlib.sha256(sources[name]).hexdigest() != expected:
            raise RuntimeError('Startup source identity mismatch: ' + name)
    vl, config, options = (sources[n].decode() for n in INPUTS)
    start = '    /* first pass of option parsing */\n'
    end = '    /* second pass of option parsing */\n'
    if vl.count(start) != 1 or vl.count(end) != 1:
        raise RuntimeError('Ambiguous startup interval')
    interval = vl[vl.index(start):vl.index(end)]
    # Actual first three DEF fields, only for the options exercised here. The
    # second pass is not extracted; no architecture/property validation claimed.
    entries = []
    for name in ('no-user-config', 'machine', 'kernel', 'readconfig', 'dump-vmstate'):
        match = re.findall(r'DEF\("' + re.escape(name) +
                           r'",\s*(HAS_ARG|0),\s*(QEMU_OPTION_\w+),', options)
        if len(match) != 1:
            raise RuntimeError('Ambiguous option definition: ' + name)
        entries.append((name, *match[0]))
    table = 'enum { ' + ', '.join(e[2] for e in entries) + ' };\n'
    table += 'static const QEMUOption qemu_options[] = {\n'
    table += ''.join('    {"%s", %s, %s},\n' % e for e in entries)
    table += '    {NULL, 0, 0}\n};\n'
    if mutation == 'late-disable':
        interval = interval.replace('                userconfig = false;',
                                    '                deferred_disable = true;')
        interval += '    if (deferred_disable) { userconfig = false; }\n'
    elif mutation == 'omit-disable':
        interval = interval.replace('                userconfig = false;',
                                    '                /* deliberately omitted */')
    elif mutation not in (None, 'reopen'):
        raise RuntimeError('Unknown startup mutation')
    # vl.c carries a GPL notice; qemu-config.c has no leading notice. Preserve
    # vl.c's entire original notice, and identify the other extracted source.
    notice = vl[:vl.index('*/') + 2] + '\n'
    notice += '/* Also extracts util/qemu-config.c from pinned QEMU; see QEMU LICENSE/COPYING. */\n'
    reader = extract(config, 'int qemu_read_config_file')
    if mutation == 'reopen':
        reader = reader.replace('    fclose(f);',
                                '    fclose(f);\n    fclose(fopen(filename, "r"));')
    return (notice + PRELUDE + table +
            extract(vl, 'static const QEMUOption *lookup_opt') + reader +
            extract(vl, 'static void qemu_read_default_config_file') +
            'static void first_pass(int argc, char **argv)\n{\n'
            '    int optind;\n    const char *optarg;\n    bool userconfig = true;\n' +
            ('    bool deferred_disable = false;\n' if mutation == 'late-disable' else '') +
            interval + '}\n' + DRIVER)


PRELUDE = r'''
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#define HAS_ARG 1
#define CONFIG_QEMU_CONFDIR "synthetic-config"
#define ERRP_GUARD() ((void)0)
#define g_autofree
typedef int Error;
typedef void QEMUConfigCB(void);
typedef struct { const char *name; int flags, index; } QEMUOption;
static Error *error_fatal;
static void *machine_opts_dict;
static void *vm_config_groups;
static unsigned opens, parses, closes, marker;
static bool deny_open;
#define CHECK(c, msg) do { if (!(c)) { fputs("FAIL: " msg "\n", stderr); exit(90); } } while (0)
static void error_report(const char *s) { fprintf(stderr, "%s\n", s); }
static void loc_set_cmdline(char **v, int i, int n) { (void)v; (void)i; (void)n; }
static void *qdict_new(void) { return &marker; }
static void qemu_parse_config_group(void) { }
static void error_free(Error *e) { (void)e; }
static void error_setg_file_open(Error **e, int n, const char *s) {
    (void)e; (void)n; (void)s;
}
static char *get_relocated_path(const char *s) {
    CHECK(!strcmp(s, "synthetic-config/qemu.conf"), "relocation input");
    /* Fixed synthetic file in the controller-owned working directory. */
    return "qemu.conf";
}
static int qemu_config_foreach(FILE *f, QEMUConfigCB *cb, void *groups,
                               const char *name, Error **errp) {
    (void)cb; (void)groups; (void)name; (void)errp;
    parses++;
    /* Parser is modeled. Actual libc read proves only synthetic bytes arrived. */
    CHECK(fgetc(f) == '#', "synthetic byte");
    return 0;
}
static FILE *observed_fopen(const char *path, const char *mode) {
    opens++;
    CHECK(marker == 0, "open after late marker");
    CHECK(!strcmp(path, "qemu.conf") && !strcmp(mode, "r"), "unexpected pathname");
    if (deny_open) {
        fputs("DENIED: config open before late marker\n", stderr);
        exit(93);
    }
    return fopen(path, mode);
}
static int observed_fclose(FILE *f) { closes++; return fclose(f); }
#define fopen observed_fopen
#define fclose observed_fclose
'''

DRIVER = r'''
int main(int argc, char **argv) {
    CHECK(argc >= 4, "driver arguments");
    unsigned expected = (unsigned)strtoul(argv[1], NULL, 10);
    deny_open = !strcmp(argv[2], "deny");
    /* Remaining argv is the synthetic QEMU command line, including argv[0]. */
    first_pass(argc - 3, argv + 3);
    marker = 1; /* proposed after-parsing guard is strictly later than this */
    CHECK(opens == expected && parses == expected && closes == expected,
          "configuration boundary counts");
    CHECK(machine_opts_dict != NULL, "first pass completed");
    puts("PASS: startup interval counts");
    return 0;
}
'''


def cases():
    # name, expected calls, observer, argv, exit, stdout, stderr
    ok = 'PASS: startup interval counts\n'
    denied = 'DENIED: config open before late marker\n'
    return [
        ('implicit', 1, 'allow', [], 0, ok, ''),
        ('implicit-denied', 1, 'deny', [], 93, '', denied),
        ('disabled', 0, 'deny', ['-no-user-config'], 0, ok, ''),
        ('double-dash', 0, 'deny', ['--no-user-config'], 0, ok, ''),
        ('duplicate-disable', 0, 'deny', ['-no-user-config'] * 2, 0, ok, ''),
        ('positional-disk', 1, 'deny', ['synthetic-disk'], 93, '', denied),
        ('machine-invalid-later', 1, 'deny', ['-machine', 'invalid'], 93, '', denied),
        ('kernel-path-later', 1, 'deny', ['-kernel', 'synthetic-kernel'], 93, '', denied),
        ('explicit-config-later', 1, 'deny', ['-readconfig', 'synthetic-other'], 93, '', denied),
        ('dump-later', 1, 'deny', ['-dump-vmstate', 'synthetic-output'], 93, '', denied),
        ('option-as-argument', 1, 'deny', ['-kernel', '-no-user-config'], 93, '', denied),
        ('unknown-option', 0, 'deny', ['-pdva-unknown'], 1, '', 'invalid option\n'),
        ('missing-argument', 0, 'deny', ['-kernel'], 1, '', 'requires an argument\n'),
    ]


def require_result(result, code, stdout, stderr):
    if (result.returncode, result.stdout, result.stderr) != (code, stdout, stderr):
        raise RuntimeError('Unexpected startup control outcome: ' + repr(
            (result.returncode, result.stdout, result.stderr)))


def read_sources(qemu):
    sources = {}
    for name in INPUTS:
        path = qemu / name
        if (not stat.S_ISREG(path.lstat().st_mode) or path.is_symlink() or
                any(p.is_symlink() for p in path.parents)):
            raise RuntimeError('Unsafe startup input: ' + name)
        sources[name] = path.read_bytes()
    render(sources)
    return sources


def run_controls(qemu, root, run, emit):
    if platform.system() != 'Linux':
        raise RuntimeError('Startup controls require Linux')
    sources = read_sources(qemu)
    work = root / 'startup-order'
    work.mkdir()  # Existing output is terminal; never overwrite earlier evidence.
    (work / 'qemu.conf').write_bytes(b'# synthetic configuration only\n')
    for mutation in (None, 'late-disable', 'omit-disable', 'reopen'):
        name = mutation or 'positive'
        source, binary = work / (name + '.c'), work / name
        source.write_text(render(sources, mutation), encoding='utf-8', newline='\n')
        emit(f'STARTUP {name} source-sha256=' + hashlib.sha256(source.read_bytes()).hexdigest())
        run('cc', '-std=c11', '-O0', '-Wall', '-Wextra', '-Werror', source, '-o', binary)
        emit(f'STARTUP {name} binary-sha256=' + hashlib.sha256(binary.read_bytes()).hexdigest())
        tests = cases() if mutation is None else [
            (name, 1 if mutation == 'reopen' else 0,
             'allow' if mutation == 'reopen' else 'deny',
             [] if mutation == 'reopen' else ['-no-user-config'],
             90 if mutation == 'reopen' else 93, '',
             'FAIL: configuration boundary counts\n' if mutation == 'reopen' else
             'DENIED: config open before late marker\n')]
        for label, expected, observer, args, code, out, err in tests:
            result = subprocess.run([str(binary), str(expected), observer, 'qemu', *args],
                                    cwd=work, capture_output=True, text=True, timeout=5)
            require_result(result, code, out, err)
            emit(f'STARTUP {label}: exact exit={code}; PASS')
    emit('STARTUP COMPLETE: 13 cases, 3 mutants; extracted interval, no QEMU execution')
