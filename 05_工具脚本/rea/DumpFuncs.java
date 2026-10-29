// DumpFuncs.java — 导出全部函数入口 VA，用于与 .pdata 地面真值比对
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import java.io.PrintWriter;

public class DumpFuncs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String outPath = (args.length > 0) ? args[0] : "/home/nas/re/funcs.txt";
        PrintWriter pw = new PrintWriter(outPath);
        int n = 0;
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            long va = f.getEntryPoint().getOffset();
            long body = f.getBody().getNumAddresses();
            boolean thunk = f.isThunk();
            boolean ext = f.isExternal();
            // VA 16 进制 / 函数体字节数 / 是否 thunk / 是否 external
            pw.printf("%x\t%d\t%d\t%d\n", va, body, thunk ? 1 : 0, ext ? 1 : 0);
            n++;
        }
        pw.close();
        println("DUMPFUNCS wrote=" + n + " -> " + outPath);
    }
}
