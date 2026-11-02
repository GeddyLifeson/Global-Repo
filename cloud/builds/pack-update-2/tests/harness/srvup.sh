#!/bin/bash
# srvup.sh SRV LOG : boot the server and leave it running; commands go to LOG.in
SRV=$1 LOG=$2; cd $SRV; export PATH=/home/user/jdk25/bin:$PATH
IN=$LOG.in; rm -f $IN $LOG.exit $LOG.pid; mkfifo $IN
( tail -f $IN | java -Xms1G -Xmx2500M @libraries/net/neoforged/neoforge/26.1.2.116/unix_args.txt nogui > $LOG 2>&1 3>&-; echo "JAVA_EXIT $?" >> $LOG.exit ) &
t0=$(date +%s)
until grep -qE 'Done \([0-9.]+s\)!|Mod loading has failed' $LOG || [ $(( $(date +%s)-t0 )) -gt 900 ]; do sleep 2; done
grep -oE 'Done \([0-9.]+s\)!|Mod loading has failed' $LOG | head -1
