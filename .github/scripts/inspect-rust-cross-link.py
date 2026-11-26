"""Static inspection only. A layout pass is never a cross-link qualification."""
import re
import struct
import sys
from pathlib import Path

HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
PHDR = struct.Struct("<IIQQQQQQ")
DYN = struct.Struct("<qQ")
STACK = 0x6474E551


class Reject(ValueError):
    pass


def check(ok, reason):
    if not ok:
        raise Reject(reason)


def layout(data):
    check(len(data) >= HEADER.size, "header-extent")
    ident, kind, machine, version, entry, offset, _, flags, size, stride, count, *_ = HEADER.unpack_from(data)
    check(ident[:7] == b"\x7fELF\x02\x01\x01", "elf-class-data")
    check(kind == 3 and machine == 183 and version == 1 and flags == 0, "elf-target")
    check(entry == 0, "entry-point")
    check(size == HEADER.size and stride == PHDR.size and 0 < count < 256 and
          offset >= size and offset + stride * count <= len(data), "program-table")
    loads, stacks, dynamics = [], [], []
    for i in range(count):
        typ, perms, off, addr, _, filesz, memsz, align = PHDR.unpack_from(data, offset + i * stride)
        check(off + filesz <= len(data) and filesz <= memsz and addr + memsz < 2**64, "segment-extent")
        check(typ != 3, "interpreter")
        if typ == STACK:
            stacks.append(perms)
        if typ == 2:
            dynamics.append((off, addr, filesz))
        if typ != 1:
            continue
        check(perms & 3 != 3, "writable-executable")
        check(align >= 16384 and align & (align - 1) == 0, "load-alignment")
        check((off - addr) % align == 0, "load-congruence")
        loads.append((addr, off, filesz, memsz, perms))
    check(stacks == [6], "gnu-stack")
    check(loads and any(p & 1 for _, _, _, _, p in loads), "executable-load")
    for page in (4096, 16384):
        for i, (addr, _, _, mem, perm) in enumerate(loads):
            for other, _, _, length, protection in loads[:i]:
                overlaps = addr // page < (other + length + page - 1) // page and (
                    other // page < (addr + mem + page - 1) // page)
                check(not overlaps or (perm | protection) & 3 != 3, "page-alias")
    check(len(dynamics) == 1, "dynamic-table")
    start, va, length = dynamics[0]
    check(any(off <= start and start + length <= off + n and va - addr == start - off
              for addr, off, n, _, _ in loads), "dynamic-mapping")
    check(length and length % DYN.size == 0, "dynamic-extent")
    entries = []
    for pos in range(start, start + length, DYN.size):
        tag, value = DYN.unpack_from(data, pos)
        if tag == 0:
            break
        check(tag not in (15, 29), "dynamic-search-path")
        check(tag != 22 and not (tag == 30 and value & 4), "text-relocation")
        entries.append((tag, value))
    else:
        raise Reject("dynamic-terminator")
    return entries


def fixture():
    ident = b"\x7fELF\x02\x01\x01" + bytes(9)
    data = bytearray(512)
    HEADER.pack_into(data, 0, ident, 3, 183, 1, 0, 64, 0, 0, 64, 56, 3, 0, 0, 0)
    for i, row in enumerate(((1, 5, 0, 0, 0, 512, 512, 16384),
                             (STACK, 6, 0, 0, 0, 0, 0, 16),
                             (2, 4, 448, 448, 0, 32, 32, 8))):
        PHDR.pack_into(data, 64 + 56 * i, *row)
    return data


def controls():
    check(layout(fixture()) == [], "positive-control")
    cases = (
        (4, "B", 1, "elf-class-data"), (16, "H", 2, "elf-target"),
        (18, "H", 62, "elf-target"), (24, "Q", 1, "entry-point"),
        (56, "H", 100, "program-table"), (96, "Q", 513, "segment-extent"),
        (68, "I", 7, "writable-executable"), (112, "Q", 4096, "load-alignment"),
        (80, "Q", 1, "load-congruence"), (124, "I", 7, "gnu-stack"),
        (120, "I", 3, "interpreter"), (176, "I", 0, "dynamic-table"),
        (192, "Q", 449, "dynamic-mapping"), (208, "Q", 17, "dynamic-extent"),
        (448, "q", 15, "dynamic-search-path"), (448, "q", 29, "dynamic-search-path"),
        (448, "q", 22, "text-relocation"),
    )
    def refused(data, reason):
        try:
            layout(data)
        except Reject as exc:
            check(str(exc) == reason, "wrong-detector-" + reason)
        else:
            raise AssertionError("accepted-" + reason)

    for offset, fmt, value, reason in cases:
        data = fixture()
        struct.pack_into("<" + fmt, data, offset, value)
        refused(data, reason)
    refused(fixture()[:32], "header-extent")
    data = fixture()
    struct.pack_into("<I", data, 68, 4)
    refused(data, "executable-load")
    data = fixture()
    DYN.pack_into(data, 448, 30, 4)
    refused(data, "text-relocation")
    DYN.pack_into(data, 448, 1, 0)
    DYN.pack_into(data, 464, 1, 0)
    refused(data, "dynamic-terminator")
    data = fixture()
    struct.pack_into("<H", data, 56, 4)
    PHDR.pack_into(data, 232, 1, 6, 16, 16, 0, 16, 16, 16384)
    refused(data, "page-alias")
    print("PASS layout positive and 22 specific negative fixtures")


def library_contract(exports, imports, needed, stubs, allowed):
    """Inputs use (symbol, version) pairs, including weak undefined symbols."""
    check(exports == {"pdva_scm_probe"}, "export-allowlist")
    check(set(needed) == {"libc.so"} and len(needed) == 1, "needed-allowlist")
    check(imports <= allowed and imports <= stubs["libc.so"], "import-allowlist")
    check({"sendmsg", "recvmsg"} <= {sym for sym, _ in imports}, "required-imports")


def direct_edges(words, start):
    """Reachable immediate control transfers. Refuse unresolved computed jumps."""
    active = [start]
    visited = set()
    calls = set()
    while active:
        pc = active.pop()
        if pc in visited:
            continue
        visited.add(pc)
        check(pc in words, "instruction-extent")
        op = words[pc]
        def dest(shift, bits):
            value = (op >> shift) & ((1 << bits) - 1)
            if value & (1 << (bits - 1)):
                value -= 1 << bits
            return pc + 4 * value
        if op == 0xd65f03c0:
            continue
        if op & 0xfc000000 == 0x94000000:
            calls.add((pc, dest(0, 26)))
            active.append(pc + 4)
        elif op & 0xfc000000 == 0x14000000:
            active.append(dest(0, 26))
        elif op & 0xff000010 == 0x54000000 or op & 0x7e000000 == 0x34000000:
            active.extend((pc + 4, dest(5, 19)))
        elif op & 0x7e000000 == 0x36000000:
            active.extend((pc + 4, dest(5, 14)))
        else:
            check(op & 0xfe000000 != 0xd6000000, "indirect-control")
            active.append(pc + 4)
    return calls


