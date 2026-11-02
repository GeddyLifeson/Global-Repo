# Diaithir perf pass 2 (includes pass 1; safe to rerun). Stops the server, applies, STARTS it, verifies the port. Backs up every file it edits to *.bak-perf.
$root = "E:\DiaithirServer"; New-Item -ItemType Directory -Force "$root\logs" | Out-Null
$log = "$root\logs\perf2.log"; Start-Transcript -Path $log -Append | Out-Null
function Up { [bool](Get-NetTCPConnection -LocalPort 25570 -State Listen -ErrorAction SilentlyContinue) }
if (Up) {
  "Stopping server..."
  $pidf = "$root\server.pid"
  if (Test-Path "$root\stop_server.ps1") { & "$root\stop_server.ps1" } elseif (Test-Path $pidf) { Stop-Process -Id (Get-Content $pidf) }
  $t = 0; while ((Up) -and $t -lt 180) { Start-Sleep 2; $t += 2 }
  if (Up) { "ERROR: server did not stop in 180 s. Nothing changed."; Stop-Transcript; exit 1 }
}
$s = "$root\server"
function Bak($p) { if (Test-Path $p) { Copy-Item $p "$p.bak-perf" -Force } }

# 1. JVM: compact object headers (-700 MB measured with the pack's server heap, no downside on Java 25)
$j = "$s\user_jvm_args.txt"; Bak $j
if (-not (Select-String -Path $j -Pattern 'UseCompactObjectHeaders' -Quiet)) { Add-Content $j "-XX:+UseCompactObjectHeaders" }

# 2. Server-only mods that are client mods (DistantHorizons etc). Moved, not deleted. The pack bundle makes this permanent.
$off = "$s\mods_disabled_perf"; New-Item -ItemType Directory -Force $off | Out-Null
foreach ($p in 'DistantHorizons','journeymap','MapFrontiers','configured-neoforge') {
  Get-ChildItem "$s\mods\$p*.jar" -ErrorAction SilentlyContinue | Move-Item -Destination $off -Force
}

# 3. ServerCore: adaptive load shedding and cheaper villagers/fluids
$c = "$s\config\servercore\config.yml"
if (Test-Path $c) { Bak $c
  $t = Get-Content $c -Raw
  $t = [regex]::Replace($t, '(?ms)(lobotomize-villagers:\s*\r?\n\s*enabled:) false', '$1 true')
  $t = [regex]::Replace($t, '(?ms)(^dynamic:\s*\r?\n\s*enabled:) false', '$1 true')
  Set-Content $c $t -NoNewline }
$o = "$s\config\servercore\optimizations.yml"
if (Test-Path $o) { Bak $o
  (Get-Content $o -Raw) -replace 'cancel-duplicate-fluid-ticks: false','cancel-duplicate-fluid-ticks: true' | Set-Content $o -NoNewline }


# 4. Heap and distances for a PC with ~4 GB free (measured: Xmx5G view 6 / sim 4 and Xmx4G view 4 / sim 3 both hold 20 TPS with Tellus chunks loaded)
$j = "$s\user_jvm_args.txt"
(Get-Content $j) -replace '^-Xmx.*','-Xmx5G' -replace '^-Xms.*','-Xms2G' | Set-Content $j
$p = "$s\server.properties"; Bak $p
$t = Get-Content $p
$t = $t -replace '^view-distance=.*','view-distance=6' -replace '^simulation-distance=.*','simulation-distance=4'
if (-not ($t -match '^pause-when-empty-seconds=')) { $t += 'pause-when-empty-seconds=60' }
Set-Content $p $t

# 5. Start and verify
"Starting server..."
& "$root\start_server.ps1"
$t = 0; while (-not (Up) -and $t -lt 360) { Start-Sleep 3; $t += 3 }
if (Up) { "Server is up (port 25570) after $t s" } else { "ERROR: port 25570 not listening after 360 s. Last lines of server.err:"; Get-Content "$root\server.err" -Tail 25 -ErrorAction SilentlyContinue }
Stop-Transcript | Out-Null
