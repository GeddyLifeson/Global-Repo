# PC judging run (model router + Ollama)
Queue: `priority.jsonl.gz` (20,000 pages with text, beings by Haiku evidence interleaved 3:1 with weapon/armor/vehicle candidates, all in-thread shard pages excluded). Only Python 3 stdlib needed.
Run from the repo root (branch claude/project-thread-ix4yis), with both endpoints in one shared queue:

    python cloud/tools/powers/judge_pc.py plans/powers/pcrun/priority.jsonl.gz plans/powers/pcrun/results_pc.jsonl router=http://127.0.0.1:8788/v1,auto,8 ollama=http://127.0.0.1:11434/v1,gpt-oss:20b,1 --push 1000

- `auto` is the model name the router should accept; change it to whatever the router expects. Workers is the third field. If the router needs a key: set JUDGE_KEY.
- Resumable: rerun the same command and finished ids are skipped. `--push N` commits and pushes results every N pages.
- Output rows: S6975 format ({id,b,n,p,x,...} plus `by` = endpoint); bad rows are {id,error}. Quotes are validated verbatim against the page text, so weak models just lose unsupported powers.
- Check first: `head -50` of the queue to a file and run it once to see the router answers in JSON.
