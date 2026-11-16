# Handoff: bulk wiki page download (judge shards 160-927)

State: PR #126 (branch claude/project-thread-ywkxsp, base qpjd6w) has cache/shard_N.pages.json.gz, batches/shard_N.src.jsonl and .absent.json for shards 160-927, READY_SHARDS.txt (766 of 768 in 160-927 ready; 230 and 313 not, many tiny wikis). Needs merging into qpjd6w; until then validate.py on qpjd6w re-fetches live pages and rejects 161/162/167/177 (their repairs only hold against the bulk text).

Unvalidated: `validate.py all` was last run before the final resolver passes. Passes after it (xenoserieswiki, X-COM, Yakuza, absent rules) rewrote src.jsonl/cache for about 100 shards (Xenoblade, X-COM, Yakuza). Shards 160-162, 167, 177, 151 validated PASS; the rest of 160-927 have no judge output yet, so nothing to validate until judged.

Judgement call: rows with no page passing pages.match on the lead, on a fully indexed wiki (WoW, Xenoblade, X-COM, Yakuza), are written to batches/shard_N.absent.json (not counted toward the 2% cap). Renamed or edited pages could be wrongly counted absent; Xenoblade's fandom side is a July dump, xenoserieswiki is a current crawl.

Text format: tools/flat.py flattens wikitext (keeps template content like WoW {{abilities}}, drops infoboxes); differs from live HTML text, so quotes judged on live text won't match.

Tools (plans/powers/judge/tools): crawl2.py (resumable raw crawl; crawl2w.py variant uses /w/api.php), dump2idx.py, ww_conv.py, res.py (offline resolver; SRC dict lists the dumps in /tmp/s, regenerate by re-downloading), flat.py. Dumps: s3.amazonaws.com/wikia_xml_dumps/w/wo/wowpedia_pages_current.xml.7z and x/xe/xenoblade_pages_current.xml.7z; warcraft.wiki.gg and xenoserieswiki.org by crawl. Marvel/DC dumps are archived; J8 crawl targets in J8_TARGETS.txt on 8lxbuh (pace 1 req/s; Fandom 429s above that).
Open: shards 230, 313 (paused by Marlon), pages.py `]]` rule is in this branch.
