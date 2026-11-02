#!/bin/bash
# stboot.sh SRV LOG "cmd1;cmd2" WAITPATTERN: boot, run console commands, wait for pattern, stop
SRV=$1 LOG=$2 CMDS=$3 PAT=$4; cd $SRV; export PATH=/home/user/jdk25/bin:$PATH
IN=$LOG.in; rm -f $IN $LOG.exit; mkfifo $IN
( tail -f $IN | java -Xms4G -Xmx6G @libraries/net/neoforged/neoforge/26.1.2.116/unix_args.txt nogui > $LOG 2>&1 3>&-; echo "JAVA_EXIT $?" >> $LOG.exit ) &
t0=$(date +%s)
until grep -qE 'Done \([0-9.]+s\)!|Crash Report|Mod loading has failed' $LOG || [ $(( $(date +%s)-t0 )) -gt 900 ]; do sleep 2; done
sleep 5
IFS=';' read -ra A <<< "$CMDS"
for c in "${A[@]}"; do echo "$c" > $IN; sleep 3; done
t1=$(date +%s)
until grep -qE "$PAT" $LOG || [ $(( $(date +%s)-t1 )) -gt 300 ]; do sleep 2; done
sleep 3; echo stop > $IN
t2=$(date +%s); until [ -s $LOG.exit ] || [ $(( $(date +%s)-t2 )) -gt 120 ]; do sleep 1; done
cat $LOG.exit
P=$(pgrep -f "^tail -f $IN\$"); [ -n "$P" ] && kill $P
