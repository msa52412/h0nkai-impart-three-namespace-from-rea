// ApplySig.java —— 把 C# 方法签名（返回类型 + 参数类型/名字）写回 Ghidra
//
// 用法：
//   -postScript ApplySig.java <bh3_sigs.tsv> <bh3_structs2.tsv> <report.txt> [dryRun 0/1] [maxFuncs 0=全部]
//
// 设计要点（都是踩过坑之后的结论）：
//   1) 结构体在 /bh3v5 下（ApplyTypes.java 建的）。这里只按 catPath 查，不再新建。
//   2) 绝不调用 dtm.remove()：它会 deleteDataTypesUsed → CodeManager.clearData
//      遍历全程序地址清引用，单次数十秒。
//   3) 大值类型（>8 字节）返回/参数一律按指针处理 —— MS x64 下就是隐藏指针，
//      gen_sigs.py 已经用 p:<idx> 编码，这里直接照做，不能让 Ghidra 自己去摊平。
//   4) 幂等：先按期望参数个数裁掉多余的，再逐个就地更新/追加。
//@category REA
//@keybinding
//@menupath
//@toolbar

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.HashMap;
import java.util.Map;

public class ApplySig extends GhidraScript {

    private static final long IMAGE_BASE = 0x180000000L;
    private static final String ROOT = "/bh3v8";

