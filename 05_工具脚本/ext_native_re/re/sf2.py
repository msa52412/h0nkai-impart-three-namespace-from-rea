"""BH3 SerializedFile（version 17 / Unity 2017.4）解析器。

实测结论：
* 头部 0x00..0x0F 四个 u32 是【大端】；0x10 起所有字段【小端】。
* unityVersion 字符串以 0x0A 结尾（不是 0x00），实际会被读到下一个 0x00。
* enableTypeTree = 0（没有内嵌 type tree）。
* Type 记录变长：
    classID(i32) + isStripped(u8) + scriptTypeIndex(i16) + oldTypeHash[16]   = 23 字节
    若 classID == 114 (MonoBehaviour)，再跟 16 字节附加哈希                 = 39 字节
* 之后：objectCount(i32) + objects[]（i64 pathID, align4, u32 byteStart,
  u32 byteSize, i32 typeID）+ externals + refTypes + userInformation。
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

    def i16(self):
        v = struct.unpack_from("<h", self.b, self.p)[0]
        self.p += 2
        return v

    def u16(self):
        v = struct.unpack_from("<H", self.b, self.p)[0]
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


BASE_TYPES = {
    1: "GameObject", 4: "Transform", 21: "Material", 23: "MeshRenderer",
    28: "Texture2D", 33: "MeshFilter", 43: "Mesh", 48: "Shader",
    49: "TextAsset", 54: "Rigidbody", 59: "Cubemap", 60: "OcclusionCullingSettings",
    64: "MeshCollider", 65: "BoxCollider", 68: "CapsuleCollider",
    74: "AnimationClip", 75: "ConstantForce", 83: "AudioClip",
    89: "SphereCollider", 90: "CharacterController", 95: "Animator",
    96: "TrailRenderer", 102: "TextMesh", 104: "RenderSettings",
    108: "Light", 111: "Animation", 114: "MonoBehaviour", 115: "MonoScript",
    128: "Font", 129: "PlayerSettings", 135: "SphereCollider",
    137: "SkinnedMeshRenderer", 142: "AssetBundle", 143: "AssetBundleManifest",
    144: "UnityBuildSettings", 150: "AudioListener", 152: "GraphicsSettings",
    156: "LightmapSettings", 157: "Terrain", 158: "LightProbeGroup",
    159: "TerrainCollider", 183: "NavMeshSettings", 184: "NavMeshData",
    186: "NavMeshAgent", 187: "NavMeshObstacle", 188: "ParticleSystem",
    189: "ParticleSystemRenderer", 190: "ShaderVariantCollection",
    191: "LODGroup", 192: "Motion", 193: "Sprite", 194: "SpriteRenderer",
    195: "ReflectionProbe", 196: "TerrainData", 197: "LightProbes",
    198: "ParticleSystemRenderer", 199: "ParticleSystem",
    200: "ParticleCollider", 208: "SortingGroup", 212: "SpriteRenderer",
    213: "Sprite", 222: "CanvasRenderer", 223: "Canvas", 224: "RectTransform",
    225: "CanvasGroup", 226: "Billboard", 227: "SpriteMask",
    228: "RuntimeAnimatorController", 229: "AnimatorOverrideController",
    240: "AudioMixer", 1001: "Prefab", 1002: "PrefabInstance",
}


def typename(cid):
    return BASE_TYPES.get(cid, "cls%d" % cid)


def parse(path=None, data=None):
    if data is None:
        data = open(path, 'rb').read()
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
    h["type_count"] = tc = r.i32()
    types = []
    for _ in range(tc):
        t = {"class_id": r.i32(), "is_stripped": r.u8(),
             "script_type_index": r.i16(),
             "old_type_hash": r.raw(16).hex()}
        if t["class_id"] == 114:
            t["extra16"] = r.raw(16).hex()
        t["name"] = typename(t["class_id"])
        types.append(t)
    h["types"] = types
    h["object_count"] = oc = r.i32()
    objs = []
    for _ in range(oc):
        o = {"path_id": r.i64()}
        r.align4()
        o["byte_start"] = r.u32()
        o["byte_size"] = r.u32()
        o["type_id"] = r.i32()
        o["name"] = types[o["type_id"]]["name"] if 0 <= o["type_id"] < tc else "?"
        objs.append(o)
    h["objects"] = objs
    h["externals"] = []
    ne = r.i32()
    for _ in range(ne):
        tmp = r.cstr()
        path_ = r.cstr()
        guid = r.raw(16).hex()
        t = r.i32()
        h["externals"].append({"tmp": tmp, "path": path_, "guid": guid, "type": t})
    h["ref_type_count"] = r.i32()
    h["user_info"] = r.cstr()
    h["meta_parsed_end"] = r.p
    h["meta_end"] = 0x14 + h["metadata_size"]
    return h, data


def objdata(h, data, o):
    return data[o["byte_start"]:o["byte_start"] + o["byte_size"]]


if __name__ == "__main__":
    import sys
    h, data = parse(data=open(sys.argv[1], 'rb').read())
    for k in ("metadata_size", "file_size", "version", "data_offset",
              "unity_version", "target_platform", "enable_type_tree",
              "type_count", "object_count", "ref_type_count"):
        print("  %-18s %r" % (k, h[k]))
    print("  meta 解析结束 0x%x / 期望 0x%x  (%+d)" %
          (h["meta_parsed_end"], h["meta_end"], h["meta_end"] - h["meta_parsed_end"]))
    print("  externals:", [(e["path"], e["type"]) for e in h["externals"]][:6])
    print()
    print("  #  pathid       byteStart  byteSize  typeID  name")
    for i, o in enumerate(h["objects"][:40]):
        print("  %-3d %-12d %-10d %-9d %-6d %s" %
              (i, o["path_id"], o["byte_start"], o["byte_size"],
               o["type_id"], o["name"]))
    if len(h["objects"]) > 40:
        print("  ... 共 %d 个对象" % len(h["objects"]))
