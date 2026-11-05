#!/bin/bash
# S-id pending. Usage: shard.sh prep N  -> copies old shard if needed, resolves pages, prints the judge view (also saved to /tmp/judge_N.txt)
#        shard.sh done N  -> validates (re-runs validate.py), commits and pushes out/shard_N.* to the current branch
set -e
cd "$(dirname "$0")/.."; N=$2
case $1 in
prep)
  [ -f batches/shard_$N.jsonl ] || cp /mnt/project-files/plans/powers/judge/inthread/shard_$(printf %02d $N).jsonl batches/shard_$N.jsonl
  [ -f batches/shard_$N.src.jsonl ] || python3 tools/pages.py resolve $N >&2
  python3 tools/judge.py show $N | tee /tmp/judge_$N.txt ;;
done)
  python3 tools/validate.py $N | tail -3 | tee /dev/stderr | grep -q PASS
  cd ../../..; git add plans/powers/judge/out/shard_$N.* plans/powers/judge/batches/shard_$N.*
  git commit -qm "Judge shard $N (validated)" && for i in 1 2 3 4; do git push -q origin HEAD && break || sleep $((2**i)); done ;;
esac