def direct_call_controls():
    def rejected(fn, reason):
        try:
            fn()
        except Reject as exc:
            check(str(exc) == reason, "wrong-specific-rejection")
        else:
            raise AssertionError("accepted-" + reason)

    def endpoints(words):
        calls = {target for _, target in direct_edges(words, 0)}
        check({32, 64} <= calls, "missing-reachable-endpoint")
    both = {0: 0x94000008, 4: 0x9400000f, 8: 0xd65f03c0}
    endpoints(both)
    rejected(lambda: endpoints({**both, 0: 0xd65f03c0}), "missing-reachable-endpoint")
    rejected(lambda: endpoints({**both, 0: 0x14000002}), "missing-reachable-endpoint")
    rejected(lambda: endpoints({**both, 0: 0xd61f0020}), "indirect-control")
    rejected(lambda: endpoints({**both, 0: 0x14001000}), "instruction-extent")
    exports = {"pdva_scm_probe"}
    imports = {("sendmsg", "LIBC"), ("recvmsg", "LIBC")}
    stubs = {"libc.so": imports}
    def contract(e=exports, i=imports, n=("libc.so",), s=stubs):
        library_contract(e, i, n, s, imports)
    contract()
    rejected(lambda: contract(e=exports | {"extra"}), "export-allowlist")
    rejected(lambda: contract(i=imports | {("hidden", "LIBC")}), "import-allowlist")
    rejected(lambda: contract(n=("libc.so", "extra.so")), "needed-allowlist")
    rejected(lambda: contract(s={"libc.so": set()}), "import-allowlist")
    rejected(lambda: contract(i={("recvmsg", "LIBC")}), "required-imports")
    print("PASS direct-branch and library-contract controls on synthetic inputs")



def plt_endpoints(data, parts, labels, relocations):
    slots = {}
    for line in relocations.splitlines():
        match = re.match(r"^\s*([0-9a-fA-F]+)\s+\S+\s+R_AARCH64_JUMP_SLOT\s+\S+\s+([^\s@]+)",line)
        if match:
            address = int(match[1],16)
            check(address not in slots, "duplicate-jump-slot")
            slots[address] = match[2]
    endpoints = {}
    for name, address in labels.items():
        if not name.endswith("@plt"):
            continue
        code = next((data[off+address-va:off+address-va+16] for va,off,size,flags in parts
                     if flags & 1 and va<=address and address+16<=va+size), None)
        check(code is not None, "plt-extent")
        adrp, ldr, add, br = struct.unpack("<4I",code)
        check(adrp & 0x9f00001f == 0x90000010 and ldr & 0xffc003ff == 0xf9400211 and
              add & 0xffc003ff == 0x91000210 and br == 0xd61f0220, "plt-sequence")
        imm = ((adrp >> 5 & 0x7ffff) << 2) | (adrp >> 29 & 3)
        if imm & (1<<20):
            imm -= 1<<21
        offset = (ldr >> 10 & 4095)*8
        check((add >> 10 & 4095)==offset, "plt-offset")
        slot=(address & ~4095)+(imm<<12)+offset
        check(slots.get(slot)==name[:-4], "plt-binding")
        endpoints[address]=name[:-4]
    return endpoints


def account_map(text, inputs, sealed, tool):
    """Resolve each contributing input and named archive member in the lld map."""
    origins=[]
    members={}
    for line in text.splitlines():
        m=re.match(r"^\s*([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+\d+\s+(.+?):\(([^)]*)\)\s*$",line)
        if not m:
            check(":(" not in line, "map-format")
            continue
        addr,size,src,section=int(m[1],16),int(m[2],16),m[3].strip(),m[4]
        if src=="<internal>":
            continue
        archive=re.fullmatch(r"(.+)\(([^()/]+)\)",src)
        path=Path(archive[1] if archive else src)
        if path.is_relative_to("/out"):
            file=sealed/path.relative_to("/out")
            if archive:
                check(path.name in {"libvmm_sys_util.rlib","liblibc.rlib","libbitflags.rlib"},
                      "project-archive")
                family=path.name
            else:
                check(path.name.endswith(".rcgu.o") and path.name.startswith("probe."), "probe-object")
                family="probe"
        elif path.is_relative_to(inputs/"rust/lib/rustlib/aarch64-linux-android/lib"):
            match=re.fullmatch(r"lib(std|core|alloc|compiler_builtins|libc|unwind|panic_abort|"
                               r"panic_unwind|std_detect|hashbrown|rustc_demangle|addr2line|gimli|object|"
                               r"memchr|adler2|miniz_oxide|cfg_if|rustc_std_workspace_core)-[0-9a-f]+\.rlib",path.name)
            check(match and archive,"rust-runtime")
            family=match[1]
            file=path
        elif path.is_relative_to(inputs/"ndk/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64"):
            check(path.name in {"crtbegin_so.o","crtend_so.o","libunwind.a",
                                 "libclang_rt.builtins-aarch64-android.a"},"native-runtime")
            family=path.name
            file=path
        else:
            raise Reject("map-input")
        if archive:
            check(file.is_file() and file.resolve().is_relative_to(sealed if path.is_relative_to("/out") else inputs),
                  "archive-location")
            if file not in members:
                members[file]=set(tool("ar","t",file).splitlines())
            check(archive[2] in members[file],"runtime-member")
        if size:
            origins.append((addr,addr+size,family,section))
    check(bool(origins), "empty-map")
    return origins