    private DataTypeManager dtm;
    private final Map<Long, DataType> byTypeIdx = new HashMap<>();

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
            case "v":  return new VoidDataType();
            default:   return null;
        }
    }

    /** "p:123" / "s:123" / "i4" → DataType；解析不了返回 null */
    private DataType resolve(String kind) {
        if (kind == null || kind.isEmpty()) {
            return null;
        }
        if (kind.startsWith("p:")) {
            DataType d = byTypeIdx.get(Long.parseLong(kind.substring(2)));
            return d == null ? new PointerDataType(dtm) : new PointerDataType(d, dtm);
        }
        if (kind.startsWith("s:")) {
            DataType d = byTypeIdx.get(Long.parseLong(kind.substring(2)));
            return d;                       // 小值类型按值传
        }
        if ("p".equals(kind)) {
            return new PointerDataType(dtm);
        }
        return scalar(kind);
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String sigPath = args.length > 0 ? args[0] : "/home/nas/re/sym/bh3_sigs.tsv";
        String structPath = args.length > 1 ? args[1] : "/home/nas/re/sym/bh3_structs2.tsv";
        String reportPath = args.length > 2 ? args[2] : "/home/nas/re/sym/apply_sig.txt";
        boolean dry = args.length > 3 && "1".equals(args[3]);
        int maxFuncs = args.length > 4 ? Integer.parseInt(args[4]) : 0;

        dtm = currentProgram.getDataTypeManager();
        AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace();
        BufferedWriter rep = new BufferedWriter(new FileWriter(reportPath), 1 << 20);

        // ---------------- 1) typeIdx → 已有结构体 ----------------
        int nStruct = 0;
        BufferedReader bs = new BufferedReader(new FileReader(structPath), 1 << 16);
        String line;
        while ((line = bs.readLine()) != null) {
            if (line.startsWith("typeIdx")) continue;
            String[] p = line.split("\t");
            if (p.length < 7) continue;
            String cp = p[1];
            int k = cp.indexOf('/', 1);
            if (k < 0) continue;
            CategoryPath real = new CategoryPath(ROOT + cp.substring(k));
            DataType d = dtm.getDataType(real, p[2]);
            if (d != null) {
                byTypeIdx.put(Long.parseLong(p[0]), d);
                nStruct++;
            }
        }
        bs.close();
        println("SIG: 结构体索引 " + nStruct + " 个");

        if (dry) {
            rep.close();
            println("DRY RUN, skip");
            return;
        }

        // ---------------- 2) 应用签名 ----------------
        FunctionManager fm = currentProgram.getFunctionManager();
        int nOk = 0, nNoFn = 0, nNoSelf = 0, nErr = 0, n = 0, nRet = 0, nPar = 0;
        long t0 = System.currentTimeMillis();
        BufferedReader br = new BufferedReader(new FileReader(sigPath), 1 << 16);
        while ((line = br.readLine()) != null) {
            if (line.startsWith("rva")) continue;
            String[] p = line.split("\t", -1);
            if (p.length < 6) continue;
            n++;
            if (maxFuncs > 0 && n > maxFuncs) break;
            long rva = Long.parseLong(p[0], 16);
            boolean isStatic = "1".equals(p[1]);
            String thisKind = p[2];
            String retKind = p[3];
            String retName = p[4];
            String params = p[5];

            Address a = sp.getAddress(IMAGE_BASE + rva);
            if (a == null) { nNoFn++; continue; }
            Function f = fm.getFunctionAt(a);
            if (f == null) f = fm.getFunctionContaining(a);
            if (f == null || f.isThunk()) { nNoFn++; continue; }

            DataType selfDt = resolve(thisKind);
            if (!isStatic && selfDt == null) { nNoSelf++; continue; }

            // 参数清单
            String[] ps = params.isEmpty() ? new String[0] : params.split(";");
            int want = (isStatic ? 0 : 1) + ps.length;

            int tx = currentProgram.startTransaction("bh3 sig");
            try {
                // 返回类型
                if (!"v".equals(retKind)) {
                    DataType rdt = resolve(retKind);
                    if (rdt != null) {
                        f.setReturnType(rdt, SourceType.USER_DEFINED);
                        nRet++;
                    }
                } else {
                    f.setReturnType(new VoidDataType(), SourceType.USER_DEFINED);
                    nRet++;
                }

                // 裁掉多余参数
                while (f.getParameterCount() > want) {
                    f.removeParameter(f.getParameterCount() - 1);
                }

                int ord = 0;
                if (!isStatic) {
                    if (f.getParameterCount() > 0) {
                        Parameter p0 = f.getParameter(0);
                        p0.setName("this", SourceType.USER_DEFINED);
                        p0.setDataType(selfDt, SourceType.USER_DEFINED);
                    } else {
                        f.addParameter(new ParameterImpl("this", selfDt, currentProgram),
                                SourceType.USER_DEFINED);
                    }
                    ord = 1;
                }
                for (int i = 0; i < ps.length; i++) {
                    // kind 自身可能带冒号（p:6092 / s:123），参数名已清洗成 [0-9A-Za-z_]，
                    // 所以按最后一个冒号切分才是对的
                    int c = ps[i].lastIndexOf(':');
                    String kd = c > 0 ? ps[i].substring(0, c) : ps[i];
                    String nm = c > 0 ? ps[i].substring(c + 1) : ("a" + i);
                    DataType dt = resolve(kd);
                    if (dt == null) { nErr++; continue; }
                    int at = ord + i;
                    if (f.getParameterCount() > at) {
                        Parameter pa = f.getParameter(at);
                        pa.setName(nm, SourceType.USER_DEFINED);
                        pa.setDataType(dt, SourceType.USER_DEFINED);
                    } else {
                        f.addParameter(new ParameterImpl(nm, dt, currentProgram),
                                SourceType.USER_DEFINED);
                    }
                    nPar++;
                }
                nOk++;
            } catch (Exception e) {
                nErr++;
                if (nErr <= 8) rep.write("ERR " + p[0] + " " + e + "\n");
            } finally {
                currentProgram.endTransaction(tx, true);
            }

            if (nOk % 20000 == 0 && nOk > 0) {
                rep.flush();
                println("SIG ok=" + nOk + "/" + n + "  "
                        + (System.currentTimeMillis() - t0) / 1000 + "s");
            }
        }
        br.close();
        rep.write("# sig ok=" + nOk + " noFn=" + nNoFn + " noSelf=" + nNoSelf
                + " err=" + nErr + " ret=" + nRet + " params=" + nPar + "\n");
        rep.close();
        println("SIG done: ok=" + nOk + " noFn=" + nNoFn + " noSelf=" + nNoSelf
                + " err=" + nErr + " ret=" + nRet + " params=" + nPar + "  "
                + (System.currentTimeMillis() - t0) / 1000 + "s");
    }
}
