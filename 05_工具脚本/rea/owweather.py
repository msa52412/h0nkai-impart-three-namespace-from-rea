# -*- coding: utf-8 -*-
"""owweather.py - read / override the client's OWEndlessBattleConfig weather list.

Why this exists
---------------
Dirac Sea (OWEndless, EndlessConfigType=2) has FOUR small-monster areas plus a
boss.  The client builds the weather of every area from
OWEndlessBattleConfig.EnvironmentIDList (one env id per area, the boss reuses
the last one).  OWEndlessPreparePageContext.SetupAreaData (RVA 0x173C630) and
OWEndLessBattleLevelInfo.Refresh (RVA 0x15C4E90) both read that int[] through
OWEndlessBattleConfig.get_EnvironmentIDList (RVA 0x5FDD170), and
OWEndLessBattleLevelInfo.GetEnvironmentIDByLayerIndex (RVA 0x15C3B70) indexes
it with `int[n]` layout (length at +0x18, elements at +0x20).

The shipped table has no 4-area config whose four env ids are all 111, so a
pure server-side table pick can never make the weather 111 everywhere.  The
client binary is signature-checked, so we patch the live ExcelMeta object
instead: fetch the cached meta row, fetch its EnvironmentIDList array, write
the wanted env id into every slot.  Once written, every later Refresh /
SetupAreaData sees the new id (the array object is cached and shared).

Safety
------
* Only the two getters that the client itself calls are invoked, on the game
  main thread through the icall mailbox.
* Before writing we verify the row really is the expected map/areas/score and
  that every current slot holds a known OWEndlessEnvironment id.
* Every read/write is verified by reading it back.

Usage
-----
    python owweather.py probe            # print the client's table row + patch state
    python owweather.py set 111          # write 111 into all 4 weather slots
    python owweather.py set 111 --config 62000
"""
import struct
import sys
import time

sys.path.insert(0, r"D:\BH3\7.0\rea\_rea")
import icall  # noqa: E402

# MoleMole.ExcelMeta.OWEndlessBattleConfig getters (all inside UserAssembly.dll)
RVA_GET_BY_ID = 0x453BA40        # CBEKMDDICBM.NAJIOHCPGNI(int id, byte type) -> meta
RVA_GET_AREA = 0x5FDD0D0         # OWEndlessBattleConfig.get_AreaIDList     -> int[]
RVA_GET_BOSS = 0x5FDD140         # OWEndlessBattleConfig.get_BossAreaIDList -> int[]
RVA_GET_SCORE = 0x5FDD100        # OWEndlessBattleConfig.get_AreaScoreConfigID -> int
RVA_GET_ENV = 0x5FDD170          # OWEndlessBattleConfig.get_EnvironmentIDList -> int[]
RVA_GET_MAP = 0x5FDD1A0          # OWEndlessBattleConfig.get_MapID -> int

DEFAULT_CONFIG = 62000
# EndlessConfigType is the second key component of the meta lookup.  The exact
# value comes from the response object at runtime, so probe a small range and
# accept the first row that matches our map/areas/score fingerprint.
TYPE_CANDIDATES = list(range(0, 12))

KNOWN_ENV_IDS = {
    101, 102, 103, 104, 105, 106, 110, 111, 112, 113, 114, 115, 116, 117,
    118, 119, 120, 121, 122, 123, 124, 125,
    1000, 1001, 1002, 1003, 1004, 1005, 1006,
    1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108,
    2000, 2001, 2002, 2003, 2004,
}


# --------------------------------------------------------------------------
# thin wrappers over the icall mailbox
# --------------------------------------------------------------------------
def _attach():
    pid = icall.find_pid()
    if not pid:
        print("[x] BH3.exe is not running")
        return None
    st = icall.load_state()
    if not st or st.get("pid") != pid:
        print("[i] mailbox is missing or belongs to a dead process - installing")
        if icall.cmd_install() != 0:
            print("[x] mailbox install failed")
            return None
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("[x] mailbox still not bound to pid %s" % pid)
            return None
    h, pid, base = icall.open_game()
    if not h:
        return None
    span = icall.module_span() or 0
    st["base"] = base
    st["span"] = span
    return h, st


