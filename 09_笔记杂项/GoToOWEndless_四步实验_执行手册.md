# GoToOWEndless 四步实验 · 执行手册

> 2026-10-25。依据 `bodies_merged.tsv` @`1819C5E00`（反编译体）+ `bh3_symtab.tsv`（符号表）
>
> - `UserAssembly.dll` 原生反汇编三方交叉验证。>     
>   工具：`gotoow.py`（本目录）。



---

## 一、三个地址（已核实，别再猜）

| 符号                                             | RVA         | VA            | 签名                                            |
| ---------------------------------------------- | ----------- | ------------- | --------------------------------------------- |
| `MonoClientPacketConsumer.Update`              | `0x21D2550` | `0x1821D2550` | icall 宿主，钩子只打一次                               |
| `OWEndlessModule.OnGetOpenworldEndlessDataRsp` | `0x189A7D0` | `0x18189A7D0` | `bool(proto.GetOpenworldEndlessDataRsp)`，实例方法 |
| `OWEndlessModule.GoToOWEndless`                | `0x19C5E00` | `0x1819C5E00` | `void()`，**无参实例方法**                           |

> 上一轮记的 `0x19C5E00` 是对的，但换算 VA 时曾误写成 `0x199C5E00`（少进一位）。>   
> 正确 VA = `0x180000000 + 0x19C5E00` = **`0x1819C5E00`**。

入口字节（`fn.py` 实测）：

```
0x18189A7D0  4889542410   mov [rsp+0x10], rdx     ; 参数 rspill
0x18189A7D5  48894c2408   mov [rsp+8], rcx        ; ← rcx = this，钩子抓这里
0x18189A7DA  55 56 57 4156 push rbp/rsi/rdi/r14   ; 够 14 字节，可安全覆盖
```

---

## 二、修正一个旧结论：NRE 不是加载轮返回 null

反编译体（`bodies_merged.tsv` @`1819C5E00`，12041 字符）还原如下：

```c
void OWEndlessModule::GoToOWEndless() {          // rcx = this
  if (!IFix::WrappersManagerImpl::IsPatched(0x108d7)) {
    this_01 = (LoadingWheelWidgetForTwoRspContext *)il2cpp::codegen::object_new(...);
    LoadingWheelWidgetForTwoRspContext::_ctor(this_01, 0xd5c, 0xd7c, NULL);
    if (this_01 == NULL) raise_null_reference_exception();   // ← 死代码，object_new 不会返回 null
    this_01->SetIgnoreMaxWaitTimeForReq(0xd5b);
    this_02 = new KeyGeneratedEventHandler(this, <回调>);
    this_01->cmdCallBack = this_02;
    if (MainUIManager == NULL) raise_null_reference_exception();      // ← 真·空引用点 1
    MainUIManager::ShowWidget(MainUIManager, this_01, 0);
    if (NetworkManager == NULL) raise_null_reference_exception();     // ← 真·空引用点 2
    // 尾调 RequestOWEndlessData：TwoEndless::GetActiveMode → ModeToType → 发 3419
  } else {
    GetPatch(0x108d7) → __Gen_Wrap_13(this)      // 热更路径，正常不走
  }
}
```

**结论修正**：之前的「owgoto NRE = 等错 CmdID」不准确。  
`object_new` 永远返回非空，那个判空是编译器插的死代码。  
真正会炸的是 **`MainUIManager` / `NetworkManager` 单例为空** —— 也就是  
**必须在主界面、UI 系统已初始化时调用**，在加载画面或登录前调必崩。

---

## 三、两个 CmdID 的含义（**已推翻旧结论**）

| 立即数     | 十进制  | 协议                           | 服务端有没有                                        |
| ------- | ---- | ---------------------------- | --------------------------------------------- |
| `0xd5c` | 3420 | `GetOpenworldEndlessDataRsp` | **有**，`GetOpenworldEndlessDataReqHandler` 会回  |
| `0xd7c` | 3452 | `EndlessInSettleNotify`      | 没有，但**不需要**（见下）                               |
| `0xd5b` | 3419 | `GetOpenworldEndlessDataReq` | 有 handler，`SetIgnoreMaxWaitTimeForReq` 作用在它身上 |

### 旧结论（错）

> 「`ForTwoRsp` 顾名思义等两个包，3452 服务端不发 → 加载轮常转 → 要给服务端补 notify。」

### 实测反汇编（对）

`LoadingWheelWidgetForTwoRspContext._ctor` @`0x180915D50`：

```asm
mov  dword ptr [rcx+0xa0], 0x40a00000   ; maxWaitTime = 5.0f
movzx r14d, r8w                         ; r14 = waitCmd2
movzx r15d, dx                          ; r15 = waitCmd1
mov  word ptr [rbx+0xb2], r15w          ; waitCmd1 = 0xd5c (3420)
mov  word ptr [rbx+0xb4], r14w          ; waitCmd2 = 0xd7c (3452)
mov  qword ptr [rbx+0xb8], rbp          ; timeOutCallBack = r9 = null
```

`OnPacket` @`0x180915860`：

