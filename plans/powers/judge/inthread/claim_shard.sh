#!/bin/bash
# Atomically claims the next free shard and prints its number. Usage: bash claim_shard.sh [FIRST] [LAST] TAG
# Lock = mkdir shard_NN.lock (atomic), then owner is written and re-read to confirm we won.
cd "$(dirname "$0")" || exit 1
tag="${3:-thread}-$$-$RANDOM"
for n in $(seq -f %02g "${1:-16}" "${2:-99}"); do
  [ -f shard_$n.jsonl ] || break
  [ -e shard_$n.out.jsonl ] && continue
  [ -e shard_$n.claimed ] && continue
  if mkdir shard_$n.lock 2>/dev/null; then
    echo "$tag $(date -u +%H:%MZ)" > shard_$n.lock/owner
    sleep 1
    if [ "$(cut -d' ' -f1 shard_$n.lock/owner 2>/dev/null)" = "$tag" ] && [ ! -e shard_$n.out.jsonl ]; then
      cp shard_$n.lock/owner shard_$n.claimed; echo "$n"; exit 0
    fi
  fi
done
echo none; exit 1
