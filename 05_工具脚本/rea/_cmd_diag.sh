#!/bin/bash
# 远端诊断：Xmx 是否生效 + 当前内存/进度
echo "===JAVA_PROCS==="
for p in $(ls /proc | grep -E '^[0-9]+$'); do
  c=$(cat /proc/$p/comm 2>/dev/null)
  case "$c" in
    java|MainThread)
      echo "PID $p comm=$c rss=$(awk '/VmRSS/{print $2}' /proc/$p/status 2>/dev/null)KB"
      tr '\0' '\n' < /proc/$p/cmdline 2>/dev/null | grep -E '^-Xm|^MAXMEM' | sed 's/^/    arg: /'
      ;;
  esac
done
echo "===ENV_OF_LAUNCHER==="
for p in $(ls /proc | grep -E '^[0-9]+$'); do
  c=$(cat /proc/$p/comm 2>/dev/null)
  if [ "$c" = "java" ]; then
    tr '\0' '\n' < /proc/$p/environ 2>/dev/null | grep -E '^MAXMEM' | sed 's/^/    env: /'
  fi
done
echo "===RSS_TAIL==="
tail -4 ~/re/pilot_p4/rss.txt
echo "===DB==="
du -sh ~/re/ghidra/proj4/ 2>/dev/null
df -h /home | tail -1
echo "===META==="
cat ~/re/pilot_p4/meta.txt 2>/dev/null
echo "===LOGTAIL==="
tail -6 ~/re/pilot_p4/run.out