```asm
call OFFEBKADMCL                        ; 取 pkt 的 cmdId → ax
cmp  ax, word ptr [rbx+0xb2]            ; == waitCmd1 ?
je   MATCH
cmp  ax, word ptr [rbx+0xb4]            ; == waitCmd2 ?
jne  return false                       ; 两个都不是 → 不管
MATCH:
     ; 过滤器 [+0xc8] 为 null（ctor 置 0），跳过
     ; 调 cmdCallBack [+0xc0]，然后清空
     call Finish                        ; ← 命中任意一个就关轮
```

**`waitCmd1` 与 `waitCmd2` 是 OR，不是 AND。**  
`ForTwoRsp` 的意思是「这个请求可能被两种包之一应答」（正常 Rsp 或某种 Notify），  
命中任一即 `Finish()`。

→ **服务端只要回 3420，加载轮就会关。3452 不需要，服务端一行都不用改。**

### 但换出一个新风险

`SetIgnoreMaxWaitTimeForReq(0xd5b)` @`0x180915A50` 第一句就是：

```asm
mov byte ptr [rbx+0xd0], 1     ; ignoreMaxWaitTime = true
```

也就是**把 5 秒兜底关掉了**。所以：

| 情况           | 结果                                        |
| ------------ | ----------------------------------------- |
| 3420 正常到达    | `cmdCallBack(pkt)` → `Finish()` → 轮子关，继续走 |
| 3420 **没**到达 | 轮子**永远转**（兜底已被禁用）                         |

所以真正的观测点不是 3452，而是「**3419 发出去之后 3420 有没有回来**」。  
服务端 `GetOpenworldEndlessDataReqHandler` 一定会回，这条链路目前看是通的。

### 仍未定：`cmdCallBack` 指向谁

```c
this_02 = new KeyGeneratedEventHandler(this, _DAT_189b0e4b8);
this_01->cmdCallBack = this_02;
```

`_DAT_189b0e4b8` 是 il2cpp 运行时才填的元数据槽，文件里读出来是  
`50 e0 34 08 9f 79 21 01`（不是代码地址），**静态解析不出来**。

影响：如果这个回调才是「真正跳转到深渊页面」的动作，那 3420 到了就该看到界面；  
如果它只是刷新数据，轮子关了也不会跳页面。  
这一点只能**实测看画面**来区分 —— 也正是第 ④ 步要观察的。

---

## 四、四步怎么跑

```bat
cd /d D:\BH3\7.0\rea\_rea
set PY=C:\Users\Administrator\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe
set PYTHONIOENCODING=utf-8

%PY% check_stub.py             :: 0 离线校验 stub 结构（不用开游戏，11 项全绿才往下走）
%PY% gotoow.py diag            :: 0' 看全入口/信箱/捕获槽/钩子四处状态
%PY% gotoow.py 1               :: ① 在 Update 入口挂常驻信箱（三道自检）
%PY% gotoow.py probe --seconds 15  :: ①' 盯信箱 15 秒，必须「0 次变化」才继续
%PY% gotoow.py 2               :: ② 挂 OnGetOpenworldEndlessDataRsp，捕获 rcx
%PY% gotoow.py 3 --timeout 180 :: ③ 挂着等；此时去游戏里点「世界地图→出击→开放世界」
%PY% gotoow.py 4               :: ④ GoToOWEndless(this)
%PY% gotoow.py revert          :: 收工还原（撤钩子 + 还原入口）
```

判读：

| 现象                      | 含义                                                    | 下一步                                            |
| ----------------------- | ----------------------------------------------------- | ---------------------------------------------- |
| `check_stub` 有 ✗        | stub 结构不对                                             | 绝对不要 install                                   |
| ① 报「信箱自检失败」             | 那块地址不归我们                                              | 换地址重来，别硬上                                      |
| `probe` 报「有外部写入」        | 信箱被别的组件占用                                             | 换地址或换宿主函数                                      |
| ③ 打印 `✓ 捕获到 this`       | 钩子链路通，`this` 拿到                                       | 跑 ④                                            |
| ③ 一直抓不到                 | 客户端没发 3419，或没点对按钮                                     | 看服务端日志有没有 `[Abyss] GetOpenworldEndlessDataReq` |
| ④ 出现加载轮并关掉              | **打通**（3420 已回，回调已执行）                                 | 记录画面：有没有跳进深渊页                                  |
| ④ 加载轮常转不关               | **3420 没回来**（5 秒兜底已被 `SetIgnoreMaxWaitTimeForReq` 禁用） | 查服务端日志有没有回 3420；不要再去补 3452                     |
| ④ **黑屏 + 3419 风暴（已实测）** | 视图装配失败，`OnViewSet` 每帧重试 → 每帧重发 3419                   | 见第七节；查 `MonoOWEndlessUIManager` 视图为什么装不起来      |
| ④ 报「stub 拒绝执行」(done=2)  | target 被清成 0                                          | 见第五节，跑 probe 定位                                |
| ④ 直接崩溃                  | 单例为空 / 时机不对                                           | 确认在主界面再调                                       |

