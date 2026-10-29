// CheckAddr.java — 诊断若干 VA 处的函数/符号/指令状态
// 用法: -postScript CheckAddr.java 0x186a650f0 0x186b0b910 ...
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Symbol;

public class CheckAddr extends GhidraScript {
    @Override
    public void run() throws Exception {
        AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace();
        for (String s : getScriptArgs()) {
            long va = Long.parseLong(s.replace("0x", ""), 16);
            Address a = sp.getAddress(va);
            Function f = currentProgram.getFunctionManager().getFunctionAt(a);
            Function c = currentProgram.getFunctionManager().getFunctionContaining(a);
            Symbol[] syms = currentProgram.getSymbolTable().getSymbols(a);
            Instruction ins = currentProgram.getListing().getInstructionAt(a);
            StringBuilder sb = new StringBuilder();
            sb.append(String.format("%X  fnAt=%s  fnContaining=%s  insn=%s  syms=",
                    va,
                    f == null ? "-" : (f.getName() + "/body=" + f.getBody().getNumAddresses()
                            + "/thunk=" + f.isThunk() + "/ext=" + f.isExternal()),
                    c == null ? "-" : c.getName() + "@" + Long.toHexString(c.getEntryPoint().getOffset()),
                    ins == null ? "-" : ins.getMnemonicString()));
            for (Symbol y : syms) sb.append("[").append(y.getName()).append("/").append(y.getSymbolType()).append("]");
            println(sb.toString());
        }
    }
}
