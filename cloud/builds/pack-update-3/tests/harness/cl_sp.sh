#!/bin/bash
# cl_srv.sh CLIENTDIR OUTDIR: headless client joins 127.0.0.1:25565
CL=$1 OUT=$2; mkdir -p $OUT
export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe DISPLAY=:96
pgrep -f 'Xvfb :96' >/dev/null || { Xvfb :96 -screen 0 1280x720x24 >/dev/null 2>&1 3>&- & sleep 2; }
if [ -f $CL/options.txt ]; then sed -i 's/^onboardAccessibility:true/onboardAccessibility:false/' $CL/options.txt; else echo onboardAccessibility:false > $CL/options.txt; fi
rm -f $CL/logs/latest.log
( timeout 2400 portablemc --main-dir /home/user/w-pack/mc start --mc-dir $CL neoforge::26.1.2.116 -u Tester --jvm /home/user/jdk25/bin/java \
  --jvm-arg=-Xmx6G --jvm-arg=-Xms2G --jvm-arg=-XX:+UseCompactObjectHeaders --join-world world > $OUT/portablemc.out 2>&1 3>&-; echo "exit $?" >> $OUT/portablemc.out ) &