**注意**：③ 之前不要重启游戏 —— `.icall.json` 里的信箱随进程失效，重启要重跑 ①②。

---

## 五、2026-10-25 15:17 那次崩溃 · 取证与加固

### 现场

`error.log`：

```
Exception: Access Violation (0xc0000005)  Write to location 00000000
RIP: 0x00000000   RBX: 0x006a0000
Stack: 0x0014f848: 006a1039 0000...
```

三个数对上了：

- `RBX = 0x006a0000` 就是信箱基址（stub 里 `mov rbx, r11` 的结果）
- 栈顶 `0x006a1039` 落在 stub 体内（stub 在 `page+0x1000`），是 `call r11` 的下一条
- `RIP = 0` 说明 `r11` 读出来是 0，`call r11` 直接跳到地址 0

即：**stub 走了「有命令」分支，但 target 槽是 0。**

### 成因

旧 stub 只有一道判断：

```
cmp byte [r11], 0      ; pending
jne orig               ; pending == 0 → 跑原函数
... call [rbx+8]       ; 否则当有命令
```

`pending` 只要有**任何一个非 0 字节**就进命令分支，完全不管 target 是否有效。  
于是 pending 被写成 1、target 为 0 时，就是 `call 0`。

### 加固（三道闸）

| # | 措施                      | 失败时的行为        |
| - | ----------------------- | ------------- |
| 1 | `pending` 必须等于魔数 `0xA5` | 当「没命令」，跑原函数   |
| 2 | `target != 0` 才调用       | 走 bail，不 call |
| 3 | bail 时 `done = 2`       | 外部可观测，不再静默失败  |

配套的投递侧校验：

- `cmd_call` 拒绝 `target == 0` 的投递
- 写完整包后**回读比对**，不一致就放弃（pending 不置位）
- 置魔数后再回读一次确认
- `cmd_install` 三道自检：信箱写全 0 读回全 0 / stub 落地字节一致 / 入口指向正确，任一失败就回滚并退出

stub 从 75 → 109 → **115 字节**（多出 `jmp restore` + `bail: done=2` 共 6 字节）。  
`check_stub.py` 用 capstone 离线验 11 项，当前全绿。

### 顺带修掉的隐患

`SCRATCH_OFF = 0x2000`、文档写「0x6000 字节」，而 `HOOK_BASE_OFF = 0x4000`。  
scratch 名义上盖到 0x7FFF，**和钩子槽重叠**。任何用 `--arg0 scratch` 的函数  
一旦往 0x4000 以后写，就会把捕获 stub 打烂。  
已把 scratch 收窄到 `0x2000~0x3FFF`（0x2000 字节），文档同步改正。

### 还没定论的一点

`target` 为什么会变成 0，目前没有直接证据。两种可能：

1. **投递侧竞态**：`write_mem(pkt)` 与 `write_mem(MAGIC)` 之间被插了一脚
2. **地址被占**：`0x006a0000` 这块并不专属我们，进程内有别的东西在写

`probe` 就是用来区分这两者的：15 秒内如果信箱「0 次变化」，说明内存安静，  
倾向 (1)，加固后应当不再复现；如果报「有外部写入」，就是 (2)，必须换地址。

---

## 六、当前客户端补丁状态（与本实验无关，但会影响你看到的画面）

`patch_slot.py status`（2026-10-25 实测）：

```
0x59F70  entryID=1007  isFixed=1     ← 原 Task_5（角色教学 1013）被改成 1007
0x4EA20  entryID=1005  isFixed=0     ← 动态槽，改 entryID 无效
其余 10 个槽位保持原值
```

`0x59F70` 现在指向 **1007**（旧版迪拉克 EntryID，`FeatureType [3]`，  
但 `forceShowContent=2 = ForceToHide`、`ContentIDList=[]`），所以那张卡大概率是空卡或被隐藏。

本实验**完全不依赖**这张卡 —— 走的是直接调函数，不经过 `CheckEntryValid` 门禁。  
要还原：`python patch_slot.py set 0x59F70 1013`（Task_5 角色教学）或 `restore`。

---

## 七、④ 实测结果（2026-10-25 15:42）· 3419 风暴 + 黑屏

### 结果

| 项         | 结果                                                        |
| --------- | --------------------------------------------------------- |
| ① install | ✓ 三道自检通过，信箱 `0x29a70000`、stub `0x29a71000`（115 字节）        |
| probe 15s | ✓ **0 次变化** —— 信箱安静，上次的脏字节不是常态                            |
| ② hook    | ✓ 覆盖 15 字节 `48 89 54 24 10 48 89 4c 24 08 55 56 57 41 56` |
| ③ 捕获 this | ✓ `0x70059d9ddd0`，klass `0xe586a80`，耗时 22.2s              |
| ④ 调用      | ✓ **未崩溃**，`rax=1`，0.05s 返回                                |
| ④ 后果      | ✗ **界面黑屏（可点击）+ 服务端被 3419 打爆**                             |

### 风暴数据

按秒统计 `GetOpenworldEndlessDataReq`：

