@echo off
rem ============================================================
rem  BH3 逆向进度看板  —  双击即可运行
rem  用法：
rem    双击            自动监控最新的 Ghidra 工程，每 10 秒刷新
rem    拖入工程名       如 proj4，只看指定工程
rem    Ctrl-C          退出
rem ============================================================
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
cd /d "%~dp0"

rem --- 找 Python：先用托管版，找不到再退回 PATH 里的 ---
set "PY=C:\Users\Administrator\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe"
if not exist "%PY%" set "PY=python"

rem --- paramiko 在本目录的 _pylibs 下 ---
set "PYTHONPATH=%~dp0_pylibs"

title BH3 逆向进度看板
echo.
echo   ============================================
echo    BH3 逆向进度看板   远端 192.168.0.104
echo    每 10 秒刷新，Ctrl-C 退出
echo   ============================================
echo.

if "%~1"=="" (
    "%PY%" mon.py -w 10
) else (
    "%PY%" mon.py -w 10 --proj %~1
)

echo.
echo   监控已停止。
pause
