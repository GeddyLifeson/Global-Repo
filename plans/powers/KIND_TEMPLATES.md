# Kind power templates (S6981)
A being's kind (vampire, zombie, undead, lycanthrope, ghost, demon, angel, cyborg, android, mutant, dragon, deity, elemental, golem, fae, giant, shapeshifter) carries a default set of powers. The template is a refinable reference, not a hard rule.

- `KIND_MAP.tsv`: how a kind is detected: judge `x` tag regex, definition in the page lead ("... is a vampire"), or kind word in the name ("vampire hunter" style names are skipped). Edit to add kinds or tags.
- `KIND_TEMPLATES.tsv`: kind, scope (`*` = all settings, or a wiki slug for a franchise variant), powers (`pool_id:m`, C3M scale 1-10), n, source_page (`wiki|lead_idx` example page), source, note.
  - `observed` rows are rebuilt on every run from page-stated powers of judged beings and from pages that define the kind (power kept if stated by 30-35% of them; franchise rows need 3 beings or 2 defining pages).
  - `*` rows add a genre baseline (`seed`) under what pages state, because most pages state no kind powers. Magnitude 1 = peak human.
  - Set `source` to `manual` to freeze a row; rebuilds never touch manual rows.
- `BEING_KINDS.tsv`: page id, kind, how (x / text / name) for every judged being whose kind is stated.
- Order at merge time (merge_judged.py): page-stated power keeps its page value; template fills only ids the page does not state, franchise row first then `*`. Evidence rows read `template@kind@scope`, confidence low. A being judged without powers keeps its old rows and gains the missing template ids.
- Refine: edit a row (franchise variant: add a row with the wiki slug and source page), rerun `python3 cloud/tools/powers/kind_templates.py build plans/powers`, then merge_judged.py. Recurring corrections: copy the correction into the kind row (manual) so every being of that kind picks it up.