```
15:42:29  x25     15:42:30  x60     15:42:31  x60     ...
15:43:34  x46     累计约 3900 次，稳定 60 次/秒（= 帧率）
撤销全部钩子后重测：仍 120 次/秒持续（两个实例 × 60fps）
```

### 风暴不是我们的 stub 打的

`cmd_call` 返回后信箱状态：`pending=0x00, done=0x01, target=0x7ffeca735e00`。  
**只有 `cmd_call` 会写 `pending=0xA5`，且全程只写了一次** → stub 只执行了一次。  
另外**撤销全部补丁后风暴照旧**，与我们的补丁无关。

顺带：`done=2` 那道闸在实战里验证成功 —— 投一个 `target=0` 的假命令，  
stub 拒绝执行并置 `done=2`，**没有崩溃**（上一轮就是栽在这个场景）。

### 调用链（`whocall.py` 抓返回地址得到）

```
BaseContext.OnViewSet            RVA 0x306FC8E  (0x306FC8E-0x306F9B0 = +0x2DE)
  └→ MonoOWEndlessUIManager.SetupView   RVA 0x185AF00  (+0x9A)
       └→ NetworkManager.RequestOWEndlessData  RVA 0x1AC59D0   ← 无条件，无守卫
            └→ 发 3419
```

- `SetupView` 里那句 `NetworkManager::RequestOWEndlessData()` 在 **+0x9A，前面没有任何条件判断**：    
  只要 `SetupView` 被调，就必发一次 3419。
- `OnGetOpenworldEndlessDataRsp`（回包处理）**不调用 `SetupView`**，它只做    
  `EndlessBaseData::Refresh` / `RefreshMyScoreByMainRsp` / `RefreshMyItemListByMainRsp` /    
  `RefreshUserLocalData` / `QTInLevelData::Refresh`，最后 `return false`。    
  **所以闭环不在回包处理里。**

### 结论

`OnViewSet` 正常只应在视图装配完成时调**一次**。现在每帧都在调，说明  
**视图装配一直没有成功完成** —— 黑屏就是这个失败的外在表现，  
每帧重试一次 `SetupView`，就每帧重发一次 3419。

即：**黑屏是原因，3419 风暴是症状**，不是反过来。

下一步要查的是「`MonoOWEndlessUIManager` 的视图为什么装不起来」——  
大概率是 prefab / 资源缺失，或 `SetupView` 中途异常返回导致框架重试。  
可继续用 `whocall.py` 往上抓 `OnViewSet` 的调用者，或看 `SetupView` 的返回值/异常路径。

### 事故处置

- 四处入口已全部还原为原始字节（Update / SetupView / RequestOWEndlessData / OnGetOpenworldEndlessDataRsp）
- `.icall.json` 对应进程已失效，重开游戏后需重跑 ①
- 服务端未做任何改动（**不需要补 3452**，见第三节）
- 游戏需重启才能退出该状态

---

## 八、新增工具

| 文件                | 用途                                                  |
| ----------------- | --------------------------------------------------- |
| `check_stub.py`   | capstone 离线校验 stub 结构（11 项），不开游戏也能跑                 |
| `extract_body.py` | 从 948MB 的 `bodies_merged.tsv` 流式取反编译体（首列是**大写** VA） |
| `whocall.py`      | 在任意函数入口挂「只读型」stub，捕获 `[rsp]` 返回地址 → 反查调用者符号         |

---


## 九、④ 黑屏的根因（已实证，未再调用 GoToOWEndless）

### 怎么查的（不拿游戏去赌）

`whocall.py --rcx` 挂 `OWEndlessModule.OnPacket`（RVA `0x189AFD0`），收包时 `rcx` 就是 `this`，
几秒内抓到实例，**全程不调用任何游戏函数**。然后用 `inspect_ow.py` / `precheck_ow.py` 只读 + 调两个 getter。

### OWEndlessModule 字段偏移

来自 `GetCurrentEndlessData`（RVA `0x18981B0`）的反汇编：

| 字段 | 偏移 |
|---|---|
| `PreActivity_k_BackingField` | `+0x50` |
| `TwoEndless_k_BackingField` | `+0x58` |
| `baseDataList` | `+0x68` |

il2cpp `List<T>` 布局：`+0x10 _items`、`+0x18 _size`（**int32**）、`+0x20 _version`。
⚠ 把 `_size` 当 u64 读会得到 `0x3_0000_0002` 这种怪值，低 32 位才是真实条数。

### 实测

```
baseDataList 共 2 条，元素 +0x10 分别为 2(Openworld) 和 3(Quantum)
GetActiveMode()          = 4  (Ultra)
GetCurrentEndlessData()  = 0x0  (null)
```

### 因果链

```
CurStatus.EndlessType = Ultra(4)
  → GetActiveMode() = 4
    → baseDataList 固定只有 {2 Openworld, 3 Quantum}，没有 4
      → GetCurrentEndlessData() = null
        → SetupView 在 0x18185B0A2 抛 NRE
          → 视图装配失败（黑屏）
            → BaseContext.OnViewSet 每帧重试
              → SetupView+0x9A 无条件 RequestOWEndlessData
                → 60~120 次/秒的 3419 风暴
```

