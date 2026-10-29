#!/bin/bash
# run_dump.sh — 在 105 上启动一轮 DumpBodies
# 用法: run_dump.sh <listFile> [outFile]
# 单独做成脚本的目的：避免用 pkill -f 'analyzeHeadless.*body_list' 那种模式匹配
# —— 发起命令的 shell 自身命令行里也含这些词，会被自己杀掉（rc=-1）。
set -u
LIST="${1:?need listFile}"
OUT="${2:-/home/nas/re/sym/bodies_b.tsv}"
LOG=/home/nas/re/sym/bodies_b.log
GH=/home/nas/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless

cd /home/nas/re/ghidra || exit 1
GHIDRA_HEADLESS_MAXMEM=3G nohup "$GH" \
  /home/nas/re/ghidra/proj4 bh3fix \
  -process UserAssembly_fixed.dll -noanalysis \
  -scriptPath /home/nas/re/ghidra/scripts \
  -postScript DumpBodies.java "$LIST" "$OUT" \
  > "$LOG" 2>&1 &
echo "started pid=$!"
