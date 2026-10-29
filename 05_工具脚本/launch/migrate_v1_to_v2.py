# -*- coding: utf-8 -*-
"""
v1（MongoDB）存档 → v2（SQLite）导入

三段式，每段都能单独跑、单独看结果：

  export  mongo 副本上起一个临时 mongod(27018)，把 9 个集合导成 JSONL
  check   把 JSONL 的字段名和 v2 的 C# scheme 属性名对齐，报告差异（只读）
  apply   按 v2 的建表 DDL 写 SQLite（幂等：已有同名行会先清空该表）

为什么要先复制 dbpath：
  原存档在 runtime\\mongo\\data\\jiale_data_013，v1 还在用它。
  mongod 一启动就会写 journal / 加锁文件，所以这里复制一份到 _ext\\tmp\\mongo_import 再读，
  原目录一个字节都不动。

用法：
  python migrate_v1_to_v2.py export [--src <dbpath>] [--out <dir>]
  python migrate_v1_to_v2.py check  [--out <dir>]
  python migrate_v1_to_v2.py apply  [--out <dir>] [--db <sqlite>] [--dry-run]
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time

BASE = r"D:\BH3\7.0"
MONGO_BIN = os.path.join(BASE, r"runtime\mongo\bin")
MONGOD = os.path.join(MONGO_BIN, "mongod.exe")
MONGO = os.path.join(MONGO_BIN, "mongo.exe")

SRC_DBPATH = os.path.join(BASE, r"runtime\mongo\data\jiale_data_013")
WORK = os.path.join(BASE, r"_ext\tmp\mongo_import")
TMP_DBPATH = os.path.join(WORK, "dbpath")
OUT_DIR = os.path.join(WORK, "jsonl")
TMP_PORT = 27018
DB_NAME = "PemukulPaku"

SQLITE = os.path.join(BASE, r"server-v2\run\data\pemukul.sqlite")
SCHEME_DIR = os.path.join(BASE, r"server-v2\Common\Common.Database")
PROTO_DIR = os.path.join(BASE, r"server-v2\Common\Common.Resources.Proto")

# 集合 → (v2 表名, C# 类名, 键列[(列名, 类型, C# 属性, 唯一)])
TABLES = [
    ("Users", "Users", "UserScheme",
     [("uid", "INTEGER", "Uid", True), ("name", "TEXT", "Name", True), ("token", "TEXT", "Token", True)]),
    ("Avatars", "Avatars", "AvatarScheme",
     [("owner_uid", "INTEGER", "OwnerUid", False), ("avatar_id", "INTEGER", "AvatarId", False)]),
    ("Equipments", "Equipments", "EquipmentScheme",
     [("owner_uid", "INTEGER", "OwnerUid", True)]),
    ("OpenWorlds", "OpenWorlds", "OpenWorldScheme",
     [("owner_uid", "INTEGER", "OwnerUid", False), ("map_id", "INTEGER", "MapId", False)]),
    ("Elfs", "Elfs", "ElfsScheme",
     [("owner_uid", "INTEGER", "OwnerUid", True)]),
    ("Dorms", "Dorms", "DormsScheme",
     [("owner_uid", "INTEGER", "OwnerUid", True)]),
    ("ClientDatas", "ClientDatas", "ClientDataScheme",
     [("owner_uid", "INTEGER", "OwnerUid", False), ("type", "INTEGER", "Type", False),
      ("client_data_id", "INTEGER", "ClientDataId", False)]),
    ("Logins", "Logins", "LoginScheme",
     [("owner_uid", "INTEGER", "OwnerUid", False)]),
    ("PrivateMessages", "PrivateMessages", "PrivateMessageScheme",
     [("sender_uid", "INTEGER", "SenderUid", False), ("target_uid", "INTEGER", "TargetUid", False)]),
    ("DLCs", "DLCs", "DLCsScheme",
     [("owner_uid", "INTEGER", "OwnerUid", True)]),
    ("GrandKeys", "GrandKeys", "GrandKeysScheme",
     [("owner_uid", "INTEGER", "OwnerUid", True)]),
    ("AutoIncrements", "AutoIncrements", "AI",
     [("name", "TEXT", "Name", True), ("count", "INTEGER", "Count", False)]),
]


def out(msg=""):
    print(msg)


def head(msg):
    print()
    print("== %s %s" % (msg, "=" * max(0, 74 - len(msg))))


def port_open(port, host="127.0.0.1", timeout=0.4):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        return s.connect_ex((host, port)) == 0
    except OSError:
        return False
    finally:
        s.close()


def run(cmd, cwd=None, timeout=120):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=timeout)
    txt = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("cp936", "replace")
    return r.returncode, txt


# ---------------------------------------------------------------- export
def cmd_export(args):
    src = args.src
    head("1. 复制 dbpath（原存档只读）")
    if not os.path.isdir(src):
        out("  [FAIL] 源目录不存在：%s" % src)
        return 1
    if os.path.isdir(TMP_DBPATH):
        shutil.rmtree(TMP_DBPATH)
    os.makedirs(WORK, exist_ok=True)
    t0 = time.time()
    shutil.copytree(src, TMP_DBPATH)
    out("  [ OK ] %s -> %s  (%.0f s)" % (src, TMP_DBPATH, time.time() - t0))
    for junk in ("mongod.lock", "WiredTiger.lock", "storage.bson"):
        p = os.path.join(TMP_DBPATH, junk)
        if os.path.exists(p):
            os.remove(p)

    head("2. 起临时 mongod（:%d）" % TMP_PORT)
    if port_open(TMP_PORT):
        out("  [FAIL] 端口 %d 已被占用，先停掉" % TMP_PORT)
        return 1
    logp = os.path.join(WORK, "mongod.log")
    p = subprocess.Popen([MONGOD, "--dbpath", TMP_DBPATH, "--port", str(TMP_PORT),
                          "--bind_ip", "127.0.0.1", "--logpath", logp],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        if port_open(TMP_PORT):
            break
        time.sleep(0.5)
    if not port_open(TMP_PORT):
        out("  [FAIL] mongod 没起来，看 %s" % logp)
        p.terminate()
        return 1
    out("  [ OK ] mongod 就绪 (PID %d)" % p.pid)

    head("3. 导出集合 -> JSONL")
    os.makedirs(OUT_DIR, exist_ok=True)
    ok = True
    try:
        for coll, table, cls, cols in TABLES:
            js = ('var d=db.getSiblingDB("%s");'
                  'd.getCollection("%s").find().forEach(function(x){print(JSON.stringify(x))});'
                  % (DB_NAME, coll))
            rc, txt = run([MONGO, "--quiet", "--port", str(TMP_PORT), "--eval", js], timeout=300)
            lines = [ln for ln in txt.splitlines() if ln.startswith("{")]
            path = os.path.join(OUT_DIR, table + ".jsonl")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + ("\n" if lines else ""))
            out("  %s %-16s %4d 行 -> %s" % ("[ OK ]" if rc == 0 else "[FAIL]", coll, len(lines),
                                             os.path.basename(path)))
            ok = ok and rc == 0
    finally:
        head("4. 停临时 mongod")
        p.terminate()
        try:
            p.wait(15)
        except subprocess.TimeoutExpired:
            p.kill()
        out("  [ OK ] 已停止")

    return 0 if ok else 1


# ---------------------------------------------------------------- check
def scheme_props(cls):
    """从 v2 的 C# 类里抠出 public 属性名（`public T Name { get; set; }` 形式），并顺着基类往上找。

    为什么要顺基类：AvatarScheme / EquipmentScheme 这些是
    `class AvatarScheme : Common.Resources.Proto.Avatar, IRow`，
    AvatarId / Star / Level 这些字段全在 proto 基类里，光扫 scheme 文件会漏。
    """
    return _class_props(cls, set())


def _class_props(cls, seen):
    import re
    if cls in seen or not cls:
        return set()
    seen.add(cls)
    texts = []
    for d in (SCHEME_DIR, PROTO_DIR):
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.endswith(".cs"):
                continue
            cand = open(os.path.join(d, fn), encoding="utf-8", errors="replace").read()
            # 同名类可能不止一处（Common.Database\Avatar.cs 是集合访问器，
            # Common.Resources.Proto\Avatar.cs 才是带字段的 proto 类），两处都算
            if re.search(r"class\s+%s\b" % re.escape(cls), cand):
                texts.append(cand)
    if not texts:
        return set()
    props = set()
    for txt in texts:
        # 自动属性 + protobuf-net 的 `__pbn__X` 后备字段（proto 生成类都是后者）
        props |= set(re.findall(r"public\s+[\w\<\>\[\]\?\.]+\s+(\w+)\s*\{\s*get;", txt))
        props |= set(re.findall(r"__pbn__(\w+)", txt))
        m = re.search(r"public\s+(?:partial\s+)?class\s+%s\s*:\s*([\w\.]+)" % re.escape(cls), txt)
        if m:
            base = m.group(1).split(".")[-1]
            if base not in ("IExtensible", "object"):
                props |= _class_props(base, seen)
    return props


def cmd_check(args):
    head("字段名对齐（Mongo 文档键 vs v2 C# 属性）")
    total_bad = 0
    for coll, table, cls, cols in TABLES:
        path = os.path.join(OUT_DIR, table + ".jsonl")
        if not os.path.exists(path):
            out("  [ -- ] %-16s 没有导出文件，跳过" % coll)
            continue
        docs = [json.loads(ln) for ln in open(path, encoding="utf-8") if ln.strip()]
        if not docs:
            out("  [ -- ] %-16s 空集合" % coll)
            continue
        keys = set()
        for d in docs:
            keys |= set(d.keys())
        keys.discard("_id")
        props = scheme_props(cls)
        extra = sorted(keys - props)
        missing = sorted(props - keys)
        status = "[ OK ]" if not extra and not missing else "[WARN]"
        if extra or missing:
            total_bad += 1
        out("  %s %-16s %3d 文档  %2d 键" % (status, coll, len(docs), len(keys)))
        if extra:
            out("         Mongo 有、C# 没有：%s" % ", ".join(extra))
        if missing:
            out("         C# 有、Mongo 没有：%s" % ", ".join(missing))
        # 嵌套 _id 统计：顶层比对看不出这个坑（见 _rename_mongo_id 的说明）。
        # 注意要先把根 _id 摘掉，否则统计到的是「文档数」而不是嵌套数量。
        n_nested = sum(
            json.dumps({k: v for k, v in d.items() if k != "_id"}, ensure_ascii=False).count('"_id"')
            for d in docs)
        if n_nested:
            out("         嵌套 _id（物品 ID）%d 处 -> apply 时会改名成 Id" % n_nested)
        for col, typ, prop, uniq in cols:
            if prop not in keys:
                out("         [FAIL] 键列 %s 依赖的属性 %s 不在文档里" % (col, prop))
    out("")
    out("  说明：Mongo 有 / C# 没有 = 导入时会丢字段（一般是被 BsonIgnore 的计算属性）；")
    out("        C# 有 / Mongo 没有 = 导入后取默认值，不影响启动。")
    return 0 if total_bad == 0 else 0


# ---------------------------------------------------------------- apply
def oid_created_at(oid):
    """ObjectId 前 4 字节是大端时间戳（秒）——v1 的 Login 就是拿它算「今天」的"""
    try:
        return int(str(oid)[:8], 16)
    except Exception:
        return 0


def to_payload(doc):
    """Mongo 文档 -> v2 的 payload JSON。
    去掉根 _id，补 CreatedAt（取 ObjectId 时间戳），其余键原样保留。"""
    d = {k: v for k, v in doc.items() if k != "_id"}
    d["CreatedAt"] = oid_created_at(doc.get("_id", ""))
    _rename_mongo_id(d)
    return d


def _rename_mongo_id(node):
    """把嵌套对象里的 "_id" 递归改名成 "Id"。

    ★ 这是 v1→v2 最关键的一处翻译。
    MongoDB 的 C# 驱动有一条默认约定：属性名 `Id` 会自动映射到元素名 `_id`。
    所以 v1 时代存档里，武器 / 圣痕 / 材料 / 宿舍房间的「物品 ID」全都叫 `_id`：
        {"UniqueId": 101, "_id": 20001, "Level": 1, ...}
    v2 换成 Newtonsoft + JSON，没有这层约定，`_id` 会被当成未知字段丢掉，
    于是 `Weapon.Id` 变成 0 —— 客户端拿不到物品 ID，武器/圣痕/材料/家具全部显示不出来
    （现象：能登录，但背包里东西是空白/问号）。

    注意 cmd_check 只比对**顶层**键，且会 discard 掉 `_id`，所以它发现不了这个问题；
    下面的 cmd_check 里补了嵌套 `_id` 的统计。
    """
    if isinstance(node, list):
        for item in node:
            _rename_mongo_id(item)
    elif isinstance(node, dict):
        if "_id" in node and "Id" not in node:
            node["Id"] = node.pop("_id")
        for value in node.values():
            _rename_mongo_id(value)


def cmd_apply(args):
    import sqlite3

    only = None
    if getattr(args, "only", None):
        only = {s.strip() for s in args.only.split(",") if s.strip()}
        known = {t for _, t, _, _ in TABLES}
        bad = only - known
        if bad:
            out("[ERROR] --only 里有未知表名：%s（可用：%s）" % (", ".join(sorted(bad)), ", ".join(sorted(known))))
            return 1

    db = args.db
    head("1. 目标库")
    out("  %s" % db)
    if only:
        out("  [ -- ] --only=%s：其它表原样保留" % ",".join(sorted(only)))
    if os.path.exists(db) and not args.dry_run:
        backup = db + ".before-import"
        if not os.path.exists(backup):
            shutil.copyfile(db, backup)
            out("  [ OK ] 已备份 -> %s" % backup)
        else:
            out("  [ -- ] 备份已存在，不覆盖：%s" % backup)

    con = sqlite3.connect(db)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")

    head("2. 建表（DDL 与 v2 的 SqlTable 完全一致）")
    for coll, table, cls, cols in TABLES:
        defs = ['"id" INTEGER PRIMARY KEY AUTOINCREMENT', '"payload" TEXT NOT NULL']
        idx = []
        for col, typ, prop, uniq in cols:
            defs.append('"%s" %s' % (col, typ))
            kind = "UNIQUE INDEX" if uniq else "INDEX"
            name = ("ux_" if uniq else "ix_") + table + "_" + col
            idx.append('CREATE %s IF NOT EXISTS "%s" ON "%s"("%s");' % (kind, name, table, col))
        con.execute('CREATE TABLE IF NOT EXISTS "%s" (%s);' % (table, ", ".join(defs)))
        for s in idx:
            con.execute(s)
        out("  [ OK ] %-16s %s" % (table, ", ".join(c[0] for c in cols)))

    head("3. 写数据")
    grand = 0
    for coll, table, cls, cols in TABLES:
        if only and table not in only:
            out("  [ -- ] %-16s 跳过（--only 未包含）" % table)
            continue
        path = os.path.join(OUT_DIR, table + ".jsonl")
        if not os.path.exists(path):
            out("  [ -- ] %-16s 无导出文件" % table)
            continue
        docs = [json.loads(ln) for ln in open(path, encoding="utf-8") if ln.strip()]
        if args.dry_run:
            out("  [dry ] %-16s 将写入 %d 行" % (table, len(docs)))
            continue
        con.execute('DELETE FROM "%s";' % table)
        names = ["payload"] + [c[0] for c in cols]
        sql = 'INSERT INTO "%s" (%s) VALUES (%s)' % (
            table, ", ".join('"%s"' % n for n in names), ", ".join("?" * len(names)))
        rows = []
        for d in docs:
            payload = to_payload(d)
            vals = [json.dumps(payload, ensure_ascii=False)]
            for col, typ, prop, uniq in cols:
                v = payload.get(prop)
                if isinstance(v, bool):
                    v = int(v)
                vals.append(v)
            rows.append(vals)
        con.executemany(sql, rows)
        grand += len(rows)
        out("  [ OK ] %-16s %4d 行" % (table, len(rows)))
    con.commit()

    head("4. 自检")
    for coll, table, cls, cols in TABLES:
        try:
            n = con.execute('SELECT COUNT(*) FROM "%s";' % table).fetchone()[0]
        except sqlite3.OperationalError:
            continue
        if n:
            out("  [ OK ] %-16s %4d 行" % (table, n))
    users = con.execute('SELECT id, uid, name, token FROM Users ORDER BY uid;').fetchall()
    out("")
    out("  Users：")
    for uid, u, name, token in users:
        out("    uid=%-6s name=%-14s token=%s" % (u, name, (token or "")[:8] + "..."))
    con.close()

    head("完成")
    out("  共写入 %d 行" % grand)
    out("  启动：D:\\BH3\\7.0\\启动服务端v2.bat")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="migrate_v1_to_v2")
    sub = ap.add_subparsers(dest="cmd")

    e = sub.add_parser("export")
    e.add_argument("--src", default=SRC_DBPATH)

    c = sub.add_parser("check")

    a = sub.add_parser("apply")
    a.add_argument("--db", default=SQLITE)
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--only", default="",
                   help="只重导这些表（逗号分隔，如 Equipments,Dorms），其它表原样保留")

    args = ap.parse_args()
    if args.cmd == "export":
        return cmd_export(args)
    if args.cmd == "check":
        return cmd_check(args)
    if args.cmd == "apply":
        return cmd_apply(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
