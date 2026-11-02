#!/bin/bash
export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe
cd /home/user
xvfb-run -a -s "-screen 0 1280x720x24" timeout 2400 portablemc --main-dir /home/user/mc start --mc-dir /home/user/cit6/client-_24snt0h neoforge::26.1.2.116 -u Tester --jvm /home/user/jdk/jdk-25.0.4.1+1/bin/java --jvm-arg=-Xmx8G --jvm-arg=-Xms2G --jvm-arg=-Xlog:gc*:file=/home/user/boot/client_gc.log --join-world world > /home/user/boot/client_out.log 2>&1
echo "exit $?" >> /home/user/boot/client_out.log
