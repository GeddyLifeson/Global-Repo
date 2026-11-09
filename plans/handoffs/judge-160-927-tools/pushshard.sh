#!/bin/bash
# usage: pushshard.sh N  -- pushes out/shard_N.* from main repo to qpjd6w via temp worktree, retries on race
N=$1; R=/home/user/global-repo; B=claude/project-thread-qpjd6w; W=/tmp/claude-0/wt_$N
for t in 1 2 3 4 5 6; do
  cd $R; git fetch -q origin $B; rm -rf $W; git worktree prune; git worktree add -q --detach $W origin/$B || { sleep 3; continue; }
  cp $R/plans/powers/judge/out/shard_$N.out.jsonl $R/plans/powers/judge/out/shard_$N.meta.json $W/plans/powers/judge/out/
  cd $W; git add plans/powers/judge/out/shard_$N.*
  git commit -q -m "Judge shard $N (PASS)

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Q3r8pfVFMKZWjdp65JsnkX"
  if git push -q origin HEAD:$B 2>/dev/null; then echo "pushed $N"; cd $R; git worktree remove --force $W; exit 0; fi
  cd $R; git worktree remove --force $W; sleep $((RANDOM%8+2))
done; echo "PUSH FAILED $N"; exit 1
