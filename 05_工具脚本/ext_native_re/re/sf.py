"""Unity SerializedFile（version 17 / 2017.4）手工解析器。

头（小端，本作 endianness=0）：
  u32 metadataSize
  u32 fileSize
  u32 version
  u32 dataOffset
  u8  endian
  u8[3] reserved
  asciiz unityVersion
  i32 targetPlatform        (version >= 15? 实测有)
  u8  enableTypeTree
  i32 typeCount
  typeCount x Type{ i32 classID; u8 isStripped; i16 scriptTypeIndex(if v>=16);
                     asciiz oldTypeHash (v>=16);
                     [if enableTypeTree] TypeTree }
  i32 objectCount
  objectCount x Object{ i64 pathID; (align4) u32 byteStart; u32 byteSize; i32 typeID }
"""
import struct


class R:
    def __init__(self, b, pos=0):
        self.b = b
        self.p = pos

    def u8(self):
        v = self.b[self.p]
        self.p += 1
        return v

    def u16(self):
        v = struct.unpack_from("<H", self.b, self.p)[0]
        self.p += 2
        return v

    def i16(self):
        v = struct.unpack_from("<h", self.b, self.p)[0]
        self.p += 2
        return v

    def i32(self):
        v = struct.unpack_from("<i", self.b, self.p)[0]
        self.p += 4
        return v

    def u32(self):
        v = struct.unpack_from("<I", self.b, self.p)[0]
        self.p += 4
        return v

    def i64(self):
        v = struct.unpack_from("<q", self.b, self.p)[0]
        self.p += 8
        return v

    def align4(self):
        self.p = (self.p + 3) & ~3

    def cstr(self):
        e = self.b.index(b"\0", self.p)
        s = self.b[self.p:e].decode("utf-8", "replace")
        self.p = e + 1
        return s

    def raw(self, n):
        v = self.b[self.p:self.p + n]
        self.p += n
        return v


def parse(path=None, data=None):
    if data is None:
        data = open(path, 'rb').read()
    r = R(data)
    h = {}
    # 注意：本作（米哈游）SerializedFile 的前 16 字节数值字段是【大端】，
    # 而 0x14 之后的所有 body 字段是【小端】。已用 targetPlatform=19
    # (StandaloneWindows64)、typeCount=73、classID=115(MonoScript) 三重验证。
    h["metadata_size"] = int.from_bytes(data[0:4], "big")
    h["file_size"] = int.from_bytes(data[4:8], "big")
    h["version"] = int.from_bytes(data[8:12], "big")
    h["data_offset"] = int.from_bytes(data[12:16], "big")
    r.p = 16
    endian = r.u8()
    h["endian"] = endian
    h["big"] = endian != 0
    r.raw(3)
    h["unity_version"] = r.cstr()
    h["target_platform"] = r.i32()
    h["enable_type_tree"] = r.u8()
    h["type_count"] = r.i32()
    types = []
    for _ in range(h["type_count"]):
        t = {}
        t["class_id"] = r.i32()
        t["is_stripped"] = r.u8()
        if h["version"] >= 16:
            t["script_type_index"] = r.i16()
        if h["version"] >= 16:
            t["old_type_hash"] = r.raw(16).hex()
        # TypeTree
        if h["enable_type_tree"]:
            node_count = r.i32()
            strbuf_len = r.i32()
            nodes = []
            for _ in range(node_count):
                nd = {}
                nd["version"] = r.u16()
                nd["level"] = r.u8()
                nd["type_flags"] = r.u8()
                nd["type_str_offset"] = r.u32()
                nd["name_str_offset"] = r.u32()
                nd["byte_size"] = r.i32()
                nd["index"] = r.i32()
                nd["meta_flag"] = r.i32()
                nd["ref_type_hash"] = r.i64()
                nodes.append(nd)
            sbuf = r.raw(strbuf_len)
            t["nodes"] = nodes
            t["sbuf"] = sbuf
        types.append(t)
    h["types"] = types
    h["object_count"] = r.i32()
    objs = []
    for _ in range(h["object_count"]):
        o = {}
        o["path_id"] = r.i64()
        r.align4()
        o["byte_start"] = r.u32()
        o["byte_size"] = r.u32()
        o["type_id"] = r.i32()
        objs.append(o)
    h["objects"] = objs
    return h, data


def typename(class_id):
    return {
        1: "GameObject", 4: "Transform", 21: "Material", 28: "Texture2D",
        43: "Mesh", 48: "Shader", 49: "TextAsset", 74: "AnimationClip",
        83: "AudioClip", 114: "MonoBehaviour", 128: "Font", 142: "AssetBundle",
        213: "Sprite", 222: "CanvasRenderer", 223: "Canvas",
        224: "RectTransform", 225: "CanvasGroup", 226: "Billboard",
        114: "MonoBehaviour", 115: "MonoScript", 212: "SpriteRenderer",
        1001: "Prefab", 1002: "PrefabInstance",
    }.get(class_id, "cls%d" % class_id)


if __name__ == "__main__":
    import sys
    h, data = parse(data=open(sys.argv[1], 'rb').read())
    for k in ("metadata_size", "file_size", "version", "data_offset",
              "endian", "unity_version", "target_platform", "enable_type_tree",
              "type_count", "object_count"):
        print("  %-18s %s" % (k, h[k]))
    print("  types:", [t["class_id"] for t in h["types"]])
    print()
    print("  #  pathid       byteStart  byteSize  typeID  name")
    for i, o in enumerate(h["objects"]):
        print("  %-3d %-12d %-10d %-9d %-7d %s" %
              (i, o["path_id"], o["byte_start"], o["byte_size"],
               o["type_id"], typename(o["type_id"])))
