"""wmvkit —— BH3 7.0 客户端 .wmv 资源包读写工具（只读分析 + 同长度原地补丁）

== 格式结论（全部实测验证） ==

1) 文件 = 多个 UnityFS bundle 首尾拼接
   bundle 总长 = 0x36 + bi_len + sum(block.csize)
   下一个 bundle 必须落在 b"UnityFS\\0" 上或 EOF —— 唯一可靠的自校验。

2) 单个 bundle
   0x00..0x07  "UnityFS\\0"
   0x08..0x35  46 字节被米哈游变换过的头字段（未攻破算法；但
               只要 payload 总长度不变就可以原字节照抄，完全绕过）
   0x36..      blocksInfo，LZ4 流，解压需 16 字节零前缀：
                 hash[16]
                 u8 blockCount
                 blockCount * { u32BE usize, u32BE csize, u16BE flags }
                 u32BE nodeCount
                 nodeCount * { u64BE offset, u64BE size, u32BE flags, asciiz path }
               flags: 2/3 = LZ4，5 = 原样；node flags: 4
   之后        sum(csize) 字节数据块；每块解压后拼成 payload。

3) payload 内按 node.offset/size 切出 SerializedFile（CAB-*）与 .resS（原始流）

4) SerializedFile（version 17 / Unity 2017.4）
   前 16 字节四个 u32 是【大端】(metadataSize/fileSize/version/dataOffset)，
   0x10 之后全部【小端】。enableTypeTree = 0。
   Type 记录变长：classID(4)+isStripped(1)+scriptTypeIndex(2)+oldTypeHash(16)=23，
   若 classID == 114 再 +16 = 39。
   对象地址 = data_offset + byteStart（本作是相对 dataOffset）。
"""
import os
import struct

MAGIC = b"UnityFS\0"
HEADER_LEN = 0x36


# ------------------------------------------------------------------ LZ4
def lz4_decode(src, prefix=b"", max_out=256 * 1024 * 1024, track=False):
    out = bytearray(prefix)
    pre = len(prefix)
    i, n = 0, len(src)
    clean = False
    bounds = []
    srcmap = [] if track else None       # 输出下标 -> 输入下标（-1 表示来自 match）
    if track:
        srcmap = [-1] * pre
    while i < n:
        token = src[i]
        i += 1
        lit = token >> 4
        if lit == 15:
            while True:
                if i >= n:
                    return bytes(out), i, False, bounds, srcmap
                b = src[i]
                i += 1
                lit += b
                if b != 255:
                    break
        if i + lit > n:
            return bytes(out), i, False, bounds, srcmap
        if track:
            srcmap.extend(range(i, i + lit))
        out += src[i:i + lit]
        i += lit
        if len(out) - pre > max_out:
            return bytes(out), i, False, bounds, srcmap
        bounds.append((i, len(out)))
        if i >= n:
            clean = True
            break
        if i + 2 > n:
            return bytes(out), i, False, bounds, srcmap
        off = src[i] | (src[i + 1] << 8)
        i += 2
        if off == 0 or off > len(out):
            return bytes(out), i, False, bounds, srcmap
        ml = (token & 0x0F) + 4
        if (token & 0x0F) == 15:
            while True:
                if i >= n:
                    return bytes(out), i, False, bounds, srcmap
                b = src[i]
                i += 1
                ml += b
                if b != 255:
                    break
        st = len(out) - off
        for k in range(ml):
            out.append(out[st + k])
        if track:
            srcmap.extend([-1] * ml)
        if len(out) - pre > max_out:
            return bytes(out), i, False, bounds, srcmap
    return bytes(out), i, clean, bounds, srcmap


def _u(b, off, n):
    return int.from_bytes(b[off:off + n], 'big')


