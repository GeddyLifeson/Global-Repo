# Global Repo

One catalogue of every script Marlon's sessions use, with copies. Start at `SCRIPTS_INDEX.md`; each script has a stable ID (S0001...). IDs never change or get reused. Copies sit under `cloud/`, `pc/`, `laptop/`.

Add a script: run `python3 -I claim_id.py` (S0322; counter lives in /mnt/project-files/compute/id_counters, no GitHub push needed) to get a collision-free ID; never pick one by hand. Then, put `# Sxxxx <what it does>` as the header comment in the script, add its row to `<device>_inventory.tsv`, run `python3 -I build_index.py .`, commit and push. Never commit keys, tokens or emails.