### 关键理解：`TwoEndless` = 「两套旧深渊」

`TwoEndless` 就是 **迪拉克之海(Openworld) + 量子奇点(Quantum)** 这两套。
`baseDataList` 是模块初始化时建的**固定两条**，与 `NextStatusLists` 无关
（所以 Greedy=5 根本不在列表里）。

`OnGetEndlessStatusRsp` 只调 `TwoEndless.Refresh` + `RefreshPreGeneralActivity`，
**都不碰 `baseDataList`**。

### 修法

让 `CurStatus.EndlessType` 变成 2 或 3：

```
游戏内聊天打： abyss legacy 2        （→ 迪拉克之海；回退用 abyss legacy 5）
```

`AbyssCommand` 的 `case "legacy"` → `AbyssConfig.SetSelected(2)`，热生效。

**但客户端只在登录时请求 `GetEndlessStatusReq`**（实测全程仅 2 次），
所以改完**必须重新登录**（或重开面板）让客户端重新拉一次状态。

连带风险已排查：`RefreshPreGeneralActivity` 在 mode 2/3 时会访问 `[this+0x50] PreActivity`，
实测非 null，不会在状态回包里抛异常。

### 放行判据

改完重新登录后跑：

```
python precheck_ow.py <this>
```

- `GetCurrentEndlessData() != 0` → 放行，可以调 `GoToOWEndless`
- `== 0` → 拦截（exit 2），说明状态还没生效

---

## 十、新增工具（第二批）

| 文件 | 用途 |
|---|---|
| `whocall.py --rcx` | 抓任意实例方法的 `this`（不调用函数，纯捕获）|
| `inspect_ow.py` | 只读倒出 module / TwoEndless / baseDataList / 元素内存 |
| `precheck_ow.py` | 调 `GoToOWEndless` 前的放行闸：先算 `GetActiveMode` + `GetCurrentEndlessData` |

---

## 十一、环境依赖（这次补齐的）

- `capstone` / `pefile`：项目内嵌 python 没有，已装进
  `C:\Users\Administrator\.workbuddy-ai\binaries\python\envs\default`（`icall.py`/`fn.py` 都依赖）
- `fn.py` 原先硬编码 `D:\Carol-start\_rea`，该目录已不存在 → 已改为相对本目录
  （`peutil.py` / `addr2name.json` 本地都有副本）
- 控制台中文/符号乱码：跑脚本前设 `PYTHONIOENCODING=utf-8` 并
  `[Console]::OutputEncoding=[Text.Encoding]::UTF8`

---

## 十二、第二次黑屏的真正阻塞点（2026-10-25 16:xx）· OWEndlessGroup 查表落空

### 结论先行

预检放行（`GetActiveMode()=2`、`GetCurrentEndlessData()=0x700fdf65840` 非空）、
`GoToOWEndless` 也返回 1，但**仍然黑屏 + 仍然 119.5 次/秒的 3419 风暴**。

原因不是「`GetCurrentEndlessData` 判空」那一处。真正的 NRE 抛在：

```
MonoOWEndlessUIManager.RefreshPlayerGroup + 0x404     (VA 0x18185994E 的调用点)
```

### 完整链条（逐层实证）

**第 1 层：`RefreshPlayerGroup` 里到底做了什么**

```asm
0x1818598ED  call IsPatched(0x2853)              ; IFix 热修分支，实测走未打补丁路径
0x1818598F9  call GetCurrentEndlessData(rbx)
0x181859901  je   -> NRE                          ; data == null
0x181859907  rax = data->[0x20]                   ; = EndlessBaseData.<Group>
0x18185992E  je   -> NRE                          ; Group == null
0x18185993B  ebx = Group->[0x24]                  ; = GroupInfo._GroupLevel
0x18185994E  call GetOWEndlessGroupMetaByKey(ebx)
0x181859956  je   0x181859C4F  -> NRE             ; ← 实际命中的就是这一处
```

**第 2 层：字段偏移靠布局表确认，不是猜的**

`bh3_layout.tsv` 里 `MoleMole.EndlessBaseData`：

| 偏移 | 字段 | 类型 |
|---|---|---|
| +0x10 | `<Mode>` | EndlessMode |
| +0x18 | `<Schedule>` | ScheduleInfo |
| **+0x20** | **`<Group>`** | **GroupInfo** |
| +0x28 | `<BattleLevelInfo>` | OWEndLessBattleLevelInfo |

`GroupInfo`：

| 偏移 | 字段 | 类型 |
|---|---|---|
| +0x10 | `<Mode>` | EndlessMode |
| +0x18 | `_rsp` | proto.GetOpenworldEndlessDataRsp |
| +0x20 | `<_GroupID>` | int |
| **+0x24** | **`<_GroupLevel>`** | **int** ← 喂给查询的就是它 |
| +0x28 | `<_CurTopGroupLevel>` | int |
| +0x2C | `<_TopGroupPlayerNum>` | int |

**第 3 层：`GetOWEndlessGroupMetaByKey` 自己又把 mode 塞进 key**

