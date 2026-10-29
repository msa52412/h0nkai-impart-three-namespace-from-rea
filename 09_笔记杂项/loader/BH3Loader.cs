// BH3Loader —— 自建启动器：绕过 BH3Base.dll 的文件完整性校验
//
// 原理
// ----
// 崩坏3 PC 的进程结构（实测）：
//
//     BH3.exe (648 KB stub)
//       └─ 导入 BH3Base.dll!ord#1        <- 完整性校验 / SDK / ACE 都在这里
//            └─ 调用 UnityPlayer.dll!UnityMain(cmdline)
//
//   * UnityPlayer.dll  **只导出 1 个函数**：UnityMain
//   * BH3Base.dll      **只导出 1 个函数**：ord#1（无名）
//   * UserAssembly.dll 导入表：ADVAPI32/IPHLPAPI/KERNEL32/OLEAUT32/SHELL32/USER32/WS2_32/ole32
//     不含 BH3Base、不含 AntiCheatExpert、不含 ACE-DRV，字符串里也 0 次出现
//   * UnityPlayer.dll 导入表同样不含 BH3Base / ACE
//
//   => 游戏本体与启动器、反作弊之间没有任何依赖。
//      自己调用 UnityMain，校验器和 ACE 都不会被加载，
//      于是 UserAssembly.dll 可以随便改。
//
// 编译
// ----
//   csc /target:winexe /platform:x64 /out:BH3.exe BH3Loader.cs
//
// 部署（重要：Unity 用「宿主 exe 文件名」推导数据目录 <exe名>_Data）
// ----
//   1. cd D:\BH3\7.0
//   2. ren BH3.exe BH3.exe.orig
//   3. 把编译出的 BH3.exe 放到 D:\BH3\7.0\
//   4. 直接运行 BH3.exe
//
//   若不想动原 BH3.exe，也可以编译成 BH3Loader.exe 并建一个目录联接：
//       mklink /J D:\BH3\7.0\BH3Loader_Data D:\BH3\7.0\BH3_Data
//
// 排错
// ----
//   运行后同目录会生成 BH3Loader.log，记录每一步及 GetLastError。
//   UnityMain 的参数通常是：
//       int UnityMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
//                     LPWSTR lpCmdLine, int nShowCmd)
//   个别版本用 LPSTR。源码里 ANSI 分支已备好，改 USE_ANSI 常量即可。

using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

static class BH3Loader
{
    // Unity 2017.4.18f1 用宽字符命令行；若启动失败可改这里对比
    const bool USE_ANSI = false;

    [DllImport("kernel32", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern IntPtr LoadLibraryW(string lpFileName);

    [DllImport("kernel32", CharSet = CharSet.Ansi, SetLastError = true)]
    static extern IntPtr GetProcAddress(IntPtr hModule, string lpProcName);

    [DllImport("kernel32", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool SetCurrentDirectoryW(string lpPathName);

    [DllImport("kernel32", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool SetDllDirectoryW(string lpPathName);

    [DllImport("kernel32")]
    static extern IntPtr GetModuleHandleW(string lpModuleName);

    [UnmanagedFunctionPointer(CallingConvention.StdCall, CharSet = CharSet.Unicode)]
    delegate int UnityMainW(IntPtr hInstance, IntPtr hPrevInstance, string lpCmdLine, int nShowCmd);

    [UnmanagedFunctionPointer(CallingConvention.StdCall, CharSet = CharSet.Ansi)]
    delegate int UnityMainA(IntPtr hInstance, IntPtr hPrevInstance, string lpCmdLine, int nShowCmd);

    static StreamWriter log;

    static void Log(string s)
    {
        try
        {
            if (log == null)
                log = new StreamWriter(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "BH3Loader.log"), false, Encoding.UTF8);
            log.WriteLine(DateTime.Now.ToString("HH:mm:ss.fff") + "  " + s);
            log.Flush();
        }
        catch { }
    }

    [STAThread]
    static int Main(string[] args)
    {
        string exeDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\');
        string exePath = Path.Combine(exeDir, Path.GetFileName(Environment.GetCommandLineArgs()[0]));
        string dataDir = Path.Combine(exeDir, Path.GetFileNameWithoutExtension(exePath) + "_Data");
        string unityDll = Path.Combine(exeDir, "UnityPlayer.dll");

        Log("=== BH3Loader 启动 ===");
        Log("exe      = " + exePath);
        Log("dataDir  = " + dataDir);
        Log("unityDll = " + unityDll);

        if (!Directory.Exists(dataDir))
            Log("警告: 数据目录不存在，Unity 可能会自己报 Data folder not found");

        SetCurrentDirectoryW(exeDir);
        SetDllDirectoryW(exeDir);

        IntPtr h = LoadLibraryW(unityDll);
        if (h == IntPtr.Zero)
        {
            Log("LoadLibraryW 失败, err=" + Marshal.GetLastWin32Error());
            return 2;
        }
        Log("UnityPlayer.dll 已加载 @ " + h.ToString("X"));

        IntPtr fn = GetProcAddress(h, "UnityMain");
        if (fn == IntPtr.Zero)
        {
            Log("GetProcAddress(UnityMain) 失败, err=" + Marshal.GetLastWin32Error());
            return 3;
        }
        Log("UnityMain @ " + fn.ToString("X"));

        // 命令行：默认空。若需要可在此拼接，例如 -screen-width 1920 -screen-height 1080
        string cmd = string.Join(" ", args);
        Log("命令行 = \"" + cmd + "\"");

        IntPtr hInst = GetModuleHandleW(null);
        int rc;
        try
        {
            if (USE_ANSI)
                rc = Marshal.GetDelegateForFunctionPointer<UnityMainA>(fn)(hInst, IntPtr.Zero, cmd, 5);
            else
                rc = Marshal.GetDelegateForFunctionPointer<UnityMainW>(fn)(hInst, IntPtr.Zero, cmd, 5);
        }
        catch (Exception e)
        {
            Log("调用 UnityMain 抛异常: " + e);
            return 4;
        }

        Log("UnityMain 返回 " + rc);
        return rc;
    }
}
