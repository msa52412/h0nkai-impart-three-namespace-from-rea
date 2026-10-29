"""从 global-metadata.dat 提取全部明文字符串，按兴趣关键词过滤"""
import sys, io

p = r'BH3_Data/Managed/Metadata/global-metadata.dat'
data = open(p, 'rb').read()

# --- 1. 全文件提取可打印字符串（>=4 字符），只要落在 ASCII 可打印带 ---
strings = []  # (offset, str)
start = None
for i, b in enumerate(data):
    if 32 <= b < 127:
        if start is None:
            start = i
    else:
        if start is not None:
            if i - start >= 4:
                strings.append((start, data[start:i].decode('ascii', 'replace')))
        start = None
if start is not None and len(data) - start >= 4:
    strings.append((start, data[start:].decode('ascii', 'replace')))

print(f'提取到 {len(strings)} 条明文字符串')

# --- 2. 按兴趣关键词分类 ---
KEYWORDS = {
    'UI页面': ['PageContext'],
    '深渊/无尽': ['Endless', 'Abyss'],
    '开放世界': ['Openworld', 'OpenWorld'],
    '等级锁': ['LevelLock', 'LayUp'],
    '资源/清单': ['.wmv', '.xmf', 'Blocks', 'BlockMeta'],
    '哈希/校验': ['md5', 'Md5', 'MD5', 'Hash', 'Check'],
    'IL2CPP/元数据': ['Il2Cpp', 'il2cpp', 'Metadata', 'metadata'],
    '调度/登录': ['Dispatch', 'Gateway', 'query_'],
    '错误码': ['10014', 'errorCode', 'ErrorCode'],
}

out = io.StringIO()
for cat, kws in KEYWORDS.items():
    out.write(f'\n{"="*70}\n# {cat}\n{"="*70}\n')
    hits = set()
    for off, s in strings:
        for kw in kws:
            if kw in s:
                hits.add(s)
                break
    for s in sorted(hits):
        out.write(s + '\n')
    out.write(f'-- 共 {len(hits)} 条\n')

open(r'_ext\re\metadata_strings_catalog.txt', 'w', encoding='utf-8').write(out.getvalue())
print('已写入 _ext/re/metadata_strings_catalog.txt')

# --- 3. 快速看几个关键类的命名空间归属（字符串前后扫）---
print('\n=== 现场抽查（部分） ===')
sample_kws = ['UltraEndlessPreparePageContext', 'OpenworldPreparePageContext',
              'OpenWorldMainStubPageContext', 'TaskPageContext', 'SinDemonExMainStubPageContext']
for sk in sample_kws:
    hits = [s for _, s in strings if sk == s or sk in s]
    print(f'{sk:38s} -> {len(hits)} hits: {hits[:3]}')
