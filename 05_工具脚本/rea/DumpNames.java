// DumpNames.java — 导出全部函数 entry/name/size，供本地做入度统计
// 用法: -postScript DumpNames.java /home/nas/re/sym/names_all.tsv
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

import java.io.PrintWriter;

public class DumpNames extends GhidraScript {
    @Override
    public void run() throws Exception {
        String out = (getScriptArgs().length > 0) ? getScriptArgs()[0] : "/home/nas/re/sym/names_all.tsv";
        PrintWriter pw = new PrintWriter(out);
        pw.println("entry\tname\tsize\tthunk");
        int n = 0;
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            pw.println(String.format("%X\t%s\t%d\t%d",
                    f.getEntryPoint().getOffset(),
                    f.getName(),
                    f.getBody().getNumAddresses(),
                    f.isThunk() ? 1 : 0));
            n++;
        }
        pw.close();
        println("DumpNames -> " + out + "  n=" + n);
    }
}
