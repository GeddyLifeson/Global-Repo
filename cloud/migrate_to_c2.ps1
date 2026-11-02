# Moves E:\Prism and E:\DiaithirServer to C: (E: is a USB spinning disk, exFAT, so no junctions) and rewrites E:\Prism / E:\DiaithirServer
# paths inside the copied files on C:. E: is left untouched as the backup. Safe to rerun (re-copies from E: and re-applies the edits).
# It does NOT touch scheduled tasks or desktop shortcuts: it lists every one that still points at E: so they can be repointed separately.
# Log: C:\DiaithirMigrate\migrate2.log
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force C:\DiaithirMigrate | Out-Null
Start-Transcript -Path C:\DiaithirMigrate\migrate2.log -Append | Out-Null
function Die($m) { "ERROR: $m"; Stop-Transcript | Out-Null; exit 1 }
$pairs = @(@{src='E:\Prism'; dst='C:\Prism'}, @{src='E:\DiaithirServer'; dst='C:\DiaithirServer'})
$rx = '(?i)\bE:(\\\\|\\|/)(Prism|DiaithirServer)\b'
function Fix([string]$s) { [regex]::Replace($s, $rx, { param($m) 'C:' + $m.Groups[1].Value + $m.Groups[2].Value }) }
function Up { [bool](Get-NetTCPConnection -LocalPort 25570 -State Listen -ErrorAction SilentlyContinue) }

# 0. Checks
foreach ($p in $pairs) { if (-not (Test-Path $p.src)) { Die "$($p.src) missing" } }
$need = 0
foreach ($p in $pairs) { $need += (Get-ChildItem $p.src -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum }
$free = (Get-Volume -DriveLetter C).SizeRemaining
"Need $([math]::Round($need/1GB,1)) GB, C: free $([math]::Round($free/1GB,1)) GB"
if ($free -lt ($need + 10GB)) { Die "Not enough space on C: (need data + 10 GB spare). Nothing changed." }

# 1. Stop the server cleanly, refuse if Prism or the game is running
if (Up) {
  "Stopping server..."
  if (Test-Path E:\DiaithirServer\stop_server.ps1) { & E:\DiaithirServer\stop_server.ps1 }
  $t = 0; while ((Up) -and $t -lt 240) { Start-Sleep 2; $t += 2 }
  if (Up) { Die "server did not stop in 240 s. Nothing changed." }
}
$held = Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match 'E:\\Prism' }
if ($held) { Die "Prism or the game is running (PID $($held[0].ProcessId)). Close it and run again. Nothing changed." }
# the old stall watchdog watches the E: server; the new start_server.ps1 starts its own on C:
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'server_watchdog\.py.*E:\\DiaithirServer' } | ForEach-Object { "Stopping old watchdog PID $($_.ProcessId)"; Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

# 2. Copy and verify (E: is never modified)
foreach ($p in $pairs) {
  "Copying $($p.src) -> $($p.dst) ..."
  robocopy $p.src $p.dst /MIR /COPY:DAT /DCOPY:DAT /R:2 /W:2 /MT:8 /NFL /NDL /NP | Out-Null
  if ($LASTEXITCODE -ge 8) { Die "robocopy failed ($LASTEXITCODE) for $($p.src). E: untouched." }
  robocopy $p.src $p.dst /MIR /L /NJH /NJS /NFL /NDL /NP | Out-Null
  if ($LASTEXITCODE -ne 0) { Die "verify pass found differences in $($p.src). C: copy kept for inspection." }
  "verified $($p.src)"
}

# 3. Rewrite the E: paths to C: inside the C: copies (text files only; skips worlds, jars, libraries, logs)
$skip = '\\(world|mods|libraries|logs|saves|backups|\.cache|assets|versions|resourcepacks|java|watchdog|diaithirperf|crash-reports)(\\|$)'
$ext = '.ps1','.bat','.cmd','.py','.json','.toml','.cfg','.yml','.yaml','.txt','.properties','.xml','.sh','.conf','.ini','.md','.js','.vbs'
$edited = 0
foreach ($p in $pairs) {
  Get-ChildItem $p.dst -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $ext -contains $_.Extension.ToLower() -and $_.Length -lt 2MB -and $_.FullName -notmatch $skip } | ForEach-Object {
      $b = [IO.File]::ReadAllBytes($_.FullName)
      if ($b.Length -ge 2 -and $b[0] -eq 0xFF -and $b[1] -eq 0xFE) { $enc = [Text.Encoding]::Unicode; $off = 2; $bom = $true }
      elseif ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF) { $enc = New-Object Text.UTF8Encoding($true); $off = 3; $bom = $true }
      else { $enc = New-Object Text.UTF8Encoding($false); $off = 0; $bom = $false }
      $s = $enc.GetString($b, $off, $b.Length - $off)
      if ($s -match $rx) {
        $out = $enc.GetBytes((Fix $s)); if ($bom) { $out = $enc.GetPreamble() + $out }
        [IO.File]::WriteAllBytes($_.FullName, $out); $edited++; "  edited $($_.FullName)"
      } }
}
"$edited files rewritten"

# 4. Report (read-only) what still points at E:
"--- Scheduled tasks still pointing at E:\Prism or E:\DiaithirServer:"
foreach ($t in Get-ScheduledTask -ErrorAction SilentlyContinue) {
  try { if ((Export-ScheduledTask -TaskName $t.TaskName -TaskPath $t.TaskPath) -match $rx) { "  $($t.TaskPath)$($t.TaskName)" } } catch {}
}
"--- Shortcuts still pointing at E:\Prism or E:\DiaithirServer:"
$sh = New-Object -ComObject WScript.Shell
foreach ($r in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('StartMenu'), [Environment]::GetFolderPath('Startup')) | Where-Object { $_ -and (Test-Path $_) }) {
  Get-ChildItem $r -Recurse -Filter *.lnk -ErrorAction SilentlyContinue | ForEach-Object {
    $l = $sh.CreateShortcut($_.FullName); if (("$($l.TargetPath) $($l.Arguments) $($l.WorkingDirectory)") -match $rx) { "  $($_.FullName)" } }
}

# 5. Start the server from C: and verify the port
"Starting server from C:..."
& C:\DiaithirServer\start_server.ps1
$t = 0; while (-not (Up) -and $t -lt 360) { Start-Sleep 3; $t += 3 }
if (Up) { "Server is up (port 25570), running from C:\DiaithirServer after $t s. E: copies are untouched backups." }
else {
  "ERROR: port 25570 not listening after 360 s. Last lines of server.err:"
  Get-Content C:\DiaithirServer\server.err -Tail 25 -ErrorAction SilentlyContinue
  "E: is untouched, so nothing is lost."
}
Stop-Transcript | Out-Null
