#!/bin/bash
# hold.sh CLIENTDIR: start the client under Xvfb :91 and leave it running (killed by hand)
CL=$1; export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe DISPLAY=:91
pgrep -x Xvfb >/dev/null || { Xvfb :91 -screen 0 1280x720x24 >/dev/null 2>&1 3>&- & sleep 2; }
rm -f $CL/logs/latest.log
timeout 3000 portablemc --main-dir /home/user/w-pack/mc start --mc-dir $CL neoforge::26.1.2.116 -u Tester --jvm /home/user/jdk25/bin/java \
  --jvm-arg=-Xmx6G --jvm-arg=-Xms2G --jvm-arg=-XX:+UseCompactObjectHeaders --join-world world > $CL/../hold.out 2>&1 3>&-
