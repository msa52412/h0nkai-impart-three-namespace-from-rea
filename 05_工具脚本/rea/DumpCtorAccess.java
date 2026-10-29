// DumpCtorAccess.java — 反编译每类型代表方法，提取「this + 偏移」的访问集合
//
// 输入 TSV: typeIdx \t rva(hex) \t isCtor
// 输出 TSV: typeIdx \t offsets(逗号分隔 hex) \t nAccess \t nLines
//
// 原理：非静态方法的第一个参数就是 this。Ghidra 反编译里实例字段访问表现为
//   *(undefined4 *)(param_1 + 0x18)
//   param_1[5]              （数组下标形式，偏移 = 5*4）
// 而 static 字段的基址是全局指针（_DAT_xxx / &DAT_xxx），不会出现 param_1。
// 所以这个集合就是「实例字段偏移的地面真值」。
//
// 断点续跑：若 out.tsv 已存在，读取其中已完成的 typeIdx 并跳过。
//
// 参数: $1 probe.tsv  $2 out.tsv  [$3 maxTypes=0 表示不限]
// @category BH3
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.listing.Function;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.HashSet;
import java.util.Set;
import java.util.TreeSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DumpCtorAccess extends GhidraScript {

    private static final long IMAGE_BASE = 0x180000000L;

    // this 在反编译里可能叫 param_1，也可能被识别成 this
    private static final Pattern P_DISP =
            Pattern.compile("(?:param_1|this)\\s*\\+\\s*0x([0-9a-fA-F]+)");
    private static final Pattern P_IDX =
            Pattern.compile("(?:param_1|this)\\[(\\d+)\\]");
    private static final Pattern P_ZERO =
            Pattern.compile("\\*\\([a-zA-Z0-9_ ]+\\*\\)(?:param_1|this)(?![\\s\\w+\\[])");

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String inPath = args.length > 0 ? args[0] : "/home/nas/re/sym/layout_probe.tsv";
        String outPath = args.length > 1 ? args[1] : "/home/nas/re/sym/layout_obs.tsv";
        int maxTypes = args.length > 2 ? Integer.parseInt(args[2]) : 0;

        AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace();

        // ---- 断点续跑：收集已完成的 typeIdx ----
        Set<Integer> done = new HashSet<>();
        File of = new File(outPath);
        boolean append = of.exists() && of.length() > 0;
        if (append) {
            BufferedReader pr = new BufferedReader(new FileReader(of), 1 << 16);
            String l;
            while ((l = pr.readLine()) != null) {
                int t = l.indexOf('\t');
                if (t <= 0) continue;
                try { done.add(Integer.parseInt(l.substring(0, t))); } catch (Exception ignore) { }
            }
            pr.close();
            println("RESUME: 已有 " + done.size() + " 个类型");
        }

        DecompInterface ifc = new DecompInterface();
        ifc.toggleCCode(true);
        ifc.toggleSyntaxTree(true);
        // 注意：只能用 "decompile"，"normalize" 不产出 C 文本（getDecompiledFunction() 返回 null）
        ifc.setSimplificationStyle("decompile");
        if (!ifc.openProgram(currentProgram)) {
            println("openProgram failed: " + ifc.getLastMessage());
            return;
        }

        BufferedReader br = new BufferedReader(new FileReader(inPath), 1 << 16);
        BufferedWriter bw = new BufferedWriter(new FileWriter(outPath, append), 1 << 20);
        if (!append) bw.write("typeIdx\toffsets\tnAccess\tnLines\n");

        long t0 = System.currentTimeMillis();
        int n = 0, ok = 0, noFn = 0, empty = 0, err = 0, skip = 0, bigFn = 0;
        String line;
        while ((line = br.readLine()) != null) {
            if (line.startsWith("typeIdx")) continue;
            String[] p = line.split("\t");
            if (p.length < 3) continue;
            int ti;
            try { ti = Integer.parseInt(p[0]); } catch (Exception e) { continue; }
            if (done.contains(ti)) { skip++; continue; }
            if (maxTypes > 0 && n >= maxTypes) break;
            n++;
            String[] rvas = p[1].split(",");
            TreeSet<Long> offs = new TreeSet<>();
            int nLines = 0, nOk = 0;
            for (String rs : rvas) {
                long rva;
                try { rva = Long.parseLong(rs.trim(), 16); } catch (Exception e) { continue; }
                Address a = sp.getAddress(IMAGE_BASE + rva);
                Function f = currentProgram.getFunctionManager().getFunctionAt(a);
                if (f == null) f = currentProgram.getFunctionManager().getFunctionContaining(a);
                if (f == null) { noFn++; continue; }
                // 巨型函数（Ghidra 边界错误吞并产物）反编译极慢且无意义，直接跳过
                long naddr = f.getBody().getNumAddresses();
                if (naddr > 20000) { bigFn++; continue; }
                String c;
                try {
                    DecompileResults res = ifc.decompileFunction(f, 10, monitor);
                    if (res == null || !res.decompileCompleted()
                            || res.getDecompiledFunction() == null) {
                        err++;
                        if (err <= 3) {
                            println("ERRMSG " + (res == null ? "res=null" : res.getErrorMessage()));
                        }
                        continue;
                    }
                    c = res.getDecompiledFunction().getC();
                } catch (Exception e) {
                    err++;
                    if (err <= 3) println("EXC " + e);
                    continue;
                }
                if (c == null || c.isEmpty()) { empty++; continue; }
                nOk++;
                nLines += c.split("\n").length;
                Matcher m = P_DISP.matcher(c);
                while (m.find()) {
                    try { offs.add(Long.parseLong(m.group(1), 16)); } catch (Exception ignore) { }
                }
                m = P_IDX.matcher(c);
                while (m.find()) {
                    try { offs.add(Long.parseLong(m.group(1)) * 4L); } catch (Exception ignore) { }
                }
                if (P_ZERO.matcher(c).find()) offs.add(0L);
            }
            if (nOk == 0) { bw.write(ti + "\t\t0\t0\n"); continue; }

            StringBuilder sb = new StringBuilder();
            for (Long o : offs) {
                if (sb.length() > 0) sb.append(",");
                sb.append("0x").append(Long.toHexString(o));
            }
            bw.write(ti + "\t" + sb + "\t" + offs.size() + "\t" + nLines + "\n");
            ok++;
            if (ok % 500 == 0) {
                bw.flush();
                long el = (System.currentTimeMillis() - t0) / 1000;
                long eta = ok > 0 ? el * (37752 - done.size() - ok) / ok : 0;
                println("PROGRESS ok=" + ok + " skip=" + skip + " el=" + el + "s eta=" + eta + "s");
            }
        }
        br.close();
        bw.close();
        ifc.dispose();
        println("DumpCtorAccess done: processed=" + n + " ok=" + ok + " skip=" + skip
                + " noFn=" + noFn + " bigFn=" + bigFn + " empty=" + empty + " err=" + err + "  "
                + (System.currentTimeMillis() - t0) / 1000 + "s");
    }
}