def call(st, rva, args, wait=8.0):
    """Invoke one game function on the main thread, return rax."""
    if not (0 <= rva < st["span"]):
        raise RuntimeError("rva %#x outside UserAssembly image" % rva)
    mb = st["mailbox"]
    a = ([st["scratch"] if x == "scratch" else x for x in args] + [0, 0, 0, 0])[:4]
    pkt = b"\x00\x00" + b"\x00" * 6 + struct.pack("<Q", st["base"] + rva)
    pkt += b"".join(struct.pack("<Q", x & 0xFFFFFFFFFFFFFFFF) for x in a)
    pkt += struct.pack("<Q", 0)
    h = st["_h"]
    if not icall.write_mem(h, mb, pkt):
        raise RuntimeError("mailbox write failed")
    if icall.read_mem(h, mb, len(pkt)) != pkt:
        icall.write_mem(h, mb, b"\x00" * len(pkt))
        raise RuntimeError("mailbox echo mismatch")
    if not icall.write_mem(h, mb, bytes([icall.MAGIC])):
        raise RuntimeError("mailbox magic write failed")
    t0 = time.time()
    while time.time() - t0 < wait:
        d = icall.read_mem(h, mb, 2)
        if d and d[0] == 0:
            if d[1] == 1:
                raw = icall.read_mem(h, mb + 0x30, 8)
                if not raw or len(raw) != 8:
                    raise RuntimeError("cannot read mailbox ret")
                return struct.unpack("<Q", raw)[0]
            if d[1] == 2:
                raise RuntimeError("stub refused: target was 0")
        time.sleep(0.02)
    icall.write_mem(h, mb, b"\x00")
    raise RuntimeError("timeout: the game thread did not pick the command up")


def _i32(h, va):
    d = icall.read_mem(h, va, 4)
    if not d or len(d) != 4:
        return None
    return struct.unpack("<i", d)[0]


def _i64(h, va):
    d = icall.read_mem(h, va, 8)
    if not d or len(d) != 8:
        return None
    return struct.unpack("<Q", d)[0]


def array_ints(h, arr, n=None):
    """Read a managed int[]: length at +0x18, elements at +0x20."""
    if not arr:
        return []
    count = _i32(h, arr + 0x18)
    if count is None or not (0 <= count <= 64):
        return []
    if n is None:
        n = count
    n = min(n, count)
    raw = icall.read_mem(h, arr + 0x20, 4 * n)
    if not raw or len(raw) != 4 * n:
        return []
    return list(struct.unpack("<%di" % n, raw))


# --------------------------------------------------------------------------
# find the cached meta row
# --------------------------------------------------------------------------
def find_meta(h, st, config_id):
    for t in TYPE_CANDIDATES:
        meta = call(st, RVA_GET_BY_ID, [config_id, t])
        if not meta or meta < 0x10000 or meta % 8:
            continue
        area = call(st, RVA_GET_AREA, [meta])
        boss = call(st, RVA_GET_BOSS, [meta])
        score = call(st, RVA_GET_SCORE, [meta])
        mp = call(st, RVA_GET_MAP, [meta])
        env = call(st, RVA_GET_ENV, [meta])
        areas = array_ints(h, area)
        bosses = array_ints(h, boss)
        envs = array_ints(h, env)
        if not areas or not envs:
            continue
        # fingerprint: 4 small-monster areas, a boss, map 301 for Dirac Sea
        if len(areas) < 4 or not bosses:
            continue
        if mp != 301 or score < 1000:
            continue
        return {
            "type": t, "meta": meta,
            "area_arr": area, "areas": areas,
            "boss_arr": boss, "bosses": bosses,
            "score": score, "map": mp,
            "env_arr": env, "envs": envs,
        }
    return None


