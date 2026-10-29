# -*- coding: utf-8 -*-
"""追加 isFixedEntry 发现到工作记忆。"""
P = r"D:\Carol-start\.workbuddy-ai\memory\2026-10-24.md"

ADD = """

---

## 突破：isFixedEntry 才是卡片绑定的开关（18:00）

### 根因
`MonoWorldMapEntryContainerBase` 序列化布局（对象起始）：
+0x20 entryID / +0x24 index / +0x28 isFixedEntry

**isFixedEntry=0 时，序列化的 entryID 在运行时被完全忽略**，卡片由活动列表动态填充。

12 个槽位实测：
```
1010@0x01CB70 f=1   1000@0x021DB4 f=0 动态   1005@0x02FDB0 f=0 动态
1002@0x02FFF8 f=1   1004@0x040818 f=1        1001@0x044670 f=1
1005@0x04EA20 f=0 动态  1007@0x04F530 f=1    1008@0x0527D0 f=1
1003@0x057178 f=1   1013@0x059F70 f=1        1009@0x0605E8 f=1
```
0x04EA20 就是之前反复改的那个槽位 —— 它是动态槽，所以改 entryID 1006->1012 / 1006->1005
全部无效。不是补丁没生效，是字段根本没被读。

### 两个确认事实
1. 440 个 wmv / 16.13GB 全量裸字节扫描：只有 0a95a351...wmv 含 Task_3/4/6/9 卡片节点
   -> 一直改的文件是对的。其他 wmv 有 MapPanel/Canvas2D/TypeTab/OWEndless，是 UI 其他部分。
2. AssetNativePlugin.dll 导出表全是 wmv 块文件系统 API，IsBlockFileInfoChange 比的是
   FileName_MD5（文件名里的 MD5），不是内容哈希 -> 本地 wmv 内容改动不会被拒绝。

### LZ4 约束
patch_same_length 只能改 LZ4 字面量。entryID 低 1~2 字节是字面量可改；高 2 字节（恒 0）
和 isFixedEntry 那个 0x00 都在 match 区改不了 -> 动态槽无法转固定槽，只能挑本来 f=1 的槽。
整块重压缩方案不可用：block#2 31381B，HC12 压到 31228B，补零后 bundle_payload 返回 None。

### 已装改动
Task_5 卡片（原 1013 角色教学）-> 1012 迪拉克之海，@0x059F70，isFixed=1。
依据：PlayerLog 实证 Task_5 点开是角色教学=1013。
文件长度未变，2095 个 bundle 解析全正常。

### 工具
`D:\\Carol-start\\_rea\\patch_slot.py`
  status / set <0x偏移> <entryID> / restore

### 文档
`D:\\Carol-start\\_rea\\卡片槽位机制_实测.md`

### 判读
- 卡变迪拉克封面 -> 完全成功
- 卡变空白/消失/变灰 -> 机制生效，只是 1012 配置不全（ContentIDList=[]、UnlockLevel=25）
- 毫无变化 -> prefab 真没被加载，必须攻破 editor_compressed 的 805 个加密包

### 下一步硬骨头
EntryID 1012 的 FeatureType/ContentIDList 来自客户端 excel（OODENFBANCC <- FNPIAMHMCKC），
服务端 WorldMap.json 改不动。要可玩必须让 ContentIDList 非空。
"""

with open(P, "a", encoding="utf-8") as f:
    f.write(ADD)
print("已追加 %d 字符" % len(ADD))
