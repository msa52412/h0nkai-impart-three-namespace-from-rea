#!/bin/bash
echo "===META==="
cat ~/re/pilot_p4/meta.txt
echo
echo "===FUNCCOUNT 全文==="
grep -a 'FUNCCOUNT' ~/re/pilot_p4/run.out
echo
echo "===RSS 峰值曲线（每 30 采样=1分钟）==="
awk 'NR%30==1{printf "%s  RSS %6.0f MB  可用 %5d MB\n", strftime("%H:%M:%S",$1), $2/1024, $3}' ~/re/pilot_p4/rss.txt
echo
echo "===尾部日志==="
tail -8 ~/re/pilot_p4/run.out | cut -c1-150
echo
echo "===工程/磁盘==="
du -sh ~/re/ghidra/proj4/; df -h /home | tail -1
