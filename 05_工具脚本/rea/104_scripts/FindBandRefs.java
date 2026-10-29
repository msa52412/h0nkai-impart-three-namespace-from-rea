// FindBandRefs.java — 找读取 metadata 加密带(段偏移 0x1C6766C..0x1D79820)的代码
// 原理: 该带无全局指针, 只能通过 [metadata_ptr + 大偏移] 访问。
// 扫指令中含 movsxd/lea 使用 imm/add 常数落在带域, 或 rip 全局链二跳
//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;

public class FindBandRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        long LO = 0x1C6766CL, HI = 0x1D79820L;
        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        int n = 0;
        while (it.hasNext()) {
            Instruction ins = it.next();
            for (int i = 0; i < ins.getNumOperands(); i++) {
                Object[] ops = ins.getOpObjects(i);
                for (Object o : ops) {
                    if (o instanceof Scalar) {
                        long v = ((Scalar) o).getUnsignedValue();
                        if (v >= LO && v <= HI) {
                            println(String.format("HIT 0x%X  %s   imm=0x%X",
                                ins.getAddress().getOffset(), ins.toString(), v));
                            n++;
                            if (n > 200) return;
                        }
                    }
                }
            }
        }
        println("total hits: " + n);
    }
}
