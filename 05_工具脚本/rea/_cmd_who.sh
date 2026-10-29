#!/bin/bash
echo "===PID 16176 身份==="
tr '\0' ' ' < /proc/16176/cmdline 2>/dev/null | cut -c1-400
echo
echo "父进程: $(awk '/^PPid/{print $2}' /proc/16176/status 2>/dev/null)"
echo "启动: $(ps -o lstart= -p 16176 2>/dev/null)"
echo "状态: $(awk '/^State/{print $2,$3}' /proc/16176/status 2>/dev/null)"
echo
echo "===分析是否已建出函数（日志关键字）==="
grep -ac 'FUNCCOUNT' ~/re/pilot_p4/run.out 2>/dev/null
echo "===当前可用内存==="
free -m | head -2
