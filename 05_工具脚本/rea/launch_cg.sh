#!/bin/bash
# launch_cg.sh — 后台启动「全量调用图导出」，立刻返回
# 用法: launch_cg.sh [MAXMEM]
set -u
MM="${1:-3G}"
DIR="$HOME/re/cg"
mkdir -p "$DIR"
GH="$HOME/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless"
rm -f "$DIR/run.out" "$DIR/meta.txt"

# 用 ( ... & ) 双重脱离：脚本自己立刻退出，ssh 通道才能 EOF
(
  setsid nohup env GHIDRA_HEADLESS_MAXMEM="$MM" "$GH" \
    "$HOME/re/ghidra/proj4" bh3fix \
    -process UserAssembly_fixed.dll \
    -noanalysis \
    -scriptPath "$HOME/re/ghidra/scripts" \
    -postScript DumpCallGraph.java "$DIR/funcs.tsv" "$DIR/edges.tsv" \
    > "$DIR/run.out" 2>&1 < /dev/null &
)

echo "STARTED dir=$DIR maxmem=$MM"
