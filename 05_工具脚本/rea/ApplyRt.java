// ApplyRt.java — 给 il2cpp 运行时 / codegen helper 贴名字 + 标记 noreturn
//
// 与 ApplySymbols.java 的差别：
//   1) 强制改名（不看当前名是否 FUN_），用于二次修正
//   2) 支持 noreturn 标志 —— 抛异常的函数标了之后，反编译不再输出
//      `pcVar = swi(3); (*pcVar)();` 这段不可达尾巴
//   3) 命名空间层级直接由 ns 点分路径建，类名单独一层
//
// 输入 TSV（制表符分隔，无表头）：
//   va  noreturn  ns  cls  method
//   va 为十六进制 VA（含 0x180000000 基址）
//
// 用法: -postScript ApplyRt.java <in.tsv> <report.txt>
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Namespace;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.SymbolTable;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Map;

public class ApplyRt extends GhidraScript {

    private SymbolTable st;
    private final Map<String, Namespace> cache = new HashMap<>();

    private Namespace nsOf(String dotted, Namespace root) {
        Namespace cur = root;
        for (String part : dotted.split("\\.")) {
            if (part.isEmpty()) continue;
            String key = cur.getID() + "/" + part;
            Namespace hit = cache.get(key);
            if (hit == null) {
                Namespace n = st.getNamespace(part, cur);
                if (n == null) {
                    try {
                        n = st.createNameSpace(cur, part, SourceType.USER_DEFINED);
                    } catch (Exception e) {
                        n = cur;
                    }
                }
                cache.put(key, n);
                hit = n;
            }
            cur = hit;
        }
        return cur;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String in = args[0];
        String rep = (args.length > 1) ? args[1] : "/home/nas/re/sym/apply_rt2.txt";

        st = currentProgram.getSymbolTable();
        FunctionManager fm = currentProgram.getFunctionManager();
        PrintWriter pw = new PrintWriter(rep);
        pw.println("va\tstatus\toldName\tnewName\tnoreturn");

        int ok = 0, miss = 0, err = 0;
        int tx = currentProgram.startTransaction("ApplyRt");
        try {
            BufferedReader br = new BufferedReader(new FileReader(in));
            String line;
            while ((line = br.readLine()) != null) {
                if (line.trim().isEmpty() || line.startsWith("#")) continue;
                String[] p = line.split("\t", -1);
                if (p.length < 5) continue;
                long va;
                try {
                    va = Long.parseLong(p[0].trim().replace("0x", "").replace("0X", ""), 16);
                } catch (Exception e) { continue; }
                boolean noRet = p[1].trim().equals("1");
                String ns = p[2].trim(), cls = p[3].trim(), meth = p[4].trim();

                Address a = toAddr(va);
                Function f = fm.getFunctionAt(a);
                if (f == null) f = fm.getFunctionContaining(a);
                if (f == null) {
                    pw.printf("%X\tNOTFOUND\t\t%s::%s::%s\t%d%n", va, ns, cls, meth, noRet ? 1 : 0);
                    miss++;
                    continue;
                }
                String old = f.getName();
                try {
                    Namespace parent = nsOf(ns, currentProgram.getGlobalNamespace());
                    parent = nsOf(cls, parent);
                    f.setParentNamespace(parent);
                    f.setName(meth, SourceType.USER_DEFINED);
                    if (noRet) f.setNoReturn(true);
                    ok++;
                    pw.printf("%X\tOK\t%s\t%s::%s::%s\t%d%n", va, old, ns, cls, meth, noRet ? 1 : 0);
                } catch (Exception e) {
                    err++;
                    pw.printf("%X\tERROR\t%s\t%s\t%d\t%s%n", va, old, meth, noRet ? 1 : 0, e);
                }
            }
            br.close();
        } finally {
            currentProgram.endTransaction(tx, true);
        }
        pw.close();
        println("ApplyRt ok=" + ok + " miss=" + miss + " err=" + err + " -> " + rep);
    }
}