def witness(instructions, root, external, read_byte, budget=200000, observe=lambda address: None, received_fd=47, call_origin=lambda name, sites: None):
    """Constant propagation for one ABI witness. Unsupported states have no proof.

    Track a fresh abstract stack, returned allocation addresses and owned test FDs.
    An unknown branch condition, unresolved target, unread byte or unsupported
    instruction refuses the witness. No machine code is run.
    """
    import re
    registers = {}
    registers.update(x0=31, x1=32, x2=33, x30=0xfffffff0, sp=1 << 48)
    memory = {}
    frames = []
    next_alloc = 1 << 47
    allocations = {}
    closed = set()
    phase = 0
    flags = {}
    pc = root
    def num(x):
        return int(x.strip().removeprefix("#"), 0)
    def width(r):
        return 4 if r.startswith("w") else 8
    def reg(r):
        if r in ("xzr", "wzr"):
            return 0
        key = "x" + r[1:] if r.startswith("w") else r
        check(key in registers, "unknown-register")
        return registers[key] % (1 << (width(r) * 8))
    def put(r, value):
        if r not in ("wzr", "xzr"):
            check(re.fullmatch(r"(?:[wx](?:[0-9]|[12][0-9]|30)|sp)", r), "unsupported-register")
            registers["x" + r[1:] if r.startswith("w") else r] = value % (1 << (width(r) * 8))
    def atom(x):
        return num(x) if x.startswith("#") else reg(x)
    def read(addr, length):
        value = 0
        for i in range(length):
            byte = memory.get(addr + i)
            if byte is None:
                byte = read_byte(addr + i)
            check(byte is not None, "unknown-memory")
            value |= byte << (8 * i)
        return value
    def write(addr, value, length):
        check(((1 << 48) - (1 << 22) <= addr and addr + length <= 1 << 48) or
              any(a <= addr and addr + length <= a+n for a,n in allocations.items()), "write-region")
        for i in range(length):
            memory[addr + i] = value >> (8*i) & 255
    def message(sending):
        msg = reg("x1")
        check(read(msg,8)==0 and read(msg+8,4)==0, "message-name")
        iov = read(msg + 16, 8)
        ctrl = read(msg + 32, 8)
        check(read(msg + 24, 8) == 1 and read(iov+8, 8) == 1 and read(msg+40, 8) >= 24,
              "msghdr-contract")
        buf = read(iov, 8)
        if sending:
            check(reg("w0") == 31 and reg("w2") == 0x4000 and read(buf, 1) == 0x51 and
                  read(ctrl, 8) == 20 and read(ctrl+8, 4) == 1 and read(ctrl+12, 4) == 1 and
                  read(ctrl+16, 4) == 33, "scm-send-contract")
        else:
            check(reg("w0") == 32 and reg("w2") == 0, "scm-receive-contract")
            write(buf, 0x51, 1)
            for off, value, size in ((0,20,8),(8,1,4),(12,1,4),(16,received_fd,4)):
                write(ctrl+off,value,size)
            write(msg+40,24,8)
            write(msg+48,0,4)
    def finish_call(result):
        for i in range(19):
            registers.pop("x"+str(i), None)
        flags.clear()
        if result is not None:
            put("x0", result)
    for _ in range(budget):
        if pc in external:
            name = external[pc]
            if name in ("sendmsg","recvmsg"):
                check(phase == (0 if name == "sendmsg" else 1), "message-order")
                call_origin(name,[ret-4 for ret in frames])
                message(name == "sendmsg")
                phase += 1
                finish_call(1)
            elif name == "close":
                fd = reg("w0")
                check(fd in (31,32,received_fd) and fd not in closed, "fd-ownership")
                closed.add(fd)
                finish_call(0)
            elif name == "malloc":
                size = reg("x0")
                check(0 < size <= 65536, "allocation-size")
                address = next_alloc
                next_alloc += (size+31) & ~15
                allocations[address] = size
                finish_call(address)
            elif name == "free":
                address = reg("x0")
                check(address in allocations, "allocation-ownership")
                del allocations[address]
                finish_call(None)
            elif name in ("memcpy", "memset"):
                dest, value, length = reg("x0"), reg("x1"), reg("x2")
                check(length <= 65536, "memory-operation")
                for i in range(length):
                    write(dest+i, read(value+i,1) if name=="memcpy" else value, 1)
                finish_call(dest)
            else:
                raise Reject("unmodeled-external")
            check(frames and reg('x30') == frames[-1], 'call-return')
            pc = frames.pop()
            continue

        check(pc in instructions, "instruction-extent")
        observe(pc)
        op, operands = instructions[pc]
        pc += 4
        args = [s.strip() for s in operands.split(",")] if operands else []
        def branch():
            return int(args[-1].split()[0],16)
        if op in ("b","bl"):
            if op=="bl":
                frames.append(pc)
                put("x30", pc)
            pc = branch()
        elif op == "ret":
            if frames:
                check(reg("x30") == frames[-1], "return-address")
                pc = frames.pop()
            else:
                check(reg("x30")==0xfffffff0 and reg("sp")==1<<48 and phase==2 and closed=={31,32,received_fd} and not allocations and reg("w0")==0,
                      "successful-scm-witness")
                return
        elif op in ("cbz","cbnz"):
            if (reg(args[0])==0) == (op=="cbz"):
                pc = branch()
        elif op in ("tbz","tbnz"):
            if ((reg(args[0]) >> num(args[1])) & 1) == (op=="tbnz"):
                pc = branch()
        elif op.startswith("b."):
            cond = op[2:]
            check(cond in flags, "unknown-condition")
            if flags[cond]:
                pc=branch()
        elif op == "cmp":
            check(len(args)==2, "compare-operands")
            a,b=reg(args[0]),atom(args[1]) % (1 << (8*width(args[0])))
            flags={"eq":a==b,"ne":a!=b,"lo":a<b,"hs":a>=b,"hi":a>b,"ls":a<=b}
        elif op == "mov":
            put(args[0],atom(args[1]))
        elif op in ("add","sub","and","orr","eor","lsl","lsr"):
            check(len(args)==3, "shifted-operand")
            a,b=reg(args[1]),atom(args[2])
            if op=="add": value=a+b
            elif op=="sub": value=a-b
            elif op=="and": value=a&b
            elif op=="orr": value=a|b
            elif op=="eor": value=a^b
            elif op=="lsl": value=a << (b % (8*width(args[0])))
            else: value=a >> (b % (8*width(args[0])))
            put(args[0],value)
        elif op in ("str","ldr","strb","ldrb","strh","ldrh","stp","ldp"):
            match=re.fullmatch(r"([wx][\w]+)(?:,\s*([wx][\w]+))?,\s*\[(sp|x\d+)(?:,\s*(#-?(?:0x[0-9a-f]+|\d+)))?\](!)?(?:,\s*(#-?(?:0x[0-9a-f]+|\d+)))?",operands)
            check(match is not None, "address-mode")
            first,second,base,offset,pre,post=match.groups()
            check(bool(second)==(op in ("stp","ldp")), "pair-width")
            addr=reg(base)+num(offset or "#0")
            if pre:
                put(base,addr)
            size=1 if op.endswith("b") else 2 if op.endswith("h") else width(first)
            for i,r in enumerate((first,second) if second else (first,)):
                if op.startswith("st"):
                    write(addr+i*size,reg(r),size)
                else:
                    put(r,read(addr+i*size,size))
            if post:
                put(base,reg(base)+num(post))
        elif op == "nop":
            pass
        else:
            raise Reject("unsupported-witness-instruction")
    raise Reject("witness-budget")



