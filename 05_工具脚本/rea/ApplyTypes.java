// ApplyTypes.java — 把解出的字段布局写成 Ghidra 结构体，并把 `this` 参数重定型
//
// 输入：
//   $1 bh3_structs.tsv   typeIdx \t catPath \t name \t size \t conf \t nInst \t fields
//                        fields = off:kind:name;...   kind ∈ {i1,u1,i2,u2,i4,u4,i8,u8,f4,f8,ref,st:<idx>,pad}
//                        （文件已按「值类型优先」拓扑排序，直接顺序建即可）
//   $2 bh3_this.tsv      rva \t typeIdx（非静态方法 → 声明类型）
//   $3 report.txt
//   $4 dryRun 0/1（可选，默认 0）
//   $5 maxFuncs（可选，0 = 全部）
//
// 为什么要建「含对象头」的结构体：类实例前 16 字节是
//   { Il2CppClass* klass; void* monitor; }
// 把它也建进结构体，`this` 指向结构体起点后，所有字段偏移就能一一对应，
// 反编译里 `*(int *)(param_1 + 0x10)` 会变成 `this->m_stringLength`。
//
// @category BH3
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.HashMap;
import java.util.Map;

public class ApplyTypes extends GhidraScript {

    private static final long IMAGE_BASE = 0x180000000L;
    private static final String ROOT2 = "/bh3v8";

    private DataTypeManager dtm;
    private final Map<Long, DataType> byTypeIdx = new HashMap<>();
    private final Map<Long, Integer> sizeByTypeIdx = new HashMap<>();

