#!/bin/bash
echo "===analyzeHeadless MAXMEM 相关==="
grep -n -B4 -A8 'MAXMEM' ~/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless
echo
echo "===launch.sh 里 MAXMEM 的默认值逻辑==="
grep -n -B6 -A10 'MAXMEM_DEFAULT\|MAXMEM=' ~/opt/ghidra_12.1.4_PUBLIC/support/launch.sh | head -60
