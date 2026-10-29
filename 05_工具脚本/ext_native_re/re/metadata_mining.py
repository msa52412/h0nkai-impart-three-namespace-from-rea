"""全量导出 metadata stringLiteral 表，并做重点挖掘"""
import sys

p = r'BH3_Data/Managed/Metadata/global-metadata.dat'
data = open(p, 'rb').read()

strings = []
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

with open(r'_ext\re\metadata_all_strings.txt', 'w', encoding='utf-8') as f:
    for off, s in strings:
        f.write(f'{off}\t{s}\n')
print(f'共 {len(strings)} 条 -> _ext/re/metadata_all_strings.txt')

# ---------- 重点挖掘 1：UI/Menus/Page 全部页面路径 ----------
pages = sorted(set(s for _, s in strings if s.startswith('UI/Menus/Page/')))
print(f'\n=== UI/Menus/Page/ 一级页面共 {len(pages)} 个 ===')
tops = {}
for s in pages:
    parts = s.split('/')
    key = parts[3] if len(parts) > 3 else s
    tops.setdefault(key, []).append(s)
for k in sorted(tops):
    print(f'  {k:32s} {len(tops[k])} 个子路径')

# ---------- 重点挖掘 2：Task 页（挑战页） ----------
print('\n=== Task 页面结构 ===')
for s in sorted(set(s for _, s in strings if '/Page/Task' in s or 'TaskPage' in s)):
    print(' ', s)

# ---------- 重点挖掘 3：深渊相关页面 ----------
print('\n=== Endless/OWEndless 页面 ===')
for s in sorted(set(s for _, s in strings if '/Page/' in s and ('Endless' in s or 'Endless' in s.split('/')[-1]))):
    print(' ', s)

# ---------- 重点挖掘 4：本地化 key（深渊名称类） ----------
print('\n=== 深渊相关本地化 key ===')
for s in sorted(set(s for _, s in strings if 'Endless' in s and ('Menu_' in s or 'CL_' in s or 'Text' in s)))[:40]:
    print(' ', s)
