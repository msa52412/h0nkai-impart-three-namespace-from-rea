// BlockList.java — 列出程序全部内存块
// Usage: -postScript BlockList.java <outFile>
//@category REA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.MemoryBlock;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.PrintWriter;

public class BlockList extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String out = (args.length > 0) ? args[0] : "/tmp/blocks.txt";
        PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(out), 1 << 16));
        pw.println("ImageBase = " + currentProgram.getImageBase());
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            pw.println(String.format("%-10s %s .. %s  size=%-12d init=%-5s r=%s w=%s x=%s",
                    b.getName(), b.getStart(), b.getEnd(), b.getSize(),
                    b.isInitialized(), b.isRead(), b.isWrite(), b.isExecute()));
        }
        pw.close();
        println("BlockList: wrote " + out);
    }
}
