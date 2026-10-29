# -*- coding: utf-8 -*-
"""PE 工具：节表解析、文件偏移 <-> 虚拟地址、字符串引用查找。"""
import struct


class PE:
    def __init__(self, path):
        self.path = path
        self.data = open(path, "rb").read()
        d = self.data
        e_lfanew = struct.unpack_from("<I", d, 0x3C)[0]
        coff = e_lfanew + 4
        nsec = struct.unpack_from("<H", d, coff + 2)[0]
        optsz = struct.unpack_from("<H", d, coff + 16)[0]
        opt = coff + 20
        magic = struct.unpack_from("<H", d, opt)[0]
        self.is64 = magic == 0x20B
        self.image_base = struct.unpack_from("<Q", d, opt + 24)[0] if self.is64 else struct.unpack_from("<I", d, opt + 28)[0]
        self.sections = []
        sh = opt + optsz
        for i in range(nsec):
            o = sh + i * 40
            name = d[o:o + 8].rstrip(b"\x00").decode("latin1")
            vsize, va, rsize, rptr = struct.unpack_from("<IIII", d, o + 8)
            chars = struct.unpack_from("<I", d, o + 36)[0]
            self.sections.append({"name": name, "va": va, "vsize": vsize,
                                  "rsize": rsize, "rptr": rptr, "chars": chars})

    def off2va(self, off):
        for s in self.sections:
            if s["rptr"] <= off < s["rptr"] + s["rsize"]:
                return self.image_base + s["va"] + (off - s["rptr"])
        return None

    def va2off(self, va):
        rva = va - self.image_base
        for s in self.sections:
            if s["va"] <= rva < s["va"] + max(s["vsize"], s["rsize"]):
                if s["rsize"] == 0:
                    return None
                return s["rptr"] + (rva - s["va"])
        return None

    def section_of_va(self, va):
        rva = va - self.image_base
        for s in self.sections:
            if s["va"] <= rva < s["va"] + max(s["vsize"], s["rsize"]):
                return s
        return None


if __name__ == "__main__":
    import sys
    pe = PE(sys.argv[1] if len(sys.argv) > 1 else r"D:\BH3\7.0\UnityPlayer.dll")
    print("image_base = 0x%X  64位=%s" % (pe.image_base, pe.is64))
    for s in pe.sections:
        print("  %-10s va=0x%08X vsize=0x%-8X rptr=0x%-8X rsize=0x%-8X" %
              (s["name"], s["va"], s["vsize"], s["rptr"], s["rsize"]))
