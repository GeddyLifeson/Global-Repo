# Moves E:\Prism and E:\DiaithirServer to the C: NVMe SSD (E: is a USB spinning disk).
# Method: robocopy to C:, verify, rename the E: folder to *.e-backup, junction the old path to C:.
# Scripts, shortcuts, scheduled tasks and Prism settings that say E:\... keep working with no edits. E: copy stays as backup.
# Log: C:\DiaithirMigrate\migrate.log
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force C:\DiaithirMigrate | Out-Null
Start-Transcript -Path C:\DiaithirMigrate\migrate.log -Append | Out-Null
function Die($m) { "ERROR: $m"; Stop-Transcript | Out-Null; exit 1 }
$pairs = @(@{src='E:\Prism'; dst='C:\Prism'}, @{src='E:\DiaithirServer'; dst='C:\DiaithirServer'})

# 0. Checks
$fs = (Get-Volume -DriveLetter E).FileSystem
if ($fs -ne 'NTFS') { Die "E: is $fs, junctions need NTFS. Nothing changed." }
foreach ($p in $pairs) {
  if (-not (Test-Path $p.src)) { Die "$($p.src) missing" }
  if ((Get-Item $p.src -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { Die "$($p.src) is already a junction (migrated?)" }
}
$need = 0
foreach ($p in $pairs) { $need += (Get-ChildItem $p.src -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum }
$free = (Get-Volume -DriveLetter C).SizeRemaining
"Need $([math]::Round($need/1GB,1)) GB, C: free $([math]::Round($free/1GB,1)) GB"
if ($free -lt ($need + 20GB)) { Die "Not enough space on C: (need data + 20 GB spare). Nothing changed." }

# 1. Stop the server cleanly, then anything holding files under the two folders
function Up { [bool](Get-NetTCPConnection -LocalPort 25570 -State Listen -ErrorAction SilentlyContinue) }
if (Up) {
  "Stopping server..."
  if (Test-Path E:\DiaithirServer\stop_server.ps1) { & E:\DiaithirServer\stop_server.ps1 }
  $t = 0; while ((Up) -and $t -lt 240) { Start-Sleep 2; $t += 2 }
  if (Up) { Die "server did not stop in 240 s. Nothing changed." }
}
$held = Get-CimInstance Win32_Process | Where-Object {
  $_.ProcessId -ne $PID -and $_.Name -notmatch 'powershell|pwsh|conhost' -and
  ($_.ExecutablePath -match '^E:\\(Prism|DiaithirServer)' -or $_.CommandLine -match 'E:\\(Prism|DiaithirServer)') }
$relaunch = @()
foreach ($h in $held) {
  if ($h.CommandLine -match 'Prism') { Die "Prism or the game is running (PID $($h.ProcessId)). Close it and run again. Nothing changed." }
  if ($h.Name -notmatch 'java') { $relaunch += $h.CommandLine }
  "Stopping $($h.Name) PID $($h.ProcessId)"; Stop-Process -Id $h.ProcessId -Force -ErrorAction SilentlyContinue
}
Start-Sleep 3

# 2. Copy and verify (E: stays untouched until both pass)
foreach ($p in $pairs) {
  "Copying $($p.src) -> $($p.dst) ..."
  robocopy $p.src $p.dst /MIR /COPY:DAT /DCOPY:DAT /R:2 /W:2 /MT:8 /NFL /NDL /NP /XJ | Out-Null
  if ($LASTEXITCODE -ge 8) { Die "robocopy failed ($LASTEXITCODE) for $($p.src). E: untouched." }
  robocopy $p.src $p.dst /MIR /L /NJH /NJS /NFL /NDL /NP /XJ | Out-Null
  if ($LASTEXITCODE -ne 0) { Die "verify pass found differences in $($p.src). E: untouched, C: copy kept." }
  "verified $($p.src)"
}

# 3. Swap: E:\X -> E:\X.e-backup, junction E:\X -> C:\X
foreach ($p in $pairs) {
  Rename-Item $p.src ((Split-Path $p.src -Leaf) + '.e-backup')
  New-Item -ItemType Junction -Path $p.src -Target $p.dst | Out-Null
  "junction $($p.src) -> $($p.dst)"
}

# 4. Relaunch stopped tools (not java), start the server, verify the port
foreach ($c in $relaunch) { "Relaunching: $c"; Start-Process -WindowStyle Hidden cmd.exe -ArgumentList "/c $c" }
"Starting server..."
& E:\DiaithirServer\start_server.ps1
$t = 0; while (-not (Up) -and $t -lt 360) { Start-Sleep 3; $t += 3 }
if (Up) { "Server is up (port 25570) from C: after $t s. Old copies: E:\Prism.e-backup, E:\DiaithirServer.e-backup." }
else {
  "ERROR: port 25570 not listening after 360 s. Last lines of server.err:"
  Get-Content E:\DiaithirServer\server.err -Tail 25 -ErrorAction SilentlyContinue
  "Undo: delete the junctions E:\Prism and E:\DiaithirServer, rename the .e-backup folders back."
}
Stop-Transcript | Out-Null
