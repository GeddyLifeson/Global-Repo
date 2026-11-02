#!/bin/bash
# cl_sp.sh CLIENTDIR OUTDIR : singleplayer quick play into saves/world
CL=$1 OUT=$2; mkdir -p $OUT
export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe DISPLAY=:95
sed -i 's/^onboardAccessibility:true/onboardAccessibility:false/' $CL/options.txt
rm -f $CL/logs/latest.log
( timeout 3000 portablemc --main-dir /home/user/w-pack/mc start --mc-dir $CL neoforge::26.1.2.116 -u Tester --jvm /home/user/jdk25/bin/java \
  --jvm-arg=-Xmx6G --jvm-arg=-Xms2G --jvm-arg=-XX:+UseCompactObjectHeaders --join-world world > $OUT/portablemc.out 2>&1 3>&-; echo "exit $?" >> $OUT/portablemc.out ) &