def witness_program():
    ops = []
    def emit(op, args):
        ops.append((op,args))
    def store(value, off, width="x"):
        emit("mov",width+"9, #"+str(value))
        emit("str",width+"9, [sp, #"+str(off)+"]")
    def pointer(dst, off):
        emit("add","x9, sp, #"+str(off))
        emit("str","x9, [sp, #"+str(dst)+"]")
    emit("sub","sp, sp, #192")
    emit("str","x30, [sp, #176]")
    store(0,0)
    store(0,8)
    pointer(16,72)
    store(1,24)
    pointer(32,96)
    store(24,40)
    store(0,48)
    pointer(72,136)
    store(1,80)
    store(20,96)
    store(1,104,"w")
    store(1,108,"w")
    store(33,112,"w")
    store(0x51,136)
    for name,fd,flags in (("sendmsg",31,0x4000),("recvmsg",32,0)):
        emit("mov","w0, #"+str(fd))
        emit("mov","x1, sp")
        emit("mov","w2, #"+str(flags))
        emit("bl","0x10000" if name=="sendmsg" else "0x10004")
        emit("cmp","x0, #1")
        emit("b.ne","0xdeadc")
    emit("ldr","w0, [sp, #112]")
    emit("bl","0x10008")
    for fd in (31,32):
        emit("mov","w0, #"+str(fd))
        emit("bl","0x10008")
    emit("mov","w0, #0")
    emit("ldr","x30, [sp, #176]")
    emit("add","sp, sp, #192")
    emit("ret","")
    return ops


def witness_controls():
    ops = witness_program()
    def prove(ops,received=47):
        return witness(dict(enumerate_words(ops)),0,{65536:"sendmsg",65540:"recvmsg",65544:"close"},
                       lambda address: None, received_fd=received)
    prove(ops,83)
    prove(ops)
    def reject(mutant,reason):
        try:
            prove(mutant)
        except Reject as exc:
            check(str(exc)==reason,"witness-control-"+reason)
        else:
            raise AssertionError("accepted-"+reason)
    reject([("ret","")]+ops[1:],"successful-scm-witness")
    reject([(op,args) if op!="b.ne" else ("b.eq","0xdeadc")
            for op,args in ops],"instruction-extent")
    reject([(op, "w9, #34" if args=="w9, #33" else args) for op,args in ops],"scm-send-contract")
    print("PASS static successful-send continuation, inert export, infeasible branch and changed descriptor")


def enumerate_words(ops):
    return ((4*i,pair) for i,pair in enumerate(ops))



def loaded_instruction(data, parts, address, encoded):
    chunks = [data[off+address-va:off+address-va+4] for va,off,length,flags in parts
              if flags & 1 and va <= address and address+4 <= va+length]
    words = encoded.split()
    raw = (int(words[0],16).to_bytes(4,"little") if len(words)==1 else bytes.fromhex(encoded))
    check(chunks == [raw], "disassembly-load-bytes")


DT_NEEDED, DT_PLTRELSZ, DT_PLTGOT, DT_HASH, DT_STRTAB, DT_SYMTAB = range(1, 7)
DT_RELA, DT_RELASZ, DT_RELAENT, DT_STRSZ, DT_SYMENT = range(7, 12)
DT_PLTREL, DT_JMPREL = 20, 23
DT_GNU_HASH, DT_VERSYM = 0x6ffffef5, 0x6ffffff0
DT_VERNEED, DT_VERNEEDNUM = 0x6ffffffe, 0x6fffffff
DT_AUXILIARY, DT_FILTER = 0x7ffffffd, 0x7fffffff
DT_CONFIG, DT_DEPAUDIT, DT_AUDIT = 0x6ffffefa, 0x6ffffefb, 0x6ffffefc


def tag_contract(entries):
    tags = dict(entries)
    check(not ({DT_CONFIG, DT_DEPAUDIT, DT_AUDIT, DT_FILTER, DT_AUXILIARY} & tags.keys()),
          "dynamic-loader-override")
    check(len(tags) == len(entries), "duplicate-dynamic-tag")
    check((DT_VERNEED in tags) == (DT_VERNEEDNUM in tags) and
          (DT_VERNEED not in tags or DT_VERSYM in tags), "version-tag-pair")
    for family in ((DT_JMPREL, DT_PLTRELSZ, DT_PLTREL), (DT_RELA, DT_RELASZ, DT_RELAENT)):
        check(not any(t in tags for t in family) or all(t in tags for t in family), "relocation-tag-family")
    check(tags.get(DT_PLTREL, DT_RELA) == DT_RELA and tags.get(DT_RELAENT, 24) == 24,
          "relocation-format")
    return tags


def relocation_bytes(data, entries, segments, rows):
    """Cross-check the loader's actual RELA records against the independent tool listing."""
    tags = tag_contract(entries)
    def file_bytes(address, length):
        offsets = [off+address-va for va,off,size,_ in segments if va<=address and address+length<=va+size]
        check(len(offsets)==1,"relocation-mapping")
        return data[offsets[0]:offsets[0]+length]
    types = {257:"R_AARCH64_ABS64",1025:"R_AARCH64_GLOB_DAT",1026:"R_AARCH64_JUMP_SLOT",
             1027:"R_AARCH64_RELATIVE"}
    observed = {}
    for addr_tag, size_tag in ((DT_RELA,DT_RELASZ),(DT_JMPREL,DT_PLTRELSZ)):
        if addr_tag not in tags:
            continue
        length=tags[size_tag]
        check(length%24==0 and length<=len(data),"rela-size")
        for address,info,addend in struct.iter_unpack("<QQq",file_bytes(tags[addr_tag],length)):
            kind=info & 0xffffffff
            check(kind in types and address not in observed and
                  (kind==1026)==(addr_tag==DT_JMPREL),"relocation-record")
            sym=info>>32
            check((kind==1027)==(sym==0),"relocation-symbol")
            name=""
            if sym:
                index,_,_,_,_,_=struct.unpack("<IBBHQQ",file_bytes(tags[DT_SYMTAB]+24*sym,24))
                check(index<tags[DT_STRSZ],"relocation-string")
                raw=file_bytes(tags[DT_STRTAB]+index,tags[DT_STRSZ]-index)
                check(b"\0" in raw,"relocation-string")
                name=raw.split(b"\0",1)[0].decode("ascii")
            if kind==1026:
                check(addend==0,"plt-addend")
            observed[address]=(info,types[kind],name)
    parsed={}
    for line in rows.splitlines():
        fields=line.split()
        if len(fields)<3 or not fields[2].startswith("R_AARCH64_"):
            continue
        address=int(fields[0],16)
        check(address not in parsed,"duplicate-relocation")
        name=fields[4].split("@")[0] if fields[2]!="R_AARCH64_RELATIVE" and len(fields)>=5 else ""
        parsed[address]=(int(fields[1],16),fields[2],name)
    check(observed==parsed,"relocation-tool-disagreement")



