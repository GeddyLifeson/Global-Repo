#!/usr/bin/env bash
# Branch cleanup from the 2026-10-21 consolidation. Run from a DiaithirRPG clone after Marlon approves.
# Group A: tip already inside engine or another kept branch (nothing lost).
# Group B: squash-merged PR heads (commits stay on the PR page).
# Group C: archived to tags/archive/<name> first, then deleted (restorable with git push origin archive/X:refs/heads/X).
set -e
A=" boot-speed chargen client economy hidden-launch loadtest music safety weapons v11 failsafe mc-update claude/tech-ages-per-item claude/project-thread-dwqtyp claude/project-thread-h0mj7e claude/archive-in-between-kit claude/archive-in-between-tzu7bt claude/earth-history claude/earth-wikidata claude/league-of-legends-kit claude/league-of-legends-library claude/panscriptum-map-accuracy-archive-os70eh claude/panscriptum-phases-4-8-62tcr3 claude/panscriptum-sync-wpoakk claude/project-thread-6haol2 claude/project-thread-aa6og9 claude/scp-backrooms-kit claude/scp-backrooms-library claude/wh-scifi-kit claude/own-distribution-inventory claude/project-thread-7w7w1o claude/earth-dates-build claude/earth-dates-cloud claude/project-thread-yqrj53 claude/project-thread-w0697r-snowline claude/project-thread-w0697r-tellus"
B="claude/project-thread-patksv claude/modal-actions-engine claude/modal-actions claude/project-thread-4haddv claude/project-thread-lpel0u claude/atlas-live-link"
C="master claude/pc-compare coverage-data claude/wh-scifi-titles claude/wh-scifi-titles-2 claude/archive-wiki-fetch tmp/lol-wiki-raw tmp/lol-crawl v11b claude/azgaar-maps claude/earth-dates-cloud-2 claude/earth-dates-cloud-3 claude/earth-dates-cloud-4 claude/project-thread-k0rl0h"
git fetch -q origin
git push origin $(for b in $C; do echo "origin/$b:refs/tags/archive/$b"; done)
git push origin $(for b in $A $B $C; do echo ":refs/heads/$b"; done)
# Other repos (all merged):
# Diathiris: claude/project-thread-0raokz claude/project-thread-dhak1g claude/project-thread-ua3fgh claude/atlas-live-link
# diaithir-ports: claude/publish-workflow
# shardfall-game: claude/staged-modules