# ------------------------------------------------------- blocksInfo
def parse_blocks_info(buf, s=16):
    n = len(buf)
    if s + 1 > n:
        return None
    bc = buf[s]
    if not (0 < bc <= 4096):
        return None
    p = s + 1
    blocks = []
    for _ in range(bc):
        if p + 10 > n:
            return None
        usize = _u(buf, p, 4)
        csize = _u(buf, p + 4, 4)
        flags = _u(buf, p + 8, 2)
        if usize == 0 or csize == 0 or usize > (1 << 31) or csize > (1 << 31):
            return None
        if flags not in (0, 1, 2, 3, 4, 5):
            return None
        blocks.append((usize, csize, flags))
        p += 10
    if p + 4 > n:
        return None
    nc = _u(buf, p, 4)
    if not (0 < nc <= 40000):
        return None
    p += 4
    nodes = []
    for _ in range(nc):
        if p + 20 > n:
            return None
        off = _u(buf, p, 8)
        size = _u(buf, p + 8, 8)
        fl = _u(buf, p + 16, 4)
        p += 20
        e = buf.find(b"\0", p)
        if e < 0:
            return None
        path = buf[p:e]
        if not path or len(path) > 512 or not all(32 <= c < 127 for c in path):
            return None
        nodes.append({"offset": off, "size": size, "flags": fl,
                      "path": path.decode("ascii")})
        p = e + 1
    return {"block_count": bc, "blocks": blocks, "node_count": nc,
            "nodes": nodes, "end": p}


# ------------------------------------------------------- bundle
def try_bundle(data, p):
    if data[p:p + 8] != MAGIC:
        return None
    out, used, clean, bounds, _ = lz4_decode(data[p + HEADER_LEN:], bytes(16),
                                             max_out=1 << 20)
    fsize = len(data)
    for bi_len, out_len in bounds:
        if bi_len > (1 << 17):
            break
        r = parse_blocks_info(out[:out_len], 16)
        if not r or r["end"] != out_len:
            continue
        total = HEADER_LEN + bi_len + sum(b[1] for b in r["blocks"])
        if p + total > fsize:
            continue
        nxt = p + total
        if nxt != fsize and data[nxt:nxt + 8] != MAGIC:
            continue
        r.update(start=p, bi_len=bi_len, total=total,
                 data_start=p + HEADER_LEN + bi_len,
                 head_raw=data[p:p + HEADER_LEN])
        return r
    return None


def walk(path=None, data=None):
    if data is None:
        data = open(path, 'rb').read()
    p, out = 0, []
    while p < len(data):
        b = try_bundle(data, p)
        if not b:
            out.append({"ok": False, "start": p, "rest": len(data) - p})
            break
        b["ok"] = True
        out.append(b)
        p = b["start"] + b["total"]
    return data, out


def bundle_payload(data, b):
    p = b["data_start"]
    buf = bytearray()
    for usize, csize, flags in b["blocks"]:
        chunk = data[p:p + csize]
        if len(chunk) != csize:
            return None
        if flags in (2, 3):
            d, u, c, _, _ = lz4_decode(chunk, b"")
            if not c or u != csize:
                return None
            buf += d
        else:
            buf += chunk
        p += csize
    return bytes(buf)


# ------------------------------------------------------- SerializedFile
class R:
    def __init__(self, b, pos=0):
        self.b, self.p = b, pos

    def u8(self):
        v = self.b[self.p]; self.p += 1; return v

    def i16(self):
        v = struct.unpack_from("<h", self.b, self.p)[0]; self.p += 2; return v

    def i32(self):
        v = struct.unpack_from("<i", self.b, self.p)[0]; self.p += 4; return v

    def u32(self):
        v = struct.unpack_from("<I", self.b, self.p)[0]; self.p += 4; return v

    def i64(self):
        v = struct.unpack_from("<q", self.b, self.p)[0]; self.p += 8; return v

    def align4(self):
        self.p = (self.p + 3) & ~3

    def cstr(self):
        e = self.b.index(b"\0", self.p)
        s = self.b[self.p:e].decode("utf-8", "replace")
        self.p = e + 1
        return s

    def raw(self, n):
        v = self.b[self.p:self.p + n]; self.p += n; return v


TYPE_NAMES = {
    1: "GameObject", 4: "Transform", 20: "Camera", 21: "Material", 23: "MeshRenderer",
    28: "Texture2D", 33: "MeshFilter", 43: "Mesh", 48: "Shader", 49: "TextAsset",
    50: "RenderTexture", 54: "Rigidbody", 59: "Cubemap", 60: "OcclusionCullingSettings",
    61: "CullingGroup", 64: "MeshCollider", 65: "BoxCollider", 68: "CapsuleCollider",
    74: "AnimationClip", 75: "ConstantForce", 81: "AudioReverbZone", 83: "AudioClip",
    89: "SphereCollider", 90: "CharacterController", 92: "SpriteRenderer",
    95: "Animator", 96: "TrailRenderer", 102: "TextMesh", 104: "RenderSettings",
    108: "Light", 111: "Animation", 114: "MonoBehaviour", 115: "MonoScript",
    124: "Behaviour", 128: "Font", 129: "PlayerSettings", 137: "SkinnedMeshRenderer",
    142: "AssetBundle", 143: "AssetBundleManifest", 150: "AudioListener",
    152: "GraphicsSettings", 156: "LightmapSettings", 157: "Terrain",
    183: "NavMeshSettings", 188: "ParticleSystem", 189: "ParticleSystemRenderer",
    191: "LODGroup", 193: "Sprite", 194: "SpriteRenderer", 195: "ReflectionProbe",
    212: "SpriteRenderer", 213: "Sprite", 222: "CanvasRenderer", 223: "Canvas",
    224: "RectTransform", 225: "CanvasGroup", 226: "Billboard",
    228: "RuntimeAnimatorController", 240: "AudioMixer", 1001: "Prefab",
    1002: "PrefabInstance",
}


