#!/bin/bash
# client.sh CLIENTDIR OUTDIR [maxsec]: boot the client under Xvfb, quick-play into saves/world, screenshots + jstack on stall
CL=$1 OUT=$2 MAX=${3:-1800}; mkdir -p $OUT; rm -f $OUT/*
export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe DISPLAY=:91
pgrep -x Xvfb >/dev/null || { Xvfb :91 -screen 0 1280x720x24 >/dev/null 2>&1 3>&- & sleep 2; }
shot() { xwd -root -silent -display :91 2>/dev/null | convert xwd:- $1.png 2>/dev/null; xwininfo -root -tree -display :91 2>/dev/null | grep -vE '^\s*$' | head -20 > $1.windows.txt; }
# skip the vanilla first-launch accessibility screen, which holds quick-play until clicked
if [ -f $CL/options.txt ]; then sed -i 's/^onboardAccessibility:true/onboardAccessibility:false/' $CL/options.txt; else echo onboardAccessibility:false > $CL/options.txt; fi
LOG=$CL/logs/latest.log; rm -f $LOG
( timeout $MAX portablemc --main-dir /home/user/w-pack/mc start --mc-dir $CL neoforge::26.1.2.116 -u Tester --jvm /home/user/jdk25/bin/java \
  --jvm-arg=-Xmx6G --jvm-arg=-Xms2G --jvm-arg=-XX:+UseCompactObjectHeaders --join-world world > $OUT/portablemc.out 2>&1 3>&-; echo "exit $?" >> $OUT/portablemc.out ) &
t0=$(date +%s); last=0; lastsz=0; stall=0; n=0; res=TIMEOUT
while true; do
  sleep 15; el=$(( $(date +%s)-t0 ))
  grep -q '^exit ' $OUT/portablemc.out && { res=EXITED; break; }
  [ $el -gt $MAX ] && break
  if [ -f $LOG ] && grep -qE 'joined the game' $LOG; then
    echo "joined_at $(grep -m1 'joined the game' $LOG | cut -c1-10)" > $OUT/joined.txt
    JP0=$(for p in $(pgrep java); do [ "$(readlink /proc/$p/cwd)" = "$CL" ] && tr '\0' ' ' < /proc/$p/cmdline | grep -q Xmx6G && echo $p; done | head -1)
    sleep 150
    if grep -q 'Client disconnected' $LOG; then res=JOINED_THEN_DISCONNECTED; else res=JOINED_IN_WORLD; fi
    shot $OUT/world
    /home/user/jdk25/bin/jcmd $JP0 GC.class_histogram 2>/dev/null | grep -E 'client.gui.screens|Screen ' | head -20 > $OUT/screens.txt
    break
  fi
  if [ -f $LOG ] && grep -qE -e '---- Minecraft Crash Report|Mod loading has failed|FatalStartupException|Critical injection failure|Missing or unsupported mandatory|Network Protocol Error|Missing element ResourceKey' $LOG; then sleep 10; res=CRASH; break; fi
  sz=$(stat -c %s $LOG 2>/dev/null || echo 0)
  if [ $sz -eq $lastsz ]; then stall=$((stall+15)); else stall=0; lastsz=$sz; fi
  if [ $(( el % 120 )) -lt 15 ]; then n=$((n+1)); shot $OUT/shot_$n; fi
  if [ $stall -ge ${STALL:-600} ]; then res=STALL; break; fi
done
P=$(pgrep -f 'cpw.mods|neoforged.*client|net.neoforged.fml.startup.Client' | head -1)
[ -z "$P" ] && P=$(pgrep -f "mc-dir $CL" -n)
JP=$(pgrep -f 'java.*-XX:\+UseCompactObjectHeaders.*Tester' | head -1)
shot $OUT/final
if [ -n "$JP" ]; then /home/user/jdk25/bin/jstack $JP > $OUT/jstack1.txt 2>&1; sleep 10; /home/user/jdk25/bin/jstack $JP > $OUT/jstack2.txt 2>&1; kill $JP; sleep 10; kill -9 $JP 2>/dev/null; fi
cp $LOG $OUT/latest.log 2>/dev/null; cp $CL/logs/debug.log $OUT/ 2>/dev/null
echo "RESULT $res after $(( $(date +%s)-t0 ))s"
# CrashAssistant spawns a helper JVM that inherits the boot.lock fd; kill every JVM left in this client dir
for p in $(pgrep java); do [ "$(readlink /proc/$p/cwd)" = "$CL" ] && kill $p; done
