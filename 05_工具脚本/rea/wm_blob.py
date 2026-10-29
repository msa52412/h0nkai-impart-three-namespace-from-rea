# -*- coding: utf-8 -*-
"""解析 GetWorldMapDataReqHandler 里的 protobuf blob。"""
import binascii, struct

HEX = "0800121c080110c0c4f4eb0418bffbaad60720002800300038c0c4f4eb044001121c080210c0c4f4eb0418bffbaad60720002800300038c0c4f4eb044002121c080310c0c4f4eb0418bffbaad6072019281e300038c0c4f4eb044003121c080410c0c4f4eb0418bffbaad60720002800300138c0c4f4eb044004121c080510c0c4f4eb0418bffbaad60720002800300138c0c4f4eb044005121c080610c0c4f4eb0418bffbaad607200f2858300138c0c4f4eb044006121c080710c0c4f4eb0418bffbaad607201e2828300138c0c4f4eb044007121c080810c0c4f4eb0418bffbaad60720002800300138c0c4f4eb044008121c080910c0c4f4eb0418bffbaad60720002800300138c0c4f4eb044009121c080a10c0c4f4eb0418bffbaad60720002800300138c0c4f4eb04400a121c080b10c0c4f4eb0418bffbaad60720002800300138c0c4f4eb04400b121c080c10c0c4f4eb0418bffbaad60720002800300138c0c4f4eb044031121e08bb1010a099aae90518bffbaad6072014286330cd0138a099aae9054079121d081210c0c4f4eb0418bffbaad60720322863300138c0c4f4eb04409e02121e08ad1110a092c3800618bffbaad607200f2858300138a092c3800640b302121e08db1110c0e494a30618bfa2f2a40620002800307a38c0e494a306408103"

NAMES = {1: "world_map_id", 2: "begin_time", 3: "end_time", 4: "hl_min_lv",
         5: "hl_max_lv", 6: "weight", 7: "advance_time", 8: "id"}


def read_varint(b, i):
    r = 0; s = 0
    while True:
        x = b[i]; i += 1
        r |= (x & 0x7F) << s
        if not x & 0x80:
            return r, i
        s += 7


def parse(b):
    i = 0; out = {}
    while i < len(b):
        k, i = read_varint(b, i)
        f, wt = k >> 3, k & 7
        if wt == 0:
            v, i = read_varint(b, i)
            out.setdefault(f, []).append(v)
        elif wt == 2:
            ln, i = read_varint(b, i)
            out.setdefault(f, []).append(b[i:i + ln]); i += ln
        else:
            raise ValueError("wt=%d" % wt)
    return out


d = binascii.unhexlify(HEX)
top = parse(d)
print("retcode =", top.get(1))
rows = top.get(2, [])
print("WorldMapLists 条数 =", len(rows))
print("%-6s %-8s %-12s %-12s %-8s %-8s %-8s" % ("id", "mapId", "begin", "end", "hlMin", "hlMax", "weight"))
for r in rows:
    m = parse(r)
    print("%-6s %-8s %-12s %-12s %-8s %-8s %-8s" % (
        (m.get(8) or [None])[0], (m.get(1) or [None])[0],
        (m.get(2) or [None])[0], (m.get(3) or [None])[0],
        (m.get(4) or [None])[0], (m.get(5) or [None])[0], (m.get(6) or [None])[0]))
