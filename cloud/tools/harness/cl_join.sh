#!/bin/bash
# S0334 cl_join.sh CLIENTDIR OUTDIR : headless client (Xvfb + portablemc) joins a world or server; returns at once.
# Env: JAVA_HOME (default /tmp/claude-0/jdk25), NF (NeoForge version, default 26.1.2.116), MCDIR (portablemc main dir, default /tmp/claude-0/mc), DISPLAY_NUM (96), XMX (6G), JOIN ("--join-world world" or "--server 127.0.0.1 --port 25565"), TIMEOUT (2400).
# portablemc 5.x flags (pip install "portablemc>=5"): JOIN="--join-world world" or "--join-server 127.0.0.1 --join-server-port 25565". Old "--server/--port" are translated below.
# Needs a machine with enough RAM; the cloud cannot run the full pack client (OOM), so use it for light packs only.
CL=$1 OUT=$2; mkdir -p "$OUT"
D=${DISPLAY_NUM:-96}; export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe DISPLAY=:$D
pgrep -f "Xvfb :$D" >/dev/null || { Xvfb :$D -screen 0 1280x720x24 >/dev/null 2>&1 3>&- & sleep 2; }
if [ -f "$CL/options.txt" ]; then sed -i 's/^onboardAccessibility:true/onboardAccessibility:false/' "$CL/options.txt"; else echo onboardAccessibility:false > "$CL/options.txt"; fi
JOIN=$(echo "${JOIN:---join-world world}" | sed "s/--server /--join-server /; s/--port /--join-server-port /")
rm -f "$CL/logs/latest.log"
( timeout ${TIMEOUT:-2400} portablemc --main-dir ${MCDIR:-/tmp/claude-0/mc} start --mc-dir "$CL" neoforge::${NF:-26.1.2.116} -u Tester --jvm ${JAVA_HOME:-/tmp/claude-0/jdk25}/bin/java \
  --jvm-arg=-Xmx${XMX:-6G} --jvm-arg=-Xms2G --jvm-arg=-XX:+UseCompactObjectHeaders $JOIN > "$OUT/portablemc.out" 2>&1 3>&-; echo "exit $?" >> "$OUT/portablemc.out" ) &
