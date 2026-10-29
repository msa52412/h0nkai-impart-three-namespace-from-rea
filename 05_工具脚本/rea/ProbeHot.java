// ProbeHot.java — 热点函数定位：解析桩 → 跟跳转 → 反编译最终目标
// Usage: -postScript ProbeHot.java <outFile> <VA> [<VA> ...]
//@category REA

import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.PrintWriter;

public class ProbeHot extends GhidraScript {

    private DecompInterface di;

    private String nm(Address a) {
        if (a == null) return "-";
        Function f = getFunctionAt(a);
        if (f != null) return "FUNC:" + f.getName();
        Symbol s = getSymbolAt(a);
        return s != null ? ("SYM:" + s.getName()) : "none";
    }

    private String bodyInfo(Address a) {
        Function f = getFunctionContaining(a);
        if (f == null) return "no-func";
        return f.getName() + " [" + f.getEntryPoint() + ".."
                + f.getBody().getMaxAddress() + "] n=" + f.getBody().getNumAddresses();
    }

    private int refCount(Address a) {
        int n = 0;
        ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(a);
        while (it.hasNext()) { it.next(); n++; }
        return n;
    }

    private void decompile(Address a, PrintWriter pw) {
        Function f = getFunctionAt(a);
        if (f == null) {
            Function c = getFunctionContaining(a);
            if (c != null) f = c;
        }
        if (f == null) { pw.println("    <无函数可反编译>"); return; }
        DecompileResults r = di.decompileFunction(f, 90, monitor);
        if (r == null || !r.decompileCompleted() || r.getDecompiledFunction() == null) {
            pw.println("    <反编译失败: " + (r == null ? "null" : r.getErrorMessage()) + ">");
            return;
        }
        String c = r.getDecompiledFunction().getC();
        for (String ln : c.split("\n")) pw.println("    " + ln);
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) { println("ProbeHot: need outFile and >=1 VA"); return; }
        di = new DecompInterface();
        di.openProgram(currentProgram);

        PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(args[0]), 1 << 16));
        pw.println("program = " + currentProgram.getName());
        pw.println("imageBase = " + currentProgram.getImageBase());

        for (int i = 1; i < args.length; i++) {
            Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(args[i]);
            pw.println("================================================================");
            pw.println("VA " + a + "   " + nm(a) + "   refs=" + refCount(a));
            pw.println("  in : " + bodyInfo(a));

            Address cur = a;
            Address finalTarget = a;
            for (int hop = 0; hop < 6; hop++) {
                if (getInstructionAt(cur) == null) {
                    try { disassemble(cur); } catch (Exception ex) { }
                }
                Instruction ins = getInstructionAt(cur);
                if (ins == null) { pw.println("    [" + hop + "] " + cur + "  <无反汇编>"); finalTarget = cur; break; }
                pw.println("    [" + hop + "] " + cur + "  " + ins.toString());
                String mn = ins.getMnemonicString();
                Address[] flows = ins.getFlows();
                if ((mn.equals("JMP") || mn.equals("JMPF")) && flows != null && flows.length == 1) {
                    cur = flows[0];
                    finalTarget = cur;
                    continue;
                }
                finalTarget = cur;
                break;
            }

            pw.println("  -> 最终目标 " + finalTarget + "  " + nm(finalTarget) + "  refs="
                    + refCount(finalTarget) + "  in " + bodyInfo(finalTarget));
            pw.println("  ---- 反编译 ----");
            decompile(finalTarget, pw);

            if (!finalTarget.equals(a)) {
                pw.println("  ---- 原始地址所在函数（若非同一函数）----");
                Function fa = getFunctionContaining(a);
                Function ft = getFunctionContaining(finalTarget);
                if (fa != null && (ft == null || !fa.getEntryPoint().equals(ft.getEntryPoint()))) {
                    decompile(fa.getEntryPoint(), pw);
                } else {
                    pw.println("    <与最终目标同一函数或无函数>");
                }
            }
            pw.println();
        }
        pw.close();
        println("ProbeHot done -> " + args[0]);
    }
}
