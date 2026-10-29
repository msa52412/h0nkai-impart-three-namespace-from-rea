#!/bin/bash
# pilot.sh — 带 RSS 采样的 Ghidra 分析压测
# 用法: pilot.sh <MAXMEM> <超时秒> <工程目录> <工程名> <程序名> <标签>
set -u
MAXMEM_V="${1:-4G}"
TMO="${2:-600}"
PROJDIR="${3:-$HOME/re/ghidra/proj4}"
PROJNAME="${4:-bh3fix}"
PROG="${5:-UserAssembly_fixed.dll}"
TAG="${6:-pilot}"

GH="$HOME/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless"
OUT="$HOME/re/pilot_$TAG"
mkdir -p "$OUT"
rm -f "$OUT/rss.txt" "$OUT/run.out"

echo "start=$(date +%s) maxmem=$MAXMEM_V timeout=$TMO" > "$OUT/meta.txt"

# --- RSS 采样器：每 2 秒抓一次 java 进程 RSS(KB) 和系统可用内存 ---
(
  while true; do
    RS=$(ps -eo rss,comm --sort=-rss 2>/dev/null | awk '$2 ~ /^java/ {print $1; exit}')
    AV=$(free -m | awk '/^Mem:/{print $7}')
    [ -z "$RS" ] && RS=0
    echo "$(date +%s) ${RS:-0} ${AV:-0}" >> "$OUT/rss.txt"
    sleep 2
  done
) &
SAMPLER=$!

# --- 主分析 ---
MAXMEM="$MAXMEM_V" "$GH" "$PROJDIR" "$PROJNAME" \
  -process "$PROG" \
  -analysisTimeoutPerFile "$TMO" \
  -scriptPath "$HOME/re/ghidra/scripts" \
  -postScript FuncCount.java \
  > "$OUT/run.out" 2>&1
RC=$?

kill $SAMPLER 2>/dev/null
wait $SAMPLER 2>/dev/null

echo "rc=$RC end=$(date +%s)" >> "$OUT/meta.txt"

# --- 汇总 ---
awk 'BEGIN{mx=0;mn=999999999} {if($2>mx)mx=$2; if($3<mn)mn=$3; n++}
     END{printf "samples=%d peakRssMb=%.0f minAvailMb=%d\n", n, mx/1024, mn}' \
     "$OUT/rss.txt" >> "$OUT/meta.txt"
echo "---META---"; cat "$OUT/meta.txt"
echo "---FUNC---"; grep -a 'FUNCCOUNT' "$OUT/run.out" || echo "(no FUNCCOUNT)"
echo "---TAIL---"; tail -15 "$OUT/run.out"