```asm
0x183506277  call GetActiveMode
0x183506293  movzx edx, bl          ; 第 2 参 = (byte)GetActiveMode()
0x183506296  mov   ecx, edi         ; 第 1 参 = 入参（即 _GroupLevel）
0x1835062A2  jmp   OAMJKBBEFOK      ; 尾调用，真正的字典查询
```

`OAMJKBBEFOK` 再尾调 `DJNNGHGDNGL`（0x18419CC80）。

所以查询 key 是 **二元组 `(_GroupLevel, EndlessType)`**，不是单一 GroupLevel。

**第 4 层：这张表的 API 全集（`OWEndlessGroupMetaReaderExtend`）**

```
GetOWEndlessGroupMetaByKey(int GroupLevel)                     0x3506220  ← 内部用 GetActiveMode()
GetOWEndlessGroupMetaByKey(int GroupLevel, EndlessMode mode)   0x35062C0  ← 真正的重载
GetGroupByPlayerGroup(List<..>, int playerGroup)               0x3505E50
GetGroupCountByGroupLevel(int level)                           0x3506030
GetTopGroupLevel()                                             0x3506300
GetTopLevelPlayerGroup()                                       0x35063A0
IsGroupLevelMinInPlayerGroup(..)                               0x3506440
LoadFromFileAndBuildMap / ..Async / BuildMap / Clear
```

### 一个重要的排除：不是「表整张缺失」

扫了整个 `il2cpp` 段（rva 0x52E000~0x6C58B2A）的 `E8 rel32`：

| 目标 | 直接调用点数 |
|---|---|
| `GetOWEndlessGroupMetaByKey(1参)` | **28** |
| `GetOWEndlessGroupMetaByKey(2参)` | **10** |
| `BuildMap` | 5 |
| `LoadFromFileAndBuildMap` | **0** |
| `LoadFromFileAndBuildMapAsync` | **0** |

- 28 个调用点说明这是一张被大量使用的真实表，**不可能整张不存在**。
- 两个 `LoadFromFile*` 直接调用点为 0 → 它由 ExcelManager 通过方法表/反射统一驱动，
  所以「静态找不到调用者」是正常的，不代表没被调用。

### 还剩两种可能，需要一次运行时读操作来区分

| 可能 | 判据 |
|---|---|
| **A. `_GroupLevel` 的值不在表里** | `GetOWEndlessGroupMetaByKey(_GroupLevel, 2) == null`，但相邻 level 有行 |
| **B. 表在 mode=2 下整段为空** | 所有 level 在 mode=2 下都 null |

服务端 `GetOpenworldEndlessDataReqHandler` 目前发的是：

```csharp
uint groupLevel = session.Player.User.AbyssGroupLevel;
if (groupLevel == 0) groupLevel = 1u;      // 兜底 1
rsp.GroupId = 1u;  rsp.GroupLevel = groupLevel;
rsp.CurTopGroupLevel = 22u;                // ← 22 这个数字是硬编码的
```

`CurTopGroupLevel=22` 暗示分组等级上限是 22，`GroupLevel=1` 理论上该有行；
但 `AbyssGroupLevel` 在历史实验里被改成过 8，未必合法。

### 下一步：`probe_group.py`（纯只读，30 秒）

游戏重启登录后跑：

```
python probe_group.py            # 纯观察
python probe_group.py 25 --load  # 若表级接口全 0，再尝试手动 LoadFromFileAndBuildMap()
```

它会打印：

1. `GetActiveMode()`
2. `EndlessBaseData -> Group` 的 `_GroupID` / `_GroupLevel` / `_CurTopGroupLevel`（**真实值**）
3. `GetTopGroupLevel()` / `GetTopLevelPlayerGroup()`（0 就说明表没加载）
4. `level 1..25 × mode{2, active}` 的 `GetGroupCountByGroupLevel` 和 `GetOWEndlessGroupMetaByKey` 结果表
5. 直接给结论：A 还是 B；A 的话给出「服务端该下发哪个 GroupLevel」

只调三类东西：`GetCurrentEndlessData`（getter）、`GetTopGroupLevel` 等表级 getter、
`GetOWEndlessGroupMetaByKey`（字典查询）。不装配 UI、不写业务字段。

### 顺带修掉的一个坑

`disasm.py` 里的 `DLL` 常量一直指向 `D:\BH3\7.0\UnityPlayer.dll`（28MB，
`.text` 到 rva `0x14CC0CA` 就结束）。拿它反汇编 `0x18xxxxxxx` 会落进 `.rdata`，
输出一堆 `add byte ptr [rax], bl` 之类的垃圾指令 —— 很容易被当成「代码被改了」。
正确模块是 `D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll`（`il2cpp` 节 rva 0x52E000 起）。已改。

### 事故记录：这一轮的崩溃是我自己的工具打的

`whocall.py 0x4FE400 --seconds 3` 想抓 `raise_null_reference_exception` 的调用者，
结果把该函数入口 14 字节原样搬到 stub，其中含 `e8 67 a5 f4 ff`（`call rel32`）。
位移不变但基准地址变了，目标从 `0x180448970` 变成未映射的 `0xD9B573` → Access Violation。

