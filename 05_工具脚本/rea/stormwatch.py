# -*- coding: utf-8 -*-
"""stormwatch —— 盯 GetOpenworldEndlessDataReq 的速率，一旦成风暴立刻把 send_brief 关掉。

为什么：2026-10-25 18:02 的经验是「brief 非空 -> 黑屏 + 59 次/秒请求风暴」，
而 18:07 把 send_brief 改回 false 后客户端几秒内恢复。
本脚本把这个回滚做成自动的：风暴一起就改文件，热加载下一帧生效。

用法：
    python stormwatch.py            # 默认阈值 12 次/秒，回滚后退出
    python stormwatch.py 20         # 自定义阈值
    python stormwatch.py 12 --keep   # 只报警，不回滚

日志：_launch/logs/v2_Server.log（只读增量）
安全：只改 run\\abyss_ow.json 的 send_brief 为 false，其它字段原样保留。
"""
import io
import json
import os
import sys
import time

LOG = r'D:\BH3\7.0\_launch\logs\v2_Server.log'
CFG = r'D:\BH3\7.0\server-v2\run\abyss_ow.json'
NEEDLE = 'OpenworldEndlessDataReq'


def rollback():
    with io.open(CFG, encoding='utf-8') as f:
        d = json.load(f)
    d['send_brief'] = False
    tmp = CFG + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, CFG)
    print('[watch] 已回滚 send_brief=false -> %s' % d)


def main():
    threshold = 12
    keep = '--keep' in sys.argv
    for a in sys.argv[1:]:
        if a.isdigit():
            threshold = int(a)

    pos = os.path.getsize(LOG)
    print('[watch] 起点 %d, 阈值 %d 次/秒' % (pos, threshold))
    window = []
    last_report = time.time()
    while True:
        time.sleep(0.25)
        try:
            size = os.path.getsize(LOG)
            if size < pos:          # 日志被轮转
                pos = 0
            if size == pos:
                continue
            with io.open(LOG, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(pos)
                chunk = f.read(size - pos)
            pos = size
        except Exception as e:
            print('[watch] 读日志失败: %s' % e)
            continue

        now = time.time()
        n = chunk.count(NEEDLE)
        if n:
            window.append((now, n))
        window = [x for x in window if now - x[0] <= 2.0]
        rate = sum(x[1] for x in window) / 2.0
        if now - last_report >= 5:
            last_report = now
            total = sum(x[1] for x in window)
            print('[watch] 近 2s 请求 %d 次 (%.1f/s)' % (total, rate))
        if rate >= threshold:
            print('[watch] *** 风暴：%.1f 次/秒 ***' % rate)
            if not keep:
                rollback()
                print('[watch] 回滚完成，退出')
                return 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
