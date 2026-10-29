// DumpBodies.java — 批量导出函数反编译体（可断点续跑）
//
// 输入：listFile，每行一个十六进制 VA（不含 0x 也行）
// 输出：outFile，TSV 两列：VA<TAB>函数体（\n 转义成字面量 \n）
//       函数体取反编译 C 里第一个 '{' 到最后一个 '}' 之间的内容，
//       签名部分丢掉（调用方已有还原出的 C# 签名）
//
// 断点续跑：启动时先把 outFile 里已有的 VA 读进来，跳过。
//
// 用法: -postScript DumpBodies.java <listFile> <outFile> [maxCount]
// @category BH3
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class DumpBodies extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length < 2) {
            println("DumpBodies: need listFile outFile [maxCount]");
            return;
        }
        String listPath = a[0];
        String outPath = a[1];
        int maxCount = (a.length > 2) ? Integer.parseInt(a[2]) : Integer.MAX_VALUE;

        // 1) 已完成的 VA
        Set<Long> done = new HashSet<>();
        java.io.File of = new java.io.File(outPath);
        if (of.exists()) {
            BufferedReader br = new BufferedReader(new FileReader(of), 1 << 20);
            String ln;
            while ((ln = br.readLine()) != null) {
                int t = ln.indexOf('\t');
                if (t > 0) {
                    try { done.add(Long.parseLong(ln.substring(0, t), 16)); } catch (Exception e) { }
                }
            }
            br.close();
        }
        println("已有 " + done.size() + " 条，续跑");

        // 2) 待处理列表
        List<Long> todo = new ArrayList<>();
        BufferedReader br = new BufferedReader(new FileReader(listPath), 1 << 20);
        String ln;
        while ((ln = br.readLine()) != null) {
            ln = ln.trim();
            if (ln.isEmpty()) continue;
            try {
                long va = Long.parseLong(ln.replace("0x", "").replace("0X", ""), 16);
                if (!done.contains(va)) todo.add(va);
            } catch (Exception e) { }
        }
        br.close();
        println("待处理 " + todo.size() + " 个，本次上限 " + maxCount);

        DecompInterface ifc = new DecompInterface();
        ifc.toggleCCode(true);
        ifc.toggleSyntaxTree(false);
        ifc.setSimplificationStyle("decompile");
        if (!ifc.openProgram(currentProgram)) {
            println("openProgram 失败: " + ifc.getLastMessage());
            return;
        }

        FunctionManager fm = currentProgram.getFunctionManager();
        PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(outPath, true), 1 << 22));

        long t0 = System.currentTimeMillis();
        int ok = 0, miss = 0, empty = 0, n = 0;
        for (long va : todo) {
            if (ok >= maxCount) break;
            n++;
            Address ad = toAddr(va);
            Function f = fm.getFunctionAt(ad);
            if (f == null) f = fm.getFunctionContaining(ad);
            if (f == null) { miss++; continue; }
            String body = null;
            try {
                DecompileResults r = ifc.decompileFunction(f, 45, monitor);
                if (r != null && r.decompileCompleted() && r.getDecompiledFunction() != null) {
                    String c = r.getDecompiledFunction().getC();
                    int b = c.indexOf('{');
                    int e = c.lastIndexOf('}');
                    if (b >= 0 && e > b) body = c.substring(b + 1, e);
                }
            } catch (Exception ex) {
                body = null;
            }
            if (body == null) { empty++; continue; }
            // 缩进归一 + 转义
            StringBuilder sb = new StringBuilder(body.length() + 16);
            for (String line : body.split("\n", -1)) {
                String s = line.stripTrailing();
                if (s.isEmpty()) { sb.append("\\n"); continue; }
                // 去掉反编译默认的 2 空格基准缩进
                if (s.startsWith("  ")) s = s.substring(2);
                sb.append(s).append("\\n");
            }
            String out = sb.toString();
            if (out.endsWith("\\n")) out = out.substring(0, out.length() - 3);
            pw.println(String.format("%X\t%s", va, out));
            ok++;
            if (ok % 500 == 0) {
                pw.flush();
                long ms = System.currentTimeMillis() - t0;
                double rate = ok * 1000.0 / Math.max(1, ms);
                long eta = (long) ((todo.size() - n) / Math.max(0.001, rate));
                println(String.format("PROGRESS %d/%d  %.1f 个/秒  剩余约 %d 分  miss=%d empty=%d",
                        n, todo.size(), rate, eta / 60, miss, empty));
            }
        }
        pw.flush();
        pw.close();
        ifc.dispose();
        long ms = System.currentTimeMillis() - t0;
        println(String.format("DumpBodies 完成 ok=%d miss=%d empty=%d 用时 %.0f 秒", ok, miss, empty, ms / 1000.0));
    }
}