已加 `unsafe_replay()` 闸：搬之前用 capstone 逐条检查，只要出现
「块外的 `rel32` 分支目标」或「块外的 RIP 相对寻址」就拒绝挂钩，入口保持不动。
离线验证结果：

| 函数 | 结果 |
|---|---|
| `raise_null_reference_exception` (0x4FE400) | ✗ 拒绝（`call @+0x4 → 0x180448970 块外`）|
| `Update` (0x21D2550) | ✓ 放行 |
| `OnGetOpenworldEndlessDataRsp` | ✓ 放行 |
| `OnPacket` (0x189AFD0) | ✓ 放行 |

也就是说**前三次挂钩没崩纯属运气** —— 那三个函数的头部恰好没有位置相关指令。

---

## 十三、根因定论（2026-10-25 16:20）· 服务端 GroupLevel 不合法

> **修正第十二节的推断**：那里我写了「表在 mode=2 下是否整段为空」这个可能，
> 还提过一个「SetupView 发 3419 与 rsp 填充之间的死锁」猜想。
> 实测后两者**都不成立**，正确结论见下。

### 实测：表是好的，只是 key 不在里面

`probe_group.py` 在游戏里只读扫出来（`GetTopGroupLevel()=35` 说明表已加载）：

| mode | 有行的 GroupLevel |
|---|---|
| 2 迪拉克之海 | **21, 22, 23, 24** |
| 3 量子奇点 | 11, 12, 13, 14, 21, 22, 23, 24 |
| 4 超弦空间 | 无（这张表不管超弦，超弦走 `UltraEndless*`）|

而服务端 `GetOpenworldEndlessDataReqHandler` 当时发的是
`User.AbyssGroupLevel`（建号默认 **8**，0 时兜底 **1**）—— 8 和 1 都不在表里。

### `GroupInfo.Refresh(rsp)` 就是直接搬运，没有任何转换

```asm
0x180EF8E92  [rsi+0x18] = rbp        ; _rsp        = rsp
0x180EF8E9F  eax = [rbp+0x14]
0x180EF8EA2  [rsi+0x20] = eax        ; _GroupID    = rsp.GroupId
0x180EF8EA5  eax = [rbp+0x18]
0x180EF8EA8  [rsi+0x24] = eax        ; _GroupLevel = rsp.GroupLevel
```

所以**服务端发什么，`_GroupLevel` 就是什么**，查表成不成功完全由服务端决定。

### 修正：不需要「先预拉数据」

反编译 `GoToOWEndless` 本体（`_gotoow_fmt.c`）可以看到它自己就发 3419：

```c
if (!IsPatched(0x108d7)) {
    ctx = new LoadingWheelWidgetForTwoRspContext();
    ctx->ctor(0xd5c, 0xd7c, null);
    ctx->SetIgnoreMaxWaitTimeForReq(0xd5b);          // 关掉 5 秒兜底超时
    ctx->cmdCallBack = new KeyGeneratedEventHandler(this, _DAT_189b0e4b8);
    MainUIManager::ShowWidget(ctx, 0);               // 显示加载轮
    nm = <静态单例追逐 _DAT_189a981a8>;               // NetworkManager
    ... 内联 RequestOWEndlessData → 发 3419           // uStack_30 = 0x181ac59e3
}
```

所以 rsp 一定会来、`Refresh` 一定会跑。缺的不是「拉数据」这一步，
而是**拉回来的数据本身不合法**。

### 服务端改动（已发布）

| 文件 | 改动 |
|---|---|
| `AbyssConfig.cs` | 新增 `OwGroupLevel = 21u`，带完整注释说明为何不能复用 `User.AbyssGroupLevel` |
| `GetOpenworldEndlessDataReqHandler.cs` | `groupLevel` 改用 `AbyssConfig.OwGroupLevel`；新增回包日志 |
| `AbyssCommand.cs` | 新增 `abyss owlevel <n>` 热切换 |

为什么不复用 `User.AbyssGroupLevel`：它建号默认 8，且被超弦空间的
`UltraEndlessGetMainDataReqHand` 共用，直接改会波及超弦。

新增回包日志（客户端查表失败时不会有任何提示，只能靠这行核对）：

```
[Abyss] GetOpenworldEndlessDataRsp type=2 GroupId=1 GroupLevel=21 CurTopGroupLevel=22
```

### 重新编译 / 重启的正确姿势

- `build.bat` 走不通 —— 本机 PowerShell 工具禁用了 `cmd.exe`。直接调：
  ```
  dotnet build "Server\Server.csproj" -c Release --nologo -v q
  dotnet publish "Server\Server.csproj" -c Release -r win-x64 --self-contained true --nologo -v q -o "run"
  ```
- 重启只用 `_launch\restart_server.py`（复用 launch_v2 的 spawn/kill_pid），
  **不要用 `launch_v2.py stop`** —— 它会把 nginx(:80)、mitmdump(:8891)
  和系统代理一起拆掉，代价太大。

### 下一步

