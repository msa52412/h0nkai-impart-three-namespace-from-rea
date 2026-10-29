// StatNames.java — 统计符号落地后的命名覆盖情况
// 用法: -postScript StatNames.java /home/nas/re/sym/stat.txt
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.symbol.Namespace;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class StatNames extends GhidraScript {
    @Override
    public void run() throws Exception {
        String out = (getScriptArgs().length > 0) ? getScriptArgs()[0] : "/home/nas/re/sym/stat.txt";
        PrintWriter pw = new PrintWriter(out);

        int total = 0, named = 0, fun = 0, thunk = 0, ext = 0;
        long bytesNamed = 0, bytesAll = 0;
        Map<String, int[]> byNs = new HashMap<>();
        Map<String, Integer> topCls = new HashMap<>();

        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            total++;
            long b = f.getBody().getNumAddresses();
            bytesAll += b;
            if (f.isThunk()) thunk++;
            if (f.isExternal()) ext++;
            String n = f.getName();
            boolean isAuto = n.startsWith("FUN_") || n.startsWith("thunk_FUN_") || n.startsWith("SUB_");
            if (isAuto) {
                fun++;
            } else {
                named++;
                bytesNamed += b;
                Namespace ns = f.getParentNamespace();
                String key = (ns == null) ? "?" : ns.getName(true);
                byNs.computeIfAbsent(key, k -> new int[1])[0]++;
                String ck = key;
                topCls.merge(ck, 1, Integer::sum);
            }
        }

        pw.printf("总函数数        : %d%n", total);
        pw.printf("有 C# 名字      : %d (%.2f%%)%n", named, 100.0 * named / total);
        pw.printf("仍是 FUN_ 自动名 : %d (%.2f%%)%n", fun, 100.0 * fun / total);
        pw.printf("thunk / external : %d / %d%n", thunk, ext);
        pw.printf("命名函数体字节   : %d / %d (%.2f%%)%n", bytesNamed, bytesAll,
                100.0 * bytesNamed / bytesAll);

        List<Map.Entry<String, int[]>> lst = new ArrayList<>(byNs.entrySet());
        lst.sort((a, b) -> Integer.compare(b.getValue()[0], a.getValue()[0]));
        pw.printf("%n命名空间数      : %d%n", lst.size());
        pw.printf("%nTop 25 命名空间（按函数数）%n");
        for (int i = 0; i < Math.min(25, lst.size()); i++) {
            pw.printf("  %-52s %6d%n", lst.get(i).getKey(), lst.get(i).getValue()[0]);
        }
        pw.close();
        println("StatNames -> " + out + "  total=" + total + " named=" + named + " auto=" + fun);
    }
}
