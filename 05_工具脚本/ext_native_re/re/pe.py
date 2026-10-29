"""PE 读取 + 反汇编脚手架：BH3 UnityPlayer.dll 专用。"""
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

DLL = r"D:\BH3\7.0\UnityPlayer.dll"
_pe = pefile.PE(DLL, fast_load=True)
IMAGE_BASE = _pe.OPTIONAL_HEADER.ImageBase
_secs = []
for s in _pe.sections:
    name = s.Name.rstrip(b"\0").decode("ascii", "replace")
    _secs.append((name, s.VirtualAddress, s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData))
with open(DLL, "rb") as f:
    _data = f.read()


def secs():
    return _secs


def off2va(off):
    for name, va, vsz, raw, rsz in _secs:
        if raw <= off < raw + rsz:
            return IMAGE_BASE + va + (off - raw)
    return None


def va2off(va):
    rva = va - IMAGE_BASE
    for name, sva, vsz, raw, rsz in _secs:
        if sva <= rva < sva + max(vsz, rsz):
            return raw + (rva - sva)
    return None


def read_va(va, n):
    off = va2off(va)
    if off is None:
        return b""
    return _data[off:off + n]


def cstr_va(va, maxlen=200):
    b = read_va(va, maxlen)
    i = b.find(b"\0")
    if i >= 0:
        b = b[:i]
    return b.decode("utf-8", "replace")


_md = Cs(CS_ARCH_X86, CS_MODE_64)
_md.detail = True


def disasm(va, n, annotate=True):
    """返回 [(va, size, mnemonic, op_str, bytes)]，并尝试解析 RIP 相对目标。"""
    code = read_va(va, n)
    if not code:
        return []
    out = []
    for ins in _md.disasm(code, va):
        txt = ins.op_str
        if annotate and "rip" in txt:
            try:
                for op in ins.operands:
                    if op.type == 3 and op.mem.base == 41:  # X86_OP_MEM, RIP
                        tgt = ins.address + ins.size + op.mem.disp
                        note = ""
                        s = cstr_va(tgt, 64)
                        if s and s.isprintable() and len(s) > 3:
                            note = '  ; "%s"' % s
                        else:
                            note = "  ; =%#x" % tgt
                        txt = txt + note
            except Exception:
                pass
        out.append((ins.address, ins.size, ins.mnemonic, txt, ins.bytes.hex()))
    return out


def show(va, n, annotate=True):
    for a, sz, mn, ops, hx in disasm(va, n, annotate):
        print("%#012x  %-24s %-8s %s" % (a, hx, mn, ops))
