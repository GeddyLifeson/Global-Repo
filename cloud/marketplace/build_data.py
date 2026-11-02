import csv, json, sys
V = {  # name (lowercase, exact listing name) -> (verdict, note)
 "renovate": ("adopted", "Installed on diaithir-ports; config PR #5 (NeoForge + Gradle grouped, OSV alerts)"),
 "sonarqube cloud": ("adapted", "pre-commit: ruff + shellcheck, PR #85"), "codacy": ("adapted", "pre-commit, merged in PR #85"),
 "deepsource": ("adapted", "pre-commit, merged in PR #85"), "codefactor": ("adapted", "pre-commit, merged in PR #85"), "qlty cloud": ("adapted", "pre-commit, merged in PR #85"),
 "semgrep": ("adapted", "pre-commit, merged in PR #85"), "pep 8 speaks": ("adapted", "ruff in pre-commit"), "hound": ("adapted", "pre-commit"),
 "gitguardian": ("adapted", "detect-secrets in pre-commit + push protection on diaithir-ports"),
 "aikido security": ("adapted", "detect-secrets + OSV via Renovate"), "arnica pipelineless application security": ("adapted", "detect-secrets + OSV"),
 "snyk": ("adapted", "OSV alerts through Renovate"), "socket security": ("adapted", "OSV alerts through Renovate"),
 "mend bolt": ("adapted", "OSV alerts through Renovate"), "debricked": ("adapted", "OSV alerts through Renovate"), "depfu": ("adapted", "Renovate"),
 "coderabbit": ("adapted", "tools/offload/pr_review.py on the free LLM pool; CodeRabbit itself free on public repos (click)"),
 "qodo": ("adapted", "pr_review.py"), "qodo - free for open source projects": ("click", "Free for public repos; pr_review.py covers private"),
 "sourcery": ("adapted", "pr_review.py"), "greptile apps": ("adapted", "pr_review.py"), "cubic": ("adapted", "pr_review.py"),
 "bito's ai code review agent": ("adapted", "pr_review.py"), "cr.gpt": ("adapted", "pr_review.py"), "what the diff": ("adapted", "pr_review.py"),
 "baz ai code review": ("adapted", "pr_review.py"), "codeant ai": ("adapted", "pr_review.py"), "chatgptbot": ("adapted", "pr_review.py"),
 "rewind backups for github": ("adapted", "mirror_repos.py nightly to E:\\Backups\\github, all 18 repos"),
 "cloudback: github backup & restore": ("adapted", "mirror_repos.py"), "gitprotect github backup & recovery": ("adapted", "mirror_repos.py"),
 "pre-commit ci": ("click", "Free for public repos; runs our pre-commit configs on PRs without Actions"),
 "imgbot": ("skipped", "Would rewrite pack PNGs and break build_pack hash checks"),
 "circleci": ("skipped", "PC job queue + cloud threads do CI"), "travis ci": ("skipped", "PC job queue"), "render": ("skipped", "No web service to host"),
 "linear": ("skipped", "Project ledger + threads already track work"), "atlassian": ("skipped", "Not used"), "zenhub": ("skipped", "Not used"),
 "slack + github": ("skipped", "No Slack workspace"), "mergify": ("skipped", "Claude merges; one owner"), "codecov": ("skipped", "No test-coverage pipeline"),
 "cto.new": ("skipped", "Another coding agent; Claude threads already do this"), "wakatime": ("skipped", "Time tracking not needed"),
 "io.github.upstash/context7": ("adopted", "Picked for the desktop user config with Marlon's key; install paused while PC work is light"),
 "com.microsoft/markitdown": ("adopted", "Picked for the desktop user config (PDFs, Word, screenplays, Allan-Odis docs to Markdown); install paused while PC work is light"),
 "io.github.microsoft/playwright-mcp": ("skipped", "Cloud has Playwright, desktop has Claude in Chrome"),
 "io.github.deusdata/codebase-memory-mcp": ("blocked", "36k downloads/month token saver; cloud safety check refuses running third-party packages"),
 "io.github.mrfentmen/modrinth-mcp": ("skipped", "Modrinth public API is reachable directly; unvetted single-author package"),
 "io.github.sintexer/jvmsrc": ("skipped", "Unvetted (733 downloads/month); Gradle sources already on desktop"),
 "io.github.mrfentmen/sports-scores-mcp": ("skipped", "ESPN public API is keyless, usable directly for SAM"),
 "io.github.nero-engine/bulk-ocr-image-pdf-to-text": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "io.github.nero-engine/dataset-pdf-extract": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "io.github.lintlab/pdf-to-markdown": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "io.github.monietools/pdf-to-text-markdown-ocr": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "com.errandkit/pdf-to-markdown-tables": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "dev.pdf2md/pdf-to-markdown": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "dev.tanod/docs": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "ai.file2markdown/file2markdown": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "com.tensormaster/pdf": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "dev.tanod/document-to-markdown": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "io.github.granturismo/anytomarkdown": ("adapted", "Offline: tools/offload/ocr_pdf.py (scanned pages, PR #85) + Markitdown (text PDFs, Word)"),
 "io.github.github/github-mcp-server": ("adopted", "Already connected"),
}
rows = []
for r in csv.DictReader(open("marketplace_scored.csv", encoding="utf-8")):
    v = V.get(r["name"].lower(), ("", ""))
    if int(r["score"]) == 0 and not v[0]: continue
    rows.append([r["source"], r["name"], r["description"][:160], r["areas"], int(r["score"]), v[0], v[1], r["repo"], "key" if r["keys"] else ""])
json.dump(rows, open(sys.argv[1], "w", encoding="utf-8"), separators=(",", ":"))
from collections import Counter
print(len(rows), Counter(x[5] for x in rows if x[5]))