    private DataType scalar(String kind) {
        switch (kind) {
            case "i1": return new SignedByteDataType();
            case "u1": return new ByteDataType();
            case "i2": return new ShortDataType();
            case "u2": return new UnsignedShortDataType();
            case "i4": return new IntegerDataType();
            case "u4": return new UnsignedIntegerDataType();
            case "i8": return new LongLongDataType();
            case "u8": return new UnsignedLongLongDataType();
            case "f4": return new FloatDataType();
            case "f8": return new DoubleDataType();
            case "ref": return new PointerDataType(dtm);
            default: return null;
        }
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String structsPath = args.length > 0 ? args[0] : "/home/nas/re/sym/bh3_structs.tsv";
        String thisPath = args.length > 1 ? args[1] : "/home/nas/re/sym/bh3_this.tsv";
        String reportPath = args.length > 2 ? args[2] : "/home/nas/re/sym/apply_types.txt";
        boolean dry = args.length > 3 && "1".equals(args[3]);
        int maxFuncs = args.length > 4 ? Integer.parseInt(args[4]) : 0;

        dtm = currentProgram.getDataTypeManager();
        AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace();
        BufferedWriter rep = new BufferedWriter(new FileWriter(reportPath), 1 << 20);

        // ---------------- 1) 建结构体 ----------------
        int nStruct = 0, nSkip = 0, nField = 0, nFail = 0, nPadDep = 0, nTrail = 0;
        int rSize = 0, rOff = 0, rSpec = 0, rLen = 0, rDep = 0, rScalar = 0, rExist = 0;
        long t0 = System.currentTimeMillis();
        int tx = dtm.startTransaction("bh3 structs");
        try {
            BufferedReader br = new BufferedReader(new FileReader(structsPath), 1 << 16);
            String line;
            while ((line = br.readLine()) != null) {
                if (line.startsWith("typeIdx")) continue;
                String[] p = line.split("\t");
                if (p.length < 7) continue;
                long ti = Long.parseLong(p[0]);
                // ★ 换根到 /bh3v2：旧 /bh3 里那批结构体长度和当前规格对不上，
                //   而 dtm.remove() 会触发 ProgramDataTypeManager.deleteDataTypesUsed
                //   → CodeManager.clearData 遍历全程序地址（44 万函数），单次就是几十秒，
                //   2.4 万次根本跑不完。换一个干净的根目录即可完全绕开冲突。
                CategoryPath cp = new CategoryPath(ROOT2 + p[1].substring("/bh3".length()));
                String name = p[2];
                int size = Integer.parseInt(p[3]);
                if (size <= 0 || size > 0x4000) { nSkip++; rSize++; continue; }
                sizeByTypeIdx.put(ti, Integer.valueOf(size));

                // 同名同长度已存在 → 直接复用。
                // 二次运行时若仍走 remove+add，会在 2.4 万结构体上触发 O(n²) 的
                // DataTypeManager 缓存重建（实测 4 分钟还没建完，而首次创建只要 3 秒）。
                DataType exist = dtm.getDataType(cp, name);
                if (exist instanceof StructureDataType && exist.getLength() == size
                        && ((StructureDataType) exist).getNumComponents() > 0) {
                    byTypeIdx.put(ti, exist);
                    nSkip++; rExist++;
                    continue;
                }

                StructureDataType sdt = new StructureDataType(cp, name, 0, null);
                // conf 写进结构体描述，Ghidra 里能直接看到可信度
                try { sdt.setDescription("bh3 conf=" + p[4]); } catch (Exception ignore) { }
                int cur = 0;
                boolean bad = false;
                for (String spec : p[6].split(";")) {
                    if (spec.isEmpty()) continue;
                    String[] q = spec.split(":", 3);
                    if (q.length < 3) { rSpec++; continue; }
                    int off = Integer.parseInt(q[0]);
                    String kind = q[1];
                    String arg = q[2];
                    if (off < cur) { bad = true; rOff++; break; }
                    if (off > cur) {
                        int gap = off - cur;
                        sdt.add(new ArrayDataType(new Undefined1DataType(), gap, 1, dtm),
                                gap, String.format("pad_%X", cur), null);
                        cur = off;
                    }
                    if ("pad".equals(kind)) {
                        int len = Integer.parseInt(arg);
                        if (len <= 0) { bad = true; break; }
                        sdt.add(new ArrayDataType(new Undefined1DataType(), len, 1, dtm),
                                len, String.format("pad_%X", off), null);
                        cur += len;
                        continue;
                    }
                    DataType ft;
                    int flen;
                    if (kind.startsWith("st.") || kind.startsWith("st:")) {
                        long di = Long.parseLong(kind.substring(3));
                        ft = byTypeIdx.get(di);
                        Integer sz = sizeByTypeIdx.get(di);
                        flen = sz != null ? sz.intValue() : (ft != null ? ft.getLength() : -1);
                        // ★ 依赖结构体缺失、或 Ghidra 里的长度与规格不一致时，
                        //   退化成「同长度填充」而不是丢掉整个类型。
                        //   这样后续字段偏移完全不受影响，只损失这一个字段的类型。
                        if (ft == null || flen <= 0 || ft.getLength() != flen) {
                            if (flen <= 0) { bad = true; rDep++; break; }
                            sdt.add(new ArrayDataType(new Undefined1DataType(), flen, 1, dtm),
                                    flen, String.format("pad_%X", off), null);
                            cur += flen;
                            nPadDep++;
                            continue;
                        }
                    } else {
                        ft = scalar(kind);
                        if (ft == null) { bad = true; rScalar++; break; }
                        flen = ft.getLength();
                    }
                    if (flen <= 0) { bad = true; rLen++; break; }
                    sdt.add(ft, flen, arg, null);
                    cur += flen;
                    nField++;
                }
                if (bad) { nSkip++; continue; }
                // 不足的部分补尾填充；超出就按实际布局长度（不再整类丢弃）
                if (cur < size) {
                    int gap = size - cur;
                    sdt.add(new ArrayDataType(new Undefined1DataType(), gap, 1, dtm),
                            gap, String.format("pad_%X", cur), null);
                    nTrail++;
                }
                // ★ 绝不调用 dtm.remove()：它会 deleteDataTypesUsed → clearData
                //   遍历全程序地址清引用，单次数十秒，2.4 万次跑不完。
                //   新根 /bh3v2 里不会有冲突，直接 add 即可。
                DataType added = dtm.addDataType(sdt, DataTypeConflictHandler.REPLACE_HANDLER);
                if (added != null) {
                    byTypeIdx.put(ti, added);
                    nStruct++;
                    if (nStruct % 2000 == 0) {
                        println("STRUCTS " + nStruct + "  " + nSkip + " skip  "
                                + (System.currentTimeMillis() - t0) / 1000 + "s");
                    }
                } else {
                    nFail++;
                }
            }
            br.close();
        } finally {
            dtm.endTransaction(tx, true);
        }
        println("STRUCTS done: created=" + nStruct + " skip=" + nSkip + " fail=" + nFail
                + " fields=" + nField + " padDep=" + nPadDep + " trail=" + nTrail
                + " | why: size=" + rSize + " off=" + rOff + " spec=" + rSpec
                + " len=" + rLen + " dep=" + rDep + " scalar=" + rScalar + " exist=" + rExist
                + "  " + (System.currentTimeMillis() - t0) / 1000 + "s");
        rep.write("# structs created=" + nStruct + " skip=" + nSkip + " fail=" + nFail
                + " fields=" + nField + " padDep=" + nPadDep + " trail=" + nTrail + "\n");

        if (dry) {
            rep.close();
            println("DRY RUN, skip retyping");
            return;
        }

        // ---------------- 2) 重定型 this ----------------
        long t1 = System.currentTimeMillis();
        int nOk = 0, nNoFn = 0, nNoParam = 0, nNoType = 0, nErr = 0, n = 0;
        BufferedReader br = new BufferedReader(new FileReader(thisPath), 1 << 16);
        String line;
        while ((line = br.readLine()) != null) {
            if (line.startsWith("rva")) continue;
            String[] p = line.split("\t");
            if (p.length < 2) continue;
            n++;
            if (maxFuncs > 0 && n > maxFuncs) break;
            long rva = Long.parseLong(p[0], 16);
            long ti = Long.parseLong(p[1]);
            DataType dt = byTypeIdx.get(ti);
            if (dt == null) { nNoType++; continue; }
            Address a = sp.getAddress(IMAGE_BASE + rva);
            if (a == null) { nNoFn++; continue; }
            Function f = currentProgram.getFunctionManager().getFunctionAt(a);
            if (f == null) f = currentProgram.getFunctionManager().getFunctionContaining(a);
            if (f == null) { nNoFn++; continue; }
            int tx2 = currentProgram.startTransaction("bh3 this");
            try {
                PointerDataType ptr = new PointerDataType(dt, dtm);
                if (f.getParameterCount() > 0) {
                    Parameter p0 = f.getParameter(0);
                    p0.setDataType(ptr, SourceType.USER_DEFINED);
                } else {
                    // 函数在库里还没有参数表（建函数时没做签名推断），
                    // 直接追加一个 this —— Ghidra 会按 x64 约定把它放到 RCX
                    f.addParameter(new ParameterImpl("this", ptr, currentProgram),
                            SourceType.USER_DEFINED);
                }
                nOk++;
            } catch (Exception e) {
                nErr++;
                if (nErr <= 5) rep.write("ERR " + p[0] + " " + e + "\n");
            } finally {
                currentProgram.endTransaction(tx2, true);
            }
            if (nOk % 5000 == 0 && nOk > 0) {
                rep.flush();
                println("RETYPE ok=" + nOk + "/" + n + "  "
                        + (System.currentTimeMillis() - t1) / 1000 + "s");
            }
        }
        br.close();
        rep.write("# retype ok=" + nOk + " noFn=" + nNoFn + " noParam=" + nNoParam
                + " noType=" + nNoType + " err=" + nErr + "\n");
        rep.close();
        println("RETYPE done: ok=" + nOk + " noFn=" + nNoFn + " noParam=" + nNoParam
                + " noType=" + nNoType + " err=" + nErr + "  "
                + (System.currentTimeMillis() - t1) / 1000 + "s");
    }
}
