#!/bin/bash
# qboot.sh SRV LOG: boot to Done, wait 20 s, stop
SRV=$1 LOG=$2; cd $SRV; export PATH=/home/user/jdk25/bin:$PATH
IN=$LOG.in; rm -f $IN $LOG.exit; mkfifo $IN
( tail -f $IN | java -Xms4G -Xmx6G @libraries/net/neoforged/neoforge/26.1.2.116/unix_args.txt nogui > $LOG 2>&1; echo "JAVA_EXIT $?" >> $LOG.exit ) &
t0=$(date +%s)
until grep -qE 'Done \([0-9.]+s\)!|Crash Report|crash report has been saved|Mod loading has failed|FatalStartupException' $LOG || [ $(( $(date +%s)-t0 )) -gt 900 ]; do sleep 2; done
sleep 20; timeout 5 bash -c "echo stop > $IN"; t1=$(date +%s)
until [ -s $LOG.exit ] || [ $(( $(date +%s)-t1 )) -gt 120 ]; do sleep 1; done
echo "stop_to_exit_s $(( $(date +%s)-t1 ))"; cat $LOG.exit 2>/dev/null
P=$(pgrep -f "^tail -f $IN\$"); [ -n "$P" ] && kill $P
grep -oE 'Done \([0-9.]+s\)!|Mod loading has failed|FatalStartupException' $LOG | head -2
