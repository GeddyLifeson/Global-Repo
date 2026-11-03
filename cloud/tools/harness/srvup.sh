#!/bin/bash
# S0331 srvup.sh SRV LOG : boot a NeoForge server and leave it running; commands go to LOG.in (use cmd.sh). Prints Done/failed line.
# Env: JAVA_HOME (default /tmp/claude-0/jdk25), NF (NeoForge version, default: auto-detect from SRV/libraries), XMX (default 2500M), WAIT (default 900 s).
SRV=$1 LOG=$2; cd "$SRV" || exit 1; LOG=$(realpath -m "$LOG")
export PATH=${JAVA_HOME:-/tmp/claude-0/jdk25}/bin:$PATH
NF=${NF:-$(ls libraries/net/neoforged/neoforge | sort -V | tail -1)}
IN=$LOG.in; rm -f "$IN" "$LOG.exit"; mkfifo "$IN"
( tail -f "$IN" | java -Xms1G -Xmx${XMX:-2500M} @libraries/net/neoforged/neoforge/$NF/unix_args.txt nogui > "$LOG" 2>&1 3>&-; echo "JAVA_EXIT $?" >> "$LOG.exit" ) &
t0=$(date +%s)
until grep -qE 'Done \([0-9.]+s\)!|Mod loading has failed' "$LOG" || [ $(( $(date +%s)-t0 )) -gt ${WAIT:-900} ]; do sleep 2; done
grep -oE 'Done \([0-9.]+s\)!|Mod loading has failed' "$LOG" | head -1
