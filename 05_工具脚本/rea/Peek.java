// Peek.java — 在 Ghidra 里直接读指定地址的字节/字符串，并列出引用它的代码位置
// 用法: -postScript Peek.java <outFile> <va1> [va2 ...]
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

import java.io.PrintWriter;

public class Peek extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] a = getScriptArgs();
        String out = a[0];
        PrintWriter pw = new PrintWriter(out);
        Memory mem = currentProgram.getMemory();
        ReferenceManager rm = currentProgram.getReferenceManager();
        FunctionManager fm = currentProgram.getFunctionManager();

        for (int i = 1; i < a.length; i++) {
            long va;
            try {
                va = Long.parseLong(a[i].replace("0x", "").replace("0X", ""), 16);
            } catch (Exception e) {
                continue;
            }
            Address ad = toAddr(va);
            pw.printf("%n/* ===== %X ===== */%n", va);

            // 字节 + ASCII
            byte[] b = new byte[80];
            int n = 0;
            try { n = mem.getBytes(ad, b); } catch (Exception e) { n = 0; }
            StringBuilder hex = new StringBuilder();
            StringBuilder asc = new StringBuilder();
            for (int k = 0; k < n; k++) {
                hex.append(String.format("%02X ", b[k] & 0xFF));
                int c = b[k] & 0xFF;
                asc.append((c >= 0x20 && c < 0x7F) ? (char) c : '.');
            }
            pw.println("bytes: " + hex);
            pw.println("ascii: " + asc);

            // 当作 C 字符串读（若首个字节可打印）
            if (n > 0 && (b[0] & 0xFF) >= 0x20 && (b[0] & 0xFF) < 0x7F) {
                StringBuilder s = new StringBuilder();
                for (int k = 0; k < n; k++) {
                    int c = b[k] & 0xFF;
                    if (c == 0) break;
                    if (c < 0x20 || c >= 0x7F) { s.append('?'); continue; }
                    s.append((char) c);
                }
                pw.println("cstr : \"" + s + "\"");
            }

            // 引用者
            int cnt = 0;
            ReferenceIterator it = rm.getReferencesTo(ad);
            while (it.hasNext() && cnt < 40) {
                Reference r = it.next();
                Address from = r.getFromAddress();
                Function f = fm.getFunctionContaining(from);
                pw.printf("  ref from %X  type=%s  in=%s%n",
                        from.getOffset(), r.getReferenceType(),
                        f == null ? "<none>" : (f.getName() + "@" + Long.toHexString(f.getEntryPoint().getOffset())));
                cnt++;
            }
            if (cnt == 0) pw.println("  (no refs)");
        }
        pw.close();
        println("Peek -> " + out);
    }
}
