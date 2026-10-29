# -*- coding: utf-8 -*-
"""把本轮实测结论追加到工作记忆（避免 shell 反引号转义问题）。"""
P = r"D:\Carol-start\.workbuddy-ai\memory\2026-10-24.md"

ADD = """

---

## 客户端资源加载链路实测（17:40 追加）

### DLL 封死
`UserAssembly.dll` 带 Authenticode 签名（PE Certificate RVA 0xb604050 size 0x2848）。
改任意字节 -> 签名失效 -> 启动器报「文件缺失 UserAssembly.dll」。
已还原原版：md5 2db62015ae66014f1533c39294ccd1d2，0xA5113B = 7e 08。此 DLL 不可再改。

### 客户端不读 wmv（关键）
一次会话 nginx 日志：`editor_compressed` 16,330 次、`StreamingAsb` 61 次（全是 BlockMeta）、
`.wmv` 0 次（5 次全是 10/22 的 404）。
所有资源来自 `runtime/web/asset_bundle/overseas01/1.1/{data,event,ai}/editor_compressed/`。

### 822 个热更包构成
`data/editor_compressed/data/` 下 822 个 `{uint32}_{SHA1}`，每个逻辑包两份不同 SHA1 副本。
- 17 个明文 UnityFS：lua0-4 各 2 份、excel_output 1 份(298,849B)、setting 2 份、bh 2 份、sv 2 份
- 805 个全加密：首 4 字节随机，整体加密

### 明文包 header 混淆已部分破解
固定位置 XOR 密钥流（17 个文件前 0x30 字节完全相同）。
bundle 大小 = BE int64 @0x10，keystream[0x10..0x17] = 37 79 77 79 3B 9E 77 37
（用 908/938/298849 三个长度交叉验证通过）。
SerializedFile @0xAE，大端，version=17，dataOffset=0x1000，unityVersion@0xC2。

### 否定项
- `excel_output` 是本地化文本池，不是 WorldMapEntry 表（FeatureType/EntryID/WorldMap/newbie37 全 0 命中）
- Lua 是编译字节码，`WorldMapUIManager` 在 10 个 lua 包里 0 命中，字符串碎片化
- `GetWorldMapDataRsp` 是硬编码 blob，只含世界地图开启状态，不含 FeatureType

### wmv 里 prefab 唯一性再确认
全扫 2095 个 bundle：只有 #848（CAB-97db9bad...）同时含 `Task_6` + `WorldMapUIManager`；
#849（CAB-d11852e4...）只含 WorldMapUIManager。之前打的位置没错。

### 关键认知修正
EntryID 1012（迪拉克）在配置里 ContentIDList=[] 为空、UnlockLevel=25、已关闭。
「指向一个打不开的玩法」的表现就是「点击没变化」，之前误判成「补丁没生效」。

### 已装验证实验
`patch_wmv.py set 1005`：Task_6 的 entryID 1006 -> 1005（服务端不存在的 EntryID）。
- 卡变空白 => prefab 补丁生效，wmv 是正确来源
- 卡仍是悬赏委托 => 补丁未被加载，必须攻破 805 个加密包

### 新工具
`D:\\Carol-start\\_rea\\patch_wmv.py` —— 支持 status / set <id> / restore。
技术要点：entryID 低 2 字节在 LZ4 字面量区可原地改；高 2 字节在 match 区改不了，
但 entryID<65536 所以只改低 2 字节即可任意设值。
注意：`wmvkit.patch_same_length` 改 3/4 字节会失败，必须只传 2 字节。

### 文档
`D:\\Carol-start\\_rea\\客户端资源加载链路_实测.md`
"""

with open(P, "a", encoding="utf-8") as f:
    f.write(ADD)
print("已追加 %d 字符" % len(ADD))
