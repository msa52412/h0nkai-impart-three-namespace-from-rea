// FuncCount.java — 报告当前程序的函数数量与内存占用（Ghidra postScript）
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.address.AddressSetView;

public class FuncCount extends GhidraScript {
    @Override
    public void run() throws Exception {
        int n = 0;
        long totalBytes = 0;
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            n++;
            totalBytes += f.getBody().getNumAddresses();
        }
        Runtime rt = Runtime.getRuntime();
        long usedMb = (rt.totalMemory() - rt.freeMemory()) / (1024 * 1024);
        long maxMb = rt.maxMemory() / (1024 * 1024);
        println("FUNCCOUNT total=" + n
                + " bodyBytes=" + totalBytes
                + " heapUsedMb=" + usedMb
                + " heapMaxMb=" + maxMb);
        println("FUNCCOUNT-DONE");
    }
}