def sf_parse(data):
    h = {}
    h["metadata_size"] = int.from_bytes(data[0:4], "big")
    h["file_size"] = int.from_bytes(data[4:8], "big")
    h["version"] = int.from_bytes(data[8:12], "big")
    h["data_offset"] = int.from_bytes(data[12:16], "big")
    r = R(data, 16)
    h["endian"] = r.u8()
    r.raw(3)
    h["unity_version"] = r.cstr()
    h["target_platform"] = r.i32()
    h["enable_type_tree"] = r.u8()
    tc = r.i32()
    h["type_count"] = tc
    types = []
    for _ in range(tc):
        cid = r.i32()
        t = {"class_id": cid, "is_stripped": r.u8(),
             "script_type_index": r.i16(), "old_type_hash": r.raw(16).hex()}
        if cid == 114:
            t["extra16"] = r.raw(16).hex()
        t["name"] = TYPE_NAMES.get(cid, "cls%d" % cid)
        types.append(t)
    h["types"] = types
    oc = r.i32()
    h["object_count"] = oc
    objs = []
    for _ in range(oc):
        o = {"path_id": r.i64()}
        r.align4()
        o["byte_start"] = r.u32()
        o["byte_size"] = r.u32()
        o["type_id"] = r.i32()
        o["name"] = (types[o["type_id"]]["name"]
                     if 0 <= o["type_id"] < tc else "?")
        o["obj_table_pos"] = r.p - 20
        objs.append(o)
    h["objects"] = objs
    h["obj_table_end"] = r.p
    return h


def sf_objdata(h, data, o):
    a = h["data_offset"] + o["byte_start"]
    return data[a:a + o["byte_size"]]


# ------------------------------------------------------- 同长度原地补丁
def locate_payload_byte(b, off_in_payload):
    """payload 内偏移 -> (block_index, 块内输出偏移)"""
    acc = 0
    for i, (usize, csize, flags) in enumerate(b["blocks"]):
        if acc <= off_in_payload < acc + usize:
            return i, off_in_payload - acc
        acc += usize
    return None, None


def patch_same_length(data, b, payload_off, old, new):
    """把 bundle payload 中 payload_off 处的 old 换成等长 new（只改 LZ4 字面量）。

    返回 (ok, msg)。data 为 bytearray，原地修改。
    """
    if len(old) != len(new):
        return False, "长度不同"
    bi, boff = locate_payload_byte(b, payload_off)
    if bi is None:
        return False, "偏移超出 payload"
    usize, csize, flags = b["blocks"][bi]
    cstart = b["data_start"]
    for j in range(bi):
        cstart += b["blocks"][j][1]
    if flags not in (2, 3):
        return False, "该块未压缩，请用 raw 通道"
    chunk = bytes(data[cstart:cstart + csize])
    out, used, clean, _, srcmap = lz4_decode(chunk, b"", track=True)
    if out[boff:boff + len(old)] != old:
        return False, "payload 内容不匹配（实际 %r）" % out[boff:boff + len(old)]
    # 逐字节检查是否都来自字面量
    ins = []
    for k in range(len(old)):
        s = srcmap[boff + k]
        if s < 0:
            return False, "目标字节位于 LZ4 match 区，无法原地改（第 %d 字节）" % k
        ins.append(s)
    if ins != list(range(ins[0], ins[0] + len(old))):
        return False, "字面量不连续"
    data[cstart + ins[0]:cstart + ins[0] + len(new)] = new
    return True, "ok block#%d 压缩流内偏移 %d" % (bi, ins[0])


def verify_file(path, data):
    """重新走一遍，确认结构完好。"""
    _, bs = walk(data=bytes(data))
    return all(b["ok"] for b in bs), len(bs)
