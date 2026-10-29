// ApplySymbols.java — 把 metadata 解出的 311,382 个「方法名 + 签名」贴到 Ghidra 函数上
//
// 输入 TSV（无表头也可，按列位置）：
//   rva  ns  cls  method  ret  params  isStatic  token  module  aliasOf
//   rva 为十六进制 RVA（相对镜像基址 0x180000000）
//
// 行为：
//   - 只改「当前名以 FUN_ 开头」的函数，已有人工/分析命名的保持不动（真名写进注释）
//   - 命名空间按 ns 分段 + 类名建层级：ns::Cls::Method
//   - 同一 RVA 的其它方法（泛型共享体）写入注释 aliases
//   - 每 5000 个提交一次事务，避免单个巨型事务吃内存
//
// 参数：$1 symtab.tsv  $2 report.txt  [$3 dryRun=0/1]
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Program;
import ghidra.program.model.symbol.Namespace;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.SymbolTable;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class ApplySymbols extends GhidraScript {

    private static final long IMAGE_BASE = 0x180000000L;
    private static final int BATCH = 5000;

    private Program prog;
    private AddressSpace space;
    private FunctionManager fm;
    private SymbolTable st;
    private final Map<String, Namespace> nsCache = new HashMap<>();

    private String clean(String s) {
        if (s == null) return "";
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9')
                    || c == '_' || c == '$' || c == '.') {
                sb.append(c);
            } else {
                sb.append('_');
            }
        }
        String r = sb.toString().replaceAll("_+", "_").replaceAll("^\\.+|\\.+$", "");
        if (r.isEmpty()) r = "unnamed";
        if (r.length() > 100) r = r.substring(0, 100);
        return r;
    }

    private Namespace getOrCreate(String name, Namespace parent) {
        String key = Long.toString(parent.getID()) + "/" + name;
        Namespace hit = nsCache.get(key);
        if (hit != null) return hit;
        Namespace n = st.getNamespace(name, parent);
        if (n == null) {
            try {
                n = st.createNameSpace(parent, name, SourceType.USER_DEFINED);
            } catch (Exception e) {
                return parent;
            }
        }
        nsCache.put(key, n);
        return n;
    }

    private Namespace resolveNamespace(String ns, String cls) {
        Namespace cur = prog.getGlobalNamespace();
        if (ns != null && !ns.isEmpty()) {
            for (String part : ns.split("\\.")) {
                String p = clean(part);
                if (p.isEmpty() || p.equals("unnamed")) continue;
                cur = getOrCreate(p, cur);
            }
        }
        String c = clean(cls);
        if (!c.isEmpty() && !c.equals("unnamed")) cur = getOrCreate(c, cur);
        return cur;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String inPath = (args.length > 0) ? args[0] : "/home/nas/re/sym/bh3_symtab.tsv";
        String repPath = (args.length > 1) ? args[1] : "/home/nas/re/sym/apply_report.txt";
        boolean dry = (args.length > 2) && args[2].equals("1");

        prog = currentProgram;
        space = prog.getAddressFactory().getDefaultAddressSpace();
        fm = prog.getFunctionManager();
        st = prog.getSymbolTable();

        long t0 = System.currentTimeMillis();

        // 1) 读 TSV，按 RVA 归并
        Map<Long, String[]> main = new LinkedHashMap<>();
        Map<Long, List<String>> alias = new HashMap<>();
        int nLine = 0, nBad = 0;
        BufferedReader br = new BufferedReader(new FileReader(inPath), 1 << 20);
        String line;
        while ((line = br.readLine()) != null) {
            nLine++;
            if (line.startsWith("rva\t")) continue;
            String[] p = line.split("\t", -1);
            if (p.length < 10) { nBad++; continue; }
            long rva;
            try {
                rva = Long.parseLong(p[0], 16);
            } catch (Exception e) { nBad++; continue; }
            String full = (p[1].isEmpty() ? "" : p[1] + "::") + p[2] + "::" + p[3];
            if (p[9].isEmpty()) {
                if (!main.containsKey(rva)) main.put(rva, p);
            } else {
                alias.computeIfAbsent(rva, k -> new ArrayList<>()).add(full);
            }
        }
        br.close();
        println("读入 " + nLine + " 行，主名 " + main.size() + "，坏行 " + nBad
                + "，别名 RVA " + alias.size());

        // 2) 逐个应用
        int nFound = 0, nRenamed = 0, nKept = 0, nNotFound = 0, nDup = 0, nErr = 0, nCreated = 0;
        int inTx = 0;
        List<String> samples = new ArrayList<>();
        BufferedWriter rep = new BufferedWriter(new FileWriter(repPath), 1 << 20);
        rep.write("rva\tstatus\toldName\tnewName\n");

        int tx = prog.startTransaction("ApplySymbols");
        for (Map.Entry<Long, String[]> e : main.entrySet()) {
            long rva = e.getKey();
            String[] p = e.getValue();
            Address a = space.getAddress(IMAGE_BASE + rva);
            Function f = fm.getFunctionAt(a);
            boolean created = false;
            if (f == null && !dry) {
                // metadata 是地面真值：Ghidra 没在此建函数（未识别 / 被吞进巨型函数体），强制建并拆分
                try {
                    Namespace ns0 = resolveNamespace(p[1], p[2]);
                    f = createFunction(a, p[3]);
                    if (f != null) {
                        f.setParentNamespace(ns0);
                        created = true;
                        nCreated++;
                    }
                } catch (Exception ex) {
                    f = null;
                }
            }
            if (f == null) f = fm.getFunctionContaining(a);
            if (f == null) {
                nNotFound++;
                rep.write(String.format("%X\tNOTFOUND\t\t%s%n", rva, p[3]));
                continue;
            }
            nFound++;
            String oldName = f.getName();
            boolean isAuto = !created && (oldName.startsWith("FUN_")
                    || oldName.startsWith("thunk_FUN_") || oldName.startsWith("SUB_"));
            String want = p[3];

            if (!dry && isAuto) {
                try {
                    Namespace ns = resolveNamespace(p[1], p[2]);
                    f.setParentNamespace(ns);
                    String name = want;
                    try {
                        f.setName(name, SourceType.USER_DEFINED);
                    } catch (Exception dup) {
                        name = want + "_" + Long.toHexString(rva & 0xFFFF);
                        try {
                            f.setName(name, SourceType.USER_DEFINED);
                        } catch (Exception dup2) {
                            nDup++;
                            name = null;
                        }
                    }
                    if (name != null) {
                        nRenamed++;
                        rep.write(String.format("%X\tRENAMED\t%s\t%s::%s%n",
                                rva, oldName, p[2], name));
                        if (samples.size() < 20) {
                            samples.add(String.format("  %08X  %s::%s::%s", rva, p[1], p[2], name));
                        }
                    }
                } catch (Exception ex) {
                    nErr++;
                    rep.write(String.format("%X\tERROR\t%s\t%s%n", rva, oldName, ex));
                }
            } else {
                if (created) {
                    rep.write(String.format("%X\tCREATED\t\t%s::%s%n", rva, p[2], want));
                    if (samples.size() < 20) {
                        samples.add(String.format("  %08X  %s::%s::%s  [new]", rva, p[1], p[2], want));
                    }
                } else {
                    nKept++;
                    rep.write(String.format("%X\tKEPT\t%s\t%s%n", rva, oldName, want));
                }
            }

            // 注释：签名 + 别名
            if (!dry) {
                try {
                    StringBuilder cm = new StringBuilder();
                    cm.append("C#: ").append(p[4]).append(" ").append(p[2]).append("::")
                      .append(p[3]).append("(").append(p[5]).append(")");
                    if (p[6].equals("1")) cm.append("  [static]");
                    cm.append("  token=").append(p[7]);
                    List<String> al = alias.get(rva);
                    if (al != null) {
                        cm.append("\nGENERIC-SHARED aliases (").append(al.size()).append("): ");
                        int k = 0;
                        for (String s : al) {
                            if (k++ >= 12) { cm.append(" ..."); break; }
                            cm.append(s).append("; ");
                        }
                    }
                    String prev = f.getComment();
                    if (prev == null || !prev.startsWith("C#:")) {
                        f.setComment(cm.toString());
                    }
                } catch (Exception ignore) { }
            }

            if (++inTx >= BATCH) {
                prog.endTransaction(tx, true);
                tx = prog.startTransaction("ApplySymbols");
                inTx = 0;
                println("PROGRESS " + nRenamed + " renamed / " + main.size()
                        + "  (" + (System.currentTimeMillis() - t0) / 1000 + "s)");
            }
        }
        prog.endTransaction(tx, true);
        rep.close();

        long sec = (System.currentTimeMillis() - t0) / 1000;
        StringBuilder out = new StringBuilder();
        out.append("=== ApplySymbols 完成 ").append(sec).append("s ===\n");
        out.append("主名条目      : ").append(main.size()).append("\n");
        out.append("找到函数      : ").append(nFound).append("\n");
        out.append("已重命名      : ").append(nRenamed).append("\n");
        out.append("新建函数      : ").append(nCreated).append("\n");
        out.append("保留原名      : ").append(nKept).append("（已有非 FUN_ 名字）\n");
        out.append("未找到函数    : ").append(nNotFound).append("\n");
        out.append("重名放弃      : ").append(nDup).append("\n");
        out.append("异常          : ").append(nErr).append("\n");
        out.append("命名空间缓存  : ").append(nsCache.size()).append("\n");
        out.append("\n样例：\n");
        for (String s : samples) out.append(s).append("\n");
        println(out.toString());
    }
}
