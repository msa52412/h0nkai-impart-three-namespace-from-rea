# h0nkai-impart-three-namespace-from-rea

《某坏3rd》7.0 客户端 IL2CPP 反编译产物的**代码层**整理集。

## 目录

| 目录 | 内容 | 文件数 |
| --- | --- | --- |
| `01_CSharp还原` | 由 `global-metadata.dat` 还原的 C# 骨架，**按 namespace 分文件**。每个类型含 token / 字段偏移 / 方法注释（含 RVAs），方法体为空 `{ }` | 469 |
| `02_原生反编译` | 关键函数的手工反编译 C 伪码（抽卡、CG、图标路径等） | 46 |
| `05_工具脚本` | 还原/分析用的 Python、C# 脚本（`rea` 453 / `ext_native_re` 69 / `launch` 11） | 533 |
| `09_笔记杂项` | 调研笔记、结构体/命名表 JSON、临时诊断脚本 | 106 |

## 重要说明

- **`01_CSharp还原` 里的方法体是空的。** 真实方法体不在 `.cs` 里，而在原始产物的
  `03_符号与地址表/bodies_merged.tsv`（按 VA → 伪 C 索引），本仓库未收录该大表。
- 命名空间规模参考：`MoleMole` 12172 类型、`proto` 4318、`MoleMole.ExcelMeta` 3614、
  `MoleMole.Config` 2400，全局命名空间 22186。
- `.cs` 文件按命名空间聚合，单个文件可能很大（`MoleMole.cs` 约 25 MB）。
- `09_笔记杂项` 中的 `.log` / `.out` 是当时的运行输出，属于快照，不代表当前状态。

## 用法

1. 想找某个类：`grep -rn "class ModelGacha" 01_CSharp还原/`
2. 想找某个方法落在哪个命名空间：先在 `.cs` 里搜方法名，再对照 `09_笔记杂项/addr2name.json`。
3. 想知道某个方法到底做了什么：拿 `.cs` 注释里的 VA 去 `bodies_merged.tsv` 查伪 C。

## 免责声明

仅用于本地学习与研究。代码版权归米哈游所有，本仓库不提供任何游戏资源文件。