def native_artifact(elf, map_path, inputs):
    import re
    import subprocess
    def tool(*args):
        return subprocess.check_output(args, env={"PATH": "/usr/bin", "LC_ALL": "C"},
                                       stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                       close_fds=True, timeout=90, text=True)
    data = elf.read_bytes()
    dynamic = layout(data)
    root_values = []
    def symbols(path):
        defined, imported = set(), set()
        for row in tool("readelf", "--use-dynamic", "--syms", "--wide", path).splitlines():
            if not re.match(r"^\s*[1-9][0-9]*:", row):
                continue
            fields = row.split()
            check(len(fields) >= 8, "dynamic-symbol-row")
            _, _, _, kind, binding, visibility, section, name = fields[:8]
            if binding == "LOCAL":
                continue
            check(binding in {"GLOBAL", "WEAK"} and visibility in {"DEFAULT", "PROTECTED"}, "symbol-binding")
            base, _, version = name.replace("@@", "@").partition("@")
            if path == elf and section != "UND" and base == "pdva_scm_probe":
                check(kind=="FUNC" and binding=="GLOBAL" and visibility=="DEFAULT", "probe-binding")
                root_values.append(int(fields[1],16))
            (imported if section == "UND" else defined).add((base, version))
        return defined, imported

    tag_contract(dynamic)
    listing = tool("readelf", "-dW", elf)
    needed = re.findall(r"\(NEEDED\)\s+Shared library: \[([^\]]+)\]", listing)
    check(len(needed) == sum(tag == 1 for tag, _ in dynamic), "needed-table")
    loader_root, loader_imports, loader_needed = loader_contract(data, dynamic)
    exports, imports = symbols(elf)
    check(root_values == [loader_root] and imports == loader_imports and needed == loader_needed,
          "dynamic-tables-disagree")
    check(exports == {("pdva_scm_probe", "")}, "export-allowlist")
    stubs = inputs / "ndk/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/30"
    public, _ = symbols(stubs / "libc.so")
    names = ("sendmsg recvmsg close malloc calloc realloc free posix_memalign memcpy memset memmove "
             "memcmp strlen abort __stack_chk_fail __stack_chk_guard __errno read write writev "
             "fcntl pthread_key_create pthread_key_delete pthread_getspecific pthread_setspecific "
             "pthread_mutex_lock pthread_mutex_unlock pthread_once dl_iterate_phdr getauxval").split()
    library_contract({name for name, _ in exports}, imports, needed, {"libc.so": public},
                     {(name, "LIBC") for name in names})
    segments = []
    for i in range(HEADER.unpack_from(data)[10]):
        header = HEADER.unpack_from(data)
        typ, flags, _, addr, _, _, size, _ = PHDR.unpack_from(data, header[5] + i * PHDR.size)
        if typ == 1:
            segments.append((addr, addr + size, flags))
    # Fail closed on packed formats until every target address can be checked.
    check(not any(tag in {35, 36, 37, 0x6000000f, 0x60000010, 0x60000011, 0x60000012,
                          17, 18, 19, 0x6fffe000, 0x6fffe001, 0x6fffe003} for tag, _ in dynamic),
          "packed-relocations")
    relocations = tool("readelf", "--use-dynamic", "-rW", elf)
    relocation_targets(relocations, segments, dynamic)
    text = tool("llvm-objdump-18", "-d", elf)
    whole_map = map_path.read_text()
    check(all(s in whole_map for s in ("libvmm_sys_util.rlib", "liblibc.rlib", "pdva_scm_probe")),
          "missing-map-origins")
    labels = {name: int(addr, 16) for addr, name in
              re.findall(r"^([0-9a-fA-F]+) <([^>]+)>:$", text, re.M)}
    required = ["pdva_scm_probe", "sendmsg@plt", "recvmsg@plt"]
    check(all(name in labels for name in required), "missing-call-endpoint")
    check(root_values == [labels["pdva_scm_probe"]], "export-address")
    parts = []
    for i in range(header[10]):
        typ, flags, off, addr, _, length, _, _ = PHDR.unpack_from(data, header[5] + i * PHDR.size)
        if typ == 1:
            parts.append((addr,off,length,flags))
    relocation_bytes(data, dynamic, parts, relocations)
    external = plt_endpoints(data, parts, labels, relocations)
    origins = account_map(whole_map, inputs, elf.parent, tool)
    instructions = {}
    for line in text.splitlines():
        row = re.match(r"^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]{8}|(?:[0-9a-fA-F]{2}\s+){3}[0-9a-fA-F]{2})\s+([a-z.0-9]+)\s*(.*?)\s*$",line)
        if row:
            address=int(row[1],16)
            check(address not in instructions, "duplicate-instruction")
            loaded_instruction(data,parts,address,row[2])
            instructions[address]=(row[3],row[4].split("//")[0].strip())
    def readonly_byte(address):
        for va,off,size,flags in parts:
            if va <= address < va+size and not flags & 2:
                return data[off+address-va]
        return None
    def origin(address):
        matched=[(family,section) for lo,hi,family,section in origins if lo <= address < hi]
        check(len(matched)==1, "instruction-map")
        return matched[0]
    def call_origin(name, sites):
        operation = name.removesuffix("msg")
        chain = [origin(site) for site in sites]
        check(any(family in {"probe","libvmm_sys_util.rlib"} and
                  ("raw_"+name in section or operation+"_with_fd" in section)
                  for family,section in chain), "scm-method-origin")
    for received in (47,83):
        witness(instructions,labels["pdva_scm_probe"],external,readonly_byte,
                observe=origin,received_fd=received,call_origin=call_origin)
    print("PASS static witness and sealed map input inventory")


