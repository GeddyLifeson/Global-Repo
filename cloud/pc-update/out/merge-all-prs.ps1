# Merge all PRs: marks every open draft PR ready and merges all open PRs, stacked PRs in order,
# across the three Diaithir repos. Uses your stored GitHub login (gh, or Git Credential Manager).
# Double-click "Merge All PRs". A log is written to the Desktop (merge-all-prs.log).

$ErrorActionPreference = 'Stop'
$repos = 'GeddyLifeson/DiaithirRPG', 'GeddyLifeson/diaithir-ports', 'GeddyLifeson/shardfall-game'
$log = Join-Path ([Environment]::GetFolderPath('Desktop')) 'merge-all-prs.log'
try { Start-Transcript -Path $log -Force | Out-Null } catch { }

function Finish($code) {
    try { Stop-Transcript | Out-Null } catch { }
    Write-Host ''
    Read-Host 'Press Enter to close'
    exit $code
}

function Get-Token {
    $t = $null
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $t = (& gh auth token 2>$null | Out-String).Trim()
    }
    if (-not $t) {
        $in = "protocol=https`nhost=github.com`n`n"
        $out = $in | & git credential fill 2>$null
        foreach ($l in $out) { if ($l -like 'password=*') { $t = $l.Substring(9) } }
    }
    if (-not $t) { throw 'No GitHub login found. Run "gh auth login" once, or push to GitHub once from Git so it stores a login.' }
    $t
}

function Api($method, $path, $body) {
    $h = @{ Authorization = "Bearer $script:token"; Accept = 'application/vnd.github+json'; 'X-GitHub-Api-Version' = '2022-11-28' }
    $p = @{ Method = $method; Uri = "https://api.github.com$path"; Headers = $h; UseBasicParsing = $true }
    if ($body) { $p.Body = ($body | ConvertTo-Json -Compress); $p.ContentType = 'application/json' }
    Invoke-RestMethod @p
}

function Ready($node) {
    $q = 'mutation($id:ID!){markPullRequestReadyForReview(input:{pullRequestId:$id}){pullRequest{isDraft}}}'
    Api 'POST' '/graphql' @{ query = $q; variables = @{ id = $node } } | Out-Null
}

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $script:token = Get-Token
    $merged = 0; $failed = @()
    foreach ($repo in $repos) {
        Write-Host ''; Write-Host "== $repo =="
        $def = (Api 'GET' "/repos/$repo").default_branch
        $open = @()
        $page = 1
        while ($true) {
            $r = @(Api 'GET' "/repos/$repo/pulls?state=open&per_page=100&page=$page")
            if ($r.Count -eq 0) { break }
            $open += $r; $page++
        }
        Write-Host "$($open.Count) open PRs (default branch $def)"
        $skip = @{}
        for ($round = 0; $round -lt 60 -and $open.Count -gt 0; $round++) {
            $heads = @($open | ForEach-Object { $_.head.ref })
            # ready now: base is the default branch or a branch no open PR still owns
            $ready = @($open | Where-Object { -not $skip[$_.number] -and ($_.base.ref -eq $def -or $heads -notcontains $_.base.ref) } | Sort-Object number)
            if ($ready.Count -eq 0) { break }
            foreach ($pr in $ready) {
                $n = $pr.number
                try {
                    $cur = Api 'GET' "/repos/$repo/pulls/$n"
                    if ($cur.base.ref -ne $def -and $heads -notcontains $cur.base.ref) {
                        Api 'PATCH' "/repos/$repo/pulls/$n" @{ base = $def } | Out-Null
                    }
                    if ($cur.draft) { Ready $cur.node_id; Start-Sleep -Seconds 2 }
                    $ok = $false
                    for ($i = 0; $i -lt 6 -and -not $ok; $i++) {
                        try {
                            Api 'PUT' "/repos/$repo/pulls/$n/merge" @{ merge_method = 'merge' } | Out-Null
                            $ok = $true
                        } catch {
                            $code = 0; try { $code = [int]$_.Exception.Response.StatusCode } catch { }
                            if ($code -eq 405 -or $code -eq 409) { Start-Sleep -Seconds 5 } else { throw }
                        }
                    }
                    if (-not $ok) { throw 'GitHub would not merge it (conflict or blocked)' }
                    Write-Host "merged #$n  $($pr.title)"
                    $merged++
                    $open = @($open | Where-Object { $_.number -ne $n })
                    # stacked PRs that sat on this branch move to the default branch
                    foreach ($d in @($open | Where-Object { $_.base.ref -eq $pr.head.ref })) {
                        try { Api 'PATCH' "/repos/$repo/pulls/$($d.number)" @{ base = $def } | Out-Null; $d.base.ref = $def } catch { }
                    }
                } catch {
                    Write-Host "FAILED #$n  $($pr.title): $($_.Exception.Message)" -ForegroundColor Red
                    $failed += "$repo#$n"
                    $skip[$n] = $true
                }
            }
        }
    }
    Write-Host ''
    Write-Host "Done. Merged $merged. Failed or left open: $($failed.Count)"
    if ($failed.Count) { $failed | ForEach-Object { Write-Host "  $_" } }
    Write-Host "Log: $log"
    Finish 0
}
catch {
    Write-Host ''
    Write-Host "Merge failed: $($_.Exception.Message)" -ForegroundColor Red
    Finish 1
}