def print_row(info):
    print("  meta          = %#x  (lookup type=%d)" % (info["meta"], info["type"]))
    print("  map           = %d" % info["map"])
    print("  score config  = %d" % info["score"])
    print("  areas         = %s   []@%#x" % (info["areas"], info["area_arr"]))
    print("  boss areas    = %s   []@%#x" % (info["bosses"], info["boss_arr"]))
    print("  weather(env)  = %s   []@%#x" % (info["envs"], info["env_arr"]))


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------
def attempt(probe_only, config_id, want):
    """One shot.  Returns (rc, retryable)."""
    got = _attach()
    if not got:
        return 1, True
    h, st = got
    st["_h"] = h
    try:
        info = find_meta(h, st, config_id)
        if not info:
            print("[!] config %d not found yet (endless table not loaded?)" % config_id)
            return 1, True
        print("== client OWEndlessBattleConfig %d ==" % config_id)
        print_row(info)
        bad = [e for e in info["envs"] if e not in KNOWN_ENV_IDS]
        if bad:
            print("  [!] unknown env ids %s - do NOT patch" % bad)
            return 1, False
        if probe_only:
            return 0, False

        arr = info["env_arr"]
        count = _i32(h, arr + 0x18)
        if count is None or count < 1 or count > 16:
            print("[x] suspicious array length %s at %#x - refusing" % (count, arr))
            return 1, False
        cur = array_ints(h, arr)
        if not cur or len(cur) != count:
            print("[x] cannot read %d ints from %#x - refusing" % (count, arr))
            return 1, False
        klass = _i64(h, arr)
        if not klass or klass < 0x10000 or klass % 8:
            print("[x] array klass ptr looks wrong (%s) - refusing" % klass)
            return 1, False
        if cur == [want] * count:
            print("\n[ok] already set to %d - nothing to do." % want)
            return 0, False

        payload = struct.pack("<%di" % count, *([want] * count))
        if not icall.write_mem(h, arr + 0x20, payload):
            print("[x] write failed")
            return 1, False
        back = array_ints(h, arr)
        print("\n== after ==")
        print("  weather(env)  = %s   []@%#x" % (back, arr))
        if back != [want] * count:
            print("[x] verify failed: read back %s" % back)
            return 1, False

        # re-fetch through the same getter the client uses, to prove the cache
        # still hands out the object we just edited
        env2 = call(st, RVA_GET_ENV, [info["meta"]])
        vals2 = array_ints(h, env2, count)
        print("  getter again  = %s   []@%#x %s"
              % (vals2, env2, "(same object)" if env2 == arr else "(NEW object!)"))
        if env2 != arr:
            print("[!] the getter returned a fresh array - patch may not stick")
        if vals2 != [want] * count:
            print("[x] getter does not see the patch")
            return 1, False

        print("\n[ok] every weather slot for config %d is now %d." % (config_id, want))
        print("     open the Dirac page now, or close and re-open it if it is already open.")
        return 0, False
    except Exception as e:  # noqa: BLE001
        print("[x] %s" % e)
        return 1, True
    finally:
        icall.k32.CloseHandle(h)


def run(probe_only, config_id, want, wait=0):
    deadline = time.time() + max(0, wait)
    while True:
        rc, retryable = attempt(probe_only, config_id, want)
        if rc == 0 or not retryable or time.time() >= deadline:
            return rc
        time.sleep(2)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    argv = sys.argv[2:]
    config_id = DEFAULT_CONFIG
    wait = 0
    if "--config" in argv:
        i = argv.index("--config")
        config_id = int(argv[i + 1], 0)
        del argv[i:i + 2]
    if "--wait" in argv:
        i = argv.index("--wait")
        wait = int(argv[i + 1], 0)
        del argv[i:i + 2]
    if cmd == "probe":
        return run(True, config_id, 0, wait)
    if cmd == "set":
        want = int(argv[0], 0) if argv else 111
        return run(False, config_id, want, wait)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