def relocation_targets(rows, segments, dynamic):
    accepted = {"R_AARCH64_RELATIVE","R_AARCH64_GLOB_DAT","R_AARCH64_JUMP_SLOT","R_AARCH64_ABS64"}
    sizes = [value for tag,value in dynamic if tag in (2,8)]
    check(all(n%24 == 0 for n in sizes), "rela-size")
    actual = 0
    for line in rows.splitlines():
        if not re.match(r"^\s*[0-9a-fA-F]{8,}\s+[0-9a-fA-F]+\s+",line):
            continue
        parts = line.split()
        check(len(parts)>=3 and parts[2] in accepted,"relocation-kind")
        address=int(parts[0],16)
        check(any(lo<=address and address+8<=hi and flags&2 for lo,hi,flags in segments)
              and not any(address<hi and address+8>lo and flags&1 for lo,hi,flags in segments),
              "relocation-target")
        actual+=1
    check(actual==sum(sizes)//24,"relocation-count")


def binding_controls():
    def refused(fn, reason):
        try:
            fn()
        except Reject as failure:
            check(str(failure)==reason,"binding-control-"+reason)
        else:
            raise AssertionError("accepted-"+reason)
    machine=bytes.fromhex("c0035fd6")
    loaded_instruction(machine,[(0,0,4,5)],0,"d65f03c0")
    loaded_instruction(machine,[(0,0,4,5)],0,"c0 03 5f d6")
    refused(lambda:loaded_instruction(machine,[(0,0,4,5)],0,"14000000"),"disassembly-load-bytes")
    r="00001000 0000 R_AARCH64_JUMP_SLOT 00000000 sendmsg@LIBC + 0"
    relocation_targets(r,[(4096,8192,6)],[(2,24)])
    refused(lambda:relocation_targets(r,[(4096,8192,5)],[(2,24)]),"relocation-target")
    refused(lambda:relocation_targets(r,[(4096,8192,6)],[(2,48)]),"relocation-count")
    refused(lambda:relocation_targets(r.replace("JUMP_SLOT","OTHER"),[(4096,8192,6)],[(2,24)]),"relocation-kind")
    stub=struct.pack("<4I",0xb0000010,0xf9400211,0x91000210,0xd61f0220)
    endpoints=plt_endpoints(stub,[(0,0,16,5)],{"sendmsg@plt":0},r)
    check(endpoints=={0:"sendmsg"},"plt-control")
    refused(lambda:plt_endpoints(stub,[(0,0,16,5)],{"recvmsg@plt":0},r),"plt-binding")
    refused(lambda:plt_endpoints(bytes(16),[(0,0,16,5)],{"sendmsg@plt":0},r),"plt-sequence")
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp).resolve()
        sealed=root/"sealed"
        sealed.mkdir()
        archive=sealed/"libvmm_sys_util.rlib"
        archive.write_bytes(b"fixture")
        line=" 100 100 4 4 /out/libvmm_sys_util.rlib(a.o):(.text.raw_recvmsg)"
        listing=lambda *args: "a.o\n"
        check(account_map(line,root/"inputs",sealed,listing)==[(256,260,"libvmm_sys_util.rlib",".text.raw_recvmsg")],
              "map-positive")
        refused(lambda:account_map(line.replace("a.o","b.o"),root/"inputs",sealed,listing),"runtime-member")
        refused(lambda:account_map(line.replace("libvmm_sys_util","other"),root/"inputs",sealed,listing),"project-archive")
    print("PASS relocation targets, counts, PLT/GOT binding and map member controls")



def loader_contract(data, entries):
    """Decode the dynamic loader's symbol inventory independently of section headers."""
    by_tag = {}
    for tag,value in entries:
        by_tag.setdefault(tag,[]).append(value)
    def one(tag):
        check(len(by_tag.get(tag,())) == 1, "dynamic-tag")
        return by_tag[tag][0]
    h=HEADER.unpack_from(data)
    parts=[PHDR.unpack_from(data,h[5]+i*PHDR.size) for i in range(h[10])]
    def chunk(addr,count):
        matches=[off+addr-va for typ,flags,off,va,_,length,_,_ in parts
                 if typ==1 and va<=addr and addr+count<=va+length]
        check(len(matches)==1,"dynamic-pointer")
        return data[matches[0]:matches[0]+count]
    def u32(a):
        return struct.unpack("<I",chunk(a,4))[0]
    if 4 in by_tag:
        hash_addr=one(4)
        count=u32(hash_addr+4)
        check(0<count<=65536,"dynamic-symbol-count")
        chunk(hash_addr,8+4*(u32(hash_addr)+count))
    else:
        addr=one(0x6ffffef5)
        buckets,first,bloom,_=struct.unpack("<4I",chunk(addr,16))
        check(0<buckets<=65536 and 0<bloom<=65536 and 0<first<=65536,"gnu-hash-size")
        bucket_base=addr+16+bloom*8
        indices=struct.unpack("<"+"I"*buckets,chunk(bucket_base,buckets*4))
        last=max(indices)
        count=first
        if last:
            check(first<=last<65536,"gnu-hash-index")
            chain=bucket_base+4*buckets
            while last<65536 and not u32(chain+4*(last-first))&1:
                last+=1
            check(last<65536,"gnu-hash-chain")
            count=last+1
    require_size=one(10)
    check(0<require_size<=8<<20,"string-table-size")
    strings=chunk(one(5),require_size)
    def string(index):
        end=strings.find(b"\0",index)
        check(index<len(strings) and end>=index,"dynamic-string")
        return strings[index:end].decode("ascii")
    needed=[string(n) for n in by_tag.get(1,())]
    check(len(needed)==1 and needed[0]=="libc.so","needed-allowlist")
    check(one(11)==24,"symbol-stride")
    vers={}
    if DT_VERNEED in by_tag:
        addr=one(DT_VERNEED)
        num=one(DT_VERNEEDNUM)
        check(0<num<=len(needed),"version-count")
        for i in range(num):
            version,n,file,aux,nxt=struct.unpack("<HHIII",chunk(addr,16))
            check(version==1 and string(file) in needed and 0<n<=256 and aux>=16,"version-library")
            auxaddr=addr+aux
            for j in range(n):
                _,_,idx,name,skip=struct.unpack("<IHHII",chunk(auxaddr,16))
                check(1<idx<32768 and idx not in vers,"version-index")
                vers[idx]=string(name)
                check((skip>=16 if j+1<n else skip==0),"version-chain")
                auxaddr+=skip
            check((nxt>=16 if i+1<num else nxt==0),"version-chain")
            addr+=nxt
    versions=(struct.unpack("<"+"H"*count,chunk(one(DT_VERSYM),2*count))
              if 0x6ffffff0 in by_tag else [1]*count)
    table=chunk(one(6),count*24)
    exports=[]
    imported=set()
    for i in range(1,count):
        index,info,other,section,value,size=struct.unpack_from("<IBBHQQ",table,24*i)
        if info>>4==0:
            continue
        check(info>>4 in (1,2) and other in (0,3),"dynamic-binding")
        name = string(index)
        if section==0:
            idx=versions[i]
            check(idx in vers or idx==1,"import-version")
            imported.add((name,vers.get(idx,"")))
        else:
            check(info==0x12 and other==0 and versions[i]==1,"probe-binding")
            exports.append((name,value))
    check(len(exports)==1 and exports[0][0]=="pdva_scm_probe","export-allowlist")
    return exports[0][1], imported, needed