重新登录后先 `python owgo.py check`，然后 `python owgo.py call`。
预期服务端日志出现 `GroupLevel=21`，且 3419 不再刷屏。

---

## 十四、④ 成功（2026-10-25 16:32）· 进入迪拉克之海界面

**四步实验 ④ 首次成功。** 界面正常打开，3419 风暴彻底消失。

### 调用前的四项前置条件（缺一不可）

```
GetActiveMode()         = 2   Openworld(迪拉克之海)     ← 必须 2 或 3
GetCurrentEndlessData() = 0x700246ca380  非空
GroupInfo._GroupLevel   = 21                            ← 必须在客户端表里
3419 速率                = 0.00 次/秒                    ← 调用前必须干净
```

### 调用时序（实测）

| 时刻 | 事件 |
|---|---|
| 16:31:52 | 调用 `GoToOWEndless`，加载轮出现，开始发 3419 |
| 16:31:52~16:32:04 | 重试期，**2 次/秒**（日志每秒 4 行 = 2 个请求 × 2 行）|
| 16:32:04 | 重试停止，界面装配完成 |
| 16:32:05 起 | **稳态 0.00 次/秒**，窗口内除心跳外无任何请求 |

对比之前的失败：**120 次/秒 → 2 次/秒 → 0**。

那 12 秒的 2 次/秒不是故障，是 `BaseContext.OnViewSet` 在视图装配完成前的正常重试；
装配成功后自然归零。真正的判据是**最终能不能归零**，不是「有没有重试」。

### 成功后的客户端状态

```
this                    = 0x700244a4dd0
baseDataList            = 2 条，模式 [2, 3]
GetActiveMode()         = 2  Openworld
GetCurrentEndlessData() = 0x700246ca380
GroupInfo: _GroupID=1  _GroupLevel=21  _CurTopGroupLevel=22  _rsp=0x7002a2a2410
```

注意 `_rsp` 的地址每次刷新都会变（0x7002a2a25b0 → 0x7002a2a2410），
因为 proto 对象是每次回包新建的。**判断有没有拉过数据看 `_rsp != 0`，不要比对地址。**

### 完整因果链（最终版，已全部实证）

```
服务端 GetOpenworldEndlessDataRsp.GroupLevel
   ↓ (GroupInfo.Refresh @0x180EF8E70 直接搬运 rsp[0x18])
GroupInfo._GroupLevel
   ↓ (RefreshPlayerGroup @0x18185993B)
GetOWEndlessGroupMetaByKey(_GroupLevel, GetActiveMode())
   ↓ 客户端 OWEndlessGroup 表 mode=2 只有 21~24
返回 null → 0x181859956 je → 冷区 NRE thunk
   ↓
视图装配失败 → BaseContext.OnViewSet 每帧重试 → 每帧重发 3419
   ↓
120 次/秒风暴 + 黑屏（仍可点击）
```

**两个独立必要条件**：
1. `CurStatus.EndlessType` ∈ {2,3} —— 否则 `GetCurrentEndlessData()` 为 null，
   NRE 提前发生在 `SetupView` 里的判空处。
2. `rsp.GroupLevel` ∈ 客户端表有效集 —— 否则 NRE 发生在 `RefreshPlayerGroup+0x404`。

两者都满足才进得去。历史上两次黑屏分别命中这两条。

### 复现步骤（下次直接照做）

```powershell
# 0. 服务端默认是 Ultra，必须切到 2（重启服务端会重置）
#    游戏内聊天：abyss legacy 2
#    然后退出再进一次「世界地图 → 出击 → 开放世界」让客户端重拉状态

# 1. 预检（会打印 GetActiveMode / GetCurrentEndlessData / GroupInfo）
python owgo.py check

# 2. 确认 3419 速率为 0（用文件长度增量，别用固定窗口）
#    python 小脚本或手工比对日志长度

# 3. 四项都绿才调用
python owgo.py call
```

### 踩过的坑（按代价排序）

1. **重启服务端会把 `AbyssConfig` 静态字段重置回默认值** —— 改代码前先把默认值改成目标值，
   否则白重启一次 + 白让用户重登一次。
2. **客户端不只在登录时发 `GetEndlessStatusReq`** —— 进出面板就会重拉，
   所以切 `abyss legacy 2` 后**不需要重登录**，退出去再进一次面板即可。
3. **`GetGroupCountByGroupLevel(1..20)` 会抛异常**（不是返回 0），
   在 `cmd_call` 里表现为 5 秒超时。批量扫表时用 `--skip-count` 或只调
   `GetOWEndlessGroupMetaByKey`。
4. **`disasm.py` 的 DLL 必须指向 `BH3_Data\Native\UserAssembly.dll`**，
   指向 `UnityPlayer.dll` 会反汇编出垃圾。
5. **本机 PowerShell 工具禁用 `cmd.exe`** —— `build.bat` 走不通，
   直接 `dotnet build` / `dotnet publish`。
6. **不要用 `launch_v2.py stop` 改服务端代码** —— 它会连 nginx、mitmdump、
   系统代理一起拆掉。用 `_launch\restart_server.py`。



