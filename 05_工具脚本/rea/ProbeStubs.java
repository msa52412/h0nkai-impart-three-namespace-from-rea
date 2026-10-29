// ProbeStubs.java — 对给定 VA 列表逐个强制反汇编 + 建函数，报告：
//   内存块归属 / 反汇编前后函数状态 / 指令流 / jmp 目标归属 / 函数体范围
// Usage: -postScript ProbeStubs.java <outFile> <VA> [<VA> ...]
//@category REA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Symbol;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.PrintWriter;

public class ProbeStubs extends GhidraScript {

    private String fnName(Address a) {
        if (a == null) return "-";
        Symbol s = getSymbolAt(a);
        Function f = getFunctionAt(a);
        if (f != null) {
            return "FUNCTION:" + f.getName() + " body[" + f.getBody().getMinAddress()
                    + ".." + f.getBody().getMaxAddress() + "] size=" + f.getBody().getNumAddresses();
        }
        if (s != null) return "SYMBOL:" + s.getName();
        Function c = getFunctionContaining(a);
        if (c != null) return "IN_BODY_OF:" + c.getName() + " [" + c.getEntryPoint() + "]";
        return "none";
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) { println("ProbeStubs: need outFile and >=1 VA"); return; }
        PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(args[0]), 1 << 16));

        for (int i = 1; i < args.length; i++) {
            Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(args[i]);
            pw.println("================================================================");
            pw.println("VA " + a);
            MemoryBlock mb = getMemoryBlock(a);
            pw.println("  block       : " + (mb == null ? "**UNMAPPED**"
                    : mb.getName() + " init=" + mb.isInitialized()) + "   before=" + fnName(a));

            if (getInstructionAt(a) == null) {
                try { disassemble(a); } catch (Exception ex) { pw.println("  disasm EXC " + ex.getMessage()); }
            }
            Instruction ins = getInstructionAt(a);
            if (ins == null) { pw.println("  ** disassembly failed **"); pw.println(); continue; }

            Address p = a;
            int n = 0;
            Address jmpTarget = null;
            String jmpOp = "";
            while (p != null && n < 40) {
                Instruction cur = getInstructionAt(p);
                if (cur == null) {
                    try { disassemble(p); } catch (Exception ex) { break; }
                    cur = getInstructionAt(p);
                    if (cur == null) break;
                }
                pw.println("    " + cur.getAddress() + "  " + cur.toString());
                n++;
                String mn = cur.getMnemonicString();
                if (mn != null && mn.equalsIgnoreCase("JMP")) {
                    jmpOp = cur.getDefaultOperandRepresentation(0);
                    Address[] fl = cur.getDefaultFlows();
                    if (fl != null && fl.length > 0) jmpTarget = fl[0];
                }
                if (cur.getFlowType().isTerminal()) break;
                if (mn != null && mn.equalsIgnoreCase("INT3")) break;
                p = cur.getMaxAddress().next();
            }
            pw.println("  insns       : " + n);
            if (jmpOp.length() > 0) {
                pw.println("  jmp operand : " + jmpOp);
                pw.println("  jmp target  : " + (jmpTarget == null ? "(indirect)" : jmpTarget.toString()));
                if (jmpTarget != null) pw.println("  target is   : " + fnName(jmpTarget));
            }

            // 尝试在该地址建函数，看 Ghidra 认为函数体到哪里
            if (getFunctionAt(a) == null) {
                try {
                    Function nf = createFunction(a, null);
                    if (nf != null) {
                        pw.println("  createFunction -> body[" + nf.getBody().getMinAddress()
                                + ".." + nf.getBody().getMaxAddress() + "] size=" + nf.getBody().getNumAddresses());
                        nf.setName("probe_" + Long.toHexString(a.getOffset()), ghidra.program.model.symbol.SourceType.USER_DEFINED);
                    } else {
                        pw.println("  createFunction -> null");
                    }
                } catch (Exception ex) {
                    pw.println("  createFunction EXC " + ex.getMessage());
                }
            }
            pw.println();
        }
        pw.close();
        println("ProbeStubs: wrote " + args[0]);
    }
}
