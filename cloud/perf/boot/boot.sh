#!/bin/bash
cd /home/user/boot/srv
export PATH=/home/user/jdk/jdk-25.0.4.1+1/bin:$PATH
rm -f /tmp/claude-0/bootin; mkfifo /tmp/claude-0/bootin
( tail -f /tmp/claude-0/bootin | timeout 2400 ./run.sh nogui > /home/user/boot/boot.log 2>&1; echo "exit $?" >> /home/user/boot/boot.log ) &
for i in $(seq 1 2400); do
  sleep 1
  if grep -q -E "Done \([0-9.]+s\)! For help" /home/user/boot/boot.log; then echo stop > /tmp/claude-0/bootin; sleep 60; break; fi
  grep -q "^exit " /home/user/boot/boot.log && break
done
echo stop > /tmp/claude-0/bootin 2>/dev/null; sleep 5; pkill -f "tail -f /tmp/claude-0/bootin"
grep -E "Done \(|Crash|crash report|Exception in|FATAL|Mod loading has failed" /home/user/boot/boot.log | head -20
