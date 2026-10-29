# -*- coding: utf-8 -*-
"""metadata 回写器 v1 —— 元数据层修改的地基工具
   可逆回写三块：
   ① fdv 值池（枚举值/const 数值，明文区直写）
   ② fdv string 值（长度前缀+UTF8，需处理长度变化→只能等长或改偏移指向新追加区）
   ③ blob 字面量池（行级流密码 XOR，同长度可直接改）
   安全原则：只操作本地副本 WORK_META，NAS 原件只读
   用法（库方式）:
     from meta_writer import MetaWriter
     w = MetaWriter(r"D:\\Carol-start\\_rea\\work_metadata.dat")
     w.set_enum_value(fieldIdx, 123)          # 改枚举成员值
     w.set_blob_text(rowIdx, "新文本")          # 改字面量(同长度限制)
     w.save()                                  # 写回副本
"""
import struct

M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1

# ---- 全部加密常数（12 轮破解成果复用）----
FDV_TBL = 0x564210          # fieldDefaultValues 表（明文 12B {fi, off, typeIdx}）
FDV_SENT = 0xFFFFFFFF
POOL = 0x1D79938            # 值池（明文）

TBL_BLOB = 0x118 + 0x1EC6620   # blob 描述表 77,396×8B
DATA_BLOB = 0x3185A9C          # blob 数据区

def key_row(i):
    v = (i * 0x1AB6B1E4CD9A) & M64
    v >>= 0xB
    v = (v * 0x6595FC2F) & M64
    v ^= 0x790A43A40000
    v >>= 0x11
    return v & M32

def blob_seed(i):
    v = (i * 0x54CCBD2A6C08DF18) & M64
    v ^= 0x25450C2973B42381
    v = (v * 0x174BDB9B4B2EC230) & M64
    v ^= 0x6F7A46CC48B4908D
    v = (v * 0x2BB71BC476FEFD2E) & M64
    return (v - 0x0EEA8D685E597BCC) & M64

BLOB_STEP = 0x5BB8DBE022B62203


class MetaWriter:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.buf = bytearray(f.read())
        self.n = len(self.buf)
        self.dirty = 0

    # ---------- fdv 表定位 ----------
    def _fdv_row(self, fieldIdx):
        """二分查 fdv 表 {fi 单调递增}"""
        lo, hi = 0, 207815
        while lo < hi:
            mid = (lo + hi) // 2
            fi = struct.unpack_from("<I", self.buf, FDV_TBL + mid * 12)[0]
            if fi < fieldIdx:
                lo = mid + 1
            else:
                hi = mid
        fi = struct.unpack_from("<I", self.buf, FDV_TBL + lo * 12)[0]
        if fi != fieldIdx:
            return None
        off = FDV_TBL + lo * 12
        c1 = struct.unpack_from("<I", self.buf, off + 4)[0]
        if c1 == FDV_SENT:
            return None
        return off, c1

    # ---------- ① 枚举/const 数值 ----------
    def set_enum_value(self, fieldIdx, value, width=4):
        """改枚举成员/const 的数值（明文值池直写，长度不变）"""
        r = self._fdv_row(fieldIdx)
        if r is None:
            raise KeyError("fieldIdx %d 无默认值行" % fieldIdx)
        _, off = r
        fmt = {1: "<B", 2: "<H", 4: "<I", 8: "<Q"}[width]
        if value >= (1 << (width * 8)):
            raise ValueError("值超出 %d 字节宽度" % width)
        struct.pack_into(fmt, self.buf, POOL + off, value)
        self.dirty += 1
        return True

    # ---------- ② blob 字面量（同长度替换）----------
    def blob_info(self, rowIdx):
        off = TBL_BLOB + rowIdx * 8
        k = key_row(rowIdx)
        o = ((struct.unpack_from("<I", self.buf, off)[0] ^ 0x2BE4EEE9) - k) & M32
        l = (struct.unpack_from("<I", self.buf, off + 4)[0] - k - 0x25C2F1A9) & M32
        return o, l

    def get_blob_text(self, rowIdx):
        o, l = self.blob_info(rowIdx)
        kk = blob_seed(rowIdx)
        out = bytearray()
        for q in range((l + 7) >> 3):
            out += (struct.unpack_from("<Q", self.buf, DATA_BLOB + o + q * 8)[0] ^ kk).to_bytes(8, "little")
            kk = (kk + BLOB_STEP) & M64
        return bytes(out[:l]).decode("utf-8", "replace")

    def set_blob_text(self, rowIdx, text):
        """同长度（字节数）替换字面量文本；长度不同则报错（追加区机制 v2 再做）
           尾部不足 8 字节的 qword 按 读-改-写 处理，避免污染相邻行"""
        o, l = self.blob_info(rowIdx)
        data = text.encode("utf-8")
        if len(data) != l:
            raise ValueError("长度不匹配: 原文 %d 字节, 新文 %d 字节（v1 仅支持等长）" % (l, len(data)))
        kk = blob_seed(rowIdx)
        nq = (l + 7) >> 3
        base = DATA_BLOB + o
        for q in range(nq):
            src = data[q * 8:(q + 1) * 8]
            # 原始 qword 读出，保留行尾后的原有字节
            orig = struct.unpack_from("<Q", self.buf, base + q * 8)[0] ^ kk
            ob = orig.to_bytes(8, "little")
            keep = len(ob) - len(src)
            chunk_bytes = src + ob[len(src):]     # 新数据 + 保留行尾外的原字节
            chunk = struct.unpack("<Q", chunk_bytes)[0] ^ kk
            struct.pack_into("<Q", self.buf, base + q * 8, chunk)
            kk = (kk + BLOB_STEP) & M64
        self.dirty += 1
        return True

    # ---------- 保存 ----------
    def save(self, path):
        with open(path, "wb") as f:
            f.write(self.buf)
        return self.n