def loader_controls():
    data=fixture()
    data.extend(bytes(1024))
    PHDR.pack_into(data,64,1,5,0,0,0,len(data),len(data),16384)
    strings=b"\0libc.so\0pdva_scm_probe\0sendmsg\0recvmsg\0LIBC\0"
    data[800:800+len(strings)]=strings
    tags=[(1,1),(4,880),(5,800),(10,len(strings)),(6,960),(11,24),
          (0x6ffffff0,1100),(0x6ffffffe,1120),(0x6fffffff,1),(0,0)]
    PHDR.pack_into(data,176,2,4,448,448,0,16*len(tags),16*len(tags),8)
    for i,pair in enumerate(tags):
        DYN.pack_into(data,448+16*i,*pair)
    struct.pack_into("<7I",data,880,1,4,1,0,2,3,0)
    for i,name in enumerate((b"pdva_scm_probe",b"sendmsg",b"recvmsg"),1):
        struct.pack_into("<IBBHQQ",data,960+24*i,strings.index(name),0x12,0,
                         int(i==1),1280 if i==1 else 0,4 if i==1 else 0)
    struct.pack_into("<4H",data,1100,0,1,2,2)
    struct.pack_into("<HHIII",data,1120,1,1,1,16,0)
    struct.pack_into("<IHHII",data,1136,0,0,2,strings.index(b"LIBC"),0)
    struct.pack_into("<I",data,1280,0xd65f03c0)
    allowed={("sendmsg","LIBC"),("recvmsg","LIBC")}
    def inspect(raw):
        root,imports,needed=loader_contract(raw,layout(raw))
        library_contract({"pdva_scm_probe"},imports,needed,{"libc.so":allowed},allowed)
        return root
    check(inspect(data)==1280,"loader-positive")
    for old,new,reason in ((b"libc.so",b"evil.so","needed-allowlist"),
                           (b"sendmsg",b"badcall","import-allowlist"),
                           (b"pdva_scm_probe",b"pdva_bad_probe","export-allowlist")):
        changed=data.replace(old,new,1)
        try:
            inspect(changed)
        except Reject as exc:
            check(str(exc)==reason,"loader-control")
        else:
            raise AssertionError("accepted-"+reason)
    root=inspect(data)
    try:
        witness({root:("ret","")},root,{},lambda a:None)
    except Reject as exc:
        check(str(exc)=="successful-scm-witness","inert-elf-control")
    else:
        raise AssertionError("inert-elf-accepted")
    print("PASS synthetic ELF dynamic tables, changed NEEDED, import, export and inert entry")



