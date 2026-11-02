#!/bin/bash
# per batch: fresh server (boot = new world), client boot + quick-play join on that world; bench for 3 and 4
export PATH=/home/user/jdk25/bin:$PATH
W=/home/user/w-pack; L=/tmp/claude-0/boot.lock
for n in ${BATCHES:-1 2 3 4}; do
  S=$W/srvt$n; C=$W/clt$n
  rm -rf $S $C; cp -al $W/ci$n/server-* $S; cp -al $W/ci$n/client-* $C
  (cd $S && java -jar $W/pw/neoforge-26.1.2.116-installer.jar --installServer > /dev/null 2>&1)
  echo eula=true > $S/eula.txt; cp $W/srv-b3/server.properties $S/; mkdir -p $S/off; mv $S/mods/grieflogger* $S/off/ 2>/dev/null
  echo "== batch $n server: $(flock $L $W/s/qboot.sh $S $W/qbt$n.log | tr '\n' ' ')"
  P=$(for p in $(pgrep java); do [ "$(readlink /proc/$p/cwd)" = "$S" ] && echo $p; done); [ -n "$P" ] && { echo "killing leftover server JVM $P"; kill -9 $P; }
  mkdir -p $C/saves; cp -r $S/world $C/saves/world
  echo "== batch $n client: $(STALL=420 flock $L $W/s/client.sh $C $W/crt$n 1800 | tail -1) $(cat $W/crt$n/joined.txt 2>/dev/null | tr '\n' ' ')"
  for p in $(pgrep java); do [ "$(readlink /proc/$p/cwd)" = "$C" ] && kill -9 $p; done
done
for n in ${BENCH:-3 4}; do
  S=$W/srvt$n; rm -rf $S/world
  flock $L bash $W/perfbr/diaithir-perf/bench/bench.sh $S $W/bencht$n > $W/bencht$n.out 2>&1
  echo "== batch $n bench:"; grep -E "startup|forceload|heap_" $W/bencht$n/result.txt | tr "\n" " "; echo
  for p in $(pgrep java); do [ "$(readlink /proc/$p/cwd)" = "$S" ] && kill -9 $p; done
done
echo ALLDONE
