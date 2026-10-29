// Dump assembly listing for address ranges.
// Usage: -postScript DumpAsm.java <outFile> <startVA>-<endVA> [...]
//@category REA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DumpAsm extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            println("DumpAsm: need outFile and at least one start-end range");
            return;
        }
        String outPath = args[0];
        PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(outPath), 1 << 20));
        Listing listing = currentProgram.getListing();

        for (int i = 1; i < args.length; i++) {
            String spec = args[i];
            int dash = spec.indexOf('-');
            if (dash <= 0) {
                pw.println("// bad range: " + spec);
                continue;
            }
            Address start = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(spec.substring(0, dash));
            Address end = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(spec.substring(dash + 1));
            pw.println("// ================= " + spec + " =================");
            InstructionIterator it = listing.getInstructions(start, true);
            int n = 0;
            while (it.hasNext()) {
                Instruction ins = it.next();
                if (ins.getAddress().compareTo(end) > 0) {
                    break;
                }
                pw.println(ins.getAddress() + "  " + ins.toString());
                n++;
            }
            pw.println("// " + n + " instructions");
            pw.println();
            println("DumpAsm: " + spec + " -> " + n + " instructions");
        }
        pw.close();
        println("DumpAsm: wrote " + outPath);
    }
}