def integrated_control():
    """One synthetic file through native_artifact, including its external-tool parsers."""
    import tempfile
    from unittest.mock import patch
    ops = witness_program()
    entry = 0x800
    call_addresses = {0x10000:0x1000, 0x10004:0x1010, 0x10008:0x1020}
    fail = entry + 4*len(ops)
    names = ("sendmsg","recvmsg","close")
    data = bytearray(0x4100)
    data[:512] = fixture()
    struct.pack_into("<H",data,56,4)
    PHDR.pack_into(data,64,1,5,0,0,0,0x1100,0x1100,16384)
    PHDR.pack_into(data,232,1,6,0x4000,0x4000,0,0x100,0x100,16384)
    strings = b"\0libc.so\0pdva_scm_probe\0sendmsg\0recvmsg\0close\0LIBC\0"
    data[800:800+len(strings)] = strings
    tags=[(1,1),(4,880),(5,800),(10,len(strings)),(6,960),(11,24),
          (DT_VERSYM,1100),(DT_VERNEED,1120),(DT_VERNEEDNUM,1),
          (DT_JMPREL,1280),(DT_PLTRELSZ,72),(DT_PLTREL,DT_RELA),(0,0)]
    PHDR.pack_into(data,176,2,4,448,448,0,len(tags)*16,len(tags)*16,8)
    for i,pair in enumerate(tags):
        DYN.pack_into(data,448+16*i,*pair)
    struct.pack_into("<8I",data,880,1,5,1,0,2,3,4,0)
    dynsyms=[]
    for i,name in enumerate(("pdva_scm_probe",*names),1):
        defined=i==1
        struct.pack_into("<IBBHQQ",data,960+24*i,strings.index(name.encode()),0x12,0,int(defined),
                         entry if defined else 0,4*len(ops) if defined else 0)
        dynsyms.append(f"{i}: {entry if defined else 0:x} 4 FUNC GLOBAL DEFAULT "
                       + ("1 "+name if defined else "UND "+name+"@LIBC"))
    struct.pack_into("<5H",data,1100,0,1,2,2,2)
    struct.pack_into("<HHIII",data,1120,1,1,1,16,0)
    struct.pack_into("<IHHII",data,1136,0,0,2,strings.index(b"LIBC"),0)
    reloc=[]
    lines=[f"{entry:016x} <pdva_scm_probe>:"]
    for i,name in enumerate(names):
        slot=0x4000+8*i
        info=((2+i)<<32)|1026
        struct.pack_into("<QQq",data,1280+24*i,slot,info,0)
        addr=0x1000+16*i
        struct.pack_into("<4I",data,addr,0xf0000010,0xf9400211|(i<<10),0x91000210|(8*i<<10),0xd61f0220)
        lines.append(f"{addr:016x} <{name}@plt>:")
        reloc.append(f"{slot:016x} {info:016x} R_AARCH64_JUMP_SLOT 0 {name}@LIBC + 0")
    def register(name):
        return 31 if name=="sp" else int(name[1:])
    for i,(op,args) in enumerate(ops):
        pc=entry+i*4
        a=[token.strip() for token in args.split(",")]
        if op in ("ldr","str"):
            offset=int(re.search(r"#(\d+)",args)[1])
            wide=a[0][0]=="x"
            word=(0xf9000000 if wide else 0xb9000000) | ((op=="ldr")<<22)
            word |= (offset//(8 if wide else 4))<<10 | 31<<5 | register(a[0])
        elif op in ("add","sub"):
            word=(0x91000000 if op=="add" else 0xd1000000) | int(a[2][1:])<<10 | register(a[1])<<5 | register(a[0])
        elif op=="mov":
            word=(0xd2800000 if a[0][0]=="x" else 0x52800000) | int(a[1][1:])<<5 | register(a[0]) if a[1]!="sp" else 0x910003e1
        elif op=="bl":
            addr=call_addresses[int(args,16)]
            word=0x94000000|((addr-pc)//4 & 0x3ffffff)
            args=hex(addr)
        elif op=="cmp":
            word=0xf100041f
        elif op=="b.ne":
            word=0x54000001|(((fail-pc)//4)<<5)
            args=hex(fail)
        elif op=="ret":
            word=0xd65f03c0
        else:
            raise AssertionError(op)
        struct.pack_into("<I",data,pc,word)
        lines.append(f"{pc:x}: {word:08x} {op} {args}")
    struct.pack_into("<I",data,fail,0xd65f03c0)
    lines.append(f"{fail:x}: d65f03c0 ret")
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp).resolve()
        elf=root/"fixture.so"
        elf.write_bytes(data)
        linkmap=root/"fixture.map"
        mid=entry+4*next(i for i,x in enumerate(ops) if x==("bl","0x10000"))+4
        linkmap.write_text(f"{entry:x} {entry:x} {mid-entry:x} 4 /out/libvmm_sys_util.rlib(a.o):(.text.raw_sendmsg)\n"
                           f"{mid:x} {mid:x} {fail+4-mid:x} 4 /out/libvmm_sys_util.rlib(a.o):(.text.raw_recvmsg)\n"
                           "0 0 0 1 /out/liblibc.rlib(c.o):(.note)\n"
                           f"{entry:x} {entry:x} 0 1 pdva_scm_probe\n")
        for lib in ("libvmm_sys_util.rlib","liblibc.rlib"):
            (root/lib).write_bytes(b"!<arch>\n")
        def fixture_tool(argv,**kwargs):
            if argv[0]=="ar":
                return "a.o\nc.o\n"
            if argv[0]=="llvm-objdump-18":
                return "\n".join(lines)
            if "--syms" in argv:
                if argv[-1]==elf:
                    return "\n".join(dynsyms)
                return "\n".join(f"{i}: 10 4 FUNC GLOBAL DEFAULT 1 {name}@@LIBC" for i,name in enumerate(names,1))
            if "-dW" in argv:
                return "(NEEDED) Shared library: [libc.so]"
            if "-rW" in argv:
                return "\n".join(reloc)
            raise AssertionError("unrecognized-tool-in-fixture")
        with patch("subprocess.check_output",side_effect=fixture_tool):
            native_artifact(elf,linkmap,root)
            for offset,fmt,value,reason in (
                (448+8*16,"q",DT_FILTER,"dynamic-loader-override"),
                (448+8*16,"q",DT_AUDIT,"dynamic-loader-override"),
                (448+8*16,"q",0x1234,"version-tag-pair"),
                (448+11*16+8,"Q",17,"relocation-format"),
                (1280+16,"q",1,"plt-addend"),
                (1280+8,"Q",(3<<32)|1026,"relocation-tool-disagreement"),
                (entry,"I",0xd65f03c0,"disassembly-load-bytes")):
                changed=data.copy()
                struct.pack_into("<"+fmt,changed,offset,value)
                elf.write_bytes(changed)
                try:
                    native_artifact(elf,linkmap,root)
                except Reject as exc:
                    check(str(exc)==reason,"integrated-control-"+reason)
                else:
                    raise AssertionError("accepted-"+reason)
    print("PASS integrated native_artifact with synthetic tool transcripts and seven specific refusals")



def integrated_host_tools():
    """Optional Linux integration. Only synthetic assembly is assembled and linked."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp).resolve()
        def run(*args):
            subprocess.run(args,cwd=root,check=True,timeout=60,stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        stub=root/"inputs/ndk/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/30"
        stub.mkdir(parents=True)
        (root/"stub.s").write_text("\n".join(f".globl {n}\n.type {n},%function\n{n}: ret"
                                             for n in ("sendmsg","recvmsg","close"))+"\n")
        (root/"version").write_text("LIBC { global: sendmsg; recvmsg; close; local: *; };\n")
        def assemble(name):
            run("clang","--target=aarch64-linux-gnu","-c",name+".s","-o",name+".o")
        assemble("stub")
        run("ld.lld","-shared","-soname","libc.so","--version-script=version",
            "--hash-style=sysv","stub.o","-o",stub/"libc.so")
        asm=['.section .text.raw_sendmsg,"ax",%progbits','.globl pdva_scm_probe',
             '.type pdva_scm_probe,%function','pdva_scm_probe:']
        for op,args in witness_program():
            if op=="bl":
                name={"0x10000":"sendmsg","0x10004":"recvmsg","0x10008":"close"}[args]
                args=name
            if op=="b.ne":
                args=".Lfailure"
            asm.append(f"  {op} {args}")
            if op=="bl" and args=="sendmsg":
                asm.append('.section .text.raw_recvmsg,"ax",%progbits')
        asm+=[".Lfailure: ret"]

        (root/"a.s").write_text("\n".join(asm)+"\n")
        (root/"c.s").write_text('.section .rodata.fixture,"a",%progbits\n.byte 0\n')
        for obj,lib in (("a","libvmm_sys_util.rlib"),("c","liblibc.rlib")):
            assemble(obj)
            run("ar","rcs",lib,obj+".o")
        run("ld.lld","-shared","--hash-style=sysv","-z","noexecstack","-z","max-page-size=16384",
            "-Map=fixture.map","--whole-archive","libvmm_sys_util.rlib","liblibc.rlib",
            "--no-whole-archive",stub/"libc.so","-o","fixture.so")
        linkmap=root/"fixture.map"
        content=linkmap.read_text()
        for lib in ("libvmm_sys_util.rlib","liblibc.rlib"):
            content=content.replace(lib+"(", "/out/"+lib+"(")
        linkmap.write_text(content)
        native_artifact(root/"fixture.so",linkmap,root/"inputs")



if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        controls()
        direct_call_controls()
        witness_controls()
        binding_controls()
        loader_controls()
        integrated_control()
    elif sys.argv[1:] == ["--self-test-host-tools"]:
        integrated_host_tools()
    elif len(sys.argv) == 5 and sys.argv[1] == "--artifact":
        native_artifact(*map(Path, sys.argv[2:]))
    elif len(sys.argv) == 3 and sys.argv[1] == "--layout":
        file = Path(sys.argv[2])
        check(file.stat().st_size <= 128 << 20, "inspection-size")
        layout(file.read_bytes())
        print("PASS ELF layout only")
    else:
        raise SystemExit("expected --self-test or --layout FILE")
