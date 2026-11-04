# Merge Safe data (single source)

The Merge Safe PRs shortcut on the PC downloads `merge-order.csv` and `merge-safe-config.json` from this folder on branch `claude/project-thread-zuc996` at the start of every run, and falls back to its local copies only if GitHub is unreachable. Edit these two files here, never on the PC.

To update the list from a cloud session: copy the new `plans/MERGE_ORDER.csv` over `merge-safe/merge-order.csv` on that branch (git push or the GitHub contents API). Do not rely on `/mnt/project-files/merge-safe/`: the PC cannot read it.

A PR listed in the CSV is "clear": drafts in it are marked ready and merged. Anything not listed is skipped.
