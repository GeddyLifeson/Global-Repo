#!/bin/bash
# cl.sh CLIENTDIR OUTDIR PORT : start the client (multiplayer quick play) under Xvfb in the background; returns at once
CL=$1 OUT=$2 PORT=$3; mkdir -p $OUT
export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe DISPLAY=:95
true
if [ -f $CL/options.txt ]; then sed -i 's/^onboardAccessibility:true/onboardAccessibility:false/' $CL/options.txt; grep -q onboardAccessibility $CL/options.txt || echo onboardAccessibility:false >> $CL/options.txt; else echo onboardAccessibility:false > $CL/options.txt; fi
rm -f $CL/logs/latest.log
( timeout 3000 portablemc --main-dir /home/user/w-pack/mc start --mc-dir $CL neoforge::26.1.2.116 -u Tester --jvm /home/user/jdk25/bin/java \
  --jvm-arg=-Xmx4500M --jvm-arg=-Xms1G --jvm-arg=-XX:+UseCompactObjectHeaders --join-server 127.0.0.1 --join-server-port $PORT > $OUT/portablemc.out 2>&1 3>&-; echo "exit $?" >> $OUT/portablemc.out ) &
