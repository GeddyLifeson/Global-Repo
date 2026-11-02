# Global Repo

One catalogue of every script Marlon's sessions use, with copies. Start at `SCRIPTS_INDEX.md`; each script has a stable ID (S0001...). IDs never change or get reused. Copies sit under `cloud/`, `pc/`, `laptop/`.

Add a script: take the next free ID from `ids.tsv`, put `# Sxxxx <what it does>` as the header comment in the script, add its row to `<device>_inventory.tsv`, run `python3 -I build_index.py .`, commit and push. Never commit keys, tokens or emails.
