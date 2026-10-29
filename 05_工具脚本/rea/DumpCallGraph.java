// DumpCallGraph.java — 导出全量调用图（线性成本，几分钟级）
//
// 输出 TSV：
//   F<TAB>va<TAB>body<TAB>flags<TAB>name          函数表
//   E<TAB>callerVa<TAB>calleeVa<TAB>insnVa        调用边表
//
// 只遍历指令找 CALL 类 flow，不走 getCalledFunctions（后者对 42 万函数太慢）。
// 每 20000 个函数往 stdout 打一行 PROGRESS，便于 mon.py / 日志观察进度。
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.FlowType;
import java.io.BufferedWriter;
import java.io.FileWriter;

public class DumpCallGraph extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String fnPath = (args.length > 0) ? args[0] : "/home/nas/re/callgraph.tsv";
        String ePath = (args.length > 1) ? args[1] : "/home/nas/re/callgraph_edges.tsv";

        long t0 = System.currentTimeMillis();
        int nFunc = 0, nEdge = 0, nIndirect = 0, nErr = 0;
        long totalInsn = 0;

        BufferedWriter fe = new BufferedWriter(new FileWriter(ePath), 1 << 20);
        fe.write("caller\tcallee\tinsn\n");

        BufferedWriter ff = new BufferedWriter(new FileWriter(fnPath), 1 << 20);
        ff.write("va\tbody\tthunk\tname\n");

        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            nFunc++;
            Address fEntry = f.getEntryPoint();
            ff.write(String.format("%x\t%d\t%d\t%s%n", fEntry.getOffset(),
                    f.getBody().getNumAddresses(), f.isThunk() ? 1 : 0,
                    f.getName()));

            try {
                InstructionIterator ii =
                        currentProgram.getListing().getInstructions(f.getBody(), true);
                while (ii.hasNext()) {
                    Instruction ins = ii.next();
                    totalInsn++;
                    FlowType ft = ins.getFlowType();
                    if (!ft.isCall() && !ft.isJump()) {
                        continue;
                    }
                    Address[] flows = ins.getDefaultFlows();
                    if (flows == null || flows.length == 0) {
                        if (ft.isCall()) {
                            nIndirect++;
                        }
                        continue;
                    }
                    for (Address tgt : flows) {
                        Function cf = currentProgram.getFunctionManager()
                                .getFunctionContaining(tgt);
                        if (cf == null) {
                            continue;
                        }
                        // 只记真正的调用/尾调用，不记函数内跳转
                        if (ft.isCall() || !cf.getEntryPoint().equals(fEntry)) {
                            fe.write(String.format("%x\t%x\t%x%n",
                                    fEntry.getOffset(), cf.getEntryPoint().getOffset(),
                                    ins.getAddress().getOffset()));
                            nEdge++;
                        }
                    }
                }
            } catch (Exception ex) {
                nErr++;
            }

            if (nFunc % 20000 == 0) {
                println("PROGRESS funcs=" + nFunc + " edges=" + nEdge
                        + " insn=" + totalInsn
                        + " elapsed=" + ((System.currentTimeMillis() - t0) / 1000) + "s");
            }
        }
        fe.close();
        ff.close();

        long secs = (System.currentTimeMillis() - t0) / 1000;
        println("CALLGRAPH-DONE funcs=" + nFunc + " edges=" + nEdge
                + " indirectCalls=" + nIndirect + " insn=" + totalInsn
                + " errors=" + nErr + " seconds=" + secs);
    }
}
