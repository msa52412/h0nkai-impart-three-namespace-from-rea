// Dump pseudo-C for a list of addresses from Ghidra headless.
// Usage: -postScript DumpDecomp.java <outFile> <addr1> <addr2> ...
//@category REA
//@keybinding
//@menupath
//@toolbar

import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DumpDecomp extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("DumpDecomp: need at least an output path");
            return;
        }
        String outPath = args[0];
        PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(outPath), 1 << 20));

        DecompInterface ifc = new DecompInterface();
        ifc.toggleCCode(true);
        ifc.toggleSyntaxTree(true);
        ifc.setSimplificationStyle("decompile");

        if (!ifc.openProgram(currentProgram)) {
            pw.println("// openProgram failed: " + ifc.getLastMessage());
            pw.close();
            return;
        }

        FunctionManager fm = currentProgram.getFunctionManager();
        pw.println("// program: " + currentProgram.getName());
        pw.println("// imageBase: " + currentProgram.getImageBase());
        pw.println("// functions in db: " + fm.getFunctionCount());
        pw.println();

        for (int i = 1; i < args.length; i++) {
            String spec = args[i];
            Address addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(spec);
            pw.println("/* ================= " + spec + " ================= */");
            if (addr == null) {
                pw.println("// bad address: " + spec);
                pw.println();
                continue;
            }
            Function f = fm.getFunctionAt(addr);
            if (f == null) {
                f = fm.getFunctionContaining(addr);
            }
            if (f == null) {
                pw.println("// no function defined at or containing " + spec);
                pw.println();
                pw.flush();
                continue;
            }
            long n = f.getBody().getNumAddresses();
            pw.println("/* name   = " + f.getName() + " */");
            pw.println("/* entry  = " + f.getEntryPoint() + " */");
            pw.println("/* body   = " + n + " bytes */");
            pw.println("/* sig    = " + f.getPrototypeString(false, false) + " */");
            pw.println();

            DecompileResults res = ifc.decompileFunction(f, 300, monitor);
            if (res == null) {
                pw.println("// decompile returned null");
            } else if (!res.decompileCompleted()) {
                pw.println("// decompile incomplete: " + res.getErrorMessage());
                if (res.getDecompiledFunction() != null) {
                    pw.println(res.getDecompiledFunction().getC());
                }
            } else {
                pw.println(res.getDecompiledFunction().getC());
            }
            pw.println();
            pw.flush();
            println("DumpDecomp: done " + spec + " (" + f.getName() + ", " + n + " bytes)");
        }

        ifc.dispose();
        pw.close();
        println("DumpDecomp: wrote " + outPath);
    }
}
